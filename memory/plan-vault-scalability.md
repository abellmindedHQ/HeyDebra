# Vault & Graph Scalability Plan

> Created: 2026-03-29 (overnight cleanup session)

## Current State (Post-Cleanup)

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Neo4j Person nodes | 7,677 | 4,766 | -38% |
| Obsidian vault files | 5,476 | ~5,400 | Stable |
| Weaver runtime | TIMEOUT (>150s) | TBD | Needs fix |

## What Caused the Mess

1. **LLM conversation imports** — Claude/ChatGPT conversations about ServiceNow, music business, Lunchpool brainstorming all had concepts extracted as Person nodes
2. **Social media imports** — 12.2GB Facebook + Instagram dumps created thousands of thin contact nodes
3. **No entity validation** — Weaver and import scripts didn't distinguish people from concepts
4. **No cleanup automation** — Junk accumulated over time with no periodic pruning

## Neo4j Cleanup Done Tonight

- Deleted 2,285 orphan Person nodes (zero relationships)
- Deleted 455+ ServiceNow/IT concept nodes mislabeled as Person
- Deleted 86 high-connection concept nodes (brainstorming artifacts)
- Merged 3 duplicate Alex Abell nodes into 1
- Removed music industry concepts, brand names, text fragments

## Weaver Fixes Done Tonight

- Added `ABSOLUTE_MIN_NAME_LENGTH = 3` hard floor
- Added single-letter and common short words to AMBIGUOUS_NAMES
- Added email address exclusion
- Added date-slug file pattern exclusion (YYYY-MM-DD-*)
- Cleaned 139 vault files with bad [[K]], [[e]], [[trim]] wikilinks

## Long-Term Scalability Strategy

### Phase 1: Weaver Performance (URGENT)
- **Incremental mode**: Only process files modified since last run (check mtime)
- **Chunked processing**: Process 500 files per batch, yield between batches
- **Cache entity lookup**: Save the entity index to a JSON file, only rebuild on new files
- **Timeout**: Increase from 150s to 300s minimum

### Phase 2: Neo4j Hygiene (weekly)
- **Scheduled cleanup cron**: Weekly check for orphan nodes, concept-as-person mismatches
- **Entity type validation**: Before creating Person nodes, validate against a pattern (must look like a name)
- **Dedup automation**: Auto-merge duplicate Person nodes (same name, different cases)
- **Add labels**: Distinguish Person vs Concept vs Organization vs Place properly

### Phase 3: Vault Organization (monthly)
- **Archive old conversation notes**: Move processed LLM conversations to archive folder
- **Consolidate thin contact cards**: Merge contacts with <3 data points into a summary file
- **Folder structure audit**: Ensure consistent naming, no orphan files
- **Index file**: Generate a vault index for fast lookup without scanning all files

### Phase 4: Future Scale (when vault hits 10K+ files)
- **Obsidian vault splitting**: Separate vaults for Messages (bulk), People, Projects
- **Neo4j indexing**: Add proper indexes on Person.name, SocialProfile.platform
- **Incremental graph updates**: Instead of full reimports, use delta updates
- **Read-only replicas**: If we add more agents (Avery), they get read-only graph access
