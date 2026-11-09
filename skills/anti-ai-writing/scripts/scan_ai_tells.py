#!/usr/bin/env python3
"""Scan a draft for AI writing tells in Hebrew and English.

Usage:
    scan_ai_tells.py <file>
    scan_ai_tells.py -            # read stdin

Reports candidates, not verdicts. Every hit needs human judgement.
Exit code 0 always: this is a report, not a gate.
"""

import re
import sys
import unicodedata
from statistics import mean, pstdev

HEB = re.compile(r"[֐-׿]")

SEVERITY_ORDER = {"HIGH": 0, "MED": 1, "LOW": 2}

# ---------------------------------------------------------------- word lists

HE_PHRASES_HIGH = [
    "בעולם של היום", "בעולם המודרני", "בימינו אנו", "בעידן הדיגיטלי",
    "בעידן הבינה המלאכותית", "בעולם התחרותי", "אין ספק ש", "חשוב לציין",
    "יש לציין כי", "כפי שכולנו יודעים", "לפני שנצלול", "לסיכום", "לסיום",
    "בשורה התחתונה", "בסופו של דבר", "אז מה למדנו", "התחילו עוד היום",
    "הזמן לפעול הוא עכשיו", "לצלול לעומק", "צלילה לעומק", "פורץ דרך",
    "מהפכני", "לחולל מהפכה", "את כללי המשחק", "משנה משחק",
    "לרתום את הכוח", "לשחרר את הפוטנציאל", "למצות את הפוטנציאל",
    "לשלב הבא", "אבן דרך", "הנוף העסקי", "הנוף השיווקי", "עולם ומלואו",
    "כלי רב עוצמה", "חוויה בלתי נשכחת", "ברמה הגבוהה ביותר",
    "תפורים בהתאמה אישית", "פתרונות מותאמים אישית", "לפתוח דלתות",
    "בואו נצלול", "זה עושה שכל", "בסוף היום", "לקחת את זה לשלב הבא",
]

HE_PHRASES_MED = [
    "כידוע", "רבים שואלים", "מה שבטוח", "פתרון מקיף", "ערך אמיתי",
    "שדרוג משמעותי", "נקודת מפנה", "המסע שלך", "לספק ערך", "מקרה שימוש",
    "מקצועיות ואמינות",
]

# Hebrew inflects: "אמין ובטוח" also appears as "אמינה ובטוחה" / "אמינים ובטוחים".
# Match the stems with an optional gender/number suffix.
HE_DOUBLET_STEMS = [
    ("יעיל", "אפקטיבי"), ("פשוט", "נוח"), ("חכם", "מתקדם"),
    ("איכותי", "מקצועי"), ("ברור", "מדויק"), ("נגיש", "ידידותי"),
    ("אמין", "בטוח"), ("מקיף", "מעמיק"), ("מהיר", "זמין"),
]
# A stem ending in a final letter loses it when a suffix is added:
# אמין -> אמינה. Build the exact forms instead of gluing an optional suffix on.
FINAL_TO_REGULAR = {"ך": "כ", "ם": "מ", "ן": "נ", "ף": "פ", "ץ": "צ"}
SUFFIXES = ["ה", "ים", "ות", "ת"]


def inflect(stem):
    """Bare stem plus its gender/number forms."""
    base = stem
    if stem[-1] in FINAL_TO_REGULAR:
        base = stem[:-1] + FINAL_TO_REGULAR[stem[-1]]
    return [stem] + [base + suf for suf in SUFFIXES]


def _doublet(first, second):
    a = "|".join(inflect(first))
    b = "|".join(inflect(second))
    vav = "\u05d5"
    return re.compile("(?:" + a + ")" + r"\s+" + vav + "(?:" + b + ")")


HE_DOUBLETS = [
    (first + " \u05d5" + second, _doublet(first, second))
    for first, second in HE_DOUBLET_STEMS
]

HE_HEADINGS = ["למה זה חשוב", "נקודות מפתח", "מחשבות לסיום", "הצעדים הבאים", "היתרונות"]

HE_CONNECTORS = ["בנוסף", "יתרה מזאת", "יתרה מכך", "לפיכך", "כמו כן", "עם זאת",
                 "מאידך", "אי לכך", "זאת ועוד"]

