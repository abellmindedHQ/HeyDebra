# Dream Cycle #23 Proposals — 2026-04-29

## Summary
DC #23 found 10 items (5 high relevance), deep-dived 4 topics. Key themes: our infrastructure is aging (OC 8 versions behind, HA 5+ behind), supply chain security is a real threat to our stack, and Anthropic is shipping features that overlap with what we've built by hand. Alex has been silent 5 days. 30+ proposals from DC #19-22 remain unreviewed. This cycle focuses on high-impact, Debra-executable items rather than adding to the pile.

## Proposed Changes

### 1. Upgrade OpenClaw to 2026.4.27
**Category:** infrastructure
**Priority:** high
**Effort:** moderate
**Files affected:** system (npm global), openclaw.json (potential config changes)

**What:** Upgrade from 2026.4.19-beta.2 to 2026.4.27 (or latest stable). 8 releases behind includes security patches, asymmetric embeddings for memory_search, agent compaction, and non-image attachment staging.
**Why:** Security risk (multiple CVEs between versions). Asymmetric embeddings could meaningfully improve memory_search quality. Agent compaction reduces context bloat in long cron sessions like this one. Non-image attachment staging could fix BB attachment workarounds.
**Steps:**
```
1. Back up: cp ~/.openclaw/openclaw.json ~/.openclaw/openclaw.json.bak
2. Review breaking changes in changelog
3. npm install -g openclaw@latest
4. openclaw gateway restart
5. Verify: crons fire, BB works, memory_search works, all channels respond
```
**Risk:** Config format changes between 8 versions could break things. Mitigation: backup + test plan.

### 2. Run npm Audit Across All Projects
**Category:** infrastructure/security
**Priority:** high
**Effort:** trivial
**Files affected:** none (read-only audit)

**What:** Run `npm audit` in every project directory that has a node_modules. Flag any high/critical vulnerabilities. Specifically check for compromised packages from the Shai Hulud / axios / Bitwarden campaigns.
**Why:** The AI coding stack is now a primary attack target. We run multiple npm-based tools (OpenClaw, Paperclip, clawhub, various CLIs). The Vercel breach via a third-party AI tool is especially relevant since abellminded.com is on Vercel.
**Steps:**
```
1. find ~ -name "package-lock.json" -not -path "*/node_modules/*" | head -20
2. For each: cd <dir> && npm audit --json 2>/dev/null | jq '.metadata.vulnerabilities'
3. Flag any high/critical
4. Report findings in next GSD report
```

### 3. Fix Proposal Delivery Workflow
**Category:** workflow
**Priority:** high
**Effort:** trivial
**Files affected:** skills/dream-cycle/SKILL.md (delivery section), AGENTS.md (optional)

**What:** Stop treating proposals as a separate artifact that Alex has to go find. Instead: (1) embed top 1-2 proposals directly in the GSD report, (2) limit to one actionable proposal per day, (3) kill the separate "proposals ready" iMessage. The GSD report is the only channel where Alex has any engagement pattern.
**Why:** 5 consecutive dream cycles have identified this problem. 30+ proposals unreviewed. The current "save to file → mention in iMessage" pipeline has a 0% success rate. The medium is wrong.
**Diff preview:**
```markdown
# In SKILL.md Delivery section, replace:
- "Deliver summary via iMessage to Alex in the morning"
+ "Embed top 1-2 proposals in the next GSD report. Do NOT send a separate proposals message."
```

### 4. Implement Silence Protocol
**Category:** workflow
**Priority:** medium
**Effort:** trivial
**Files affected:** AGENTS.md (new section)

**What:** Add an escalation protocol for extended Alex silence:
- **24h:** Normal. Continue crons, flag anything urgent.
- **48h:** Switch to minimal comms (1 message/day max, time-critical only). Stop dream cycle summaries.
- **72h:** Prepare a compressed "when you surface" briefing. Pause non-essential crons.
- **5d+:** Briefing only. No new messages until Alex initiates.
**Why:** We're at day 5 of silence. I've been sending daily GSD reports, DC summaries, and heartbeat checks into the void. Alex's inbox is filling with Debra messages that compound the overwhelm when he returns.
**Diff preview:**
```markdown
## Silence Protocol
Add to AGENTS.md under a new "## Extended Silence" section
```

### 5. Follow SKILL.md Model Guidance (Sonnet for DC Phases 1-2)
**Category:** config/cost
**Priority:** medium
**Effort:** trivial
**Files affected:** cron config (dream-cycle model field)

**What:** The dream-cycle SKILL.md already specifies Sonnet for phases 1-2 and Opus for phases 3-4. We've been running the entire cycle on Opus. Follow the guidance: set the cron to launch on Sonnet, spawn Opus sub-agent for phases 3-4 only.
**Why:** Cost reduction. Phases 1-2 (web search aggregation, reflection) don't need Opus-level reasoning. This is the easiest "triager pattern" win.
**Implementation:** Update cron config model field to `anthropic/claude-sonnet-4-6`, have the SKILL.md note that Phase 3 should spawn with model override to Opus.

### 6. Verify BB Port and Update TOOLS.md
**Category:** memory
**Priority:** medium
**Effort:** trivial
**Files affected:** TOOLS.md

**What:** DC #21 flagged BB port discrepancy (1234 vs 1235). Verify current live port and update TOOLS.md if stale.
**Why:** Memory accuracy. If a cron or session uses the wrong port, BB calls silently fail.
**Steps:** `curl -s http://localhost:1234/api/v1/server/info | head -5` and `curl -s http://localhost:1235/api/v1/server/info | head -5`

### 7. Update TOOLS.md Claude Code Bug Note
**Category:** memory
**Priority:** low
**Effort:** trivial
**Files affected:** TOOLS.md

**What:** Update the Claude Code git reset bug note. The Apr 23 Anthropic postmortem confirms issues were fixed in v2.1.116. Note should reference the fix version and recommend verifying our CC version.
**Why:** Stale TOOLS.md notes lead to unnecessary caution or wrong assumptions.

## Deferred / Watching

| Item | Why Deferred | Revisit |
|------|-------------|---------|
| Anthropic Managed Agents evaluation | Architecture is interesting but we're not ready to migrate. Our hand-built system works. | June |
| HA upgrade to 2026.4 | 5+ versions behind but not blocking anything. Need to plan carefully with 197 components. | Post-Amsterdam trip |
| Neo4j restart | Flagged since March. Should just do it. But want Alex's OK since it touches SecondBrain infra. | Next Alex interaction |
| Continuous npm monitoring (Snyk/Socket) | Worth doing but needs Alex to decide on tooling preference | Post-audit |
| Full triager pattern implementation | Start with DC model split, evaluate before broader rollout | June |
| Graph memory architecture (Agentic GraphRAG) | Validates our Neo4j + QMD approach. Revisit when Neo4j is back online. | Q3 |

## Meta
- Research scan: 10 findings, 10 kept (5 high, 4 medium, 1 low)
- Self-reflection: 4 issues identified (proposal delivery, silence protocol, infrastructure stagnation, approaching deadlines)
- Memory verification: 10 probes, 9 passed, 1 flagged (BB port)
- Corrections analysis: 0 new corrections (8+ day streak)
- Deep dives: 4 topics (Managed Agents, OC upgrade, supply chain security, triager pattern)
- Proposals: 7 changes (3 high, 3 medium, 1 low)
- Estimated cost: ~$3-4 (Opus for full cycle)
- Cycle duration: ~20 min
