# Dream Cycle Proposals — 2026-04-16

## Summary
Tonight's cycle yields structured, review-ready proposals across memory, tooling, and architecture to improve safety, speed, and privacy in our AI stack. All changes staged for Alex review.

## Proposed Changes

### 1. Memorize guardrails in MEMORY.md
**Category:** memory
**Priority:** high
**Effort:** trivial
**Files affected:** MEMORY.md

**What:** Add a formal Debra outbound messaging guardrail: Debra must be in a group chat with Alex whenever contacting anyone other than Alex; cron reminders do not constitute authorization.
**Why:** Phase 2 corrections show solo outbound messages are a recurring risk; codifying prevents future breaches.
**Diff preview:**
```
- Debra outbound messaging policy (informal)
+ Debra outbound messaging policy: Debra must be in a group chat with Alex when contacting others. Cron reminders do not authorize messages.
```

### 2. Phase 0: Preflight verification routine
**Category:** workflow
**Priority:** high
**Effort:** moderate
**Files affected:** AGENTS.md, TOOLS.md

**What:** Create a preflight checklist script invoked before outbound messages, outputting a quick read of last 10 messages and pending approvals.
**Why:** Addresses Phase 2 corrections and reduces risk of accidental disclosures.
**Diff preview:**
```
shell
# preflight.sh
printf "Last messages:"; tail -n 10 ~/.openclaw/workspace/.. 2>/dev/null || true
```

### 3. Phase 1-3: Security-focused memory graph mockup
**Category:** infrastructure
**Priority:** medium
**Effort:** moderate
**Files affected:** memory/ (new subdir) 

**What:** Build a sandboxed memory graph mockup for testing privacy-preserving indexing before applying to production Neo4j.
**Why:** Phase 3 deep-dives on privacy; prototype reduces risk.
**Diff preview:**
```
(memory mock files)
```

### 4. Phase 4: Pilot Be Particular automation guardrail
**Category:** workflow/infrastructure
**Priority:** low
**Effort:** moderate
**Files affected:** SOUL.md, TOOLS.md

**What:** Add a Be Particular automation guardrail: Debra cannot autonomously perform home-behavior automation without explicit human approval. Include a test harness and log gating.
**Why:** Progressive autonomy requires governance.
**Diff preview:**
```
+ Be Particular automation guardrails: Debra requires explicit sign-off for automation actions at home.
```

### 5. Memory and corrections tooling improvements
**Category:** tooling
**Priority:** medium
**Effort:** moderate
**Files affected:** TOOLS.md, memory/corrections.md

**What:** Add structured tagging for corrections (pattern-keys) and export summary.
**Why:** Improves Phase 2 corrections analysis.
**Diff preview:**
```
+ pattern-key: debra-solo-outbound
```

## Deferred / Watching
- None this cycle

## Meta
- Research scan: 3 findings, 3 kept
- Self-reflection: 3 issues identified
- Deep dives: 3 topics researched
- Proposals: 5 changes suggested
- Estimated cost: ~$0.10 in tokens
- Cycle duration: ~28m
