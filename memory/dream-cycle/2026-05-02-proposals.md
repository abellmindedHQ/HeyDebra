# Dream Cycle #27 Proposals — 2026-05-02

## Summary
27th consecutive dream cycle. Research scan found 10 items (4 high relevance): OC 2026.5.2 release, YourMemory biological decay, escalating npm supply chain attacks, Neo4j Context Graphs, and Claude Opus 4.7. Self-reflection identified the meta-pattern of **passivity during Alex's silence** as the dominant issue. 76+ hours of idle time with zero proactive work on infrastructure, inbox, or Amsterdam prep. BB send broken 3 days with zero fix attempts. Proposing 8 changes, 4 high priority, all executable during Alex's Amsterdam trip window.

## Proposed Changes

### 1. Upgrade OpenClaw to 2026.5.2
**Category:** infrastructure
**Priority:** high
**Effort:** moderate
**Files affected:** global npm install, openclaw.json (doctor --fix migration)

**What:** Upgrade from 2026.4.19-beta.2 to 2026.5.2 (15 releases). Run `openclaw doctor --fix` for config migration. Verify BB plugin, cron execution, gateway performance.
**Why:** 15 releases behind. Plugin externalization means future upgrades get easier once we cross this bridge. Gateway startup optimization and plugin descriptor caching directly improve our heavy-skill setup. Supply chain security patches included.
**When:** During Alex's Amsterdam trip (May 4+) to minimize impact.
**Diff preview:**
```bash
npm install -g openclaw@2026.5.2
openclaw doctor --fix
openclaw gateway restart
```

### 2. Upgrade to Claude Opus 4.7
**Category:** config
**Priority:** high
**Effort:** trivial
**Files affected:** openclaw.json, MEMORY.md (update model reference)

**What:** Change primary model from `anthropic/claude-opus-4-6` to `anthropic/claude-opus-4-7`.
**Why:** Self-verification improvements directly address our report-without-verifying pattern (6x corrections). Better file-system memory. Same pricing. "More opinionated" aligns with SOUL.md's design. Task budgets could optimize token costs.
**Diff preview:**
```json
// openclaw.json
- "model": "anthropic/claude-opus-4-6"
+ "model": "anthropic/claude-opus-4-7"
```

### 3. Run npm Security Audit
**Category:** infrastructure
**Priority:** high
**Effort:** trivial
**Files affected:** none (diagnostic only)

**What:** Run `npm audit` on global OpenClaw install and workspace. Review results. Set up daily audit cron.
**Why:** npm supply chain attacks now specifically target AI agent configurations. Axios (100M DL/week) was compromised in March. Bitwarden CLI hijacked in April targeting AI tool configs. We have never run an audit. This is negligence.
**Diff preview:**
```bash
npm audit --global
cd ~/.openclaw/workspace && npm audit 2>/dev/null || echo "no package.json"
# Review output, address any critical/high findings
```

### 4. Restart Neo4j
**Category:** infrastructure
**Priority:** high
**Effort:** trivial
**Files affected:** none

**What:** `brew services start neo4j`. Verify data integrity with test queries. Re-sync with SecondBrain vault if needed.
**Why:** Down 35+ days. Neo4j is building exactly the context graph infrastructure we need. Every day it's down is a day our knowledge graph atrophies. This is a one-command fix. The fact that it's been proposed in 5+ dream cycles and never done is the problem this proposal is trying to solve.
**Diff preview:**
```bash
brew services start neo4j
# Wait 10s
curl -s http://localhost:7474 | head -5
cypher-shell -u neo4j -p secondbrain2026 "MATCH (n) RETURN count(n)"
```

### 5. Fix BB Port Reference in TOOLS.md
**Category:** memory
**Priority:** medium
**Effort:** trivial
**Files affected:** TOOLS.md

