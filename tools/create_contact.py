from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from utils import params
from utils.pinlyx_client import PinlyxClient


class CreateContactTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        body = params.drop_empty(
            {
                "name": params.text(tool_parameters.get("name")),
                "username": params.text(tool_parameters.get("username")),
                "phone": params.text(tool_parameters.get("phone")),
                "email": params.text(tool_parameters.get("email")),
                "company": params.text(tool_parameters.get("company")),
                "externalId": params.text(tool_parameters.get("external_id")),
                "notes": params.text(tool_parameters.get("notes")),
                "stage": params.text(tool_parameters.get("stage")),
                "tags": params.csv_list(tool_parameters.get("tags")),
            }
        )
        identifying = ("name", "username", "phone", "email", "externalId")
        if not any(key in body for key in identifying):
            raise ValueError("Provide at least one of name, username, phone, email or external_id.")
        contact = PinlyxClient(self.runtime.credentials).post("/v1/contacts", body)
        yield self.create_json_message(contact)
        yield self.create_text_message(f"Created contact #{contact['id']} (stage: {contact.get('stage')}).")
