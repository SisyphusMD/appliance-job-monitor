"""A configuration that cannot work is reported once and writes nothing."""

from __future__ import annotations

import pytest
from homeassistant.components import persistent_notification
from homeassistant.core import CoreState, HomeAssistant

from .conftest import (
    AUTOMATION,
    OVERLOAD,
    PLUG,
    SELECT,
    Advance,
    Monitor,
    fired,
    set_power,
    settle,
    state,
)

NOTIFICATION = f"appliance_job_monitor_{AUTOMATION}"


def notification(hass: HomeAssistant) -> str | None:
    found = persistent_notification._async_get_or_create_notifications(hass).get(NOTIFICATION)
    return None if found is None else found["message"]


async def boot(hass: HomeAssistant, monitor: Monitor, **kwargs: object) -> dict:
    """Set up while Home Assistant is still starting, then finish starting it."""
    hass.set_state(CoreState.not_running)
    calls = await monitor(**kwargs)
    await hass.async_start()
    await settle()
    return calls


async def test_a_valid_configuration_raises_no_notification(
    hass: HomeAssistant, monitor: Monitor, advance: Advance
) -> None:
    await boot(hass, monitor, plug_switch=PLUG, overload_sensor=OVERLOAD)

    assert notification(hass) is None


@pytest.mark.parametrize(
    ("inputs", "labels", "expected"),
    [
        ({}, ["idle", "job_completed"], 'The Running label "job_ongoing" is not an option of input_select.washer_state.'),
        ({"plug_switch": PLUG}, ["job_ongoing", "job_completed", "idle", "unplugged"], 'The Paused label "paused"'),
        ({"overload_sensor": OVERLOAD}, ["job_ongoing", "job_completed", "idle", "unplugged"], 'Cut off by overload label'),
        ({"overload_sensor": OVERLOAD}, ["job_ongoing", "job_completed", "unplugged", "detached_overload"], 'The Idle label'),
        ({"label_completed": "job_ongoing"}, ["job_ongoing"], "Each state label must be different."),
        ({"finish_threshold": 5}, None, "The finish threshold (5 W) must be below the start threshold (5 W)."),
        ({"state_select": "input_select.missing"}, None, "The state helper input_select.missing was not found."),
    ],
    ids=["running", "paused", "overload", "idle", "duplicate", "thresholds", "helper"],
)
async def test_a_broken_configuration_is_reported_and_writes_nothing(
    hass: HomeAssistant,
    monitor: Monitor,
    advance: Advance,
    inputs: dict,
    labels: list[str] | None,
    expected: str,
) -> None:
    initial = labels[0] if labels else "idle"
    calls = await boot(hass, monitor, labels=labels, initial=initial, **inputs)

    assert expected in (notification(hass) or "")

    set_power(hass, 50)
    await advance(600)
    set_power(hass, 0)
    await advance(600)
    assert state(hass) == initial
    fired(calls)


async def test_labels_a_configuration_cannot_reach_are_not_required(
    hass: HomeAssistant, monitor: Monitor, advance: Advance
) -> None:
    await boot(hass, monitor, labels=["job_ongoing", "job_completed"], initial="job_completed")

    assert notification(hass) is None


async def test_the_notification_names_the_automation(
    hass: HomeAssistant, monitor: Monitor, advance: Advance
) -> None:
    await boot(hass, monitor, finish_threshold=10)

    found = persistent_notification._async_get_or_create_notifications(hass)[NOTIFICATION]
    assert found["title"] == "Washer monitor is not running"


async def test_a_dismissed_notification_is_not_raised_again_by_power_readings(
    hass: HomeAssistant, monitor: Monitor, advance: Advance
) -> None:
    await boot(hass, monitor, finish_threshold=10)
    persistent_notification.async_dismiss(hass, NOTIFICATION)

    for watts in (50, 0, 50, 0):
        set_power(hass, watts)
        await advance(60)

    assert notification(hass) is None


async def test_fixing_the_helper_options_clears_the_notification_and_starts_monitoring(
    hass: HomeAssistant, monitor: Monitor, advance: Advance
) -> None:
    calls = await boot(hass, monitor, plug_switch=PLUG, labels=["idle", "job_ongoing", "job_completed"])
    assert 'The Paused label "paused"' in (notification(hass) or "")

    await hass.services.async_call(
        "input_select",
        "set_options",
        {"entity_id": SELECT, "options": ["idle", "job_ongoing", "paused", "job_completed", "unplugged"]},
        blocking=True,
    )
    await advance(1)
    assert notification(hass) is None

    set_power(hass, 50)
    await advance(1)
    assert state(hass) == "job_ongoing"
    fired(calls, job_started=1)


async def test_breaking_the_helper_options_later_is_reported(
    hass: HomeAssistant, monitor: Monitor, advance: Advance
) -> None:
    await boot(hass, monitor)
    assert notification(hass) is None

    await hass.services.async_call(
        "input_select", "set_options", {"entity_id": SELECT, "options": ["idle", "job_completed"]}, blocking=True
    )
    await advance(1)

    assert 'The Running label "job_ongoing"' in (notification(hass) or "")


async def test_labels_that_differ_only_in_case_are_different_states(
    hass: HomeAssistant, monitor: Monitor, advance: Advance
) -> None:
    """Home Assistant compares states case-sensitively."""
    calls = await boot(
        hass, monitor, labels=["RUNNING", "running"], initial="running", label_running="RUNNING", label_completed="running"
    )
    assert notification(hass) is None

    set_power(hass, 50)
    await advance(1)
    assert state(hass) == "RUNNING"
    set_power(hass, 0)
    await advance(11)
    assert state(hass) == "running"
    fired(calls, job_started=1, job_completed=1)
