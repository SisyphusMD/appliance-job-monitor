"""An overload sensor: jobs cut off by a trip, and how they resume or are abandoned."""

from __future__ import annotations

import pytest
from homeassistant.core import CoreState, HomeAssistant

from .conftest import (
    OVERLOAD,
    PLUG,
    Advance,
    Monitor,
    fired,
    set_overload,
    set_plug,
    set_power,
    settle,
    state,
)


@pytest.fixture(autouse=True)
def healthy_plug(hass: HomeAssistant) -> None:
    set_plug(hass, "on")
    set_overload(hass, "off")


async def overload_monitor(monitor: Monitor, **kwargs: object) -> dict:
    return await monitor(plug_switch=PLUG, overload_sensor=OVERLOAD, **kwargs)


async def trip_and_cut(hass: HomeAssistant, advance: Advance) -> None:
    """A plug that cuts its own relay on overload: the trip, the relay and the power drop."""
    set_overload(hass, "on")
    set_plug(hass, "off")
    set_power(hass, 0)
    await advance(600)


@pytest.mark.parametrize("initial", ["job_ongoing", "paused"])
async def test_a_trip_cuts_off_an_interrupted_or_running_job_and_never_completes_it(
    hass: HomeAssistant, monitor: Monitor, advance: Advance, initial: str
) -> None:
    calls = await overload_monitor(monitor, initial=initial, power=50 if initial == "job_ongoing" else 0)

    await trip_and_cut(hass, advance)

    assert state(hass) == "detached_overload"
    fired(calls, overload=1)


@pytest.mark.parametrize("initial", ["idle", "job_completed"])
async def test_a_trip_with_no_job_running_unplugs_until_it_clears(
    hass: HomeAssistant, monitor: Monitor, advance: Advance, initial: str
) -> None:
    calls = await overload_monitor(monitor, initial=initial, power=0.5)
    set_overload(hass, "on")
    await advance(1)
    assert state(hass) == "unplugged"

    set_plug(hass, "off")
    set_plug(hass, "on")
    await advance(1)
    assert state(hass) == "unplugged", "switching on while still tripped left unplugged"

    set_overload(hass, "off")
    await advance(600)
    assert state(hass) == "idle"
    fired(calls, unplugged=1)


async def test_switching_the_plug_while_tripped_changes_nothing(
    hass: HomeAssistant, monitor: Monitor, advance: Advance
) -> None:
    calls = await overload_monitor(monitor, initial="job_ongoing", power=50)
    await trip_and_cut(hass, advance)

    for relay in ("on", "off", "on", "off"):
        set_plug(hass, relay)
        await advance(600)

    assert state(hass) == "detached_overload"
    fired(calls, overload=1)


@pytest.mark.parametrize("cleared_first", [True, False], ids=["overload-clears-first", "plug-on-first"])
async def test_a_tripped_job_that_draws_power_again_resumes(
    hass: HomeAssistant, monitor: Monitor, advance: Advance, cleared_first: bool
) -> None:
    calls = await overload_monitor(monitor, initial="job_ongoing", power=50)
    await trip_and_cut(hass, advance)

    for change in ((set_overload, "off"), (set_plug, "on")) if cleared_first else ((set_plug, "on"), (set_overload, "off")):
        change[0](hass, change[1])
        await advance(1)
    set_power(hass, 50)
    await advance(1)
    assert state(hass) == "job_ongoing"

    await advance(600)
    assert state(hass) == "job_ongoing"
    fired(calls, overload=1, job_resumed=1)


@pytest.mark.parametrize("cleared_first", [True, False], ids=["overload-clears-first", "plug-on-first"])
async def test_a_tripped_job_that_never_resumes_is_abandoned_after_the_grace(
    hass: HomeAssistant, monitor: Monitor, advance: Advance, cleared_first: bool
) -> None:
    calls = await overload_monitor(monitor, initial="job_ongoing", power=50, resume_grace={"seconds": 120})
    await trip_and_cut(hass, advance)

    for change in ((set_overload, "off"), (set_plug, "on")) if cleared_first else ((set_plug, "on"), (set_overload, "off")):
        change[0](hass, change[1])
        await advance(10)
    await advance(100)
    assert state(hass) == "detached_overload"

    await advance(20)
    assert state(hass) == "idle"
    fired(calls, overload=1, abandoned=1)


