---
name: docs-freshness-audit
description: "Use when auditing documentation freshness across the workspace .md and README files under $CLAUDE_WORK_DIR/: broken markdown links, dates that have passed, stale last-updated lines, empty sections, pending TODO/TBD/FIXME. Hebrew triggers: תבדוק את התיעוד, תיעוד לא מעודכן, READMEs מיושנים, תאריכים שעברו, קישורים שבורים, סעיפים ריקים, בדיקת תיעוד שבועית, לבדוק תאריכי יעד שעברו."
context: fork
background: false
---

# Docs Freshness Audit

## Overview

Scan every real `.md` / `README.md` doc under `$CLAUDE_WORK_DIR/` and flag six freshness defects: broken markdown links, dates that have passed, stale `Last updated:` lines, empty sections, pending TODO/TBD/FIXME markers, and past deadlines. This is a READ-ONLY audit: never edit any `.md` file. Output suggested replacement text plus the exact path.

The whole point of this skill is that the raw scan is dominated by false positives (clones, dumps and logs far outnumber the real docs). The value is the exclusion list and the link-resolution rules below. Run the packaged scanner so a fresh subagent produces the same result every time.

## When to Use

- the user asks to check documentation, find stale dates, find broken links, find empty sections, find old `Last updated:` lines, or find pending TODOs under `$CLAUDE_WORK_DIR/`.
- Any request to audit doc freshness or past deadlines in the workspace.

## When NOT to Use

- Editing or fixing docs. This audit only reports; the fix is a separate, explicitly-requested step.
- Auditing a single client's automations or blueprints (that is a different skill).
- Fetching or validating `http`/`https` URLs. Only local file links are checked; network links are never fetched.

## Core rule: exclusions come first

Without the exclusion list the scan is noise. Apply ALL of these before any check runs:

| Exclude | Why | Rough count |
|---|---|---|
| `*/.git/*`, `*/node_modules/*`, `*/__pycache__/*` | Machinery, not docs | large |
| `*/skills/*` | Skill packages (own SKILL.md conventions, not audited as docs) | ~214 |
| `*/.claude/*` | Per-project harness dirs (agents, settings, local skills) | ~194 |
| `daily/` archives | Dated snapshots, expected to be stale | small |

`scan.py` reports `files_scanned`. If it jumps far above the last run, a new folder of non-docs (a cloned repo, a dump) probably entered the scope: exclude it in `scan.py`.

## Core rule: what is NOT a broken link

The link checker produces garbage unless it skips these. Encode all four:

