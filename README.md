# Claude Business Kit

ערכה להקמת סביבת Claude Code לעסק: הגדרות, הוקים לבטיחות, תבנית סוכן, בוט טלגרם לכל עובד עם הרשאות שונות, וחיבור ל-SendPulse.

נבנה ונבדק על ידי LvlUp.

## מה בפנים
| תיקייה | מה זה |
|---|---|
| `install/windows.md` | התקנה של Git, Node, Python, FFmpeg, Claude Code, Remotion ו-HyperFrames |
| `claude-config/` | תבנית CLAUDE.md, הגדרות, 3 הוקים ותבנית סוכן |
| `telegram-bridge/` | בוט טלגרם לכל עובד, כל אחד עם תפקיד והרשאות משלו |
| `mcp/sendpulse/` | שרת MCP ל-SendPulse (ווטסאפ) |

## ההוקים
- `block_dangerous.py`: חוסם מחיקות רקורסיביות, `git push --force`, `git reset --hard` ופירמוט.
- `protect_secrets.py`: מונע מקלוד לקרוא או לערוך קבצי סודות.
- `session_log.py`: רושם כל סבב עבודה ל-`~/.claude/activity-log.md`.

## סדר הקמה מומלץ
1. `install/windows.md`
2. `claude-config/`: ממלאים CLAUDE.md ומעתיקים הוקים
3. `mcp/sendpulse/`
4. `telegram-bridge/`

## אבטחה
טוקנים ומפתחות לא נכנסים לריפו. `bots.json`, `mcp.json` ו-`state/` נמצאים ב-`.gitignore`.
