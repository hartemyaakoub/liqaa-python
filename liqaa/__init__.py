"""LIQAA — drop-in video calls and messaging for any website.

Server-side Python SDK for the LIQAA Public API.

>>> from liqaa import LiqaaClient
>>> client = LiqaaClient(public_key="pk_live_...", secret_key="sk_live_...")
>>> token = client.exchange_sdk_token(email="user@example.com", name="User")
>>> token["sdk_token"]  # 1-hour JWT — pass to the browser
"""

from .client import LiqaaClient
from .webhook import WebhookVerifier

__all__ = ["LiqaaClient", "WebhookVerifier"]
__version__ = "1.0.0"
