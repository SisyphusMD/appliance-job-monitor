# #12 Test the AGit and fork trust gate on every pull_request job

- Kind: issue, state: closed, by cody, created 2026-11-17T13:11:50-08:00
- Labels: status:in-progress, type:chore; milestone: none

Follow-up to the AGit gate (`github.event.pull_request.flow == 0` beside the head-repository check) and SisyphusMD/project-rules#79.

- Nothing tests the gate. Add a test that walks every job of every `pull_request`-triggered workflow under `.forgejo/workflows/` and fails unless its `if:` carries both clauses, with named exemptions and a reason for each. A job that loses its whole `if:` must fail it.
- `CONTRIBUTING.md` says an AGit pull request gets no CI. It should say the same of a pull request from a fork.

## cody, 2026-11-17T13:24:52-08:00

Status: test and CONTRIBUTING change written and green locally (102 passed, all 60 blueprint branches), not committed: the commit review had not finished when the session was handed off. Next: qx review, commit, push branch ci/agit-guard-followups, open the PR.

## cody, 2026-11-17T13:41:20-08:00

Merged in #13 at 9bff38e. All ten Forgejo contexts, including AI review and both Home Assistant legs, passed on the exact head before merge. Default-branch protection remains tracked under #5 and project-rules #86.
