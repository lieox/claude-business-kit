#!/usr/bin/env python3
"""Docs freshness audit scanner for $CLAUDE_WORK_DIR/ (READ-ONLY).

Single source of truth for the walk + the six checks + the false-positive
guards, so any subagent produces the same result. Prints JSON to stdout.

Usage:
    python3 scan.py [ROOT]        # ROOT defaults to $CLAUDE_WORK_DIR
"""
import json
import os
import re
import subprocess
import sys
import urllib.parse
from datetime import datetime, timezone, date

# --- exclusions (path substrings; keep in sync with known-baseline.md) ---
EXCLUDE_DIR_PARTS = (
    "/.git/", "/node_modules/", "/__pycache__/", "/.venv/", "/venv/",
    # Skill packages and per-project harness dirs follow their own conventions, not docs.
    "/skills/", "/.claude/",
    # Snapshots are stale the moment they are taken, which is the point of them.
    "/.backups/", "/daily/",
    # Add folders of non-docs here (cloned third-party repos, dumps), and list them in
    # references/known-baseline.md with the reason.
)

# Whole files that are logs rather than documentation. claudememory.md is an append-only
# git commit log: every row carries a past timestamp, so it alone produced ~1300 bogus
# past_deadline / outdated_date hits (29% of all findings) before being excluded.
EXCLUDE_FILE_NAMES = frozenset(("claudememory.md",))

# Path-scoped log exclusions. Same family as claudememory.md: append-only dated ledgers
# where every row legitimately carries a past date. Scoped by full path, not by bare
# filename, so a tickets.md written as real documentation elsewhere is still audited.
#
# reminders.md is DELIBERATELY NOT here, resolving a conflict between two records:
# T-2026-08-25-013 asked for all four to be excluded, while known-baseline.md item 11
# warned that reminders.md's UNCHECKED past-due lines are real signal and must stay in
# scope. The keyword and latest-date fixes above settled it with data: the four files
# fell from 375 past_deadline hits to 61 (fronts 21, tickets 19, reminders 16,
# delegations 5), so keeping reminders.md audited now costs 16 lines instead of 111.
# The baseline's check is preserved and the flood is gone. (2026-08-26)
# Path-scoped log exclusions: append-only dated ledgers where every row legitimately carries a past
# date. Scoped by path suffix, so a file with the same name elsewhere is still audited.
EXCLUDE_PATH_SUFFIXES = ()

# Collected for reference but kept out of issues_count and top_findings: a bare past date
# in prose is almost always a correct historical fact ("MCP active as of 2026-05-07"),
# not a defect. Forward-looking dates are already covered by past_deadlines.
INFORMATIONAL_CATEGORIES = ("outdated_dates",)

# --- category-scoped guards (see known-baseline.md) -------------------------
# Each of these suppresses ONE OR TWO checks for a file, never the whole file:
# dates and links are still audited everywhere.

# Docs that describe the audit itself quote TODO/TBD as examples, so the
# pending-marker check reports the auditor for auditing. knowledge/audits/ holds past
# audit reports, and skills-catalog.md carries this skill's description verbatim.
SELF_REFERENTIAL_TODO_PARTS = ("/knowledge/audits/",)
SELF_REFERENTIAL_TODO_NAMES = frozenset(("skills-catalog.md",))

# Template scaffolding: unfilled sections and placeholder markers ARE the
# deliverable. Suppresses pending_todos + empty_sections only.
TEMPLATE_PATH_RE = re.compile(r"/templates?/")
TEMPLATE_NAME_RE = re.compile(r"^template[-_. ]|^template\.md$", re.IGNORECASE)

# known-baseline.md entry 2: four knowledge/technical topic files created from the
# section template and never filled. Long-standing and known, not a regression.
KNOWN_EMPTY_STUBS = frozenset((
    "knowledge/technical/icount.md",
    "knowledge/technical/monday.md",
    "knowledge/technical/morning.md",
    "knowledge/technical/wordpress.md",
))

