# #25 AI review: 40-minute deadline inside a 45-minute job

- Kind: pull, state: closed, by cody, created 2026-11-19T17:41:10-08:00
- Labels: none; milestone: none
- refs/pull/25/head -> main, merged: True

Closes #24

Sync from SisyphusMD/project-rules#108 (byte-identical copies of the script and workflow; tests live there). A 40-minute deadline from the review's start ends a slow review with an error status instead of the job being killed at 20 minutes with the required check left pending. The job limit is now 45 minutes.

## cody, 2026-11-19T18:10:04-08:00

Retry: the review errored reaching the model (HTTPError) while 12 reviews were queued on the Studio.

## cody, 2026-11-19T18:13:28-08:00

Retry: second URLError reaching the model while the Studio queue drained.

## forgejo-actions, 2026-11-19T18:14:22-08:00

<!-- ai-review -->
**AI review** of `bd39066ba0`: Clean sync of the AI review script and workflow from project-rules#108: adds a 40-minute signal-based deadline inside a 45-minute job so the required check always gets a terminal status instead of staying pending when the job is killed. Error handling is restructured to a catch-all that guarantees a status write; signal handling is correct (alarm cancelled in finally before any status write, Deadline not an OSError so urllib won't wrap it).

No findings.

Disagree? Reply on this PR with your reasoning; the reviewer re-reads every reply.
<!-- ai-review-state W10= -->
