#!/bin/bash
# Git sync for the Claude work folder: commit + pull + push, at most once in the morning and once in
# the evening. Run it from a SessionStart hook or from a scheduled task (see README.md).
#
# Commit-first design: it never runs a standalone `git stash` and never `checkout --theirs`, so it
# cannot silently discard or orphan uncommitted work. Local changes are committed first, then the
# remote is merged with `pull --rebase --autostash`. On a real conflict it aborts and stops, and the
# local commits stay intact for a manual merge.
#
# Settings (environment variables, all optional):
#   CLAUDE_WORK_DIR      the work folder (a git repo with an "origin" remote). Default: ~/claude-work
#   CLAUDE_SYNC_BRANCH   the only branch it will ever sync. Default: main
#   CLAUDE_SYNC_ANYTIME  set to 1 to run now, outside the morning/evening windows (manual sync)

REPO="${CLAUDE_WORK_DIR:-$HOME/claude-work}"
BRANCH_MAIN="${CLAUDE_SYNC_BRANCH:-main}"
LOG="$REPO/.git-sync.log"
STATE="$REPO/.git-sync-state"
STUCK_NOTE="$REPO/GIT-SYNC-STUCK.md"
TS=$(date "+%Y-%m-%d %H:%M:%S")
log() { echo "[$TS] $1" >> "$LOG"; }

[ -d "$REPO/.git" ] || exit 0
cd "$REPO" || exit 0
git remote get-url origin &>/dev/null || exit 0

