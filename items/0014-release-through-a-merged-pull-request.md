# #14 Release through a merged pull request

- Kind: issue, state: closed, by cody, created 2026-11-17T14:07:39-08:00
- Labels: status:blocked, type:feature; milestone: none

Part of SisyphusMD/project-rules#86. Keep the existing release qualification, open the changelog promotion as a pull request, then use a second maintainer dispatch to verify and tag exactly the merged release. Prove the preparation and tag-only stages before blocking direct pushes to main.

Depends on SisyphusMD/project-rules#96.

## cody, 2026-11-17T14:59:28-08:00

Prepare Release and Publish Release are drafted. Both Home Assistant suites passed (103 tests and all 60 blueprint branches on each target). A local Git/API fixture proved candidate-only push, idempotent PR reuse and refusal when main moves during qualification. The shared helpers must be vendored together from the official project-rules v0.3.1 release after publication.
