"""Every job a pull request can start carries the trust gate, or is named here with the reason."""

from __future__ import annotations

from pathlib import Path

# PyYAML is installed with the Home Assistant test environment.
import yaml

WORKFLOWS = Path(__file__).resolve().parents[1] / ".forgejo" / "workflows"
# Both clauses: a fork PR fails the first, and an AGit PR (pushed to refs/for/<branch>) reports this
# repo as its head, so only the second turns it away.
GATE = (
    "github.event.pull_request.head.repo.full_name == github.repository",
    "github.event.pull_request.flow == 0",
)
# Recognize the job gate as a whole so wrapping just one clause in an OR can't
# pass the test.
TRUSTED = " && ".join(GATE)
TRUSTED_CONDITIONS = {
    TRUSTED,
    f"github.event_name != 'pull_request' || ({TRUSTED})",
    f"github.event_name == 'pull_request' && {TRUSTED}",
}
# (workflow file, job id) -> why the job may run for an outside pull request.
UNGATED: dict[tuple[str, str], str] = {}


def pull_request_jobs(workflows: Path) -> dict[tuple[str, str], str]:
    """Collect the normalized job conditions for `pull_request` workflows.

    `pull_request_target` workflows run main's copy and read the PR only as data, so they are out
    of scope here (project-rules#57).
    """
    found = {}
    for path in sorted(workflows.glob("*.y*ml")):
        document = yaml.safe_load(path.read_text()) or {}
        triggers = document.get("on", document.get(True)) or {}
        if "pull_request" not in (triggers if isinstance(triggers, (dict, list)) else [triggers]):
            continue
        for job, spec in (document.get("jobs") or {}).items():
            condition = " ".join(str((spec or {}).get("if", "")).split())
            condition = condition.removeprefix("${{").removesuffix("}}").strip()
            found[(path.name, job)] = condition
    return found


def test_every_pull_request_job_is_gated_or_named() -> None:
    jobs = pull_request_jobs(WORKFLOWS)
    assert {("tests.yml", "lint"), ("tests.yml", "test")} <= jobs.keys()
    found = {job for job, condition in jobs.items() if condition not in TRUSTED_CONDITIONS}
    missing = sorted(found - UNGATED.keys())
    assert not missing, (
        f"pull_request jobs an outside or AGit pull request can run: {missing}. Gate them on "
        f"`{GATE[0]} && {GATE[1]}`, or name the job and the reason in UNGATED."
    )
    stale = sorted(UNGATED.keys() - found)
    assert not stale, f"UNGATED names jobs that are gated or gone: {stale}"


def test_a_job_without_its_gate_is_caught(tmp_path: Path) -> None:
    gated = "github.event_name != 'pull_request' || (" + " && ".join(GATE) + ")"
    (tmp_path / "ci.yml").write_text(
        yaml.safe_dump(
            {
                "on": {"pull_request": None, "push": {"branches": ["main"]}},
                "jobs": {
                    "gated": {"if": gated, "runs-on": "x"},
                    "no_if": {"runs-on": "x"},
                    "fork_only": {"if": GATE[0], "runs-on": "x"},
                    "agit_only": {"if": GATE[1], "runs-on": "x"},
                    "either": {"if": " || ".join(GATE), "runs-on": "x"},
                },
            }
        )
    )
    (tmp_path / "target.yml").write_text(
        yaml.safe_dump({"on": {"pull_request_target": None}, "jobs": {"t": {"runs-on": "x"}}})
    )
    jobs = pull_request_jobs(tmp_path)
    assert all(workflow == "ci.yml" for workflow, _ in jobs)
    assert {job for (_, job), condition in jobs.items() if condition not in TRUSTED_CONDITIONS} == {
        "agit_only",
        "either",
        "fork_only",
        "no_if",
    }
