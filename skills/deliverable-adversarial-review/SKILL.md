---
name: deliverable-adversarial-review
description: "Use before any deliverable leaves to a client or an external party: PDF, landing page, live site change, zip package, proposal, report, spreadsheet, video. An adversarial evaluator inspects the FINAL RENDERED artifact as the recipient will experience it, never the source that produced it. Triggers: לפני שזה יוצא ללקוח, תבדוק את התוצר, בדיקה סופית, מעריך יריב, לוודא לפני שליחה, יש דליפה במסמך, האם המסמך תקין, לבדוק PDF לפני שליחה, לבדוק דף נחיתה חי, לבדוק זיפ למסירה, final check before sending, verify deliverable, adversarial review."
---

# Deliverable Adversarial Review

## Overview

The generator cannot grade itself. This skill is the separate evaluator: it looks only at the
artifact the recipient actually opens, and its job is to find a reason to block it.

The rule this exists to enforce is already in CLAUDE.md ("סוכן מפריך שני שמנסה לשבור את התוצר
לפני שהוא יוצא"). This turns it into a procedure that runs.

**This is not a code test gate.** A code gate runs build, typecheck, lint, tests,
coverage. It passes green on every failure this skill is built to catch, because none of them
are code bugs.

## Core rule

**Grade the surface the reader sees.**

Never grep the source to conclude something about the output. Every transform between source
and artifact can add, strip, or mangle exactly the thing you are checking for.

## Stance

- The default verdict is **BLOCK**. PASS must be earned with evidence produced in this run.
- Uncertain means BLOCK. "Probably fine" is a block.
- Every finding cites the artifact it was seen in: a page image, a screenshot, an extracted file
  path. A finding without a produced artifact is not a finding.
- Do not spawn agents for this. It runs inline. If a second independent opinion is wanted, the user
  asks for it explicitly.

## Phase 0 - Freshness gate (run first, always)

A stale artifact returns a false green: you review last week's export and pass a document that
no longer matches the source.

```bash
stat -f "%Sm %N" -t "%Y-%m-%d %H:%M" ARTIFACT SOURCE_FILE...
```

If the artifact is older than any source it derives from, **STOP**. Rebuild, then review.
Report the timestamps.

## Phase 1 - Render the artifact

Pick by type. The point of this phase is to produce something a human eye can read.

**PDF**
```bash
pdftoppm -png -r 110 FILE.pdf /tmp/rev/page
ls /tmp/rev/page-*.png
```
Then Read every page image. Not the first page, every page.

**HTML / landing page / live site**
Use Playwright MCP. Navigate to the live URL (not the local file, unless the local file is what
ships). Screenshot at the widths the audience actually uses, and at the width the user works at.
Click the primary CTA and submit any form with test data. Capture console errors.

**ZIP / delivery package**
```bash
mkdir -p /tmp/rev/unz && unzip -o FILE.zip -d /tmp/rev/unz && find /tmp/rev/unz -type f | sort
```
Review the **extracted contents**. The zip is part of the delivery: a clean email with a leaky
zip beside it is a leak.

**DOCX / XLSX**
Convert to PDF and treat as PDF, or open and read computed values. For a spreadsheet, read what
the cells display, not the formulas.

**Video**
Render the actual output file and watch it. A preview that looks right is not the MP4.

## Phase 2 - The rubric

Score each. Any FAIL blocks.

### 1. Internal leakage
Anything that belongs to the workshop, not the client:
internal file paths, agent or tool names, editing tags, "אומת מול X", notes comparing the
document to a previous version, TODO/TBD/FIXME, reviewer commentary, other clients' names.

Scan the rendered text, not the source. For a PDF, extract from the PDF itself:
```bash
pdftotext FILE.pdf - | grep -nE "TODO|TBD|FIXME|אומת|גרסה קודמת|/Users/|\.claude|scratchpad"
```
Then still read the page images, because an image or a header can carry text `pdftotext` misses.

### 2. Rendering integrity
Hebrew digits present and correct, RTL direction right, no mirrored text, no clipped or
overflowing content, fonts actually loaded, no tofu boxes, tables not spilling off the page,
no overlapping elements. On a page, check the real breakpoints, not one.

### 3. Completeness
Every section promised is present and populated. No empty headings, no placeholder text, no
lorem, no unresolved variable like `{{name}}` or `[CLIENT]`.

### 4. Factual accuracy
Numbers, dates, names and prices in the artifact match the source of truth. Financial and legal
figures get checked digit by digit against the system they came from, not against memory.

### 4b. Client comments coverage (added 10.10.2026)
When the deliverable answers a round of client feedback, build a table before the verdict: every
comment from the latest round (WhatsApp, email, voice notes transcribed, the client's notes book)
in its own row, against where the artifact addresses it, or why it does not (a legal or policy
reason, with the source). A comment with no row, or a row with no location, is a FAIL. Quote the
client's words, not a paraphrase.

### 5. Emoji and tone
No emojis in client documents. Marking is carried by words.
Run `python3 ~/.claude/skills/anti-ai-writing/scripts/scan_ai_tells.py` on the text the client
will read, extracted from the rendered artifact. A HIGH finding is a FAIL; MED findings are read
and judged. A clean scan is not proof of tone (see the anti-ai-writing skill).

### 6. Design quality (visual deliverables only)

Skip for a text-only document. Apply to any landing page, site page, deck, ad creative, or
one-pager where the look is part of the product.

**Why this check exists:** the other five checks all pass on a page that is accurate, leak
free, complete, and mediocre. That page still costs a client money. The gate had no criterion
for it until now.

**Source:** the design rules and slop blacklist below are adapted from
[`garrytan/gstack`](https://github.com/garrytan/gstack) (MIT), which in turn credits OpenAI's
"Designing Delightful Frontends" (Mar 2026).

**Classify first, then apply the matching rule set:**

| Type | What it is | Rules |
|---|---|---|
| MARKETING / LANDING | hero-driven, brand-forward, conversion-focused | Landing rules |
| APP UI | workspace-driven, data-dense, task-focused | App rules |
| HYBRID | marketing shell with app-like sections | Landing rules on the marketing part, App rules on the functional part |

**Instant-fail patterns.** Any one of these blocks:

1. Generic SaaS card grid as the first impression
2. A beautiful image with a weak brand
3. A strong headline with no clear action
4. Busy imagery behind text
5. Sections repeating the same mood statement
6. A carousel with no narrative purpose
7. App UI built from stacked cards instead of a layout

**The AI slop blacklist.** These are what make a page read as machine-made. Check every one
against the rendered page:

1. Purple, violet or indigo gradient backgrounds, or blue-to-purple schemes
2. **The three-column feature grid**: icon in a colored circle, bold title, two-line
   description, repeated three times symmetrically. The single most recognizable AI layout
3. Icons in colored circles as section decoration
4. Everything centered
5. The same large border-radius on every element
6. Decorative blobs, floating circles, wavy SVG dividers. An empty-feeling section needs
   better content, not decoration
7. Emoji as design elements
8. Colored left-border on cards
9. Generic hero copy: "Welcome to X", "Unlock the power of", "Your all-in-one solution for"
10. Cookie-cutter section rhythm: hero, three features, testimonials, pricing, CTA, every
    section the same height
11. `system-ui` or `-apple-system` as the primary display font. The "gave up on typography" signal

**Landing page rules:**

- The first viewport reads as one composition, not a dashboard
- Brand first: brand, then headline, then body, then CTA
- No default font stacks (Inter, Roboto, Arial, system)
- No flat single-color backgrounds
- Hero is full-bleed. Budget: brand, one headline, one supporting sentence, one CTA group,
  one image. No cards in the hero
- One job per section
- Two to three intentional motions minimum
- CSS variables for the color system, one accent
- "If deleting 30% of the copy improves it, keep deleting"

**Universal rules, and three of them are legal here, not aesthetic:**

- ⚖️ Body text never below 16px, contrast never below 4.5:1
- ⚖️ Never placeholder-as-only-label. The label stays visible when the field has content
- ⚖️ Touch targets at least 44x44px
- Visited and unvisited links stay visually distinct
- A heading sits closer to the section it introduces than to the one above it
- Cards earn their existence

**The three marked ⚖️ are IS 5568 obligations for an Israeli client site**, which makes them
blockers on legal grounds even if the page looks fine. The `israeli-accessibility-compliance` skill from skills-il covers the details.

**Litmus checks.** Answer each yes or no on the rendered page:

1. Is the brand unmistakable in the first screen?
2. Is there one strong visual anchor?
3. Is the page understandable by scanning headlines alone?
4. Does each section have one job?
5. Are the cards actually necessary?
6. Does motion improve hierarchy, or is it decoration?
7. Would it still feel premium with every decorative shadow removed?

## Phase 3 - False-green traps

These are real incidents. Check each before writing PASS.

| Trap | What happened | Guard |
|---|---|---|
| The transform strips your marker | A markdown-to-PDF converter removed `[[ ]]` and left the filename, so grepping the source for `[[` came back clean while the reader saw a bare filename | Search the rendered output for what the reader sees, not the syntax |
| Source scanned instead of output | An internal block labelled as internal still shipped, because the label was treated as a filter | Filter in code, then scan the produced file |
| Stale artifact | A review passed on an export older than the fix | Phase 0 |
| Data validated, document not | A legal document was checked as a data structure and the rendered page was wrong | Read the rendered page |
| Font eats digits | SFHebrew rendered 0 of 10 digits and silently broke a financial document | Read the page image and count the digits |
| Reported edit never landed | A UI change was reported done and the live field still held the old value | Read the live field |
| The test asserts the machine | A passing test described the harness, not the live world | Verify against the live thing |
| The package beside the email | The email was clean and the leak travelled in the zip packed next to it | Review extracted contents |

## Phase 4 - Verdict

Report in this shape:

```
VERDICT: BLOCK | PASS
ARTIFACT: <path or URL>  (built <timestamp>)
EVIDENCE: <page images / screenshots / extracted paths produced this run>

FAIL   <check> - <what the reader would see> - <where>
PASS   <check> - <what was inspected>
```

On BLOCK, state the smallest fix that clears it. Fix it in the generator, not by hand-patching
the artifact, or the next export reintroduces it.

Never write "בוצע", "תקין", "נקי" or "passing" without the evidence from this run attached.

**On PASS, open it for the user:** `open <file>` for a PDF, HTML page or image, or `open <folder>` when several files go
out together. Name in the reply what was opened.
Skip this when running headless (`claude -p`) or inside a subagent.
