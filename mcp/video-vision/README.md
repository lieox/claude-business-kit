# Video Vision: קלוד צופה בסרטונים

[claude-video-vision](https://github.com/jordanrendric/claude-video-vision) (רישיון MIT) נותן לקלוד לצפות בסרטון: הוא חותך פריימים עם ffmpeg ומתמלל את האודיו. ככה קלוד רואה מה קורה על המסך ושומע מה נאמר, עם זמנים.

## למה זה טוב לעסק
- לנתח רילס שעבד אצל מתחרה: מה ההוק, מה בכל שוט, מה נאמר בשנייה 3.
- לבדוק סרטון שלכם לפני פרסום: כתוביות, קצב, טקסט על המסך.
- לתמלל הקלטה של פגישה או שיעור ולסכם אותה.
- לעבוד עם `content-strategist` על סרטונים אמיתיים, ולא רק על רעיונות.

## דרישות
צריך ffmpeg, והוא כבר מותקן אם עברתם על `install/windows.md`. בשביל קישורי יוטיוב צריך גם `yt-dlp`.

לתמלול יש שלוש אפשרויות:

| אפשרות | עלות | הערות |
|---|---|---|
| Gemini API | חינם עד מכסה יומית | מפתח מ-[ai.google.dev](https://ai.google.dev/gemini-api/docs/api-key). הכי פשוט ב-Windows. בעברית לא נבדק |
| Whisper מקומי | חינם, בלי אינטרנט | במק: `brew install whisper-cpp`. המודל יורד לבד בשימוש הראשון |
| OpenAI API | בתשלום לפי שימוש | מפתח מ-OpenAI |

## התקנה

**Windows**, ב-Command Prompt:
```
npm install -g claude-video-vision@1.3.2
claude mcp add -s user claude-video-vision cmd /c claude-video-vision
```

**Mac:**
```
claude mcp add -s user claude-video-vision -- npx -y claude-video-vision@1.3.2
```

**בדיקה:** `claude mcp get claude-video-vision` צריך להחזיר Connected. אחר כך מבקשים מקלוד "תריץ video_setup", והוא בודק מה חסר ומסביר איך להשלים.

## עברית: לנעול את מודל התמלול
כשמודל ה-Whisper מוגדר `auto`, הכלי בוחר לפי הזיכרון של המחשב. במחשב עם פחות מ-8GB זיכרון הוא בוחר מודל קטן שמעוות עברית, והתמלול יוצא קריא אבל עם מילים שגויות. אין שום הודעת שגיאה, ולכן קל לפספס את זה.

הפתרון: בקובץ `~/.claude-video-vision/config.json` (ב-Windows: `%USERPROFILE%\.claude-video-vision\config.json`) לקבוע:
```json
"whisper_model": "large-v3-turbo"
```
`large-v3-turbo` מחזיק עברית טוב ורץ מהר יותר מ-`large-v3`.

## לדעת
- סרטון ארוך שולח הרבה פריימים לקלוד וצורך הרבה מהמכסה. עדיף לבקש קטע ("שניות 0 עד 30") או מספר פריימים קטן.
- גרסה 1.3.2 היא הגרסה שנבדקה. התקנה גלובלית לא מתעדכנת לבד.
- ב-Windows זה לא נבדק עדיין.
