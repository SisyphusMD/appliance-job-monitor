"""Switching the plug off and on: paused, unplugged, resumed and abandoned jobs."""

from __future__ import annotations

import pytest
from homeassistant.core import HomeAssistant

from .conftest import PLUG, Advance, Monitor, fired, set_plug, set_power, state


async def relay_monitor(monitor: Monitor, **kwargs: object) -> dict:
    return await monitor(plug_switch=PLUG, **kwargs)


@pytest.fixture(autouse=True)
def plug_on(hass: HomeAssistant) -> None:
    set_plug(hass, "on")


async def test_switching_a_running_job_off_pauses_it_and_never_completes_it(
    hass: HomeAssistant, monitor: Monitor, advance: Advance
) -> None:
    calls = await relay_monitor(monitor, initial="job_ongoing", power=50)

    set_plug(hass, "off")
    await advance(1)
    set_power(hass, 0)
    await advance(600)

    assert state(hass) == "paused"
    fired(calls, paused=1)


async def test_zero_watts_reported_just_before_the_switch_still_pauses(
    hass: HomeAssistant, monitor: Monitor, advance: Advance
) -> None:
    """A plug may report the power drop before the relay change."""
    calls = await relay_monitor(monitor, initial="job_ongoing", power=50)

    set_power(hass, 0)
    await advance(0.2)
    set_plug(hass, "off")
    await advance(600)

    assert state(hass) == "paused"
    fired(calls, paused=1)


async def test_a_paused_job_that_draws_power_again_resumes(
    hass: HomeAssistant, monitor: Monitor, advance: Advance
) -> None:
    calls = await relay_monitor(monitor, initial="job_ongoing", power=50)
    set_plug(hass, "off")
    set_power(hass, 0)
    await advance(60)

    set_plug(hass, "on")
    await advance(120)
    set_power(hass, 50)
    await advance(1)
    assert state(hass) == "job_ongoing"

    await advance(600)
    assert state(hass) == "job_ongoing", "a resumed job was abandoned by the earlier switch on"
    fired(calls, paused=1, job_resumed=1)


async def test_a_paused_job_that_never_resumes_is_abandoned_after_the_grace(
    hass: HomeAssistant, monitor: Monitor, advance: Advance
) -> None:
    calls = await relay_monitor(
        monitor, initial="job_ongoing", power=50, resume_grace={"seconds": 120}
    )
    set_plug(hass, "off")
    set_power(hass, 0)
    await advance(60)

    set_plug(hass, "on")
    await advance(110)
    assert state(hass) == "paused"

    await advance(20)
    assert state(hass) == "idle"
    fired(calls, paused=1, abandoned=1)


async def test_switching_off_again_during_the_grace_keeps_the_job_paused(
    hass: HomeAssistant, monitor: Monitor, advance: Advance
) -> None:
    calls = await relay_monitor(
        monitor, initial="job_ongoing", power=50, resume_grace={"seconds": 120}
    )
    set_plug(hass, "off")
    set_power(hass, 0)
    await advance(1)
    set_plug(hass, "on")
    await advance(60)
    set_plug(hass, "off")
    await advance(600)

    assert state(hass) == "paused"
    fired(calls, paused=1)


@pytest.mark.parametrize("initial", ["idle", "job_completed"])
async def test_switching_off_with_no_job_running_unplugs_and_switching_on_returns_to_idle(
    hass: HomeAssistant, monitor: Monitor, advance: Advance, initial: str
) -> None:
    calls = await relay_monitor(monitor, initial=initial, power=0.5)

    set_plug(hass, "off")
    await advance(1)
    assert state(hass) == "unplugged"

    set_plug(hass, "on")
    await advance(600)
    assert state(hass) == "idle"
    fired(calls, unplugged=1)


async def test_a_job_started_after_switching_back_on_is_a_new_job(
    hass: HomeAssistant, monitor: Monitor, advance: Advance
) -> None:
    calls = await relay_monitor(monitor, initial="job_completed", power=0.5)
    set_plug(hass, "off")
    await advance(1)
    set_plug(hass, "on")
    await advance(1)

    set_power(hass, 50)
    await advance(1)
    await advance(300)

    assert state(hass) == "job_ongoing"
    fired(calls, unplugged=1, job_started=1)


async def test_power_while_unplugged_starts_a_job_when_the_switch_reading_is_stale(
    hass: HomeAssistant, monitor: Monitor, advance: Advance
) -> None:
    calls = await relay_monitor(monitor, initial="unplugged", power=0.5)
    set_plug(hass, "unavailable")

    set_power(hass, 50)
    await advance(1)

    assert state(hass) == "job_ongoing"
    fired(calls, job_started=1)


async def test_a_completion_and_a_switch_off_in_quick_succession_both_run(
    hass: HomeAssistant, monitor: Monitor, advance: Advance
) -> None:
    calls = await relay_monitor(monitor, initial="job_ongoing", power=50)
    set_power(hass, 0.5)
    await advance(10)
    await advance(0.5)
    set_plug(hass, "off")
    await advance(1)

    assert state(hass) == "unplugged"
    fired(calls, job_completed=1, unplugged=1)


async def test_custom_labels_cover_the_relay_states(
    hass: HomeAssistant, monitor: Monitor, advance: Advance
) -> None:
    labels = {
        "label_idle": "Off",
        "label_running": "Running",
        "label_paused": "On hold",
        "label_completed": "Done",
        "label_unplugged": "No power",
        "label_overload": "Tripped",
    }
    await relay_monitor(
        monitor, labels=list(labels.values()), initial="Done", resume_grace={"seconds": 60}, **labels
    )

    set_plug(hass, "off")
    await advance(1)
    assert state(hass) == "No power"
    set_plug(hass, "on")
    await advance(1)
    assert state(hass) == "Off"

    set_power(hass, 50)
    await advance(1)
    set_plug(hass, "off")
    await advance(1)
    assert state(hass) == "On hold"
    set_plug(hass, "on")
    set_power(hass, 0)
    await advance(61)
    assert state(hass) == "Off"


async def test_a_resume_and_a_second_switch_off_during_a_slow_action_apply_in_order(
    hass: HomeAssistant, monitor: Monitor, advance: Advance
) -> None:
    """The grace period running out while queued must not abandon a job that had resumed."""
    calls = await relay_monitor(
        monitor,
        initial="job_ongoing",
        power=50,
        resume_grace={"seconds": 120},
        on_paused=[{"delay": {"seconds": 600}}, {"action": "test.paused"}],
    )
    set_plug(hass, "off")
    set_power(hass, 0)
    await advance(10)
    set_plug(hass, "on")
    await advance(10)
    set_power(hass, 50)
    await advance(180)
    set_plug(hass, "off")
    set_power(hass, 0)
    await advance(600)
    await advance(600)

    assert state(hass) == "paused"
    fired(calls, paused=2, job_resumed=1)