# known-baseline.md entry 1: a client marked Inactive/Past/Closed has no live
# work, so an unfilled audience doc or an empty card section is the correct state.
# Read from the doc's OWN status field, so an Active client is still audited.
CLIENTS_DIR_PART = "/knowledge/business/clients/"
STATUS_LINE_RE = re.compile(r"^status\s*:\s*(.+)$", re.IGNORECASE)
INACTIVE_STATUS_WORDS = ("inactive", "past", "closed", "archived",
                         "\u05dc\u05d0 \u05e4\u05e2\u05d9\u05dc", "\u05e0\u05e1\u05d2\u05e8", "\u05d4\u05e1\u05ea\u05d9\u05d9\u05dd")
STATUS_HEADER_LINES = 20

# A line that asserts the ABSENCE of a marker ("No TBD/TODO.", "אין TBD, אין TODO")
# is a plan's own placeholder-scan checklist, not a pending item. The negation has
# to sit directly in front of the token, so "no owner yet, TODO assign" still fires.
NEGATED_MARKER_RE = re.compile(
    r"(?:\bno\b|\bnot\b|\bwithout\b|\bzero\b|\u05d0\u05d9\u05df|\u05dc\u05dc\u05d0|\u05d0\u05e4\u05e1)"
    r"\s*[\"\'\u201c\u201d\u00ab]?\s*(?:(?:TODO|TBD|FIXME|XXX)[\"\'\u201d]?\s*[/,\u00b7]?\s*)*$",
    re.IGNORECASE)

# "05X-XXX-XXXX" is a phone-format mask, not the XXX marker.
MASK_CHARS = frozenset("Xx0123456789()+-")

# A title wrapped over two headings ("# Title" then "# (subtitle)") leaves the
# first one bodyless. The parenthesis is the tell: it continues the line above.
CONTINUATION_HEADING_RE = re.compile(r"^\s*[(\uff08]")

DATE_RE = re.compile(r"\b(\d{4})-(\d{2})-(\d{2})\b")
# Israeli / European day-first format used across the user's Hebrew docs (24.07.2026, 24/7/26)
DATE_IL_RE = re.compile(r"\b(\d{1,2})[./](\d{1,2})[./](\d{2,4})\b")
# Year-less Israeli stamp: "עודכן 14.08". Only used when the same line carries a full
# date to borrow the year from (see _year_hint), never to guess from today.
# Guards, each of which was a real false positive in testing:
#   day 01-31 and month 01-12 only     -> "פרק 0.2" and "גרסה 2.15" do not match
#   (?![./]\d)                          -> does not match the "24.07" inside "24.07.2026"
#   (?<![./\d])                         -> does not match the "07.2026" tail of the same
DATE_IL_SHORT_RE = re.compile(
    r"(?<![./\d])(0?[1-9]|[12]\d|3[01])[./](0?[1-9]|1[0-2])(?![./]?\d)"
)
MD_LINK_RE = re.compile(r"(?<!\!)\[[^\]]*\]\(([^)]+)\)")
# Most of the user's docs stamp freshness in Hebrew, so English-only matching found nothing.
LAST_UPDATED_RE = re.compile(
    r"(last updated|updated:|עודכן לאחרונה|עודכן|עדכון אחרון|תאריך עדכון|רוענן לאחרונה|נכון ל)",
    re.IGNORECASE)
TODO_RE = re.compile(r"\b(TODO|TBD|FIXME|XXX)\b")  # case-sensitive tokens below
# Word-boundary matched, NOT substring. Substring matching made "עד" fire inside
# "עדכון" (update) and "מועד" (appointment), and "by" fire inside "bytes", so every
# Hebrew heading of the form "## עדכון <past date>" was reported as a passed deadline.
# That was the single largest source of the 729 past_deadline hits on 2026-08-25.
# "by" additionally requires a digit right after it, so "maintained by the team" is not a
# deadline while "by 2026-09-01" is.
DEADLINE_RE = re.compile(
    r"\bby(?=\s+\d)"
    r"|\b(?:until|due|deadlines?"
    r"|ships?|shipped|shipping"
    r"|launch(?:es|ed|ing)?"
    r"|דדליין|תאריך\s+יעד)\b"
    # "עד" is Hebrew for both "until" (a deadline) and "up to" (a quantity), so like
    # "by" it only counts when it actually introduces a date: "עד 2026-02-01" is a
    # deadline, "עד ₪1,000 למסר" and "עד שבודקים את הסט" are not.
    r"|\bעד(?=\s+\d)",
    re.IGNORECASE)
