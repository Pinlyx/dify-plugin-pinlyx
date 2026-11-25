from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from utils import params
from utils.pinlyx_client import PinlyxClient


class GetContactTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        contact_id = params.integer(tool_parameters.get("contact_id"), "contact_id", minimum=1)
        if contact_id is None:
            raise ValueError("contact_id is required.")
        contact = PinlyxClient(self.runtime.credentials).get(f"/v1/contacts/{contact_id}")
        who = contact.get("name") or contact.get("username") or contact.get("email") or "unnamed"
        tags = ", ".join(t["name"] for t in (contact.get("tags") or [])) or "none"
        yield self.create_json_message(contact)
        yield self.create_text_message(
            f"Contact #{contact['id']} {who} | stage: {contact.get('stage')} | tags: {tags}"
        )
