# המרת עיצוב HTML ל-Elementor Pro: הסטנדרט והוורקפלו

**Source**: a landing page (2026-06-06) + a product page deep-fix (2026-06-23)
**Category**: playbooks
**Added**: 2026-06-06 · **Updated**: 2026-06-23

## הסטנדרט (6 כללים שתמיד חלים)
1. **תוכן = widgets native, בלי HTML widget לתוכן.** כל מה שהלקוח עורך (כותרות, טקסט, בולטים, כפתורים, תמונות, מחיר, דירוג, טאבים) = widget native: heading, text-editor, icon-list, button, image, image-carousel, star-rating, tabs, divider. "בלי HTML widget" מתייחס לתוכן בלבד.
2. **CSS = HTML widget אחד גלובלי (css-host), לא page_settings.** כל ה-`<link>` לפונטים + ה-`<style>` יושבים ב-HTML widget יחיד, בתוך section עם `_element_id: e-css-host` בראש העמוד. **לעולם לא ב-page_settings.custom_css** - הוא לא נוסע עם שיבוץ Saved Template והעיצוב נעלם. ראה [[elementor-css-survives-import-and-styling]].
3. **למקד ב-node הפנימי של Elementor.** ה-CSS מעצב את הפלט: `.cls .elementor-heading-title`, `.cls .elementor-button`, `.cls .elementor-icon-list-text`. סלקטור על ה-wrapper בלבד לא צובע את הטקסט הנראה.
4. **כל text node מקבל font-family AND color מפורשים.** אחרת ה-Kit של האתר דורס (Arimo + צבע כותרת דיפולטי). פונט על body לא מגיע לטקסט בתוך widgets.
5. **wrapper תקין לייבוא.** `{version:"0.4", title, type:"page", content, page_settings}`; columns בלי `_inline_size:null` ובלי `isInner`; sections עם isInner; אפס מפתחות null.
6. **לאמת ברינדור לפני שהלקוח מייבא.** ראה [[elementor-verify-render-headless]].

## הוורקפלו (סדר פעולות)
1. בנה/קבל HTML standalone מאושר = המטרה הויזואלית (ראה [[standalone-html-first-then-convert]]).
2. בנה את התבנית: section `e-css-host` (HTML widget עם הסטיילשיט) + sections של תוכן ב-widgets native, כל אחד עם `_css_classes`/`_element_id` שה-CSS תופס.
3. הזרק את ה-CSS לקליטה אמיתית של העמוד המיובא, רנדר headless, מדוד computed styles מול המוקאפ, כוונן עד התאמה.
4. החזר JSON תקין (`python3 -m json.tool`), בלי em/en dash, עם הוראות ייבוא + רשימת placeholders + הערת WooCommerce.

## למה ההיברידי הזה
- הכל ב-HTML widget = לא ניתן לעריכה ("לא פרקטי לערוך באלמנטור").
- הכל native בלי css-host = מאבד אפקטים, ו-page_settings לא שורד ייבוא.
- האיזון: תוכן native + css-host אחד. יחס אופייני ~30 widgets native מול 1 HTML (הסטיילשיט).

## WooCommerce (עמוד מוצר)
מחיר/הוספה-לסל/דירוג דינמיים לא נשמרים אמין ב-Saved Template (צריך קונטקסט מוצר). בנה אותם native סטטיים, והערה ללקוח: לבנות כ-Single Product template (Theme Builder) ולהחליף ב-Product Price / Add To Cart / Product Rating שנקשרים למוצר האמיתי.

## When to Use
כל המרת עיצוב HTML מותאם ל-Elementor שבה הלקוח צריך לערוך טקסטים בעורך אבל גם דורש נאמנות ויזואלית גבוהה.
