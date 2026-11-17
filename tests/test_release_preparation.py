"""Run the release PR creation step against local Git and a stub Forgejo API."""

import json
import os
import subprocess
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def test_release_preparation_pushes_only_the_candidate_and_reuses_the_pr(tmp_path):
    repo = tmp_path / "checkout"
    primary = tmp_path / "primary.git"
    repo.mkdir()

    def git(*args):
        return subprocess.check_output(["git", *args], cwd=repo, text=True).strip()

    git("init", "--bare", str(primary))
    git("init", "-b", "main")
    git("config", "user.name", "Release test")
    git("config", "user.email", "release@example.test")
    git("config", "commit.gpgsign", "false")
    git("remote", "add", "origin", str(primary))
    git("commit", "--allow-empty", "-m", "base")
    git("push", "origin", "main")
    original = git("rev-parse", "HEAD")
    git("commit", "--allow-empty", "-m", "prepare 1.2.3")
    candidate = git("rev-parse", "HEAD")

    log = tmp_path / "created.json"
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    curl = fake_bin / "curl"
    curl.write_text(
        """#!/usr/bin/env python3
import json, os, pathlib, sys
args = sys.argv[1:]
log = pathlib.Path(os.environ["CREATED"])
if args[-1].endswith("/issues/7"):
    assert "Authorization: token issue-reader" in args
    print('{"state":"open","pull_request":null}')
elif "--get" in args:
    assert "state=open" in args and "head=release/v1.2.3" in args
    if log.exists():
        payload = json.loads(log.read_text())
        print(json.dumps([{
            "flow": 0,
            "head": {
                "label": payload["head"], "ref": payload["head"],
                "sha": os.environ["CANDIDATE"], "repo": {"full_name": "Owner/Project"},
            },
            "base": {"ref": payload["base"]},
            "body": payload["body"],
            "html_url": "https://forge.example.test/Owner/Project/pulls/8",
        }]))
    else:
        print("[]")
elif "--data" in args:
    assert not log.exists(), "duplicate PR create"
    log.write_text(args[args.index("--data") + 1])
    print('{"html_url":"https://forge.example.test/Owner/Project/pulls/8"}')
else:
    sys.exit("unexpected request")
"""
    )
    curl.chmod(0o700)
    workflow = yaml.safe_load((ROOT / ".forgejo/workflows/release.yml").read_text())
    script = next(
        step["run"] for step in workflow["jobs"]["prepare"]["steps"]
        if step.get("name") == "Open the release pull request"
    )
    env = dict(
        os.environ, PATH=f"{fake_bin}:{os.environ['PATH']}", CREATED=str(log), TAG="v1.2.3",
        CANDIDATE=candidate,
        ISSUE="7", ISSUE_TOKEN="issue-reader", TOKEN="stub", GITHUB_SERVER_URL="https://forge.example.test",
        GITHUB_REPOSITORY="Owner/Project",
    )
    for _ in range(2):
        result = subprocess.run(
            ["bash", "-c", script], cwd=repo, env=env, capture_output=True, text=True, check=False,
        )
        assert result.returncode == 0, result.stderr
        assert result.stdout.strip() == "https://forge.example.test/Owner/Project/pulls/8"

    assert git("ls-remote", "origin", "refs/heads/main") == f"{original}\trefs/heads/main"
    assert git("ls-remote", "origin", "refs/heads/release/v1.2.3") == (
        f"{candidate}\trefs/heads/release/v1.2.3"
    )
    assert not git("ls-remote", "--tags", "origin")
    body = json.loads(log.read_text())
    assert body["head"] == "release/v1.2.3"
    assert body["base"] == "main"
    assert body["body"].startswith("Closes #7.")

    advanced = git("commit-tree", "HEAD^{tree}", "-p", original, "-m", "Advance main during qualification")
    git("push", "origin", f"{advanced}:refs/heads/main")
    result = subprocess.run(
        ["bash", "-c", script], cwd=repo, env=env, capture_output=True, text=True, check=False,
    )
    assert result.returncode != 0
    assert "main moved during qualification" in result.stdout
    assert git("ls-remote", "origin", "refs/heads/release/v1.2.3").split()[0] == candidate


