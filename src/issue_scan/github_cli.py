from __future__ import annotations

import json
import subprocess
from typing import Any


def gh_json(gh_bin: str, args: list[str]) -> Any:
    result = subprocess.run([gh_bin, *args], capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip())
    return json.loads(result.stdout)


def list_open_issues(gh_bin: str, repo: str, author: str) -> list[int]:
    data = gh_json(
        gh_bin,
        [
            "issue", "list",
            "--repo", repo,
            "--state", "open",
            "--author", author,
            "--json", "number,labels",
        ],
    )
    return [int(item["number"]) for item in data]


def view_issue(gh_bin: str, repo: str, number: int) -> dict:
    return gh_json(
        gh_bin,
        [
            "issue", "view", str(number),
            "--repo", repo,
            "--json", "title,body,labels,url,createdAt,comments",
        ],
    )
