# #26 chore: default blueprint imports to the latest Forgejo release

- Kind: pull, state: closed, by cody, created 2026-11-20T00:15:20-08:00
- Labels: none; milestone: none
- refs/pull/26/head -> main, merged: True

Closes #21

New installs, the import badge and the blueprint `source_url` now point at the Forgejo latest release alias, which serves v0.1.1 byte-for-byte. Existing GitHub imports keep working; the README explains how to switch one (edit `source_url`, reload automations so HA drops the cached URL, re-import). A metadata test pins the URL in the blueprint and both README spots.

Checks: Ruff, yamllint and diff check locally; both pinned HA suites passed before the rebase onto main (main only changed AI review scripts). Cold review (cx) findings fixed: reload step added, unrelated CONTRIBUTING link dropped.

## forgejo-actions, 2026-11-20T00:16:54-08:00

<!-- ai-review -->
**AI review** of `553fe5ca59`: Clean, focused PR that switches blueprint import URLs from the GitHub mirror to the Forgejo latest-release alias, updates the README with migration instructions for existing imports, and adds a metadata test pinning the URL in the blueprint and both README locations. All changes serve issue #21; the test would fail without the fix; no issues found.

No findings.

Disagree? Reply on this PR with your reasoning; the reviewer re-reads every reply.
<!-- ai-review-state W10= -->