def test_publish_workflow_tags_the_verified_merge_when_main_has_advanced(tmp_path):
    repo = tmp_path / "checkout"
    primary = tmp_path / "primary.git"
    repo.mkdir()

    def git(*args):
        return subprocess.check_output(["git", *args], cwd=repo, text=True).strip()

    git("init", "--bare", str(primary))
    git("init", "-b", "main")
    git("config", "user.name", "Release test")
    git("config", "user.email", "release@example.test")
    git("config", "commit.gpgsign", "false")
    git("config", "tag.gpgsign", "false")
    git("remote", "add", "origin", str(primary))
    packaging = repo / "packaging"
    packaging.mkdir()
    for name in ("verify-release-pr.py", "push-tag.sh"):
        (packaging / name).write_bytes((ROOT / "packaging" / name).read_bytes())
    git("add", "packaging")
    git("commit", "-m", "Base")
    branch = "release/v1.2.3"
    git("checkout", "-b", branch)
    (repo / "CHANGELOG.md").write_text("## [Unreleased]\n\n## [1.2.3] - 2026-11-17\n")
    git("add", "CHANGELOG.md")
    git("commit", "-m", "Prepare release")
    candidate = git("rev-parse", "HEAD")
    git("checkout", "main")
    git("merge", "--no-ff", branch)
    merge = git("rev-parse", "HEAD")
    git("commit", "--allow-empty", "-m", "Advance main after merging the release")
    main = git("rev-parse", "HEAD")
    git("push", "origin", "main")

    slug = "Owner/Project"
    identity = {"full_name": slug}
    payload = tmp_path / "pull.json"
    payload.write_text(json.dumps({
        "number": 8, "flow": 0, "state": "closed", "merged": True,
        "base": {"ref": "main", "repo": identity},
        "head": {"ref": "refs/pull/8/head", "label": branch, "sha": candidate, "repo": identity},
        "merge_commit_sha": merge,
    }))
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    curl = fake_bin / "curl"
    curl.write_text(
        '#!/bin/sh\nfor arg do last=$arg; done\n'
        'case "$last" in */pulls/8) cat "$PAYLOAD";; */push_mirrors-sync) exit 0;; *) exit 1;; esac\n'
    )
    sleep = fake_bin / "sleep"
    sleep.write_text("#!/bin/sh\nexit 0\n")
    for executable in (curl, sleep):
        executable.chmod(0o700)
    output = tmp_path / "output"
    env = dict(
        os.environ, PATH=f"{fake_bin}:{os.environ['PATH']}", PAYLOAD=str(payload),
        PR="8", TOKEN="stub", GITHUB_SERVER_URL="https://forge.example.test",
        GITHUB_REPOSITORY=slug, GITHUB_OUTPUT=str(output),
    )
    workflow = yaml.safe_load((ROOT / ".forgejo/workflows/publish-release.yml").read_text())
    verify, publish = [step["run"] for step in workflow["jobs"]["publish"]["steps"] if "run" in step]
    subprocess.run(["bash", "-c", verify], cwd=repo, env=env, check=True, capture_output=True)
    published = dict(line.split("=", 1) for line in output.read_text().splitlines())
    assert published == {"tag": "v1.2.3", "commit": merge}
    for _ in range(2):
        subprocess.run(
            ["bash", "-c", publish], cwd=repo,
            env=dict(env, TAG=published["tag"], MERGE_COMMIT=published["commit"]),
            check=True, capture_output=True,
        )
    assert git("ls-remote", "origin", "refs/heads/main") == f"{main}\trefs/heads/main"
    assert git("ls-remote", "origin", "refs/tags/v1.2.3^{}") == f"{merge}\trefs/tags/v1.2.3^{{}}"
