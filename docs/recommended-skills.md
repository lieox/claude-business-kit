# סקילים מומלצים

סקיל הוא חבילת הוראות שקלוד טוען כשהמשימה מתאימה. חלק מהסקילים כבר בתוך הערכה, ואת השאר מתקינים מהמקור.

## כבר בערכה (`skills/`)

| סקיל | מתי הוא רץ |
|---|---|
| `anti-ai-writing` | לפני שטקסט יוצא ללקוח: מוריד סימנים של כתיבת AI, בעברית ובאנגלית, עם סורק |
| `deliverable-adversarial-review` | לפני שקובץ, דף או מסמך יוצא ללקוח: בודק את התוצר כמו שהלקוח יראה אותו |
| `il-outreach-legality-gate` | לפני דיוור, הודעות שיווקיות או פנייה קרה בישראל: בודק הסכמה וחוק הספאם |
| `market` ועוד 13 | ניתוח שיווקי של אתר. מתחילים עם `/market audit <כתובת>`. מקור: [ai-marketing-claude](https://github.com/zubair-trabzada/ai-marketing-claude), רישיון MIT |

## להתקין מהמקור

**מה-marketplace הרשמי של Anthropic**, בתוך Claude Code:
```
/plugin install superpowers@claude-plugins-official
/plugin install skill-creator@claude-plugins-official
/plugin install frontend-design@claude-plugins-official
```
- `superpowers`: תכנון לפני עבודה, דיבאג שיטתי, ובדיקה שמשהו באמת עובד לפני שאומרים "בוצע".
- `skill-creator`: לבנות סקילים משלכם.
- `frontend-design`: עיצוב דפים וממשקים שלא נראים גנריים.

**קבצים: PDF, Word, Excel, PowerPoint**
```
/plugin marketplace add anthropics/skills
/plugin install document-skills@anthropic-agent-skills
```

**שיווק, מכירות ומשפטי** (מ-Anthropic):
```
/plugin marketplace add anthropics/knowledge-work-plugins
/plugin install marketing@knowledge-work-plugins
/plugin install sales@knowledge-work-plugins
/plugin install legal@knowledge-work-plugins
```

**קופי ושיווק**: [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills), רישיון MIT. כולל `copywriting`, `page-cro`, `form-cro`, `email-sequence`, `content-strategy` ועוד. בטרמינל:
```
npx skills add coreyhaines31/marketingskills
```

**סקילים לשוק הישראלי**: [github.com/skills-il](https://github.com/skills-il), רישיון MIT. ריפו לכל תחום: הנהלת חשבונות, מיסים, תקשורת עם לקוחות, ציות ופרטיות, שיווק, חינוך ועוד. הוראות ההתקנה בעמוד של כל ריפו.

## כלל אחד לפני התקנה
סקיל מריץ הוראות במחשב שלכם. מתקינים רק ממקור מוכר, וקוראים את קובץ ה-`SKILL.md` לפני ההתקנה.