async def test_switching_off_after_the_trip_clears_waits_for_the_plug_and_stays_cut_off(
    hass: HomeAssistant, monitor: Monitor, advance: Advance
) -> None:
    calls = await overload_monitor(monitor, initial="job_ongoing", power=50, resume_grace={"seconds": 120})
    set_overload(hass, "on")
    set_power(hass, 0)
    await advance(1)
    set_overload(hass, "off")
    await advance(60)

    set_plug(hass, "off")
    await advance(600)
    assert state(hass) == "detached_overload"

    set_plug(hass, "on")
    await advance(110)
    assert state(hass) == "detached_overload"
    await advance(11)
    assert state(hass) == "idle"
    fired(calls, overload=1, abandoned=1)


async def test_a_sensor_that_does_not_cut_power_resumes_once_it_clears(
    hass: HomeAssistant, monitor: Monitor, advance: Advance
) -> None:
    """Power never stopped, so there is no crossing for the usual start trigger to see."""
    calls = await overload_monitor(monitor, initial="job_ongoing", power=50, start_delay={"seconds": 5})
    set_overload(hass, "on")
    await advance(60)
    assert state(hass) == "detached_overload"

    set_overload(hass, "off")
    await advance(4)
    assert state(hass) == "detached_overload"
    await advance(2)
    assert state(hass) == "job_ongoing"
    await advance(600)
    fired(calls, overload=1, job_resumed=1)


async def test_power_returning_while_still_tripped_resumes_the_job(
    hass: HomeAssistant, monitor: Monitor, advance: Advance
) -> None:
    calls = await overload_monitor(monitor, initial="job_ongoing", power=50)
    set_overload(hass, "on")
    set_power(hass, 0)
    await advance(60)

    set_power(hass, 50)
    await advance(1)
    assert state(hass) == "job_ongoing"

    set_overload(hass, "off")
    await advance(600)
    assert state(hass) == "job_ongoing"
    fired(calls, overload=1, job_resumed=1)


async def test_custom_label_for_a_trip(hass: HomeAssistant, monitor: Monitor, advance: Advance) -> None:
    await overload_monitor(
        monitor,
        labels=["idle", "job_ongoing", "paused", "job_completed", "unplugged", "Tripped"],
        initial="job_ongoing",
        power=50,
        label_overload="Tripped",
    )

    await trip_and_cut(hass, advance)

    assert state(hass) == "Tripped"


async def boot(hass: HomeAssistant, monitor: Monitor, **kwargs: object) -> dict:
    hass.set_state(CoreState.not_running)
    calls = await overload_monitor(monitor, **kwargs)
    await hass.async_start()
    await settle()
    return calls


@pytest.mark.parametrize(
    ("initial", "expected", "hook"),
    [
        ("job_ongoing", "detached_overload", "overload"),
        ("paused", "detached_overload", "overload"),
        ("idle", "unplugged", "unplugged"),
        ("job_completed", "unplugged", "unplugged"),
        ("detached_overload", "detached_overload", None),
    ],
)
async def test_a_trip_while_home_assistant_was_down_is_applied(
    hass: HomeAssistant, monitor: Monitor, advance: Advance, initial: str, expected: str, hook: str | None
) -> None:
    set_overload(hass, "on")
    set_plug(hass, "off")
    calls = await boot(hass, monitor, initial=initial, power=0)
    await advance(900)

    assert state(hass) == expected
    fired(calls, **({hook: 1} if hook else {}))


async def test_a_cleared_trip_with_the_plug_off_at_startup_waits_for_the_plug(
    hass: HomeAssistant, monitor: Monitor, advance: Advance
) -> None:
    set_plug(hass, "off")
    calls = await boot(hass, monitor, initial="detached_overload", power=0, resume_grace={"seconds": 120})
    await advance(900)
    assert state(hass) == "detached_overload"
    fired(calls)

    set_plug(hass, "on")
    await advance(121)
    assert state(hass) == "idle"
    fired(calls, abandoned=1)


@pytest.mark.parametrize(("power", "expected", "hook"), [(0, "idle", "abandoned"), (50, "job_ongoing", "job_resumed")])
async def test_a_cleared_trip_at_startup_resumes_or_is_abandoned(
    hass: HomeAssistant, monitor: Monitor, advance: Advance, power: float, expected: str, hook: str
) -> None:
    calls = await boot(hass, monitor, initial="detached_overload", power=power, resume_grace={"seconds": 120})
    await advance(110)
    if power == 0:
        assert state(hass) == "detached_overload"
    await advance(20)

    assert state(hass) == expected
    fired(calls, **{hook: 1})


