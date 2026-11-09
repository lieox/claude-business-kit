# אימות רינדור headless לפני ייבוא (Elementor)

**Source**: a product page deep-fix (2026-06-23)
**Category**: playbooks
**Added**: 2026-06-23

## Core Insight
אי אפשר לייבא ל-WP בעצמך, אבל אפשר לאמת את הרינדור מקומית ולכוונן את ה-CSS לפני שהלקוח מייבא שוב. זה שובר את לולאת הפידבק האיטית (ייבוא, צילום, תיקון). measure, don't guess.

## הכלים
- chrome-headless-shell מה-cache של Playwright: `~/Library/Caches/ms-playwright/chromium_headless_shell-*/chrome-headless-shell-mac-arm64/chrome-headless-shell` (Chrome ל-Playwright MCP לא מותקן, ה-binary הזה כן).
- puppeteer-core בלי הורדת דפדפן: `cd /tmp/x && npm init -y && PUPPETEER_SKIP_DOWNLOAD=1 npm i puppeteer-core`, ואז `puppeteer.launch({executablePath:<chrome-headless-shell>})`.

## הסיגנל הכי טוב: הקליטה של העמוד המיובא
בקש מהלקוח "save page" של העמוד אחרי ייבוא. היא נושאת את ה-DOM האמיתי של Elementor + ה-CSS החיצוני (קישורים מוחלטים שנטענים מהאתר ברשת) = רינדור נאמן. אז:
1. הזרק את ה-CSS המועמד לעותק של הקליטה (`<style>` לפני `</body>`).
2. רנדר headless, מדוד `getComputedStyle` (fontFamily, color, bounding boxes, חפיפות), גבהי sections, side-by-side.
3. כוונן את ה-CSS עד שה-computed תואם למוקאפ.
4. הטמע את ה-CSS הסופי ב-css-host של ה-JSON.

## אזהרת קליטה
קליטה עם inline styles בלבד (בלי `<link>` חיצוניים) לא משקפת את המראה החי. צריך את זו עם קישורי CSS חיצוניים מוחלטים.

## בונוס: חילוץ אתרי JS (Canva וכו')
WebFetch נכשל על אתרי Canva/JS. רנדר headless + גלילה בצעדים + `document.body.innerText`. כותרות מונפשות מתפצלות לאות-בשורה; אחד שורות של תו בודד כדי לנקות את הטקסט.

## When to Use
כל המרת HTML ל-Elementor שבה צריך נאמנות ויזואלית גבוהה, ובכל באג רינדור שדורש מדידה (פונט/צבע/פריסה/מרווח) במקום ניחוש.
