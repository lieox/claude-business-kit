#!/usr/bin/env python3
"""חיפוש וביקורת על מאגר הזיכרון, בלי לטעון את כל האינדקס לקונטקסט.

שלוש שכבות, מהזול ליקר:
  find   , אינדקס דחוס של התאמות (שם, סוג, תיאור מקוצר)
  show   , גוף מלא של זיכרונות נבחרים לפי שם
  audit  , מצב המאגר: נפח, חריגים, שדות חסרים, קישורים שבורים
"""
import argparse
import os
import re
import sys
from pathlib import Path

def _default_memory_dir():
    """תיקיית הזיכרון של קלוד: MEM_DIR אם הוגדר, אחרת התיקייה עם ה-MEMORY.md שעודכן אחרון."""
    env = os.environ.get("MEM_DIR")
    if env:
        return Path(env).expanduser()
    found = sorted((Path.home() / ".claude" / "projects").glob("*/memory/MEMORY.md"),
                   key=lambda f: f.stat().st_mtime, reverse=True)
    return found[0].parent if found else Path.home() / ".claude" / "memory"


MEMORY_DIR = _default_memory_dir()
INDEX_FILE = "MEMORY.md"
# אינדקס משני לזיכרונות סגורים, מושהים או רדומים. ההארנס לא טוען אותו לסשן,
# ולכן הוא לא נספר בתקרה, אבל זיכרון שמופיע בו נחשב מאונדקס.
ARCHIVE_INDEX_FILE = "MEMORY-archive.md"
INDEX_FILES = {INDEX_FILE, ARCHIVE_INDEX_FILE}
OVERSIZE_CHARS = 20000
SNIPPET_CHARS = 160
HEBREW_CHARS_PER_TOKEN = 3
# שתי תקרות, מה שנחתך ראשון קובע. מקור: code.claude.com/docs/en/memory
# "The first 200 lines of MEMORY.md, or the first 25KB, whichever comes first"
#
# ⚠️ תוקן 20.09.2026: ה-"25KB" האלה נמדדים ב-*תווים*, לא בבייטים, והכיול הקודם
# (25 * 1024 בייט) היה מחמיר ב-22% על אינדקס עברי, כי עברית היא 2 בייט לתו.
# הראיה: ההארנס הזהיר "MEMORY.md is 24.8KB (limit: 24.4KB)" בדיוק כשהקובץ היה
# 25,352 תווים (= 24.76 KiB) ו-33,860 בייט (= 33.1 KiB). הוא דיווח 24.8 ⟹ תווים.
# ומ-24.4 KiB * 1024 = 24,986 נגזר שהתקרה עצמה היא 25,000 תווים עגולים,
# שההארנס מציג חלקי 1024. בדיקת אימות: 25,352 - 25,000 = 352 תווים חריגה,
# וההארנס חתך "2 of 171 lines starting at line 170", כלומר 2 השורות האחרונות
# שסכומן ~395 תווים. מתיישב.
INDEX_CEILING_CHARS = 25_000
INDEX_CEILING_LINES = 200


class Memory:
    def __init__(self, path):
        self.path = path
        self.name = path.stem
        text = path.read_text(encoding="utf-8", errors="replace")
        self.raw = text
        self.frontmatter, self.body = _split_frontmatter(text)
        self.description = _field(self.frontmatter, "description")
        self.type = _field(self.frontmatter, "type")
        self.nested = bool(re.search(r"^metadata:", self.frontmatter, re.M))
        self.kind = _field(self.frontmatter, "kind")
        self.chars = len(text)

    @property
    def tokens(self):
        return self.chars // HEBREW_CHARS_PER_TOKEN

    @property
    def links(self):
        # ⛔ קוד לא נספר כקישור. זיכרון שמדגים דליפה מצטט שם קובץ פנימי בתוך
        # backticks, וזיכרון אחר מחזיק
        # פלייסהולדר נתיב. שניהם דווחו כ"קישור שבור" 30.08 והם false positive:
        # "תיקון" שלהם היה הורס את ההדגמה עצמה. מסירים בלוקי קוד ו-code spans קודם.
        text = re.sub(r"```.*?```", " ", self.body, flags=re.S)
        text = re.sub(r"`[^`\n]*`", " ", text)
        found = re.findall(r"\[\[([^\[\]\n|]{1,60})\]\]", text)
        return [f.strip() for f in found if f.strip()]


