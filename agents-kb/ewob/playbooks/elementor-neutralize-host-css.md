# נטרול ה-wrappers של Elementor

**Source**: Workshop landing Elementor conversion (this session, 2026-06-06)
**Category**: playbooks
**Added**: 2026-06-06

## Core Insight
עיצוב full-bleed (רקעים על כל הרוחב, nav, גרדיאנטים) "נשבר" כי Elementor עוטף כל אלמנט ב-section/container/column/widget עם padding ו-max-width משלהם. צריך שכבת CSS גלובלית שמנטרלת אותם + מסתירה את ה-header/footer של התבנית.

## How It Works
שים בראש ה-`<style>` הגלובלי:
```css
header.site-header,.site-footer,#masthead,.main-navigation,footer.site-footer{display:none!important}
.elementor-section,.elementor-container,.elementor-column,.elementor-widget-wrap,.elementor-widget,.elementor-element{max-width:100%!important;padding:0!important;margin:0!important}
.elementor-section>.elementor-container{max-width:1080px}  /* רוחב תוכן מבוקר */
body{background:#0a0a1f!important;color:#e8e6f0!important;font-family:'Heebo',sans-serif!important;direction:rtl;overflow-x:hidden}
.elementor-section{position:relative;z-index:1;background:transparent}
```
שכבות רקע fixed שמוזרקות ל-body מקבלות `z-index:0` והסקשנים `z-index:1` מעליהן.

## Example
בלי האיפוס, ה-counter band וה-nag לא נמתחו לרוחב מלא וה-container הבוקסי (~1140px) חתך את הרקע. עם האיפוס, ה-grid bg, ה-glows וה-scanlines מילאו את המסך.

## When to Use
בתחילת כל המרה ל-Elementor, עוד לפני בניית הסקשנים. תמיד canvas template (`elementor_canvas`, `hide_title: yes`).
