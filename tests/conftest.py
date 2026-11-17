"""Load the shipped blueprint into a real Home Assistant and drive it through fake entities."""

from __future__ import annotations

# Lets the frozen clock drive Home Assistant's timers. The latest harness loads this itself; the
# 2024.10 floor harness ships it without loading it, so its timers would never come due.
import pytest_homeassistant_custom_component.patch_time  # noqa: F401  # isort: skip

import asyncio
import shutil
from collections.abc import Awaitable, Callable, Iterator
from datetime import timedelta
from pathlib import Path
from typing import Any

import pytest
from freezegun.api import FrozenDateTimeFactory
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.setup import async_setup_component
from pytest_homeassistant_custom_component.common import (
    async_fire_time_changed,
    async_mock_service,
)

from . import branch_coverage

ROOT = Path(__file__).resolve().parent.parent
BLUEPRINT = ROOT / "blueprints" / "automation" / "sisyphusmd" / "appliance-job-monitor.yaml"
BLUEPRINT_PATH = "sisyphusmd/appliance-job-monitor.yaml"

POWER = "sensor.washer_power"
SELECT = "input_select.washer_state"
PLUG = "switch.washer_plug"
OVERLOAD = "binary_sensor.washer_plug_overload"
AUTOMATION = "automation.washer_monitor"
# Passed as an input value to leave that input out entirely, so a default would apply.
OMIT = object()
HOOKS = ["job_started", "job_resumed", "job_completed", "paused", "abandoned", "unplugged", "overload"]
DEFAULT_LABELS = ["idle", "job_ongoing", "paused", "job_completed", "unplugged", "detached_overload"]


@pytest.fixture(autouse=True)
def blueprint_dir(hass: HomeAssistant, tmp_path: Path) -> None:
    """Point the config dir at a scratch tree holding the blueprint, as an import would."""
    hass.config.config_dir = str(tmp_path)
    target = tmp_path / "blueprints" / "automation" / BLUEPRINT_PATH
    target.parent.mkdir(parents=True)
    shutil.copy2(BLUEPRINT, target)


@pytest.fixture(autouse=True)
def record_branches(hass: HomeAssistant) -> Iterator[None]:
    """Note which blueprint branches this test's automation runs took.

    Home Assistant stores no trace for an automation without an id, so a test of one counts for
    nothing here.
    """
    yield
    branch_coverage.TAKEN.update(branch_coverage.taken(hass))


def pytest_deselected(items: list[pytest.Item]) -> None:
    branch_coverage.DESELECTED += len(items)


@pytest.hookimpl(wrapper=True)
def pytest_runtestloop(session: pytest.Session) -> Iterator[None]:
    """Fail a whole-suite run in which some branch of the blueprint was never taken.

    Only a run of the whole suite from the repository root, the way CI runs it, is checked: one
    narrowed by paths, -k, -m or deselection is not meant to cover everything, and one with
    failures already fails. The summary says which happened. A skipped test takes no branches.
    """
    result = yield
    config = session.config
    if config.option.collectonly:
        reason = "collect-only"
    elif config.args_source != pytest.Config.ArgsSource.TESTPATHS:
        reason = "test paths given (needs a whole-suite run from the repository root)"
    elif branch_coverage.DESELECTED:
        reason = f"{branch_coverage.DESELECTED} tests deselected"
    elif session.testsfailed:
        reason = f"{session.testsfailed} tests failed"
    else:
        expected = branch_coverage.branches(BLUEPRINT)
        branch_coverage.MISSING = [
            where for branch, where in expected.items() if branch not in branch_coverage.TAKEN
        ]
        if branch_coverage.MISSING:
            session.testsfailed += 1
        taken = len(expected) - len(branch_coverage.MISSING)
        branch_coverage.SUMMARY = (
            f"Blueprint branch coverage: {taken} of {len(expected)} branches taken."
            if branch_coverage.MISSING
            else f"All {len(expected)} blueprint branches taken."
        )
        return result
    branch_coverage.SUMMARY = f"Blueprint branch coverage NOT checked: {reason}."
    return result


