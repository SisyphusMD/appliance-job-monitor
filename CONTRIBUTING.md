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