1. **Links inside fenced code blocks** (between ` ``` ` fences) are examples, not real links. Track fence state line-by-line and skip everything inside. (Real cases this fixes: `formulas.md`, a `lexi` slug doc with a link written inside a code block.)
2. **Links inside HTML comments** (`<!-- ... -->`, possibly multi-line) are commented-out and must be skipped.
3. **`[[wikilinks]]`** are Obsidian-style vault links, NOT markdown links. Resolve them against the vault root, not the file's own directory.
4. **`http`/`https`/`mailto:` targets** are network links: skip, never fetch.

For a real markdown link `[text](path)`, resolve `path` relative to the containing file's directory (and also try repo-root for `/absolute` style), then check the target file exists. Only a genuinely missing local target is a broken link.

## Core rule: intentional TODO / empty docs are not bugs

Some docs are deliberately unfinished. Do not flag these as defects (they are the baseline, encoded in `references/known-baseline.md`):

- **Known empty stubs** under `knowledge/technical/` (for example `icount.md`, `monday.md`, `wordpress.md`, and `morning.md`) are long-standing empty stubs, not new regressions. `morning.md` in particular is a meaningless-topic stub.
- Any doc whose own content marks itself as a deliberate placeholder or work-in-progress: report at low priority, not as a hard defect.

Everything a run confirms as intentional belongs in `references/known-baseline.md` so the NEXT run does not re-report it.

## Procedure

1. **Load the baseline.** Read `references/known-baseline.md` for the standing exclusions and intentional-TODO allowlist.
2. **Run the scanner** at `references/scan.py` (self-contained, stdlib only). It walks the scope with the exclusions baked in, applies all six checks with the false-positive guards, and prints JSON to stdout. See "Run the scan" below.
3. **Subtract the baseline.** Drop any finding that matches an intentional-TODO / known-stub entry in `references/known-baseline.md`.
4. **Rank.** Priority order for the top findings list: `past_deadlines` > `broken_links` > `stale_last_updated` > `pending_todos` > `empty_sections`. `outdated_dates` is INFORMATIONAL only (see "Category weighting" below): it is excluded from `issues_count` and `top_findings`, and must not be reported as a list of problems.
5. **Report.** For each finding give `{ file, line, snippet, issue }` and, where a fix is obvious, a suggested replacement string plus the exact path. Never edit the file.
6. **Update the baseline.** If the run confirms a NEW intentional TODO/stub (a false positive that should never re-fire), add it to `references/known-baseline.md` with a one-line reason.

## Run the scan

The scanner is the single source of truth so every subagent runs the checks identically. It takes the root as an argument and prints JSON.

```bash
python3 "$SKILL_DIR/references/scan.py" "$CLAUDE_WORK_DIR"
```

Read the JSON it prints. Do not re-implement the walk inline; if a new exclusion or guard is needed, edit `references/scan.py` so the change is permanent and shared.

Today's date for every "has this passed" comparison is whatever the system reports at run time. The scanner reads the current date itself; do not hardcode a date.

## Output schema (what scan.py prints)

```json
{
  "last_run": "<ISO 8601 UTC>",
  "files_scanned": 0,
  "issues_count": 0,
  "informational_counts": { "outdated_dates": 0 },
  "top_findings": [],
  "categories": {
    "outdated_dates": [],
    "broken_links": [],
    "empty_sections": [],
    "stale_last_updated": [],
    "pending_todos": [],
    "past_deadlines": []
  }
}
```

Each finding entry: `{ "file": "<abs path>", "line": 42, "snippet": "<text>", "issue": "<what is wrong>" }`. `top_findings` is the flat top-10 across categories using the priority order above.

`issues_count` counts DEFECTS only and excludes every category listed in `informational_counts`. `categories.outdated_dates` stays populated for reference, but its total belongs in `informational_counts`, never in the defect count.

## Category weighting

`outdated_dates` is informational, not a defect. A bare past date in prose is almost always a correct historical fact ("Meta Ads MCP active as of 2026-05-07"); genuinely forward-looking dates are already covered by `past_deadlines`. Before this split (2026-07-24) the category contributed 3383 of 4600 findings and drowned the report.

## Check definitions

| Category | What counts | False-positive guard |
|---|---|---|
| `broken_links` | `[text](path)` where `path` is a local file that does not exist | Skip code fences, HTML comments, wikilinks, and `http`/`https`/`mailto` (see rules above) |
| `outdated_dates` | A `YYYY-MM-DD` in the text that is earlier than today | Ignore dates inside code fences. INFORMATIONAL ONLY: excluded from `issues_count` and `top_findings` |
| `stale_last_updated` | A freshness stamp in the first 10 lines whose date is more than 14 days EARLIER than the file's last content change (git commit date; mtime only for untracked files). Matches English `Last updated:`/`Updated:` and the Hebrew markers `עודכן` / `עודכן לאחרונה` / `עדכון אחרון` / `תאריך עדכון` / `רוענן לאחרונה` / `נכון ל`, in both ISO and day-first (`24.07.2026`) formats | Drift, not absolute age: an old stamp on a doc nobody touched is fine. Header window only; table rows and dated log rows (`- 2026-06-18 \| ...`) are skipped, because deeper in the body `עודכן <date>` usually describes an external resource. **Files with 0 or 1 commits are skipped in code** (`git_commit_count()`): the lone date is a bulk first-commit, or an mtime that any copy/move bumps, so the drift is an artifact rather than a stale stamp |
| `empty_sections` | A heading (`## X`) followed only by whitespace, a SAME-OR-SHALLOWER heading, or an italic `TBD`/`empty`/`to be populated` placeholder | A DEEPER heading right after means the section holds subsections and its content lives there, so `#`->`##` and `##`->`###` are never flagged (that bug alone was 587 of 628 hits). `slides-*.md` files and break headings (`### הפסקה`) are skipped in code. Also skip anything on the known-stub allowlist |
| `pending_todos` | Lines containing `TODO`, `TBD`, `FIXME`, `XXX` (case-sensitive) | Skip intentional-TODO docs on the baseline allowlist |
| `past_deadlines` | A date that has passed on a line with deadline words (`by`, `until`, `due`, `ship`, `launch`, `deadline`, `עד`, `תאריך יעד`) | Ignore code fences; needs both a passed date and a deadline word |

## Common Mistakes

| Mistake | Fix |
|---|---|
| Scanning every `.md` file, including clones and dumps | Apply the full exclusion list first |
| Reporting `[[wikilinks]]` as broken links | Wikilinks resolve to the vault root, not the file dir; never report them |
| Flagging a link written inside a ` ``` ` code block | Track fence state and skip fenced content (and HTML comments) |
| Re-reporting known empty stubs each week | Subtract `references/known-baseline.md`; add new confirmed stubs to it |
| Fetching `http`/`https` links | Never fetch network links; only local file targets are checked |
| Editing a doc to "fix" it | READ-ONLY. Output suggested text + path only |
| Re-implementing the walk inline and getting a different count | Run `references/scan.py`; edit it if a rule must change |
| Hardcoding today's date | The scanner reads the system date; compare against that |

## Canonical sources

- Scanner (single source of truth for the walk + checks): `references/scan.py` (in this skill dir)
- Standing exclusions + intentional-TODO allowlist: `references/known-baseline.md` (in this skill dir)
