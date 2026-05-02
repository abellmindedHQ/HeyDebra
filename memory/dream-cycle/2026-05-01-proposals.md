# Dream Cycle #26 Proposals — 2026-05-01

## Summary
26th consecutive nightly cycle. Big headlines: Opus 4.7 is out and directly addresses our worst correction patterns (self-verification, tool error recovery). The Shai-Hulud npm supply chain campaign is now targeting AI coding agent configs as a persistence vector, which is directly relevant since we use Claude Code. We're 12 releases behind on OpenClaw. GraphRAG is going mainstream, validating our Neo4j+Obsidian+qmd architecture, but Neo4j has been down for 34 days. On self-reflection: 12+ day clean streak on corrections, but proposal delivery is still broken (26 cycles, 0 reviews) and BB send is unreliable.

## Proposed Changes

### 1. Upgrade Model to Claude Opus 4.7
**Category:** config
**Priority:** high
**Effort:** trivial (after OC upgrade)
**Files affected:** openclaw.json, MEMORY.md, TOOLS.md

**What:** Change primary model from `anthropic/claude-opus-4-6` to `anthropic/claude-opus-4-7`.
**Why:** Opus 4.7 has self-verification (addresses 6x report-without-verifying pattern), better tool error recovery (fewer failed crons), +14% multi-step accuracy at fewer tokens and 1/3 tool errors. Same pricing. Low-effort 4.7 ≈ medium-effort 4.6 = potential cost savings.
**Diff preview:**
```json
// openclaw.json
- "model": "anthropic/claude-opus-4-6"
+ "model": "anthropic/claude-opus-4-7"
```
**Prerequisite:** OC upgrade to 2026.4.29+ for thinking parity.

### 2. Upgrade OpenClaw to 2026.4.30
**Category:** infrastructure
**Priority:** high
**Effort:** moderate
**Files affected:** global npm package, gateway config

**What:** Upgrade from 2026.4.19-beta.2 to latest (2026.4.30). 12 releases behind.
**Why:** Security patches (SSRF bypass fixes, OpenGrep), people-aware wiki memory, Opus 4.7 thinking parity, stale-session recovery, WhatsApp/BB channel fixes. Being 12 releases behind with active supply chain attacks targeting npm is a security risk.
**Diff preview:**
```bash
cp ~/.openclaw/openclaw.json ~/.openclaw/openclaw.json.bak
npm update -g openclaw
openclaw doctor --fix
openclaw gateway restart
```
**Risk:** tools.exec/tools.fs profile change in 2026.4.29 may need config adjustment. Back up first.

### 3. Run npm Security Audit
**Category:** infrastructure
**Priority:** high
**Effort:** trivial
**Files affected:** none (read-only)

**What:** Run `npm audit --global` immediately. Check for `.claude/settings.json` and `.vscode/tasks.json` persistence files in cloned repos. Set up weekly audit cron.
**Why:** Mini Shai-Hulud campaign (TeamPCP) is actively compromising npm packages and now targeting AI coding agent configs (Claude Code SessionStart hooks). Our Mac mini has 1Password CLI, GitHub creds, API keys. A compromised package could exfiltrate everything.
**Diff preview:**
```bash
npm audit --global
find ~/Projects -name ".claude" -path "*settings.json" -exec grep -l "SessionStart" {} \;
find ~/Projects -name "tasks.json" -path "*/.vscode/*" -exec grep -l "runOn" {} \;
```

### 4. Restart Neo4j
**Category:** infrastructure
**Priority:** medium
**Effort:** trivial
**Files affected:** none

**What:** Restart Neo4j (down 34 days). Verify data integrity. Re-enable graph queries.
**Why:** GraphRAG is becoming industry standard. Our architecture (Neo4j + Obsidian + qmd) is exactly the hybrid approach everyone is converging on. But the graph layer has been offline for over a month. Embarrassing.
**Diff preview:**
```bash
brew services start neo4j
# Verify
cypher-shell -u neo4j -p secondbrain2026 "MATCH (n) RETURN count(n)"
```

### 5. Fix TOOLS.md BB Port Discrepancy
**Category:** memory
**Priority:** medium
**Effort:** trivial
**Files affected:** TOOLS.md

**What:** Fix BlueBubbles server port reference from 1235 to 1234. This discrepancy has been flagged in 3 consecutive dream cycles without being fixed.
**Why:** Incorrect documentation leads to failed BB interactions. Memory verification has flagged this in DC #23, #25, and #26.
**Diff preview:**
```
- Server: localhost:1235 (same machine)
+ Server: localhost:1234 (same machine)
```

### 6. Embed Top Proposals in GSD Reports
**Category:** workflow
**Priority:** medium
**Effort:** moderate
**Files affected:** skills/gsd-agent/SKILL.md

**What:** Add a "Quick Wins from Dream Cycle" section to the morning GSD report. Include top 1-2 proposals with one-liner description + effort estimate.
**Why:** 26 cycles of proposals, 0 reviews. Alex reads GSD reports but never opens dream-cycle proposal files. If proposals ride the GSD, they have a chance of being seen. This was proposed in DC #25 and still not implemented.
**Format:**
```markdown
## 🌙 Dream Cycle Quick Wins
• **Upgrade to Opus 4.7** — better self-verification, same price [trivial]
• **Run npm audit** — supply chain attacks targeting AI agent configs [trivial]
```

### 7. Fix BB Send Reliability
**Category:** infrastructure
**Priority:** medium
**Effort:** moderate
**Files affected:** BB server config

**What:** Diagnose and fix BB send API hanging (since Apr 30). Test restart of BB server and Messages.app. Document recovery procedure.
**Why:** GSD report delivery has failed for 2 days. iMessage is our primary delivery channel for Alex. If sends don't work, all GSD reports, dream cycle summaries, and reminders are dead letters.
**Diff preview:**
```bash
# Test BB health
curl -s http://localhost:1234/api/v1/ping
# Restart if needed
brew services restart bluebubbles
# Test send
curl -X POST http://localhost:1234/api/v1/message/text ...
```

## Deferred / Watching

- **Grok 4.3 as fallback model** — compelling pricing ($1.25/$2.50 per MTok), 1M context. Test when time allows.
- **Claude Security** — Enterprise-only codebase scanner. Watch for Team/Max rollout.
- **Apple Home Hub / HomePad** — smart home display with A18 chip. Track for HA ecosystem planning.
- **Mem0g / GraphRAG pipeline** — graph-enhanced memory. Queue after Neo4j restart.
- **xAI Custom Voices** — voice cloning from 120s audio. Potential ElevenLabs backup.

## Meta
- Research scan: 10 findings, 10 kept (4 high, 4 medium, 2 low)
- Self-reflection: 5 issues identified (BB send, reorg escalation, proposal delivery, infra stagnation, passivity)
- Memory verification: 10 probes, 9 passed, 1 flagged (BB port discrepancy, 3rd consecutive flag)
- Corrections: 0 new in 12+ days. All major patterns already promoted.
- Deep dives: 5 topics researched (Opus 4.7, Shai-Hulud, OC upgrade, GraphRAG, Grok 4.3)
- Proposals: 7 changes suggested (3 high, 4 medium)
- Cycle duration: ~25 min
