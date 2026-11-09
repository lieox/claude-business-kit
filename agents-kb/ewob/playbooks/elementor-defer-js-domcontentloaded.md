# JS - לדחות ל-DOMContentLoaded + להזריק רקע ל-body

**Source**: Workshop landing Elementor conversion (this session, 2026-06-06)
**Category**: playbooks
**Added**: 2026-06-06

## Core Insight
סקריפט בתוך HTML widget שממוקם בראש העמוד רץ **בזמן הפרסור**, לפני שה-widgets שמתחתיו קיימים ב-DOM, אז `getElementById` על אלמנט מאוחר מחזיר null. עטוף הכל ב-DOMContentLoaded.

## How It Works
```js
(function(){ function run(){ /* ...all logic... */ }
  if(document.readyState!=='loading') run();
  else document.addEventListener('DOMContentLoaded', run);
})();
```
שכבות רקע fixed (grid/glows/scanlines/progress/nav), הזרק ל-`document.body` עם `insertAdjacentHTML('afterbegin', ...)` כדי לברוח מ-stacking contexts של סקשנים, ותן להן `z-index:0` מתחת לסקשנים (`z-index:1`).

## Example
הטרמינל המקליד נשאר ריק כי ה-typewriter רץ לפני ש-`#eTerm` נטען. הדחייה ל-DOMContentLoaded תיקנה, ההקלדה הופיעה. אותו סקריפט גם מזריק את ה-nav והרקע ל-body ומפעיל את ה-IntersectionObserver לחשיפות.

## When to Use
כל סקריפט ב-HTML widget שנוגע באלמנטים אחרים בעמוד (טרמינל, reveals, nav scroll, counters מותאמים).
