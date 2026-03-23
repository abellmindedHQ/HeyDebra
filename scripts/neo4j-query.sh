#!/bin/bash
# Usage: neo4j-query.sh "CYPHER QUERY"
curl -s -X POST "http://localhost:7474/db/neo4j/query/v2" \
  -H "Content-Type: application/json" \
  -u "neo4j:secondbrain2026" \
  -d "{\"statement\": \"$1\"}" | python3 -m json.tool
