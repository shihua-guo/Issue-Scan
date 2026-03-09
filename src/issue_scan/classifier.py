from __future__ import annotations

import re


DISCUSSION_PATTERNS = [
    r"不要修改代码", r"不要改代码", r"不要修改任何代码", r"不要有任何修改动作",
    r"不要改仓库", r"不要提交pr", r"不要提pr", r"只回答问题", r"只分析",
    r"do not modify", r"no code changes", r"answer only", r"analysis only",
    r"do not submit pr", r"do not create pr",
]

IMPLEMENTATION_PATTERNS = [
    r"修复", r"修一下", r"fix", r"bugfix", r"implement", r"实现",
    r"增加支持", r"支持一下", r"提交pr", r"提pr", r"pull request",
    r"修改代码", r"改代码", r"更新文档", r"修改文档", r"update docs",
    r"update documentation", r"修改配置", r"改配置", r"patch", r"落地实现",
    r"请直接处理", r"按这个方案改", r"按照这个方案修改", r"直接修改",
    r"直接执行", r"开始修改", r"开始执行", r"同步到文档", r"同步更新文档",
]

PLAN_PATTERNS = [
    r"方案", r"计划", r"思路", r"设计建议", r"proposal", r"design",
    r"plan", r"architecture", r"先分析再说", r"先给方案",
]


def classify_issue(labels: list[str], text: str) -> tuple[str, str]:
    label_text = ", ".join(labels)
    lowered = text.lower()

    if re.search(r"(^|[ ,|])idea([ ,|]|$)|(^|[ ,|])plan mode([ ,|]|$)", label_text, re.I):
        return "plan-only", "label:idea-or-plan-mode"

    if any(re.search(pattern, lowered, re.I) for pattern in DISCUSSION_PATTERNS):
        return "discussion-only", "explicit-no-change-request"

    if any(re.search(pattern, lowered, re.I) for pattern in IMPLEMENTATION_PATTERNS):
        return "implementation-request", "explicit-implementation-request"

    if any(re.search(pattern, lowered, re.I) for pattern in PLAN_PATTERNS):
        return "plan-only", "plan-oriented-request"

    return "mixed-or-unclear", "needs-agent-judgement"
