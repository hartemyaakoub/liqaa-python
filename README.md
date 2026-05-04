<div align="center">

# LIQAA Python SDK

**Server-side Python client for the LIQAA Public API.**

[![pypi version](https://img.shields.io/pypi/v/liqaa.svg?style=flat-square&color=1d4ed8)](https://pypi.org/project/liqaa)
[![python](https://img.shields.io/badge/python-%3E%3D3.9-3776ab?style=flat-square)](https://python.org)
[![license](https://img.shields.io/badge/license-MIT-475569.svg?style=flat-square)](./LICENSE)
[![docs](https://img.shields.io/badge/docs-liqaa.io-1d4ed8.svg?style=flat-square)](https://liqaa.io/docs)

[Website](https://liqaa.io) · [Docs](https://liqaa.io/docs) · [JS SDK](https://github.com/hartemyaakoub/liqaa-js)

</div>

---

## Install

```bash
pip install liqaa
```

Pure-Python, zero dependencies (uses stdlib `urllib` + `hmac`). Python 3.9+.

## Quick start

### Exchange identity → JWT

```python
from liqaa import LiqaaClient

client = LiqaaClient(public_key=os.environ["LIQAA_PK"], secret_key=os.environ["LIQAA_SK"])

token = client.exchange_sdk_token(email="visitor@example.com", name="Anonymous Visitor")
print(token["sdk_token"]) # → tkc_eyJhbGciOi…
```

### Create a persistent room

```python
conv = client.create_conversation(
 caller_email="agent@yoursite.com",
 callee_email="customer@example.com",
 external_conversation_id="ticket-42",
)
print(conv["join_url"]) # → https://liqaa.io/meeting/room-abc123
```

### Verify a webhook

```python
from liqaa import WebhookVerifier
from flask import Flask, request, abort

verifier = WebhookVerifier(os.environ["LIQAA_WEBHOOK_SECRET"])
app = Flask(__name__)

@app.post("/webhooks/liqaa")
def handle():
 sig = request.headers.get("X-LIQAA-Signature", "")
 if not verifier.verify(request.get_data(), sig):
 abort(401)
 event = request.get_json()
# event["event"] == "call.started" / "call.ended" / etc.
 return "", 204
```

## Async support

```python
from liqaa.aio import AsyncLiqaaClient

async def main():
 client = AsyncLiqaaClient(public_key=..., secret_key=...)
 conv = await client.create_conversation(caller_email="a@b.com", callee_email="c@d.com")
```

## Frameworks

- **Flask** — see [`examples/flask`](./examples/flask)
- **Django** — see [`examples/django`](./examples/django)
- **FastAPI** — see [`examples/fastapi`](./examples/fastapi)

## License

[MIT](./LICENSE) © TKAWEN — LIQAA Cloud.
