"""The blueprint's supported Home Assistant versions and published import links."""

from __future__ import annotations

import os
from urllib.parse import quote

from awesomeversion import AwesomeVersion
from homeassistant.const import __version__ as HA_VERSION
from homeassistant.util.yaml.loader import parse_yaml

from .conftest import BLUEPRINT, ROOT


def min_version() -> AwesomeVersion:
    blueprint = parse_yaml(BLUEPRINT.read_text())
    return AwesomeVersion(blueprint["blueprint"]["homeassistant"]["min_version"])


def test_the_suite_runs_on_a_supported_release() -> None:
    assert AwesomeVersion(HA_VERSION) >= min_version()


def test_the_floor_suite_runs_on_exactly_the_declared_floor() -> None:
    """Raising min_version without the floor pin, or the reverse, would test the wrong release."""
    if os.environ.get("APPLIANCE_TEST_TARGET") != "floor":
        return
    assert AwesomeVersion(HA_VERSION) == min_version()


def test_reimport_uses_latest_published_blueprint() -> None:
    blueprint = parse_yaml(BLUEPRINT.read_text())
    url = blueprint["blueprint"]["source_url"]
    assert url == (
        "https://forgejo.bryantserver.com/SisyphusMD/appliance-job-monitor/"
        "releases/download/latest/appliance-job-monitor.yaml"
    )
    readme = (ROOT / "README.md").read_text()
    assert f"```text\n{url}\n```" in readme
    assert f"?blueprint_url={quote(url, safe='')})" in readme
