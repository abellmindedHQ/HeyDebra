---
name: night-swimming-contacts
description: Contact triage skill for Google Contacts. Pulls all contacts, classifies them into relationship tiers, cross-references with Neo4j people graph, identifies enrichment candidates, and generates a tiered report. Use when asked to "triage contacts", "tier my contacts", "run night swimming contacts", or as part of a nightly batch.
---

# night-swimming-contacts

Pull Google Contacts, classify into relationship tiers, cross-reference with Neo4j, and generate a contact health report saved to SecondBrain.

---

## Inputs

- **Account** (default: `alexander.o.abell@gmail.com`): Google account for contacts
- **Report date** (default: today): YYYY-MM-DD for the output filename
- **Mode**: `full` (re-tier everything) | `new-only` (only contacts added since last run)

---

## Config

```
Tool:    gog CLI (Google Workspace CLI)
Access:  Google Contacts read
Neo4j:   bolt://localhost:7687 / neo4j / secondbrain2026
Output:  /Users/debra/SecondBrain/Reflections/Daily/YYYY-MM-DD-contacts-triage.md
```

---

## Relationship Tiers

### Tier 1 — Inner Circle
Real, active relationships. People Alex actually talks to or thinks about.
- Signals: known name, recent interaction context, family, close friends, actual phone use
- Action: Keep enriched. If missing phone/email/org, flag for enrichment.
- Examples: Hannah, Annika, Sallijo, Chelsea, Jay, Brandon

### Tier 2 — Professional Network
Colleagues, collaborators, clients, former teammates. Real but not intimate.
- Signals: ORNL context, startup/tech world, LinkedIn mutual, clear org/title
- Action: Keep. Enrich if has potential value. Flag for people-intel if interesting.
- Examples: ORNL colleagues, fellow founders, contractors

### Tier 3 — Acquaintance
Met once or twice, vaguely remember, might reconnect someday.
- Signals: Single context note, conference/event pickup, unclear how they know each other
- Action: Keep but lower priority. Note last contact date if available.

### Tier 4 — LinkedIn Import
Mass-imported via LinkedIn sync. Have no personal connection data.
- Signals: Exactly "LinkedIn" as source, no phone, no email, no notes, name + company only
- Action: Flag for review. Don't delete — but don't pretend these are real relationships.
- Sub-tier: If they show up in Neo4j with a real relationship edge → promote to Tier 2-3

### Tier 5 — Noise / Stubs
Barely-there entries: single name, no context, auto-created, likely duplicates or spam.
- Signals: No phone, no email, no org, no notes. First name only or just an email address.
- Action: Flag for deletion review. Do NOT delete automatically.

---

## Workflow

### Step 1 — Pull All Contacts

```bash
gog contacts list --account alexander.o.abell@gmail.com --format json --limit 2000
```

Parse fields: resourceName, givenName, familyName, emailAddresses, phoneNumbers, organizations, biographies (notes), sources, metadata.updateTime.

### Step 2 — Cross-Reference Neo4j

For each contact with a real name, query Neo4j for existing Person nodes:

```bash
cypher-shell -a bolt://localhost:7687 -u neo4j -p secondbrain2026 << 'EOF'
MATCH (p:Person)
RETURN p.name, p.email, p.phone, p.org, p.title, p.relationship_type
ORDER BY p.name
EOF
```

Build a lookup map: `name → neo4j_data`. Used to:
- Upgrade tier for LinkedIn imports that have Neo4j relationship edges
- Flag contacts with Neo4j records but no Google Contact (gap to fill)
- Identify contacts with Google Contact but no Neo4j node (enrich candidates)

### Step 3 — Classify Each Contact

