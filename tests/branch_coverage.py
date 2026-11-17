"""Which of the blueprint's branches the suite takes, read from Home Assistant's run traces.

A branch is a trace path and the outcome recorded there: each trigger firing; each `if` taken and
not taken (with or without an `else`); each `choose` option, plus its default or, where it has none,
no option matching; and each `condition` step inside a sequence both passing and stopping the run.
Taking every branch runs every action, so every state transition, at least once.

Two deliberate limits. The conditions listed under an `if` or a `choose` option are judged as a
whole, passing or not, rather than each one separately. A wait's outcome (finished or timed out)
is covered through the `if` or `condition` step that follows every wait in the blueprint.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.util.yaml.loader import parse_yaml

Branch = tuple[str, Any]

TAKEN: set[Branch] = set()
DESELECTED = 0
SUMMARY = ""
MISSING: list[str] = []


def branches(blueprint: Path) -> dict[Branch, str]:
    """Every branch the blueprint has, each with a description that locates it."""
    config = parse_yaml(blueprint.read_text())
    found: dict[Branch, str] = {}
    # By index, not id: four triggers share the id `recheck`.
    for idx, trigger in enumerate(config["triggers"]):
        found[(f"trigger/{idx}", None)] = f"{_line(trigger)}: trigger {trigger.get('id', idx)}"
    _walk(config["actions"], "action", found)
    return found


def _line(node: Any) -> str:
    return f"line {getattr(node, '__line__', '?')}"


def _walk(steps: Any, path: str, found: dict[Branch, str]) -> None:
    if not isinstance(steps, list):
        return  # a sequence the user supplies through an input
    for idx, step in enumerate(steps):
        here = f"{path}/{idx}"
        # Anchored steps report the line of their definition, so the path tells reuses apart.
        where = f"{_line(step)}: {here}"
        if "if" in step:
            found[(f"{here}/if", True)] = f"{where} if, then"
            found[(f"{here}/if", False)] = f"{where} if, {'else' if 'else' in step else 'not taken'}"
            _walk(step["then"], f"{here}/then", found)
            _walk(step.get("else"), f"{here}/else", found)
        elif "choose" in step:
            for option_idx, option in enumerate(step["choose"]):
                found[(here, option_idx)] = f"{_line(option)}: {here} choose option {option_idx}"
                _walk(option["sequence"], f"{here}/choose/{option_idx}/sequence", found)
            if "default" in step:
                found[(here, "default")] = f"{where} choose default"
                _walk(step["default"], f"{here}/default", found)
            else:
                found[(here, None)] = f"{where} choose, no option matching"
        elif "condition" in step:
            found[(here, True)] = f"{where} condition passing"
            found[(here, False)] = f"{where} condition stopping the run"
        elif "sequence" in step:
            _walk(step["sequence"], f"{here}/sequence", found)
        elif step.keys() & {"repeat", "parallel", "while", "until"}:
            raise NotImplementedError(f"{where}: teach branch_coverage.py this step's branches")


def taken(hass: HomeAssistant) -> set[Branch]:
    """The trace path and outcome of every step in every stored automation run.

    A `choose` records the option taken as its choice, and nothing when none matched; an `if`
    records its test under `<path>/if`; a condition step records its result.
    """
    found: set[Branch] = set()
    for bucket in hass.data.get("trace", {}).values():
        # Newer releases keep not-triggered evaluations beside the runs.
        for trace in getattr(bucket, "runs", bucket).values():
            run = trace.as_extended_dict()
            # A run cancelled while a `choose` was testing its options also records no choice.
            finished = run["script_execution"] == "finished"
            for path, elements in run["trace"].items():
                for element in elements:
                    result = element.get("result") or {}
                    outcome = result.get("choice", result.get("result"))
                    if outcome is not None or finished or path.startswith("trigger/"):
                        found.add((path, outcome))
    return found
