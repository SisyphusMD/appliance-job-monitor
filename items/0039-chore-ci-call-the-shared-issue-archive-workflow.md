# #39 chore(ci): call the shared issue-archive workflow

- Kind: pull, state: closed, by cody, created 2026-11-27T07:11:14-08:00
- Labels: none; milestone: none
- refs/pull/39/head -> main, merged: True

Replaces the copied issue-archive job with the caller from project-rules main and deletes the copied script, which no longer runs.

Closes #38


## forgejo-actions, 2026-11-27T07:15:40-08:00

<!-- ai-review -->
**AI review** of `4aa0326786`: Clean, focused change that replaces the copied issue-archive job with a caller to project-rules' shared workflow, deletes the now-unused script, preserves schedule/concurrency/secrets, and adds a CHANGELOG entry. No issues found.

No findings.

Disagree? Reply on this PR with your reasoning; the reviewer re-reads every reply.
<!-- ai-review-state W10= -->
