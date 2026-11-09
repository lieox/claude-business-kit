---
name: agentshield
description: Run an AgentShield security scan of the user's Claude Code setup (~/.claude) and report ONLY new or real findings against the saved baseline. Use when the user asks for סריקת אבטחה, בדיקת אבטחה, agentshield, security scan of the setup/agents/MCPs/hooks, or after installing a new plugin, MCP server, hook, or agent. Also use to scan a CLIENT Claude setup directory before delivery.
---

# AgentShield - סריקת אבטחה לסטאפ

AgentShield (ecc-agentshield, מבית ECC) סורק קונפיגורציית Claude Code: secrets, הרשאות, hooks, סוכנים, MCPs. רץ עם npx בלי התקנה קבועה.

## גרסה נעולה

**כל הסריקות, כולל שמירת baseline וסריקת לקוח: `ecc-agentshield@1.6.0`.** ה-baseline נבנה מחדש על 1.6.0 ב-14.09.2026. לא להריץ בלי גרסה.

- `npx -y ecc-agentshield` בלי גרסה מושך latest. ב-10.09.2026 latest עבר מ-1.4.0 ל-1.6.0, ואותו סטאפ בדיוק החזיר **1,820 "חדשים"** מול baseline שנבנה ב-1.4.0, לעומת **6** ב-1.4.0. המנוע החדש סורק פי שלושה קבצים ומוסיף מחלקות כללים, כך שהחלפת מנוע נראית כמו רגרסיה.
- **לא שומרים baseline בגרסה אחרת מזו שסורקת מולו**, ולא מחליפים גרסה בשורה אחת בלבד.
- מעבר גרסה: סריקה בגרסה החדשה, טריאז' לפי מחלקת ממצא, אישור, עדכון `references/known-findings.md`, baseline חדש בגרסה החדשה, ורק אז החלפת הגרסה בשורת הסריקה ובשורת השמירה יחד.

## סריקה שוטפת (ברירת מחדל)

```bash
DATE=$(date +%Y-%m-%d)
OUT=$CLAUDE_WORK_DIR/tools/agentshield-report-$DATE.md
TMP=$(mktemp -t agentshield-scan)
npx -y ecc-agentshield@1.6.0 scan --path ~/.claude --supply-chain \
  --baseline $CLAUDE_WORK_DIR/tools/agentshield-baseline.json \
  --format markdown > "$TMP" 2>/dev/null
# Format gate: only a real scan is allowed to land on $OUT. Writing straight to $OUT with
# `>` truncated it the instant npx started, so a crash left a garbage "report" behind
# (2026-08-16: 81 bytes of `API Error`). Validate first, move second.
if head -1 "$TMP" | grep -q '^# AgentShield Security Report' && grep -q 'Summary' "$TMP"; then
  mv "$TMP" "$OUT"; echo "scan saved: $OUT ($(wc -c < "$OUT") bytes)"
else
  echo "SCAN INVALID - $OUT left untouched. Raw output kept at: $TMP"; exit 1
fi
```

- exit code 2 = יש ממצאים, זה צפוי. הדוח נשמר ב-tools/.
- ההשוואה ל-baseline מציגה רגרסיות: ממצאים שלא היו בסריקה הקודמת.
- אחרי שהמשתמש מאשר שהמצב תקין, לרענן את ה-baseline, **באותה גרסה שסורקת מולו**:
  `npx -y ecc-agentshield@1.6.0 scan --path ~/.claude --supply-chain --save-baseline $CLAUDE_WORK_DIR/tools/agentshield-baseline.json --format json > /dev/null`

## איך לסכם למשתמש (חשוב)

לדווח בעברית, קצר, רק מה שחדש או אמיתי. **לא** להציף את כל הממצאים.

⛔ **הסיכום נכתב בצ'אט, לא לקובץ. ובשום מצב לא לנתיב הדוח.**
`agentshield-report-YYYY-MM-DD.md` שייך לפלט הגולמי של הסורק **בלבד**, והוא לקריאה בלבד ברגע שנכתב.
זו תקלה חוזרת ולא תיאורטית: ב-19.07, ב-02.08, ב-09.08 וב-23.08 הסיכום העברי נכתב על הדוח הגולמי
ומחק אותו. ב-23.08 נמדד במדויק, 111KB ב-11:00 הפכו ל-1.6KB ב-12:19, **והפלט הגולמי של אותן
ארבע סריקות אבוד לתמיד.** אם המשתמש ביקש במפורש סיכום כקובץ, הנתיב הוא
`$CLAUDE_WORK_DIR/tools/agentshield-summary-YYYY-MM-DD.md`, שם נפרד לגמרי.

לפני הסיכום, לקרוא את `references/known-findings.md` ולחסר את כל מה שברשימות שם: זו הרשימה המתוחזקת היחידה של false-positives ידועים + סיכונים מקובלים. אם המשתמש מאשר ממצא חדש כבטוח, מוסיפים אותו לקובץ הזה במקום להסביר אותו שוב בכל ריצה.

מה כן לדווח: ממצא קריטי/גבוה חדש שלא ב-known-findings.md, ובמיוחד: secrets חדשים בקבצים, hook חדש שלא מוכר, MCP package חשוד ב-supply-chain, הרשאה רחבה חדשה.

## אם עולה ממצא קריטי/גבוה חדש אמיתי

1. **לא לתקן אוטומטית.** לדווח למשתמש בעברית קודם: מה נמצא, איפה (נתיב קובץ), ולמה זה מסוכן.
2. אם נחשף secret אמיתי (token/key בקובץ שעלול להיכנס לגיט או שכבר נכנס): להתריע מיד שצריך לסובב אותו (rotate), ולוודא שהקובץ ב-.gitignore. לא להדביק את ה-secret עצמו בסיכום.
3. רק אחרי אישור המשתמש: או לתקן, או להוסיף ל-known-findings.md כסיכון מקובל ולרענן baseline.

## סריקת סטאפ של לקוח (לפני מסירה)

```bash
npx -y ecc-agentshield@1.6.0 scan --path /path/to/client/.claude --supply-chain --format markdown
```

גרסה נעולה על 1.6.0 ולא 1.4.0: אין כאן baseline שיישבר, ו-1.4.0 לא מגלה `.mcp.json` בשורש פרויקט (תוקן ב-1.5.0). בדוח ללקוח לציין את גרסת הסורק, ולקבץ את כל ממצאי `Missing prompt defense` לשורה אחת במקום להציף.

בלי baseline (אין היסטוריה), לדווח הכל חוץ מ-false-positives גנריים בסגנון known-findings.md (הרשימה שם שייכת לסטאפ שלך, לא לסטאפ של הלקוח).

## מצבי עומק (רק לבקשת המשתמש במפורש)

- `--injection` בדיקת prompt injection אקטיבית, `--sandbox` מריץ hooks בארגז חול, `--taint` מעקב זרימת נתונים, `--deep` הכל ביחד + ניתוח Opus (עולה כסף/זמן). לא להריץ כברירת מחדל.

## מיקומים

- baseline: `$CLAUDE_WORK_DIR/tools/agentshield-baseline.json`
- דוחות (פלט סורק גולמי, **לא לכתיבה אחרי הסריקה**): `$CLAUDE_WORK_DIR/tools/agentshield-report-YYYY-MM-DD.md`
- סיכום עברי, רק אם התבקש כקובץ: `$CLAUDE_WORK_DIR/tools/agentshield-summary-YYYY-MM-DD.md`
