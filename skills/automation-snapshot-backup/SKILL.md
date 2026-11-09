---
name: automation-snapshot-backup
description: "Use when about to edit, PATCH, clone, or delete a live client automation: a Make scenario/blueprint, a SendPulse template/flow/bot, an Airtable automation, or any record-writing or delete script. Also when a local snapshot may be stale before an edit. Triggers: לפני שעורכים אוטומציה, גיבוי לפני שינוי, גבה קודם, snapshot לפני עריכה, בלופרינט לפני PATCH, לגבות תבניות SendPulse, גיבוי דאטה ב-Airtable, למשוך מחדש לפני עריכה, back up first."
---

# Automation Snapshot and Backup Discipline

## Overview

Every live automation layer is fragile, shared state that the client keeps changing between sessions. There is no built-in undo: a bad PATCH can invalidate a Make blueprint, a template edit overwrites the old one, and a data script can corrupt records in one batch. The saved snapshot IS the only undo path. So the rule is absolute: snapshot the exact live state into the client folder BEFORE you touch it, and re-pull first whenever your local copy might be stale. This applies to every automation client, with no exceptions.

This skill is the discipline layer. For the Make REST mechanics (auth, User-Agent, PATCH, verify-active) use `make-scenario-ops`; when an MCP is missing or fails use `mcp-rest-fallback`.

## When to Use

- About to edit, PATCH, clone, or delete a Make scenario or its blueprint.
- About to change a SendPulse template, flow, bot, or trigger.
- About to edit an Airtable automation (script action), or run a script/batch that writes or deletes records.
- About to bulk-update or delete records on any platform (records are shared live state).
- Your local snapshot is older than the last time the client could have edited in the UI (assume they did): re-pull before editing.
- Starting work on a new automation client and there is no backup folder yet.

## When NOT to Use

- Pure read-only inspection (listing, fetching, reporting) that writes nothing: no snapshot needed.
- Editing your OWN files in the repo under version control (git already gives you history).
- A layer the client marked read-only reference (for example an old-version folder kept as a baseline during a migration): do not edit it at all, so nothing to back up.

## The Core Rule

1. **Re-pull the live state.** Any copy already in the client folder is a point-in-time snapshot; assume the client iterated in the UI since. Pull fresh from the API before doing anything.
2. **Save the snapshot into the client folder** with the house naming convention (below), BEFORE any write.
3. **Only then edit.** Make the change via the platform-specific skill.
4. **Verify, and keep the snapshot** as the restore point. If the edit breaks the layer, restore the snapshot.

Never edit off a stale snapshot. Never edit without a fresh snapshot on disk. The snapshot is the undo button; if it does not exist, there is no undo.

## Where Snapshots Live: the Client Folder Convention

Every client (or the business itself) has a folder in the work folder defined in CLAUDE.md, for example:

```
<work folder>/clients/<Client>/
```

Inside it, backups are organized by layer:

| Layer | Location | What to save |
|---|---|---|
| Make scenarios (versioned edits) | `<Client>/make-scenarios/<version>/` | one `.LIVE-<date>.json` per scenario (see below) |
| Make full-account backup | `<Client>/make-automations-backup/` | one raw blueprint per scenario + an `_INDEX.json` mapping |
| SendPulse templates/flows/bots | `<Client>/sendpulse-templates-backup/` | raw API dumps: `raw_templates.json`, `raw_flows.json`, `raw_bots.json` |
| Airtable data snapshots (before a script/batch) | `<Client>/backups/` | descriptive `<what>-<date>.json` (see below) |

Create the subfolder if it does not exist. Keep the client's `INDEX.md` (scenario / apps / tables mapping) updated when you add or change a Make snapshot.

## Naming Conventions (match these exactly)

### Make scenario snapshots

```
<Client>/make-scenarios/<version>/{scenarioId} - {scenario name}.LIVE-{YYYY-MM-DD}.json
```

Real examples on disk (verify the shape, do not reuse the values):
- `make-scenarios/v2/{scenarioId} - Monthly Session Generation.LIVE-{YYYY-MM-DD}.json`
- `make-scenarios/v1/{scenarioId} - <scenario name>.LIVE-{YYYY-MM-DD}.json`

Rules:
- `{scenarioId}` and `{scenario name}` come straight from the scenario. The date is the day you pulled it.
- `.LIVE-` marks it as a pulled-from-production snapshot (not a hand-edited draft).
- Every re-pull writes a NEW dated file; do not overwrite an older `.LIVE-` snapshot. The dated history is the point. Multiple dates for one scenario id living side by side is correct and expected.
- Two file shapes exist in the wild: the raw API wrapper `{"code":"OK","response":{"blueprint":{...}}}` and the bare blueprint `{name, flow, metadata}`. Save whatever the GET returned; when you later restore or diff, detect by top-level keys and unwrap the wrapper first (a PATCH takes only the bare blueprint, stringified). See `make-scenario-ops`.

### Make full-account backup

```
<Client>/make-automations-backup/{state}_{slug}__{scenarioId}.json
<Client>/make-automations-backup/_INDEX.json
```

`{state}` encodes whether the scenario was active at capture time (`on` / `off`), `{slug}` is a short human name, `{scenarioId}` is the numeric id. Staged (not-yet-pushed) edits get their own name, for example `phase1-edited-STAGED__{scenarioId}.json`, so the pristine backup is never confused with your draft.

### SendPulse template/flow backup

Dump the raw API responses verbatim, one file per resource type:

```
<Client>/sendpulse-templates-backup/raw_templates.json
<Client>/sendpulse-templates-backup/raw_flows.json
<Client>/sendpulse-templates-backup/raw_bots.json
```