# v2 (10.10.2026): Hebrew versions of antislop-copywriting (miqdadbadjuber/anti-slop, MIT)
# plus two kinds of client-rejected text the v1 scanner passed as clean.
HE_CHATBOT_CLOSERS = [
    "אשמח לעזור", "מקווה שזה עוזר", "מקווה שזה ברור", "מקווה שעזרתי", "אם יש שאלות",
    "לכל שאלה", "בכל שאלה", "אני כאן בשבילך", "אני כאן לכל", "אל תהססו", "אל תהסס",
    "אל תהססי", "נשמח לעמוד לשירותך", "עומדים לרשותך", "תרגישו חופשי", "תרגיש חופשי",
]
HE_FAKE_CANDID = ["האמת היא ש", "בכנות,", "אהיה כנה", "אני חייב להודות", "בואו נהיה כנים",
                  "בוא נהיה כנים"]
HE_SIGNPOSTS = [
    "הנה העניין", "הנה הדבר", "בוא נפרק", "בואו נפרק", "בואו נדבר על", "בוא נדבר על",
    "חשוב להבין ש", "מה שחשוב לדעת", "הנה מה שצריך לדעת", "וכאן זה נהיה מעניין",
    "וזה החלק המעניין", "שימו לב:",
]
HE_WEASEL = ["מחקרים מראים", "מחקרים מוכיחים", "מחקרים מצביעים", "מומחים אומרים",
             "מומחים ממליצים", "מומחים מסכימים", "רבים טוענים", "מוכח מדעית", "ידוע ש"]
HE_INFLATION = ["חוויה ייחודית", "חוויה מושלמת", "הפתרון המושלם", "ברמה אחרת", "סטנדרט חדש",
                "חוויה של פעם בחיים", "בצורה הטובה ביותר", "ללא תחרות", "אין שני לו"]
HE_POSITIVE_CLOSE = ["העתיד נראה מבטיח", "השמיים הם הגבול", "הדרך להצלחה", "ביחד נצליח",
                     "וזו רק ההתחלה", "המסע רק מתחיל"]
# A message that points at its own parts reads like a spec. Repeat the word instead.
HE_INTERNAL_REFS = ["מאותה סיבה", "כאמור", "כנ\"ל", "ראה לעיל", "כפי שציינתי", "כפי שכתבתי",
                    "כפי שצוין", "בהמשך לסעיף", "כמפורט לעיל", "כמפורט להלן"]
HE_HEDGES = ["ייתכן ש", "יכול להיות ש", "במידה מסוימת", "באופן כללי", "במובן מסוים"]
# Verbal nouns in construct ("הזנת הנתונים") instead of a person doing a verb ("אני מזין את הנתונים").
HE_NOMINALIZATIONS = ["הזנת", "הגדרת", "הטמעת", "הפעלת", "העברת", "הוספת", "הסרת", "השלמת",
                      "התאמת", "ביצוע", "בדיקת", "קביעת", "שליחת", "כתיבת", "בניית", "יישום"]
HE_SECOND_PERSON = re.compile(
    r"(?<!\w)(לך|לכם|לכן|שלך|שלכם|שלכן|אותך|אתכם|אצלך|בשבילך|ממך|ממכם|איתך|איתכם|אתה|אתם|אתן|"
    r"שלחי|שלח|כתבי|בואי|תגידי|תשאלי|תעדכני|תעדכן|כתבת|שלחת|ביקשת)(?!\w)")
GREETING = re.compile(r"^\s*(היי|הי|שלום|אהלן|בוקר טוב|ערב טוב|צהריים טובים)\b", re.M)

EN_WORDS_HIGH = [
    "delve", "tapestry", "realm", "unlock", "harness", "pivotal", "elucidate",
    "groundbreaking", "revolutionize", "game-changer", "game changer",
    "cutting-edge", "ever-evolving", "testament", "landscape", "embark",
    "enlightening", "esteemed", "shed light", "abyss", "disruptive",
    "utilize", "utilizing", "dive deep", "illuminate", "unveil", "intricate",
    "skyrocket", "skyrocketing", "in a world where", "remains to be seen",
    "glimpse into", "navigating", "in conclusion", "in summary", "in closing",
    "the key takeaway", "not alone", "here's the thing", "let that sink in",
    "here's where it gets interesting",
]

