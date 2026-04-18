# Dream Cycle Proposals — 2026-04-18

## Summary
Tonight's cycle yields proposals around dream-cycle governance, memory architecture, and privacy in our AI stack. All changes staged for Alex review.

## Proposed Changes

### 1. Memory Graph Sandbox (Phase 2+3)
**Category:** infrastructure
**Priority:** medium
**Effort:** moderate
**Files affected:** memory/dream-cycle/2026-04-18-research.md

**What:** Implement a sandboxed memory graph mockup (local-first) to test privacy-preserving indexing before production Neo4j

**Why:** Aligns with Phase 2/3 findings on local-first memory graphs

**Diff preview:**
```
- memory/dream-cycle/2026-04-18-research.md
+ memory/dream-cycle/memory-graph-sandbox/README.md
```

### 2. Phase 0 Preflight Script (Guardrail)
**Category:** workflow
**Priority:** high
**Effort:** moderate
**Files affected:** AGENTS.md, TOOLS.md

**What:** Add preflight.sh to perform quick last-10-message and pending-approval checks before outbound actions

**Why:** Enforces guardrails from Phase 2 reflections

### 3. Phase 4: Dream Cycle Review Channel
**Category:** workflow
**Priority:** medium
**Effort:** moderate
**Files affected:** memory/dream-cycle/2026-04-18-proposals.md

**What:** Add a concise review summary in a dedicated channel/message for Alex

**Why:** Solves delivery bottleneck by surfacing top 3 proposals

### 4. Be Particular Guardrails (pilot)
**Category:** infrastructure/workflow
**Priority:** low
**Effort:** moderate
**Files affected:** SOUL.md

**What:** Add guardrails around Be Particular automation to require explicit sign-offs

**Why:** Progressive autonomy with governance

### 5. Corrections Tagging Upgrade
**Category:** tooling
**Priority:** medium
**Files affected:** memory/corrections.md, TOOLS.md

**What:** Adopt pattern-key tagging for corrections, exportable summaries

**Why:** Improves Phase 2 analysis and triage

## Deferred / Watching
- None this cycle

## Meta
- Research scan: 3 findings kept
- Self-reflection: 3 issues identified
- Deep dives: 3 topics researched
- Proposals: 5 changes suggested
- Cost: ~$0.15
- Cycle duration: ~30m
