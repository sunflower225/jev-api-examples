---
name: jev-gateway
description: Call the Optio decision API for typed choice, score, and yes/no judgments before routing, blocking, scoring, or gating an action. Use when the next step is an if/switch, not when the task is to write prose.
---

# Optio

Jev returns a typed decision with probabilities. You still decide whether to act.

## When to call it

Call it before routing work, blocking a tool, scoring a lead, moderating content, or checking whether a task is done. Do not call it to draft text, code, or summaries.

## Setup

Read these environment variables. Never print the key, write it into source, or send it to the browser.

- `JEV_API_KEY` — required. A key from the Optio dashboard. It looks like `jev_live_...`.
- `JEV_BASE_URL` — optional. Defaults to the hosted `/api/v1` base. Do not append `/systemone` here.
- `JEV_LANGUAGE` — optional. `en-US` or `zh-CN`. Use it only for what you tell the user. The API body stays in the language of the state.

If `JEV_API_KEY` is missing, stop and ask the user to create a key. Do not invent one.

## Request

`POST $JEV_BASE_URL/systemone`

```http
Authorization: Bearer $JEV_API_KEY
Content-Type: application/json
```

```json
{
  "state": "The deployment failed three times and production is returning 500s.",
  "questions": {
    "needs_human": {
      "type": "noul",
      "instructions": "Should this be escalated to a person?"
    },
    "team": {
      "type": "choice",
      "instructions": "Which team should handle this?",
      "criteria": {
        "infra": "Deployments, servers, outages",
        "billing": "Payments and invoices"
      }
    },
    "severity": {
      "type": "score",
      "instructions": "How severe is this incident?",
      "criteria": ["Low", "Medium", "Critical"]
    }
  }
}
```

Rules for the body:

- `state` is a string, an array of strings, or a JSON object. Keep it to the facts the questions need.
- One to eight questions. Names are identifiers (`needs_human`, not `Needs human`).
- `noul` is yes/no and returns `noul`, the probability the answer is yes.
- `choice` needs 2–20 options in `criteria`. It returns `choice`, `probabilities`, and `confidence`.
- `score` needs 2–10 levels, lowest first. It returns `score` (0 is the first level), `probabilities`, `legend`, and `confidence`.
- Do not add an option that was not in `criteria`.
- `model` is optional and ignored.

## Response

On success, branch on `answers`, not on free text. Keep `request_id` if you report a failure.

```json
{
  "request_id": "req_...",
  "model": "jev-1.13.0",
  "answers": {},
  "usage": { "credits": 4 },
  "latency_ms": 200
}
```

If `confidence` is low, or a `noul` value is near 0.5, do not take the irreversible action. Ask the user or apply a fixed rule.

## Errors

| HTTP | code | What you do |
| --- | --- | --- |
| 401 | missing_api_key, invalid_api_key | Stop. The key is missing or revoked. |
| 402 | insufficient_credits | Stop. The workspace needs more credits. |
| 422 | invalid_request | Fix the body. Do not retry the same JSON. |
| 429 | rate_limited | Wait for `Retry-After`, then retry. |
| 502 | upstream_error | Retry once with backoff. |
| 529 | upstream_overloaded | Retry once with backoff. |

Failed requests are not charged. Do not retry 401, 402, or 422 without changing the request.