EN_WORDS_MED = [
    "furthermore", "moreover", "hence", "remarkable", "exciting", "powerful",
    "boost", "opened up", "inquiries", "stark", "craft", "crafting", "imagine",
    "discover", "seamless", "leverage", "robust", "holistic", "empower",
]

EN_CHATBOT = ["hope this helps", "let me know if you have any questions",
              "feel free to reach out", "happy to help", "don't hesitate to", "to be honest",
              "let's be real", "let's break it down", "here's what you need to know"]

EN_WORDS_LOW = ["just", "very", "really", "literally", "actually", "certainly",
                "probably", "basically", "maybe"]

EN_HEADINGS = ["key takeaways", "why it matters", "benefits", "final thoughts",
               "conclusion", "takeaways"]

# Wikipedia:Signs_of_AI_writing (WikiProject AI Cleanup). Added from item #061.
# Inflated significance. The dominant tell in AI-written business and place copy.
EN_PROMO = [
    "boasts a", "boasts an", "nestled in", "nestled within", "nestled among",
    "rich cultural heritage", "vibrant town", "vibrant city", "vibrant community",
    "marking a pivotal moment", "represents a significant shift",
    "represented a significant shift", "part of a broader movement",
    "solidify its role", "solidifying its role", "breathtaking region",
    "stands as a testament", "rich tapestry", "storied history",
]

# Weasel attribution. A credibility problem before it is a style problem.
EN_VAGUE_ATTRIB = [
    "industry reports", "observers have cited", "observers note", "experts argue",
    "experts say", "experts agree", "some critics argue", "critics argue",
    "studies show", "studies suggest", "research suggests", "research shows",
    "several sources", "it is widely believed", "it is often said",
    "many believe", "is of interest to researchers",
]

# Formulaic close. The "despite these challenges" family.
EN_FORMULAIC_CLOSE = [
    "despite these challenges", "despite its challenges", "faces challenges",
    "challenges and legacy", "future outlook", "looking ahead", "only time will tell",
    "continues to evolve", "remains to be seen",
]

# Era vocabulary. Wikipedia tracks these by model generation; mid-2024 onward.
EN_ERA_WORDS = [
    "align with", "aligns with", "enhance", "enhances", "enhancing", "emphasizing",
    "fostering", "highlighting", "showcasing", "underscore", "underscores",
    "garner", "garnered", "crucial", "enduring", "seamlessly", "notably",
]

# Placeholder and machine-voice leakage. The highest-stakes group for a client file.
EN_LEAKAGE = [
    "as of my last update", "as of my knowledge cutoff", "my training data",
    "as an ai language model", "as an ai model", "i cannot browse",
    "lorem ipsum", "[insert", "[your ", "[client", "[company name",
    "todo:", "tbd", "xxx placeholder", "placeholder text",
]

# Re-check of the Wikipedia page, 31.10.2026 (revid 1382925076).
# Copula avoidance: "serves as" for "is". "features"/"offers" are left out on purpose,
# they are ordinary words in ad copy.
EN_COPULA = ["serves as", "serving as", "stands as", "functions as", "operates as",
             "acts as a", "acts as an"]
# Mid-2026 corrective framings and vague connection.
EN_CORRECTIVE = ["should be treated as", "should not be confused with",
                 "does not establish", "do not establish"]
EN_VAGUE_CONNECT = ["associated with", "in connection with", "connected to"]
# Hebrew parallel of the copula tell: "מהווה" for "הוא", "משמש כ"/"מתהדר ב" for "יש".
HE_COPULA = ["מהווה", "מהווים", "מהוות", "משמש כ", "משמשת כ", "משמשים כ", "משמשות כ",
             "מתהדר ב", "מתהדרת ב", "מתהדרים ב"]
HE_CORRECTIVE = ["יש להתייחס לזה כ", "יש להתייחס לכך כ", "לא מאפשר לקבוע",
                 "אין לבלבל", "לא לבלבל עם"]