STALE_DAYS = 60
# A freshness stamp is stale when the file's content changed this many days AFTER the
# stamp. Absolute age alone is useless: a doc stamped 6 months ago that nobody touched
# is fine, while one stamped 3 weeks ago and edited last week is not.
STALE_DRIFT_DAYS = 14
# Only header stamps describe the doc itself. Deeper in the body, "עודכן <date>" almost
# always describes an external resource (a GitHub repo, a Google Doc) and is a false positive.
STAMP_HEADER_LINES = 10
# "- 2026-06-18 | ..." is a dated log entry, not a stamp describing the document.
LOG_ROW_RE = re.compile(r"^\s*[-*]\s*\d{4}-\d{2}-\d{2}\s*[|,]")
# Slide decks (slides-*.md) use headings as slide markers, so bodyless headings are the
# format, not a defect. Empty-section checking is skipped for them entirely.
SLIDE_FILE_RE = re.compile(r"^slides?[-_.]", re.IGNORECASE)
# A heading that is only a break/interval marker in an agenda is contentless on purpose.
BREAK_HEADING_RE = re.compile(r"^\s*(הפסקה|הפסקת\s|break\b|intermission\b)", re.IGNORECASE)


def is_excluded(path):
    p = path if path.endswith("/") else path
    for part in EXCLUDE_DIR_PARTS:
        if part in p:
            return True
    norm = p.replace(os.sep, "/")
    for suffix in EXCLUDE_PATH_SUFFIXES:
        if norm.endswith(suffix):
            return True
    return os.path.basename(p) in EXCLUDE_FILE_NAMES


def iter_md_files(root):
    for dirpath, dirnames, filenames in os.walk(root):
        dp = dirpath + "/"
        if is_excluded(dp):
            dirnames[:] = []
            continue
        for name in filenames:
            if name.endswith(".md"):
                full = os.path.join(dirpath, name)
                if not is_excluded(full):
                    yield full


def mask_line_text(line, in_fence, in_comment):
    """Blank out inline-code spans and HTML-comment content on one line so the
    link/date regexes never see example or commented-out links. Returns
    (masked_text, in_comment_after). Fenced lines are fully blanked by caller."""
    if in_fence:
        return "", in_comment
    out = []
    i = 0
    n = len(line)
    in_inline = False
    while i < n:
        if in_comment:
            end = line.find("-->", i)
            if end == -1:
                out.append(" " * (n - i))
                return "".join(out), True
            out.append(" " * (end + 3 - i))
            i = end + 3
            in_comment = False
            continue
        # start of an HTML comment on this line?
        if line.startswith("<!--", i):
            in_comment = True
            i += 4
            out.append("    ")
            continue
        ch = line[i]
        if ch == "`":
            in_inline = not in_inline
            out.append(" ")
            i += 1
            continue
        out.append(" " if in_inline else ch)
        i += 1
    return "".join(out), in_comment


def build_masked_lines(lines):
    """Return a parallel list of lines with fenced blocks, HTML comments, and
    inline-code spans blanked out. Link/date checks run on THESE lines; empty
    -section detection uses the mask only to skip fenced headings."""
    masked_text = []
    fenced_flag = []
    in_fence = False
    in_comment = False
    for line in lines:
        stripped = line.lstrip()
        if not in_comment and stripped.startswith("```"):
            in_fence = not in_fence
            masked_text.append("")
            fenced_flag.append(True)
            continue
        mt, in_comment = mask_line_text(line, in_fence, in_comment)
        masked_text.append(mt)
        fenced_flag.append(in_fence)
    return masked_text, fenced_flag


def doc_status(lines):
    """The status a doc declares about its own subject: frontmatter `status: Past`
    or a card's `**Status:** Inactive`. None when the doc declares nothing."""
    for raw in lines[:STATUS_HEADER_LINES]:
        s = raw.replace("*", "").strip()
        m = STATUS_LINE_RE.match(s)
        if m:
            return m.group(1).strip().strip("'\"").lower()
    return None


def suppress_stub_checks(path, root, lines):
    """True when pending_todos + empty_sections are meaningless for this file:
    a template, a confirmed long-standing stub, or a doc about an inactive client.
    Date and link checks are unaffected."""
    name = os.path.basename(path)
    if TEMPLATE_PATH_RE.search(path) or TEMPLATE_NAME_RE.match(name):
        return True
    rel = os.path.relpath(path, root)
    if rel in KNOWN_EMPTY_STUBS:
        return True
    if CLIENTS_DIR_PART in path:
        status = doc_status(lines)
        if status and any(w in status for w in INACTIVE_STATUS_WORDS):
            return True
    return False


