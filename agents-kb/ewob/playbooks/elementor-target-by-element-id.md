# למקד ב-#element_id, לא ב-class (לעיצוב קריטי)

**Source**: Workshop landing Elementor conversion (this session, 2026-06-06)
**Category**: playbooks
**Added**: 2026-06-06

## Core Insight
לעיצוב קריטי שחייב "לתפוס", מקד ב-`_element_id` (סלקטור `#id`) ולא רק ב-`_css_classes`. ה-id תמיד נדבק כ-attribute על האלמנט, בעוד שעיצוב מבוסס-class על column/widget לפעמים לא נתפס כצפוי, וה-specificity של `#id` (1,0,0) גובר על default-ים של Elementor.

## How It Works
- שים `_element_id` על האלמנט (column/section), ובחר אותו ב-CSS עם `#id ...`.
- שמור class-ים לעיצוב כללי/חוזר; id-ים לבלוקים ייחודיים וקריטיים (טופס, hero, band-ים).

## Example
כרטיס הטופס עוצב דרך `.e-form-card` (class על ה-column), והשדות נשארו לבנים, בלי כרטיס. המעבר ל-`#signup .elementor-field` ו-`#signup{background;border;box-shadow;padding}` (ה-id של ה-column) תיקן מיד, שדות כהים, בורדר ניאון, פינות HUD.

## When to Use
טפסים, hero, ה-band-ים החשובים, כל מקום שבו עיצוב מבוסס-class לא הופיע אחרי ייבוא.
