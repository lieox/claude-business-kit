"""PreToolUse hook (Read/Edit/Write): keeps Claude away from files that hold passwords and keys."""
import json
import re
import sys

SECRET_FILES = re.compile(
    r"(^|[\\/])(\.env(\..*)?|.*\.pem|.*\.key|id_rsa.*|credentials.*\.json|secrets?\..*|bots\.json|mcp\.json)$",
    re.IGNORECASE,
)


def main():
    data = json.load(sys.stdin)
    path = data.get("tool_input", {}).get("file_path", "")
    if path and SECRET_FILES.search(path) and not path.lower().endswith(".example.json"):
        print(f"נחסם: {path} מכיל סודות (מפתחות, סיסמאות, טוקנים). עורכים אותו ידנית.", file=sys.stderr)
        sys.exit(2)
    sys.exit(0)


if __name__ == "__main__":
    main()