def is_self_referential_todo_doc(path):
    """Docs that document the audit itself quote TODO/TBD as examples."""
    if os.path.basename(path) in SELF_REFERENTIAL_TODO_NAMES:
        return True
    return any(part in path for part in SELF_REFERENTIAL_TODO_PARTS)


def is_format_mask(line, start, end):
    """True when the matched token sits inside a masked format like 05X-XXX-XXXX."""
    i, j = start, end
    while i > 0 and line[i - 1] in MASK_CHARS:
        i -= 1
    while j < len(line) and line[j] in MASK_CHARS:
        j += 1
    token = line[i:j]
    return token != line[start:end] and any(c.isdigit() for c in token)


def check_file(path, root, today):
    findings = {k: [] for k in
                ("outdated_dates", "broken_links", "empty_sections",
                 "stale_last_updated", "pending_todos", "past_deadlines")}
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            lines = fh.read().splitlines()
    except OSError:
        return findings
    masked_lines, fenced = build_masked_lines(lines)
    base_dir = os.path.dirname(path)
    skip_stub_checks = suppress_stub_checks(path, root, lines)
    skip_todos = skip_stub_checks or is_self_referential_todo_doc(path)

    for idx, raw in enumerate(lines):
        lineno = idx + 1
        line = masked_lines[idx]   # link/date checks run on masked text
        if not line.strip():
            continue

        # --- broken_links ---
        for m in MD_LINK_RE.finditer(line):
            target = m.group(1).strip()
            # drop title part: [text](path "title")
            target = target.split(" ", 1)[0].strip()
            if not target:
                continue
            if target.startswith(("http://", "https://", "mailto:", "#",
                                   "sandbox:", "tel:", "data:")):
                continue  # network / anchor / pseudo-scheme: skip
            if target.startswith("[["):
                continue  # wikilink text captured oddly: skip
            clean = target.split("#", 1)[0]
            if not clean:
                continue
            clean = urllib.parse.unquote(clean)  # decode %20, %D7.. before lookup
            if clean.startswith("~"):
                cand = os.path.expanduser(clean)
            elif clean.startswith("/"):
                cand = os.path.join(root, clean.lstrip("/"))
            else:
                cand = os.path.normpath(os.path.join(base_dir, clean))
            root_cand = os.path.normpath(os.path.join(root, clean.lstrip("/")))
            if not (os.path.exists(cand) or os.path.exists(root_cand)):
                findings["broken_links"].append(
                    {"file": path, "line": lineno, "snippet": raw.strip()[:200],
                     "issue": "local link target missing: " + clean})

        # --- dates (outdated + past deadlines) ---
        # A line carrying a deadline word is judged ONCE, on its LATEST date. Judging
        # every date independently reported a passed deadline for any older date that
        # merely shared the line: "**Token expires:** 2026-09-06 (verified 2026-07-24)"
        # was filed as a passed deadline on the strength of the verification date, while
        # the deadline itself had not arrived (INSTALLS.md:281, found 2026-08-25).
        line_dates = []
        for dm in DATE_RE.finditer(line):
            y, mo, d = int(dm.group(1)), int(dm.group(2)), int(dm.group(3))
            try:
                line_dates.append(date(y, mo, d))
            except ValueError:
                continue

        is_deadline_line = bool(DEADLINE_RE.search(line))
        if is_deadline_line and line_dates:
            latest = max(line_dates)
            if latest < today:
                findings["past_deadlines"].append(
                    {"file": path, "line": lineno,
                     "snippet": raw.strip()[:200],
                     "issue": "deadline date passed: " + latest.isoformat()})
        else:
            for dt in line_dates:
                if dt < today:
                    findings["outdated_dates"].append(
                        {"file": path, "line": lineno,
                         "snippet": raw.strip()[:200],
                         "issue": "date has passed: " + dt.isoformat()})

        # --- stale last updated ---
        # Header stamps only, and never a table row: deeper in the body a date next to
        # "עודכן" describes some external resource, not this document.
        if (lineno <= STAMP_HEADER_LINES
                and not raw.lstrip().startswith("|")
                and not LOG_ROW_RE.match(raw)
                and LAST_UPDATED_RE.search(line)):
            dt = parse_stamp_date_after_keyword(line)
            # 0 or 1 commit means there is no committed history to compare against: the
            # single date is when the file was first committed (a bulk sync) or, for an
            # untracked file, an mtime any copy/move bumps. Either way the "drift" is an
            # artifact, not a stale stamp.
            trustworthy = dt is not None and git_commit_count(path) > 1
            changed = content_changed_date(path) if trustworthy else None
            if dt and changed and (changed - dt).days > STALE_DRIFT_DAYS:
                findings["stale_last_updated"].append(
                    {"file": path, "line": lineno,
                     "snippet": raw.strip()[:200],
                     "issue": "freshness stamp %s not bumped; content changed %s (%dd drift)"
                              % (dt.isoformat(), changed.isoformat(), (changed - dt).days)})

        # --- pending todos (case-sensitive tokens) ---
        if not skip_todos:
            for tm in TODO_RE.finditer(line):
                if NEGATED_MARKER_RE.search(line[:tm.start()]):
                    continue  # "No TBD/TODO." asserts the absence of one
                if tm.group(1) == "XXX" and is_format_mask(line, tm.start(), tm.end()):
                    continue  # 05X-XXX-XXXX is a phone mask
                findings["pending_todos"].append(
                    {"file": path, "line": lineno, "snippet": raw.strip()[:200],
                     "issue": "pending marker: " + tm.group(1)})

    # --- empty sections ---
    if not skip_stub_checks:
        findings["empty_sections"].extend(find_empty_sections(path, lines, fenced))
    return findings


