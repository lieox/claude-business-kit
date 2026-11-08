"""Telegram -> Claude Code bridge. One process serves several bots, each with its own role and permissions.

Run:  python bridge.py            (reads bots.json next to this file)
Each incoming message runs `claude -p` in the bot's workspace with only the tools that bot is allowed.
Standard library only, works on Windows, macOS and Linux.
"""
import json
import os
import shutil
import subprocess
import sys
import threading
import time
import urllib.parse
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
CONFIG = HERE / "bots.json"
STATE = HERE / "state"
STATE.mkdir(exist_ok=True)
LOG = STATE / "bridge.log"
TG_LIMIT = 4000
CLAUDE_TIMEOUT = 600


def log(msg):
    line = f"{time.strftime('%Y-%m-%d %H:%M:%S')} {msg}"
    print(line, flush=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def tg(token, method, **params):
    data = urllib.parse.urlencode(params).encode()
    url = f"https://api.telegram.org/bot{token}/{method}"
    with urllib.request.urlopen(url, data=data, timeout=70) as r:
        return json.loads(r.read().decode())


def send(token, chat_id, text):
    text = text.strip() or "(אין תשובה)"
    for i in range(0, len(text), TG_LIMIT):
        tg(token, "sendMessage", chat_id=chat_id, text=text[i:i + TG_LIMIT])


def load_json(path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def save_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def claude_exe():
    path = shutil.which("claude")
    if not path:
        sys.exit("claude not found on PATH. Install Claude Code first.")
    if path.lower().endswith((".cmd", ".bat")):
        # A .cmd wrapper runs through cmd.exe, where message text could inject commands.
        sys.exit("claude resolves to a .cmd wrapper. Use the native installer (claude.exe).")
    return path


CLAUDE = None


def run_claude(bot, chat_id, text):
    sessions_file = STATE / f"{bot['name']}-sessions.json"
    sessions = load_json(sessions_file, {})
    role = (HERE / bot["role_file"]).read_text(encoding="utf-8")
    workspace = Path(bot["workspace"]).expanduser()
    workspace.mkdir(parents=True, exist_ok=True)

    cmd = [
        CLAUDE, "-p",
        "--output-format", "json",
        "--append-system-prompt", role,
        "--max-turns", str(bot.get("max_turns", 15)),
    ]
    if bot.get("allowed_tools"):
        cmd += ["--allowedTools", ",".join(bot["allowed_tools"])]
    if bot.get("disallowed_tools"):
        cmd += ["--disallowedTools", ",".join(bot["disallowed_tools"])]
    for extra_dir in bot.get("extra_dirs", []):
        cmd += ["--add-dir", str(Path(extra_dir).expanduser())]
    if bot.get("mcp_config"):
        cmd += ["--mcp-config", str((HERE / bot["mcp_config"]).resolve()), "--strict-mcp-config"]
    session_id = sessions.get(str(chat_id))
    if session_id:
        cmd += ["--resume", session_id]

    # The message goes in via stdin, never as an argument: text starting with "-" would parse as a flag.
    proc = subprocess.run(
        cmd, cwd=workspace, input=text, capture_output=True,
        text=True, encoding="utf-8", timeout=CLAUDE_TIMEOUT
    )
    try:
        out = json.loads(proc.stdout)
    except json.JSONDecodeError:
        if session_id:  # stale session: start fresh once
            sessions.pop(str(chat_id), None)
            save_json(sessions_file, sessions)
            return run_claude(bot, chat_id, text)
        raise RuntimeError((proc.stderr or proc.stdout or "no output")[-500:])
    if out.get("session_id"):
        sessions[str(chat_id)] = out["session_id"]
        save_json(sessions_file, sessions)
    return out.get("result") or "(הסוכן סיים בלי טקסט)"


def handle(bot, msg):
    chat_id = msg["chat"]["id"]
    user_id = msg.get("from", {}).get("id")
    text = msg.get("text", "")
    if user_id not in bot["allowed_user_ids"]:
        log(f"[{bot['name']}] blocked user {user_id}")
        return
    if text.strip() == "/new":
        sessions_file = STATE / f"{bot['name']}-sessions.json"
        sessions = load_json(sessions_file, {})
        sessions.pop(str(chat_id), None)
        save_json(sessions_file, sessions)
        send(bot["token"], chat_id, "שיחה חדשה התחילה.")
        return
    if not text:
        send(bot["token"], chat_id, "כרגע אני מקבל רק טקסט.")
        return
    log(f"[{bot['name']}] in from {user_id}: {text[:80]}")
    tg(bot["token"], "sendChatAction", chat_id=chat_id, action="typing")
    try:
        reply = run_claude(bot, chat_id, text)
    except subprocess.TimeoutExpired:
        reply = "המשימה לקחה יותר מדי זמן ונעצרה. נסה לפרק אותה לחלקים."
    except Exception as e:  # report to the user instead of dying silently
        log(f"[{bot['name']}] error: {e}")
        reply = "משהו נכשל. הפרטים נרשמו בלוג."
    send(bot["token"], chat_id, reply)


def poll(bot):
    offset_file = STATE / f"{bot['name']}-offset.txt"
    offset = int(offset_file.read_text()) if offset_file.exists() else 0
    log(f"[{bot['name']}] polling")
    while True:
        try:
            res = tg(bot["token"], "getUpdates", offset=offset, timeout=50)
            for upd in res.get("result", []):
                offset = upd["update_id"] + 1
                offset_file.write_text(str(offset))  # advance first, so a crash never replays a message
                if "message" in upd:
                    handle(bot, upd["message"])
        except Exception as e:
            log(f"[{bot['name']}] poll error: {e}")
            time.sleep(5)


def main():
    global CLAUDE
    CLAUDE = claude_exe()
    if not CONFIG.exists():
        sys.exit("bots.json not found. Copy bots.example.json to bots.json and fill it in.")
    bots = json.loads(CONFIG.read_text(encoding="utf-8"))["bots"]
    for bot in bots:
        token_env = bot.get("token_env")
        bot["token"] = os.environ.get(token_env) if token_env else bot.get("token")
        if not bot["token"]:
            sys.exit(f"bot {bot['name']}: no token (set {token_env})")
    threads = [threading.Thread(target=poll, args=(b,), daemon=True) for b in bots]
    for t in threads:
        t.start()
    while True:
        time.sleep(3600)


if __name__ == "__main__":
    main()