# ---------------------------------------------------------------- patterns

PATTERNS = [
    ("HIGH", "תבנית 'לא רק X אלא גם Y'", re.compile(r"לא רק .{1,60}?אלא (גם|)")),
    ("HIGH", "תבנית 'זה לא X, זה Y'", re.compile(r"זה לא .{1,50}?,\s*(זה|אלא)")),
    ("HIGH", "תבנית 'X הוא לא מותרות'", re.compile(r"הו[אי] לא מותרות")),
    ("HIGH", "'not just X but Y'", re.compile(r"\bnot just\b.{1,60}?\bbut\b", re.I)),
    ("HIGH", "\"it's not X. it's Y\"", re.compile(r"\bit'?s not\b.{1,50}?[.,]\s*\bit'?s\b", re.I)),
    ("MED", "שאלה רטורית ואז תשובה", re.compile(r"\?\s*(פשוט מאוד|התשובה|ובכן|אז ככה)")),
    ("MED", "rhetorical question as transition", re.compile(r"\?\s*(The answer|Simple\.|Well,)", re.I)),
    ("HIGH", "negative parallelism 'not X, but Y'", re.compile(r"\bnot (a|an|the)?\s?\w[\w\s]{0,40}?,?\s+but (a|an|the|in|rather)\b", re.I)),
    ("HIGH", "'not only X, but also Y'", re.compile(r"\bnot only\b.{1,60}?\bbut (also|)\b", re.I)),
    ("MED", "'Despite ... , X continues/faces'", re.compile(r"\bDespite\b.{1,80}?\b(continues|faces|remains)\b", re.I)),
    ("HIGH", "הפניה פנימית '(סעיף N)', כמו במפרט", re.compile(r"\(סעיף \d+\)")),
    ("MED", "זנב שלילה 'X, לא Y'", re.compile(r"^[^,\n]{2,40}, לא [^,.\n]{2,30}[.!]?\s*$")),
    ("MED", "אנטיתזה סימטרית 'X רך, X קשה'", re.compile(r"(?<!\w)(\w{3,}) \w+, \1 \w+")),
    ("MED", "תבנית 'יש X ויש Y'", re.compile(r"(?<!\w)יש \w+(?: \w+)? ויש ")),
    ("LOW", "טווח מזויף 'מ-X ועד Y'", re.compile(r"(?<!\w)מ-?\w+ ועד ה?\w+")),
    ("MED", "משפטים קצוצים לדרמה ('פשוט. מהיר. עובד.')", re.compile(r"(?:(?<!\w)\w+(?: \w+)?\. ){2,}\w+(?: \w+)?\.")),
    ("LOW", "ציטוט ארוך באנגלית בתוך טקסט עברי", re.compile(r"\"[A-Za-z][^\"]{40,}\"")),
    ("MED", "בולט עם כותרת מודגשת '**כותרת:**'", re.compile(r"^\s*([-*•]|\d+[.)])\s+\*\*[^*\n]{1,40}:?\*\*:?")),
    # 31.10.2026, Wikipedia re-check. "Y rather than X" is the 2026 form of negative parallelism.
    ("MED", "'Y rather than X' (שלילה הפוכה, נפוצה במודלים של 2026)", re.compile(r"\brather than\b", re.I)),
    ("MED", "זנב 'Y ולא X' (שלילה הפוכה)", re.compile(r"(?<!\w)ולא (?!רק\b)[^\s,.!?]+(?: [^\s,.!?]+){0,3}[.!]?\s*$")),
    ("LOW", "'במקום X' בפתיחת משפט, מסגור ניגוד", re.compile(r"(?:^|[.!?]\s+)\s*במקום ")),
    ("MED", "אימוג'י בתחילת כותרת או שורה ברשימה", re.compile(
        r"^\s*(?:#{1,6}\s*|[-*•]\s+|\d+[.)]\s+)?[\U0001F300-\U0001FAFF☀-➿]")),
    ("LOW", "Title Case Heading", re.compile(r"^#{1,6}\s+(?:[A-Z][a-z]+\s+){2,}[A-Z][a-z]+\s*$")),
]

