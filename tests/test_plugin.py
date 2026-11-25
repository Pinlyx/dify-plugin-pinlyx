"""Offline tests: the HTTP layer is replaced, no call ever leaves the machine."""

import importlib
import sys
from pathlib import Path

import pytest
import requests

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from dify_plugin.entities.tool import ToolRuntime  # noqa: E402
from dify_plugin.errors.tool import ToolProviderCredentialValidationError  # noqa: E402

from utils.pinlyx_client import BASE_URL, PinlyxApiError, PinlyxClient  # noqa: E402

FAKE_KEY = "csk_live_" + "x" * 44  # shape only, not a real key


class FakeResponse:
    def __init__(self, status=200, body=None):
        self.status_code = status
        self._body = body
        self.content = b"" if body is None else b"x"
        self.text = str(body)

    def json(self):
        if self._body is None:
            raise ValueError("no body")
        return self._body


class Calls(list):
    """Recorded requests; `.queue` holds the canned responses."""

    def __init__(self):
        super().__init__()
        self.queue = []


@pytest.fixture
def calls(monkeypatch):
    recorded = Calls()
    queue = recorded.queue

    def fake_request(self, method, url, **kwargs):
        recorded.append({"method": method, "url": url, **kwargs})
        return queue.pop(0) if queue else FakeResponse(200, {})

    monkeypatch.setattr(requests.Session, "request", fake_request)
    return recorded


def run_tool(module, cls, tool_parameters, credentials=None):
    mod = importlib.import_module(f"tools.{module}")
    runtime = ToolRuntime(credentials=credentials or {"api_key": FAKE_KEY}, user_id="u", session_id="s")
    tool = getattr(mod, cls)(runtime=runtime, session=None)
    return list(tool._invoke(tool_parameters))


def test_client_sends_key_and_workspace_headers(calls):
    PinlyxClient({"api_key": FAKE_KEY, "workspace_id": " 7 "}).get("/v1/me")
    sent = calls[0]
    assert sent["url"] == f"{BASE_URL}/v1/me"
    assert sent["headers"]["X-Api-Key"] == FAKE_KEY
    assert sent["headers"]["X-Workspace-Id"] == "7"


def test_client_requires_key():
    with pytest.raises(ValueError):
        PinlyxClient({"api_key": "  "})


def test_client_maps_error_envelope(calls):
    calls.queue.append(FakeResponse(409, {"error": "conflict", "message": "externalId exists"}))
    with pytest.raises(PinlyxApiError) as err:
        PinlyxClient({"api_key": FAKE_KEY}).post("/v1/contacts", {"name": "A"})
    assert err.value.status == 409 and err.value.code == "conflict"
    assert "externalId exists" in str(err.value)


def test_search_contacts_query(calls):
    calls.queue.append(FakeResponse(200, {"items": [{"id": 5, "name": "Ada", "stage": "Lead", "platform": "Telegram"}], "hasMore": False}))
    out = run_tool("search_contacts", "SearchContactsTool", {"query": " ada ", "limit": 5.0})
    assert calls[0]["method"] == "GET" and calls[0]["url"].endswith("/v1/contacts")
    assert calls[0]["params"] == {"q": "ada", "limit": 5}
    assert "#5 Ada" in out[1].message.text


def test_get_contact(calls):
    calls.queue.append(FakeResponse(200, {"id": 9, "name": "Bo", "stage": "Lead", "tags": [{"id": 1, "name": "vip"}]}))
    out = run_tool("get_contact", "GetContactTool", {"contact_id": 9})
    assert calls[0]["url"].endswith("/v1/contacts/9")
    assert "vip" in out[1].message.text


def test_create_contact_payload(calls):
    calls.queue.append(FakeResponse(201, {"id": 11, "stage": "Lead"}))
    run_tool("create_contact", "CreateContactTool", {"name": "Cy", "email": "cy@example.com", "tags": "vip, webinar,", "external_id": "ext-1"})
    sent = calls[0]
    assert sent["method"] == "POST" and sent["url"].endswith("/v1/contacts")
    assert sent["json"] == {"name": "Cy", "email": "cy@example.com", "externalId": "ext-1", "tags": ["vip", "webinar"]}


def test_create_contact_needs_an_identifier(calls):
    with pytest.raises(ValueError):
        run_tool("create_contact", "CreateContactTool", {"company": "Acme"})
    assert calls == []


def test_update_contact_stage(calls):
    calls.queue.append(FakeResponse(200, {"id": 3, "stage": "Proposal"}))
    run_tool("update_contact_stage", "UpdateContactStageTool", {"contact_id": 3, "stage": "Proposal"})
    assert calls[0]["url"].endswith("/v1/contacts/3/stage")
    assert calls[0]["json"] == {"stage": "proposal"}


def test_update_contact_stage_rejects_unknown_stage(calls):
    with pytest.raises(ValueError):
        run_tool("update_contact_stage", "UpdateContactStageTool", {"contact_id": 3, "stage": "hot"})
    assert calls == []


def test_list_deals_filters(calls):
    calls.queue.append(FakeResponse(200, {"items": [{"id": 1, "title": "Big", "value": 10, "currency": "USD", "stage": "Lead"}], "hasMore": True}))
    out = run_tool("list_deals", "ListDealsTool", {"stage": "lead", "contact_id": 4})
    assert calls[0]["params"] == {"stage": "lead", "contactId": 4, "limit": 10}
    assert "more available" in out[1].message.text


def test_create_deal_payload(calls):
    calls.queue.append(FakeResponse(201, {"id": 2, "title": "Renewal", "stage": "Lead"}))
    run_tool("create_deal", "CreateDealTool", {"title": "Renewal", "value": 1200, "currency": "usd", "probability": 40.0, "contact_id": 4})
    assert calls[0]["url"].endswith("/v1/deals")
    assert calls[0]["json"] == {"title": "Renewal", "contactId": 4, "value": 1200.0, "currency": "usd", "probability": 40}


def test_create_task_payload(calls):
    calls.queue.append(FakeResponse(201, {"id": 8, "title": "Call", "priority": "High"}))
    run_tool("create_task", "CreateTaskTool", {"title": "Call", "priority": "high", "deal_id": 2, "due_at": "2026-12-01T09:00:00Z"})
    assert calls[0]["url"].endswith("/v1/tasks")
    assert calls[0]["json"] == {"title": "Call", "dealId": 2, "priority": "high", "dueAt": "2026-12-01T09:00:00Z"}


def test_provider_validate_ok_and_rejected(calls):
    from provider.pinlyx import PinlyxProvider

    provider = PinlyxProvider()
    calls.queue.append(FakeResponse(200, {"id": 1}))
    provider._validate_credentials({"api_key": FAKE_KEY})
    assert calls[0]["url"].endswith("/v1/me")

    calls.queue.append(FakeResponse(401, {"error": "unauthorized", "message": "bad key"}))
    with pytest.raises(ToolProviderCredentialValidationError):
        provider._validate_credentials({"api_key": FAKE_KEY})
    with pytest.raises(ToolProviderCredentialValidationError):
        provider._validate_credentials({"api_key": ""})
