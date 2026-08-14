#!/usr/bin/env python3
"""Merge projects.json with live GitHub repository data.

User controls: name, repo, logo, description, tags, order.
Auto-fetched: stars, languages, pushed_at.
If GitHub is unavailable, config data is preserved so the project card still renders.
"""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "projects.json"
OUTPUT = ROOT / "projects" / "merged.json"
TOKEN = os.environ.get("GITHUB_TOKEN", "")


def github_json(url: str):
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "ashishraj140744-profile-projects",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=20) as response:
        return json.load(response)


def normalize_repo(repo: str) -> str:
    repo = repo.strip().replace("https://github.com/", "").replace("http://github.com/", "")
    return repo.rstrip("/")


def main() -> None:
    if not SOURCE.exists():
        raise SystemExit(f"Missing {SOURCE}")

    projects = json.loads(SOURCE.read_text(encoding="utf-8"))
    for project in projects:
        repo = normalize_repo(project.get("repo", ""))
        project["repo"] = repo
        project.setdefault("stars", 0)
        project.setdefault("languages", {})
        project.setdefault("pushed_at", None)

        if not repo or "/" not in repo:
            print(f"warn: invalid repo '{repo}'", file=sys.stderr)
            continue

        try:
            info = github_json(f"https://api.github.com/repos/{repo}")
            project["stars"] = info.get("stargazers_count", 0)
            project["pushed_at"] = info.get("pushed_at")
            if not project.get("description"):
                project["description"] = info.get("description") or ""
            project["languages"] = github_json(f"https://api.github.com/repos/{repo}/languages")
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, ValueError) as exc:
            print(f"warn: could not fetch {repo}: {exc}", file=sys.stderr)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(projects, indent=2), encoding="utf-8")
    print(f"merged {len(projects)} projects -> {OUTPUT}")


if __name__ == "__main__":
    main()
