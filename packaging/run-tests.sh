#!/usr/bin/env bash
# Install the test harness for one Home Assistant target into its own virtualenv and run the suite.
#
#   packaging/run-tests.sh latest|floor [pytest arguments...]
#
# The one place both CI workflows and a local run install from, so the floor's resolve date and the
# Python each target needs cannot differ between them. Needs uv on PATH.
set -euo pipefail
cd "$(dirname "$0")/.."

target="${1:?usage: packaging/run-tests.sh latest|floor [pytest arguments...]}"
shift
case "$target" in
  latest)
    requirements="requirements-test.txt"
    python=3.14
    venv=.venv
    resolve=()
    ;;
  floor)
    requirements="requirements-test-floor.txt"
    python=3.12
    venv=.venv-floor
    # Later releases of the floor's unpinned dependencies break Home Assistant 2024.10 (josepy 2 no
    # longer provides what its cloud client imports), so resolve as of the day it shipped.
    resolve=(--exclude-newer 2024-10-03)
    ;;
  *)
    echo "unknown target: $target (expected latest or floor)" >&2
    exit 2
    ;;
esac

uv venv --quiet --allow-existing --python "$python" "$venv"
uv pip install --quiet --python "$venv/bin/python" "${resolve[@]}" -r "$requirements"
APPLIANCE_TEST_TARGET="$target" "$venv/bin/python" -m pytest -q -p no:cacheprovider "$@"
