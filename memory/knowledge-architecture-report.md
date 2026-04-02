# Knowledge Architecture Report — OpenClaw Personal AI Stack
*Compiled: 2026-04-01 | Author: Debra (deep research subagent)*
*For: Alex Abell | Classification: Internal/Strategic*

---

## 1. Executive Summary

OpenClaw currently runs a three-layer knowledge stack (Neo4j graph + Obsidian vault + Gemini-embedded memory_search) that's more powerful than you need today but architected for where you're going with Mirror. Neo4j is NOT overkill for the vision, but it IS overkill for what we currently use it for (mostly a people directory that could live in SQLite). The real win isn't dropping components. It's restructuring data flow: raw imports OUT of Obsidian (they're junking your graph view), curated knowledge IN, and letting OpenClaw's built-in LCM + vector search handle the conversational memory layer it was literally designed for. The ideal architecture is three tiers: hot (OpenClaw LCM/SQLite), warm (Obsidian as curated knowledge), cold (staging area for raw imports). Neo4j earns its keep only when Mirror ships and you need real relationship traversal, temporal reasoning, and Johari Window graph queries. Until then, it's optional infrastructure that costs you maintenance headaches.

---

## 2. Current State Assessment

### What We Have

| Component | What It Does | Status |
|-----------|-------------|--------|
| **Neo4j** (localhost:7687) | People graph: 3,067 Person nodes, 6,061 SocialProfiles, 353 GroupChats, 297 Conversations. ~11,500 relationships (dominated by DM_CONVERSATION and MENTIONED_IN) | Running but auth issues, frequently goes down, requires manual restart |
| **Obsidian Vault** (~/SecondBrain/) | 1,262 markdown files across 15 folders. People (116), Meetings (492), Reflections (359), Conversations (211), Concepts (31) | Working but cluttered. 800+ files are raw imports (Meetings + Reflections + Conversations) that junk up graph view |
| **memory_search** (OpenClaw built-in) | SQLite-backed hybrid search (BM25 + Gemini vector embeddings). 44 indexed files, 325 chunks, 479 cached embeddings. Covers workspace/memory/ only | Works well for session memory. Doesn't index SecondBrain vault |
| **OpenClaw LCM** | Lossless Context Management via SQLite. Summary DAG for compaction. Pre-compaction memory flush | Built-in, automatic, solid |
| **Things 3** | Task management | Works, integrated via CLI |
| **Google Contacts/Gmail/Calendar** | Via gog CLI | Works |
| **BlueBubbles** | iMessage gateway | Works |

### What Works

- **memory_search** is surprisingly good for session-to-session continuity. The daily memory files + MEMORY.md + semantic search covers 90% of "remember what happened" needs.
- **Obsidian People cards** are excellent for curated relationship context. 116 detailed profiles with wikilinks.
- **Neo4j relationship traversal** is theoretically powerful (CO_MENTIONED_WITH, MENTIONED_IN, social graph data). Nobody queries it regularly.
- **The file-first philosophy** is correct. Human-readable > hidden in a database.

### What Doesn't Work

- **Neo4j reliability**: Goes down frequently. No auto-restart. Password management is ad-hoc. When it's down, nothing breaks because nothing critical depends on it in real-time.
- **Obsidian graph view is polluted**: 492 Meeting files + 359 Reflections + 211 Conversations = ~1,062 files that are raw imports, not curated knowledge. They create noise in graph view and dilute the signal of actual concept/people connections.
- **No unified search**: memory_search covers workspace, Obsidian is separate, Neo4j is separate. Three silos.
- **Weaver** (the Obsidian→Neo4j bridge) works but is custom Python that needs maintenance. It's another moving part.
- **No voice/speaker layer**: Otter transcripts and voice notes go into Obsidian as flat text. No speaker embeddings, no diarization-aware search.

---

## 3. GAN Analysis

### Decision 1: Should We Keep Neo4j?

#### GENERATOR: Keep Neo4j — It's the Foundation of Mirror

Neo4j is not a people directory. It's a **relationship reasoning engine** and Mirror literally requires one.

**The case:**
- Mirror's Johari Window needs to map relationships between self-perception, others' perceptions, and blind spots. That's a graph problem. You can't do "show me everyone who sees me as X when I see myself as Y" in a flat file.
- The Sentinel component needs to track behavioral patterns across relationships over time. Temporal graph queries (who did I message most in Q1? which relationships are cooling?) require graph traversal.
- Registry (the people/entity directory) IS a graph. People connect to organizations, projects, conversations, topics. That's not a table. It's a web.
- The social data pipeline already has 6,061 SocialProfiles with DM_CONVERSATION edges. When Mirror ships, this becomes the social graph that powers "know your world" (Pools).
- Zep/Graphiti (2025) proved that temporal knowledge graphs for agent memory outperform vector-only approaches. Their benchmarks show 94.8% accuracy on deep memory retrieval vs 93.4% for MemGPT. Neo4j is Graphiti's recommended backend.
- GraphRAG (Microsoft, 2024-2025) demonstrated that combining knowledge graphs with vector retrieval produces richer, more accurate responses than vector-only RAG. Entity-centric retrieval beats chunk-centric.
- Neo4j's 2026 community edition is free, mature, and has the richest ecosystem (Cypher, GDS library, APOC).

**The real argument:** You're building toward a product (Mirror) that needs graph infrastructure. Ripping it out now saves short-term headaches but creates a bigger migration later.

#### DISCRIMINATOR: Drop Neo4j — It's Expensive Complexity for a Personal Setup

Let's be honest about what Neo4j actually does for us today: **it's a fancy contacts database.**

**The case against:**
- 3,067 Person nodes and some MENTIONED_IN edges. That's a CSV file. You don't need a JVM-based graph database burning 500MB+ RAM to store what SQLite handles in 2MB.
- It goes down regularly. When it does, nothing breaks. That's the clearest signal that nothing depends on it.
- The relationship data (DM_CONVERSATION, MESSAGED, etc.) was bulk-imported from social exports. Nobody queries "who messaged whom on Instagram in 2023" in practice.
- Weaver (the bridge to Obsidian) is custom, fragile, and needs babysitting. Every hour maintaining Weaver is an hour not building Mirror.
- SQLite with recursive CTEs handles graphs up to ~50K nodes comfortably. We have ~10K. The `simple-graph` library or `sqlite-graph` extension gives you Cypher queries on SQLite. Sub-millisecond traversals.
- OpenClaw already runs on SQLite for LCM. Adding graph tables to the same database = zero new infrastructure.
- Mem0 and Cognee both offer graph memory without requiring a separate Neo4j instance. They use vector + graph hybrid approaches that integrate with existing infrastructure.
- Neo4j Community Edition has limitations (no clustering, no online backup) that will bite if you ever need production reliability for Mirror.

**The cost math:**
- Neo4j: ~500MB RAM, JVM overhead, port 7474+7687, auth management, startup scripts, monitoring
- SQLite graph: 0 additional processes, 2MB file, backed up with `cp`, never goes down because there's no server

#### SYNTHESIS: Hibernate Neo4j, Build on SQLite, Resurrect for Mirror

**The real answer:** Neo4j is right for Mirror but wrong for today.

**Plan:**
1. **Export the Neo4j graph to SQLite** using `simple-graph` schema (nodes + edges as JSON). This preserves all 10K nodes and 11K relationships in a single file.
2. **Build a `knowledge.sqlite` database** alongside OpenClaw's existing `main.sqlite`. Tables: `people`, `relationships`, `organizations`, `social_profiles`. Use recursive CTEs for traversal.
3. **Stop the Neo4j service.** Free up RAM. Eliminate the reliability headache.
4. **When Mirror enters real development**, evaluate: do you bring Neo4j back, use Memgraph (Bolt-compatible, faster, in-memory), or use Zep/Graphiti (purpose-built for agent temporal memory on Neo4j)?
5. **The data is portable.** A clean JSON export means you can load it into any graph database later.

**What you lose:** Cypher's expressiveness for complex pattern matching, GDS algorithms (community detection, PageRank), and the Neo4j visualization tools. 
**What you gain:** Zero maintenance, zero downtime, one less service to monitor, and all the same data accessible via SQL.

---

### Decision 2: Should Raw Imports Live Outside Obsidian?

#### GENERATOR: Yes — Separate Staging from Curated Knowledge

The vault has 1,262 files. Here's the breakdown:

| Folder | Files | Type |
|--------|-------|------|
| Meetings | 492 | Raw Otter/voice-note transcripts |
| Reflections | 359 | LLM processing outputs, daily reflections |
| Conversations | 211 | ChatGPT/Claude export processing |
| People | 116 | Curated profiles ✓ |
| Concepts | 31 | Curated knowledge ✓ |
| Projects | 21 | Active work ✓ |
| Journal | 11 | Personal ✓ |
| Others | 21 | Mixed |

**~85% of your vault is raw imports.** The 180 curated files (People + Concepts + Projects + Journal) are drowning in 1,082 import files.

**Why this matters:**
- **Obsidian graph view becomes useless** when every meeting transcript creates nodes and edges. The signal-to-noise ratio kills the visualization that makes Obsidian valuable.
- **Search quality degrades.** When you search for "HeartMath", you want the concept note, not 47 meeting transcripts that mention it.
- **Wikilinks become polluted.** Auto-generated links from transcripts create false connections.
- **Vault performance** starts degrading around 8-10K files. At current growth rate (492 meetings in ~10 days of processing), you'd hit that in weeks.

**The staging pattern:**
```
~/SecondBrain/           ← Curated vault (~200 files, clean graph)
~/SecondBrain-Staging/   ← Raw imports (meetings, transcripts, LLM exports)
~/SecondBrain-Archive/   ← Processed, no longer actively referenced
```

Raw files get processed (action items extracted, key entities linked, summaries created) and the OUTPUTS go into the main vault. The raw files stay in staging for reference but don't pollute the graph.

#### DISCRIMINATOR: No — Keep Everything Together, Just Organize Better

Splitting vaults breaks wikilinks. Period.

**The case for keeping it together:**
- Obsidian's power IS the interconnection. A meeting where Chelsea mentioned HeartMath SHOULD link to the HeartMath concept note. Splitting vaults kills that.
- The existing vault-scale-architecture doc says "don't split before 10K files." We're at 1,262.
- The real problem isn't the files existing. It's the graph view configuration. Obsidian lets you filter graph view by folder, tag, or path. Just exclude Meetings/ and Conversations/ from graph view.
- Having everything in one vault means memory_search (if extended to cover SecondBrain) gets the full picture. Split vaults = split context.
- The staging pattern adds operational complexity: "where does this file go?" becomes a decision for every import.

**Counter-counter:** You can have folders within a vault that are excluded from graph view and search via `.obsidian/workspace.json` settings. No split needed.

#### SYNTHESIS: Keep One Vault, Add a Staging Prefix, Configure Graph View

**The real answer:** Don't split vaults. Do reorganize.

**Plan:**
1. **Move raw imports under a `_raw/` prefix** within the vault:
   ```
   ~/SecondBrain/_raw/meetings/     (move 492 files)
   ~/SecondBrain/_raw/reflections/  (move 359 files)  
   ~/SecondBrain/_raw/conversations/ (move 211 files)
   ```
2. **Configure Obsidian graph view** to exclude `_raw/` path. One filter, instant clean graph.
3. **Configure search** to deprioritize `_raw/` results (Obsidian search supports `path:` operators).
4. **The import pipeline** writes to `_raw/`, then a processing step extracts summaries/action items into the main vault area.
5. **If/when you extend memory_search to SecondBrain**, use the folder structure to weight relevance (curated > raw).

This preserves wikilinks, keeps everything searchable, and gives you a clean graph view. Best of both worlds.

---

### Decision 3: What's the Ideal Minimal Stack?

#### GENERATOR: Go All-In on OpenClaw's Built-In Memory

OpenClaw already has everything you need:

**What's built in:**
- **LCM (Lossless Context Management):** SQLite-backed, summary DAG, pre-compaction flush. This is your conversational memory. It works.
- **memory_search:** Hybrid BM25 + vector (Gemini embeddings). 325 chunks across 44 files. This is your semantic recall. It works.
- **Bootstrap files:** MEMORY.md, SOUL.md, USER.md, AGENTS.md load every session. This is your durable identity. It works.
- **Daily memory files:** Append-only logs. This is your episodic memory. It works.
- **Memory plugins:** Extensible to alternative backends.

**The minimal stack:**
```
OpenClaw LCM (SQLite)     → Conversational memory, session state
memory_search (BM25+vec)  → Semantic recall across all memory
MEMORY.md + daily logs    → Curated long-term + episodic memory
Obsidian vault            → Human-browsable knowledge base
Things 3                  → Task management
gog CLI                   → Google Workspace
```

That's it. No Neo4j. No separate vector database. No Mem0 or Cognee dependency. OpenClaw's architecture was designed exactly for this use case.

**Token cost argument:** Every additional retrieval system means more context injected into prompts. OpenClaw's memory_search is already tuned to return relevant chunks. Adding Neo4j results or a separate vector DB means more tokens per query, more cost, more latency, and potentially conflicting information from different sources.

#### DISCRIMINATOR: The Minimal Stack Can't Support the Vision

The minimal stack is fine for "personal assistant." It's not enough for Mirror.

**What's missing:**
- **Relationship graph queries.** "Who in my network knows someone at Google?" requires traversal. Flat files can't do this.
- **Temporal reasoning.** "How has my communication pattern with Hannah changed over the last 6 months?" requires time-indexed relationship data.
- **Multi-modal memory.** Voice vectors, speaker identification, biometric data (HeartMath HRV) don't fit in markdown files.
- **Cross-entity reasoning.** "What topics do Chelsea and I discuss most?" requires entity-aware aggregation, not keyword search.
- **Scale.** 325 chunks works for 44 files. When you have 5,000 files of rich conversational history, you need proper vector indexing with HNSW, not SQLite FTS5.

**The vision stack needs:**
- Graph layer (relationship reasoning)
- Vector layer (semantic similarity at scale)
- Temporal layer (time-aware facts)
- Biometric layer (HeartMath, voice)
- Conversational layer (OpenClaw LCM)

That's at least three databases, not one.

#### SYNTHESIS: Minimal Today, Modular for Tomorrow

**The real answer:** Build the minimal stack now. Design the interfaces so each layer can be upgraded independently.

```
TODAY (April 2026):
┌─────────────────────────────────────────────────┐
│                   OpenClaw Agent                 │
│                                                  │
│  ┌──────────┐ ┌──────────┐ ┌──────────────────┐ │
│  │ LCM/     │ │ memory_  │ │ Bootstrap Files  │ │
│  │ SQLite   │ │ search   │ │ MEMORY.md etc    │ │
│  │ (session)│ │ (recall) │ │ (identity)       │ │
│  └────┬─────┘ └────┬─────┘ └────────┬─────────┘ │
│       │             │                │           │
│       └─────────────┼────────────────┘           │
│                     │                            │
│  ┌──────────────────┴──────────────────────────┐ │
│  │     knowledge.sqlite (NEW)                  │ │
│  │     People + Relationships + Orgs           │ │
│  │     (migrated from Neo4j)                   │ │
│  └──────────────────┬──────────────────────────┘ │
│                     │                            │
└─────────────────────┼────────────────────────────┘
                      │
    ┌─────────────────┼─────────────────┐
    │                 │                 │
┌───┴────┐    ┌──────┴──────┐   ┌──────┴──────┐
│Obsidian│    │  Things 3   │   │  gog CLI    │
│ Vault  │    │  (tasks)    │   │ (Google)    │
│(curated│    └─────────────┘   └─────────────┘
│  KB)   │
└────────┘

MIRROR ERA (when product development starts):
┌─────────────────────────────────────────────────┐
│                   OpenClaw Agent                 │
│                                                  │
│  ┌──────────┐ ┌──────────┐ ┌──────────────────┐ │
│  │ LCM/     │ │ memory_  │ │ Bootstrap Files  │ │
│  │ SQLite   │ │ search   │ │                  │ │
│  └────┬─────┘ └────┬─────┘ └────────┬─────────┘ │
│       │             │                │           │
│  ┌────┴─────────────┴────────────────┴─────────┐ │
│  │          Unified Memory Layer               │ │
│  │  ┌─────────┐  ┌──────────┐  ┌────────────┐ │ │
│  │  │ Graph   │  │ Vector   │  │ Temporal   │ │ │
│  │  │(Graphiti│  │(LanceDB/ │  │(Zep-style  │ │ │
│  │  │ or Neo4j│  │ Qdrant)  │  │ bi-temp)   │ │ │
│  │  └─────────┘  └──────────┘  └────────────┘ │ │
│  │                                             │ │
│  │  ┌──────────────┐  ┌─────────────────────┐  │ │
│  │  │ Voice/Speaker│  │ Biometric/HeartMath │  │ │
│  │  │ Embeddings   │  │ Time-Series         │  │ │
│  │  └──────────────┘  └─────────────────────┘  │ │
│  └─────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────┘
```

**The key principle:** Each layer has a clean interface. The agent queries a unified retrieval function that fans out to the appropriate backends. Today that's just memory_search + knowledge.sqlite. Tomorrow it's memory_search + graph + vector + temporal. The agent code doesn't change. Only the retrieval layer expands.

---

### Decision 4: Where Do Voice Vectors and Speaker ID Fit?

#### GENERATOR: Build a Speaker Registry Now

Voice is becoming a primary input. Otter transcripts, voice notes, phone calls (HoldPlease), and eventually Mirror's conversational capture all produce audio with speakers.

**Current state:** Voice notes and Otter exports go through transcription and land in Obsidian as flat text. Speaker attribution is best-effort from Otter's diarization (which labels speakers as "Speaker 1", "Speaker 2" etc.).

**What voice vectors enable:**
- **Automatic speaker identification:** "This is Alex" vs "This is Chelsea" without manual labeling
- **Cross-session speaker linking:** Same voice across multiple recordings = same person
- **Voice-aware search:** "Find all meetings where Jay spoke about budget"
- **Mirror integration:** Voice patterns as biometric identity data
- **x-vectors** (the standard representation) are 128-512 dimensional embeddings that fit naturally in any vector database

**Where they fit architecturally:**
```
Audio Input → Transcription (AssemblyAI/Whisper) → Text + Speaker Diarization
                                                      ↓
                                                  Voice Embedding Model
                                                      ↓
                                                  x-vector (per speaker)
                                                      ↓
                                              Speaker Registry (vector DB)
                                                      ↓
                                              Person ID Resolution
                                                      ↓
                                              Enriched Transcript
                                              (with named speakers)
```

The speaker registry is essentially a small collection of voice embeddings (one per known person) stored alongside the people graph. When a new audio comes in, extract speaker segments, embed them, and match against known voices.

#### DISCRIMINATOR: This Is Premature Optimization

We process maybe 2-3 voice notes a week. We don't have enough audio to train speaker models. And the voice-notes-processor skill already handles transcription with AssemblyAI (which does diarization).

**Why not now:**
- Building a speaker registry for <50 known voices is overengineering
- AssemblyAI already returns speaker labels. Manual correction is faster than building a custom pipeline.
- Voice embedding models (Resemblyzer, SpeechBrain, Pyannote) require GPU for reasonable performance. The Mac mini's CPU would be slow.
- The ROI doesn't justify the effort until Mirror needs it.
- x-vectors stored in a vector DB is yet another component to maintain.

#### SYNTHESIS: Design the Schema, Don't Build the Pipeline

**The real answer:** Add a `speaker_embeddings` table to knowledge.sqlite now (just the schema). When HoldPlease or Mirror generates enough audio to justify it, plug in a speaker embedding model. The table sits empty and costs nothing.

```sql
CREATE TABLE speaker_embeddings (
  id TEXT PRIMARY KEY,
  person_id TEXT,           -- links to people table
  embedding BLOB,           -- x-vector, 512-dim float32
  source_file TEXT,         -- which audio file this came from
  confidence REAL,          -- match confidence
  created_at TEXT,
  FOREIGN KEY (person_id) REFERENCES people(id)
);
```

**Meanwhile:** When voice-notes-processor runs, save the speaker segments metadata (start/end times, speaker label) alongside the transcript. This makes future re-processing possible without re-transcribing.

---

### Decision 5: What Vector Database for the Future?

#### GENERATOR: LanceDB — Local-First, Multimodal, Zero Ops

For a personal AI stack running on a Mac mini, LanceDB is the winner.

**Why LanceDB over others:**
- **Serverless/embedded:** No separate process. Just a library. Like SQLite for vectors.
- **Multimodal:** Handles text embeddings, voice embeddings, image embeddings in one store. Future-proofed for Mirror's multi-modal needs.
- **Lance format:** Columnar, versioned, designed for ML workloads. You get automatic data versioning.
- **Local-first → cloud-ready:** Start on disk, scale to S3 without changing code.
- **Python-native:** Integrates with LangChain, Pydantic. Fits the OpenClaw/Python ecosystem.
- **Performance:** Rust core, HNSW indexing. Handles millions of vectors on a single machine.

**Comparison:**

| Feature | LanceDB | Chroma | Qdrant | pgvector |
|---------|---------|--------|--------|----------|
| Deployment | Embedded | Embedded/Server | Server (Docker) | Extension (needs Postgres) |
| Multimodal | ✓ native | Text-focused | ✓ payload store | No |
| Versioning | ✓ automatic | No | No | No |
| Maintenance | Zero | Low | Medium | Medium |
| Scale ceiling | Millions | Millions | Billions | Millions |
| Best for | Personal AI, local-first | Quick prototypes | Production scale | Existing Postgres users |

#### DISCRIMINATOR: We Already Have Vector Search in OpenClaw

OpenClaw's memory_search already does BM25 + Gemini vector embeddings. It indexes 44 files into 325 chunks with 479 cached embeddings. Adding LanceDB or any other vector DB is adding complexity for marginal improvement.

**The real question:** Is the current memory_search insufficient? 

At 325 chunks, it's trivially fast. At 5,000 chunks (if we index SecondBrain), it's still fast on SQLite FTS5 + vec extension. You'd need to hit 100K+ chunks before a dedicated vector DB offers meaningful performance advantages over SQLite's built-in vector search.

And OpenClaw explicitly supports memory plugins. If you outgrow SQLite vectors, you swap the backend. You don't need to adopt LanceDB preemptively.

#### SYNTHESIS: Extend OpenClaw memory_search First, LanceDB When It Hurts

**The real answer:** 

1. **Now:** Extend memory_search to index SecondBrain vault (or at least the curated portions). This probably means updating the file glob patterns in OpenClaw's memory config. Cheap win.
2. **When 10K+ chunks:** If retrieval quality or latency degrades, evaluate LanceDB as a drop-in backend via OpenClaw's memory plugin system.
3. **When Mirror needs multimodal:** LanceDB becomes the obvious choice because it handles text + voice + image embeddings in one store.

---

## 4. Recommended Architecture

### Immediate (This Week)

```
┌─────────────────────────────────────────────────────┐
│                  OpenClaw Agent (Debra)              │
│                                                      │
│  Session Memory ← LCM (SQLite, built-in)            │
│  Semantic Recall ← memory_search (BM25+vec, extend) │  
│  Identity ← MEMORY.md + SOUL.md + USER.md           │
│  People/Graph ← knowledge.sqlite (NEW, from Neo4j)  │
│  Tasks ← Things 3                                   │
│  Comms ← BlueBubbles + gog CLI                      │
│                                                      │
│  Obsidian Vault (~/SecondBrain/)                     │
│  ├── People/        (116 curated profiles)           │
│  ├── Concepts/      (31 concept notes)               │
│  ├── Projects/      (21 active projects)             │
│  ├── Journal/       (11 personal entries)            │
│  ├── Areas/         (7 life areas)                   │
│  ├── GTD/           (task management bridge)         │
│  ├── _raw/meetings/ (492 transcripts, graph-hidden)  │
│  ├── _raw/reflect/  (359 reflections, graph-hidden)  │
│  └── _raw/convos/   (211 LLM exports, graph-hidden) │
│                                                      │
│  Neo4j: STOPPED (data exported to knowledge.sqlite)  │
└─────────────────────────────────────────────────────┘
```

### Mirror Era (When Product Development Begins)

```
┌─────────────────────────────────────────────────────┐
│              OpenClaw / Mirror Runtime               │
│                                                      │
│  ┌──────────────── Unified Memory API ────────────┐  │
│  │                                                │  │
│  │  memory.query("who knows me best?")            │  │
│  │    → fans out to: graph + vector + temporal     │  │
│  │    → merges, ranks, returns                    │  │
│  │                                                │  │
│  │  Backends (swappable):                         │  │
│  │  ├── Graph: Graphiti/Neo4j OR Memgraph         │  │
│  │  ├── Vector: LanceDB (text + voice + bio)      │  │
│  │  ├── Temporal: Zep-style bi-temporal indexing   │  │
│  │  ├── Session: OpenClaw LCM (SQLite)            │  │
│  │  └── Files: Obsidian vault (human-readable)    │  │
│  └────────────────────────────────────────────────┘  │
│                                                      │
│  Mirror Components:                                  │
│  ├── Sentinel (behavioral pattern detection)         │
│  ├── Silvering (self-reflection prompts)             │
│  ├── Looking Glass (Johari Window visualization)     │
│  ├── Registry (people + relationships)               │
│  └── Mirror Mirror (the conversational interface)    │
└─────────────────────────────────────────────────────┘
```

---

## 5. Migration Path

### Phase 1: Vault Cleanup (1-2 hours, this week)

1. Create `_raw/` directories in SecondBrain
2. Move Meetings/, Reflections/, Conversations/ contents into `_raw/` equivalents
3. Configure Obsidian graph view to exclude `_raw/` path
4. Verify wikilinks still resolve (Obsidian auto-updates links on move)
5. Verify Weaver still works (or update its paths)

**Risk:** Low. Obsidian handles moves gracefully. Reversible.

### Phase 2: Neo4j → SQLite Migration (2-4 hours, this week)

1. Export Neo4j graph:
   ```cypher
   // Export all nodes
   MATCH (n) RETURN labels(n) AS labels, properties(n) AS props
   // Export all relationships  
   MATCH (a)-[r]->(b) RETURN id(a), type(r), properties(r), id(b)
   ```
2. Create `knowledge.sqlite` with schema:
   ```sql
   CREATE TABLE people (
     id TEXT PRIMARY KEY,
     name TEXT NOT NULL,
     properties JSON,  -- phone, email, notes, etc.
     created_at TEXT,
     updated_at TEXT
   );
   CREATE TABLE relationships (
     id INTEGER PRIMARY KEY,
     from_id TEXT, to_id TEXT,
     type TEXT,  -- FRIEND, COLLEAGUE, CO_PARENT, etc.
     properties JSON,
     created_at TEXT,
     FOREIGN KEY (from_id) REFERENCES people(id),
     FOREIGN KEY (to_id) REFERENCES people(id)
   );
   CREATE TABLE social_profiles (
     id TEXT PRIMARY KEY,
     person_id TEXT,
     platform TEXT,  -- instagram, facebook, linkedin, etc.
     username TEXT,
     properties JSON,
     FOREIGN KEY (person_id) REFERENCES people(id)
   );
   CREATE TABLE organizations (
     id TEXT PRIMARY KEY,
     name TEXT,
     properties JSON
   );
   -- Future: speaker_embeddings, biometric_readings, etc.
   ```
3. Migrate data with Python script
4. Verify queries work (recursive CTE for relationship traversal)
5. Build simple query functions for skills that need people lookup
6. Stop Neo4j service, disable LaunchAgent

**Risk:** Medium. Need to update any skills/scripts that query Neo4j directly. Search codebase for bolt:// and neo4j references.

### Phase 3: Extend memory_search (1-2 hours, next week)

1. Check OpenClaw config for memory_search file patterns
2. Add SecondBrain curated paths (People/, Concepts/, Projects/) to indexed paths
3. Optionally add `_raw/` at lower weight or as a separate search scope
4. Verify retrieval quality with test queries

**Risk:** Low. Additive change.

### Phase 4: Unified People Query (ongoing)

1. Build an OpenClaw skill or function that queries knowledge.sqlite + Google Contacts + memory_search together
2. When you ask "tell me about Brandon Bruce", it checks: knowledge.sqlite (relationships, social), Obsidian People card (curated notes), Google Contacts (phone/email), memory files (recent interactions)
3. Returns a merged, prioritized result

---

## 6. Cost/Complexity Analysis

### Current Stack

| Component | RAM | Disk | Maintenance | Reliability |
|-----------|-----|------|-------------|-------------|
| Neo4j | ~500MB | ~200MB | High (restarts, auth, Weaver) | Low (frequent crashes) |
| Obsidian vault | N/A (file-based) | ~20MB | Low | High |
| memory_search | ~50MB (SQLite) | ~65MB | Zero (auto) | High |
| OpenClaw LCM | ~10MB | Included in main.sqlite | Zero (auto) | High |

### Proposed Stack

| Component | RAM | Disk | Maintenance | Reliability |
|-----------|-----|------|-------------|-------------|
| knowledge.sqlite | ~5MB | ~10MB | Low (no server) | Very High |
| Obsidian vault | N/A | ~20MB | Low (better organized) | High |
| memory_search | ~50MB | ~65MB (+ SecondBrain) | Zero (auto) | High |
| OpenClaw LCM | ~10MB | Included | Zero (auto) | High |

**Net change:**
- **-500MB RAM** (Neo4j gone)
- **-1 JVM process, -2 open ports, -1 LaunchAgent**
- **-1 custom Python script** (Weaver, or simplified to knowledge.sqlite writer)
- **+1 SQLite file** (knowledge.sqlite, ~10MB)
- **Same data, same capabilities** for current use cases
- **Better organized vault** (graph view actually useful)

### Token Cost Impact

| Scenario | Current | Proposed | Change |
|----------|---------|----------|--------|
| People lookup | memory_search only | memory_search + knowledge.sqlite | +~200 tokens (SQL result) |
| General query | memory_search (325 chunks) | memory_search (1000+ chunks with SecondBrain) | +~500 tokens (more context) |
| Relationship query | N/A (nobody queries Neo4j via agent) | knowledge.sqlite recursive CTE | New capability, ~300 tokens |

Token cost increase is minimal and buys better retrieval quality.

---

## 7. Connection to Mirror Product Architecture

Mirror's components map directly to this knowledge architecture:

### Sentinel (Behavioral Pattern Detection)
**Needs:** Time-series data on communication patterns, biometric readings, behavioral signals
**Today:** Nothing actively tracks this
**Architecture:** `knowledge.sqlite` relationship timestamps + future HeartMath time-series table + LCM conversation patterns
**Mirror era:** Zep/Graphiti temporal graph for "how am I changing over time?"

### Silvering (Self-Reflection Prompts)
**Needs:** Rich personal context to generate meaningful reflection prompts
**Today:** Obsidian Reflections folder has 359 files of LLM-processed reflections
**Architecture:** memory_search over reflection content + knowledge.sqlite for relationship context
**Mirror era:** Vector search over reflection history to avoid repeating themes, surface unresolved patterns

### Looking Glass (Johari Window Visualization)
**Needs:** Graph of self-perception vs others' perception vs blind spots
**Today:** Not implemented
**Architecture:** This is the strongest case for a real graph database. The Johari Window IS a graph problem:
```
(Self) --[PERCEIVES_AS {trait: "empathetic"}]--> (Alex)
(Chelsea) --[PERCEIVES_AS {trait: "avoidant"}]--> (Alex)  
(Hannah) --[PERCEIVES_AS {trait: "caring"}]--> (Alex)
```
When traits match = Open quadrant. When others see it but self doesn't = Blind spot. This requires multi-hop graph queries.
**Mirror era:** Neo4j or Graphiti is justified here. This is the killer use case.

### Registry (People + Entity Directory)
**Needs:** Comprehensive people profiles with relationships, interactions, context
**Today:** Obsidian People cards (116) + Neo4j Person nodes (3,067) + Google Contacts
**Architecture:** `knowledge.sqlite` as the structured data layer, Obsidian as the rich-text layer, Google Contacts as the canonical contact info
**Mirror era:** Registry becomes the source of truth for all person-related queries across Mirror, Pools, and the AI Companion

### Mirror Mirror (Conversational Interface)
**Needs:** Full memory stack for deep, context-aware conversations about self
**Today:** OpenClaw LCM + memory_search
**Architecture:** This is already well-served by OpenClaw's built-in memory. The missing piece is the specialized knowledge (Johari graph, behavioral patterns, biometric data) feeding into the conversation.
**Mirror era:** Unified Memory API that combines all layers

### The Data Sovereignty Angle
The file-first architecture (Obsidian + SQLite + flat files) is perfectly aligned with the "your data belongs to you" philosophy of Abellminded. Everything is portable, readable, and owned. No vendor lock-in to a vector DB SaaS or a proprietary graph format. This IS the product differentiator.

---

## 8. What the Research Says (2025-2026)

### Key Papers and Developments

1. **GraphRAG (Microsoft, 2024-2025):** Combining knowledge graphs with RAG produces more accurate results than vector-only retrieval, especially for queries requiring relationship reasoning. Entity-centric > chunk-centric. [Source: microsoft.com, meilisearch.com]

2. **Zep/Graphiti (2025):** Temporal knowledge graphs for agent memory. Bi-temporal modeling (event time + ingestion time). 94.8% accuracy on deep memory retrieval benchmarks, 90% latency reduction vs. alternatives. Open-source, built on Neo4j. [Source: arxiv.org/abs/2501.13956, getzep.com]

3. **Mem0 (2025):** Combined vector + graph memory for AI agents. 26% accuracy improvement over OpenAI Memory on LOCOMO benchmark, 91% faster, 90% fewer tokens. Supports Qdrant, Chroma, pgvector backends. [Source: mem0.ai, github.com/mem0ai]

4. **Cognee (2025):** ECL (Extract, Cognify, Load) pipeline for building context graphs. Unifies vectors, graphs, and reasoning. High scores on HotPotQA. [Source: cognee.ai, github.com/topoteretes/cognee]

5. **Letta/MemGPT (2025-2026):** OS-inspired virtual context management. Agents manage their own memory through function calls. Tiered memory architecture. Model-agnostic. [Source: letta.com, github.com/letta-ai]

6. **OpenClaw LCM (2026):** Summary DAG preserves full conversation history through compaction. BM25 + vector hybrid search. Pre-compaction memory flush. This is architecturally aligned with the research trends (hybrid retrieval, summary hierarchies, persistent memory). [Source: openclaw docs]

7. **Agentic RAG (2025-2026):** Moving from linear retrieve-then-generate to autonomous agents that plan, retrieve, reason, and iterate. LangGraph-style orchestration. Multi-agent collaboration through shared knowledge graphs. [Source: various, emerging standard]

### The Consensus View

The 2025-2026 research consensus is:
- **Vector-only memory is insufficient** for complex reasoning. You need graph structure for relationships and temporal awareness for evolving facts.
- **Hybrid approaches win.** Vector for semantic similarity, graph for relationship traversal, temporal for time-aware reasoning.
- **The "memory runtime" pattern** (a unified API over multiple backends) is emerging as the architecture of choice.
- **File-first and human-readable** is a differentiator, not a limitation. Most frameworks hide data in opaque stores.

OpenClaw's architecture is already well-positioned. The main gap is the graph layer, which knowledge.sqlite fills for now and Graphiti/Neo4j fills for Mirror.

---

## 9. Open Questions for Alex

1. **How often do you actually use Obsidian graph view?** If rarely, the vault pollution is annoying but not blocking. If frequently, the `_raw/` reorganization is urgent.

2. **Do you want people lookup to work from the agent?** e.g., "tell me everything about Brandon Bruce" → merged result from all sources. This drives the knowledge.sqlite priority.

3. **When does Mirror development actually start?** If it's 6+ months out, hibernate Neo4j now. If it's weeks, keep it warm and start building Johari Window schemas.

4. **Should memory_search index SecondBrain?** Right now it only covers workspace/memory/. Extending it to SecondBrain curated folders would be a major recall improvement for almost zero effort.

5. **What's your appetite for Graphiti/Zep?** It's the most research-backed approach for temporal agent memory, but it runs ON Neo4j. If we're going to need Neo4j for Mirror anyway, maybe the play is to migrate FROM raw Neo4j TO Graphiti-managed Neo4j rather than to SQLite.

6. **Voice notes volume:** Are you going to record more? If voice becomes a primary input (meetings, reflections, Mirror conversations), the speaker embedding pipeline moves up in priority.

7. **Weaver's future:** It bridges Obsidian → Neo4j. If Neo4j goes away, does Weaver become Obsidian → knowledge.sqlite? Or do we kill it and let skills write to knowledge.sqlite directly?

8. **The Obsidian-as-product question:** Is SecondBrain just your personal vault, or does it become part of the Mirror product? If product, it needs to be architected for multi-user. If personal, keep it messy and functional.

---

*Report complete. The TL;DR: simplify now (SQLite + organized vault + extended memory_search), design interfaces for the future (unified memory API), and bring the big guns (Neo4j/Graphiti + LanceDB) back when Mirror needs them. Don't carry infrastructure you're not using. Don't paint yourself into a corner either.*

— Debra 💁🏽‍♀️
