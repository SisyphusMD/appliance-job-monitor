# #9 test: fail CI when a blueprint branch has no test

- Kind: pull, state: closed, by cody, created 2026-11-17T12:19:46-08:00
- Labels: none; milestone: none
- refs/pull/9/head -> main, merged: True

Closes #7

The rules ask for coverage, and nothing measured it for the blueprint: a branch could go untested without anyone noticing. Now a whole-suite test run fails unless every branch in the blueprint is taken by some test.

How: `tests/branch_coverage.py` lists the blueprint's branches from its YAML (each trigger by index, both outcomes of every `if`, each `choose` option plus "nothing matched", and each `condition` step passing and stopping). `conftest.py` keeps every automation run's Home Assistant trace and records the step paths and outcomes each test took. At the end of a full run, any branch nothing took is listed by blueprint line and the run fails. A run that cannot be judged (paths given, tests deselected or failed, collect-only) says "Blueprint branch coverage NOT checked" and why, so it never looks like a pass. A "nothing matched" outcome counts only from a run that finished, not one stopped mid-step. `repeat`, `parallel`, `while` and `until` raise, so a new construct cannot slip past uncounted.

It found two real gaps, both now tested: an overload that clears while power is high but drops within the start delay, on a paused job and on an unplugged appliance (`test_power_that_falls_within_the_start_delay_after_a_trip_clears_*`). Each new test fails when its condition is forced.

Proof it fails: with `test_a_sensor_that_does_not_cut_power_resumes_once_it_clears` skipped, both floor (2024.10) and latest (2026.10) exit 1 with `line 475: action/2/choose/9/sequence/1 condition passing` and "59 of 60 branches taken". Unmodified, both print "All 60 blueprint branches taken." with 100 passed.

## forgejo-actions, 2026-11-17T12:22:56-08:00

<!-- ai-review -->
**AI review** of `b116f1fbd3`: Well-designed branch coverage enforcement for the blueprint YAML, correctly reading HA run traces and gating on whole-suite runs. The two new tests cover real gaps the checker found, docs are updated in the same PR, and the implementation correctly handles all step types the blueprint uses.

No findings.

Disagree? Reply on this PR with your reasoning; the reviewer re-reads every reply.
<!-- ai-review-state W10= -->
