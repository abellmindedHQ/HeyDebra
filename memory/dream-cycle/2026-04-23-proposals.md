# Dream Cycle Proposals — 2026-04-23

## Summary
Cycle #17. Quietest correction period in weeks (0 new corrections Apr 22-23). Research highlighted: Opus 4.7 vuln data confirmed again, OpenClaw 2026.4.22 has features we want (Active Memory plugin, per-group systemPrompts, diagnostics), Neo4j agent-memory library is a near-perfect architecture match, and MCP vulnerability is permanent by Anthropic's design. Claude Mythos unauthorized access is a notable security event. Top proposals: enable Active Memory plugin (after OC upgrade), bind MCP to localhost, and investigate Neo4j agent-memory for weekend project.

## Proposed Changes

### 1. Upgrade OpenClaw to 2026.4.22
**Category:** infrastructure
**Priority:** high
**Effort:** moderate
**Files affected:** Gateway config, possibly openclaw.json

**What:** Upgrade from 2026.4.19-beta.2 to 2026.4.22. Key features we want: Active Memory plugin, WhatsApp per-group systemPrompt, diagnostics export, `/models add` from chat.
**Why:** Enables proposal #2 (Active Memory) and unblocks several quality-of-life improvements. We've been 3 versions behind for 4 days.
**Risk:** Breaking changes to crons, skills, or channel configs. Mitigate by reviewing release notes and testing crons post-upgrade.

### 2. Enable Active Memory Plugin (after upgrade)
**Category:** config
**Priority:** high
**Effort:** trivial
**Files affected:** openclaw.json

**What:** Enable the Active Memory plugin in "recent" mode, targeted at the main agent.
**Why:** Directly addresses the "search memory before asking Alex" pattern (know-your-context correction, documented 5+ times). Automates context retrieval that I currently forget to do manually.
**Diff preview:**
```json
// Add to openclaw.json
{
  "plugins": {
    "active-memory": {
      "enabled": true,
      "target": ["main"],
      "mode": "recent"
    }
  }
}
```
**Monitoring:** Use `/verbose` for first week to verify retrieval quality. Track token cost delta.

### 3. Bind Kapture MCP to Localhost
**Category:** infrastructure/security
**Priority:** high
**Effort:** trivial
**Files affected:** Kapture MCP config, TOOLS.md

**What:** Change Kapture MCP bind address from 0.0.0.0 to 127.0.0.1. MCP STDIO vulnerability is confirmed permanent — Anthropic won't fix.
**Why:** Port 61822 is currently exposed on all interfaces (flagged in security hardening Apr 21). Any LAN device could potentially exploit MCP's unsafe STDIO defaults. There's no reason for MCP to be reachable beyond localhost.
**Note:** This qualifies as trivial security fix under dream cycle self-apply policy, but flagging for approval given it changes a service bind.

### 4. Investigate Neo4j Agent-Memory Library
**Category:** infrastructure
**Priority:** medium
**Effort:** significant (research phase: moderate)
**Files affected:** None yet (investigation only)

**What:** Install and evaluate `neo4j-agent-memory` against our existing Neo4j instance. Start with reasoning traces only (record how problems were solved, link to corrections).
**Why:** Maps directly to our SecondBrain architecture. Reasoning memory could help break the repeat-correction cycle. Entity extraction could automate memory management. But need to verify schema compatibility first.
**Next step:** `pip install neo4j-agent-memory`, connect to localhost:7474, create test namespace, try recording a few reasoning traces. Weekend project.

### 5. Fix Proposal Delivery Mechanism
**Category:** workflow
**Priority:** medium
**Effort:** trivial
**Files affected:** SKILL.md (dream-cycle), AGENTS.md

**What:** Instead of staging proposals in files and saying "ready when you want em," distill top 1-2 proposals into specific yes/no questions in the morning iMessage. Make proposals actionable in-chat.
**Why:** 21+ proposals unreviewed across 16 cycles. Alex doesn't read files on demand. He responds to direct questions in iMessage. The current delivery mechanism is broken by design.
**Diff preview:**
```
Morning message changes from:
"Proposals ready for review when you want em."

To:
"Quick yes/no: should I enable Auto Memory plugin? It'd search memory before each response so I stop asking you stuff I should already know. ~$0.50/day extra tokens."
```

### 6. Clean Up Stale Cron (Hero Video)
**Category:** config
**Priority:** low
**Effort:** trivial
**Files affected:** Cron config

**What:** Remove or fix the hero video cron that's looking for a nonexistent file path (hero-draft-v2.mp4).
**Why:** It runs and fails silently every cycle. Wastes a session. Already noted in Apr 21 daily log.

### 7. Pin Paperclip Agents to Opus 4.6
**Category:** infrastructure
**Priority:** medium
**Effort:** trivial
**Files affected:** Paperclip agent configs

**What:** Verify what Claude model the Paperclip agents use. If any are on Opus 4.7, pin to 4.6.
**Why:** Opus 4.7 has 52% code vulnerability rate. Ratchet (CTO) generates website code. Brand kit code could have security issues.

## Deferred / Watching

- **Opus 4.7 evaluation**: Don't upgrade until Anthropic addresses the vuln rate discrepancy. Monitor future Veracode/TrustedSec reports.
- **Claude Mythos**: Third-party breach is concerning but not actionable for us. Monitor for wider leak implications.
- **Microsoft Agent Framework 1.0**: Interesting for comparison but not immediately relevant. Could be useful if Paperclip limitations become blocking.
- **Full Neo4j agent-memory migration**: Don't attempt until: (1) Neo4j is stable, (2) initial reasoning trace experiment works, (3) SecondBrain schema is documented.
- **Per-group BB systemPrompts**: Available in OC 2026.4.22. Could customize behavior per group chat (more casual in KBUDDS, more professional in Jay chat). Queue after upgrade.

## Meta
- Research scan: 10 findings, 10 kept (5 high, 5 medium)
- Self-reflection: 5 issues identified, 0 new corrections (best period yet)
- Memory verification: 10 probes, 9 passed, 1 flagged (stale hero cron)
- Deep dives: 4 topics researched
- Proposals: 7 changes suggested (3 high, 3 medium, 1 low)
- Cycle duration: ~25m
- Correction trend: IMPROVING (0 new corrections in 2 days)
