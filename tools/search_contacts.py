from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from utils import params
from utils.pinlyx_client import PinlyxClient


class SearchContactsTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        query = params.drop_empty(
            {
                "q": params.text(tool_parameters.get("query")),
                "email": params.text(tool_parameters.get("email")),
                "externalId": params.text(tool_parameters.get("external_id")),
                "limit": params.integer(tool_parameters.get("limit"), "limit", minimum=1, maximum=100) or 10,
                "after": params.integer(tool_parameters.get("after"), "after", minimum=1),
            }
        )
        result = PinlyxClient(self.runtime.credentials).get("/v1/contacts", params=query)
        items = result.get("items", [])
        lines = [f"Found {len(items)} contact(s)" + (" (more available)." if result.get("hasMore") else ".")]
        for c in items:
            who = c.get("name") or c.get("username") or c.get("email") or c.get("phone") or "unnamed"
            lines.append(f"- #{c['id']} {who} | stage: {c.get('stage')} | platform: {c.get('platform')}")
        yield self.create_json_message(result)
        yield self.create_text_message("\n".join(lines))
