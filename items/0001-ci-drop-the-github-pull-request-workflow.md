# #1 ci: drop the GitHub pull request workflow

- Kind: pull, state: closed, by cody, created 2026-11-16T09:56:20-08:00
- Labels: none; milestone: none
- ci/drop-github-pr-ci -> main, merged: True

Step 1 of the GitHub runner exit. GitHub is a read-only mirror with no CI, so ci-pr.yml goes; Forgejo ci.yml already runs the same lint and both Home Assistant suites. The fork-gate comment no longer points at the deleted file. ci-pr.yml never ran on GitHub (0 runs).