@pytest.mark.parametrize(
    ("initial", "power", "expected", "hook"),
    [("job_ongoing", 0.5, "detached_overload", "overload"), ("idle", 50, "unplugged", "unplugged")],
    ids=["finish-delay", "start-delay"],
)
async def test_a_trip_during_a_startup_delay_is_applied_instead(
    hass: HomeAssistant, monitor: Monitor, advance: Advance, initial: str, power: float, expected: str, hook: str
) -> None:
    calls = await boot(
        hass, monitor, initial=initial, power=power, start_delay={"seconds": 60}, finish_delay={"seconds": 60}
    )
    await advance(20)
    set_overload(hass, "on")
    await advance(600)

    assert state(hass) == expected
    fired(calls, **{hook: 1})


async def test_a_trip_during_the_startup_grace_cuts_the_job_off(
    hass: HomeAssistant, monitor: Monitor, advance: Advance
) -> None:
    calls = await boot(hass, monitor, initial="paused", power=0, resume_grace={"seconds": 120})
    await advance(60)
    set_overload(hass, "on")
    await advance(600)

    assert state(hass) == "detached_overload"
    fired(calls, overload=1)


async def test_a_trip_during_a_resume_at_startup_cuts_the_job_off(
    hass: HomeAssistant, monitor: Monitor, advance: Advance
) -> None:
    calls = await boot(
        hass, monitor, initial="paused", power=50, start_delay={"seconds": 30}, resume_grace={"seconds": 120}
    )
    await advance(10)
    set_overload(hass, "on")
    await advance(600)

    assert state(hass) == "detached_overload"
    fired(calls, overload=1)


async def test_a_resume_and_a_second_trip_during_a_slow_action_apply_in_order(
    hass: HomeAssistant, monitor: Monitor, advance: Advance
) -> None:
    """The grace period running out while queued must not abandon a job that had resumed."""
    calls = await overload_monitor(
        monitor,
        initial="job_ongoing",
        power=50,
        resume_grace={"seconds": 120},
        on_overload=[{"delay": {"seconds": 600}}, {"action": "test.overload"}],
    )
    set_overload(hass, "on")
    set_power(hass, 0)
    await advance(10)
    set_overload(hass, "off")
    await advance(10)
    set_power(hass, 50)
    await advance(180)
    set_overload(hass, "on")
    set_power(hass, 0)
    await advance(600)
    await advance(600)

    assert state(hass) == "detached_overload"
    fired(calls, overload=2, job_resumed=1)


async def test_an_overload_clearing_on_a_switched_off_plug_stays_unplugged(
    hass: HomeAssistant, monitor: Monitor, advance: Advance
) -> None:
    calls = await overload_monitor(monitor, power=0.5)
    set_plug(hass, "off")
    await advance(1)
    set_overload(hass, "on")
    await advance(1)
    set_overload(hass, "off")
    await advance(600)

    assert state(hass) == "unplugged"
    fired(calls, unplugged=1)


async def test_the_grace_runs_from_the_overload_clearing_when_that_comes_last(
    hass: HomeAssistant, monitor: Monitor, advance: Advance
) -> None:
    calls = await overload_monitor(
        monitor,
        initial="job_ongoing",
        power=50,
        resume_grace={"seconds": 120},
        on_overload=[{"delay": {"seconds": 600}}, {"action": "test.overload"}],
    )
    await trip_and_cut(hass, advance)
    set_plug(hass, "on")
    await advance(10)
    set_overload(hass, "off")
    await advance(1)
    await advance(100)
    assert state(hass) == "detached_overload", "abandoned before the grace after the trip cleared"

    await advance(20)
    assert state(hass) == "idle"
    fired(calls, overload=1, abandoned=1)


async def test_power_already_flowing_when_a_trip_clears_on_an_unplugged_appliance_starts_a_job(
    hass: HomeAssistant, monitor: Monitor, advance: Advance
) -> None:
    """A sensor that does not cut power: the reading stays high, so there is no crossing."""
    set_overload(hass, "on")
    calls = await boot(hass, monitor, power=50, start_delay={"seconds": 5})
    await advance(60)
    assert state(hass) == "unplugged"

    set_overload(hass, "off")
    await advance(4)
    assert state(hass) == "idle"
    await advance(2)
    assert state(hass) == "job_ongoing"
    await advance(300)
    assert state(hass) == "job_ongoing"
    fired(calls, unplugged=1, job_started=1)
