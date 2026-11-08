# SendPulse MCP

שרת MCP שנותן לקלוד גישה לבוט הווטסאפ ב-SendPulse: שיחות, אנשי קשר, תגיות, פלואים, טמפלייטים ושליחת הודעות.

## התקנה
```powershell
cd mcp\sendpulse
npm install
npm run build
```

## מפתחות
ב-SendPulse: Settings ← API ← מעתיקים ID ו-Secret.

## חיבור לקלוד
```powershell
claude mcp add sendpulse --scope user --env SENDPULSE_ACCOUNTS='{"main":{"id":"ID","secret":"SECRET"}}' -- node C:/path/to/mcp/sendpulse/dist/index.js
```
בדיקה: פותחים `claude`, מריצים `/mcp`, ו-sendpulse צריך להופיע מחובר. אחר כך: "תראה לי את הבוטים שלי ב-SendPulse".

## כללים
- שליחת הודעה וקמפיין עוברות אישור של אדם. בבוטים של הצוות הן חסומות (`disallowed_tools` ב-bots.json).
- ווטסאפ מחוץ לחלון 24 השעות דורש טמפלייט מאושר.
- דיוור שיווקי רק למי שנתן הסכמה (חוק הספאם).
