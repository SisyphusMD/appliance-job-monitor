# #4 chore: vendor the shared standard from SisyphusMD/project-rules 0.2.0

- Kind: pull, state: closed, by cody, created 2026-11-16T16:43:26-08:00
- Labels: none; milestone: none
- refs/pull/4/head -> main, merged: True

## What and why

SisyphusMD/project-standard is retired into SisyphusMD/project-rules (project-rules#22). This re-vendors from project-rules v0.2.0 and moves every pointer to it: `STANDARD.lock` (source repo, v0.2.0, 156f8c1), `release-pins.env` (`PROJECT_STANDARD="0.2.0"`, `depName=SisyphusMD/project-rules`), the `.renovaterc.json` package rule, and the CONTRIBUTING, VARIANCE and CI comment links.

The pin was still at 0.1.28, so this also catches up nine releases. For the 16 files this repo takes, that is: `revendor-standard.sh` (bounded clone with a watchdog, and the new repo URL), `gitignore.base` (release and smoke output patterns, now added to `.gitignore`), and the drift message in `check-standard-sync.py`. Same change landed in SisyphusMD/whiskerless#177 and SisyphusMD/dreame-valetudo#279.

## Checks

- `check-standard-sync.py`: 16 files match v0.2.0
- `check-gitignore-base.py`, `check-doc-links.py`, `shellcheck-all.sh`, `yamllint --strict`: pass
- pytest: 98 passed
- No regression test: no behaviour change in this repo's own code.
