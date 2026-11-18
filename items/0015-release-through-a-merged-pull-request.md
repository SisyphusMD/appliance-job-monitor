# #15 Release through a merged pull request

- Kind: pull, state: closed, by cody, created 2026-11-17T15:09:53-08:00
- Labels: none; milestone: none
- refs/pull/15/head -> main, merged: True

Closes #14.

Prepare Release qualifies the changelog promotion and opens a normal, issue-linked release PR. Publish Release checks that the merged PR matches the qualified tree and pushes only an annotated tag at that exact commit. The existing tag-triggered artifact publisher still attaches the blueprint to all three releases.

Vendors the verifier and tag-only publisher from project-rules v0.3.1. The local fixture covers branch-only preparation, cross-run reuse, refusal when main advances during qualification, tagging after main advances, and replay without changing main.

Validated: 104 tests and all 60 blueprint branches on each Home Assistant target, YAML and Python lint, shellcheck, documentation links, standard lock, and Gitleaks.

## forgejo-actions, 2026-11-17T15:12:48-08:00

<!-- ai-review -->
**AI review** of `81c917c03b`: The PR restructures the release process into a two-step flow (Prepare Release opens a changelog PR; Publish Release verifies the merged PR and tags the exact commit). The implementation is sound: input validation, tree/commit verification, idempotent replay, and write-token isolation are all correct, and the local fixture covers the key scenarios described in the PR body.

No findings.

Disagree? Reply on this PR with your reasoning; the reviewer re-reads every reply.
<!-- ai-review-state W10= -->
