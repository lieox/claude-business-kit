# Claude Business Kit

הערכה הזאת הופכת את Claude Code לצוות קטן לעסק. יש בה סוכנים לתוכן, למשפטי, לאתרים ולשיווק, בוט טלגרם לכל עובד, והגנות שחוסמות מחיקות, פקודות מסוכנות וגישה לקבצי סודות.

נבנה על ידי LvlUp.

## מה בפנים

### סוכנים
הסוכנים ב-`agents/`, והידע שלהם ב-`agents-kb/`.

| סוכן | מה הוא עושה |
|---|---|
| `content-strategist` | הוקים, כיתובים, תסריטים, רשימות צילום ולוח תוכן לאינסטגרם ולטיקטוק |
| `focus-coach` | עוזר לבחור כשיש יותר מדי רעיונות, פרויקטים והזדמנויות |
| `lexi` | בודקת פרטיות, דיוור, הגנת הצרכן וחוזים, ומכינה טיוטות. לא תחליף לעו"ד |
| `ewob` | בונה אתרים ודפי נחיתה, וממיר עיצוב לאלמנטור |
| `market-*` (5 סוכנים) | ניתוח שיווקי של אתר: תוכן, המרות, מתחרים, אסטרטגיה וטכני |

### סקילים
בתיקייה `skills/`: `/market` עם 13 פקודות משנה, בדיקת טקסט ללקוח שלא יישמע כמו AI, בדיקה של כל תוצר לפני שהוא יוצא ללקוח, בדיקת חוקיות לפני דיוור, עבודה עם ווטסאפ דרך SendPulse (`sendpulse-whatsapp-ops`), וגיבוי של פלואו או תרחיש לפני שעורכים אותו (`automation-snapshot-backup`). סקילים נוספים שכדאי להתקין: [`docs/recommended-skills.md`](docs/recommended-skills.md).

### הגדרות, הוקים וחוקים
בתיקייה `claude-config/` יש תבנית CLAUDE.md עם חוקי עבודה, תבנית לבניית סוכן, ושבעה הוקים:
- `block_dangerous.py` חוסם מחיקה רקורסיבית, `git push --force`, `git reset --hard` ופירמוט.
- `protect_secrets.py` לא נותן לקלוד לקרוא או לערוך קבצי סודות.
- `agent_guard.py` שומר על המכסה: סוכן רגיל מותר עד תקרה לסשן, וצי סוכנים רק כשמבקשים במפורש.
- `install_log_reminder.py` מזכיר לקלוד לרשום ב-INSTALLS.md כל דבר שהוא מתקין.
- `session_notes.py` מעביר את הערות העבודה (`working.md`) מסשן לסשן.
- `session_log.py` רושם כל סבב עבודה ל-`~/.claude/activity-log.md`.
- `hebrew_reply_guard.py` מחזיר את קלוד לעברית כשהוא עונה באנגלית על הודעה בעברית.

ובנוסף:
- `rules/`: ארבעה קובצי חוקים שקלוד טוען לבד, על אימות לפי רדיוס הנזק, היגיינת זיכרון, איפה שומרים קבצים, ויומן התקנות.
- `commands/wrap.md`: הפקודה `/wrap` לסוף סשן. היא בודקת שכל מה שנעשה תועד במקום הנכון.
- `INSTALLS.template.md`: יומן של כל מה שמותקן במחשב.
- `templates/`: תבנית לפרויקט חדש ו-`.gitignore` לתיקיית העבודה.

### ניהול סביבת העבודה
- `tools/memory/mem.py`: חיפוש במאגר הזיכרון של קלוד, בדיקת מצב, ופיצול של זיכרון שהתנפח.
- `tools/git-sync/`: גיבוי אוטומטי לגיטהאב, בבוקר ובערב, עם סריקת סודות לפני כל קומיט.
- הסקילים `workspace-structure-audit` (קישורים שבורים וסוכנים יתומים), `docs-freshness-audit` (תיעוד שהתיישן) ו-`agentshield` (סריקת אבטחה של ההגדרות).

### בוט טלגרם לכל עובד
בתיקייה `telegram-bridge/` יש גשר אחד שמפעיל כמה בוטים. לכל בוט יש תפקיד, תיקיית עבודה והרשאות משלו, למשל מזכירה שרואה את הווטסאפ אבל לא יכולה לשלוח.

### חיבורים (MCP)
בתיקייה `mcp/` יש הוראות התקנה לשלושה שרתים:
- `sendpulse/`: ווטסאפ דרך SendPulse, עם [sendpulse-whatsapp-mcp](https://github.com/lieox/sendpulse-whatsapp-mcp). מתחילים במצב קריאה בלבד.
- `playwright/`: קלוד פותח דפדפן, לוחץ, ממלא טפסים ומצלם מסך. של מיקרוסופט.
- `video-vision/`: קלוד צופה בסרטון, רואה את הפריימים ושומע את האודיו. כולל הגדרה שחובה לתמלול בעברית.

### מדריכים
בתיקייה `docs/`: [איך בונים את סביבת העבודה של קלוד](docs/harness.md), [איך בונים סוכן יד ימין לעסק](docs/chief-of-staff.md), [סקילים מומלצים](docs/recommended-skills.md), ותבנית לקובץ פרופיל אישי (`personal-md-template.md`).

## התקנה

ב-Windows עובדים לפי [`install/windows.md`](install/windows.md), הכול ב-Command Prompt.

במק, מתוך תיקיית הערכה:
```
mkdir -p ~/.claude/hooks ~/.claude/rules ~/.claude/commands ~/.claude/tools
cp -Rn agents agents-kb skills ~/.claude/
cp -n claude-config/hooks/*.py ~/.claude/hooks/
cp -n claude-config/rules/*.md ~/.claude/rules/
cp -n claude-config/commands/*.md ~/.claude/commands/
cp -n tools/memory/mem.py tools/git-sync/git-sync.sh ~/.claude/tools/
[ -f ~/.claude/INSTALLS.md ] || cp claude-config/INSTALLS.template.md ~/.claude/INSTALLS.md
```
אחר כך ממזגים את `claude-config/settings.example.json` לתוך `~/.claude/settings.json`. במק מחליפים בכל שורת הוק את `python` ב-`python3`. בלי ההחלפה ההוקים נכשלים בשקט, ואף פקודה לא נחסמת.

אחרי ההתקנה ממלאים את `claude-config/CLAUDE.template.md` ושומרים אותו כ-`~/.claude/CLAUDE.md`. הסוכנים content-strategist, focus-coach, lexi ו-ewob קוראים אותו לפני שהם עונים, אז כדאי שיהיה בו מי אתם, מה העסק, מי הלקוחות ואיך לפנות אליכם.

## אבטחה
טוקנים ומפתחות לא נכנסים לריפו. `bots.json`, `mcp.json` ו-`state/` נמצאים ב-`.gitignore`.

## רישיון
MIT. מותר להשתמש, לשנות ולהפיץ, עם שמירת הודעת הרישיון. סקילי `market` הם של [Zubair Trabzada](https://github.com/zubair-trabzada/ai-marketing-claude), גם הם ב-MIT, וקובץ הרישיון שלהם נמצא ב-`skills/market/LICENSE`. הידע של `content-strategist` ושל `focus-coach` מסכם תוכן ציבורי, וכל קובץ מציין את המקור שלו.
