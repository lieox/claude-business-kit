"""PostToolUse hook (Bash / PowerShell): after an install command, reminds Claude to log it in INSTALLS.md.

Months later nobody remembers why a tool is on the machine, which project needed it, or how it
was installed. One row per install in ~/.claude/INSTALLS.md answers all three.
"""
import json
import re
import sys

INSTALL = re.compile(
    r"\b(npm\s+(install|i)\s+(-g|--global)|pnpm\s+add\s+-g|pip3?\s+install|uv\s+(pip\s+install|tool\s+install)|"
    r"pipx\s+install|winget\s+install|choco\s+install|scoop\s+install|brew\s+install|"
    r"npx\s+skills\s+add|claude\s+mcp\s+add|claude\s+plugin\s+install)\b",
    re.I,
)

REMINDER = (
    "רצה עכשיו פקודת התקנה. לפני שמסיימים, הוסף שורה ל-~/.claude/INSTALLS.md בטבלה המתאימה: "
    "מה הותקן, הפקודה המדויקת, בשביל מה, לאיזה פרויקט או סוכן זה שייך, והתאריך. "
    "אם הקובץ לא קיים, צור אותו לפי INSTALLS.template.md."
)


def main():
    try:
        data = json.load(sys.stdin)
        command = data.get("tool_input", {}).get("command", "")
    except Exception:
        sys.exit(0)
    if INSTALL.search(command):
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": REMINDER}}, ensure_ascii=False))
    sys.exit(0)


if __name__ == "__main__":
    main()
