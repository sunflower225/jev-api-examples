#!/usr/bin/env bash
# One yes/no decision with curl — the smallest useful Jev request.
#
# Get a key: https://jevai.website -> sign up -> dashboard -> create API key.
# Store it in an env var, never in frontend code or Git.
#
#   export JEV_API_KEY="jev_live_your_key"
#   ./curl.sh
set -euo pipefail

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
