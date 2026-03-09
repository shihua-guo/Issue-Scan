from __future__ import annotations

from issue_scan.poller import run


def main() -> int:
    return run()


if __name__ == "__main__":
    raise SystemExit(main())