FORMAT_CHECKS = [
    ("HIGH", "em dash / en dash (אסור לפי CLAUDE.md)", re.compile(r"[—–]")),
    ("HIGH", "סימן bidi בלתי נראה (אסור לפי CLAUDE.md)", re.compile(r"[‎‏‪-‮⁦-⁩]")),
    ("MED", "נקודה-פסיק", re.compile(r";")),
    ("HIGH", "utm_source= בקישור (סימן להעתקה משיתוף, לא ממקור)", re.compile(r"utm_source=")),
    ("LOW", "מרכאות מסולסלות “ ” ‘ ’", re.compile(r"[“”‘’]")),
]

# ---------------------------------------------------------------- helpers


def detect_lang(text):
    heb = len(HEB.findall(text))
    lat = len(re.findall(r"[A-Za-z]", text))
    if heb == 0 and lat == 0:
        return "unknown"
    if heb > lat * 2:
        return "he"
    if lat > heb * 2:
        return "en"
    return "mixed"


def find_phrases(lines, phrases, severity, label, word_boundary=False):
    hits = []
    for phrase in phrases:
        # re.I on BOTH branches. Without it a phrase at the start of a sentence
        # ("Nestled in...", "As of my last update...", "[Client Name]") was silently
        # missed, which hid exactly the highest-severity leakage hits. Hebrew is
        # caseless so this changes nothing for the HE lists.
        pat = (re.compile(r"\b" + re.escape(phrase) + r"\b", re.I)
               if word_boundary else re.compile(re.escape(phrase), re.I))
        for i, line in enumerate(lines, 1):
            if pat.search(line):
                hits.append((severity, i, f"{label}: ⁨{phrase}⁩".replace("⁨", "'").replace("⁩", "'")))
    return hits


def sentences(text):
    parts = re.split(r"(?<=[.!?׃])\s+|\n{2,}", text)
    return [p.strip() for p in parts if len(p.strip()) > 1]


def paragraphs(text):
    return [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]


def bullets(lines):
    return [ln.strip() for ln in lines if re.match(r"^\s*([-*•]|\d+[.)])\s+", ln)]


# ---------------------------------------------------------------- checks


def structural_checks(text, lines):
    out = []

    sents = sentences(text)
    lengths = [len(s.split()) for s in sents if len(s.split()) >= 3]
    if len(lengths) >= 6:
        sd, mu = pstdev(lengths), mean(lengths)
        cv = sd / mu if mu else 0
        note = f"אורך משפט: ממוצע {mu:.1f} מילים, סטיית תקן {sd:.1f} (CV={cv:.2f})"
        if cv < 0.35:
            out.append(("HIGH", 0, f"אחידות אורך משפטים, כמעט אין גיוון. {note}"))
        elif cv < 0.45:
            out.append(("MED", 0, f"גיוון נמוך באורך המשפט. {note}"))

    paras = paragraphs(text)
    plens = [len(p.split()) for p in paras]
    if len(plens) >= 4:
        mu = mean(plens)
        if mu and pstdev(plens) / mu < 0.30:
            out.append(("MED", 0,
                        f"כל הפסקאות באותו אורך בערך ({len(paras)} פסקאות, ממוצע {mu:.0f} מילים)"))

    # paragraph openers repeating. Skip one-line greetings/sign-offs and markdown markers
    # ("היי", "שלום", "---", "###"), which every multi-message draft repeats by design.
    openers = [p.split()[0] for p in paras
               if len(p.split()) >= 5 and re.search(r"[A-Za-z֐-׿]", p.split()[0])]
    for w in set(openers):
        n = openers.count(w)
        if n >= 3 and len(openers) >= 4:
            out.append(("MED", 0, f"{n} פסקאות פותחות באותה מילה: '{w}'"))

    bl = bullets(lines)
    if len(bl) >= 4:
        blens = [len(b.split()) for b in bl]
        mu = mean(blens)
        if mu and pstdev(blens) / mu < 0.25:
            out.append(("MED", 0, f"רשימה סימטרית מדי, {len(bl)} בולטים באורך כמעט זהה"))
        bolded = sum(1 for b in bl if re.match(r"^\s*([-*•]|\d+[.)])\s+\*\*", b))
        if bolded == len(bl):
            out.append(("MED", 0, f"כל {len(bl)} הבולטים באותו מבנה (כותרת מודגשת + הסבר)"))

    return out


