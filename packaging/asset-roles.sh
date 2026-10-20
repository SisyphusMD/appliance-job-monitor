#!/usr/bin/env bash
# The release matrix reconcile-releases.sh replicates. Sourced, never executed.
#
# Two names for the same bytes. The versioned file is the record of one release. The unversioned
# one exists because both forges resolve a "latest release" download only by exact asset name, and
# the blueprint's source_url and the import link in the README point at that route.

_ASSET_ROLES=(
  # Matches only the versioned name: the stable one has no hyphen after "monitor".
  'appliance-job-monitor-*.yaml'
  'appliance-job-monitor.yaml'
)

# Every asset a release carries is reconciled.
# shellcheck disable=SC2034 # read by reconcile-releases.sh
_IGNORED_ASSETS=()
