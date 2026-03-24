---
name: people-intel
description: Research and enrich profiles for new people. Use when someone says "look up [person]", "research [person]", "who is [person]", "create a people file for [person]", "enrich [person]'s profile", or when a new person is introduced in a group chat or conversation. Enriches three stores simultaneously: Google Contacts (via gog CLI), SecondBrain markdown files (/Users/debra/SecondBrain/People/), and Neo4j graph database (bolt://localhost:7687). Handles academics, entrepreneurs, public figures, and private individuals with tiered research depth.
---

# people-intel

Automatically research a person and enrich their profile across Google Contacts, SecondBrain, and Neo4j.

## Auto-Watch Behavior (Passive Detection)

This skill should trigger AUTOMATICALLY when Debra detects a new or unrecognized person in any channel:

### Triggers
- New phone number appears in a group chat or DM
- Someone is mentioned by name that Debra doesn't recognize
- Forwarded email from an unknown sender
- New participant joins a group chat
- Alex says "look up [person]", "who is [person]", etc.

### Check Order (before creating anything new)
1. **Google Contacts** — `gog contacts search "[name or number]" --account alexander.o.abell@gmail.com`
2. **SecondBrain/People/** — check active people files
3. **SecondBrain/People/_archived/** — check archived contacts (may be a returning connection)
4. **Neo4j** — `MATCH (p:Person) WHERE p.name CONTAINS "[name]" OR p.phone = "[number]" RETURN p`

### Actions Based on Results
- **Found in archive** → Move back to active People/, update with new context, update Neo4j
- **Found but sparse** → Enrich with available context (run research tiers as needed)
- **Found and complete** → No action needed, use existing context
- **Not found anywhere** → Run full people-intel workflow (below)

### Silent Operation
- Do NOT ask Alex before creating a contact. Just do it.
- Do NOT announce every new contact creation in chat. Log it quietly.
- DO mention it naturally if relevant to the conversation ("oh, that's Brandon's colleague, I just looked her up")

## Inputs

- **Name** (required): Full name of the person
- **Context** (recommended): How Alex knows them, org/company, city, phone, email, relationship type
- **Relationship type**: FRIEND_OF, COLLEAGUE_OF, REPORTS_TO, WORKS_AT, FOUNDED, etc.

## Quick Invocation

Run as a subagent so it doesn't block conversation:

```
Spawn subagent: research [Name] — [context]. Enrich all three stores.
```

Or run interactively for a single person with rich context already in hand.

## Research Tiers

Tier selection is automatic based on first-pass signals. See `references/tier-research-guide.md` for detailed patterns.

| Tier | When | Sources |
|------|------|---------|
| 1 | Always | LinkedIn, Twitter/X, Instagram, Facebook, Google search, company pages |
| 2 | Notable/public figure | News, podcasts, conference talks, blog/Substack/Medium |
| 3 | Academic signal | Google Scholar, ResearchGate, ORCID, citations, collaborators |
| 4 | Entrepreneur signal | Crunchbase, AngelList, Product Hunt, founding story |

Signals that trigger deeper tiers: job titles (Professor, Dr., Founder, CEO), org type (university, startup, VC), publication mentions, press coverage.

## Workflow

### 1. Research Phase

```
web_search("[Name] [org or city]")
web_search("[Name] LinkedIn")
web_search("[Name] [company] site:linkedin.com")
```

Gather: current role, org, location, email, social handles, bio summary.

Auto-promote to Tier 2+ if news results, academic papers, or startup data appears in Tier 1 results.

For academics → follow citation threads to find collaborators (each collaborator = a potential wrinkle edge in Neo4j).

### 2. Photo Search

**Strategy: try multiple sources, escalate to browser if needed.**

1. First try direct URL patterns for known org types:
   - University faculty: `[university].edu/people/profile/[name]/`, `/faculty/[name]/`, `/directory/[name]/`
   - Company: `[company].com/about`, `/team`, `/about-us`
2. If direct URLs 404, use browser to search the org's site: `browser action=open url="[org website]/?s=[name]"`
3. Extract image URL from the page source: `curl -s [page_url] | grep -oE 'src="[^"]*"' | grep -i "[name]"`
4. Download with curl: `curl -s "[image_url]" -o /Users/debra/SecondBrain/People/photos/[FirstLast].[ext]`

**Confidence rules:**
- **HIGH (save)**: Photo on official staff/faculty page with their name in URL or caption, or company team page
- **MEDIUM (save with note)**: LinkedIn profile photo where name matches
- **LOW (skip)**: Google Images with no clear attribution, social profiles where name doesn't exactly match

Save to: `/Users/debra/SecondBrain/People/photos/[FirstLast].[ext]`

### 3. Google Contact

Check if contact exists first (THIS IS THE SOURCE OF TRUTH FOR PHONE/EMAIL):
```bash
gog contacts search "[Name]" --account alexander.o.abell@gmail.com
```
**CRITICAL: If Google Contacts has a phone number or email for this person, USE THAT. Do not overwrite with web research data. Google Contacts > web research for contact info.**

Create or update:
```bash
gog contacts create --account alexander.o.abell@gmail.com \
  --given "[First Name]" --family "[Last Name]" \
  --phone "[phone]" \
  --email "[email]" \
  --org "[Organization]" \
  --title "[Title]" \
  --note "[brief context, relationship to Alex, source]"
```

If photo found with high confidence, attach it. Use `gog contacts update` if contact already exists.

### 4. SecondBrain Markdown File

Create `/Users/debra/SecondBrain/People/[FirstLast].md`:

```markdown
---
name: [Full Name]
aliases: []
photo: photos/[FirstLast].jpg  # or "none"
phone: "[phone]"
email: "[email]"
org: "[Organization]"
title: "[Title]"
location: "[City, State]"
relationship: "[How Alex knows them]"
relationship_type: [FRIEND_OF|COLLEAGUE_OF|etc]
twitter: "[handle]"
linkedin: "[url]"
instagram: "[handle]"
tags: [person, professional|academic|entrepreneur|friend]
created: [YYYY-MM-DD]
updated: [YYYY-MM-DD]
---

# [Full Name]

## Who They Are

[2-3 sentence narrative bio. Role, org, what they're known for.]

## Connection to Alex

[How they met or were introduced. Context from the conversation.]

## Professional Background

[Career arc, current role, past roles. Keep it punchy.]

## Online Presence

- LinkedIn: [url]
- Twitter: [url]
- Personal site: [url]

## Articles & Interviews

- [Title](url) — [one-sentence summary] ([year])

## Research Publications *(if academic)*

- [Title](url) — [journal], [year]. [one-sentence summary]

## Wrinkles

*(Graph relationships — auto-populated from Neo4j)*

- [RELATIONSHIP_TYPE] → [Other Person or Org]

## Notes

[Anything else worth knowing. Personality signals, interests, context clues.]
```

### 5. Neo4j Graph

Use `cypher-shell` with credentials `neo4j`/`secondbrain2026` at `bolt://localhost:7687`.

```bash
cypher-shell -a bolt://localhost:7687 -u neo4j -p secondbrain2026 << 'EOF'
MERGE (p:Person {name: "[Full Name]"})
SET p.phone = "[phone]",
    p.email = "[email]",
    p.org = "[org]",
    p.title = "[title]",
    p.location = "[location]",
    p.linkedin = "[url]",
    p.twitter = "[handle]",
    p.updated = date()

// Relationship to Alex
MERGE (alex:Person {name: "Alex Abell"})
MERGE (p)-[:RELATIONSHIP_TYPE {context: "[how they met]", since: "[year if known]"}]->(alex)

// Org node
MERGE (org:Organization {name: "[org name]"})
MERGE (p)-[:WORKS_AT]->(org)
EOF
```

Relationship types: `FRIEND_OF`, `COLLEAGUE_OF`, `REPORTS_TO`, `WORKS_AT`, `FOUNDED`, `ADVISES`, `MENTORS`, `COLLABORATES_WITH`, `STUDIED_WITH`, `MET_AT`.

For academics: add `COLLABORATES_WITH` edges to co-authors found in publications.

### 6. Update SecondBrain Wrinkles Section

After Neo4j writes are complete, query back and update the Wrinkles section in the markdown:

```bash
cypher-shell -a bolt://localhost:7687 -u neo4j -p secondbrain2026 \
  "MATCH (p:Person {name: '[Full Name]'})-[r]->(n) RETURN type(r), n.name"
```

## Photo Confidence Rules

**Attach photo if:**
- Found on an official staff/faculty page with their name in the URL or caption
- LinkedIn profile photo where name matches exactly
- Company "team" page with labeled headshot

**Skip photo if:**
- Google Images result with no clear attribution
- Social profile where name doesn't exactly match
- Any ambiguity about identity

## Output Summary

After enrichment, report back:
```
✅ [Name] enriched
- Google Contact: created/updated
- SecondBrain: /Users/debra/SecondBrain/People/[Name].md
- Neo4j: Person node + [N] relationship edges
- Photo: attached / not found
- Tiers used: 1, 2 (notable)
- Key findings: [2-3 bullet summary]
```

## Reference Files

- **`references/tier-research-guide.md`**: Detailed search patterns, source lists, and extraction strategies for each research tier. Read when going deep on a specific tier.
