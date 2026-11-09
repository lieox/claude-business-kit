---
name: workspace-structure-audit
description: "Use when auditing the integrity of the user's Claude workspace ($CLAUDE_WORK_DIR/ and ~/.claude/): dead or broken symlinks, orphan agents (agent file without a symlink, or a symlink whose target is gone), naming drift, files in the wrong place, or undocumented top-level entries. Hebrew triggers: בדיקת מבנה, תבדוק את המבנה, תיקיות לא נכונות, סוכנים בלי symlink, symlink שבור, קישור שבור, סוכן יתום, יתומים בשורש, בדיקת שלמות סביבה, מבנה תיקיות."
context: fork
background: false
---

# Workspace Structure Audit

## Overview

A scripted, repeatable audit of the integrity of the user's Claude workspace: the repo at `$CLAUDE_WORK_DIR/` and the harness config at `~/.claude/`. It surfaces dead or broken symlinks, orphan agents, naming drift, and misplaced or undocumented files.

The whole point is signal, not noise. A raw scan re-flags the same benign facts every run (a known orphan file, project-local agents). This skill carries an allowlist of legitimate entries and a baseline of known-recurring findings, so the report only surfaces genuinely NEW issues. Anything on the baseline is reported as KNOWN, never as a fresh discovery.

READ-ONLY. Never delete, rename, or move anything. For any proposed fix, print the exact command the user can run.

## When to Use

- the user asks to audit the folder structure, check conventions, or verify workspace integrity.
- Hunting for dead/broken symlinks, orphan agents, naming inconsistencies, or files in the wrong place.
- A scheduled or on-demand fleet-health pass that includes structure checks.
- After adding, removing, or renaming an agent, to confirm the symlink and folder line up.

## When NOT to Use

- Editing files to "fix" what you find. This audit only reports and proposes commands.
- Auditing a single client's business folder contents (that is domain work, not structure integrity).
- Security scanning of hooks/MCPs/agents (that is a separate concern; use the security scan skill).

## The macOS readlink trap (critical)

macOS `readlink` has NO GNU `-e` / `-f` flags. `readlink -e "$link"` errors out on macOS and falsely reports every symlink as broken. To test whether a symlink resolves, test the path's existence instead:

```bash
# CORRECT on macOS: [ -e ] follows the link and is true only if the target exists
[ -e "$link" ] || echo "BROKEN: $link"
```

`[ -e "$path" ]` is true when the target the link points to exists, false for a dangling link. Use `readlink "$link"` (no flags) only to PRINT where a link points, never to test resolution.

## What counts as an orphan agent

Two distinct orphan shapes, both worth flagging:

1. Agent file with no matching symlink: a `projects/<agent>/agents/<agent>.md` exists but there is no `~/.claude/agents/<agent>.md` pointing at it, so the harness cannot load it.
2. Symlink with no target: a `~/.claude/agents/<name>.md` link whose target file is gone (a dangling link left after the project was deleted or moved).

NOT orphans (do not flag):

- Project-local agents. A bespoke client system keeps its OWN agents under `projects/<system>/.claude/agents/*.md`. These are intentionally local to that project and are NOT part of the top-level fleet. They are never expected to have a `~/.claude/agents/` symlink, even when a same-named fleet agent was deleted in the past. The concrete list of such systems lives on the baseline (`references/allowlist-and-baseline.md`, section 4); read it before flagging any project-local agent.
- Fleet agents that historically shipped without a symlink. Note them, do not error.

## Allowlist and baseline (source of truth)

Before reporting anything as NEW, check it against the allowlist and known-findings baseline in:

`references/allowlist-and-baseline.md`

That file holds: the legitimate top-level directory allowlist, the known agent and non-agent project lists, the sanctioned naming exceptions, and the known-recurring findings that must be reported as KNOWN, not NEW. Read it at the start of every run.

## Procedure

1. **Load context.** Read `references/allowlist-and-baseline.md` (allowlist + baseline). If the work folder has its own conventions file (for example `docs/conventions.md`), read it too: it is newer than this skill's lists and wins.

2. **Run the scan** (commands below). Capture every raw finding.

