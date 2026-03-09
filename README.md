# Issue-Scan

Issue-Scan is a Python-based GitHub issue polling tool designed for OpenClaw workflows.

It replaces a shell-based polling script with a more maintainable and extensible Python implementation.

## What it does

- Polls multiple GitHub repositories for open issues
- Filters issues by author
- Ignores issues with configured labels such as `Idea`, `Plan Mode`, and `completed`
- Distinguishes user updates from AI replies using a reply prefix like `[AI]`
- Builds a deduplication marker from the latest non-AI comment timestamp
- Classifies issues into lightweight categories before waking the agent
- Resolves repository-to-local-path mappings
- Syncs local repositories before wakeup when safe
- Preloads minimal issue context:
  - title
  - body
  - latest non-AI comment
- Sends a compact but context-rich wakeup message to OpenClaw

## Why Python instead of shell

Using Python for issue polling is generally a better long-term choice than shell for this use case.

### Benefits

- Easier to maintain as logic grows
- Easier to test and refactor
- Cleaner data structures for issue metadata and config
- Better support for future features:
  - YAML / JSON config
  - per-repo rules
  - structured logging
  - retries / backoff
  - notifications
  - unit tests
  - GitHub API integration without heavy shell parsing

### Tradeoff

- Slightly more setup than a single shell script
- But much better extensibility once the polling logic becomes non-trivial

## Project structure

```text
src/issue_scan/
  cli.py          # entry point
  config.py       # configuration structures
  github_cli.py   # wrappers around gh commands
  classifier.py   # issue classification rules
  git_sync.py     # safe local repository sync
  models.py       # dataclasses
  poller.py       # polling workflow
  wake.py         # OpenClaw wake integration
```

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Requirements

- Python 3.10+
- `gh` installed and authenticated
- OpenClaw CLI available
- Local repository paths available on disk

## Example usage

```bash
issue-scan
```

The current implementation is designed to preserve the behavior of the existing shell workflow while making future extensions easier.

## Intended migration path

1. Keep the shell version running as the current production path
2. Build parity in Python
3. Validate wakeup content and dedup behavior
4. Replace the shell script with the Python project when stable

## License

MIT
