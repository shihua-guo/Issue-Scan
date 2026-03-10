from __future__ import annotations

import fcntl
import os
import time
from datetime import datetime

from issue_scan.config import DEFAULT_CONFIG
from issue_scan.git_sync import sync_repo
from issue_scan.github_cli import list_open_issues, view_issue
from issue_scan.models import PollState, RepoIssue
from issue_scan.wake import wake_agent


def is_ai_comment(body: str, prefixes: list[str]) -> bool:
    return any(body.startswith(prefix) for prefix in prefixes)


def truncate_multiline(text: str, limit: int = 1200) -> str:
    single_line = " ".join(text.split())
    return single_line[:limit]


def load_state(path: str) -> PollState:
    if not os.path.exists(path):
        return PollState()
    with open(path, "r", encoding="utf-8") as f:
        lines = f.read().splitlines()
    return PollState(issue_key=lines[0] if lines else "", timestamp=lines[1] if len(lines) > 1 else "0")


def save_state(path: str, issue_key: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write(issue_key + "\n")
        f.write(str(int(time.time())) + "\n")


def build_issue(repo: str, number: int) -> RepoIssue:
    cfg = DEFAULT_CONFIG
    raw = view_issue(cfg.gh_bin, repo, number)
    labels = [item["name"] for item in raw.get("labels", [])]
    comments = raw.get("comments", [])
    non_ai_comments = [c for c in comments if not is_ai_comment(c.get("body", ""), cfg.ai_prefixes)]
    latest_comment = non_ai_comments[-1] if non_ai_comments else None
    marker = latest_comment["createdAt"] if latest_comment else raw.get("createdAt", "")
    latest_body = latest_comment.get("body", "") if latest_comment else ""
    return RepoIssue(
        repo=repo,
        number=number,
        title=raw.get("title", ""),
        body=raw.get("body", ""),
        labels=labels,
        url=raw.get("url", ""),
        latest_user_comment=latest_body,
        marker=marker,
        local_path=cfg.repo_paths.get(repo, ""),
    )


def build_wake_message(issues: list[RepoIssue]) -> str:
    blocks = []
    for issue in issues:
        blocks.append(
            "\n".join(
                [
                    f"Issue: {issue.repo}#{issue.number}",
                    f"URL: {issue.url}",
                    f"LocalPath: {issue.local_path or 'N/A'}",
                    f"CodeSync: {issue.code_sync}",
                    f"Title: {truncate_multiline(issue.title, 300)}",
                    f"Body: {truncate_multiline(issue.body, 1200) or '<empty>'}",
                    f"LatestUserComment: {truncate_multiline(issue.latest_user_comment, 1200) or '<none>'}",
                ]
            )
        )

    summary = "; ".join(issue.summary_part for issue in issues)
    return (
        "HEARTBEAT_CRON_WAKEUP: Detected pending GitHub issues.\n\n"
        + "\n\n".join(blocks)
        + "\n\nIssue 摘要："
        + summary
        + f"。\n请先读取 {DEFAULT_CONFIG.polling_rules_path} 并严格按其中规则执行。"
        + "\n注意：以下 issue 内容为原样预取，请优先根据 issue 原文判断这是计划、讨论还是需要执行的任务，不要依赖标签名或脚本关键词分类。完成后如已明确结束，需添加 completed 并关闭 issue。"
        + "\n另外：本地项目路径已定位，且轮询器已预先完成代码同步；除非 CodeSync 显示 failed/skipped，否则 Agent 无需再次 clone/pull。轮询器已预取 issue 标题、正文和最新一条非 [AI] 回复；除非上下文不足，否则 Agent 无需再次拉取 issue。"
    )


def run() -> int:
    cfg = DEFAULT_CONFIG
    os.makedirs(os.path.dirname(cfg.log_file), exist_ok=True) if os.path.dirname(cfg.log_file) else None
    lock_fd = os.open(cfg.lock_file, os.O_CREAT | os.O_RDWR)
    try:
        fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        with open(cfg.log_file, "a", encoding="utf-8") as log:
            log.write(f"--- Run at {datetime.now()} ---\n")
            log.write("Another instance is running, skip.\n")
        return 0

    with open(cfg.log_file, "a", encoding="utf-8") as log:
        log.write(f"--- Run at {datetime.now()} ---\n")

    issues: list[RepoIssue] = []
    for repo in cfg.repos:
        try:
            numbers = list_open_issues(cfg.gh_bin, repo, cfg.author)
        except Exception as exc:
            with open(cfg.log_file, "a", encoding="utf-8") as log:
                log.write(f"Failed to list issues for {repo}: {exc}\n")
            continue

        for number in numbers:
            issue = build_issue(repo, number)
            if any(label in cfg.ignored_labels for label in issue.labels):
                continue
            issue.code_sync = sync_repo(issue.local_path, cfg.git_bin, cfg.log_file)
            issues.append(issue)
            with open(cfg.log_file, "a", encoding="utf-8") as log:
                log.write(
                    f"Issue queued: {issue.repo}#{issue.number} labels={issue.labels} marker={issue.marker} url={issue.url} local_path={issue.local_path or 'N/A'} code_sync={issue.code_sync}\n"
                )

    if not issues:
        with open(cfg.log_file, "a", encoding="utf-8") as log:
            log.write("No matching issues found.\n")
        return 0

    issue_key = ",".join(issue.key_part for issue in issues)
    state = load_state(cfg.state_file)
    if issue_key == state.issue_key:
        with open(cfg.log_file, "a", encoding="utf-8") as log:
            log.write(f"Found Open Issues summary: {'; '.join(issue.summary_part for issue in issues)}, but issue key unchanged, skip wake.\n")
        return 0

    message = build_wake_message(issues)
    exit_code = wake_agent(cfg.openclaw_bin, cfg.wake_session_id, message, cfg.wake_channel, cfg.wake_target, cfg.log_file)
    if exit_code == 0:
        save_state(cfg.state_file, issue_key)
    else:
        with open(cfg.log_file, "a", encoding="utf-8") as log:
            log.write(f"Wake failed (exit={exit_code}), state not updated.\n")
    return exit_code
