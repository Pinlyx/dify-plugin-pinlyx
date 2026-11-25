from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from utils import params
from utils.pinlyx_client import PinlyxClient


class CreateTaskTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        title = params.text(tool_parameters.get("title"))
        if title is None:
            raise ValueError("title is required.")
        body = params.drop_empty(
            {
                "title": title,
                "description": params.text(tool_parameters.get("description")),
                "contactId": params.integer(tool_parameters.get("contact_id"), "contact_id", minimum=1),
                "dealId": params.integer(tool_parameters.get("deal_id"), "deal_id", minimum=1),
                "priority": params.text(tool_parameters.get("priority")),
                "dueAt": params.text(tool_parameters.get("due_at")),
            }
        )
        task = PinlyxClient(self.runtime.credentials).post("/v1/tasks", body)
        yield self.create_json_message(task)
        yield self.create_text_message(
            f"Created task #{task['id']} '{task.get('title')}' (priority: {task.get('priority')})."
        )
