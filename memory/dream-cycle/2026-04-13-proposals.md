# Dream Cycle Proposals — 2026-04-13

## Summary
Tonight's cycle produced five deep insights and a backlog of 18+ proposals. All changes are staged for Alex review; no auto-apply.

## Proposed Changes

### 1. Update Claude Code to v2.x (Claude v2.x improvements)
**Category:** skill/config
**Priority:** high
**Effort:** moderate
**Files affected:** memory/dream-cycle/2026-04-13-proposals.md (this file) and unknown-edit to SKILL.md
**What:** Upgrade Claude Code to v2.x; enable worktree-safe workflows; adjust prompts to exploit memory/planning features.
**Why:** Addresses key reliability issues and improves ability to perform Phase 3 efficiently.
**Diff preview:**
```
- Claude Code v2.x unavailable
+ Claude Code v2.x enabled; add worktree support
```

### 2. Add explicit Cron-vs-Authorization policy (AGENTS.md)
**Category:** workflow/config
**Priority:** high
**Effort:** trivial
**Files affected:** AGENTS.md
**What:** Document cron vs explicit approval rule; require Alex to approve outbound actions in a group chat first.
**Why:** Governance safeguard after multiple incidents.
**Diff preview:**
```
+ Rule: Cron reminders do not authorize outbound actions. Debra must present in group chat with Alex and recipient for any outbound messages.
```

### 3. Change Dream Cycle delivery format to decision-forcing prompts
**Category:** workflow
**Priority:** high
**Effort:** moderate
**Files affected:** memory/dream-cycle/2026-04-13-proposals.md
**What:** End each phase with explicit decisions (Approve/Modify/Reject).
**Why:** Improves alignment and reduces back-and-forth.
**Diff preview:**
```
- Output: descriptive summary
+ Output: 3 options with decisions
```

### 4. Stale item escalation rule (7+ days)
**Category:** workflow
**Priority:** medium
**Effort:** trivial
**Files affected:** memory/dream-cycle/2026-04-13-proposals.md
**What:** If a stakeholder item is stale for 7+ days, draft outreach and flag as escalated.
**Why:** Prevents backlog from growing unchecked.

### 5. Backlog triage pipeline (Phase 1/4)
**Category:** workflow/infrastructure
**Priority:** medium
**Effort:** moderate
**Files affected:** memory/dream-cycle/2026-04-13-proposals.md
**What:** Introduce triage rubric and weekly sprint planning for backlog items.
**Why:** Improves throughput and focus.

## Deferred / Watching
- Budget-aware cycle pacing
- Be Particular be milestones planning

## Meta
- Research scan: 5 findings captured
- Self-reflection: 1 major pattern
- Deep dives: 5 topics explored
- Proposals: 5 changes staged
- Estimated cost: ~$0.20 (token usage for Claude Opus prompts)
- Cycle duration: ~25m
