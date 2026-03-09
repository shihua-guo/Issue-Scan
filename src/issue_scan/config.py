from __future__ import annotations

from issue_scan.models import AppConfig


DEFAULT_CONFIG = AppConfig(
    repos=[
        "shihua-guo/clawdbot",
        "shihua-guo/callchain-analysis",
        "shihua-guo/llm-free",
    ],
    repo_paths={
        "shihua-guo/clawdbot": "/root/clawd",
        "shihua-guo/callchain-analysis": "/root/clawd/tmp/callchain-analysis",
        "shihua-guo/llm-free": "/root/clawd/tmp/llm-free",
    },
    author="shihua-guo",
    ignored_labels=["Idea", "Plan Mode", "plan mode", "completed"],
    ai_prefixes=["[AI]", "$[AI]"],
    log_file="/tmp/clawdbot_poll.log",
    state_file="/tmp/clawdbot_poll.state",
    lock_file="/tmp/clawdbot_poll.lock",
    wake_session_id="agent:main:main",
    wake_channel="telegram",
    wake_target="telegram:5454111304",
    polling_rules_path="/root/clawd/GITHUB_ISSUE_POLLING.md",
    openclaw_bin="/usr/local/lib/nodejs/node-v24/bin/openclaw",
    gh_bin="/usr/local/bin/gh",
    git_bin="git",
)