# --- Window gate: once in the morning, once in the evening (24h clock, end exclusive) ---
MORNING_START=5;  MORNING_END=12
EVENING_START=17; EVENING_END=24
HOUR=$((10#$(date +%H)))
if   [ "$HOUR" -ge "$MORNING_START" ] && [ "$HOUR" -lt "$MORNING_END" ]; then WINDOW=morning
elif [ "$HOUR" -ge "$EVENING_START" ] && [ "$HOUR" -lt "$EVENING_END" ]; then WINDOW=evening
else WINDOW=""; fi
[ -n "$CLAUDE_SYNC_ANYTIME" ] && WINDOW="${WINDOW:-manual}"
if [ -z "$WINDOW" ]; then
  log "skipped (outside morning/evening window, hour=$HOUR)"
  exit 0
fi
STAMP="$(date +%Y-%m-%d)-$WINDOW"
if [ -f "$STATE" ] && [ "$(cat "$STATE" 2>/dev/null)" = "$STAMP" ]; then
  log "skipped ($WINDOW already synced today)"
  exit 0
fi

# A stuck repo must reach a human, not only this log. The note sits in the work folder root,
# where it is seen, and the next session's Claude reads it.
flag_stuck() {
  {
    echo "# הסנכרון ל-git תקוע"
    echo
    echo "- מתי: $TS"
    echo "- מה: $1"
    echo "- שום דבר לא נכנס לקומיט ולא נדחף. הפירוט ב-\`.git-sync.log\`."
    echo "- לסגור את המצב בלי לאבד עבודה, ואז למחוק את הקובץ הזה."
  } > "$STUCK_NOTE"
}
in_progress() {  # prints the git operation left open, if any
  local d m
  d="$(git rev-parse --absolute-git-dir 2>/dev/null)" || return 0
  for m in rebase-merge rebase-apply MERGE_HEAD CHERRY_PICK_HEAD; do
    if [ -e "$d/$m" ]; then echo "$m"; return 0; fi
  done
}

OPEN_OP="$(in_progress)"
if [ -n "$OPEN_OP" ]; then
  log "STUCK: $OPEN_OP in progress, nothing committed or pushed"
  flag_stuck "$OPEN_OP פתוח בריפו"
  exit 0
fi

# Only ever sync the main branch. Otherwise a feature branch gets committed and rebased by a hook.
BRANCH="$(git rev-parse --abbrev-ref HEAD 2>/dev/null)"
if [ "$BRANCH" = "HEAD" ]; then
  log "STUCK: detached HEAD, nothing committed or pushed"
  flag_stuck "HEAD מנותק"
  exit 0
fi
if [ "$BRANCH" != "$BRANCH_MAIN" ]; then
  log "skipped (on branch '$BRANCH', not $BRANCH_MAIN)"
  exit 0
fi

echo "$STAMP" > "$STATE"
log "running $WINDOW sync (hour=$HOUR)"

# 1. Commit local changes. Sensitive file shapes are kept out of the commit.
#    This is an unattended publish step, so a denylist alone is not enough: step 1b scans content.
git add -A \
  -- ':!.git-sync-state' ':!.git-sync.log' ':!GIT-SYNC-STUCK.md' \
     ':!*.env' ':!.env*' ':!*.pem' ':!*.key' ':!*.p12' ':!*.pfx' \
     ':!*id_rsa*' ':!*id_ed25519*' ':!*.ppk' \
     ':!*credentials*' ':!*secret*' ':!*.secrets' ':!*token*.json' \
     ':!*service-account*.json' ':!*cookies.txt' ':!*.sqlite' ':!*.sqlite3' \
     ':!**/bots.json' ':!**/mcp.json' \
     2>/dev/null

# 1b. Refuse to commit staged content that looks like a live credential. A filename denylist cannot
#     catch a key pasted into an ordinary .md, so this scans the staged diff. Python and not grep:
#     some grep builds reject long patterns and exit non-zero, which reads as "nothing found".
#     Any error, or no Python at all, aborts the commit (fail closed).
PY="$(command -v python3 || command -v python || command -v py)"
if [ -z "$PY" ]; then
  log "ABORTED: no python found for the secret scan. Nothing committed, nothing pushed."
  exit 0
fi
SECRET_SCAN=$(git diff --cached -U0 2>/dev/null | "$PY" -c '
import re, sys
PAT = re.compile(
    r"sk-ant-(?:api|admin|oat|sid)[0-9]{2}-[A-Za-z0-9_-]{20}"
    r"|sk-(?:proj-)?[A-Za-z0-9_-]{30}"
    r"|github_pat_[A-Za-z0-9_]{20}"
    r"|ghp_[A-Za-z0-9]{30}"
    r"|xox[baprs]-[A-Za-z0-9-]{20}"
    r"|AKIA[0-9A-Z]{16}"
    r"|AIza[0-9A-Za-z_-]{35}"
    r"|-----BEGIN [A-Z ]*PRIVATE KEY-----"
    r"|EAA[A-Za-z0-9]{40}"
    r"|[0-9]{8,10}:[A-Za-z0-9_-]{35}"
)
try:
    for line in sys.stdin:
        if line[:1] == "+" and PAT.search(line):
            print("HIT"); break
except Exception:
    print("HIT")
' 2>/dev/null || echo "HIT")
if [ "$SECRET_SCAN" = "HIT" ]; then
  log "ABORTED: staged content matched a credential pattern. Nothing committed, nothing pushed."
  flag_stuck "נמצא בקבצים משהו שנראה כמו מפתח או טוקן. הקבצים נשארו בשלב ה-staging, ושום דבר לא נכנס לקומיט"
  exit 0
fi

if ! git diff --cached --quiet; then
  git commit -m "$WINDOW sync $(date +%Y-%m-%d)" --quiet
  log "committed local changes ($WINDOW)"
fi

# 2. Sync with the remote. --autostash shelves the excluded files around the rebase and reapplies them.
git fetch origin "$BRANCH_MAIN" --quiet 2>/dev/null
if [ "$(git rev-parse HEAD)" = "$(git rev-parse "origin/$BRANCH_MAIN" 2>/dev/null)" ]; then
  log "already in sync"
  rm -f "$STUCK_NOTE"
  exit 0
fi
if ! PULL_ERR="$(git pull --rebase --autostash origin "$BRANCH_MAIN" --quiet 2>&1)"; then
  ABORT_ERR="$(git rebase --abort 2>&1)"
  OPEN_OP="$(in_progress)"
  if [ -n "$OPEN_OP" ]; then
    log "REBASE STUCK: abort failed, $OPEN_OP still open: ${ABORT_ERR//$'\n'/ }"
    flag_stuck "rebase --abort נכשל, $OPEN_OP פתוח"
  else
    log "rebase conflict with remote, manual merge needed, local commits intact: ${PULL_ERR//$'\n'/ }"
    flag_stuck "התנגשות מול השרת. הקומיטים המקומיים שמורים, צריך מיזוג ידני"
  fi
  exit 0
fi

# 3. Push if ahead. A failed push is logged and flagged: silence is not success.
AHEAD=$(git rev-list "origin/$BRANCH_MAIN..HEAD" --count 2>/dev/null)
if [ "$AHEAD" -gt 0 ] 2>/dev/null; then
  if PUSH_ERR="$(git push origin "$BRANCH_MAIN" --quiet 2>&1)"; then
    log "pushed ($AHEAD commits)"
    rm -f "$STUCK_NOTE"
  else
    log "PUSH FAILED ($AHEAD commits still local): ${PUSH_ERR//$'\n'/ }"
    flag_stuck "הדחיפה נכשלה. $AHEAD קומיטים נשארו רק במחשב"
  fi
fi