3. **Classify each finding** against the baseline:
   - On the baseline: report under KNOWN (recurring, no action).
   - Not on the baseline: report under NEW (needs the user's attention).

4. **Report.** Group by category. For each NEW finding, print the exact READ-ONLY diagnosis and, if a fix is obvious, the exact command the user can run. Never run a mutating command.

5. **Persist learning.** When a NEW finding turns out to be benign and will recur, append it to the baseline so future runs report it as KNOWN. Add newly created legit projects/dirs to the allowlist. One dated line; do not log session chatter.

## Scan commands

Run these exactly so every run is identical. `ROOT` and `CFG` are the two trees.

```bash
ROOT="$CLAUDE_WORK_DIR"
CFG="$HOME/.claude"

# --- A. Dead / broken symlinks (macOS-safe existence test) ---
# Agent + command symlinks in the harness config, plus any symlink in the repo.
for dir in "$CFG/agents" "$CFG/commands"; do
  find "$dir" -maxdepth 1 -type l 2>/dev/null | while read -r l; do
    [ -e "$l" ] || echo "BROKEN LINK: $l -> $(readlink "$l")"
  done
done
# Repo-side symlinks (top level of the repo).
find "$ROOT" -maxdepth 1 -type l 2>/dev/null | while read -r l; do
  [ -e "$l" ] || echo "BROKEN LINK (repo): $l -> $(readlink "$l")"
done

# --- B. Orphan agents, shape 1: agent file with no matching symlink ---
# Every fleet agent lives at projects/<agent>/agents/<agent>.md and should have
# a ~/.claude/agents/<agent>.md symlink. (Skip any naming exceptions listed in the baseline.)
for f in "$ROOT"/projects/*/agents/*.md; do
  [ -e "$f" ] || continue
  name="$(basename "$f" .md)"
  [ -L "$CFG/agents/$name.md" ] || echo "AGENT WITHOUT SYMLINK: $f (expected $CFG/agents/$name.md)"
done

# --- B2. Orphan agents, shape 2: symlink whose target is gone (dangling) ---
# Covered by check A, listed here for clarity: a ~/.claude/agents/*.md link that fails [ -e ].

# --- C. Naming drift: folder name should match the agent file inside ---
for d in "$ROOT"/projects/*/; do
  proj="$(basename "$d")"
  [ -d "$d/agents" ] || continue
  [ -f "$d/agents/$proj.md" ] || echo "NAMING DRIFT: project '$proj' has no agents/$proj.md"
done

# --- D. Misplaced / undocumented top-level entries ---
# List what is actually at the repo root; compare against the allowlist in the baseline file.
ls -1A "$ROOT"

# --- E. Settings source of truth (only if the work folder uses the claude-global link, see docs/harness.md) ---
# Both paths must resolve to one physical file (same inode). stat -f is macOS, stat -c is Linux / Git Bash.
if [ -e "$ROOT/claude-global" ]; then
  stat -f '%i %N' "$ROOT/claude-global/settings.json" "$CFG/settings.json" 2>/dev/null \
    || stat -c '%i %n' "$ROOT/claude-global/settings.json" "$CFG/settings.json"
fi
```

Notes on the commands:
- Check D prints the raw root listing. Diff it by hand against the top-level allowlist in the baseline file; anything not on the allowlist is a candidate NEW orphan (but check the baseline first: the known permanent orphan file lives here). Ignore `.DS_Store` (a macOS Finder artifact that recurs at the root and inside folders): it is on the baseline as KNOWN, never a NEW finding.
- Check E: two paths sharing one inode number is the healthy state (they are the same physical file). Two different inodes means the hardlink broke: that is a NEW finding.

## Reporting format

Group findings by category (broken symlinks, orphan agents, naming drift, misplaced/undocumented, settings). Within each, split NEW vs KNOWN. Lead with NEW. If nothing new surfaced, say so plainly: a clean run is a valid, useful result.

For fixes, output commands, never execute them. Example patterns:

```bash
# Recreate a missing agent symlink
ln -s "$CLAUDE_WORK_DIR/projects/<agent>/agents/<agent>.md" \
      "$HOME/.claude/agents/<agent>.md"

# Remove a dangling symlink (confirm with the user first)
rm "$HOME/.claude/agents/<name>.md"
```

## Common mistakes

| Mistake | Rule / Fix |
|---|---|
| `readlink -e "$link"` to test a symlink | macOS has no `-e`/`-f`. It errors and falsely marks every link BROKEN. Use `[ -e "$link" ]` |
| Re-flagging a known finding every run | If it is on the baseline, state it once as KNOWN |
| Flagging project-local agents as fleet orphans | `projects/<system>/.claude/agents/*.md` are intentionally local. Never expected to have a `~/.claude/agents/` symlink |
| Running a fix command | READ-ONLY audit. Print the command for the user; never execute a mutation |

## Canonical sources

- Allowlist + known-findings baseline: `references/allowlist-and-baseline.md` (in this skill)
- The work folder's own conventions file, if it has one.
- Global rules: `$HOME/.claude/CLAUDE.md`