def find_empty_sections(path, lines, fenced):
    out = []
    # A slide deck's headings are slide markers, not prose sections: the format is
    # "## label" immediately followed by "# Slide Title", so a bodyless heading is
    # the format working as intended, not a gap.
    if SLIDE_FILE_RE.match(os.path.basename(path)):
        return out
    heading_re = re.compile(r"^(#{1,6})\s+(.*)$")
    placeholder_re = re.compile(r"^\*?_?\s*(tbd|empty|to be populated)\s*_?\*?$",
                                re.IGNORECASE)
    n = len(lines)
    for i, line in enumerate(lines):
        if fenced[i]:
            continue
        hm = heading_re.match(line.strip())
        if not hm:
            continue
        # "### הפסקה (10 דק')" in an agenda is a timetable slot, deliberately contentless.
        if BREAK_HEADING_RE.search(hm.group(2)):
            continue
        level = len(hm.group(1))
        j = i + 1
        body_seen = False
        while j < n:
            nxt = lines[j].strip()
            nm = heading_re.match(nxt)
            if nm:
                # A deeper heading means this section holds subsections, so its
                # content lives there. Only a same-or-shallower heading right
                # after means the section is genuinely empty.
                if len(nm.group(1)) > level:
                    body_seen = True
                elif (len(nm.group(1)) == level
                      and CONTINUATION_HEADING_RE.match(nm.group(2))):
                    # "# Title" + "# (subtitle)" is one title wrapped over two
                    # lines, not a section with nothing in it.
                    body_seen = True
                break
            if nxt and not placeholder_re.match(nxt):
                body_seen = True
                break
            j += 1
        if not body_seen:
            out.append({"file": path, "line": i + 1,
                        "snippet": line.strip()[:200],
                        "issue": "heading with no content"})
    return out


_GIT_LOG_CACHE = {}


def git_commits(path):
    """[(sha, date), ...] newest first for one file. Empty when git is
    unavailable or the file is untracked."""
    if path not in _GIT_LOG_CACHE:
        rows = []
        try:
            out = subprocess.run(
                ["git", "log", "--format=%H %cs", "--", path],
                cwd=os.path.dirname(path) or ".",
                capture_output=True, text=True, timeout=20)
            for ln in out.stdout.splitlines():
                parts = ln.split()
                if len(parts) != 2:
                    continue
                m = DATE_RE.search(parts[1])
                if m:
                    rows.append((parts[0],
                                 date(int(m.group(1)), int(m.group(2)),
                                      int(m.group(3)))))
        except Exception:
            rows = []
        _GIT_LOG_CACHE[path] = rows
    return _GIT_LOG_CACHE[path]