def _split_frontmatter(text):
    if not text.startswith("---"):
        return "", text
    end = text.find("\n---", 3)
    if end == -1:
        return "", text
    return text[3:end], text[end + 4:]


def _field(frontmatter, key):
    match = re.search(rf"^\s*{key}:\s*(.+)$", frontmatter, re.M)
    if not match:
        return ""
    return match.group(1).strip().strip('"').strip("'")


def load_all(memory_dir=MEMORY_DIR):
    return [Memory(p) for p in sorted(Path(memory_dir).glob("*.md")) if p.name not in INDEX_FILES]


def score(memory, terms, deep):
    """שם ותיאור שוקלים יותר מהגוף, כי הם מה שמחליט רלוונטיות."""
    haystacks = [(memory.name.replace("_", " ").lower(), 6),
                 (memory.description.lower(), 3)]
    if deep:
        haystacks.append((memory.body.lower(), 1))
    total = 0
    for term in terms:
        for text, weight in haystacks:
            if term in text:
                total += weight
    return total


def cmd_find(args):
    terms = [t.lower() for t in args.terms]
    memories = load_all(args.dir)
    hits = [(score(m, terms, args.deep), m) for m in memories]
    hits = sorted([h for h in hits if h[0] > 0], key=lambda h: -h[0])[:args.limit]
    if not hits:
        print("אין התאמות. נסה מונח אחר או --deep לחיפוש גם בגוף.")
        return 1
    for points, memory in hits:
        label = memory.kind or memory.type or "?"
        snippet = " ".join(memory.description.split())[:SNIPPET_CHARS]
        print(f"[{points:2d}] {memory.name}  ({label}, {memory.tokens} טוקנים)")
        print(f"     {snippet}{'...' if len(memory.description) > SNIPPET_CHARS else ''}")
    print(f"\n{len(hits)} התאמות. לגוף מלא: mem.py show <שם> [<שם>...]", file=sys.stderr)
    return 0


def cmd_show(args):
    memories = {m.name: m for m in load_all(args.dir)}
    for name in args.names:
        memory = memories.get(name) or memories.get(name.removesuffix(".md"))
        if not memory:
            print(f"לא נמצא: {name}", file=sys.stderr)
            continue
        if memory.chars > args.max_chars:
            print(f"--- {memory.name} (חתוך ל-{args.max_chars} מתוך {memory.chars} תווים) ---")
            print(memory.body[:args.max_chars])
        else:
            print(f"--- {memory.name} ---")
            print(memory.body.strip())
        print()
    return 0


