# Meta Conversions API (CAPI) server-side ב-WordPress בלי תוסף

> מקור: GPT "Meta API התקנה ידנית" (2025). התקנת CAPI צד-שרת ישירות מ-functions.php, בלי תוסף, יורה אירועים מ-WooCommerce ומטפסי Elementor Pro.

## הפונקציה (functions.php)
```php
function send_meta_capi_event($event_name, $event_data = []) {
    $access_token = 'YOUR_ACCESS_TOKEN';
    $pixel_id = 'YOUR_PIXEL_ID';
    $url = 'https://graph.facebook.com/v18.0/' . $pixel_id . '/events?access_token=' . $access_token;
    $payload = [ 'data' => [ [
        'event_name' => $event_name,
        'event_time' => time(),
        'event_source_url' => $_SERVER['HTTP_REFERER'] ?? '',
        'action_source' => 'website',
        'user_data' => [
            'client_ip_address' => $_SERVER['REMOTE_ADDR'],
            'client_user_agent' => $_SERVER['HTTP_USER_AGENT'],
        ],
        'custom_data' => $event_data
    ] ] ];
    $options = [ 'http' => [ 'method'=>'POST','header'=>'Content-Type: application/json','content'=>json_encode($payload) ] ];
    file_get_contents($url, false, stream_context_create($options));
}
```

## ההוקים שנושאים את הערך (הדבר החשוב)
```php
// רכישה ב-WooCommerce:
add_action('woocommerce_thankyou', function($order_id){
    $o = wc_get_order($order_id);
    send_meta_capi_event('Purchase', ['value'=>$o->get_total(),'currency'=>$o->get_currency()]);
});
// ליד מטופס Elementor Pro:
add_action('elementor_pro/forms/new_record', function($record){
    if ($record->get_form_settings('form_name')==='Lead Form')
        send_meta_capi_event('Lead', ['value'=>1,'currency'=>'USD']);
});
```
- הפיקסל (browser) נכנס ב-`header.php` מעל `</head>`.
- בדיקה: הוסף `'test_event_code' => 'YOUR_TEST_CODE'` בתוך `$payload` → Events Manager → Test Events.

## ⚠️ Hardening (חובה לפני פרודקשן)
- `file_get_contents` הגולמי **לא מאמת SSL** - עדיף `wp_remote_post()` עם timeout וטיפול בשגיאות.
- **אין `event_id` לדדופ מול הפיקסל בדפדפן** → אירועים כפולים. הוסף `event_id` זהה גם ל-CAPI וגם לפיקסל (dedup של Meta).
- אל תשים את ה-`access_token` בקוד גלוי בגיט - `wp-config.php` / env.
