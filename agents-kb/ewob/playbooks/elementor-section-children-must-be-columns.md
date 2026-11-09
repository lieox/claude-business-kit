# ילדי section חייבים להיות columns

**Source**: Workshop landing Elementor conversion (this session, 2026-06-06)
**Category**: playbooks
**Added**: 2026-06-06

## Core Insight
ב-Elementor (סכימת sections v0.4) **הילדים הישירים של section חייבים להיות columns בלבד**. אסור לקנן section בתוך column או לערבב columns עם section כילדים, זה שובר את הייבוא/רינדור.

## How It Works
- גריד (4 כרטיסים, bento, שורת counters) = **section נפרד ברמה העליונה** עם כמה columns.
- כותרת סקשן + גריד = שני sections נפרדים (header-section + grid-section), לא section אחד שמכיל column-כותרת ו-section-גריד.
- ולידציה: עברו על העץ וודאו שכל `elType=="section"` מכיל רק ילדים `elType=="column"`.

## Example
ניסיון ראשון קינן `SEC([COL(header), SEC([cols...]), COL(line)])`, לא תקין. התיקון: שיטוח ל-`journey_head` (section עם column-כותרת) + `journey_grid` (section עם 4 columns). קו הטיימשליין עבר ל-CSS `::before` על ה-container של הגריד.

## When to Use
בכל פעם שבונים גריד/שורה של כרטיסים. גם פריסת 2×2 = שתי שורות-section נפרדות (Elementor לא עוטף columns לשורה הבאה אוטומטית).
