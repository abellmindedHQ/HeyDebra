# Pending Data Exports
*Tracking all requested data exports for SecondBrain ingestion*

## Status

| Platform | Requested | Status | Expected Wait | What We Need |
|----------|-----------|--------|---------------|-------------|
| LinkedIn (full) | 2026-03-23 | ⏳ Pending | 24-72 hours | Connections.csv (the big one), Profile, Endorsements, Skills, Recommendations |
| LinkedIn (partial) | 2026-03-23 | ✅ Received | — | Messages, Shares, Reactions, SearchQueries, PhoneNumbers. PROCESSING NOW. |
| Facebook (FULL) | 2026-03-23 | ⏳ Pending | Could be DAYS (full archive since ~2003, includes logs) | Friends list, messages, posts, photos, check-ins, life events, activity logs, comments, likes, groups, everything |
| ChatGPT (2nd export) | ~2026-03-21? | ⏳ Pending | Usually 24 hours | More conversations beyond the 139 already processed |
| Claude (export 1) | ~2026-03-21? | ⏳ Pending | Varies | Conversation history |
| Claude (export 2) | ~2026-03-21? | ⏳ Pending | Varies | Conversation history |

## Notes
- First ChatGPT export (139 convos, Jan 2025 - Mar 2026) already processed by Night Swimming
- LinkedIn partial arrived same day (fast export). Full export takes longer.
- Facebook exports notoriously slow (can take days, sometimes a week)
- Claude exports: check settings page, might need to re-request

## What To Do When Each Arrives
- **LinkedIn full**: Cross-reference Connections with message analysis to build complete network map
- **Facebook**: Friends list → People files, Messages → relationship context, Photos → profile images
- **ChatGPT 2nd**: Run Night Swimming again on new conversations
- **Claude**: Same treatment as ChatGPT — parse, extract entities, Neo4j, Obsidian notes
