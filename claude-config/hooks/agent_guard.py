"""PreToolUse hook (Agent / Task / Workflow): keeps sub-agents from eating the subscription quota.

Every sub-agent runs on the same subscription as everything else, including the Telegram bots.
A reflexive fan-out of agents for a question that could be answered directly burns the quota
for the whole team.

Rules:
- Agent / Task: allowed by default. Blocked when the user's last message refused agents
  ("בלי סוכנים"), or when the session passes a cap. The cap is low when the user did not ask
  for agents, and higher when they did.
- Workflow: one call can start many agents, so it needs the word "workflow" in the user's
  last message.

Exit code 2 blocks the call and shows the reason to Claude. Any error lets the call through.
"""
import json
import re
import sys
from pathlib import Path

CAP_UNASKED = 3
CAP_ASKED = 10
STATE = Path.home() / ".claude" / "state" / "agent_guard.json"

REFUSE = re.compile(r"בלי סוכנ|לא סוכנ|בלי צי|עצור את הסוכנ|תעצור את הסוכנ|no agents|without agents|stop the agents", re.I)
ASK = re.compile(r"סוכן|סוכנים|סוכנת|במקביל|agent|parallel|workflow|צי סוכנים", re.I)
WORKFLOW_ASK = re.compile(r"workflow|וורקפלו|צי סוכנים", re.I)


def last_user_text(transcript_path):
    last = ""
    with open(transcript_path, encoding="utf-8") as f:
        for line in f:
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            if entry.get("type") != "user" or entry.get("isMeta") or entry.get("isCompactSummary"):
                continue
            content = entry.get("message", {}).get("content")
            if isinstance(content, list):
                if any(isinstance(b, dict) and b.get("type") == "tool_result" for b in content):
                    continue
                content = "\n".join(b.get("text", "") for b in content if isinstance(b, dict) and b.get("type") == "text")
            if not isinstance(content, str) or "<task-notification>" in content:
                continue
            text = re.sub(r"<system-reminder>.*?</system-reminder>", " ", content, flags=re.S).strip()
            if text:
                last = text
    return last


def block(reason):
    print(f"נחסם: {reason}", file=sys.stderr)
    sys.exit(2)


def main():
    try:
        data = json.load(sys.stdin)
        tool = data.get("tool_name", "")
        session = data.get("session_id", "unknown")
        user = last_user_text(data["transcript_path"]) if data.get("transcript_path") else ""
    except Exception:
        sys.exit(0)

    if REFUSE.search(user):
        block("המשתמש ביקש בלי סוכנים. עשה את העבודה בעצמך, בשיחה הזו.")

    if tool == "Workflow":
        if not WORKFLOW_ASK.search(user):
            block("Workflow מפעיל הרבה סוכנים על המכסה המשותפת. מותר רק כשהמשתמש ביקש workflow במפורש. "
                  "הצע לו כמה סוכנים ולמה, וחכה לאישור.")
        sys.exit(0)

    try:
        STATE.parent.mkdir(parents=True, exist_ok=True)
        state = json.loads(STATE.read_text(encoding="utf-8")) if STATE.exists() else {}
    except Exception:
        state = {}
    count = state.get(session, 0)
    cap = CAP_ASKED if ASK.search(user) else CAP_UNASKED
    if count >= cap:
        block(f"כבר הופעלו {count} סוכנים בסשן הזה (התקרה {cap}). "
              "עשה את השאר בעצמך, או שאל את המשתמש אם להפעיל עוד.")
    state[session] = count + 1
    if len(state) > 50:
        state = dict(list(state.items())[-50:])
    try:
        STATE.write_text(json.dumps(state), encoding="utf-8")
    except Exception:
        pass
    sys.exit(0)


if __name__ == "__main__":
    main()
