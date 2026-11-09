# CSS ששורד ייבוא + מלכודות עיצוב (Elementor)

**Source**: a product page deep-fix (2026-06-23)
**Category**: playbooks
**Added**: 2026-06-23

## 1. page_settings.custom_css לא שורד שיבוץ
שיבוץ Saved Template מביא את ה-widgets אבל לא את page_settings. CSS ב-`page_settings.custom_css` פשוט לא יחול אחרי שהלקוח משבץ את התבנית בעמוד, והווידג'טים יוצאים חשופים. הוכחה: שתי תבניות שעלו מושלם  עם `page_settings.custom_css` באורך 0. הפתרון: כל ה-CSS ב-HTML widget יחיד (`<link>`+`<style>`) ב-section עם `_element_id: e-css-host`, כי הוא חלק מה-content ולכן נוסע עם הייבוא.

## 2. למקד ב-node הפנימי, לא ב-wrapper
Elementor עוטף: `.cls` (wrapper) ‹ `.elementor-widget-container` ‹ `.elementor-heading-title` (הטקסט). חוק על ה-wrapper בלבד לא צובע את הטקסט. מיפוי:
- heading: `.cls .elementor-heading-title`
- button: `.cls .elementor-button`
- text-editor: תוכן ה-HTML הפנימי עם class-ים (נתפס ישירות)
- icon-list: `.cls .elementor-icon-list-text` / `.elementor-icon-list-item`
- star-rating: `.cls .elementor-star-rating`
- tabs: `.cls .elementor-tab-title` / `.cls .elementor-tab-content`
- image: `.cls .elementor-widget-container` (border-radius/overflow) + `img`

## 3. מלכודת ברירות-המחדל של ה-Kit
אם חוק מגדיר font-size אבל לא font-family/color, ה-Kit של האתר דורס (פונט Arimo + צבע כותרת תכלת כמו #6EC1E4). כל text node צריך font-family AND color מפורשים. פונט על body לא מגיע לטקסט בתוך widgets. דפוס עמיד:
```
#sec, #sec *{font-family:"Assistant",sans-serif}
.cls-title .elementor-heading-title{font-family:"Rubik"!important;color:#23151c}
```

## 4. קריסת טורים (flex-wrap)
`.elementor-container` הוא `flex-wrap:wrap`; אם תוכן טור מרחיב מעבר ל-basis, הטורים נשברים לערימה. כפה (וסגור ב-media query כדי לשמור stacking במובייל):
```
@media (min-width:881px){
  #sec > .elementor-container{flex-wrap:nowrap;align-items:flex-start}
  #col-a{flex:0 0 46%;max-width:46%;position:relative}
  #col-b{flex:0 0 54%;max-width:54%}
}
```
`position:relative` על הטור = עוגן לאלמנטים absolute (סטיקרים/באדג'ים).

## 5. מרווח כפול
Elementor מוסיף ~20px מתחת לכל widget מעבר למרווחים שלך = מרווח כפול ועמוד מנופח. המשתנה `--widgets-spacing` לא אמין; אפס ישירות וסמוך על המרווחים המפורשים שלך:
```
#sec .elementor-widget:not(:last-child){margin-bottom:0!important}
```
כנ"ל header/footer גבוהים מדי: אפס margin של widgets + padding של columns.
