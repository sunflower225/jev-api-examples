# Jev API Examples (Optio)

[![Website](https://img.shields.io/badge/Website-jevai.website-10b981)](https://jevai.website)
[![Playground](https://img.shields.io/badge/Playground-Free_to_try-34d399)](https://jevai.website/playground)
[![API Docs](https://img.shields.io/badge/Docs-v1%2Fsystemone-gray)](https://jevai.website/docs)
[![Pricing](https://img.shields.io/badge/Pricing-%2410%20%2F%20100k%20credits-gray)](https://jevai.website/pricing)

Copy-paste examples for calling the **Jev** decision model through **Optio**, an independently operated access gateway. Jev answers typed questions — `choice`, `score`, and yes/no (`noul`) — with calibrated probabilities. It does not write prose; that is the point.

> Optio is an independent gateway. It is not affiliated with, endorsed by, or an official product of TypeSafe. Jev is a trademark of its respective owner.

[中文说明](README.zh.md)

## What's here

| Path | What it shows |
|---|---|
| [`examples/curl.sh`](examples/curl.sh) | One yes/no decision with curl — the smallest useful request |
| [`examples/python.py`](examples/python.py) | Support triage: choice + score + yes/no in one request, with retry and confidence thresholds |
| [`examples/javascript.mjs`](examples/javascript.mjs) | Same triage shape in plain Node (no dependencies) |
| [`skills/jev/SKILL.md`](skills/jev/SKILL.md) | Installable agent skill — `npx skills add sunflower225/jev-api-examples` (or copy into your agent's skills directory) |

## Quick start (60 seconds)

```bash
# 1. Get a key: register at https://jevai.website — 5 free credits, no card needed
export JEV_API_KEY="jev_live_your_key"

# 2. Make your first decision
curl https://jevai.website/api/v1/systemone \
  -H "Authorization: Bearer $JEV_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "state": "The payments webhook failed twice overnight. Should I wake up the on-call engineer?",
    "questions": {
      "page": {
        "type": "noul",
        "instructions": "Should someone be paged right now?",
        "criteria": {
          "true": "Revenue-impacting or data loss",
          "false": "Can wait until morning"
        }
      }
    }
  }'
```

The response carries `answers` keyed by your question names, `usage.credits`, and `latency_ms`.

```json
{
  "request_id": "req_fe17d05411092c4f7f97947a",
  "model": "jev-1.13.0",
  "answers": { "page": { "type": "noul", "noul": 0.91 } },
  "usage": { "input_tokens": 128, "output_tokens": 21, "credits": 1 },
  "latency_ms": 432
}
```

## The mental model

- **`state`** — the ticket, form payload, or tool call the decision is about. String, array of strings, or JSON object; up to 100,000 characters.
- **`questions`** — 1 to 8 named questions. Answer space is declared up front (`choice`: 2–20 options; `score`: 2–10 levels), so output always fits your types.
- **Your code branches on `answers`** and on the probability — route, block, or ask a human by threshold. Jev judges; your policy stays in code.

Errors always return `{error: {code, message, request_id}}`. Retry `429` / `502` / `529` with backoff; never retry `401` / `402` / `422` unchanged.

## Cost

One credit covers 1,000 input tokens (minimum 1 credit per request; output tokens are free). A typical short decision costs 1 credit — $0.0001 on the $10 Starter pack. Credits never expire. Failed requests are not charged. [Full pricing →](https://jevai.website/pricing)

## Where to try it without a key

The [free playground](https://jevai.website/playground) runs the real model in the browser: 30 runs per day anonymously, 50 signed in. The JSON you see there is the JSON your server sends.

## Links

- Docs: https://jevai.website/docs
- Playground: https://jevai.website/playground
- Pricing: https://jevai.website/pricing
- Use cases: https://jevai.website/use-cases
- Support: support@jevai.website
