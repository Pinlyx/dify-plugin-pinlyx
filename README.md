# Pinlyx for Dify

Let Dify workflows and agents search, create and update contacts, deals and tasks in your [Pinlyx](https://pinlyx.com/?utm_source=github&utm_medium=readme&utm_campaign=dify-plugin-pinlyx) CRM.

Source: https://github.com/Pinlyx/dify-plugin-pinlyx

## What you can do

| Tool | What it does | Pinlyx endpoint |
| --- | --- | --- |
| Search contacts | Free-text, exact email or external ID lookup, paged | `GET /v1/contacts` |
| Get contact | One contact with stage, score, custom fields and tags | `GET /v1/contacts/{id}` |
| Create contact | New contact with optional stage and tags | `POST /v1/contacts` |
| Update contact stage | Move a contact along the sales pipeline | `POST /v1/contacts/{id}/stage` |
| List deals | Filter by stage, contact or title, paged | `GET /v1/deals` |
| Create deal | New deal, optionally linked to a contact | `POST /v1/deals` |
| Create task | Follow-up task, optionally linked to a contact or deal | `POST /v1/tasks` |

Typical uses: an inbound-lead workflow that creates the contact and a follow-up task, a support agent that looks up the customer and their open deals before answering, or a nightly flow that moves contacts to a new stage.

## Setup

1. You need a Pinlyx workspace on the Business plan (the public REST API is part of that plan).
2. In the Pinlyx panel create an API key. Keys look like `csk_live_...`. Give it the scopes the tools need: `contacts:read`, `contacts:write`, `deals:read`, `deals:write`, `tasks:write`.
3. In Dify open Plugins, install this plugin, then open its authorization settings and paste the key into **API key**.
4. Leave **Workspace ID** empty unless your key belongs to a member of several shared workspaces and you want a specific one (it is sent as the `X-Workspace-Id` header).

Saving the credentials calls `GET /v1/me`, a read that only proves the key works.

## Credentials and connection

- Credential: one Pinlyx API key (secret). It is sent as the `X-Api-Key` header. The API also accepts `Authorization: Bearer csk_live_...`.
- Connection: the plugin only talks to `https://api.pinlyx.com` over HTTPS. The host is fixed and cannot be changed from the UI, so the key is never sent anywhere else.
- Rate limits and plan limits are enforced by Pinlyx. A rejected call surfaces the API message in the Dify node error, for example `Pinlyx API error 403 (forbidden): ...`.

## Usage notes

- IDs are numeric Pinlyx IDs. Use Search contacts first, then pass the returned `id` to the other tools.
- Paging: list tools return `nextCursor` and `hasMore`. Pass the cursor as **After ID** to get the next page.
- Contact stages: `novalue`, `lead`, `conversation`, `proposal`, `negotiation`, `won`, `lost`.
- Deal stages when creating: `lead`, `qualified`, `proposal`, `negotiation`. A deal cannot be created as won or lost through the API.
- Task priority: `low`, `medium`, `high`. Dates are ISO 8601, for example `2026-12-01T09:00:00Z`.
- Create contact fails with a conflict when the external ID is already used in the workspace.
- Write tools change real CRM data. In agents, only enable the ones you want the model to call.

## Development

```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt pytest
python -m pytest tests
```

The tests replace the HTTP layer, so they never call the live API. To package: `dify plugin package ./dify-plugin-pinlyx` with the [Dify plugin CLI](https://github.com/langgenius/dify-plugin-daemon/releases).

## Privacy

See [PRIVACY.md](PRIVACY.md) and https://pinlyx.com/privacy.

## License

MIT, see [LICENSE](LICENSE).

Built and maintained by [Pinlyx](https://pinlyx.com/?utm_source=github&utm_medium=readme&utm_campaign=dify-plugin-pinlyx), an omnichannel inbox and AI agent with a built-in CRM for Telegram, WhatsApp, Instagram, Messenger, X, email and live chat.
