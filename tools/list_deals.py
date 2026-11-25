from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from utils import params
from utils.pinlyx_client import PinlyxClient


class ListDealsTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        query = params.drop_empty(
            {
                "stage": params.text(tool_parameters.get("stage")),
                "contactId": params.integer(tool_parameters.get("contact_id"), "contact_id", minimum=1),
                "q": params.text(tool_parameters.get("query")),
                "limit": params.integer(tool_parameters.get("limit"), "limit", minimum=1, maximum=100) or 10,
                "after": params.integer(tool_parameters.get("after"), "after", minimum=1),
            }
        )
        result = PinlyxClient(self.runtime.credentials).get("/v1/deals", params=query)
        items = result.get("items", [])
        lines = [f"Found {len(items)} deal(s)" + (" (more available)." if result.get("hasMore") else ".")]
        for d in items:
            lines.append(
                f"- #{d['id']} {d.get('title')} | {d.get('value')} {d.get('currency')} | stage: {d.get('stage')}"
            )
        yield self.create_json_message(result)
        yield self.create_text_message("\n".join(lines))
