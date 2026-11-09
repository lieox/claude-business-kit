#!/usr/bin/env python3
"""Regression tests for the false-positive guards in references/scan.py.

Nine guards were added on 2026-08-19 and none of them was covered by a test, so
an adversarial review had to rediscover by hand that one of them was broader than
its own documentation. These tests exist so that does not happen twice.

    python3 tests/test_scan_guards.py
"""
import importlib.util
import io
import os
import subprocess
import sys
import tempfile
import unittest
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
SCAN = os.path.join(os.path.dirname(HERE), "references", "scan.py")

spec = importlib.util.spec_from_file_location("scan", SCAN)
S = importlib.util.module_from_spec(spec)
sys.argv = ["scan.py"]
spec.loader.exec_module(S)


def git(cwd, *args, when=None):
    env = dict(os.environ)
    if when:
        env["GIT_AUTHOR_DATE"] = env["GIT_COMMITTER_DATE"] = when
    subprocess.run(["git"] + list(args), cwd=cwd, check=True,
                   capture_output=True, env=env)


class Repo:
    def __enter__(self):
        self.d = tempfile.mkdtemp()
        git(self.d, "init", "-q", ".")
        git(self.d, "config", "user.email", "t@t")
        git(self.d, "config", "user.name", "t")
        return self

    def commit(self, name, text, when):
        with open(os.path.join(self.d, name), "w", encoding="utf-8") as f:
            f.write(text)
        git(self.d, "add", "-A")
        git(self.d, "commit", "-qm", "c", when=when)
        return os.path.join(self.d, name)

    def head(self):
        return subprocess.run(["git", "rev-parse", "HEAD"], cwd=self.d,
                              capture_output=True, text=True).stdout.strip()

    def __exit__(self, *a):
        pass


class CommitIsSubstantive(unittest.TestCase):
    """The stamp guard must cancel a stamp bump WITHOUT blinding the scanner to a
    real edit that happens to share the line. The first version of this guard
    dropped every diff line containing a freshness keyword, and LAST_UPDATED_RE
    matches bare "עודכן" and "נכון ל", so real content went invisible."""

    def test_pure_stamp_bump_is_cosmetic(self):
        with Repo() as r:
            r.commit("d.md", "# T\n\nupdated: 2026-01-01\n\nStable body.\n",
                     "2026-01-01T10:00:00")
            p = r.commit("d.md", "# T\n\nupdated: 2026-06-01\n\nStable body.\n",
                         "2026-06-01T10:00:00")
            self.assertFalse(S.commit_is_substantive(r.head(), p))

    def test_real_edit_ON_the_stamp_line_is_substantive(self):
        with Repo() as r:
            r.commit("d.md", "# T\n\nupdated: 2026-01-01 , not started, budget 1000\n\nBody.\n",
                     "2026-01-01T10:00:00")
            p = r.commit("d.md", "# T\n\nupdated: 2026-01-01 , SHIPPED, budget 90000\n\nBody.\n",
                         "2026-06-01T10:00:00")
            self.assertTrue(S.commit_is_substantive(r.head(), p),
                            "content change on a keyword line was swallowed")

    def test_real_edit_on_a_hebrew_keyword_line_is_substantive(self):
        # "נכון ל" is in LAST_UPDATED_RE, and this is a real case.
        before = "# T\n\nנכון ל-01.01.2026: תת-פרויקט 1 בבנייה\n"
        after = "# T\n\nנכון ל-01.01.2026: תת-פרויקט 2 הושלם, 105 בדיקות עוברות\n"
        with Repo() as r:
            r.commit("d.md", before, "2026-01-01T10:00:00")
            p = r.commit("d.md", after, "2026-06-01T10:00:00")
            self.assertTrue(S.commit_is_substantive(r.head(), p))

    def test_typography_sweep_is_cosmetic(self):
        with Repo() as r:
            r.commit("d.md", "# T\n\nAlpha — beta — gamma.\n", "2026-01-01T10:00:00")
            p = r.commit("d.md", "# T\n\nAlpha, beta, gamma.\n", "2026-06-01T10:00:00")
            self.assertFalse(S.commit_is_substantive(r.head(), p))

    def test_link_path_repair_is_cosmetic(self):
        with Repo() as r:
            r.commit("d.md", "# T\n\nSee [x](../../a/b.md).\n", "2026-01-01T10:00:00")
            p = r.commit("d.md", "# T\n\nSee [x](../../../a/b.md).\n", "2026-06-01T10:00:00")
            self.assertFalse(S.commit_is_substantive(r.head(), p))


class StampParsing(unittest.TestCase):
    """Reading the wrong date on a two-date line made fresh docs look stale, and
    returning None on an unparseable tail silently disabled the check entirely."""

    def test_reads_the_date_the_keyword_introduces(self):
        line = "נוצר 27.07.2026 · עודכן 14.08.2026"
        self.assertEqual(S.parse_stamp_date_after_keyword(line), date(2026, 8, 14))

    def test_falls_back_instead_of_disabling_the_check(self):
        # "14.08" has no year, so DATE_IL_RE cannot parse it. Returning None here
        # skipped the file rather than evaluating it. Fall back to an earlier date.
        line = "נוצר 27.07.2026 · עודכן 14.08"
        self.assertIsNotNone(S.parse_stamp_date_after_keyword(line))

    def test_prose_without_any_date_is_still_none(self):
        self.assertIsNone(S.parse_stamp_date_after_keyword("עודכן בעבר"))


