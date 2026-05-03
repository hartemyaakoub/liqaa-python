"""Synchronous client for the LIQAA Public API."""

from __future__ import annotations

import base64
import hmac
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from hashlib import sha256
from typing import Any

DEFAULT_BASE_URL = "https://liqaa.io/api/public/v1"


class LiqaaError(Exception):
    """Raised on transport or HTTP errors from LIQAA."""


class LiqaaClient:
    """Server-side client. Authenticates with sk_live_… — never use in browsers."""

    def __init__(
        self,
        public_key: str,
        secret_key: str,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 8.0,
    ) -> None:
        if not public_key.startswith("pk_"):
            raise ValueError("public_key must start with pk_live_ or pk_test_")
        if not secret_key.startswith("sk_"):
            raise ValueError("secret_key must start with sk_live_ or sk_test_")
        self._pk = public_key
        self._sk = secret_key
        self._base = base_url
        self._timeout = timeout

    # ── Tokens ────────────────────────────────────────────────────────────

    def exchange_sdk_token(self, *, email: str, name: str | None = None) -> dict[str, Any]:
        """Sign an identity with sk_ and exchange for a 1-hour browser-safe JWT."""
        identity = json.dumps(
            {"email": email, "name": name, "ts": int(time.time())},
            ensure_ascii=False,
        ).encode("utf-8")
        identity_b64 = base64.b64encode(identity).decode("ascii")
        signature = hmac.new(self._sk.encode(), identity_b64.encode(), sha256).hexdigest()

        return self._post(
            "/sdk-token",
            {"public_key": self._pk, "identity_base64": identity_b64, "signature": signature},
        )

    # ── Conversations ─────────────────────────────────────────────────────

    def create_conversation(
        self,
        *,
        caller_email: str,
        caller_name: str | None = None,
        callee_email: str | None = None,
        callee_name: str | None = None,
        external_conversation_id: str | None = None,
        title: str | None = None,
    ) -> dict[str, Any]:
        body = {
            "caller_email": caller_email,
            "caller_name": caller_name,
            "callee_email": callee_email,
            "callee_name": callee_name,
            "external_conversation_id": external_conversation_id,
            "title": title,
        }
        return self._post("/conversations", {k: v for k, v in body.items() if v is not None})

    def get_conversation(self, conversation_id: str) -> dict[str, Any]:
        return self._request("GET", f"/conversations/{conversation_id}")

    def end_conversation(self, conversation_id: str) -> None:
        self._request("DELETE", f"/conversations/{conversation_id}")

    # ── Webhooks ──────────────────────────────────────────────────────────

    def create_webhook(
        self, url: str, events: list[str], *, description: str | None = None
    ) -> dict[str, Any]:
        body: dict[str, Any] = {"url": url, "events": events}
        if description is not None:
            body["description"] = description
        return self._post("/webhooks", body)

    def list_webhooks(self) -> list[dict[str, Any]]:
        return self._request("GET", "/webhooks")  # type: ignore[return-value]

    def delete_webhook(self, webhook_id: int) -> None:
        self._request("DELETE", f"/webhooks/{webhook_id}")

    # ── HTTP plumbing ─────────────────────────────────────────────────────

    def _post(self, path: str, body: dict[str, Any]) -> dict[str, Any]:
        return self._request("POST", path, body)

    def _request(
        self, method: str, path: str, body: dict[str, Any] | None = None
    ) -> Any:
        data: bytes | None = None
        if body is not None:
            data = json.dumps(body, ensure_ascii=False).encode("utf-8")

        req = urllib.request.Request(
            self._base + path,
            data=data,
            method=method,
            headers={
                "Authorization": f"Bearer {self._sk}",
                "Accept": "application/json",
                "Content-Type": "application/json",
                "User-Agent": "liqaa-python/1.0.0",
            },
        )

        try:
            with urllib.request.urlopen(req, timeout=self._timeout) as resp:
                raw = resp.read()
        except urllib.error.HTTPError as e:
            raise LiqaaError(f"LIQAA API error {e.code}: {e.read()[:300].decode(errors='replace')}") from e
        except urllib.error.URLError as e:
            raise LiqaaError(f"LIQAA request failed: {e.reason}") from e

        if not raw:
            return {}
        return json.loads(raw)
