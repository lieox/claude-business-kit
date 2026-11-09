# Elementor: טקסט מעוקל (curved text) דרך SVG textPath

> מקור: GPT "Elementor Text Bending" (2026). ל-Elementor אין אופציית טקסט מעוקל native, ו-Title widget לא יכול לעקל טקסט ב-CSS (`text-path` הוא SVG בלבד, `transform: curve()` לא קיים).

## הפתרון: HTML widget (לא Title widget)
```html
<svg viewBox="0 0 500 200" width="100%">
  <path id="curve" d="M 50 150 Q 250 50 450 150" fill="transparent" />
  <text><textPath href="#curve" startOffset="50%" text-anchor="middle">Your Curved Text Here</textPath></text>
</svg>
<style> text { font-size:42px; font-weight:700; fill:#000; font-family:inherit; } </style>
```

## שליטה
- העיקול נשלט ע"י נקודת הבקרה `Q 250 50`: ערך Y נמוך (50) = עיקול חזק; גבוה (100) = עדין.
- לשמור על טיפוגרפיה גלובלית של Elementor: הסר `font-size`/`font-family` מה-`<style>` ומקד דרך class: `.curved-title text { fill: var(--e-global-color-primary); }`.
- **עברית/RTL:** כיוון הטקסט משמעותי - התאם פר-שפה (הטקסט זורם לאורך ה-path משמאל לימין כברירת מחדל).
