"""A reading already past a threshold when the automation (re)starts must still count.

numeric_state fires only on a crossing, and a pending `for:` is dropped whenever triggers are
re-attached, so without a re-check a job in progress across a restart, an edit or the automation
being switched off and on is never seen.
"""

from __future__ import annotations

from unittest.mock import patch

import pytest
from homeassistant.core import CoreState, HomeAssistant

from .conftest import (
    AUTOMATION,
    OMIT,
    PLUG,
    Advance,
    Monitor,
    automation_config,
    fired,
    set_plug,
    set_power,
    settle,
    state,
)


async def boot(hass: HomeAssistant, monitor: Monitor, **kwargs: object) -> dict:
    """Set up while Home Assistant is still starting, then finish starting it."""
    hass.set_state(CoreState.not_running)
    calls = await monitor(**kwargs)
    await hass.async_start()
    await settle()
    return calls


async def test_a_job_already_running_at_startup_is_picked_up_after_the_start_delay(
    hass: HomeAssistant, monitor: Monitor, advance: Advance
) -> None:
    calls = await boot(hass, monitor, power=50, start_delay={"seconds": 5})
    assert state(hass) == "idle"

    await advance(6)

    assert state(hass) == "job_ongoing"
    assert len(calls["on_job_started"]) == 1


async def test_a_job_that_finished_while_home_assistant_was_down_completes(
    hass: HomeAssistant, monitor: Monitor, advance: Advance
) -> None:
    calls = await boot(
        hass, monitor, initial="job_ongoing", power=0.5, finish_delay={"seconds": 180}
    )

    await advance(170)
    assert state(hass) == "job_ongoing"
    await advance(20)

    assert state(hass) == "job_completed"
    assert len(calls["on_job_completed"]) == 1


async def test_power_rising_during_the_recheck_wait_keeps_the_job_running(
    hass: HomeAssistant, monitor: Monitor, advance: Advance
) -> None:
    calls = await boot(
        hass, monitor, initial="job_ongoing", power=0.5, finish_delay={"seconds": 180}
    )

    await advance(60)
    set_power(hass, 50)
    await advance(300)

    assert state(hass) == "job_ongoing"
    assert not calls["on_job_completed"]
    assert not calls["on_job_started"], "a job that never stopped was announced again"


@pytest.mark.parametrize("automation_id", ["washer_monitor", OMIT], ids=["editor", "yaml-without-id"])
async def test_editing_the_automation_mid_countdown_still_completes_the_job(
    hass: HomeAssistant, monitor: Monitor, advance: Advance, automation_id: object
) -> None:
    """Saving an edit rebuilds the automation, dropping the pending `for:`.

    One with an id passes through unavailable on its way back on; one without has no state at all
    while its triggers attach, so only the reload event reaches it.
    """
    calls = await monitor(
        automation_id=automation_id, initial="job_ongoing", power=50, finish_delay={"seconds": 60}
    )
    set_power(hass, 0.5)
    await advance(30)

    edited = automation_config(automation_id, finish_delay={"seconds": 61})
    with patch("homeassistant.config.load_yaml_config_file", return_value=edited):
        await hass.services.async_call("automation", "reload", blocking=True)
    await advance(62)

    assert state(hass) == "job_completed"
    assert len(calls["on_job_completed"]) == 1


@pytest.mark.parametrize(
    ("initial", "power", "expected", "hook"),
    [("job_ongoing", 0.5, "job_completed", "on_job_completed"), ("idle", 50, "job_ongoing", "on_job_started")],
)
async def test_turning_the_automation_back_on_picks_up_the_current_reading(
    hass: HomeAssistant,
    monitor: Monitor,
    advance: Advance,
    initial: str,
    power: float,
    expected: str,
    hook: str,
) -> None:
    calls = await monitor(initial=initial, power=0.5 if power > 5 else 50)
    await hass.services.async_call("automation", "turn_off", {"entity_id": AUTOMATION}, blocking=True)
    set_power(hass, power)
    await advance(60)
    assert state(hass) == initial

    await hass.services.async_call("automation", "turn_on", {"entity_id": AUTOMATION}, blocking=True)
    await advance(11)

    assert state(hass) == expected
    assert len(calls[hook]) == 1


@pytest.mark.parametrize("interruption", [3, "unavailable"], ids=["at-threshold", "unavailable"])
async def test_an_interrupted_recheck_restarts_the_finish_delay(
    hass: HomeAssistant, monitor: Monitor, advance: Advance, interruption: float | str
) -> None:
    calls = await boot(hass, monitor, initial="job_ongoing", power=0.5, finish_delay={"seconds": 60})

    await advance(20)
    set_power(hass, interruption)
    await advance(20)
    set_power(hass, 0.5)
    await advance(25)
    assert state(hass) == "job_ongoing", "completed without a full finish delay of low power"

    await advance(40)
    assert state(hass) == "job_completed"
    assert len(calls["on_job_completed"]) == 1