**What:** Update BlueBubbles server reference from 1235 to 1234 (or verify which is correct and standardize).
**Why:** 4th consecutive dream cycle flagging this. Memory verification catches it every time. It's a one-line edit. The fact that we can't fix a one-line typo is symptomatic of the passivity problem.
**Diff preview:**
```markdown
- Server: localhost:1235 (same machine)
+ Server: localhost:1234 (same machine)
```

### 6. Implement Proactive Maintenance Window
**Category:** workflow
**Priority:** medium
**Effort:** moderate
**Files affected:** AGENTS.md (add section), cron config

**What:** Add a daily 2-hour "maintenance window" cron (2 PM ET when Alex is typically at work) that checks infrastructure health and performs trivial-effort fixes automatically:
- BB send test (restart if broken)
- Neo4j status (restart if down)
- `npm audit` (flag criticals)
- Stale inbox check (report if >7 days untriaged)
- Dream cycle proposal auto-archive (>14 days unreviewed = archived)

**Why:** The passivity-during-silence pattern is systemic. I need a forcing function for proactive work that doesn't depend on Alex engaging. This cron would catch exactly the issues that stagnated this week.
**Diff preview:** New cron job definition + AGENTS.md section under "Do freely."

### 7. Auto-Archive Stale Dream Cycle Proposals
**Category:** workflow
**Priority:** medium
**Effort:** trivial
**Files affected:** memory/dream-cycle/ (cleanup), dream-cycle SKILL.md (add archival step)

**What:** Proposals older than 14 days without action get moved to `memory/dream-cycle/archive/`. This applies biological decay thinking (finding #3) without requiring new infrastructure.
**Why:** 27 cycles × ~7 proposals each = ~189 proposals accumulating. Zero reviewed. This is noise, not signal. Auto-archival respects the "if it wasn't important enough to act on in 2 weeks, it's not important" heuristic. Important proposals recur naturally (like this OC upgrade, which has been proposed 5+ times).
**Diff preview:**
```bash
# Add to dream cycle Phase 4:
mkdir -p memory/dream-cycle/archive
find memory/dream-cycle/ -name "*-proposals.md" -mtime +14 -exec mv {} memory/dream-cycle/archive/ \;
```

### 8. Embed Top Proposals in GSD Reports
**Category:** workflow
**Priority:** medium
**Effort:** moderate
**Files affected:** gsd-agent SKILL.md

**What:** GSD report includes a "Dream Cycle Highlights" section with the top 2-3 proposals from the most recent dream cycle. Not a separate file Alex has to go find — right there in the report he already reads.
**Why:** The proposal delivery pipeline (save to file → mention in iMessage → Alex ignores) is dead. GSD reports are the one artifact Alex actually engages with. Embedding proposals there gives them a fighting chance. This was proposed in DC #25 and DC #26. Third time's the charm?

## Deferred / Watching

| Item | Why Deferred |
|------|-------------|
| YourMemory integration (Phase B/C) | Need OC upgrade first. Evaluate after Phase A (manual decay) runs for 2 weeks. |
| Claude for Creative Work connectors | Interesting for Hannah's music / brand work but not actionable now |
| HA Docker migration | Long-running project, not urgent |
| Cloudflare Agent Memory | Cloud-hosted, we're local-first |
| IBM Granite 4.1 | No immediate use case |
| Home automation AI / Matter 2.0 | Interesting but HA is already 5 months behind |

## Meta
- Research scan: 30+ items reviewed, 10 kept (4 high, 4 medium, 2 low-medium)
- Self-reflection: 6 issues identified (passivity dominant theme)
- Memory verification: 10 probes, 9 passed, 1 flagged (BB port, 4th consecutive)
- Deep dives: 5 topics researched
- Proposals: 8 changes suggested (4 high, 4 medium)
- Estimated cost: ~$3.50 (model usage for research + synthesis)
- Cycle duration: ~25 min
- **Consecutive cycles: 27**
- **Proposals reviewed by Alex: still 0**
