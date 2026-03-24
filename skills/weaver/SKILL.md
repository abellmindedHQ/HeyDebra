# Weaver Skill

Creates Zettelkasten-style connections between SecondBrain files via wikilinks, concept cards, and back-links.

## When to Use
- "Run Weaver", "weave the vault", "link my notes", "build connections"
- After importing new notes, conversations, or exports
- Periodic maintenance (weekly/monthly)
- When prompted to create concept cards or stubs for missing entities

## Vault Location
`/Users/debra/SecondBrain/`

## What Weaver Does

### Pass 1: Entity Weave
1. Build a lookup table of ALL filenames (without .md) across the vault (excluding `_archived/` and `Imports/`)
2. For each target file, scan content for plain-text mentions of names in the lookup table
3. Replace with `[[wikilinks]]` where not already linked
4. If a referenced entity has no file yet, create a stub with frontmatter + description + `## Wrinkles` section
5. Safe matching: use word-boundary checks, never link partial matches (e.g., don't link "Jay" inside "Jaywalking")

### Pass 2: Concept Weave
1. Scan all files for recurring terms/phrases appearing in 3+ files without their own card
2. Create concept cards at `SecondBrain/Concepts/` — definition, references list, tags
3. Add `[[wikilinks]]` back to new concept cards from source files

### Back-links
- Every file linked TO gets a `## Back-links` section (or existing `## Wrinkles` section updated)
- Format: `- [[Source File]] — brief context`
- Always APPEND, never overwrite existing content

## Directories Created If Missing
- `/Users/debra/SecondBrain/Concepts/`
- `/Users/debra/SecondBrain/MOCs/`

## Priority Targets
1. `People/` (active, not `_archived/`)
2. `Projects/` (all subdirectories)
3. `Work/ORNL/` 
4. Named files: KBUDDS-Strategy.md, Pooli-Vision.md, Mirror.md

## Concept Candidates to Watch For
HeartMath, Johari Window, PARA, Zettelkasten, GTD, Data Sovereignty, Communitism, P.O.W.E.R., The Sentinel, The Silvering, The Looking Glass, The Registry, Mirror Mirror, Night Swimming, Wrinkles, Drops, Pools, Ripples, ADAPT 2026, Fractal, SEEK, KBUDDS, Consciousness, Self-reflection, Self-actualization

## Technical Rules
- Python3 only, no pyyaml — parse frontmatter manually
- Skip content inside frontmatter (`---` ... `---`)
- Skip content inside code blocks (` ``` ` ... ` ``` `)
- Skip `_archived/` and `Imports/` directories
- Skip binary files and `.obsidian/` metadata

## Running Weaver

### Script Location
`/Users/debra/.openclaw/workspace/skills/weaver/weaver.py`

### Usage
```bash
python3 /Users/debra/.openclaw/workspace/skills/weaver/weaver.py
```

### Output
Writes report to: `SecondBrain/Reflections/Daily/YYYY-MM-DD Weaver Report.md`

Report includes:
- Total files scanned
- Total new wikilinks created
- Total stub files created  
- Total concept cards created
- Total back-links added
- Top 10 most-connected entities
- Interesting discoveries

## Report Format
```markdown
---
date: YYYY-MM-DD
type: weaver-report
---

# Weaver Report — YYYY-MM-DD

## Summary
| Metric | Count |
...

## Top 10 Most Connected Entities
...

## Discoveries
...
```
