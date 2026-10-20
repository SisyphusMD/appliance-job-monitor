# Deliberate differences from the SisyphusMD standard

[project-standard](https://forgejo.bryantserver.com/SisyphusMD/project-standard) was written for
Python projects that ship packages. This repository ships one Home Assistant blueprint file. Each
difference below is intended; anything not listed here is drift.

## Vendors a subset of the standard

`packaging/project.env` sets `STANDARD_FILES`, so only the release and hygiene helpers are
vendored and locked. The Python packaging, Homebrew, PyPI and glibc tooling has nothing to act on
here.

## Python, typing and packaging conventions do not apply

There is no Python package, so CONVENTIONS sections 1, 2, 8 and 10 do not apply, nor do the
installed-artifact rows of section 5. Tests load the blueprint into a real Home Assistant instead;
the supported Home Assistant floor and the latest release are both tested.

## License is MIT, not AGPL

archiver and GhostSpectator are AGPL-3.0. A blueprint is configuration people copy into their own
instance, so MIT matches what Home Assistant users expect. The reasoning is in
[CONTRIBUTING.md](CONTRIBUTING.md).

## No sibling repository

whiskerless and dreame-valetudo are converged siblings. This repository has none, so the pull
request template's sibling checklist is answered "not applicable".

## CI is lint plus two test suites

The siblings' CI also builds release artifacts, installs them across a matrix of platforms and
waits for native macOS runs. This repository builds nothing: the released file is the blueprint
itself, so CI lints it and tests it on the oldest and newest supported Home Assistant.

## Releases carry the blueprint under a stable name too

Each release attaches `appliance-job-monitor.yaml` beside the versioned file. Both forges resolve
a latest-release download only by exact asset name, and Home Assistant's re-import follows the
blueprint's `source_url`, so that name has to stay the same from release to release.

## No release candidates or dependency notes

The siblings cut `-rc` candidates to put on hardware before a stable release, and list the
dependency bumps in their release notes. Here the Home Assistant test suites are the hardware
check, and every pinned dependency is test or CI tooling that never reaches the installed file,
so there is no prerelease workflow and the notes are the CHANGELOG alone.
