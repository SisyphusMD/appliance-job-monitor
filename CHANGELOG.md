# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project adheres
to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

- The CI and AI review callers hand the owner's read-only `PROJECT_RULES_TOKEN` to the shared jobs, which will read the owner's private `.project-rules` manifest (SisyphusMD/project-rules#143).
- CI and AI review call project-rules' shared workflows instead of carrying copies of the jobs (#35).
- Run the gate scripts and the rules from project-rules main instead of this repo's copies (copies drift) (#33).
- Bring the AI review copy up to project-rules 72f8fcc (an answer cut off while still reasoning is asked once more under the answer schema) (#31).
- Bring the AI review copy up to project-rules 64b857c (connect retry, malformed-answer re-ask, pinned checkout) (#29).
- New blueprint imports use the latest published Forgejo release (#21).

- Require the final release PR head to match the commit that passed Prepare Release (#19).

## [0.1.1] - 2026-11-17

- Prepare stable releases through a changelog PR, then tag the exact merged commit (#14).
- CI checks that every pull-request test job keeps its AGit and fork trust gate (#12).
- Pull requests opened on the GitHub mirror are closed with a pointer to Forgejo, where this
  repo takes them (#5).
- The test suite fails unless some test takes every trigger, condition branch and state
  transition in the blueprint, read from Home Assistant's own run traces (#7).
- The repo follows the SisyphusMD project rules: their required checks and AI review, issue
  templates, a `SECURITY.md` for private vulnerability reports, and its own test workflow
  renamed to `Tests` (#5).

## [0.1.0] - 2026-10-20

### Added

- A Home Assistant automation blueprint that tracks a washer, dryer or dishwasher through its jobs
  from its smart plug's power reading, keeping the state in a dropdown helper with six options:
  idle, job_ongoing, paused, job_completed, unplugged and detached_overload.
- Optional plug switch: a job switched off midway is paused instead of finished, resumes when the
  appliance draws power again, and is abandoned after a grace period otherwise.
- Optional overload sensor: a job cut off by an overload trip is marked as such and handled like a
  paused job.
- Actions for each step: job started, resumed, finished, paused, abandoned, unplugged and cut off
  by overload.
- A persistent notification naming what to fix when the setup is incomplete or invalid.
