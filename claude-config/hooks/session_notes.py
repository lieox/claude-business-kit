"""SessionStart hook: carries the working notes from the last session into the new one.

During a long session Claude keeps ~/.claude/working.md: the task, decisions, current state and
what is left. When a new session starts, this hook shows those notes to Claude, then moves them
to ~/.claude/working-history/ and leaves an empty working.md, so the next session starts clean
but nothing is lost. On resume or after compaction the notes are shown and left in place.
"""
import json
import sys
import time
from pathlib import Path

CLAUDE_DIR = Path.home() / ".claude"
WORKING = CLAUDE_DIR / "working.md"
HISTORY = CLAUDE_DIR / "working-history"
HEADER = "# working.md\n\nהערות עבודה לסשן הזה: המשימה, החלטות, מצב נוכחי, מה נשאר.\n\n"


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        data = {}
    source = data.get("source", "startup")
    try:
        text = WORKING.read_text(encoding="utf-8") if WORKING.exists() else ""
    except Exception:
        sys.exit(0)
    body = text.replace(HEADER, "").strip()
    if body:
        print("## הערות העבודה מהסשן הקודם (working.md)\n")
        print(body)
    if source == "startup":
        try:
            if body:
                HISTORY.mkdir(parents=True, exist_ok=True)
                (HISTORY / f"{time.strftime('%Y-%m-%d_%H%M')}.md").write_text(text, encoding="utf-8")
            WORKING.write_text(HEADER, encoding="utf-8")
        except Exception:
            pass
    sys.exit(0)


if __name__ == "__main__":
    main()
