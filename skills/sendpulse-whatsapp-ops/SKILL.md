---
name: sendpulse-whatsapp-ops
description: "Use when sending WhatsApp messages through SendPulse: text sends, templates, interactive lists, broadcasts, or contact setup; when a sendpulse MCP tool returns 422; when a send fails with 'Contact is not active in 24hours'; when a business-initiated message must reach someone who has not written back recently; or before any bulk send. Hebrew triggers: שלח וואטסאפ, הודעה בוואטסאפ, סנדפולס, תבנית וואטסאפ, דיוור בוואטסאפ, רשימת תפוצה, בוט וואטסאפ."
---

# SendPulse WhatsApp Operations

## Overview

Two constraints govern every SendPulse WhatsApp send: the API accepts only exact payload shapes (the local MCP has shipped flat payloads the API rejects with 422), and WhatsApp delivers business-initiated free text only inside a 24 hour service window that the USER must open. Decide the legal and delivery path first, then send with a known-good recipe.

## When to Use

- Any WhatsApp send through SendPulse: free text, template, interactive list, media.
- A sendpulse MCP tool (send_message, set_contact_variable) returns 422.
- A send fails with "Contact is not active in 24hours".
- Business-initiated delivery (daily report, notification) to a contact who has not messaged recently.
- Any bulk or broadcast send.
- Creating or updating contacts (name, tags, variables) in a SendPulse bot.

## When NOT to Use

- SendPulse email campaigns (this skill covers WhatsApp only).
- Other WhatsApp providers (direct Meta Cloud API, Twilio).
- Pure read operations that already work via MCP (list_chats, list_bots, list_templates) and return no errors.

## Credentials