def client_text_checks(text, lines, lang):
    """Structure and tone of a message or copy a client reads. v1 passed both rejected
    drafts as clean because it only knew words; these are what actually gave them away."""
    out = []
    words = len(text.split()) or 1

    numbered = [ln for ln in lines if re.match(r"^\s*\d+[.)]\s", ln)]
    if GREETING.search(text) and len(numbered) >= 3:
        out.append(("MED", 0, f"מספור של מפרט בתוך הודעה ({len(numbered)} סעיפים ממוספרים). "
                              "מספור רק לשאלות שהלקוח צריך לענות עליהן"))

    # Tables, quotes and code are not prose a client reads as sentences.
    prose = [s for s in sentences(text)
             if "|" not in s and "`" not in s and not s.lstrip().startswith(">")]
    long_sents = [s for s in prose if len(s.split()) > 35]
    for s in long_sents[:5]:
        out.append(("MED", 0, f"משפט ארוך ({len(s.split())} מילים): '{s[:50]}...'"))

    dense = [s for s in prose
             if len(s.split()) >= 25 and re.search(r"\S:\s+\S", s) and not re.match(r"^\s*\**[^:]{1,25}:", s)]
    for s in dense[:3]:
        out.append(("MED", 0, f"משפט דחוס עם נקודתיים: '{s[:50]}...'"))

    bold = re.findall(r"\*\*[^*\n]+\*\*", text)
    if len(bold) >= 5 and len(bold) * 100 / words > 3:
        out.append(("MED", 0, f"עודף הדגשות: {len(bold)} ב-{words} מילים"))

    if lang in ("he", "mixed"):
        neg_same = re.findall(r"(?<!\w)לא (אותו|אותה|אותם)(?!\w)", text)
        if len(neg_same) >= 2:
            out.append(("MED", 0, f"ניגוד חוזר 'לא אותו X' ({len(neg_same)} פעמים)"))

        noms = [m.group(0) for n in HE_NOMINALIZATIONS
                for m in re.finditer(r"(?<!\w)" + n + r" ה\w+", text)]
        if len(noms) >= 3:
            out.append(("MED", 0, f"שמות עצם כבדים במקום פועל ({len(noms)}): " + ", ".join(noms[:4])))

        hedges = [h for h in HE_HEDGES if h in text]
        if len(hedges) >= 3:
            out.append(("LOW", 0, "גידור יתר: " + ", ".join(hedges)))

        if words >= 40 and lang == "he" and not HE_SECOND_PERSON.search(text):
            out.append(("MED", 0, "אין פנייה ישירה לקורא (אף 'לך', 'שלך', 'אתה'). "
                                  "טקסט ללקוח שמדבר על 'נשים' או 'לקוחות' בגוף שלישי נשמע קליני"))

    return out


