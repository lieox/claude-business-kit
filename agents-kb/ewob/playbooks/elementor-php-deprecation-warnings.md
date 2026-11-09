# Elementor: הצפת אזהרות PHP deprecation (php-di) ב-PHP 8.1+

> מקור: GPT "Elementor Deprecated Warning Fix" (2025). שונה מגוצ'ת YaadPay×PHP8.4 ([[wordpress-memory-exhaustion]]).

## הסימפטום
Elementor/Elementor Pro מגיע עם `php-di` ווendored שמשתמש בפרמטרים implicit-nullable, שהוצאו משימוש ב-PHP 8.1+:
```
Deprecated: ElementorProDeps\DI\create(): Implicitly marking parameter $className as nullable is deprecated
```
וזה מדרדר ל-`Cannot modify header information - headers already sent by ...ProxyFactory.php` (כי ה-deprecation מודפס לפני ה-headers).

## התיקון
אי אפשר לערוך קוד vendored (נדרס בעדכון) → **מדכאים**. ב-`wp-config.php`:
```php
error_reporting(E_ALL & ~E_DEPRECATED);
```
ובנוסף, בפרודקשן: `display_errors` off / `WP_DEBUG_DISPLAY` false, כדי שה-"headers already sent" הנגזר ייעלם.

## חתימה מבדילה
`Implicitly marking parameter ... as nullable is deprecated` תחת `ElementorProDeps`/`php-di`/`ProxyFactory` = הבעיה של Elementor עצמו. (לעומת `Creation of dynamic property ... is deprecated` = תוסף צד-שלישי לא-תואם, ראה [[wordpress-memory-exhaustion]].)
