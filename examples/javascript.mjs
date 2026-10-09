#!/usr/bin/env node
// Same support-triage decision as python.py, in plain Node — no dependencies.
//
//   export JEV_API_KEY="jev_live_your_key"
//   node examples/javascript.mjs
//
// Get a key: https://jevai.website -> sign up -> dashboard -> create API key.

const URL = "https://jevai.website/api/v1/systemone";
const PAGE_CONFIDENCE = 0.8;
const REVIEW_CONFIDENCE = 0.6;

async function decide(state) {
  const resp = await fetch(URL, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${process.env.JEV_API_KEY}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      state,
      questions: {
        department: {
          type: "choice",
          instructions: "Which team should handle this?",
          criteria: {
            billing: "Payments, payouts, invoicing, refunds",
            technical: "Bugs, outages, integrations",
            sales: "Pricing, upgrades, new accounts",
          },
        },
        frustration: {
          type: "score",
          instructions: "How frustrated is the customer?",
          criteria: ["Calm", "Frustrated", "Very angry"],
        },
        page: {
          type: "noul",
          instructions: "Should someone be paged right now?",
          criteria: {
            true: "Revenue-impacting or data loss",
            false: "Can wait until morning",
          },
        },
      },
    }),
  });

  // Retry only 429/502/529 with backoff; never retry 401/402/422 unchanged.
  for (let attempt = 0; attempt < 4; attempt++) {
    if (resp.status === 429 || resp.status === 502 || resp.status === 529) {
      const retryAfter = Number(resp.headers.get("Retry-After") ?? 2 ** attempt);
      await new Promise((r) => setTimeout(r, Math.min(retryAfter, 8) * 1000));
      continue;
    }
    if (!resp.ok) {
      const { error } = await resp.json();
      throw new Error(`${resp.status} ${error.code}: ${error.message} (request_id ${error.request_id})`);
    }
    return resp.json();
  }
  throw new Error("upstream kept failing; degrade to a human queue");
}

const tickets = [
  "Help! My payouts have been failing for 3 days and my customers keep emailing.",
  "Hi, small typo on the pricing page I thought you should know about.",
];

for (const ticket of tickets) {
  const result = await decide(ticket);
  const { department, page } = result.answers;
  console.log("ticket :", ticket.slice(0, 60) + "...");
  console.log("answers:", JSON.stringify(result.answers));
  console.log(`charge : ${result.usage.credits} credit(s), ${result.latency_ms} ms`);
  if (page.noul >= PAGE_CONFIDENCE) {
    console.log("action : page on-call");
  } else {
    const probs = Object.values(department.probabilities);
    const low = Math.min(...probs) < REVIEW_CONFIDENCE;
    console.log(low
      ? `action : low confidence -> senior queue with both teams`
      : `action : enqueue to ${department.choice}`);
  }
  console.log();
}
