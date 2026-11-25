from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from utils import params
from utils.pinlyx_client import PinlyxClient

STAGES = ("novalue", "lead", "conversation", "proposal", "negotiation", "won", "lost")


class UpdateContactStageTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        contact_id = params.integer(tool_parameters.get("contact_id"), "contact_id", minimum=1)
        stage = (params.text(tool_parameters.get("stage")) or "").lower()
        if contact_id is None:
            raise ValueError("contact_id is required.")
        if stage not in STAGES:
            raise ValueError(f"stage must be one of: {', '.join(STAGES)}.")
        contact = PinlyxClient(self.runtime.credentials).post(
            f"/v1/contacts/{contact_id}/stage", {"stage": stage}
        )
        yield self.create_json_message(contact)
        yield self.create_text_message(f"Contact #{contact_id} is now in stage: {contact.get('stage')}.")
