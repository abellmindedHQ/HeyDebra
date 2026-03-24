# SecondBrain Vision: Graph, Wrinkles, Pools, and the Living Knowledge Map
*Captured 2026-03-24 from Alex's brain dump before Best Buy*

## The Linking Problem
Current SecondBrain files are mostly isolated. The value is in the EDGES (wrinkles) between them, not just the nodes. Night Swimming and every processing job should be creating wikilinks between knowledge files as a core part of their work.

## Terminology (needs naming)
- **Nodes** = knowledge files/cards (People, Projects, Concepts, etc.) — name TBD, Alex wants something fun
- **Wrinkles** = edges/relationships between nodes (already named)
- **Pools** = interest-based mini-networks (see below)
- **Circles** = people-network views

## Zettelkasten / Linking Your Thinking Influence
- Alex explored this ~5 years ago via Obsidian
- Likely Nick Milo's "Linking Your Thinking" (LYT) or Tiago Forte's BASB
- Zettelkasten = German "slip box" system. Index cards with cross-references. Library card vibes.
- Key concept: atomic notes linked together create emergent knowledge
- Obsidian's wikilinks ([[Person Name]], [[Concept]]) make this native

## Graph Visualization Requirements
- More wrinkles (edges) between nodes → thicker connecting lines
- More knowledge on a card/node → bigger node in graph view
- Both should be visible in Obsidian's graph view AND any future web visualization (abellminded.com brain map)

## Filterable Views
- **"My Circles"** — people network knowledge
  - Who's connected to who
  - Who SHOULD I know? (suggested connections based on graph gaps)
  - Who should I get to know better? (weak ties worth strengthening)
  - Who do I know well but haven't connected with in forever? (relationship decay)
- **"My Projects"** — project graph
- **"My Ideas"** — concept map
- **"My Work"** — ORNL/professional knowledge

## Pools — Alex's Passion Concept
- Originated from **Lunchpool** (Alex's startup, 2019-2023)
- Evolved into an obsession and core research theme
- Pools ≠ Circles. Circles = who you know. Pools = interest-based mini-networks organized around topics.
- Examples: "Dating Pools", "Job Pools", "Social Pools"
- Like subreddits/communities but more personal and curated
- **Pooli** — Alex's project exploring this concept. May still have legs.
- Need to find Alex's research on Pools (likely in ChatGPT convos, Claude convos, and personal docs)
- Key question: does Pools fit into the Abellminded ecosystem? Is Pooli a product?

## Potential Brand Architecture (Updated)
```
Abellminded (umbrella)
├── Mirror (consumer — self-reflection/self-actualization)
├── SecondBrain (methodology/infrastructure — knowledge capture)
│   └── Pools (knowledge community concept within SecondBrain?)
├── Pooli (standalone product? or feature of Mirror/SecondBrain?)
├── HeyDebra (the AI assistant playbook)
└── abellminded.com/.dev (public face + docs)
```

## Night Swimming Enhancement Needed
Every processing job (email, social, LLM exports, etc.) should:
1. Create the primary content file
2. Scan for entity references (people, projects, concepts)
3. Create wikilinks ([[Person Name]], [[Project Name]]) in the content
4. Check if the linked target exists; if not, create a stub
5. Update the target file's "Wrinkles" section with a back-link
6. This creates organic graph density over time

## iMazing — Private Text Capture Stream
- Alex wants all private text history as a SecondBrain capture stream
- iMazing can export full iPhone backup including SMS/iMessage
- Would provide massive relationship context
- Needs processing pipeline similar to Instagram/ChatGPT exports
- Privacy-critical: this stays in SecondBrain, never public

## Nick Milo — Confirmed Influence
- "Linking Your Thinking" (LYT) — cohort workshops, YouTube, big on Obsidian
- MOCs (Maps of Content) — hub notes that link to related notes
- linkingyourthinking.com

## Tiago Forte — PARA Method
- "Building a Second Brain" (BASB) methodology
- PARA: Projects, Areas, Resources, Archives
- Key insight: organize by ACTIONABILITY not just domain
- Tool-agnostic, cohort-based course
- We should blend PARA's actionability layer with our domain-based taxonomy

## Brain Anatomy → SecondBrain Mapping
- Neurons → Drops (individual knowledge units)
- Synapses → Wrinkles (connections/edges)
- Hippocampus → active-context.md (working memory)
- Amygdala → emotional/priority tagging (NOT YET BUILT)
- Neocortex → MEMORY.md + Obsidian vault (long-term storage)
- Synaptic Plasticity → edge weight (more references = thicker wrinkle)
- Long-Term Potentiation → repeated activation strengthens connections

## Naming Candidates (Brain + Pools metaphor)
- **Drops** = knowledge units (notes, people, concepts). Drops form Pools.
- **Wrinkles** = edges/connections (already named ✅)
- **Pools** = interest-based clusters of Drops (Alex's passion concept)
- **Ripples** = influence/impact radiating through the graph
- This metaphor is cohesive: Drops → Wrinkles → Pools → Ripples

## Universal GTD Capture Engine (not just email)
Alex wants GTD processing from ALL streams, not just email:
- Email (gog)
- Calendar events (meeting action items)
- Teams messages (ORNL)
- iMessage conversations
- Voice notes/transcripts
- LLM conversations
- Social media DMs
Need a universal "extract action items" layer across all streams.

## Sanitize Locally, Process Externally Pattern
- Sensitive/CUI files processed by LOCAL LLM (Ollama on Mac mini or lab VM)
- Local LLM extracts knowledge, strips sensitive data (names → roles, specifics → patterns)
- Sanitized version sent to Claude/Sonnet for deeper analysis
- Results re-linked to original context locally
- Defense contractor pattern for classified + AI
- Mac mini M-series can run 7B-13B models (Llama 3, Mistral) for sanitization
- Not for deep reasoning, just for "make this safe to send externally"
- This is the defensible architecture for ORNL compliance

## ORNL Security/Compliance Constraints
- Can't merge work + personal calendars
- Multiple inboxes (ORNL + personal)
- LLM usage restricted by SBMS procedures
- Federal/lab data privacy guardrails
- Teams messages can't freely flow to personal systems
- Need compliant bridge, not workaround

## Pools Research Locations
- Google Drive: Lunchpool 2.0/3.0 pitchdecks, Pooli pitches
- ChatGPT export: likely contains Pools discussions
- Claude export: may contain additional context
- Pooli: standalone project, may have legs in this ecosystem

## TODO
- [ ] Find Alex's Pools research in ChatGPT export (already processed) and Claude export
- [ ] Search Google Drive for Lunchpool/Pooli pitchdecks
- [ ] Research Pooli project — any existing code, docs, branding?
- [ ] Confirm naming: Drops + Wrinkles + Pools + Ripples
- [ ] Build the wikilink-creation step into all Night Swimming skills
- [ ] Design filterable graph views for Obsidian
- [ ] Process Claude export with awareness of Pools/Mirror/SecondBrain context
- [ ] Deep dive Tiago Forte's PARA for what we can adopt
- [ ] Map ORNL compliance constraints for SecondBrain
- [ ] Design universal GTD capture engine architecture
