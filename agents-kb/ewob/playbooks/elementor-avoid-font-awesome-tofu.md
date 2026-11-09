# להימנע מ-Font Awesome (אייקוני □ tofu)

**Source**: Workshop landing Elementor conversion (this session, 2026-06-06)
**Category**: playbooks
**Added**: 2026-06-06

## Core Insight
אייקוני Font Awesome (ב-icon-list, accordion toggle, select arrow) מופיעים לעיתים כ-□ ("tofu") בעמודי canvas, ה-FA לא נטען/לא enqueued. אל תסתמך עליהם לאלמנטים חיוניים.

## How It Works
- pills/רשימות: השתמש ב-emoji או `✓` כחלק מהטקסט (text-editor עם markup), לא ב-`selected_icon`.
- accordion: הסתר את אייקון ה-FA והחלף ב-CSS:
```css
.e-faq .elementor-accordion-icon{display:none!important}
.e-faq .elementor-tab-title::after{content:'+';position:absolute;left:20px;color:#00e5ff}
.e-faq .elementor-tab-title.elementor-active::after{content:'−'}
```
- icon-box: שים emoji בתוך `title_text` ו-`selected_icon` ריק, לא תלוי ב-FA.

## Example
ה-trust pills (`✓ בעברית`) וה-logistics (`📅 [התאריך]`) הומרו מ-icon-list ל-text-editor עם emoji; ה-□ נעלמו. ה-+/− של ה-FAQ נבנה ב-CSS ::after.

## When to Use
בכל פעם שאייקון מופיע כריבוע ריק אחרי ייבוא, או מראש, העדף emoji/CSS על FA בעמודי canvas.
