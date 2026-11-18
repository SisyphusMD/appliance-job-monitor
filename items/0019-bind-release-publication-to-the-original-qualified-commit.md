# #19 Bind release publication to the original qualified commit

- Kind: issue, state: closed, by cody, created 2026-11-17T18:59:20-08:00
- Labels: status:in-progress, type:bug; milestone: none

Part of SisyphusMD/project-rules#99. Record the exact commit prepared by the qualification workflow, and verify that successful run still applies to the final merged release PR head before creating a new tag. Preserve safe retries of the already published v0.1.1 tag.
