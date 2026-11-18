# #16 Release appliance-job-monitor v0.1.1

- Kind: issue, state: closed, by cody, created 2026-11-17T15:23:32-08:00
- Labels: status:in-progress, type:chore; milestone: none

Cut the first patch release using the two-step Forgejo flow added in #15. Prepare the changelog PR, review and merge it, publish the exact merge by tag, and verify the blueprint assets on primary, annex and GitHub. The results inform the branch protection work in #5.

## cody, 2026-11-17T15:23:32-08:00

Decision by Cody (2026-11-17): “Yes” to publishing appliance-job-monitor v0.1.1 now to test the new release workflow. Codex is running the release.

## cody, 2026-11-17T15:27:12-08:00

Released v0.1.1 through the new hosted workflow. Prepare Release #49 created changelog-only PR #17 without changing main or creating the tag. After green CI and normal merge, Publish Release #54 tagged the exact merge at 4286feb00c0627d6070163bc1e3e8dc8b607fa29. Publish #55 and tag Tests #56 passed. Primary, annex and GitHub have the same annotated tag and both blueprint uploads match SHA-256 85005a60ffd46649a3cf3e534e81af7ddbadcb68f04d05709b311642d10c5d79. The release branch has been pruned.
