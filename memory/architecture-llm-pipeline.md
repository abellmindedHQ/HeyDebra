# LLM-to-SecondBrain Pipeline Architecture
*Designed 2026-03-24*

## The Problem
Alex has years of strategic thinking, project architecture, people research, creative work, and personal processing spread across multiple LLM accounts:
- Claude (alexander.o.abell@gmail.com) — 139 conversations, Jan 2025 - Mar 2026
- ChatGPT — 139 conversations (already processed Night Swimming Day 1)
- Gemini — unknown, needs export
- Other accounts possible

This intellectual output needs to flow into SecondBrain organized by DOMAIN, not by source.

## Guiding Principles
1. **Organize by domain, not source.** A ServiceNow conversation from Claude and a ServiceNow conversation from ChatGPT should live next to each other.
2. **Separate public from private.** Work stuff, creative output, and big ideas could be shareable. Relationship analysis and personal processing stay private.
3. **Extract, don't just archive.** The value isn't the raw conversation — it's the decisions, insights, artifacts, and context within them.
4. **Cross-reference everything.** People mentioned → People files. Projects discussed → Project files. Decisions made → linked to outcomes.

## Domain Taxonomy (for SecondBrain organization)

```
SecondBrain/
├── Work/
│   ├── ORNL/
│   │   ├── Transformation/        (strategy, quick wins, PIT)
│   │   ├── ServiceNow/            (CMDB, CSDM, PPM, catalog)
│   │   ├── Applications/          (app roster, capabilities, families)
│   │   ├── WordPress-Fractal/     (Brad's multisite platform)
│   │   ├── Power-Platform/        (governance, strategy)
│   │   ├── Team/                  (org structure, hiring, management)
│   │   └── Awards-Recognition/    (SEEK, Appy, nominations)
│   └── Consulting/
│       └── Abellminded/           (brand, strategy, offerings)
├── People/                        (already exists, 250+ files)
├── Creative/
│   ├── Music/                     (lyrics, Suno tracks, album art)
│   ├── Writing/                   (stories, book chapters, poems)
│   ├── Ideas/                     (OtherBeasts, app concepts, etc.)
│   └── Social-Captions/           (Instagram, etc.)
├── Personal/
│   ├── Relationships/             (communication analysis, therapy notes)
│   ├── Family/                    (Avie, Sallijo, Roxanne, co-parenting)
│   ├── Finance/                   (budgets, loan stuff, retirement)
│   └── Health/                    (derm, psychiatry, ADHD)
├── Learning/
│   ├── AI-and-Tech/              (Technostism, AI philosophy, tools)
│   ├── Travel/                    (Copenhagen, Camino, Europe tours)
│   └── Reference/                 (compound interest, legal, etc.)
├── Projects/                      (active project docs)
│   ├── SecondBrain/
│   ├── HeyDebra/
│   ├── NightSwimming/
│   └── Mirror/                    (TBD — need context from Alex)
├── Reflections/
│   ├── Daily/                     (processing reports)
│   ├── Instagram/                 (social media analysis)
│   └── LLM-Processing/           (conversation processing reports)
├── Documents/                     (drive audit, exports)
└── Imports/                       (raw data before processing)
    ├── chatgpt/
    ├── claude/
    ├── instagram/
    ├── linkedin/
    └── facebook/                  (when it arrives)
```

## Processing Pipeline

### Phase 1: Classification (cheap model — Gemini Flash or Sonnet)
For each conversation:
1. Read title + first few messages
2. Classify into domain (Work/Personal/Creative/Learning)
3. Assign sub-category
4. Extract key entities: people, projects, decisions
5. Rate importance: high (strategic decisions, key artifacts) / medium (useful context) / low (one-off questions)

### Phase 2: Extraction (Sonnet for most, Opus only for complex strategic thinking)
For high/medium importance conversations:
1. Extract artifacts (code, templates, frameworks, designs)
2. Extract decisions and rationale
3. Extract people context and relationship signals
4. Extract action items (completed or pending)
5. Generate a summary note for Obsidian

### Phase 3: Storage
1. Write Obsidian markdown files to appropriate domain folder
2. Create/update Neo4j nodes and relationships
3. Update People files if new context found
4. Save any artifacts to shareable location if appropriate

### Phase 4: Artifact Handling
For conversations with shareable artifacts:
1. Extract the artifact (HTML, code, design, analysis)
2. Save to abellminded GitHub repo under /lab/ or /demos/
3. If it's a deploy-worthy artifact, set up GitHub Pages/Vercel hosting
4. Link from the Obsidian note back to the hosted version

## Model Selection Strategy
- **Classification**: Gemini Flash ($0) or Sonnet ($) — just reading titles and categorizing
- **Extraction (most conversations)**: Sonnet ($$) — good enough for summaries and entity extraction
- **Extraction (complex strategic)**: Opus ($$$) — only for deep analysis of important conversations
- **Neo4j writes**: No model needed, just Cypher queries
- **Artifact formatting**: Sonnet — reformatting code/HTML doesn't need Opus

## Estimated Token Usage (Claude export, 139 conversations)
- Classification pass: ~50K input tokens (titles + snippets) → ~$0.15
- Extraction (est. 80 medium+high conversations): ~500K input, ~200K output → ~$5
- Total estimate: ~$5-8 for full processing on Sonnet
- Opus would be ~$50+ for same work. 10x more expensive, unnecessary for 90% of it.
