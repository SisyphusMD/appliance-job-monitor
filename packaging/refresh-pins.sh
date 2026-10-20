#!/usr/bin/env bash
# Run by Renovate as a postUpgradeTask on the update branch. The Renovate runner allows only this
# command, under this name, in every repository, so it is the entry point even though re-vendoring
# the standard is all it has to do here.
set -euo pipefail
bash "$(cd "$(dirname "$0")" && pwd)/revendor-standard.sh"
