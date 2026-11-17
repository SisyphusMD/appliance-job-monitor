# #5 Bring this repo under the project rules

- Kind: issue, state: open, by cody, created 2026-11-17T08:34:03-08:00
- Labels: status:in-progress, type:chore; milestone: none

Tracked in SisyphusMD/project-rules#73. Add the rules' gate workflows (issue link, tests with code, diff size, lint, secrets, AI review), the nightly issue archive, issue templates and labels, a synced .forgejo/RULES.md, and the CONTRIBUTING.md sections the template asks for. This repo's own CI moves to tests.yml so the rules' ci.yml can sit beside it, as in project-rules. Protection then requires each check once a PR has proven it.

## cody, 2026-11-17T08:41:41-08:00

Protection order (no required checks exist here yet, so nothing goes stale): merge the adoption PR with this repo's own Tests green (the rules' gates run from main via pull_request_target, so they cannot run on the PR that adds them). On the next PR, prove each new check passes once and fails once, then require the six standard contexts (CI / Issue link, Tests with code, Diff size, Lint, Secrets, AI review) plus Tests / Lint and repository checks and both Test on Home Assistant legs. Waiting on SisyphusMD/project-rules#77 so the .forgejo/RULES.md copy passes the doc-link check.

## cody, 2026-11-17T11:12:37-08:00

Protecting main waits on SisyphusMD/project-rules#86: the Release workflow pushes the changelog commit straight to main, so protection would break releases. Also open from review: SisyphusMD/project-rules#85 and #87 (CI hardening in the copied workflows), and #7 here (blueprint coverage).

## cody, 2026-11-17T12:23:50-08:00

Proof, pass half: PR #9 ran every required check under the exact names in CONTRIBUTING.md and all passed (CI / Issue link, Tests with code, Diff size, Lint, Secrets (pull_request_target); AI review; Tests / Lint and repository checks, Test on Home Assistant floor, Test on Home Assistant latest (pull_request)). Still to do: one deliberate failure per gate, then protect main once SisyphusMD/project-rules#86 lands. Also to add: .github/workflows/mirror-lockdown.yml (SisyphusMD/project-rules#89) with Actions enabled on the GitHub copy.

## cody, 2026-11-17T12:39:09-08:00

Proof, fail half so far: on PR #10, `CI / Issue link (pull_request_target)` failed with no issue in the description, and `AI review` blocked on rule 6 (Refs instead of Closes); both passed once fixed. Still to see fail: Tests with code, Diff size, Lint, Secrets, and the three Tests jobs. Mirror lockdown merged (#11) and GitHub Actions on, limited to that action, SHA pinning required, read-only token.

## cody, 2026-11-17T14:59:28-08:00

Local fixture proof succeeded for all seven remaining failure paths: Tests with code, Diff size, Lint, Secrets, repository lint and the Home Assistant floor and latest jobs. Used a synthetic secret marker and malformed blueprint in a temporary repository. The required hosted PR proof still needs to run before enabling protection, after the release path is safe.