@pytest.mark.parametrize("interruption", [5, "unavailable"], ids=["at-threshold", "unavailable"])
async def test_an_interrupted_recheck_restarts_the_start_delay(
    hass: HomeAssistant, monitor: Monitor, advance: Advance, interruption: float | str
) -> None:
    calls = await boot(hass, monitor, power=50, start_delay={"seconds": 60})

    await advance(20)
    set_power(hass, interruption)
    await advance(20)
    set_power(hass, 50)
    await advance(25)
    assert state(hass) == "idle", "started without a full start delay of high power"

    await advance(40)
    assert state(hass) == "job_ongoing"
    assert len(calls["on_job_started"]) == 1


async def test_a_settled_state_is_left_alone_by_the_recheck(
    hass: HomeAssistant, monitor: Monitor, advance: Advance
) -> None:
    calls = await boot(hass, monitor, initial="job_completed", power=0.5)

    await advance(60)

    assert state(hass) == "job_completed"
    assert not calls["on_job_started"]
    assert not calls["on_job_completed"]


async def test_a_sensor_that_comes_online_mid_job_is_tracked_without_a_recheck(
    hass: HomeAssistant, monitor: Monitor, advance: Advance
) -> None:
    """Plugs often connect after Home Assistant starts; their first reading is a crossing."""
    calls = await monitor(power=0)
    set_power(hass, "unavailable")
    await advance(1)

    set_power(hass, 50)
    await advance(1)
    assert state(hass) == "job_ongoing"

    set_power(hass, "unavailable")
    await advance(1)
    set_power(hass, 0.5)
    await advance(11)
    assert state(hass) == "job_completed"
    assert len(calls["on_job_started"]) == 1
    assert len(calls["on_job_completed"]) == 1


@pytest.mark.parametrize(
    ("initial", "expected", "hook"),
    [("job_ongoing", "paused", "paused"), ("idle", "unplugged", "unplugged"), ("job_completed", "unplugged", "unplugged")],
)
async def test_a_plug_switched_off_while_home_assistant_was_down_is_applied(
    hass: HomeAssistant, monitor: Monitor, advance: Advance, initial: str, expected: str, hook: str
) -> None:
    set_plug(hass, "off")
    calls = await boot(hass, monitor, plug_switch=PLUG, initial=initial, power=0)
    await advance(600)

    assert state(hass) == expected
    fired(calls, **{hook: 1})


@pytest.mark.parametrize(("power", "expected", "hook"), [(0.5, "idle", None), (50, "job_ongoing", "job_started")])
async def test_an_unplugged_appliance_switched_back_on_while_down_is_applied(
    hass: HomeAssistant, monitor: Monitor, advance: Advance, power: float, expected: str, hook: str | None
) -> None:
    set_plug(hass, "on")
    calls = await boot(hass, monitor, plug_switch=PLUG, initial="unplugged", power=power)
    await advance(600)

    assert state(hass) == expected
    fired(calls, **({hook: 1} if hook else {}))


async def test_a_paused_job_drawing_power_at_startup_resumes(
    hass: HomeAssistant, monitor: Monitor, advance: Advance
) -> None:
    set_plug(hass, "on")
    calls = await boot(
        hass, monitor, plug_switch=PLUG, initial="paused", power=50, start_delay={"seconds": 5}
    )
    await advance(4)
    assert state(hass) == "paused"

    await advance(2)
    assert state(hass) == "job_ongoing"
    await advance(600)
    fired(calls, job_resumed=1)


@pytest.mark.parametrize("plug_switch", [PLUG, OMIT], ids=["plug-on", "no-plug-switch"])
async def test_a_paused_job_quiet_at_startup_is_abandoned_after_the_grace(
    hass: HomeAssistant, monitor: Monitor, advance: Advance, plug_switch: object
) -> None:
    set_plug(hass, "on")
    calls = await boot(
        hass, monitor, plug_switch=plug_switch, initial="paused", power=0, resume_grace={"seconds": 120}
    )
    await advance(110)
    assert state(hass) == "paused"

    await advance(20)
    assert state(hass) == "idle"
    fired(calls, abandoned=1)


