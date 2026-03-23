#!/bin/bash
# Usage: linear-create-issue.sh "title" "stateId" priority
# States: done=aec07cf4 todo=f429f359 inprogress=bf3a3bb8 backlog=be3083bf
TITLE="$1"
STATE="$2"
PRIO="${3:-3}"
curl -s -X POST https://api.linear.app/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: REDACTED_LINEAR_KEY" \
  -d "{\"query\": \"mutation { issueCreate(input: { title: \\\"$TITLE\\\", teamId: \\\"7274d506-ba89-4a7b-8462-5ce3fc25a52e\\\", stateId: \\\"$STATE\\\", priority: $PRIO }) { success issue { identifier title } } }\"}" | python3 -c "import json,sys; d=json.load(sys.stdin); i=d['data']['issueCreate']['issue']; print(f\"{i['identifier']} {i['title']}\")"
