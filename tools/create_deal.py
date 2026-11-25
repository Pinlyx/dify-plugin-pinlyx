from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from utils import params
from utils.pinlyx_client import PinlyxClient


class CreateDealTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        title = params.text(tool_parameters.get("title"))
        if title is None:
            raise ValueError("title is required.")
        body = params.drop_empty(
            {
                "title": title,
                "contactId": params.integer(tool_parameters.get("contact_id"), "contact_id", minimum=1),
                "value": params.number(tool_parameters.get("value"), "value"),
                "currency": params.text(tool_parameters.get("currency")),
                "stage": params.text(tool_parameters.get("stage")),
                "probability": params.integer(
                    tool_parameters.get("probability"), "probability", minimum=0, maximum=100
                ),
                "expectedCloseAt": params.text(tool_parameters.get("expected_close_at")),
                "notes": params.text(tool_parameters.get("notes")),
            }
        )
        deal = PinlyxClient(self.runtime.credentials).post("/v1/deals", body)
        yield self.create_json_message(deal)
        yield self.create_text_message(
            f"Created deal #{deal['id']} '{deal.get('title')}' (stage: {deal.get('stage')})."
        )