For each contact, assign tier 1–5 based on:
1. Has phone number? (+1 signal)
2. Has personal email (not @linkedin, @noreply)? (+1 signal)
3. Has notes/bio with real context? (+1 signal)
4. Has org + title? (+1 signal)
5. Exists in Neo4j with relationship edges? (+2 signals)
6. Source = "CONTACT" (manually added) vs "DIRECTORY" (auto-sync)? (+1 if manual)
7. Name is in Alex's known people list (from USER.md / MEMORY.md context)? → Tier 1

Score → Tier:
- 4+ signals → Tier 1 or 2 (use relationship context to decide)
- 2-3 signals → Tier 2 or 3
- 1 signal → Tier 3 or 4
- 0 signals + LinkedIn source → Tier 4
- 0 signals, no source info → Tier 5

### Step 4 — Identify Enrichment Candidates

Flag contacts for people-intel enrichment if:
- Tier 1-2 but missing phone OR email OR org
- Has Neo4j relationship edges but SecondBrain markdown file doesn't exist at `/Users/debra/SecondBrain/People/[FirstLast].md`
- Tier 4 contact that appears in Neo4j (should be promoted + enriched)

```bash
# Check for SecondBrain file
ls "/Users/debra/SecondBrain/People/" | grep -i "[name]"
```

### Step 5 — Generate Report

Save to `/Users/debra/SecondBrain/Reflections/Daily/YYYY-MM-DD-contacts-triage.md`:

```markdown
---
date: YYYY-MM-DD
type: contacts-triage
account: alexander.o.abell@gmail.com
---

# 👥 Contacts Triage — YYYY-MM-DD

**Total contacts:** N | **Tier 1:** N | **Tier 2:** N | **Tier 3:** N | **Tier 4:** N | **Tier 5:** N
**Enrichment candidates:** N | **Neo4j gaps:** N | **Noise/stubs:** N

---

## 🥇 Tier 1 — Inner Circle (N)

| Name | Phone | Email | Org | Neo4j | SecondBrain | Notes |
|------|-------|-------|-----|-------|-------------|-------|
| [Name] | ✅/❌ | ✅/❌ | [org] | ✅/❌ | ✅/❌ | [any gaps] |

## 💼 Tier 2 — Professional Network (N)

[Same table format]

## 🤝 Tier 3 — Acquaintances (N)

[Same table format — condensed]

## 📥 Tier 4 — LinkedIn Imports (N)

[List with flag for any that have Neo4j promotion candidates]

## 🗑️ Tier 5 — Noise / Stubs (N)

[List — candidates for deletion review]

---

## 🌱 Enrichment Queue (N contacts)

These have real relationships but incomplete data:

- **[Name]** — missing: [phone/email/org/SecondBrain file] | Neo4j: [yes/no]
  → Suggested action: `spawn subagent: research [Name] — [context]`

---

## 🕳️ Neo4j Gaps (N)

Contacts in Google with no Neo4j node:
- [Name] ([org]) — has real signals, should be in graph

---

## 🔎 Interesting Findings

- [Any patterns, notable missing people, relationship clusters, etc.]

---

*Generated by night-swimming-contacts skill*
```

### Step 6 — Summary to User

```
👥 Contacts triage complete — YYYY-MM-DD
- Total: N contacts processed
- Tier 1 (Inner Circle): N
- Tier 2 (Professional): N  
- Tier 4 (LinkedIn noise): N
- Tier 5 (Stubs/noise): N
- Enrichment queue: N candidates flagged
- Neo4j gaps: N contacts missing from graph
- Report: SecondBrain/Reflections/Daily/YYYY-MM-DD-contacts-triage.md
```

---

## Edge Cases

- **Duplicate contacts**: Flag pairs where names are very similar (fuzzy match) — list in report, don't merge automatically
- **Large contact lists (> 2000)**: Process in batches, note if gog paginates
- **Neo4j connection failure**: Continue without cross-reference, note in report that Neo4j was unavailable
- **Contacts with only an email address**: Tier 5 unless email domain suggests a real relationship (e.g., ORNL domain → Tier 3 minimum)