def cmd_audit(args):
    memories = load_all(args.dir)
    index_path = Path(args.dir) / INDEX_FILE
    index_text = index_path.read_text(encoding="utf-8") if index_path.exists() else ""
    archive_path = Path(args.dir) / ARCHIVE_INDEX_FILE
    archive_text = archive_path.read_text(encoding="utf-8") if archive_path.exists() else ""
    names = {m.name for m in memories}

    total_chars = sum(m.chars for m in memories)
    oversize = sorted([m for m in memories if m.chars > args.oversize], key=lambda m: -m.chars)
    untyped = [m for m in memories if not m.type]
    no_description = [m for m in memories if not m.description]
    long_description = [m for m in memories if len(m.description) > 600]
    broken_links = {m.name: [l for l in m.links if l not in names] for m in memories}
    broken_links = {k: v for k, v in broken_links.items() if v}
    # התאמה על "(שם.md)" ולא על השם לבד: שם שהוא תת-מחרוזת של שם אחר נספר אחרת כמאונדקס.
    unindexed = [m.name for m in memories if f"({m.name}.md)" not in index_text + archive_text]
    styles = {"מקונן תחת metadata": [m for m in memories if m.nested],
              "שטוח": [m for m in memories if not m.nested]}

    print(f"מאגר: {len(memories)} זיכרונות, {total_chars:,} תווים (~{total_chars // HEBREW_CHARS_PER_TOKEN:,} טוקנים)")
    index_chars = len(index_text)
    index_bytes = len(index_text.encode("utf-8"))
    headroom = INDEX_CEILING_CHARS - index_chars
    print(f"אינדקס: {len(index_text.splitlines())} שורות, {index_chars:,} תווים "
          f"({index_chars / 1024:.1f} KiB, כמו שההארנס מודד; {index_bytes:,} בייט על הדיסק) "
          f"(~{index_chars // HEBREW_CHARS_PER_TOKEN:,} טוקנים בכל סשן)")
    lines = len(index_text.splitlines())
    line_room = INDEX_CEILING_LINES - lines
    per_line = max(1, index_chars // max(1, lines))
    binding = "תווים" if headroom < line_room * per_line else "שורות"
    if headroom <= 0 or line_room <= 0:
        print(f"   קריטי: האינדקס חצה תקרה ({index_chars:,} מתוך {INDEX_CEILING_CHARS:,} תווים). "
              f"הוא נטען חלקית עכשיו, בשקט.")
    elif headroom < 3000 or line_room < 25:
        print(f"   אזהרה: {headroom:,} תווים ו-{line_room} שורות לתקרה. "
              f"החוסם הוא ה{binding}, כלומר בערך {min(headroom // per_line, line_room)} שורות.")
    if archive_text:
        print(f"ארכיון: {len(archive_text.splitlines())} שורות, {len(archive_text):,} תווים "
              f"({ARCHIVE_INDEX_FILE}, לא נטען לסשן ולא נספר בתקרה)")
    print()
    _section(f"מעל {args.oversize:,} תווים (מועמדים לפיצול)",
             [f"{m.chars:>7,}  {m.name}" for m in oversize])
    _section("תיאור מעל 600 תווים (יקר בכל היזכרות)",
             [f"{len(m.description):>7,}  {m.name}" for m in long_description])
    _section("בלי שדה type", [m.name for m in untyped])
    _section("בלי description", [m.name for m in no_description])
    _section("לא מופיעים באף אינדקס", unindexed)
    _section("קישורים שבורים", [f"{k} -> {', '.join(v)}" for k, v in broken_links.items()])
    minority = min(styles.items(), key=lambda kv: len(kv[1]))
    print(f"## סגנון frontmatter: {', '.join(f'{k} {len(v)}' for k, v in styles.items())}")
    if minority[1] and len(minority[1]) < len(memories) / 2:
        print(f"   המיעוט ({minority[0]}): {', '.join(m.name for m in minority[1][:12])}")
    print()
    problems = len(oversize) + len(untyped) + len(no_description) + len(broken_links) + len(unindexed)
    print(f"\nסהכ פריטים לטיפול: {problems}")
    return 0 if problems == 0 else 1


def _resolve(target, names):
    """קישור שנכתב עם מקפים או עם סיומת .md עדיין מכוון לזיכרון קיים."""
    candidate = target.strip().removesuffix(".md")
    for variant in (candidate, candidate.replace("-", "_")):
        if variant in names:
            return variant
    return None


def cmd_fix_links(args):
    """מתקן קישורי ויקי שנכתבו במקפים או עם סיומת. ריצה יבשה כברירת מחדל."""
    memories = load_all(args.dir)
    names = {m.name for m in memories}
    planned = []
    for memory in memories:
        for target in set(memory.links):
            if target in names:
                continue
            fixed = _resolve(target, names)
            if fixed:
                planned.append((memory, target, fixed))

    if not planned:
        print("אין קישורים לתיקון.")
        return 0
    for memory, target, fixed in planned:
        print(f"  {memory.name}: [[{target}]] -> [[{fixed}]]")
    print(f"\n{len(planned)} תיקונים ב-{len({m.name for m, _, _ in planned})} קבצים.")
    if not args.apply:
        print("ריצה יבשה. להחלה: mem.py fix-links --apply")
        return 0

    by_file = {}
    for memory, target, fixed in planned:
        by_file.setdefault(memory, []).append((target, fixed))
    for memory, pairs in by_file.items():
        text = memory.raw
        for target, fixed in pairs:
            text = text.replace(f"[[{target}]]", f"[[{fixed}]]")
        memory.path.write_text(text, encoding="utf-8")
    print(f"הוחל על {len(by_file)} קבצים.")
    return 0


LOG_DIR = Path(os.environ.get("MEM_LOG_DIR", str(MEMORY_DIR.parent / "memory-logs"))).expanduser()
KEEP_SECTIONS = 3


def _sections(body):
    """מפצל לפי כותרות ## , שהן בלוקי היומן המתוארכים."""
    parts = re.split(r"^(## .*)$", body, flags=re.M)
    head = parts[0]
    blocks = [(parts[i], parts[i + 1]) for i in range(1, len(parts) - 1, 2)]
    return head, blocks


def _is_parseable(text):
    """שער לפני כתיבה: frontmatter חייב להיפתח, להיסגר, ולהחזיק name ו-description."""
    if not text.startswith("---\n"):
        return False, "אין פתיח frontmatter"
    end = text.find("\n---\n", 3)
    if end == -1:
        return False, "אין סוגר frontmatter בשורה נפרדת"
    head = text[3:end]
    for field in ("name", "description"):
        if not re.search(rf"^{field}:", head, re.M):
            return False, f"חסר שדה {field}"
    return True, ""


BLOCK_DATE_ISO = re.compile(r"20\d{2}-\d{2}-\d{2}")
BLOCK_DATE_DMY = re.compile(r"\b(\d{1,2})[./](\d{1,2})(?:[./](20\d{2}))?\b")
POINTER_LINE = re.compile(
    r"^> (?:היומן המלא|\d+ מקרים מתוארכים ישנים הועברו) .*$\n?", re.M)
DEFAULT_YEAR = "2026"


def block_date(header):
    """מחזיר תאריך מנורמל מכותרת בלוק, או None אם הבלוק אינו מקרה מתוארך."""
    iso = BLOCK_DATE_ISO.search(header)
    if iso:
        return iso.group(0)
    dmy = BLOCK_DATE_DMY.search(header)
    if dmy:
        day, month, year = dmy.group(1), dmy.group(2), dmy.group(3) or DEFAULT_YEAR
        if 1 <= int(month) <= 12 and 1 <= int(day) <= 31:
            return f"{year}-{int(month):02d}-{int(day):02d}"
    return None


def partition_blocks(blocks, keep_recent):
    """כלל הפיצול: מקרה מתוארך עם ראיה הולך ליומן, כלל או מפה או צ'קליסט נשאר בזיכרון.

    בנוסף נשארים בזיכרון גם המקרים המתוארכים האחרונים, לפי תאריך ולא לפי מיקום בקובץ.
    """
    dated = [(block_date(title), title, body) for title, body in blocks]
    undated = [(t, b) for d, t, b in dated if d is None]
    with_date = sorted([(d, t, b) for d, t, b in dated if d], key=lambda x: x[0], reverse=True)
    recent = {(t, b) for _, t, b in with_date[:keep_recent]}
    kept, moved = [], []
    for title, body in blocks:
        target = kept if (title, body) in {(t, b) for t, b in undated} or (title, body) in recent else moved
        target.append((title, body))
    return kept, moved


def cmd_split(args):
    """מוציא מקרים מתוארכים ישנים מזיכרון שהתנפח, ומשאיר כללים, מפות והמצב העדכני."""
    memories = {m.name: m for m in load_all(args.dir)}
    memory = memories.get(args.name)
    if not memory:
        print(f"לא נמצא: {args.name}", file=sys.stderr)
        return 1

    body = POINTER_LINE.sub("", memory.body)
    head, blocks = _sections(body)
    log_path = LOG_DIR / f"{memory.name}.md"
    # היומן לא ממוזג חזרה: בלוק שיצא ליומן לא חוזר לזיכרון. עד 18.10.2026 split משך
    # מהיומן פרקי "הועבר מהזיכרון", תתי-כותרות בלי תאריך ובלוקים מפיצולים קודמים,
    # והזיכרון גדל במקום לקטון (במקרה אחד מ-16,594 ל-47,704 תווים).
    kept, moved = partition_blocks(blocks, args.keep)
    if not moved:
        print(f"{memory.name}: אין מקרים מתוארכים ישנים להוצאה.")
        return 0

    pointer = (f"\n\n> {len(moved)} מקרים מתוארכים ישנים הועברו ל-"
               f"`{log_path}`. כללים, מפות והמצב העדכני נשארו כאן.\n")
    new_body = head.rstrip() + pointer + "".join(t + b for t, b in kept)
    new_text = f"---{memory.frontmatter}\n---" + new_body
    moved_text = "".join(t + b for t, b in moved)
    if log_path.exists():
        # הבלוקים החדשים נכנסים לראש היומן, אחרי הפתיח, והיומן הקיים נשמר בלי שינוי
        old_log = log_path.read_text(encoding="utf-8")
        log_head, _ = _sections(old_log)
        prefix = log_head.rstrip("\n") + "\n\n" if log_head.strip() else ""
        log_text = prefix + moved_text.rstrip("\n") + "\n\n" + old_log[len(log_head):]
    else:
        old_log = ""
        log_text = (f"# יומן ריצה: {memory.name}\n\n"
                    f"מקרים מתוארכים שהוצאו מהזיכרון כדי לצמצם עלות היזכרות.\n"
                    f"הכללים והמפות נשארו בזיכרון עצמו.\n\n"
                    + moved_text)

    undated_kept = sum(1 for t, _ in kept if block_date(t) is None)
    print(f"{memory.name}: {memory.chars:,} -> {len(new_text):,} תווים")
    print(f"  נשארים: {len(kept)} בלוקים ({undated_kept} כללים ומפות, {len(kept) - undated_kept} מקרים אחרונים)")
    print(f"  ליומן:  {len(moved)} מקרים מתוארכים"
          + (f", בראש יומן קיים ({len(old_log):,} תווים, נשמר כמו שהוא)" if old_log else ""))
    if len(memory.description) > 600:
        print(f"  שים לב: ה-description באורך {len(memory.description)} תווים ודורש קיצור ידני")
    if not args.apply:
        print("ריצה יבשה. להחלה: mem.py split <שם> --apply")
        return 0

    ok, why = _is_parseable(new_text)
    if not ok:
        print(f"נעצר לפני כתיבה: {why}. הקובץ לא שונה.", file=sys.stderr)
        return 2
    if old_log and old_log[len(_sections(old_log)[0]):] not in log_text:
        print("נעצר לפני כתיבה: היומן הקיים לא נשמר במלואו. שום קובץ לא שונה.", file=sys.stderr)
        return 2

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_path.write_text(log_text, encoding="utf-8")
    memory.path.write_text(new_text, encoding="utf-8")
    print(f"הוחל. יומן: {log_path}")
    return 0


def _section(title, rows):
    print(f"## {title}: {len(rows)}")
    for row in rows[:20]:
        print(f"   {row}")
    if len(rows) > 20:
        print(f"   ... ועוד {len(rows) - 20}")
    print()


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="חיפוש וביקורת על מאגר הזיכרון")
    parser.add_argument("--dir", default=str(MEMORY_DIR))
    subs = parser.add_subparsers(dest="command", required=True)

    p_find = subs.add_parser("find", help="אינדקס דחוס של התאמות")
    p_find.add_argument("terms", nargs="+")
    p_find.add_argument("--deep", action="store_true", help="לחפש גם בגוף הזיכרון")
    p_find.add_argument("--limit", type=int, default=8)
    p_find.set_defaults(func=cmd_find)

    p_show = subs.add_parser("show", help="גוף מלא לפי שם")
    p_show.add_argument("names", nargs="+")
    p_show.add_argument("--max-chars", type=int, default=6000)
    p_show.set_defaults(func=cmd_show)

    p_split = subs.add_parser("split", help="הוצאת יומן ישן מזיכרון מנופח")
    p_split.add_argument("name")
    p_split.add_argument("--keep", type=int, default=KEEP_SECTIONS)
    p_split.add_argument("--apply", action="store_true")
    p_split.set_defaults(func=cmd_split)

    p_fix = subs.add_parser("fix-links", help="תיקון קישורי ויקי שבורים")
    p_fix.add_argument("--apply", action="store_true", help="לכתוב בפועל")
    p_fix.set_defaults(func=cmd_fix_links)

    p_audit = subs.add_parser("audit", help="מצב המאגר")
    p_audit.add_argument("--oversize", type=int, default=OVERSIZE_CHARS)
    p_audit.set_defaults(func=cmd_audit)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
