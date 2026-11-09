# widgets native לעריכה ויזואלית + חיבור CMS

**Source**: Workshop landing Elementor conversion (this session, 2026-06-06)
**Category**: playbooks
**Added**: 2026-06-06

## Core Insight
העדף את ה-widgets ה-native של Elementor על HTML מותאם, הם ניתנים לעריכה בעורך הויזואלי **ומחוברים ל-CMS של WordPress**. במיוחד שלושה:
- **Form** (Elementor Pro), מחובר ל-WP; `submit_actions` (email / webhook / CRM / Mailchimp). זה ה"חכם" שהלקוח רצה.
- **Counter**, countUp מובנה, בלי JS מותאם.
- **Accordion**, FAQ ניתן לעריכה.

## How It Works
- מפה את ה-schema מ-export עובד ידוע (תבנית שכבר עובדת) במקום לנחש מפתחות.
- Form fields: `{"field_type":"text|tel|email|select","field_label","placeholder","required","width","custom_id"}`; select מקבל `field_options` (מופרד בשורות). `submit_actions:["email"]` כברירת מחדל, הלקוח מוסיף webhook/CRM בעורך.
- counter: `starting_number`, `ending_number`, `number_suffix`, `title`, `duration`.

## Example
טופס ההרשמה (שם/טלפון/מייל/תחום) נבנה כ-Form widget מחובר ל-WP; ה-counters (3 שעות / 1 סוכן / [##] / [דירוג]) רצים לבד; ה-FAQ accordion. רק עיצוב ה-pseudo (HUD, sun, טרמינל) נשאר CSS/HTML.

## When to Use
תמיד כשהתוכן הוא משהו שהלקוח יערוך (טקסטים, שאלות, שדות טופס, מספרים). שמור HTML רק לאפקטים שאין להם widget.
