# Dream Cycle #19 Proposals — 2026-04-25

## Summary
DC#19 focused on the Anthropic post-mortem revealing Claude Code degradation was harness bugs (not model regression), OC 2026.4.24 with search score transparency and heartbeat fixes, the verification-as-bottleneck trend, and Neo4j Aura Agent platform going GA. 5 days with zero corrections — behavioral patterns are internalized. The big strategic question: is it time to re-evaluate Opus 4.7? The post-mortem strongly suggests the 52% vuln rate was measured during the bug window. Proposing a sandboxed test.

## Proposed Changes

### 1. Upgrade OpenClaw to 2026.4.24
**Category:** infrastructure
**Priority:** high
**Effort:** moderate
**Files affected:** system (npm global), ~/.openclaw/config/openclaw.json

**What:** Upgrade from 2026.4.19-beta.2 to 2026.4.24. Key gains: memory-core hybrid search exposes vectorScore + textScore (debug search quality), heartbeat timer clamp (prevents potential 1ms crash loops), browser automation improvements (coordinate clicks, 60s action budget), MCP idle session eviction.
**Why:** 5 days behind. Heartbeat fix may resolve silent issues. Search score transparency directly helps improve memory_search accuracy. Browser improvements help social cleanup and LinkedIn workflows.
**Risk:** macOS users reporting mixed-version/unhealthy state after upgrade. Mitigate with config backup and off-hours timing.
**When:** Mon/Tue next week. NOT before weekend (Avie custody, TSA PreCheck).

### 2. Test Opus 4.7 in Sandboxed Session
**Category:** infrastructure
**Priority:** high
**Effort:** moderate
**Files affected:** gateway config (if approved), TOOLS.md, MEMORY.md

**What:** Run a representative workload (coding task, message drafting, research, memory operations) on Opus 4.7 in an isolated session. Compare quality, token usage, latency, and self-verification behavior against Opus 4.6 baseline.
**Why:** The Anthropic post-mortem strongly suggests the 52% vuln rate from Forbes/BridgeMind was an artifact of harness bugs active during testing. Opus 4.7 offers xhigh default reasoning, self-verification, and enhanced vision. These directly address our chronic report-without-verifying pattern. Staying on 4.6 out of caution that may no longer be warranted.
**Risk:** Undiscovered issues. Mythos was kept from public release for safety reasons, and Opus 4.7 has intentionally constrained cybersecurity capabilities. But for our use case (assistant work, not security research), this seems fine.
**When:** Next week, after OC upgrade. Requires Alex's approval to switch if test passes.

### 3. Fix Dream Cycle Delivery Workflow
**Category:** workflow
**Priority:** high
**Effort:** trivial
**Files affected:** skills/dream-cycle/SKILL.md

**What:** Change the delivery model: instead of staging a summary for morning delivery by another cron, have the dream cycle send the iMessage itself at completion (~midnight). Alex reads it when he wakes up. Remove the staging step entirely.
**Why:** DC#17 and DC#18 summaries were staged but never delivered (2+ days sitting unread). The stage-then-deliver model has a reliability gap: if the next-morning session doesn't pick up the staged summary, it just disappears. Sending at midnight is fine — Alex's phone is in DND mode overnight.
**Diff preview:**
```
# In SKILL.md Delivery section, replace:
"Deliver summary via iMessage to Alex in the morning (or announce in session)"
# With:
"Send summary via iMessage to Alex immediately upon completion. He'll read it when he wakes up."
```

### 4. Update TOOLS.md Claude Code Version Guidance
**Category:** memory
**Priority:** medium
**Effort:** trivial
**Files affected:** TOOLS.md

**What:** Update the Claude Code git reset bug note. Current note references v2.1.87. The post-mortem confirms all harness fixes are in v2.1.116+. Add note about the three specific bugs and their fix dates.
**Diff preview:**
```
### ⚠️ Claude Code Harness Bugs (Updated 2026-04-25)
- v2.1.87: git reset --hard bug (issue #40710, status unknown)
- v2.1.116+ (Apr 20, 2026): ALL harness quality bugs fixed:
  - Reasoning effort restored to high/xhigh (was silently downgraded to medium Mar 4)
  - Caching bug fixed (was clearing thinking every turn, not just on idle resume)
  - Verbosity system prompt reverted (was capping responses at 25/100 words)
- ALWAYS use v2.1.116+ or later
- Source: anthropic.com/engineering/april-23-postmortem
```

### 5. Bundle Top Proposals Into GSD Reports
**Category:** workflow
**Priority:** medium
**Effort:** moderate
**Files affected:** skills/gsd-agent/SKILL.md (or equivalent)

**What:** Add a "Dream Cycle Highlights" section to each GSD report that surfaces the top 2-3 proposals from the most recent dream cycle. This puts proposals where Alex already looks instead of in files he never reads.
**Why:** DC#14 through DC#19 have generated 30+ proposals. None reviewed. The proposals are good work but invisible. Alex reads GSD reports (they're delivered via iMessage). Embedding the top proposals there solves the delivery problem.
**Diff preview:**
```
## Dream Cycle Highlights (from last night)
• [Top proposal one-liner and priority]
• [Top proposal one-liner and priority]
• Full proposals: memory/dream-cycle/YYYY-MM-DD-proposals.md
```

### 6. Update MEMORY.md: Opus 4.7 Vulnerability Assessment
**Category:** memory
**Priority:** medium
**Effort:** trivial
**Files affected:** MEMORY.md

**What:** Add context to the Opus 4.7 safety assessment noting the post-mortem findings. Don't remove the caution entirely — update it with the new evidence so future sessions have accurate context.
**Diff preview:**
```
# Add to Critical Lessons or Key Infrastructure:
- **Opus 4.7 re-evaluation (Apr 25):** The 52% vuln rate (Forbes/BridgeMind) was likely measured during the Claude Code harness bug period (Mar 4 - Apr 20). Anthropic post-mortem confirms degradation was caused by 3 product-layer bugs, not model regression. Opus 4.7 has xhigh default reasoning and self-verification. Sandboxed testing recommended before switching.
```

## Deferred / Watching

| Item | Why Deferred | Revisit |
|------|-------------|---------|
| Neo4j Aura Agent evaluation | Neo4j itself needs to be running first. Get local instance stable before evaluating managed alternatives. | Post-Amsterdam (May) |
| Google Meet plugin | Interesting but requires Chrome + Google auth setup. Not urgent. | When Alex has a meeting he wants monitored |
| GLM-5.1 for Paperclip | 8-hour autonomous coding model, open weights. But Paperclip's adapter is broken — fix that first. | When Paperclip is stable |
| Deploy-verify skill | Automated verification for deployments. Good idea, needs design. | After OC upgrade |
| Adversarial self-review workflow | Red-team pass before finalizing work. Promising but adds complexity. | After verification checklist proven |

## Meta
- Research scan: 10 findings, 10 kept (4 high, 5 medium, 1 low-medium)
- Self-reflection: 5 issues identified (delivery lag, proposal backlog, Paperclip stagnation, stale overdues, dropped thread)
- Memory verification: 8 probes, 7 passed, 1 flagged (Opus 4.7 vuln data stale)
- Deep dives: 4 topics researched (post-mortem, OC 2026.4.24, verification bottleneck, Neo4j Aura)
- Proposals: 6 changes suggested (3 high, 3 medium)
- Corrections: 0 new (5+ day clean streak, best since launch)
- Estimated cost: ~$3.50 (Opus 4.6 for research-heavy cycle)
- Cycle duration: ~20 min
