# Dream Cycle #18 Proposals — 2026-04-24

## Summary
Tonight's cycle surfaced critical new intel: Anthropic's post-mortem reveals the Opus 4.7 "vulnerability" data may have been an artifact of a harness bug, not inherent model weakness. Google's ReasoningBank validates our manual correction-learning pipeline and offers a path to automate it. OpenClaw 2026.4.23 has meaningful improvements worth upgrading to. No new corrections in 4 days — behavioral patterns are stable. The chronic message fragmentation issue remains structural.

## Proposed Changes

### 1. Upgrade OpenClaw to 2026.4.23
**Category:** infrastructure
**Priority:** high
**Effort:** trivial
**Files affected:** system (npm update)

**What:** Upgrade from 2026.4.19-beta.2 to 2026.4.23. Key features: configurable memory embedding context, forked context for sessions_spawn, broader image gen, security fixes.
**Why:** 5 versions behind. Memory search improvements and sub-agent context inheritance are directly useful. Security fix for cross-bot token replay is relevant since we expose the gateway.

### 2. Re-Evaluate Opus 4.7 Post-Fix
**Category:** config
**Priority:** high
**Effort:** moderate
**Files affected:** MEMORY.md, openclaw.json (if upgrading)

**What:** The Anthropic post-mortem (Apr 23) revealed that performance degradation was caused by 3 harness-level bugs, NOT model weight regression. The 52% vulnerability rate from Forbes/Veracode may have been measured during the degradation window. Wait 1 week for independent post-fix benchmarks, then reassess.
**Why:** If the vuln data was an artifact, we're leaving a 13% coding improvement and self-verification behavior on the table for no reason. Same price as 4.6.
**Action:** Add a "re-evaluate Opus 4.7 by May 1" reminder. Update MEMORY.md to note the post-mortem context.

### 3. Bundle Top 3 Proposals into GSD Reports
**Category:** workflow
**Priority:** high
**Effort:** trivial
**Files affected:** skills/gsd-agent/SKILL.md

**What:** Add a "Dream Cycle Highlights" section to the GSD report template that includes the top 3 unreviewed proposals from the latest dream cycle. This puts proposals where Alex actually looks.
**Why:** 25+ proposals across cycles #14-17 are unreviewed. Dream cycle files are not read by humans. GSD reports ARE read. Meet Alex where he is.

### 4. Auto-Deliver Dream Cycle Summary After 12h
**Category:** workflow
**Priority:** medium
**Effort:** trivial
**Files affected:** skills/dream-cycle/SKILL.md, cron config

**What:** If the morning summary hasn't been delivered 12 hours after generation, send it anyway via iMessage. Don't wait for Alex to surface.
**Why:** Dream cycle #17 summary has been undelivered for 2 days. The info gets stale. A push notification is low-risk and high-value.

### 5. Evaluate Google ReasoningBank for Memory Pipeline
**Category:** infrastructure
**Priority:** medium
**Effort:** significant
**Files affected:** None initially (evaluation only)

**What:** Clone ReasoningBank repo, evaluate locally, map our corrections.md entries to its structured format. Assess feasibility of integrating with OpenClaw session context.
**Why:** Our manual corrections→memory pipeline works but doesn't scale. ReasoningBank automates the same pattern with proven benchmarks (+8.3% WebArena, +4.6% SWE-Bench). This is Q2 project material.

### 6. Update MEMORY.md: Opus 4.7 Post-Mortem Context
**Category:** memory
**Priority:** medium
**Effort:** trivial
**Files affected:** MEMORY.md

**What:** Add note that the Opus 4.7 "52% vulnerability rate" may be unreliable — Anthropic's Apr 23 post-mortem showed harness-level bugs (not model) caused the degradation during the measurement period.
**Diff preview:**
```
Under "Key Infrastructure":
+ **Opus 4.7 re-evaluation needed:** The Apr 23 Anthropic post-mortem revealed that perceived degradation was caused by 3 harness bugs (reasoning effort, caching, verbosity), NOT model weight regression. The 52% vuln rate from Forbes may have been measured during this window. Re-evaluate after independent post-fix benchmarks (target: May 1).
```

## Deferred / Watching

- **Neo4j MemMachine:** Great concept for unified agent memory, but Neo4j has been down ~month. Evaluate after stability is restored.
- **NVIDIA NemoClaw (sandboxed OpenClaw):** Interesting for security hardening but adds complexity. Not urgent unless we experience a security incident.
- **Claude Design:** Could help with Abellminded brand assets. Low priority until brand kit issues are resolved.
- **Edge AI / Tuya Smart integration:** Alex's smart home setup could benefit but this is lifestyle, not urgent.
- **AI Agent Governance frameworks (HN trending):** We've been solving this manually. Industry catching up. Monitor for tools/standards we could adopt.

## Meta
- Research scan: 10 findings, 4 high relevance
- Self-reflection: 5 issues identified, 0 new corrections (best 4-day stretch)
- Memory verification: 8 probes, 7 passed, 1 flagged (Opus 4.7 vuln data potentially stale)
- Deep dives: 4 topics researched (Anthropic post-mortem, ReasoningBank, OC 2026.4.23, Neo4j MemMachine)
- Proposals: 6 changes suggested (3 high, 2 medium, 1 medium)
- Estimated cost: ~$3.50 (Opus 4.6 for full cycle)
- Cycle duration: ~20m
