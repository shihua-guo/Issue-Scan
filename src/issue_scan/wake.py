from __future__ import annotations

import subprocess


def wake_agent(openclaw_bin: str, session_id: str, message: str, channel: str, target: str, log_file: str) -> int:
    with open(log_file, "a", encoding="utf-8") as log:
        proc = subprocess.run(
            [
                openclaw_bin,
                "agent",
                "--session-id", session_id,
                "--message", message,
                "--deliver",
                "--channel", channel,
                "--to", target,
            ],
            stdout=log,
            stderr=log,
        )
    return proc.returncode
