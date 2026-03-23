# Tier Research Guide

Detailed search patterns and extraction strategies for each research tier.

---

## Tier 1: Baseline (Always)

**Goal**: Establish identity — name, face, role, org, contact info, social handles.

### Search Patterns

```
"[Full Name]" "[Company/Org]"
"[Full Name]" site:linkedin.com
"[Full Name]" "[City]" professional
"[Full Name]" "[known context e.g. 'ORNL' or 'UTK']"
```

### Sources to Hit

| Source | What to look for |
|--------|-----------------|
| LinkedIn | Current title, org, location, summary, connections |
| Twitter/X | Bio, location, pinned tweet, follower count |
| Instagram | Bio, location, profile pic |
| Facebook | Current city, employer, education |
| Company/Org staff page | Official title, headshot, bio, contact email |
| Personal website | Anything—portfolio, blog, contact |

### Extraction Targets

- Full name, preferred name/nickname
- Current job title + organization
- Location (city/state at minimum)
- Email (often on company staff pages)
- Phone (rarely public, but sometimes on faculty/staff pages)
- Profile photo URL (evaluate confidence before saving)
- Social handles (Twitter, Instagram, LinkedIn URL)
- Brief bio summary (1-2 sentences)

### Stop Condition

If the person has limited public footprint (common name, private individual, no professional presence), stay in Tier 1. Note "limited public footprint" in SecondBrain notes. Don't fabricate.

---

## Tier 2: Notable / Public Figure

**Trigger signals from Tier 1:**
- News results appear in Google search
- Blog, newsletter, or Substack presence
- Podcast appearances listed on website
- Conference speaker pages
- Public writing/commentary
- Notable job (VP+, executive, politician, journalist, artist)

### Search Patterns

```
"[Full Name]" interview
"[Full Name]" podcast
"[Full Name]" "[Company]" news
"[Full Name]" TEDx OR keynote OR speaker
"[Full Name]" Substack OR Medium OR newsletter
"[Full Name]" site:medium.com
"[Full Name]" site:substack.com
```

### Sources to Hit

| Source | What to look for |
|--------|-----------------|
| News articles | Coverage, quotes, announcements |
| Podcast directories | Listen Notes, Spotify, Apple Podcasts |
| YouTube | Talks, interviews, panels |
| Medium/Substack | Their own writing |
| Conference sites | Speaker bios, talk descriptions |
| PR Newswire / Business Wire | Press releases about them |

### Extraction Targets

- Article/interview summaries (1 sentence each, with URL + year)
- Podcast episode titles and dates
- Conference talk titles and links
- Key quotes or positions they've stated publicly
- Awards, recognition, board memberships

### Notes for SecondBrain

In the "Articles & Interviews" section, list max 5-7 most relevant items. Format:

```markdown
- [Article Title](url) — [one-sentence summary] ([year])
- Podcast: [Show Name] — "[Episode Title]" — [one-sentence summary] ([year])
```

---

## Tier 3: Academic

**Trigger signals:**
- "Dr." or "Prof." prefix
- University affiliation
- Research lab or institute
- Publications appear in Tier 1 results
- Google Scholar profile found

### Search Patterns

```
"[Full Name]" site:scholar.google.com
"[Full Name]" "[University]" research
"[Full Name]" ORCID
"[Full Name]" site:researchgate.net
"[Full Name]" publications citations
"[Full Name]" "[field]" paper
```

### Sources to Hit

| Source | What to look for |
|--------|-----------------|
| Google Scholar | h-index, citation count, top papers, co-authors |
| ResearchGate | Publications list, lab affiliations |
| ORCID | Publication list, grants, employment history |
| University lab page | Research group, current projects, students |
| PubMed (life sciences) | Publications, co-authors |
| arXiv (CS/physics/math) | Preprints, co-authors |
| Semantic Scholar | Citation network |

### Extraction Targets

- Top 3-5 publications (title, journal, year, one-sentence summary)
- h-index and citation count (if visible)
- Research area / specialization
- University lab / research group name
- **Co-authors** → each co-author is a potential Neo4j `COLLABORATES_WITH` wrinkle

### Co-author Wrinkle Strategy

