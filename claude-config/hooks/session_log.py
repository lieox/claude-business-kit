"""Stop hook: appends one line per finished turn to ~/.claude/activity-log.md, so there is a trail of what ran and where."""
import json
import sys
import time
from pathlib import Path

LOG = Path.home() / ".claude" / "activity-log.md"


def main():
    data = json.load(sys.stdin)
    cwd = data.get("cwd", "")
    session = data.get("session_id", "")[:8]
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(f"- {time.strftime('%Y-%m-%d %H:%M')} | {session} | {cwd}\n")
    sys.exit(0)


if __name__ == "__main__":
    main()
