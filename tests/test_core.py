"""Starting and finishing a job from the power reading alone."""

from __future__ import annotations

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

from .conftest import AUTOMATION, OMIT, Advance, Monitor, set_power, state


async def test_a_job_starts_only_after_power_stays_high_for_the_start_delay(
    hass: HomeAssistant, monitor: Monitor, advance: Advance
) -> None:
    calls = await monitor(start_delay={"seconds": 5})

    set_power(hass, 50)
    await advance(4)
    assert state(hass) == "idle"
    assert not calls["on_job_started"]

    await advance(2)
    assert state(hass) == "job_ongoing"
    assert len(calls["on_job_started"]) == 1


async def test_a_job_finishes_only_after_power_stays_low_for_the_finish_delay(
    hass: HomeAssistant, monitor: Monitor, advance: Advance
) -> None:
    calls = await monitor(initial="job_ongoing", power=50, finish_delay={"seconds": 180})

    set_power(hass, 1)
    await advance(170)
    assert state(hass) == "job_ongoing"

    await advance(20)
    assert state(hass) == "job_completed"
    assert len(calls["on_job_completed"]) == 1


async def test_a_dip_shorter_than_the_finish_delay_never_touches_the_state(
    hass: HomeAssistant, monitor: Monitor, advance: Advance
) -> None:
    calls = await monitor(initial="job_ongoing", power=50, finish_delay={"seconds": 60})
    written = []
    hass.bus.async_listen(
        "state_changed",
        lambda event: written.append(event) if event.data["entity_id"].startswith("input_select") else None,
    )

    for _ in range(3):
        set_power(hass, 1)
        await advance(30)
        set_power(hass, 50)
        await advance(30)

    assert state(hass) == "job_ongoing"
    assert not written, "a short dip wrote to the state helper"
    assert not calls["on_job_completed"]
    assert not calls["on_job_started"], "power rising again mid-job announced a new job"


async def test_a_full_cycle_runs_each_action_once(hass: HomeAssistant, monitor: Monitor, advance: Advance) -> None:
    calls = await monitor()

    set_power(hass, 50)
    await advance(1)
    set_power(hass, 0.5)
    await advance(11)
    assert state(hass) == "job_completed"

    set_power(hass, 40)
    await advance(1)
    assert state(hass) == "job_ongoing", "a completed appliance could not start its next job"
    assert len(calls["on_job_started"]) == 2
    assert len(calls["on_job_completed"]) == 1


async def test_attribute_only_updates_do_not_run_the_automation(
    hass: HomeAssistant, monitor: Monitor, advance: Advance
) -> None:
    """A Zigbee plug republishes link quality without the power value changing."""
    await monitor(initial="job_ongoing", power=50)
    last_run = hass.states.get(AUTOMATION).attributes.get("last_triggered")

    for quality in range(10):
        set_power(hass, 50, linkquality=quality)
        await advance(1)

    assert hass.states.get(AUTOMATION).attributes.get("last_triggered") == last_run


async def test_an_unavailable_sensor_leaves_a_running_job_alone(
    hass: HomeAssistant, monitor: Monitor, advance: Advance
) -> None:
    calls = await monitor(initial="job_ongoing", power=50)

    set_power(hass, "unavailable")
    await advance(600)

    assert state(hass) == "job_ongoing"
    assert not calls["on_job_completed"]


async def test_custom_state_labels_are_written_and_read(
    hass: HomeAssistant, monitor: Monitor, advance: Advance
) -> None:
    await monitor(
        labels=["Off", "Running", "Done"],
        initial="Off",
        label_running="Running",
        label_completed="Done",
    )

    set_power(hass, 50)
    await advance(1)
    assert state(hass) == "Running"

    set_power(hass, 0)
    await advance(11)
    assert state(hass) == "Done"


async def test_a_failing_action_cannot_leave_the_state_behind(
    hass: HomeAssistant, monitor: Monitor, advance: Advance
) -> None:
    async def broken(call: object) -> None:
        raise HomeAssistantError("notification service is down")

    hass.services.async_register("test", "broken", broken)
    await monitor(on_job_started=[{"action": "test.broken"}])

    set_power(hass, 50)
    await advance(1)

    assert state(hass) == "job_ongoing"


async def test_a_reading_that_passed_while_an_action_ran_is_not_acted_on_later(
    hass: HomeAssistant, monitor: Monitor, advance: Advance
) -> None:
    """Runs queue, so a slow action holds back triggers that fired meanwhile."""
    calls = await monitor(
        initial="job_ongoing",
        power=50,
        on_job_completed=[{"delay": {"seconds": 30}}, {"action": "test.job_completed"}],
    )
    set_power(hass, 0.5)
    await advance(11)
    set_power(hass, 50)
    await advance(5)
    set_power(hass, 0.5)
    await advance(30)

    assert state(hass) == "job_completed"
    assert len(calls["on_job_completed"]) == 1
    assert not calls["on_job_started"], "a spike that had already passed started a job"


async def test_only_the_two_required_inputs_are_needed(
    hass: HomeAssistant, monitor: Monitor, advance: Advance
) -> None:
    await monitor(on_job_started=[], on_job_completed=[])

    set_power(hass, 50)
    await advance(1)
    assert state(hass) == "job_ongoing"
    set_power(hass, 0)
    await advance(11)
    assert state(hass) == "job_completed"


@pytest.mark.parametrize("missing", ["power_sensor", "state_select"])
async def test_a_missing_required_input_is_refused(
    hass: HomeAssistant, monitor: Monitor, missing: str
) -> None:
    await monitor(**{missing: OMIT})

    automation = hass.states.get(AUTOMATION)
    assert automation is not None and automation.state == "unavailable"
