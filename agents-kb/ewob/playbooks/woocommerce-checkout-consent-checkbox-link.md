# WooCommerce checkout: צ'קבוקס הסכמה עם לינק קליקבילי

> מקור: GPT "Add clickable checkbox link" (2025). רלוונטי לדרישת הסכמת-פרטיות בחנויות IL.

## הבעיה
Checkout Field Editor for WooCommerce **מנקה `<a>` מה-Label** של הצ'קבוקס, אבל **מתיר HTML ב-Description**.

## פתרון בלי קוד (CFE)
צור צ'קבוקס (key `privacy_consent`, Required), Label רגיל בלי לינק, והכנס את הלינק ב-**Description**:
```html
<a href="https://.../privacy-policy/" target="_blank" rel="noopener">מדיניות הפרטיות</a> ואני מסכימה לכל תנאיה
```
```css
#privacy_consent_field .woocommerce-input-wrapper { display:flex; align-items:center; gap:.4rem; flex-wrap:wrap; direction:rtl; }
#privacy_consent_field .description { margin:0; display:inline; }
```

## פתרון בקוד (Label כן מתיר HTML)
```php
add_action('woocommerce_review_order_before_submit', function(){
  woocommerce_form_field('privacy_consent', [
    'type'=>'checkbox','required'=>true,
    'label'=>sprintf('אני מסכימה ל<a href="%s" target="_blank">מדיניות הפרטיות</a>', esc_url($url)),
  ], WC()->checkout->get_value('privacy_consent'));
});
add_action('woocommerce_checkout_process', function(){
  if (empty($_POST['privacy_consent'])) wc_add_notice('יש לאשר את מדיניות הפרטיות','error');
});
add_action('woocommerce_checkout_update_order_meta', function($order_id){
  if (!empty($_POST['privacy_consent'])) update_post_meta($order_id,'privacy_consent','yes');
});
```
> Caveat: לחיצה על הלינק ב-description פותחת את המדיניות אבל לא מסמנת את התיבה; toggle על כל המשפט דורש JS.
