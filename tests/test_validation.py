"""A configuration that cannot work is reported once and writes nothing."""

from __future__ import annotations

from unittest.mock import patch

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
    automation_config,
    fired,
    set_power,
    settle,
    state,
)

NOTIFICATION = f"appliance_job_monitor_{AUTOMATION}"


DEFAULT_ORDER = ["idle", "job_ongoing", "paused", "job_completed", "unplugged", "detached_overload"]


def options(hass: HomeAssistant) -> list[str]:
    return hass.states.get(SELECT).attributes["options"]


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
    ("inputs", "expected"),
    [
        (
            {"labels": ["idle", "job_ongoing", "job_completed"]},
            "Add these options to input_select.washer_state: paused, unplugged, detached_overload",
        ),
        (
            {"labels": ["idle", "Washing", "job_completed", "paused", "unplugged", "detached_overload"]},
            "Add these options to input_select.washer_state: job_ongoing",
        ),
        ({"label_running": "Washing"}, "Add these options to input_select.washer_state: Washing"),
        ({"label_completed": "job_ongoing"}, "Each state label must be different."),
        ({"finish_threshold": 5}, "The finish threshold (5 W) must be below the start threshold (5 W)."),
        ({"state_select": "input_select.missing"}, "The state helper input_select.missing was not found."),
    ],
    ids=["unused-states-still-required", "missing-one", "custom-label", "duplicate", "thresholds", "helper"],
)
async def test_a_broken_configuration_is_reported_and_writes_nothing(
    hass: HomeAssistant, monitor: Monitor, advance: Advance, inputs: dict, expected: str
) -> None:
    calls = await boot(hass, monitor, **inputs)
    await advance(1)

    assert expected in (notification(hass) or "")

    set_power(hass, 50)
    await advance(600)
    set_power(hass, 0)
    await advance(600)
    assert state(hass) == "idle"
    fired(calls)


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


async def test_fixing_the_configuration_clears_the_notification(
    hass: HomeAssistant, monitor: Monitor, advance: Advance
) -> None:
    calls = await boot(hass, monitor, finish_threshold=10)
    await advance(1)
    assert notification(hass) is not None

    with patch("homeassistant.config.load_yaml_config_file", return_value=automation_config()):
        await hass.services.async_call("automation", "reload", blocking=True)
    await advance(1)
    assert notification(hass) is None

    set_power(hass, 50)
    await advance(1)
    assert state(hass) == "job_ongoing"
    fired(calls, job_started=1)


async def test_adding_the_missing_options_clears_the_notification_and_starts_monitoring(
    hass: HomeAssistant, monitor: Monitor, advance: Advance
) -> None:
    calls = await boot(hass, monitor, labels=["idle", "job_ongoing", "job_completed"])
    await advance(1)
    assert notification(hass) is not None

    await hass.services.async_call(
        "input_select", "set_options", {"entity_id": SELECT, "options": DEFAULT_ORDER}, blocking=True
    )
    await advance(1)
    assert notification(hass) is None

    set_power(hass, 50)
    await advance(1)
    assert state(hass) == "job_ongoing"
    fired(calls, job_started=1)


async def test_removing_options_later_is_reported(
    hass: HomeAssistant, monitor: Monitor, advance: Advance
) -> None:
    await boot(hass, monitor)
    await advance(1)
    assert notification(hass) is None

    await hass.services.async_call(
        "input_select", "set_options", {"entity_id": SELECT, "options": ["idle", "job_completed"]}, blocking=True
    )
    await advance(1)

    assert "paused" in (notification(hass) or "")
    assert options(hass) == ["idle", "job_completed"], "the helper's options were changed"


async def test_labels_that_differ_only_in_case_are_different_states(
    hass: HomeAssistant, monitor: Monitor, advance: Advance
) -> None:
    """Home Assistant compares states case-sensitively."""
    calls = await boot(
        hass,
        monitor,
        labels=["RUNNING", "running", "idle", "paused", "unplugged", "detached_overload"],
        initial="running",
        label_running="RUNNING",
        label_completed="running",
    )
    await advance(1)
    assert notification(hass) is None
    assert state(hass) == "running"

    set_power(hass, 50)
    await advance(1)
    assert state(hass) == "RUNNING"
    set_power(hass, 0)
    await advance(11)
    assert state(hass) == "running"
    fired(calls, job_started=1, job_completed=1)