For each co-author on their top papers:
1. Note co-author name + institution
2. Add to Neo4j: `MERGE (coauth:Person {name: "..."}) MERGE (person)-[:COLLABORATES_WITH {paper: "..."}]->(coauth)`
3. If co-author is already in SecondBrain (existing Person node), strengthen that edge
4. Don't deep-research each co-author unless explicitly asked—just create the node

### Notes for SecondBrain

```markdown
## Research Publications

- [Title](url) — *[Journal]*, [year]. [one-sentence summary]
- h-index: [N] | Citations: [N] (as of [year])
- Research focus: [2-3 word descriptor]

## Collaborators (from publications)

- [Co-author Name] ([Institution]) — co-authored [N] papers
```

---

## Tier 4: Entrepreneur

**Trigger signals:**
- "Founder", "Co-founder", "CEO" at a startup
- Company is < 10 years old or still private
- Crunchbase profile exists
- Product Hunt launch found
- Startup news coverage (TechCrunch, VentureBeat, etc.)

### Search Patterns

```
"[Full Name]" founder OR "co-founder"
"[Full Name]" site:crunchbase.com
"[Full Name]" site:angel.co
"[Company Name]" site:producthunt.com
"[Full Name]" "[Company]" funding OR "Series A" OR seed
"[Full Name]" startup story OR "how we built"
```

### Sources to Hit

| Source | What to look for |
|--------|-----------------|
| Crunchbase | Funding rounds, investors, company description |
| AngelList/Wellfound | Team, investors, job posts |
| Product Hunt | Launch date, upvotes, tagline, comments |
| TechCrunch / VentureBeat | Funding announcements, interviews |
| Company "About" page | Founding story, mission, team |
| Y Combinator / Techstars | If batch alumni, batch year |

### Extraction Targets

- Company name, founding year, stage (seed/Series A/etc.)
- Total funding raised + lead investors
- Product/service description (1-2 sentences)
- Accelerator/cohort (YC, Techstars, etc.)
- Co-founders → Neo4j `CO_FOUNDED` edges
- Key investors → Neo4j `INVESTED_IN` edges (Org → Company)

### Neo4j for Entrepreneurs

```cypher
// Company node
MERGE (co:Organization {name: "[Company]"})
SET co.type = "startup", co.founded = [year], co.stage = "[stage]"

// Founded relationship
MERGE (p)-[:FOUNDED {year: [year]}]->(co)

// Co-founder edges
MERGE (cofound:Person {name: "[Co-founder]"})
MERGE (cofound)-[:CO_FOUNDED]->(co)
MERGE (p)-[:CO_FOUNDED_WITH]->(cofound)

// Investor edges (if notable)
MERGE (inv:Organization {name: "[Investor]"})
MERGE (inv)-[:INVESTED_IN]->(co)
```

### Notes for SecondBrain

```markdown
## Ventures

- **[Company Name]** ([year]–present) — [one-sentence description]
  - Stage: [seed/Series A/etc.] | Raised: $[amount]
  - Co-founders: [names]
  - Backed by: [investors]
  - [Product Hunt link if available]
```

---

## Photo Confidence Scoring

Rate confidence before saving a photo:

| Confidence | Criteria | Action |
|------------|----------|--------|
| High (save) | Staff page URL contains their name, LinkedIn with exact name match, faculty bio page | Save + attach |
| Medium (save with flag) | Company team page, labeled conference speaker headshot | Save, note source |
| Low (skip) | Generic Google Images result, unclear attribution, common name | Skip, note "no confident photo found" |

Download command:
```bash
mkdir -p /Users/debra/SecondBrain/People/photos
curl -L -o "/Users/debra/SecondBrain/People/photos/[FirstLast].jpg" "[photo_url]"
```

---

## Common Failure Modes

- **Name collision**: Common names (e.g., "John Smith") may pull wrong person. Always cross-reference org + location before trusting results.
- **Outdated info**: LinkedIn often lags. Prefer company staff pages for current title.
- **Private individuals**: Some people have near-zero public footprint. Don't fabricate. Note "limited public presence" and move on.
- **Paywalled profiles**: LinkedIn often requires login. Use Google's cached snippets (`site:linkedin.com "[name]"`) to extract bio text without logging in.
- **Academic name variants**: Check for middle initial variants (e.g., "J. Smith", "John A. Smith"). Verify by cross-referencing institution.