WhatsApp templates, once approved, cannot be edited (only replaced), so the raw dump is your record of what the approved copy actually was. Re-dump before any template or flow change.

### Airtable data snapshot (before a script or batch write)

```
<Client>/backups/{what}-{YYYY-MM-DD}.json
```

Real examples of the shape:
- `backups/sessions-snapshot-2026-07-03.json` (full table dump before a realign script)
- `backups/trial-subs-backup-2026-07-04.json` (the specific records a batch will touch)
- `backups/<migration>-2026-07-03-old-to-new.json` (before/after map for a data migration)

Rules:
- `{what}` names the data and the operation, so a future reader knows what this restores.
- Snapshot the records the script will write to, at minimum. For a destructive or wide change, dump the whole table.
- One snapshot per run, dated. Keep the old ones.

## How to Pull Each Layer

Credentials are never hardcoded. Read them at runtime from environment variables, keep them in-process, and print only status codes or byte counts. See `mcp-rest-fallback` for the extraction pattern and per-platform recipes.

| Layer | Pull with | Key detail |
|---|---|---|
| Make blueprint | `GET /scenarios/{id}/blueprint` via REST | MANDATORY browser User-Agent header or Cloudflare 403 `error code: 1010`. Full recipe: `make-scenario-ops` |
| Make scenario list (to snapshot a whole account) | `GET /scenarios?teamId=<id>&pg%5Blimit%5D=300` | Resolve the client's real teamId; do not trust env `MAKE_TEAM` |
| SendPulse templates/flows/bots | REST GET (templates, flows, bots endpoints) | OAuth client_credentials to Bearer; MCP list tools also work for read |
| Airtable table / records | REST `GET /v0/{baseId}/{tableId}` (paginate) or MCP list/search | Hebrew `filterByFormula` with a compound value tends to 422; full-fetch and filter in code |

For Make specifically, `make-scenario-ops` Procedure 1 already bakes in the pull-then-snapshot-then-edit loop. This skill is the same discipline generalized to every other layer.

## Minimal Pull-and-Snapshot (any REST layer)

Save the raw GET response verbatim into the client folder before editing. Print only the byte count, never the token.

```python
import json, os, sys, urllib.request
from datetime import date

# creds at runtime, from environment variables
key, zone = os.environ['MAKE_API_KEY'], 'eu2.make.com'  # your Make zone

UA = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/124.0 Safari/537.36')  # else Cloudflare 1010

SID = '<scenarioId>'   # placeholder
url = f'https://{zone}/api/v2/scenarios/{SID}/blueprint'
req = urllib.request.Request(url, headers={
    'Authorization': 'Token ' + key, 'User-Agent': UA, 'Accept': 'application/json'})
raw = urllib.request.urlopen(req).read().decode()

client_dir = os.path.expanduser('<work folder>/clients/<Client>')
snap = f'{client_dir}/make-scenarios/v2/{SID} - <scenario name>.LIVE-{date.today()}.json'
open(snap, 'w').write(raw)               # save the LIVE snapshot BEFORE any PATCH
print('saved', len(raw), 'bytes')        # status only, never the token
```

## Staleness Check

Before editing off any snapshot already in the folder, ask: could the client have changed this layer in the UI since that date? Assume yes. Re-pull and compare:
- If the fresh pull differs from the stored snapshot, the stored one is stale. Save the fresh dated snapshot and edit off that.
- A known real failure mode: a repo blueprint that looked complete was actually stale (a smaller/older file than the live one), and editing off it would have dropped logic the client added in the UI. Re-pulling caught it. Always re-pull first.

## Restore

The snapshot is the undo path, so know how to use it:
- **Make blueprint:** if a PATCH leaves the scenario `isinvalid` and it will not `start`, PATCH the saved snapshot back (unwrap the `{code, response}` wrapper to the bare blueprint first, stringify it). See `make-scenario-ops`.
- **SendPulse template:** you cannot edit an approved template back; you re-create it from the raw dump copy and re-submit for approval.
- **Airtable data:** re-write the records from the dated `backups/` JSON (match by record id).

## Common Mistakes

| Mistake | Rule / Fix |
|---|---|
| Editing a Make scenario without pulling a fresh blueprint first | Re-pull `GET /scenarios/{id}/blueprint` every time; the repo copy goes stale between sessions |
| PATCH / batch / template edit with no snapshot on disk | Save the snapshot into the client folder BEFORE the write. It is the only undo |
| Overwriting yesterday's `.LIVE-<date>.json` | Each pull is a new dated file; the dated history is the restore chain. Keep them all |
| Running a data script against a whole table with no backup | Dump the affected records (or the whole table) to `<Client>/backups/{what}-<date>.json` first |
| Assuming a template edit is reversible | Approved SendPulse/WhatsApp templates cannot be edited, only replaced. The raw dump is your only record of the old copy |
| Saving the snapshot to /tmp or the scratchpad | Snapshots belong in the client folder so they survive the session and are the durable undo |
| Trusting a snapshot that predates likely UI edits | Assume the client changed it; re-pull and compare before editing |
| Backing up only your edited draft, not the pristine original | Keep the pristine pull separate (for example `..._STAGED__{id}.json` for the draft) so the true undo point is intact |
| Printing a credential while pulling | Read it at runtime from an environment variable, keep in-process, print only byte counts / status codes |

## Canonical Sources

`make-scenario-ops` and `mcp-rest-fallback` are optional skills that are not part of this kit. Without them, use the recipes in this file.


- Make REST mechanics (pull, PATCH, verify-active, webhook queue): `make-scenario-ops` skill.
- MCP missing or failing, credential extraction, per-platform REST recipes: `mcp-rest-fallback` skill.
- Per-client backups root: `<work folder>/clients/<Client>/`
- Credentials: environment variables only, never in files that go to git.
