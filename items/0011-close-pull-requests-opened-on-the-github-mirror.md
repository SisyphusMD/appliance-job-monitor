# #11 Close pull requests opened on the GitHub mirror

- Kind: issue, state: closed, by cody, created 2026-11-17T12:35:15-08:00
- Labels: status:in-progress, type:feature; milestone: none

GitHub cannot turn pull requests off, so the read-only GitHub copy still takes them. Copy project-rules' `.github/workflows/mirror-lockdown.yml` (SisyphusMD/project-rules#88, #89) and turn Actions on for the GitHub copy, limited to that one action. Part of the adoption, #5.
