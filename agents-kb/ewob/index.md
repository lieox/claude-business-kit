# Ewob Knowledge Index


בסיס הידע של ewob לבניית אתרים: וורדפרס, אלמנטור, HTML.

## Playbooks - HTML → Elementor Pro
- [הסטנדרט והוורקפלו](./playbooks/html-to-elementor-native-pattern.md) - 6 כללים + סדר פעולות: תוכן native, CSS ב-css-host HTML widget אחד (לא page_settings), wrapper תקין, אימות רינדור
- [CSS ששורד ייבוא + מלכודות עיצוב](./playbooks/elementor-css-survives-import-and-styling.md) - page_settings.custom_css לא שורד שיבוץ; למקד ב-node הפנימי; מלכודת ה-Kit (Arimo+צבע); קריסת flex-wrap; מרווח כפול
- [אימות רינדור headless לפני ייבוא](./playbooks/elementor-verify-render-headless.md) - chrome-headless-shell + puppeteer-core, הזרקת CSS לקליטה של העמוד המיובא, מדידת computed styles מול המוקאפ
- [נטרול ה-wrappers של Elementor](./playbooks/elementor-neutralize-host-css.md) - הסתרת header/footer + איפוס padding/max-width כדי שעיצוב full-bleed יעבוד
- [ילדי section = columns בלבד](./playbooks/elementor-section-children-must-be-columns.md) - לא לקנן section בתוך column; גריד = section נפרד
- [למקד ב-#element_id, לא ב-class](./playbooks/elementor-target-by-element-id.md) - id תמיד נדבק; class לפעמים לא נתפס
- [להימנע מ-Font Awesome (□ tofu)](./playbooks/elementor-avoid-font-awesome-tofu.md) - emoji/✓/CSS ::after במקום selected_icon
- [JS - לדחות ל-DOMContentLoaded](./playbooks/elementor-defer-js-domcontentloaded.md) - סקריפט עליון רץ לפני שה-DOM נטען; הזרקת רקע ל-body
- [widgets native לעריכה + CMS](./playbooks/elementor-native-widgets-cms-editing.md) - Form (מחובר ל-WP), counter (countUp), accordion (FAQ)

## Playbooks - Workflow
- [Clone Any Website With a Claude/Codex Skill, Then Rebrand It](./playbooks/clone-any-website-with-claude-codex-skill.md) - שכפול מלא ופיקסל-מדויק של כל אתר מ-link חי, ואז להחליף תוכן/מותג; לקחת אנימציה/סקשן/3D ולהתאים למותג שלך
- [HTML עצמאי קודם, ואז להמיר](./playbooks/standalone-html-first-then-convert.md) - בנה מטרה ויזואלית, אשר, ואז המר; 2-3 סבבי כוונון לפי צילומים; יעד ≥80%
- [iOS Widgets to Boost App Opens and Retention](./playbooks/ios-widgets-to-boost-app-retention.md) - Ship a home-screen widget plus a lock-screen widget to build a glance-and-open habit and lift app retention against notification noise.
- [מטופס אפיון לקוח → אפיון משודרג](./playbooks/intake-spec-form-to-upgraded-brief.md) - gap-analysis על טופס אפיון + שדרוג "עמוד אחד" למבנה local-SEO (עמוד-על לכל סוג + FAQ Schema); v1→v2 לתקציב
- [Small-Business Website Completeness Checklist (20 essentials + technical/security merge)](./playbooks/small-business-website-completeness-checklist.md) - רשימת 20 פריטי חובה לאתר עסק מקומי (CTA above the fold, sticky mobile CTA, FAQ, case studies, real photos, local business schema, meta, robots.txt, 404, breadcrumbs, alt text, OG images...) + שכבת technical/security ממקור שני (HTTPS, secrets off frontend, cookie consent, form validation, spam protection, page speed, color contrast) + שכבת חיפוש ו-AI (31.10: סורקי AI לא חסומים, llms.txt, Search Console מחובר ביום העלייה) כ-definition-of-done לפני עלייה לאוויר
- [20+ Reasons a Website/App Looks "Vibecoded"](./playbooks/avoid-vibecoded-website-look.md) - checklist of default-AI visual/copy tells (purple-blue gradient, Inter font, 3 icon boxes, shadcn untouched, em dashes, giant unexplained stats, beige+italic-serif...) to run before shipping, plus the `npx impeccable detect` automated scanner and a ready-to-use audit prompt for Claude Code

## Playbooks - Troubleshooting
- [HTML של תבנית בעמודי וורדפרס: wpautop, TinyMCE ושמירה ב-REST](./playbooks/classic-editor-template-html-wpautop-tinymce.md) - `<a>` שעוטף `<div>`: wpautop מייצר `<p>` ריק ועוגנים משוכפלים (לוח שחמט בגריד) ו-2 שורות CSS שמנקות; TinyMCE מרוקן את העוגנים; kses רק בלי `unfiltered_html` (בדיקה דרך `_links`); `save_post` רץ לפני ה-meta; שמירה בלי שינוי מזיזה את `modified`
- [אבחון קריסת זיכרון ב-WordPress](./playbooks/wordpress-memory-exhaustion.md) - סדר אבחון memory-exhausted, בידוד תוסף/תבנית, חתימת YaadPay×PHP8.4, הקשר uPress
- [Elementor php-di deprecation warnings](./playbooks/elementor-php-deprecation-warnings.md) - הצפת "Implicitly marking parameter as nullable" ב-PHP 8.1+ → `error_reporting(E_ALL & ~E_DEPRECATED)`
- [Elementor Form "parse error"](./playbooks/elementor-form-parse-error.md) - משתמש יחיד + שורד incognito → הדבקת bidi/smart-quotes שוברת את ה-JSON של admin-ajax

## Playbooks - Elementor / WooCommerce techniques
- [טקסט מעוקל דרך SVG textPath](./playbooks/elementor-curved-text-svg.md) - curved text ב-HTML widget (Title widget לא יכול); שליטת עיקול ב-nקודת בקרה של ה-path
- [צ'קבוקס הסכמה עם לינק ב-Woo checkout](./playbooks/woocommerce-checkout-consent-checkbox-link.md) - CFE מסיר `<a>` מ-label ומתיר ב-description; פתרון קוד + CSS RTL

## Playbooks - Integrations / Tracking
- [Meta CAPI server-side בלי תוסף](./playbooks/wordpress-meta-capi-no-plugin.md) - functions.php + hooks של woocommerce_thankyou / elementor_pro/forms/new_record; hardening: SSL verify + event_id dedup

## Frameworks
- [Brand Is for the Customer, Not for You](./frameworks/brand-is-for-the-customer-not-you.md) - design decisions should be reverse-engineered from what the target customer needs the brand to feel like, not the owner's personal taste
