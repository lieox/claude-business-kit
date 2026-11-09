# אבחון קריסת זיכרון ב-WordPress (Allowed memory size exhausted)

> מקור: אתר וורדפרס על uPress, 2026-04. שגיאה: `Fatal error: Allowed memory size of 268435456 bytes exhausted` (256MB). פלייבוק client-agnostic + ממצאים ספציפיים.

## סדר אבחון (מהמהיר לעמוק)
1. **wp-config.php** (לפני `/* That's all, stop editing! */`):
   ```php
   define('WP_MEMORY_LIMIT', '512M');
   define('WP_MAX_MEMORY_LIMIT', '512M');
   ```
2. **רמת שרת** (אם WP מבקש 512 אבל השרת חוסם): `memory_limit = 512M` באחד מ: `php.ini` / `.htaccess` (`php_value memory_limit 512M`) / `.user.ini`. בדיירקטאדמין/cPanel: Select PHP Version / MultiPHP INI Editor.
3. **בידוד תוסף בלי אדמין** (FTP/File Manager): שנה שם `/wp-content/plugins` → `plugins-disabled`. עלה האתר? הבעיה בתוסף. החזר שם, וכבה תוסף-תוסף ע"י שינוי שם תיקיות בודדות.
4. **בידוד תבנית:** שנה שם תיקיית התבנית הפעילה ב-`/wp-content/themes/` → WP עובר לברירת מחדל. עלה? הבעיה בתבנית/`theme.json`.
5. **דיבאג נקי:**
   ```php
   define('WP_DEBUG', true);
   define('WP_DEBUG_LOG', true);
   define('WP_DEBUG_DISPLAY', false);
   ```
   קרא את `/wp-content/debug.log`.

## קריאת דוח שגיאות - איך לזהות את החשוד
- קריסות ב-`class-wp-theme-json.php` / `class-wpdb.php` / `elementor/core/files/css/base.php` / `woocommerce/i18n/states.php` = **עומס סטאק כללי** (Elementor Pro + WooCommerce כבדים), לא קובץ בודד.
- **דגל אדום לתוסף לא-תואם:** `Undefined variable $X` + `Creation of dynamic property ... is deprecated` תחת סוקט `php84`/`php8x` = תוסף שלא תואם לגרסת ה-PHP.

## ממצא ספציפי מאומת: YaadPay × PHP 8.4
תוסף הסליקה **`yaad-sarig-payment-gateway-for-wc`** (יעד שריג/hyp) זורק תחת PHP 8.4: `Undefined variable $order_id`, `Creation of dynamic property WC_Gateway_Yaadpay::$yaad_template/$yaad_currency is deprecated`. **פתרון:** לרדת זמנית ל-PHP 8.2/8.3 עד עדכון התוסף, או לעדכן/להחליף את שער הסליקה.

## הקשר uPress (מסויג)
נראה שחבילות uPress מגבילות `memory_limit` (במקרה זה 256MB) ולא תמיד מאפשרות העלאה מעבר לכך מצד הלקוח - ייתכן שצריך פתיחת טיקט לתמיכת uPress. **לא אומת ב-100% בשיחה** (הייתה השערה). uPress מכירים היטב את הסטאק - טיקט עברי מוכן-להדבקה הוא הדפוס המנצח.

## חשוב
העלאת זיכרון מטפלת בסימפטום. אם אתר "פתאום" קרס - חפש את **הסיבה**: תוסף/תבנית שעודכן, קונפליקט חדש, או דליפת זיכרון. הזיכרון קונה זמן, לא פותר שורש.
