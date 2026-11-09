# Allowlist and baseline

Fill this in on the first run, then keep it current. Findings listed here are reported as KNOWN, not NEW.

## Top-level allowlist
Folders and files that belong at the root of the work folder:
- `projects/` `knowledge/` `docs/` `tools/` `.backups/` `.git/` `claude-global/` (link to `~/.claude`, see docs/harness.md)
- `README.md` `CLAUDE.md` `INSTALLS.md` `.gitignore`

## Agent projects
Projects under `projects/` that hold an agent (`projects/<name>/agents/<name>.md`), each expected to have a link in `~/.claude/agents/`:
-

## Non-agent projects
Projects with no agent, so no link is expected:
-

## Naming exceptions
A project folder whose agent file has a different name (sanctioned, not drift):
-

## Known recurring findings
| Finding | Why it is accepted | Date |
|---|---|---|
| `.DS_Store` / `Thumbs.db` files | Created by the operating system | |
