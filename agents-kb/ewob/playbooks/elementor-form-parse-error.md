# Elementor Form: אבחון "parse error" בשליחה

> מקור: GPT "Elementor Parse Error Fix" (2026).

## מה זה אומר
"parse error" = הקריאה של הטופס ל-`admin-ajax.php` ציפתה ל-JSON נקי אבל קיבלה משהו שבור: אזהרת PHP שהודפסה לפני ה-JSON, דף חסימה של firewall/WAF, או תשובת webhook/SMTP פגומה.
**מהלך ראשון:** DevTools → Network → שלח את הטופס → בדוק את התשובה של `admin-ajax.php`.

## כלל ההכרעה (הכי חשוב)
אם התקלה קורית ל-**משתמש יחיד** ו**שורדת incognito** ו**נמשכת אחרי ניקוי cache בשני הצדדים** → זה כמעט אף פעם לא Elementor עצמו.
החשוד החזק: **התוכן שהמשתמש מדביק בשדות** שובר את ה-JSON: מרכאות חכמות `" "`, אימוג'ים, סימני bidi נסתרים (RTL/LTR), טקסט שהועתק מ-WhatsApp/Word.
**בדיקה:** בקש מהמשתמש **להקליד** (לא להדביק) `name: test / email: שלו / message: hello`. אם זה נשלח - האשם הוא הקלט המודבק שלו.

## חשודים משניים
- AV/VPN/WAF מקומי (ESET/Avast/Cloudflare/ModSecurity) שמגיב לבקשה ספציפית.
- Extensions ששורדים incognito (מתרגמים, מנהלי סיסמאות).

> קשר: אותם סימני bidi נסתרים (U+200E/200F) ששוברים record-ID ב-Make שוברים כאן את ה-JSON של הטופס.
