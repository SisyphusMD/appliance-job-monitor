# #34 chore(gate): run the gate scripts and rules from project-rules main

- Kind: pull, state: closed, by cody, created 2026-11-24T19:11:33-08:00
- Labels: none; milestone: none
- refs/pull/34/head -> main, merged: True

Closes #33

This repo ran its own copies of the gate scripts and kept a copy of the rules for the AI review, and copies drift. `ci.yml` and `ai-review.yml` now fetch the scripts and `RULES.md` from project-rules main on every run and fail when they cannot (SisyphusMD/project-rules#78). The gate jobs and `ai-review.yml` are project-rules main's (6a6d41b4), and the copies are removed in the same change, so no run is left without either.

mirror-lockdown.yml is copied again for its source header.

Large diff: 889 of the removed lines are the deleted copies, and the added workflow lines come from project-rules main, where they were reviewed and tested.


## forgejo-actions, 2026-11-24T19:15:42-08:00

<!-- ai-review -->
**AI review** of `db852b6c5d`: The PR correctly switches ci.yml and ai-review.yml to fetch gate scripts and rules from project-rules main, removes the four local script copies and .forgejo/RULES.md, adds the source header to mirror-lockdown.yml, and records the change in the CHANGELOG. The workflow changes are sound: the gate fetch fails closed, the new 'Hold the check' step prevents stale statuses, and the checkout/SHA handling for git-diff-based scripts is preserved. The Large diff justification is valid (889 deleted lines are the removed copies).

No findings.

Disagree? Reply on this PR with your reasoning; the reviewer re-reads every reply.
<!-- ai-review-state W10= -->
