from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class RepoIssue:
    repo: str
    number: int
    title: str
    body: str
    labels: list[str]
    url: str
    latest_user_comment: str
    marker: str
    local_path: str
    code_sync: str = ""

    @property
    def key_part(self) -> str:
        return f"{self.repo}#{self.number}@{self.marker}"

    @property
    def summary_part(self) -> str:
        return f"{self.repo}#{self.number}"


@dataclass
class PollState:
    issue_key: str = ""
    timestamp: str = "0"


@dataclass
class AppConfig:
    repos: list[str]
    repo_paths: dict[str, str]
    author: str
    ignored_labels: list[str]
    ai_prefixes: list[str]
    log_file: str
    state_file: str
    lock_file: str
    wake_session_id: str
    wake_channel: str
    wake_target: str
    polling_rules_path: str
    openclaw_bin: str
    gh_bin: str
    git_bin: str
