---
name: add-issue-scan-project
description: Add a new GitHub repository to the Issue-Scan polling workflow. Use when a user asks to start scanning issues for an additional project/repository, wire its local path mapping, keep the raw-forwarding behavior, update reproducible docs, and ensure another agent can repeat the same setup safely.
---

# Add Issue-Scan Project

Use this skill when the task is to add a new repository into the Issue-Scan scanning workflow.

## Goal

Update Issue-Scan so a new repository is scanned the same way as existing repositories, without reintroducing keyword-based semantic classification.

## Preserve these invariants

Do not break these rules unless the user explicitly asks:

1. Ignore only lifecycle labels such as `completed`
2. Do not skip issues because of `Idea`, `Plan Mode`, or similar planning labels
3. Forward issue title/body/latest non-AI comment as raw context
4. Do not restore `plan-only` / `discussion-only` / `implementation-request` keyword classification
5. Let the agent infer whether an issue is planning or execution from the issue text itself

## Required inputs

Collect or confirm these values before editing:

- GitHub repo slug, for example `owner/repo`
- Local repository path on disk
- Whether the author filter should stay unchanged
- Whether wake target/channel should stay unchanged

Default assumption: keep author filter and wake target unchanged unless the user explicitly asks otherwise.

## Files to update

Usually update these files:

- `src/issue_scan/config.py`
- `README.md`
- `docs/GITHUB_ISSUE_POLLING.md` only if behavior rules changed

## Workflow

1. Open `src/issue_scan/config.py`
2. Add the new repo slug to `DEFAULT_CONFIG.repos`
3. Add the local path mapping to `DEFAULT_CONFIG.repo_paths`
4. Do not add new semantic label filters unless explicitly requested
5. Do not add new keyword-based classification logic
6. Update `README.md` so reproducible deployment docs include the new repo and path mapping
7. If the deployment is already live, run Issue-Scan manually once to sanity-check logs
8. If cron is not yet using Issue-Scan, switch cron only after validation
9. Commit and push changes when the user asked for execution, not just planning

## Validation

After editing, validate with:

```bash
python3 -m py_compile src/issue_scan/*.py
source .venv/bin/activate
issue-scan
```

Then inspect logs:

```bash
tail -n 100 /tmp/clawdbot_poll.log
tail -n 100 /tmp/issue-scan-cron.log
```

## Completion checklist

- Repo added to config
- Local path mapping added
- Raw-forwarding behavior preserved
- Docs updated
- Validation run
- Changes committed/pushed if requested
- If this work was driven by a GitHub issue, reply there with `[AI]`, summarize what changed, then add `completed` and close the issue when done
