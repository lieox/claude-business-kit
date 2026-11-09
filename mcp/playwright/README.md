# Playwright: קלוד שולט בדפדפן

השרת של מיקרוסופט ([microsoft/playwright-mcp](https://github.com/microsoft/playwright-mcp), רישיון Apache-2.0) נותן לקלוד דפדפן אמיתי. הוא יכול לפתוח אתר, ללחוץ, למלא טופס, לצלם מסך ולקרוא את מה שמופיע בדף.

## למה זה טוב לעסק
- לבדוק דף נחיתה כמו לקוח: לפתוח בנייד ובמחשב, ללחוץ על הכפתור, לשלוח טופס ניסיון.
- לצלם מסך של אתר לפני שינוי ואחריו.
- לאסוף מידע מדף שאין לו ממשק (מחירון של ספק, רשימה באתר ממשלתי).
- לעבוד עם `ewob` ועם `deliverable-adversarial-review` כשבודקים אתר חי.

## התקנה

**Windows**, ב-Command Prompt:
```
npm install -g @playwright/mcp@0.0.83
claude mcp add -s user playwright cmd /c playwright-mcp
```
ההתקנה הגלובלית חוסכת את ההורדה בהפעלה הראשונה, שלפעמים לוקחת יותר מ-30 השניות שקלוד מחכה לשרת.

**Mac:**
```
claude mcp add -s user playwright -- npx -y @playwright/mcp@0.0.83 --browser chromium
npx playwright install chromium
```

**בדיקה:** `claude mcp get playwright` צריך להחזיר Connected. אחר כך מבקשים מקלוד "תפתח את האתר שלי ותצלם מסך".

## דפדפן
כברירת מחדל השרת משתמש ב-Google Chrome שמותקן במחשב. אם אין Chrome, ב-Windows עובדים עם Edge, שמגיע עם המערכת:
```
claude mcp remove -s user playwright
claude mcp add -s user playwright -- cmd /c playwright-mcp --browser msedge
```
במק משתמשים ב-Chromium, כמו בפקודה למעלה.

## לדעת
- הדפדפן של השרת נפרד מהדפדפן שלכם, ואין בו את ההתחברויות שלכם. אתר שדורש התחברות ידרוש התחברות גם שם.
- גרסה 0.0.83 היא הגרסה שנבדקה. אפשר לעדכן ל-`@latest`, אבל אחרי עדכון כדאי לבדוק שוב.
- ב-Windows זה לא נבדק עדיין.
