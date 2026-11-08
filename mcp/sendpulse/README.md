# SendPulse MCP

משתמשים בשרת הציבורי [lieox/sendpulse-whatsapp-mcp](https://github.com/lieox/sendpulse-whatsapp-mcp): 26 כלים לבוט ווטסאפ ב-SendPulse, עם מצב קריאה בלבד. נבדק ב-Windows ב-CI.

## מפתחות
ב-SendPulse: Settings > API > Client credentials. מעתיקים ID ו-Secret. המפתחות פותחים את כל החשבון, לא להדביק בצ'אט או בצילום מסך.

## התקנה, ב-Command Prompt (לא PowerShell)
```
npm install -g github:lieox/sendpulse-whatsapp-mcp
claude mcp add -e SENDPULSE_CLIENT_ID=your-id -e SENDPULSE_CLIENT_SECRET=your-secret -s user sendpulse cmd /c sendpulse-whatsapp-mcp
```
- `-s user` חייב לבוא אחרי כל ה-`-e` ולפני השם.
- להתחלה בטוחה מוסיפים `-e SENDPULSE_READ_ONLY=1`: קורא הכל, לא שולח כלום.
- בדיקה: `claude mcp get sendpulse` צריך להחזיר Connected.

## לבוטים של הצוות
ב-`telegram-bridge/mcp.example.json` הבוטים מקבלים עותק במצב קריאה בלבד.

## כללים
- ווטסאפ מחוץ לחלון 24 השעות דורש טמפלייט מאושר.
- דיוור שיווקי רק למי שנתן הסכמה (חוק הספאם).
