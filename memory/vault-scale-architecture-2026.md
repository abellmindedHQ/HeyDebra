# Vault & Graph Scale Architecture — 2026

> Created: 2026-03-29 (overnight scalability session)
> Author: Debra (subagent overnight run)

## Current Scale (2026-03-29)

| Dimension | Current | Threshold | Action |
|-----------|---------|-----------|--------|
| Vault files | 5,486 | 8,000 | Archive old Messages |
| Vault size | 18.9 MB | 100 MB | Split vaults |
| Neo4j Person nodes | 3,067 | 10,000 | Add text search index |
| Neo4j total nodes | ~9,500 | 50,000 | Add replica |
| Weaver full scan | ~64s | 120s | Tune batch size or exclude more |
| Weaver incremental | ~12s | 30s | Good for years |

---

## When Vault Hits 8,000 Files

### Trigger
`find ~/SecondBrain -name "*.md" | wc -l` returns > 8,000

### Actions
1. **Archive old Messages** — move threads with `last_message < 2023` to `_archived/Messages/`
   - Estimated impact: ~300-500 files archived
   - The weaver SKIP_DIRS already excludes `_archived`
   - **Do not delete** — archive only (recoverable)
   
2. **Increase Weaver 50KB cap** — review if it's still the right threshold
   - Currently prevents weaving on 179 thin message files
   - Check if People files are growing > 50KB (that would be wrong)

3. **Run vault_indexer.py** after archiving to confirm counts

---

## When Vault Hits 10,000+ Files

### Recommendation: Vault Splitting

Split into multiple Obsidian vaults:
```
~/SecondBrain/          ← Primary (People, Projects, GTD, Work, Concepts)
~/SecondBrain-Messages/ ← Messages archive (read-heavy, rarely written)
~/SecondBrain-Social/   ← Social media imports (bulk, static)
```

**Why vault splitting works:**
- Obsidian opens each vault independently — no performance hit from vault size
- Weaver can target specific vaults with `--vault` flag (easy to add)
- Entity lookup is per-vault, so 5,000 entities in primary vault stays fast
- Social/Messages vaults are "read archives" — no Weaver runs needed

**Why NOT to split yet:**
- Wikilinks don't cross vault boundaries
- At 5,500 files we're fine
- Weaver incremental mode makes size less critical

---

## Neo4j Scale Plan

### Current State (2026-03-29)
- 3,067 Person nodes (good, was 7,677 before cleanup)
- 6,061 SocialProfile nodes
- 11,496 relationships
- Indexes: Person.name, .id, .phone, .email, .merge_key; SocialProfile.platform, .username

### When Graph Hits 10,000 Person Nodes

#### Add Full-Text Search Index
```cypher
CREATE FULLTEXT INDEX person_name_fulltext IF NOT EXISTS 
FOR (p:Person) ON EACH [p.name, p.email, p.phone]
OPTIONS {indexConfig: {`fulltext.analyzer`: 'english'}}
```
This enables: `CALL db.index.fulltext.queryNodes("person_name_fulltext", "alex")`

#### Add Relationship Indexes
```cypher
CREATE INDEX rel_mentioned_target IF NOT EXISTS FOR ()-[r:MENTIONED_IN]-() ON (r.source)
CREATE INDEX rel_messaged_date IF NOT EXISTS FOR ()-[r:MESSAGED]-() ON (r.date)
```

#### Consider Graph Projections (GDS)
- Neo4j Graph Data Science library for analytics
- Run community detection on MESSAGED relationships
- Identify relationship clusters (family, work, social)

### When Graph Hits 50,000 Nodes

#### Read-Only Replica
- Run second Neo4j instance as replica
- Primary: writes from importers/Weaver
- Replica: reads for agents (Debra, future agents)
- Sync via neo4j replication protocol

#### Sharding Strategy
If Neo4j community edition limits are hit:
- Person nodes by relationship type (Work, Personal, Social)
- Move SocialProfile nodes to separate database
- Keep core graph (Person, Project, Organization) in primary

---

## Weaver Scale Plan

### Current Bottlenecks (2026-03-29)
1. **Large files** — solved with 50KB cap (Messages excluded)
2. **Entity count** — currently 3,799 entities, combined regex handles up to ~10,000
3. **Incremental state** — solves the daily run problem

### When Entity Lookup Hits 10,000 Names

The combined regex with 10,000 alternations will get slow.

**Solution: Aho-Corasick automaton**
```python
# pip install pyahocorasick
import ahocorasick
A = ahocorasick.Automaton()
for idx, name in enumerate(entity_names):
    A.add_word(name.lower(), (idx, name))
A.make_automaton()

# Find all matches in O(n) time regardless of pattern count
for end_idx, (idx, name) in A.iter(text.lower()):
    start_idx = end_idx - len(name) + 1
    # verify word boundary
```
This is O(n) where n = text length, independent of pattern count. Handles 100,000+ patterns.

### Chunked Processing Scaling
- Current chunk size: 500 files
- At 10,000 files: keep 500, will have 20 chunks
- At 50,000 files: increase to 2,000 per chunk or run in parallel

### Parallel Processing (Future)
```python
from multiprocessing import Pool
with Pool(processes=4) as pool:
    results = pool.map(process_file_wrapper, file_chunks)
```
**Not needed yet** — incremental mode makes full scans rare.

---

## Import Pipeline Scale Plan

### Current Import Sources
- iMessage (via imazing export) — 1,781 message files
- Facebook DMs — ~100 files
- Instagram DMs — ~810 files
- Google Contacts — 2,412 people
- LLM conversations — 185 files

### When Adding New Import Sources

**Follow this pattern:**
1. Write importer that creates `.md` files in the right vault folder
2. Importer should write sparse files (< 50KB per file, split if needed)
3. Add source to SKIP_DIRS in Weaver if it's read-only data (Messages, Social)
4. Run weekly Neo4j cleanup after bulk imports

### Deduplication Strategy
The `dedup.py` script (already in weaver/) handles:
- Duplicate person detection by name similarity
- Fuzzy matching for common variations ("Alex Abell" vs "Alexander Abell")

**Expand this for:**
- Phone number normalization (E.164 format)
- Email deduplication across sources
- Social handle cross-referencing

---

## Recommended Weekly Maintenance (Automated)

```bash
# cron: every Sunday 3 AM
# Step 1: Run incremental Weaver
python3 ~/weaver/weaver.py

# Step 2: Neo4j cleanup
python3 ~/weaver/neo4j_weekly_cleanup.py

# Step 3: Rebuild vault index
python3 ~/weaver/vault_indexer.py

# Step 4: Commit changes
cd ~/.openclaw/workspace && git add -A && git commit -m "Weekly vault maintenance $(date +%Y-%m-%d)" && git push
```

---

## Metrics to Track Over Time

Run monthly and append to this table:

| Date | Vault Files | Vault Size | Person Nodes | Weaver Full Scan | Incremental Scan |
|------|-------------|------------|--------------|------------------|------------------|
| 2026-03-29 | 5,486 | 18.9 MB | 3,067 | 64s | 12s |

---

## Red Lines

1. **Never run --full Weaver more than weekly** — incremental handles daily changes
2. **Never bulk-delete from vault** — archive to `_archived/` instead
3. **Always run --dry-run Neo4j cleanup first** — verify before live
4. **Don't split vaults before 10K files** — unnecessary complexity
5. **Keep 50KB Weaver cap** — messages folder is intentionally excluded
