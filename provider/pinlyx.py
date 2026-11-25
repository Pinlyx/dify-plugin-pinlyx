from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError

from utils.pinlyx_client import PinlyxApiError, PinlyxClient


class PinlyxProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        api_key = (credentials.get("api_key") or "").strip()
        if not api_key:
            raise ToolProviderCredentialValidationError("API key is required.")
        try:
            # GET /v1/me is a cheap read that needs no scope: it only proves the key works.
            PinlyxClient(credentials).get("/v1/me")
        except PinlyxApiError as err:
            if err.status in (401, 403):
                raise ToolProviderCredentialValidationError(
                    "Pinlyx rejected this API key. Check the key and that the workspace is on the Business plan."
                ) from err
            raise ToolProviderCredentialValidationError(str(err)) from err
        except Exception as err:  # network errors, timeouts
            raise ToolProviderCredentialValidationError(f"Could not reach Pinlyx: {err}") from err
