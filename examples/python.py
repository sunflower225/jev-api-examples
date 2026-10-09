#!/usr/bin/env python3
"""Support triage through the Jev API (Optio gateway).

One request carries three questions: routing (choice), frustration (score)
and page-the-oncall (yes/no). Billing is per input token, so batching
questions is free until the 1,000-token ceiling.

Usage:
    export JEV_API_KEY="jev_live_your_key"
    python3 examples/python.py
"""

import os
import sys
import time

import requests  # pip install requests

URL = "https://jevai.website/api/v1/systemone"

# Thresholds are policy, and policy lives in your code, not in the model.
PAGE_CONFIDENCE = 0.8
REVIEW_CONFIDENCE = 0.6

TICKETS = [
    "Help! My payouts have been failing for 3 days and my customers keep emailing.",
    "Hi, small typo on the pricing page I thought you should know about.",
    "Need invoice INV-2041 resent today, finance is blocking our renewal.",
]


def decide(ticket: str) -> dict:
    body = {
        "state": ticket,
        "questions": {
            "department": {
                "type": "choice",
                "instructions": "Which team should handle this?",
                "criteria": {
                    "billing": "Payments, payouts, invoicing, refunds",
                    "technical": "Bugs, outages, integrations",
                    "sales": "Pricing, upgrades, new accounts",
                },
            },
            "frustration": {
                "type": "score",
                "instructions": "How frustrated is the customer?",
                "criteria": ["Calm", "Frustrated", "Very angry"],
            },
            "page": {
                "type": "noul",
                "instructions": "Should someone be paged right now?",
                "criteria": {
                    "true": "Revenue-impacting or data loss",
                    "false": "Can wait until morning",
                },
            },
        },
    }
    headers = {"Authorization": f"Bearer {os.environ['JEV_API_KEY']}"}

    for attempt in range(4):
        resp = requests.post(URL, headers=headers, json=body, timeout=30)
        # Retry only transport/rate problems; never 401/402/422.
        if resp.status_code in (429, 502, 529):
            retry_after = int(resp.headers.get("Retry-After", 2 ** attempt))
            print(f"  retrying in {retry_after}s (HTTP {resp.status_code})")
            time.sleep(min(retry_after, 8))
            continue
        resp.raise_for_status()
        return resp.json()

    raise RuntimeError("upstream kept failing; degrade to a human queue")


def act(answer: dict) -> str:
    route = answer["answers"]["department"]
    page = answer["answers"]["page"]["noul"]
    if page >= PAGE_CONFIDENCE:
        return "page on-call, else queue later"
    department = route["choice"]
    confidence = min(route["probabilities"].values())
    if confidence < REVIEW_CONFIDENCE:
        return f"low confidence ({confidence:.2f}) -> senior queue with both teams"
    return f"enqueue to {department}"


if __name__ == "__main__":
    if "JEV_API_KEY" not in os.environ:
        sys.exit("Set JEV_API_KEY first — create one at https://jevai.website")
    for ticket in TICKETS:
        result = decide(ticket)
        print(f"ticket : {ticket[:60]}...")
        print(f"answers: {result['answers']}")
        print(f"charge : {result['usage']['credits']} credit(s), {result['latency_ms']} ms")
        print(f"action : {act(result)}")
        print()
