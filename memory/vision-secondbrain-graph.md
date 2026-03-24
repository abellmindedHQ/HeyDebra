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

## TODO
- [ ] Find Alex's Pools research in ChatGPT export (already processed) and Claude export
- [ ] Research Pooli project — any existing code, docs, branding?
- [ ] Name the "nodes" — Alex wants something fun, not technical
- [ ] Build the wikilink-creation step into all Night Swimming skills
- [ ] Design filterable graph views for Obsidian
- [ ] Process Claude export with awareness of Pools/Mirror/SecondBrain context
