---
title: Webhooks
description: Sync billing and subscriptions with Stripe webhooks.
order: 2
lang: en
---

PolyScript integrates with Stripe for billing. Configure webhooks to keep subscriptions in sync.

## Setup

1. Create a webhook endpoint in Stripe
2. Set the URL to `https://api.polyscript.io/v1/webhooks/stripe`
3. Select events: `customer.subscription.created`, `customer.subscription.updated`, `customer.subscription.deleted`

## Signature verification

All webhook requests include a signature header. Verify it with your webhook secret:

```python
import hmac
import hashlib

def verify_signature(payload, signature, secret):
    expected = hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(signature, expected)
```

## Event handling

- `subscription.created` — Create subscription record, set plan limits
- `subscription.updated` — Update plan, adjust limits
- `subscription.deleted` — Downgrade to free, notify user

All events are idempotent — replaying them won't cause duplicate charges or state issues.
