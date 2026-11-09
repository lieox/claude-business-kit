# SendPulse WhatsApp REST Recipes

All endpoints relative to `https://api.sendpulse.com`. WhatsApp base is `/whatsapp` (never `/chatbot/whatsapp`). Every recipe below has been verified in production unless marked otherwise.

## 1. Credentials and OAuth

Credentials: `SENDPULSE_CLIENT_ID` and `SENDPULSE_CLIENT_SECRET`, read from environment variables at runtime.

Never print or hardcode the values.

Token (expires; fetch fresh per run):

```bash
curl -s -X POST https://api.sendpulse.com/oauth/access_token \
  -H 'Content-Type: application/json' \
  -d '{"grant_type":"client_credentials","client_id":"<ID>","client_secret":"<SECRET>"}'
# -> {"access_token":"...", ...}
```

All subsequent calls: header `Authorization: Bearer <access_token>`.

## 2. Free text send (requires open 24h service window)

```bash
curl -s -X POST https://api.sendpulse.com/whatsapp/contacts/send \
  -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  -d '{"contact_id":"<CONTACT_ID>","message":{"type":"text","text":{"body":"<MSG>"}}}'
```

- The nested `message.text.body` shape is mandatory. Flat `message.text` string = 422 "The given data was invalid".
- Success: 200 with `success:true`. Inside an open service window the conversation is free (price 0).
- Window closed: `422 {"errors":{"contact_id":["(#2) Contact is not active in 24hours"]}}`.
- WhatsApp formatting: bold = single asterisk `*bold*`.
- Cap body at 4096 characters.
- Media variant: `message.type` set to the media type with `{"<type>":{"link":"<URL>"}}` in place of `text`.

## 3. Template send by contact_id (allowed any time)

```bash
curl -s -X POST https://api.sendpulse.com/whatsapp/contacts/sendTemplate \
  -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  -d '{"contact_id":"<CONTACT_ID>","template":{"name":"<TEMPLATE_NAME>","language":{"code":"he"}}}'
```


## 4. Template send by phone, with variables and image header

Endpoint: `POST /whatsapp/contacts/sendTemplateByPhone`

If the template body contains `{{1}}`, `{{2}}`, ... you MUST pass matching `components`, otherwise: "Number of parameters does not match the expected number of params".

```json
{
  "bot_id": "<BOT_ID>",
  "phone": "972XXXXXXXXX",
  "template": {
    "name": "template_name",
    "language": { "code": "he" },
    "components": [
      {
        "type": "header",
        "parameters": [{ "type": "image", "image": { "link": "<IMAGE_URL>" } }]
      },
      {
        "type": "body",
        "parameters": [
          { "type": "text", "text": "value for {{1}}" },
          { "type": "text", "text": "value for {{2}}" }
        ]
      }
    ]
  }
}
```

Error mapping (verified):
- 404: wrong path (`/chatbot/whatsapp/...` does not exist; must be `/whatsapp/...`).
- 400: wrong template name (case-sensitive; verify with recipe 5).
- 422: in Make, body type set to `text` instead of `json`; or components do not match the template.

## 5. List templates (structure, status, language)

```bash
curl -s "https://api.sendpulse.com/whatsapp/templates?bot_id=<BOT_ID>" \
  -H "Authorization: Bearer $TOKEN"
```

Returns every template with status, language, and full components structure. Always check here before sending a parameterized template.

## 6. Interactive list (hard limit: 10 rows total)

Endpoint: `POST /whatsapp/contacts/sendByContact` (used via Make `sendpulse:apiCall` in production; body shape below).

WhatsApp allows at most 10 rows per list, even across multiple sections. More options than 10: split into multiple lists by category, or two-step navigation (category list, then items list).

```json
{
  "contact_id": "<CONTACT_ID>",
  "message": {
    "type": "interactive",
    "interactive": {
      "type": "list",
      "body": { "text": "איזה מקצוע אתה מחפש?" },
      "action": {
        "button": "בחר מקצוע",
        "sections": [{
          "title": "בנייה וגמר",
          "rows": [
            { "id": "<ROW_ID>", "title": "בנאי" },
            { "id": "<ROW_ID>", "title": "נגר" }
          ]
        }]
      }
    }
  }
}
```

Convention: `row.id` = the backing record id (e.g. Airtable record id), `row.title` = display name.

Handling the reply: the sending scenario ends after this call. A SendPulse flow/trigger wired in the dashboard UI to the list reply posts a webhook (e.g. to Make) with the contact and the chosen row. Never poll with Sleep + "get last message".

## 7. Set contact variable (REST only; the MCP tool 422s)

```bash
curl -s -X POST https://api.sendpulse.com/whatsapp/contacts/setVariable \
  -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  -d '{"contact_id":"<CONTACT_ID>","variable_name":"language","variable_value":"Arabic"}'
```

- The variable must already exist at bot level; check MCP `sendpulse_list_variables`. Missing variables can only be created in the SendPulse dashboard UI (`setVariable` on a non-existent variable returns "Variable does not exist").
- Verified at scale (37/37 contacts, zero failures).

## 8. Contact and chat lookups

- Find contact_id: MCP `sendpulse_list_chats` (this tool works fine).
- Contact details: `GET /whatsapp/contacts/get?id=<CONTACT_ID>`. A second documented variant for details including variables: `GET /chatsbot/contacts/<CONTACT_ID>`.
- Recent messages (also used to check whether the 24h window is open, and inside Make flows):

```bash
curl -s "https://api.sendpulse.com/whatsapp/chats/messages?contact_id=<CONTACT_ID>&size=50" \
  -H "Authorization: Bearer $TOKEN"
```

- Set name after creation: MCP `sendpulse_set_contact_name` (endpoint `POST /contacts/setName`).
- `POST /whatsapp/contacts/sendByPhone` exists as a documented send-by-phone endpoint; its exact body shape is not locally verified, prefer the contact_id routes above.

## 9. Make.com apiCall specifics

When calling SendPulse from a Make `sendpulse:apiCall` module:
- URL is the path only, e.g. `/whatsapp/contacts/sendTemplateByPhone`.
- Body type MUST be `json`, not `text` (422 otherwise).
- Identifying which button/message a user tapped inside a Make flow:
  - Tapped message id: `{{1.last_message_data.message.context.message_id}}`
  - After an Iterator over messages: filter `{{7.message_id}}` equals the context message_id above.

## 10. Your identifiers

Fill these in once, so every session uses the same values:

| What | Value |
|---|---|
| Bot ID | `<from sendpulse_list_bots>` |
| Approved templates | `<name>`, language `he`, category |
| Poller script for business-initiated reports | `<path>` |
