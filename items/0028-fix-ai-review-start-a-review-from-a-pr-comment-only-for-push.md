# #28 fix(ai-review): start a review from a PR comment only for pushers and the PR author

- Kind: pull, state: closed, by cody, created 2026-11-21T11:50:19-08:00
- Labels: none; milestone: none
- refs/pull/28/head -> main, merged: True

Closes #27

Copies the canonical `ai-review.yml` from SisyphusMD/project-rules #117 unchanged. A PR comment now starts an AI review only when its author can push to this repo or wrote the PR; before, any signed-in account's comment queued a run of up to 45 minutes on the Studio model. `pull_request_target` runs are unchanged. The gate reads `github.event.repository.permissions.push`, which Forgejo fills with the commenter's own permission, checked against stored run payloads (bots with push still start reviews).

The test that rejects an outside commenter lives with the canonical file: project-rules `tests/test_ai_review_gate.py`.

## forgejo-actions, 2026-11-21T11:53:26-08:00

<!-- ai-review -->
**AI review** of `bfecf95e30`: The PR copies the canonical ai-review.yml unchanged from project-rules #117, adding a gate so only pushers or the PR author can trigger an AI review via a PR comment. The condition logic is correct, the diff is minimal and focused, the issue is linked, and the test lives with the canonical file in project-rules as stated.

No findings.

Disagree? Reply on this PR with your reasoning; the reviewer re-reads every reply.
<!-- ai-review-state W10= -->
