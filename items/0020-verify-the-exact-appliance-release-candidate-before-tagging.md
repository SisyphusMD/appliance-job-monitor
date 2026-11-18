# #20 Verify the exact Appliance release candidate before tagging

- Kind: pull, state: closed, by cody, created 2026-11-17T19:08:22-08:00
- Labels: none; milestone: none
- refs/pull/20/head -> main, merged: True

Closes #19.

Record the exact head that passed Prepare Release, then bind publication to the successful dispatch’s candidate record. Retry the already-published v0.1.1 only when the exact primary tag exists and its merge still verifies.

The release fixture rejects an incorrect qualification record even when a similarly named branch exists, and proves exact tag-only publication and legacy retry. Both Home Assistant dependency targets passed the full suite before the narrow exact-ref fix and both passed the focused release fixtures afterwards.

## forgejo-actions, 2026-11-17T19:11:02-08:00

<!-- ai-review -->
**AI review** of `90f49b7dc3`: The PR correctly binds release publication to the exact qualified commit by verifying a commit status, workflow run metadata, and job log content before tagging, with a safe retry path for already-published tags. Tests cover the happy path, rejection of a wrong qualification, and the legacy retry path.

No findings.

Disagree? Reply on this PR with your reasoning; the reviewer re-reads every reply.
<!-- ai-review-state W10= -->
