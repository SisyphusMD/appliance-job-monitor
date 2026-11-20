# #21 Default blueprint imports to the latest Forgejo release

- Kind: issue, state: closed, by cody, created 2026-11-18T06:33:49-08:00
- Labels: status:in-progress, type:chore; milestone: none

Use the primary release asset in the install badge, manual import and blueprint source URL. Preserve re-import of the latest stable release.

## cody, 2026-11-18T06:53:21-08:00

The badge, manual URL and blueprint source now agree in the local patch. The latest Forgejo asset matches the bytes of v0.1.1. Both pinned Home Assistant test environments pass all 105 tests and exercise all 60 blueprint branches. The raw public request currently returns HTTP 500. Landing waits for a successful public blueprint import.

## cody, 2026-11-20T00:12:26-08:00

Status (2026-11-20, session rotating): the public-route blocker is fixed (bryantserver/k8s#2617, deployed). This repo's forgejo-defaults change (5 files) is still uncommitted in its worktree, 4 commits behind main. It is first of the four forgejo-defaults PRs; the next session picks it up.


## cody, 2026-11-20T00:15:27-08:00

Claude (rotated Casa session) has this. Gateway premise cleared by bryantserver/k8s#2617. PR #26 open; cx review findings fixed (reload-automations step, CONTRIBUTING hunk dropped).

## cody, 2026-11-20T00:18:48-08:00

Done: PR #26 merged at 3f1fcc4 (all 10 contexts green on 553fe5c), GitHub and NAS mirrors match, branch and worktree removed. Takes effect for users at the next release; the Forgejo latest alias serves v0.1.1 today.
