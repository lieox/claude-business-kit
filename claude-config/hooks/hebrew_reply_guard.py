#!/usr/bin/env python3
"""Stop hook: חוסם תשובה שרובה אותיות לטיניות כשההודעה האחרונה של המשתמש נכתבה בעברית.

קוד, נתיבים, קישורים ופלט פקודות לא נספרים. כל תקלה בקריאה = מעבר שקט (fail-open).
"""
import json
import re
import sys

HEB = re.compile(r"[֐-׿]")
LAT = re.compile(r"[A-Za-z]")
MIN_LATIN = 60
MAX_HEBREW_SHARE = 0.4
ASKED_ENGLISH = re.compile(r"באנגלית|באינגליש|\benglish\b", re.I)

REASON = (
    "המשתמש כתב בעברית, והתשובה שלך יצאה ברובה באנגלית. "
    "כתוב אותה מחדש בעברית, בלשון הפנייה שמוגדרת ב-CLAUDE.md. קוד, נתיבים, שמות ופלט פקודות נשארים כמו שהם."
)


def strip_noise(text):
    text = re.sub(r"```.*?```", " ", text, flags=re.S)
    text = re.sub(r"`[^`\n]*`", " ", text)
    text = re.sub(r"\]\([^)]*\)", "]", text)
    text = re.sub(r"https?://\S+", " ", text)
    text = re.sub(r"(?<![\w])[~.]{0,2}/[^\s)]+", " ", text)
    return text


def genuine_user_text(entry):
    if entry.get("type") != "user" or entry.get("isMeta") or entry.get("isCompactSummary"):
        return None
    content = entry.get("message", {}).get("content")
    if isinstance(content, str):
        parts = [content]
    elif isinstance(content, list):
        if any(isinstance(b, dict) and b.get("type") == "tool_result" for b in content):
            return None
        parts = [b.get("text", "") for b in content if isinstance(b, dict) and b.get("type") == "text"]
    else:
        return None
    raw = "\n".join(parts)
    if "<task-notification>" in raw or "[SYSTEM NOTIFICATION" in raw:
        return None
    text = re.sub(r"<system-reminder>.*?</system-reminder>", " ", raw, flags=re.S)
    text = re.sub(r"<[^>]+>", " ", text).strip()
    return text or None


def assistant_text(entry):
    if entry.get("type") != "assistant":
        return ""
    content = entry.get("message", {}).get("content")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(b.get("text", "") for b in content if isinstance(b, dict) and b.get("type") == "text")
    return ""


def is_hebrew(text):
    heb, lat = len(HEB.findall(text)), len(LAT.findall(text))
    return heb >= 3 and heb >= lat


def mostly_latin(text):
    clean = strip_noise(text)
    heb, lat = len(HEB.findall(clean)), len(LAT.findall(clean))
    return lat >= MIN_LATIN and heb / (heb + lat) < MAX_HEBREW_SHARE


def decide(payload):
    if payload.get("stop_hook_active"):
        return None
    entries = []
    with open(payload["transcript_path"], encoding="utf-8") as f:
        for line in f:
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    last_user, reply = None, []
    for entry in entries:
        text = genuine_user_text(entry)
        if text is not None:
            last_user, reply = text, []
            continue
        reply.append(assistant_text(entry))
    if payload.get("last_assistant_message"):
        reply.append(payload["last_assistant_message"])
    if not last_user or not is_hebrew(last_user):
        return None
    if ASKED_ENGLISH.search(last_user):
        return None
    if mostly_latin("\n".join(reply)):
        return {"decision": "block", "reason": REASON}
    return None


def main():
    try:
        result = decide(json.load(sys.stdin))
    except Exception:
        return
    if result:
        print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
