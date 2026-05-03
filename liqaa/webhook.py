"""Webhook signature verification for LIQAA."""

from __future__ import annotations

import hmac
import time
from hashlib import sha256


class WebhookVerifier:
    """Verify HMAC-SHA256 signed webhook deliveries from LIQAA.

    Header format: ``X-LIQAA-Signature: t=<unix_ts>,v1=<hex_hmac>``
    HMAC is computed over ``f"{timestamp}.{raw_body}"``.
    """

    def __init__(self, signing_secret: str, *, replay_window_seconds: int = 300) -> None:
        if not signing_secret:
            raise ValueError("signing_secret is required")
        self._secret = signing_secret.encode()
        self._replay_window = replay_window_seconds

    def verify(self, raw_body: bytes, signature_header: str) -> bool:
        """Return True iff the signature is valid AND the timestamp is fresh."""
        parsed = self._parse_header(signature_header)
        if parsed is None:
            return False
        timestamp, received = parsed

        if abs(int(time.time()) - timestamp) > self._replay_window:
            return False

        expected = hmac.new(
            self._secret,
            f"{timestamp}.".encode() + raw_body,
            sha256,
        ).hexdigest()
        return hmac.compare_digest(expected, received)

    @staticmethod
    def _parse_header(header: str) -> tuple[int, str] | None:
        if not header:
            return None
        parts: dict[str, str] = {}
        for segment in header.split(","):
            segment = segment.strip()
            if "=" not in segment:
                continue
            k, v = segment.split("=", 1)
            parts[k.strip()] = v.strip()
        try:
            return int(parts["t"]), parts["v1"]
        except (KeyError, ValueError):
            return None
