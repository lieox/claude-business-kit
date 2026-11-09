# HTML עצמאי קודם, ואז להמיר לאלמנטור

**Source**: Workshop landing Elementor conversion (this session, 2026-06-06)
**Category**: playbooks
**Added**: 2026-06-06

## Core Insight
תמיד בנה קודם **HTML עצמאי אחד** כ"מטרה" הויזואלית, אשר אותו מול מי שהזמין את האתר, ורק אז המר ל-Elementor. ה-HTML הוא מקור-האמת; ההמרה נמדדת מולו. צפה ל-2-3 סבבי כוונון לפי צילומי מסך, אי-אפשר לרנדר Elementor מקומית.

## How It Works
1. בנה standalone HTML (CSS+JS inline, RTL). שכלל איתו את העיצוב עד "אין הערות".
2. המר ל-Elementor JSON (פייתון, על בסיס schema מ-export עובד).
3. מייבאים → שולח **צילום מסך** (לא רק HTML, מ-HTML גולמי אי-אפשר לראות את הרינדור).
4. השווה מול ה-HTML המקורי, תקן את ה-style הגלובלי, חזור. יעד: ≥80% התאמה ויזואלית.

## Example
תהליך ה-workshop-landing: HTML אושר ("התקדמות משמעותית"), הומר ל-native Elementor, ואז שני סבבי תיקון לפי צילומים, טרמינל ריק (timing), אייקוני □ (FA), טופס לבן (class→#id), מרווחים. כל סבב מיקד תקלות אמיתיות מהרינדור.

## When to Use
כל פרויקט HTML→Elementor. אל תמיר עיצוב שעוד לא אושר ב-HTML, ואל תצפה לדיוק מצילום-source לבד, בקש צילום מסך.
