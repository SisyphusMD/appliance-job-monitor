# Contributing to appliance-job-monitor

Bug reports, power traces from real appliances and fixes are all welcome. Please open issues and
pull requests on [GitHub](https://github.com/SisyphusMD/appliance-job-monitor).

## Written from scratch

This blueprint replaces the
[leofabri appliance status monitor](https://github.com/leofabri/hassio_appliance-status-monitor),
which carries no license, so its code cannot be reused. Nothing here is copied or adapted from it
or from its forks. Contributions must be your own work, written against the Home Assistant
documentation and this repository, not against that blueprint's source. Matching its state names
is deliberate and fine; matching its code is not.

## Tests

The blueprint is tested in a real Home Assistant, on the oldest release it supports and on the
newest. With [uv](https://docs.astral.sh/uv/) installed:

```sh
packaging/run-tests.sh latest
packaging/run-tests.sh floor
```

A change to the blueprint comes with a test that fails without it. CI runs both suites, plus
yamllint, ruff and shellcheck, on every push and pull request.

Note user-visible changes under `## [Unreleased]` in `CHANGELOG.md`; that section becomes the
release notes.

## Releasing

Run the Release workflow on Forgejo from `main` and pick the bump. It reruns both test suites on
that commit, promotes `[Unreleased]`, and tags. The tag runs Publish, which attaches the blueprint
to the Forgejo, NAS and GitHub releases under two names with the same bytes:
`appliance-job-monitor-X.Y.Z.yaml`, and `appliance-job-monitor.yaml` for the latest-release
download link that the blueprint's `source_url` and the README's import button use. Dispatch
Publish with the tag as the ref to finish a publish that partly failed.

## License

MIT. The consumers are Home Assistant users, who import the blueprint into their own instance and
often adapt it. Copyleft would cost them nothing it could enforce, since nothing links against a
YAML file and nothing here is served over a network, but it would discourage the reuse in forum
answers that blueprints live on. Blueprints shared in the Home Assistant community are almost
always MIT, as is [whiskerless](https://github.com/SisyphusMD/whiskerless), the other SisyphusMD
project built for Home Assistant. No third-party code ships alongside it.

## Shared standard

Files listed in `STANDARD.lock` are vendored from
[project-standard](https://forgejo.bryantserver.com/SisyphusMD/project-standard) and must not be
edited here. Change them there and re-vendor; `packaging/check-standard-sync.py` fails on an edited
copy.
