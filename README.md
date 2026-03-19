# Issue-Scan

Issue-Scan is a Python-based GitHub issue polling tool for OpenClaw workflows.

It replaces the older shell-based polling script with a more maintainable and reproducible Python implementation.

## What it does

- Polls multiple GitHub repositories for open issues
- Filters issues by author
- Ignores lifecycle labels such as `completed`
- Distinguishes user updates from AI replies using reply prefixes such as `[AI]`
- Builds a deduplication marker from the latest non-AI comment timestamp
- Resolves repository-to-local-path mappings
- Syncs local repositories before wakeup when safe
- Preloads minimal issue context:
  - title
  - body
  - latest non-AI comment
- Sends a compact but context-rich wakeup message to OpenClaw
- Passes issue content through to the agent without keyword-based semantic classification

## Current behavior contract

The current deployment follows these rules:

- Scan only open issues authored by the configured GitHub user
- Do **not** skip issues because they have labels like `Idea` or `Plan Mode`
- Skip issues labeled `completed`
- Do **not** classify issues into `plan-only`, `discussion-only`, or `implementation-request`
- Forward the issue title/body/latest user comment as raw context
- Let the agent decide whether the issue is a discussion, a plan, or an execution request based on the issue text itself

This is intentional. The user writes the intent directly in the issue body, so the scanner should avoid brittle keyword heuristics.

## Project structure

```text
src/issue_scan/
  cli.py          # entry point
  config.py       # configuration structures
  github_cli.py   # wrappers around gh commands
  git_sync.py     # safe local repository sync
  models.py       # dataclasses
  poller.py       # polling workflow
  wake.py         # OpenClaw wake integration
skills/
  add-issue-scan-project/
    SKILL.md      # reusable procedure for adding a new scanned repository
```

## Requirements

- Python 3.10+
- `gh` installed and authenticated
- OpenClaw CLI available
- Local repository paths available on disk
- Access to the target OpenClaw session/channel for wake delivery

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Example usage

```bash
issue-scan
```

## Reproducible deployment guide

This section is written so another agent can fully reproduce the same setup on another machine.

### 1. Clone the repository

```bash
git clone https://github.com/shihua-guo/Issue-Scan.git
cd Issue-Scan
```

### 2. Create a virtual environment and install

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

### 3. Ensure system dependencies exist

The machine must have:

- `gh` installed and already authenticated
- `git`
- `python3`
- `openclaw` CLI available at the configured path

Recommended checks:

```bash
gh auth status
git --version
python3 --version
openclaw --help
```

### 4. Configure scan targets in `src/issue_scan/config.py`

The current production setup scans:

- `shihua-guo/clawdbot` → `/root/clawd`
- `shihua-guo/callchain-analysis` → `/root/clawd/tmp/callchain-analysis`
- `shihua-guo/llm-free` → `/root/clawd/tmp/llm-free`
- `shihua-guo/Issue-Scan` → `/root/clawd/tmp/Issue-Scan`
- `shihua-guo/opengauss-tool` → `/root/clawd/tmp/opengauss-tool`
- `shihua-guo/browser-llm-bridge` → `/root/projects/apps/browser-llm-bridge`
- `shihua-guo/Healthy` → `/root/projects/apps/Healthy`

It also uses:

- `author="shihua-guo"`
- `ignored_labels=["completed"]`
- AI reply prefixes including `[AI]`
- wake target `telegram:5454111304`
- polling rules file `/root/clawd/GITHUB_ISSUE_POLLING.md`

When reproducing on another machine, update the following if needed:

- repo list
- local repo paths
- author
- wake target / channel
- `openclaw` binary path
- `gh` binary path
- polling rules file path

### 5. Install the polling rules file

Issue-Scan depends on a companion rules document named `GITHUB_ISSUE_POLLING.md`.

Copy the repository version of that file to the OpenClaw workspace path expected by config, for example:

```bash
cp docs/GITHUB_ISSUE_POLLING.md /root/clawd/GITHUB_ISSUE_POLLING.md
```

If the target workspace differs, adjust the config accordingly.

### 6. Test a manual run

Before enabling cron, run:

```bash
source .venv/bin/activate
issue-scan
```

Then inspect logs:

```bash
tail -n 100 /tmp/clawdbot_poll.log
```

Expected behavior:

- no syntax/runtime errors
- matching issues are queued
- unchanged issue keys do not wake repeatedly
- if there are no matching issues, the log says `No matching issues found.`

### 7. Disable the old shell cron job

If the older shell script is still active, disable it before enabling Issue-Scan.

Example old job:

```cron
* * * * * /root/clawd/scripts/check_issues.sh
```

Do not let both run at the same time.

### 8. Enable the new cron job

Example production cron:

```cron
* * * * * cd /root/clawd/tmp/Issue-Scan && . /root/clawd/tmp/Issue-Scan/.venv/bin/activate && issue-scan >> /tmp/issue-scan-cron.log 2>&1
```

This keeps the runtime simple and reproducible.

### 9. Validate after cron switch

Check:

```bash
crontab -l
tail -n 100 /tmp/issue-scan-cron.log
tail -n 100 /tmp/clawdbot_poll.log
```

Confirm:

- old cron is disabled
- new cron is present
- Issue-Scan runs every minute
- issues are deduplicated correctly
- wake delivery succeeds when matching issues exist

## Included skill

This repository now includes a reusable skill:

- `skills/add-issue-scan-project/SKILL.md`

Use it when a user asks to add another repository into the Issue-Scan workflow. It captures the expected edit targets, invariants, validation steps, and completion checklist so another agent can repeat the same process with lower token cost.

## Notes for future agents

If you are another agent reproducing this setup, preserve these invariants unless the user explicitly changes them:

1. `completed` remains the only ignored label
2. `Idea` / `Plan Mode` must not block scanning
3. issue content must be forwarded raw
4. the scanner must not hardcode semantic classification rules for “plan vs execute”
5. the agent decides behavior from the issue text itself
6. the old shell polling cron should stay disabled once migration is complete

## License

MIT