class NegatedMarkers(unittest.TestCase):
    """Mirrors the real call site at scan.py:344, which tests the text BEFORE the
    first marker token, not the whole line."""

    @staticmethod
    def suppressed(line):
        tm = S.TODO_RE.search(line)
        if not tm:
            return None
        return bool(S.NEGATED_MARKER_RE.search(line[:tm.start()]))

    def test_absence_assertion_is_not_a_pending_item(self):
        for line in ("No TBD/TODO.", "אין TBD, אין TODO", "zero FIXME"):
            self.assertTrue(self.suppressed(line), line)

    def test_a_real_pending_item_still_fires(self):
        for line in ("no owner yet, TODO assign", "TODO: write this"):
            self.assertFalse(self.suppressed(line), line)


class Exclusions(unittest.TestCase):
    def test_backups_snapshot_area_is_excluded(self):
        self.assertTrue(S.is_excluded("/home/x/work/.backups/memory-20260815/a.md"))

    def test_ordinary_doc_is_not_excluded(self):
        self.assertFalse(S.is_excluded("/home/x/work/knowledge/business/a.md"))


class PastDeadlineOnlyFiresOnTheLatestDate(unittest.TestCase):
    """T-2026-08-25-013 defect 2: a past date ANYWHERE on a line carrying a deadline
    word used to fire past_deadline, even when the deadline itself is in the future.
    Verified on INSTALLS.md:281, where a 2026-09-06 expiry was reported as passed
    because a 2026-07-24 verification date shared the line."""

    def scan_line(self, text):
        with tempfile.TemporaryDirectory() as d:
            f = os.path.join(d, "doc.md")
            io.open(f, "w", encoding="utf-8").write(text + "\n")
            return S.check_file(f, d, date(2026, 8, 26))

    def test_future_deadline_with_past_verification_date_is_clean(self):
        line = ("- **Token expires:** 2026-09-06 (renewed; verified via "
                "debug_token 2026-07-24)")
        self.assertEqual(self.scan_line(line)["past_deadlines"], [])

    def test_genuinely_passed_deadline_still_fires(self):
        line = "- **Token expires:** 2026-07-24 (due date, verified 2026-07-01)"
        hits = self.scan_line(line)["past_deadlines"]
        self.assertEqual(len(hits), 1)
        self.assertIn("2026-07-24", hits[0]["issue"])

    def test_it_reports_the_latest_date_not_the_earliest(self):
        line = "deadline: shipped 2026-01-05, extended until 2026-07-30"
        hits = self.scan_line(line)["past_deadlines"]
        self.assertEqual(len(hits), 1)
        self.assertIn("2026-07-30", hits[0]["issue"])

    def test_one_finding_per_line_not_one_per_date(self):
        line = "due 2026-02-01 2026-03-01 2026-04-01"
        self.assertEqual(len(self.scan_line(line)["past_deadlines"]), 1)


class DeadlineWordsAreWordBounded(unittest.TestCase):
    """Found 2026-08-26 while fixing T-2026-08-25-013, and not in the ticket: the
    keyword test was a naive substring match, so the Hebrew "עד" fired inside "עדכון"
    (update) and "מועד" (appointment), and "by" fired inside "bytes". Every Hebrew
    "## עדכון <past date>" heading was filed as a passed deadline."""

    def scan_line(self, text):
        with tempfile.TemporaryDirectory() as d:
            f = os.path.join(d, "doc.md")
            io.open(f, "w", encoding="utf-8").write(text + "\n")
            return S.check_file(f, d, date(2026, 8, 26))["past_deadlines"]

    def test_update_heading_is_not_a_deadline(self):
        self.assertEqual(self.scan_line("## עדכון 2026-08-13 , הלקוח אישר"), [])

    def test_moed_is_not_a_deadline(self):
        self.assertEqual(self.scan_line("מועד הפגישה נקבע 2026-02-01"), [])

    def test_bytes_is_not_a_deadline(self):
        self.assertEqual(self.scan_line("the file is 2026-01-05 and 40 bytes"), [])

    def test_maintained_by_someone_is_not_a_deadline(self):
        self.assertEqual(self.scan_line("maintained by the team, last touched 2026-01-05"), [])

    def test_standalone_hebrew_ad_still_fires(self):
        self.assertEqual(len(self.scan_line("להגיש עד 2026-02-01")), 1)

    def test_ad_as_up_to_a_quantity_is_not_a_deadline(self):
        self.assertEqual(
            self.scan_line("פיצוי לדוגמה עד ₪1,000 למסר (Log 2026-06-14)"), [])

    def test_ad_as_until_a_condition_is_not_a_deadline(self):
        self.assertEqual(
            self.scan_line("הפגם לא נראה עד שבודקים את הסט (Log 2026-08-18)"), [])

    def test_by_followed_by_a_date_still_fires(self):
        self.assertEqual(len(self.scan_line("deliver by 2026-02-01")), 1)

    def test_english_deadline_words_still_fire(self):
        for line in ("due 2026-02-01", "shipped 2026-02-01",
                     "launched 2026-02-01", "deadline 2026-02-01",
                     "until 2026-02-01"):
            self.assertEqual(len(self.scan_line(line)), 1, line)

if __name__ == "__main__":
    unittest.main(verbosity=2)