The MCP server in this kit ([lieox/sendpulse-whatsapp-mcp](https://github.com/lieox/sendpulse-whatsapp-mcp)) reads `SENDPULSE_CLIENT_ID` and `SENDPULSE_CLIENT_SECRET` (SendPulse: Settings > API). For direct REST calls, read the same two values from environment variables at runtime. Never print, paste or hardcode them: they open the whole account.

If the business has more than one SendPulse account, confirm which account and which bot before any operation.

## Quick Reference

| Operation | Reliable path | Endpoint / tool |
|---|---|---|
| OAuth token | REST | `POST https://api.sendpulse.com/oauth/access_token` |
| Free text (window open) | MCP send_message; on 422 switch to REST | `POST /whatsapp/contacts/send` |
| Template (allowed any time) | REST | `POST /whatsapp/contacts/sendTemplate` (by contact_id) or `POST /whatsapp/contacts/sendTemplateByPhone` |
| Inspect templates | REST | `GET /whatsapp/templates?bot_id=<BOT_ID>` |
| Interactive list (max 10 rows) | REST | `POST /whatsapp/contacts/sendByContact` |
| Set contact variable | REST only (MCP broken: 422) | `POST /whatsapp/contacts/setVariable` |
| Find contact_id | MCP | `sendpulse_list_chats` (works fine) |
| Contact's recent messages | REST | `GET /whatsapp/chats/messages?contact_id=<id>&size=50` |
| Create contact | MCP | `sendpulse_create_contact`, then `sendpulse_set_contact_name` immediately |

All REST paths are relative to `https://api.sendpulse.com`. The WhatsApp base is `/whatsapp`, NOT `/chatbot/whatsapp` (the latter returns "Resource not found"; that error means wrong base URL, not bad credentials).

Full request bodies and curl recipes: [references/rest-recipes.md](references/rest-recipes.md).

## Send-Path Decision Tree

Run top to bottom before any send:

1. **Marketing content?** Israeli spam law (Communications Law section 30a, tikun 40) forbids marketing messages without documented prior opt-in. Every marketing message must carry the word "פרסומת", the advertiser's name and address, and a one-click unsubscribe. Exposure: exemplary damages up to 1,000 ILS per message with no proof of harm required. The "existing customer" exception is narrow and never covers cold outreach. No documented opt-in means do not send, full stop.
2. **Bulk send (more than one recipient)?** STOP and get explicit human confirmation first. Confirm all four: account, audience size, template name, scheduled time. Never fire a broadcast on your own judgment.
3. **Did the CONTACT message the business within the last 24 hours?** Check the last inbound message (`GET /whatsapp/chats/messages?contact_id=<id>&size=50`).
   - Yes: the service window is open. Free text is allowed and free (a successful send shows price 0 / not paid).
   - No: free text fails with `422 {"errors":{"contact_id":["(#2) Contact is not active in 24hours"]}}`. You MUST use an approved template. Sending a template does NOT open the window; only an inbound user action (message or button tap) does.
4. **Long free-form content, business-initiated?** Use the template + quick-reply button + poller pattern (next section).
5. **MCP or REST?** Start with the MCP. If an MCP send returns 422, do not iterate blindly more than twice: switch to direct REST with the documented payload (nested `message.text.body`).

## The Business-Initiated Delivery Pattern

Problem: WhatsApp forbids business-initiated free text outside the 24h window, and the window opens only from the user side. A daily report to someone who does not write in every day will 422 every time.

The pattern that works:

1. Get a template approved that asks permission and carries a quick-reply button, for example a Hebrew template with the button "שלחו לי את הדו"ח".
2. Send the template whenever needed (templates are allowed any time): `POST /whatsapp/contacts/sendTemplate` with `{"contact_id":"...","template":{"name":"...","language":{"code":"he"}}}`.
3. The user taps the button. That inbound action opens the 24h window.
4. A local poller (Task Scheduler on Windows, launchd on Mac, e.g. every 5 minutes) attempts the free-text send each tick: while the window is closed it gets 422 and waits; after the tap it succeeds. Mark delivery per day so it sends once.
5. Cap free text at 4096 characters.

Why a local poller and not a SendPulse flow: SendPulse variables and flows can only be created in the dashboard UI, not via API (setVariable on a non-existent variable returns "Variable does not exist"). A flow that listens to a reply CAN post to a webhook, but wiring it is manual work in the visual editor.


## Capturing Replies: Event-Driven, Never Sleep

To act on a user's button tap or interactive-list choice, never build: send list, Sleep, "get last message". A user answering faster or slower than the timer reads an empty or wrong message and the choice is silently lost; this anti-pattern silently drops replies and can make a whole matching system produce zero results.

Correct structure: scenario A ends immediately after sending the list or buttons. A SendPulse Quick Reply / keyword trigger (or a flow wired in the SendPulse UI to the list reply) fires a webhook that starts scenario B with `{contact_id, ...choice}`.

## Contact Creation Workflow

1. Phone in international format WITHOUT `+`: Israeli numbers `972XXXXXXXXX`; Palestinian 059/056 numbers become `970XXXXXXXXX` (WhatsApp runs them on 970). Never create a contact without a phone number verified with the human.
2. `sendpulse_create_contact(account, bot_id, phone)` and save the returned contact_id. This call takes ONLY phone: the contact lands nameless in the dashboard.
3. Immediately call `sendpulse_set_contact_name(contact_id, name)`. Never defer it.
4. `sendpulse_set_contact_tags(contact_id, [tags])` if applicable.
5. Variables: direct REST only (`POST /whatsapp/contacts/setVariable`); the MCP tool returns 422 even when the variable exists. The variable must already exist at bot level; missing variables can only be created in the dashboard UI.
6. Before a batch, sample an existing contact of the same type (`sendpulse_list_chats`, inspect variables) and clone the convention. For example, if existing contacts carry `client_type` and `client_status` variables, set the same ones.
7. Verify one created contact via `sendpulse_list_chats` (variables actually set).
8. Identify contacts by phone, never by name: contact names come from users' WhatsApp profiles and collide.

## Worked Example

Deliver a text report to one contact, handling the closed-window case.

```bash
python3 - <<'PY'
import json, os, sys, urllib.error, urllib.request

# 1. Creds from environment variables (never hardcode)
acc = {"id": os.environ["SENDPULSE_CLIENT_ID"], "secret": os.environ["SENDPULSE_CLIENT_SECRET"]}

def post(url, body, token=None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, json.dumps(body).encode(), headers)
    try:
        return json.load(urllib.request.urlopen(req)), 200
    except urllib.error.HTTPError as e:
        return json.loads(e.read() or b"{}"), e.code

# 2. OAuth: client_credentials -> Bearer token
tok, _ = post("https://api.sendpulse.com/oauth/access_token",
              {"grant_type": "client_credentials",
               "client_id": acc["id"], "client_secret": acc["secret"]})
token = tok["access_token"]

CONTACT = "<CONTACT_ID>"                 # from sendpulse_list_chats
report = "*Daily report*\nAll good."[:4096]  # single asterisk = WhatsApp bold

# 3. Free text with the NESTED body (message.text.body, never a flat string)
resp, code = post("https://api.sendpulse.com/whatsapp/contacts/send",
                  {"contact_id": CONTACT,
                   "message": {"type": "text", "text": {"body": report}}}, token)

# 4. Window closed? Send the approved quick-reply template; a poller retries later.
if code == 422 and "24hours" in json.dumps(resp):
    post("https://api.sendpulse.com/whatsapp/contacts/sendTemplate",
         {"contact_id": CONTACT,
          "template": {"name": "<YOUR_APPROVED_TEMPLATE>",
                       "language": {"code": "he"}}}, token)
    print("window closed: template sent, retry free text after the button tap")
else:
    print(code, resp)
PY
```

## Common Mistakes

| Mistake | Rule / Fix |
|---|---|
| MCP send_message returns `422 "The given data was invalid"` | The API needs `message.text.body` nested; a flat `message.text` string always 422s. When in doubt, send via REST with the nested body |
| Retrying blind payload variations after a 422 | After two failed variations stop guessing; switch to direct REST with the documented payload |
| Free text fails `(#2) Contact is not active in 24hours` | The 24h service window is closed. Only an inbound USER message or button tap opens it. Send an approved template, or use the template + button + poller pattern |
| Assuming a template send opens the 24h window | It does not. Only user-initiated inbound activity opens the window |
| "Resource not found" on list_bots or any endpoint | Wrong base URL: use `https://api.sendpulse.com/whatsapp`, never `/chatbot/whatsapp`. Not a credentials problem |
| 422 on every send for one specific account | Check that the account's ID and secret are real values and not placeholders |
| Interactive list with more than 10 rows | WhatsApp hard limit: 10 rows total per list, sections included. Split into multiple lists by category or use two-step navigation |
| Capturing a user's choice with Sleep + "get last message" | Fragile anti-pattern that loses replies. End the sending scenario; Quick Reply / keyword trigger fires a webhook into a second scenario |
| Template send fails "Number of parameters does not match the expected number of params" | The template body has `{{1}}`, `{{2}}` placeholders. Inspect `GET /whatsapp/templates?bot_id=...` and send full `components` with one parameter per placeholder |
| 400 on sendTemplateByPhone | Wrong template name: names are case-sensitive, verify against `GET /whatsapp/templates?bot_id=...` |
| 422 from a Make `sendpulse:apiCall` module | Body type must be `json` (not `text`) and components must match the template structure |
| MCP set_contact_variable returns 422 | Use REST `POST /whatsapp/contacts/setVariable` with `{contact_id, variable_name, variable_value}`. The variable must also already exist at bot level (dashboard UI only; the API cannot create variables) |
| Contacts created without names | create_contact accepts only phone. Call set_contact_name immediately after, never "later" |
| Matching contacts by name | Names come from WhatsApp profiles and collide. Match by phone |
| Bulk send without human sign-off | Any send to more than one recipient requires explicit confirmation of account, audience size, template, and time |
| Marketing message without documented opt-in | Forbidden by Israeli law (tikun 40): up to 1,000 ILS exemplary damages per message. Cold outreach is never covered by the existing-customer exception |
| Bold rendered literally in WhatsApp | WhatsApp bold is a single asterisk: `*bold*`, not `**bold**` |
