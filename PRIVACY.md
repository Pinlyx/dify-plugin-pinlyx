# Privacy Policy

Plugin: Pinlyx for Dify. Author: pinlyx. Contact: support@pinlyx.com.

The full Pinlyx privacy policy is at https://pinlyx.com/privacy. This page describes what this plugin does with data.

## What the plugin collects and stores

The plugin itself does not collect, store, log or retain any user data. It has no database, no analytics and no telemetry. Everything it does happens inside a single tool call and is discarded when the call ends.

The Pinlyx API key you enter as a credential is stored by Dify (encrypted credential storage), not by this plugin.

## What is sent to Pinlyx

The plugin sends data only to `https://api.pinlyx.com`, the API of the Pinlyx service that you chose to connect. Nothing is sent to any other third party.

For each tool call, the following goes to Pinlyx:

- Your API key (header `X-Api-Key`) and, if you set one, the Workspace ID (header `X-Workspace-Id`).
- The tool inputs you or your workflow provide, as request parameters or a JSON body:
  - Search contacts: search text, email, external ID, paging values.
  - Get contact, Update contact stage: contact ID and the new stage.
  - Create contact: name, username, phone, email, company, external ID, notes, stage, tags. This can be personal data about your own customers or leads.
  - List deals, Create deal: stage, contact ID, title text, value, currency, probability, expected close date, notes.
  - Create task: title, description, contact ID, deal ID, priority, due date.
- The credential check when you save the key calls `GET /v1/me`, which sends only the key.

Pinlyx processes this data as your CRM provider, under its own privacy policy. Data returned by Pinlyx (contacts, deals, tasks) is passed to your Dify workflow or agent, and from there to whatever other nodes or models you connect. Review those flows with your own privacy obligations in mind.

## Errors and logging

Error messages from the Pinlyx API are shown in the Dify node result. The plugin does not write the API key into errors or logs.

## Contact

Questions or deletion requests about data held in Pinlyx: support@pinlyx.com. See https://pinlyx.com/privacy for details.
