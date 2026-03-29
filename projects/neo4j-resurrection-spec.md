# Neo4j Resurrection Spec

> Written 2026-03-29 before hibernation. Use this to bring the graph back when Mirror MVP is ready.

## Why Hibernated
- Data was 90% noise (6,061 SocialProfiles, 3,050 ghost Person nodes, 353 null GroupChats)
- Only 14 Person nodes had phone/email, 300 had meaningful relationships
- RAM/CPU cost on Mac mini not justified without a product consuming the data
- All valuable data already exists in Obsidian People/ files and MEMORY.md

## Data Directory
- Location: /opt/homebrew/var/neo4j/ (or wherever Homebrew installed it)
- DO NOT DELETE. Cold storage. Zero cost while stopped.

## When to Resurrect
- Mirror MVP reaches "stream fusion" stage (The Silvering)
- OR: A product feature requires real-time multi-hop graph traversal
- NOT for: simple person lookup (Obsidian search handles this)

## Clean Schema (build fresh, don't reuse old data)
```cypher
// Core nodes
(:Person {name, phone, email, tier, org, title, location})
(:Organization {name, type})
(:Topic {name})
(:Conversation {title, date, source, summary})

// Core relationships
(Person)-[:WORKS_AT {since}]->(Organization)
(Person)-[:REPORTS_TO]->(Person)
(Person)-[:KNOWS {strength, context}]->(Person)
(Person)-[:DISCUSSED]->(Topic)
(Person)-[:PARTICIPATED_IN]->(Conversation)
```

## Import Source
- Obsidian People/ files (clean, enriched profiles)
- Google Contacts (phone, email, org, title)
- Conversation summaries from Obsidian Conversations/

## What NOT to Import
- Raw Facebook/Instagram social profiles (noise)
- Raw iMessage/SMS threads (use summaries)
- Every ChatGPT/Claude conversation (only import key ones with extracted insights)