def git_commit_count(path):
    """How many commits touched this file. 0 for untracked files or when git is
    unavailable, which callers treat as "no reliable history"."""
    return len(git_commits(path))


_WORDS_RE = re.compile(r"\w+", re.UNICODE)
_LINK_TARGET_RE = re.compile(r"\]\([^)]*\)")


def diff_line_signature(text):
    """One diff line reduced to its words, with markdown link targets collapsed.
    Punctuation, whitespace and invisible bidi marks all vanish, so a typography
    sweep (em dash -> comma) and a link-path repair both come out unchanged."""
    return " ".join(_WORDS_RE.findall(_LINK_TARGET_RE.sub("](@)", text)))


def commit_is_substantive(sha, path):
    """False when this commit changed nothing but punctuation, whitespace, link
    targets or the freshness stamp itself in this file. Those are the three ways
    a bulk maintenance pass fakes a 'content changed' date: the 2026-08-09 dash
    and bidi purge alone touched 767 files and produced 31 bogus stale stamps."""
    try:
        out = subprocess.run(
            ["git", "show", "--format=", "--no-color", "--unified=0", sha,
             "--", path],
            cwd=os.path.dirname(path) or ".",
            capture_output=True, text=True, timeout=20)
    except Exception:
        return True  # cannot tell: assume real, never hide a finding on an error
    removed, added = [], []
    for ln in out.stdout.splitlines():
        if ln.startswith("+++") or ln.startswith("---") or len(ln) < 1:
            continue
        if ln[0] not in "+-":
            continue
        body = ln[1:]
        # 🔴 Narrowed 2026-08-19 after an adversarial check proved the previous form
        # created FALSE NEGATIVES. It read `if LAST_UPDATED_RE.search(body): continue`,
        # i.e. it discarded any diff line merely CONTAINING a freshness keyword. Since
        # LAST_UPDATED_RE matches bare "עודכן" and "נכון ל", a real content change that
        # happened to sit on such a line became invisible, and if it was the commit's
        # only change the commit was misclassified cosmetic and the content date rolled
        # back. Real case: a paragraph announcing a sub-project shipped
        # was dropped because it contained "נכון ל".
        # Correct behaviour: do not drop the line, strip the DATE out of it. A pure
        # stamp bump then reduces to the same signature on both sides and cancels out,
        # while a real edit on a stamp line still differs and survives.
        if LAST_UPDATED_RE.search(body):
            body = DATE_RE.sub("", DATE_IL_RE.sub("", body))
        sig = diff_line_signature(body)
        if not sig:
            continue
        (added if ln[0] == "+" else removed).append(sig)
    return sorted(removed) != sorted(added)


def content_changed_date(path):
    """Date the file's content last SUBSTANTIVELY changed. Walks git history newest
    first and steps over cosmetic commits (typography sweeps, link repairs, a stamp
    bump), because those are what make an untouched doc look stale. mtime is only a
    fallback for untracked files, where any copy or move bumps it."""
    commits = git_commits(path)
    for sha, cdate in commits:
        if commit_is_substantive(sha, path):
            return cdate
    if commits:
        return commits[-1][1]  # every commit cosmetic: content dates from the first
    try:
        return date.fromtimestamp(os.path.getmtime(path))
    except Exception:
        return None


def parse_stamp_date_after_keyword(line):
    """Read the date that the freshness keyword introduces, not the first date on
    the line. "נוצר 27.07.2026 ... עודכן 14.08" is stamped 14.08, and reading the
    creation date instead made an up-to-date doc look two weeks stale. When nothing
    parseable follows the keyword the line is prose, not a stamp: return None.

    Returns the LATEST date any keyword introduces, not the first one found.
    A line carrying "עודכן 29.07 ... עודכן 14.08" is stamped 14.08.

    2026-08-28: a year-less stamp ("עודכן 14.08") is parsed by borrowing the year
    from a full date elsewhere on the same line. Before this, DATE_IL_RE needed
    three components, both keyword lookups returned None, and the whole-line
    fallback handed back the CREATION date , reporting an accurate file as 18 days
    stale. That is the same family as the `past_deadlines` bug fixed on 26.08:
    judging a line by the first date on it instead of the right one."""
    matches = list(LAST_UPDATED_RE.finditer(line))
    if not matches:
        return None
    year_hint = _year_hint(line)
    found = []
    for m in matches:
        d = parse_stamp_date(line[m.end():], year_hint=year_hint)
        if d:
            found.append(d)
    if found:
        return max(found)
    return parse_stamp_date(line, year_hint=year_hint)


