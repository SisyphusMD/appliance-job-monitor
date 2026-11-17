# #13 Check the AGit and fork gate on every pull-request job

- Kind: pull, state: closed, by cody, created 2026-11-17T13:37:11-08:00
- Labels: none; milestone: none
- refs/pull/13/head -> main, merged: True

Closes #12

The workflow test scans jobs in every `pull_request` workflow and checks the complete trust condition. It verifies the existing lint and test jobs were inspected, so a missing workflow or unrecognized trigger cannot silently pass.

Tests: a fixture rejects a job without an `if:`, a job missing either trust clause, and a job joining the clauses with OR. The existing blueprint suites still exercise all 60 branches.

CONTRIBUTING describes the maintainer's branch PR process for AGit and fork contributions. The other repositories' guard changes are tracked separately in the follow-up to SisyphusMD/project-rules#79.


## forgejo-actions, 2026-11-17T13:38:51-08:00

<!-- ai-review -->
**AI review** of `297a87227a`: The PR adds a workflow guard test that walks every pull_request-triggered workflow and asserts each job carries both trust clauses (fork + AGit), with a fixture proving it catches missing/partial/OR-joined gates, and updates CONTRIBUTING.md to mention fork PRs alongside AGit. The implementation is correct, well-tested, and scoped to issue #12.

No findings.

Disagree? Reply on this PR with your reasoning; the reviewer re-reads every reply.
<!-- ai-review-state W10= -->