def scan(text):
    lines = text.split("\n")
    lang = detect_lang(text)
    hits = []

    if lang in ("he", "mixed", "unknown"):
        hits += find_phrases(lines, HE_PHRASES_HIGH, "HIGH", "ביטוי AI")
        hits += find_phrases(lines, HE_PHRASES_MED, "MED", "ביטוי AI")
        hits += find_phrases(lines, HE_HEADINGS, "MED", "כותרת גנרית")
        for label, pat in HE_DOUBLETS:
            for i, line in enumerate(lines, 1):
                if pat.search(line):
                    hits.append(("MED", i, f"זוג מיותר: '{label}'"))
        connector_hits = find_phrases(lines, HE_CONNECTORS, "LOW", "מילת קישור")
        if len(connector_hits) >= 4:
            hits += connector_hits
        hits += find_phrases(lines, HE_CHATBOT_CLOSERS, "HIGH", "סוגר של צ'אטבוט")
        hits += find_phrases(lines, HE_FAKE_CANDID, "MED", "פתיח 'כנות' מזויף")
        hits += find_phrases(lines, HE_SIGNPOSTS, "MED", "הכרזה במקום תוכן")
        hits += find_phrases(lines, HE_WEASEL, "HIGH", "ייחוס עמום, בלי מקור")
        hits += find_phrases(lines, HE_INFLATION, "MED", "ניפוח חשיבות")
        hits += find_phrases(lines, HE_POSITIVE_CLOSE, "MED", "סוגר חיובי גנרי")
        hits += find_phrases(lines, HE_INTERNAL_REFS, "HIGH", "הפניה פנימית, כמו במפרט")
        hits += find_phrases(lines, HE_COPULA, "MED", "'מהווה' / 'משמש כ' במקום 'הוא' / 'יש'")
        hits += find_phrases(lines, HE_CORRECTIVE, "MED", "מסגור מתקן")

    if lang in ("en", "mixed", "unknown"):
        hits += find_phrases(lines, EN_WORDS_HIGH, "HIGH", "AI word", word_boundary=True)
        hits += find_phrases(lines, EN_WORDS_MED, "MED", "AI word", word_boundary=True)
        hits += find_phrases(lines, EN_HEADINGS, "MED", "generic heading", word_boundary=True)
        hits += find_phrases(lines, EN_PROMO, "HIGH", "inflated significance")
        hits += find_phrases(lines, EN_VAGUE_ATTRIB, "HIGH", "vague attribution")
        hits += find_phrases(lines, EN_LEAKAGE, "HIGH", "placeholder / machine voice")
        hits += find_phrases(lines, EN_CHATBOT, "HIGH", "chatbot closer / signpost")
        hits += find_phrases(lines, EN_FORMULAIC_CLOSE, "MED", "formulaic close")
        hits += find_phrases(lines, EN_ERA_WORDS, "MED", "era vocabulary", word_boundary=True)
        hits += find_phrases(lines, EN_COPULA, "MED", "copula avoidance ('serves as' for 'is')", word_boundary=True)
        hits += find_phrases(lines, EN_CORRECTIVE, "MED", "corrective framing", word_boundary=True)
        hits += find_phrases(lines, EN_VAGUE_CONNECT, "LOW", "vague connection", word_boundary=True)
        low = find_phrases(lines, EN_WORDS_LOW, "LOW", "filler word", word_boundary=True)
        if len(low) >= 5:
            hits += low

    for sev, label, pat in PATTERNS + FORMAT_CHECKS:
        for i, line in enumerate(lines, 1):
            for _ in pat.finditer(line):
                hits.append((sev, i, label))

    hits += structural_checks(text, lines)
    hits += client_text_checks(text, lines, lang)
    hits.sort(key=lambda h: (SEVERITY_ORDER[h[0]], h[1]))
    return lang, hits


def main():
    if len(sys.argv) != 2:
        print(__doc__, file=sys.stderr)
        return 2

    src = sys.argv[1]
    if src == "-":
        text = sys.stdin.read()
        name = "<stdin>"
    else:
        try:
            with open(src, encoding="utf-8") as f:
                text = f.read()
        except OSError as e:
            print(f"cannot read {src}: {e}", file=sys.stderr)
            return 2
        name = src

    text = unicodedata.normalize("NFC", text)
    lang, hits = scan(text)

    words = len(text.split())
    print(f"קובץ: {name}")
    print(f"שפה: {lang} | {words} מילים | {len(sentences(text))} משפטים | "
          f"{len(paragraphs(text))} פסקאות")
    print("-" * 68)

    if not hits:
        print("אין ממצאים.")
        return 0

    counts = {}
    for sev, _, _ in hits:
        counts[sev] = counts.get(sev, 0) + 1

    current = None
    for sev, line, msg in hits:
        if sev != current:
            print(f"\n[{sev}]")
            current = sev
        loc = f"שורה {line}" if line else "מבנה"
        print(f"  {loc:>10}  {msg}")

    print("\n" + "-" * 68)
    print("סה\"כ: " + " | ".join(f"{k} {counts[k]}" for k in ("HIGH", "MED", "LOW") if k in counts))
    print("אלה מועמדים, לא באגים. תשפוט כל אחד בהקשר שלו.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