def _year_hint(line):
    """The year to assume for a year-less stamp: the latest full year written on
    the same line. None when the line carries no full date at all, in which case a
    year-less stamp stays unparseable rather than being guessed from today."""
    years = [int(m.group(1)) for m in DATE_RE.finditer(line)]
    for m in DATE_IL_RE.finditer(line):
        yy = int(m.group(3))
        years.append(yy + 2000 if yy < 100 else yy)
    return max(years) if years else None


def parse_stamp_date(line, year_hint=None):
    """Read a date out of a freshness-stamp line. ISO first, then day-first
    Israeli format (24.07.2026 / 24/7/26), then a year-less day.month when
    year_hint supplies the year (see _year_hint)."""
    m = DATE_RE.search(line)
    if m:
        try:
            return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        except ValueError:
            return None
    m = DATE_IL_RE.search(line)
    if m:
        dd, mm, yy = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if yy < 100:
            yy += 2000
        try:
            return date(yy, mm, dd)
        except ValueError:
            return None
    if year_hint is None:
        return None
    m = DATE_IL_SHORT_RE.search(line)
    if not m:
        return None
    dd, mm = int(m.group(1)), int(m.group(2))
    try:
        return date(year_hint, mm, dd)
    except ValueError:
        return None


# Scope guard. The skill has always documented an expected 1000-1300 files and a
# "2000+ means an exclusion path was dropped" alarm, but that alarm lived only in prose
# and nobody read it: on 2026-08-19 the .backups/ regression hit 2164 and on 2026-08-28
# a vendored clone hit 2282, and BOTH were noticed by hand, after the fact. This turns
# it into a field in the output so the next regression announces itself.
SCOPE_EXPECTED = (1000, 1300)
SCOPE_ALARM = 2000


def scope_check(scanned):
    """Classify files_scanned against the documented expected range."""
    lo, hi = SCOPE_EXPECTED
    if scanned >= SCOPE_ALARM:
        status, note = "alarm", (
            "files_scanned >= %d: an exclusion path was probably dropped. Find vendored "
            "clones with: find . -name .git -maxdepth 5 -not -path './.git'" % SCOPE_ALARM)
    elif scanned > hi:
        status, note = "above_expected", (
            "above the documented %d-%d range but below the %d alarm. Either real growth "
            "or a small exclusion gap; confirm before treating as normal." % (lo, hi, SCOPE_ALARM))
    elif scanned < lo:
        status, note = "below_expected", (
            "below the documented %d-%d range: an exclusion may be too broad and real "
            "docs are going unscanned." % (lo, hi))
    else:
        status, note = "ok", "within the documented %d-%d range." % (lo, hi)
    return {"status": status, "files_scanned": scanned,
            "expected_range": [lo, hi], "alarm_at": SCOPE_ALARM, "note": note}


def main():
    root = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 \
        else os.path.expanduser("$CLAUDE_WORK_DIR")
    today = date.today()
    cats = {k: [] for k in
            ("outdated_dates", "broken_links", "empty_sections",
             "stale_last_updated", "pending_todos", "past_deadlines")}
    scanned = 0
    for path in iter_md_files(root):
        scanned += 1
        f = check_file(path, root, today)
        for k in cats:
            cats[k].extend(f[k])

    priority = ["past_deadlines", "broken_links", "stale_last_updated",
                "pending_todos", "empty_sections"]
    top = []
    for cat in priority:
        for item in cats[cat]:
            if len(top) >= 10:
                break
            top.append({"category": cat, **item})
        if len(top) >= 10:
            break

    issues = sum(len(v) for k, v in cats.items()
                 if k not in INFORMATIONAL_CATEGORIES)
    result = {
        "last_run": datetime.now(timezone.utc).isoformat(),
        "files_scanned": scanned,
        "scope_check": scope_check(scanned),
        "issues_count": issues,
        "informational_counts": {k: len(cats[k]) for k in INFORMATIONAL_CATEGORIES},
        "top_findings": top,
        "categories": cats,
    }
    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
