"""PreToolUse hook (Bash/PowerShell): blocks commands that destroy data or rewrite history.
Exit code 2 blocks the call and shows the reason to Claude."""
import json
import re
import sys

BLOCKED = [
    (r"\brm\s+-[a-z]*r[a-z]*f|\brm\s+-[a-z]*f[a-z]*r", "מחיקה רקורסיבית בכוח (rm -rf)"),
    (r"\bgit\s+push\b.*(--force|-f\b)", "דחיפה בכוח ל-git"),
    (r"\bgit\s+reset\s+--hard", "git reset --hard מוחק עבודה שלא נשמרה"),
    (r"\bgit\s+clean\s+-[a-z]*f", "git clean מוחק קבצים"),
    (r"\bRemove-Item\b.*-Recurse", "מחיקה רקורסיבית ב-PowerShell"),
    (r"\b(rd|rmdir)\s+/s", "מחיקת תיקייה עם כל התוכן"),
    (r"\bdel\s+/[sq]", "מחיקה המונית ב-cmd"),
    (r"\bformat\s+[a-z]:", "פירמוט כונן"),
]


def main():
    data = json.load(sys.stdin)
    command = data.get("tool_input", {}).get("command", "")
    for pattern, reason in BLOCKED:
        if re.search(pattern, command, re.IGNORECASE):
            print(f"נחסם: {reason}. אם זה באמת נחוץ, בקש מהמשתמש להריץ את זה בעצמו.", file=sys.stderr)
            sys.exit(2)
    sys.exit(0)


if __name__ == "__main__":
    main()