def pytest_terminal_summary(terminalreporter: pytest.TerminalReporter) -> None:
    if branch_coverage.MISSING:
        terminalreporter.section("Blueprint branches no test takes", red=True)
        for where in branch_coverage.MISSING:
            terminalreporter.write_line(where)
    if branch_coverage.SUMMARY:
        terminalreporter.write_line(branch_coverage.SUMMARY)


def set_power(hass: HomeAssistant, watts: float | str, **attributes: Any) -> None:
    hass.states.async_set(
        POWER, str(watts), {"unit_of_measurement": "W", "device_class": "power", **attributes}
    )


def set_plug(hass: HomeAssistant, state: str) -> None:
    hass.states.async_set(PLUG, state)


def set_overload(hass: HomeAssistant, state: str) -> None:
    hass.states.async_set(OVERLOAD, state)


def fired(calls: dict[str, list[ServiceCall]], **expected: int) -> None:
    """Assert how often each hook ran; every hook not named must not have run."""
    assert {hook: len(calls[f"on_{hook}"]) for hook in HOOKS} == {
        hook: expected.get(hook, 0) for hook in HOOKS
    }


Advance = Callable[[float], Awaitable[None]]


async def settle() -> None:
    """Run everything that is ready now, without waiting for automation runs to finish.

    `hass.async_block_till_done()` waits for every running automation, so it deadlocks against
    a run that is waiting on a timer only this test's clock can fire.
    """
    for _ in range(50):
        await asyncio.sleep(0)


@pytest.fixture
def advance(hass: HomeAssistant, freezer: FrozenDateTimeFactory) -> Advance:
    """Move the frozen clock forward and run everything that comes due."""

    async def tick(seconds: float) -> None:
        # Settle first: on older releases a state change reaches its listeners on the next loop
        # iteration, so a `for:` countdown started by it would otherwise begin after the jump.
        await settle()
        freezer.tick(timedelta(seconds=seconds))
        async_fire_time_changed(hass)
        await settle()

    return tick


def automation_config(automation_id: Any = "washer_monitor", **inputs: Any) -> dict[str, Any]:
    """One automation from the blueprint, with test hooks unless the inputs override them."""
    blueprint_inputs: dict[str, Any] = {
        "power_sensor": POWER,
        "state_select": SELECT,
        **{f"on_{hook}": [{"action": f"test.{hook}"}] for hook in HOOKS},
        **inputs,
    }
    blueprint_inputs = {k: v for k, v in blueprint_inputs.items() if v is not OMIT}
    automation = {
        "id": automation_id,
        "alias": "Washer monitor",
        # Enough to keep every run of a test, for the branch coverage check.
        "trace": {"stored_traces": 1000},
        "use_blueprint": {"path": BLUEPRINT_PATH, "input": blueprint_inputs},
    }
    return {"automation": {k: v for k, v in automation.items() if v is not OMIT}}


Monitor = Callable[..., Awaitable[dict[str, list[ServiceCall]]]]


@pytest.fixture
def monitor(hass: HomeAssistant) -> Monitor:
    """Create the state helper, a power reading and one automation from the blueprint.

    Returns the calls recorded by each hook, keyed by hook name. Extra keyword arguments become
    blueprint inputs, overriding the hooks too when given.
    """

    async def setup(
        *, labels: list[str] | None = None, initial: str = "idle", power: float = 0, **inputs: Any
    ) -> dict[str, list[ServiceCall]]:
        options = labels or DEFAULT_LABELS
        # A core integration that Home Assistant always loads; the test harness does not.
        assert await async_setup_component(hass, "persistent_notification", {})
        assert await async_setup_component(
            hass,
            "input_select",
            {"input_select": {"washer_state": {"options": options, "initial": initial}}},
        )
        set_power(hass, power)
        calls = {f"on_{hook}": async_mock_service(hass, "test", hook) for hook in HOOKS}
        assert await async_setup_component(hass, "automation", automation_config(**inputs))
        await settle()
        return calls

    return setup


def state(hass: HomeAssistant) -> str:
    current = hass.states.get(SELECT)
    assert current is not None
    return current.state
