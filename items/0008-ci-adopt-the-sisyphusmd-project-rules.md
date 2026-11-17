# #8 ci: adopt the SisyphusMD project rules

- Kind: pull, state: closed, by cody, created 2026-11-17T11:18:04-08:00
- Labels: none; milestone: none
- refs/pull/8/head -> main, merged: True

Refs #5 (stays open: main is protected only after the new checks are proven on the next PR, and after SisyphusMD/project-rules#86, since the Release workflow pushes straight to main).

This repo ran its own tests but none of the project rules' gates. It now carries them, copied verbatim from project-rules main 664d0e7:

- `ci.yml` (Issue link, Tests with code, Diff size, Lint, Secrets), `ai-review.yml`, `issue-archive.yml`, `.forgejo/scripts/`, the issue templates, and `RULES.md` as `.forgejo/RULES.md` for the AI review.
- The repo's own workflow is renamed `ci.yml` to `tests.yml` (`name: Tests`) so the two don't collide; `release.yml`'s comment follows.
- `SECURITY.md` from the template; CONTRIBUTING points at the rules, notes rule 9 (no AI attribution), and lists the required checks under the exact names Forgejo reports, plus break-glass.
- `ruff.toml` excludes the copied scripts and vendored `packaging/`: ruff 0.17's defaults flag them and the copied Lint job runs `ruff check .` (SisyphusMD/project-rules#85). Renovate ignores the copied workflows, which change only by re-copying.

The `pull_request_target` gates run from the base, so they don't run on this PR. They are proven on the next one (one pass, one deliberate failure) before they are required.

Checked locally: 98 tests pass, yamllint strict, CI's pinned ruff 0.17.5 in a clean venv, shellcheck, doc links, standard sync.

Large diff: about 1,100 lines are verbatim copies of project-rules files (scripts, workflows, rules text, templates); the repo-specific change is under 100 lines.

Follow-ups from review: SisyphusMD/project-rules#86 and #87, and #7 here (blueprint coverage).
