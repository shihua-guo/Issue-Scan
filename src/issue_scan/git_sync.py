from __future__ import annotations

import os
import subprocess


def sync_repo(repo_path: str, git_bin: str, log_file: str) -> str:
    if not repo_path:
        return "failed (local path not configured)"
    if not os.path.isdir(repo_path):
        return f"failed (path missing: {repo_path})"
    if not os.path.isdir(os.path.join(repo_path, ".git")):
        return f"failed (not a git repo: {repo_path})"

    status = subprocess.run(
        [git_bin, "-C", repo_path, "status", "--porcelain"],
        capture_output=True,
        text=True,
    )
    if status.stdout.strip():
        return "skipped (dirty working tree)"

    with open(log_file, "a", encoding="utf-8") as log:
        fetch = subprocess.run([git_bin, "-C", repo_path, "fetch", "origin"], stdout=log, stderr=log)
        if fetch.returncode != 0:
            return "failed (git fetch origin failed)"
        pull = subprocess.run([git_bin, "-C", repo_path, "pull", "--ff-only"], stdout=log, stderr=log)
        if pull.returncode != 0:
            return "failed (git pull --ff-only failed)"

    return "ok (already up to date or fast-forwarded)"