async def test_a_paused_job_resuming_during_the_startup_grace_honours_the_start_delay(
    hass: HomeAssistant, monitor: Monitor, advance: Advance
) -> None:
    set_plug(hass, "on")
    calls = await boot(
        hass,
        monitor,
        plug_switch=PLUG,
        initial="paused",
        power=0,
        start_delay={"seconds": 30},
        resume_grace={"seconds": 120},
    )
    await advance(20)
    set_power(hass, 50)
    await advance(20)
    set_power(hass, 0)
    await advance(20)
    assert state(hass) == "paused", "a blip shorter than the start delay resumed the job"

    set_power(hass, 50)
    await advance(31)
    assert state(hass) == "job_ongoing"
    await advance(600)
    fired(calls, job_resumed=1)


async def test_switching_off_during_the_startup_grace_keeps_the_job_paused(
    hass: HomeAssistant, monitor: Monitor, advance: Advance
) -> None:
    set_plug(hass, "on")
    calls = await boot(
        hass, monitor, plug_switch=PLUG, initial="paused", power=0, resume_grace={"seconds": 120}
    )
    await advance(60)
    set_plug(hass, "off")
    await advance(600)
    assert state(hass) == "paused"

    set_plug(hass, "on")
    await advance(121)
    assert state(hass) == "idle"
    fired(calls, abandoned=1)


async def test_a_paused_job_with_the_plug_still_off_stays_paused(
    hass: HomeAssistant, monitor: Monitor, advance: Advance
) -> None:
    set_plug(hass, "off")
    calls = await boot(hass, monitor, plug_switch=PLUG, initial="paused", power=0)
    await advance(900)

    assert state(hass) == "paused"
    fired(calls)


async def test_switching_off_during_the_startup_finish_delay_pauses_instead_of_completing(
    hass: HomeAssistant, monitor: Monitor, advance: Advance
) -> None:
    set_plug(hass, "on")
    calls = await boot(
        hass, monitor, plug_switch=PLUG, initial="job_ongoing", power=0.5, finish_delay={"seconds": 60}
    )
    await advance(20)
    set_plug(hass, "off")
    await advance(600)

    assert state(hass) == "paused"
    fired(calls, paused=1)


async def test_switching_off_during_the_startup_start_delay_unplugs_instead_of_starting(
    hass: HomeAssistant, monitor: Monitor, advance: Advance
) -> None:
    """The plug may report the switch before the power reading drops."""
    set_plug(hass, "on")
    calls = await boot(hass, monitor, plug_switch=PLUG, power=50, start_delay={"seconds": 60})
    await advance(20)
    set_plug(hass, "off")
    await advance(50)
    set_power(hass, 0)
    await advance(600)

    assert state(hass) == "unplugged"
    fired(calls, unplugged=1)


@pytest.mark.parametrize("plug_switch", [PLUG, OMIT], ids=["plug-on", "no-plug-switch"])
async def test_a_resume_at_startup_that_falls_short_still_gets_the_grace(
    hass: HomeAssistant, monitor: Monitor, advance: Advance, plug_switch: object
) -> None:
    set_plug(hass, "on")
    calls = await boot(
        hass,
        monitor,
        plug_switch=plug_switch,
        initial="paused",
        power=50,
        start_delay={"seconds": 30},
        resume_grace={"seconds": 120},
    )
    await advance(10)
    set_power(hass, 0)
    await advance(115)
    assert state(hass) == "paused"

    await advance(20)
    assert state(hass) == "idle"
    fired(calls, abandoned=1)


async def test_switching_off_during_a_resume_at_startup_keeps_the_job_paused(
    hass: HomeAssistant, monitor: Monitor, advance: Advance
) -> None:
    set_plug(hass, "on")
    calls = await boot(
        hass,
        monitor,
        plug_switch=PLUG,
        initial="paused",
        power=50,
        start_delay={"seconds": 30},
        resume_grace={"seconds": 120},
    )
    await advance(10)
    set_plug(hass, "off")
    await advance(600)

    assert state(hass) == "paused"
    fired(calls)


async def test_a_short_burst_of_power_during_the_startup_grace_does_not_cancel_it(
    hass: HomeAssistant, monitor: Monitor, advance: Advance
) -> None:
    set_plug(hass, "on")
    calls = await boot(
        hass,
        monitor,
        plug_switch=PLUG,
        initial="paused",
        power=0,
        start_delay={"seconds": 30},
        resume_grace={"seconds": 120},
    )
    await advance(20)
    set_power(hass, 50)
    await advance(10)
    set_power(hass, 0)
    await advance(85)
    assert state(hass) == "paused"

    await advance(10)
    assert state(hass) == "idle"
    fired(calls, abandoned=1)
