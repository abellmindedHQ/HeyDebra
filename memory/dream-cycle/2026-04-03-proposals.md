# Dream Cycle Proposals — 2026-04-03

## Summary
Cycle #7 found 8 research items (Claude Agent SDK, TurboQuant, HA 2026.4 being the top 3). Self-reflection confirms process narration is still the #1 failure mode after 7 cycles but no new corrections since Apr 1 (Alex in Boston). Memory verification passed 8/8 probes. Key theme tonight: structural enforcement (hooks, gates) over behavioral rules. The Agent SDK's hook architecture is the most promising path to solving our persistent message discipline problem.

## Proposed Changes

### 1. Evaluate Claude Agent SDK PreToolUse Hooks for Message Gating
**Category:** infrastructure/workflow
**Priority:** HIGH
**Effort:** moderate
**Files affected:** possibly AGENTS.md, new integration script

**What:** Research whether OpenClaw supports or plans to support PreToolUse-style lifecycle hooks. If not, evaluate the Claude Agent SDK as a complementary layer that enforces hard gates on message sending (no narration in external chats, preflight verification before every external send).
**Why:** Process narration in external chats is our #1 failure mode across 7 dream cycles. We have behavioral rules (preflight.sh, AGENTS.md, MEMORY.md) but 3 incidents happened in one day (Apr 1) AFTER those rules were in place. A structural hook that blocks messages matching narration patterns would catch what behavioral intent cannot.
**Next step:** Check OpenClaw's current hook/middleware capabilities. If none exist, prototype with Agent SDK.

### 2. Test TurboQuant on QMD Vector Index
**Category:** infrastructure
**Priority:** MEDIUM
**Effort:** trivial
**Files affected:** QMD config/index

**What:** Install the `turboquant` Python package and test whether it can compress QMD's 46MB embedding index (9,634 vectors) while maintaining search recall quality.
**Why:** 6x compression (46MB → ~8MB) would speed up semantic searches across SecondBrain. Google Research validated zero accuracy loss across standard benchmarks. Drop-in package available.
**Diff preview:**
```bash
pip install turboquant
# Then test: compress QMD index, run recall benchmark before/after
```

### 3. Update Home Assistant to 2026.4
**Category:** infrastructure
**Priority:** MEDIUM
**Effort:** trivial
**Files affected:** HA instance

**What:** Update Alex's Home Assistant from current version to 2026.4. New features: native IR support, AI thinking transparency, Matter lock management, improved automation triggers.
**Why:** IR support opens the door to controlling the Nebula projector, LG OLED, and other IR-only devices. AI thinking helps debug smart home automations. Low risk update.
**Next step:** Check current HA version, review breaking changes, update.

### 4. Consolidate Dream Cycle Proposal Backlog
**Category:** workflow
**Priority:** MEDIUM
**Effort:** trivial
**Files affected:** memory/dream-cycle/proposal-backlog-summary.md (new)

**What:** Create a single consolidated summary of all pending proposals (cycles 5-7, ~13 items) with dedup, priority ranking, and estimated effort. Present to Alex as ONE document when he returns instead of making him read 3 separate proposal files.
**Why:** Proposal backlog is growing (now 3 unreviewed cycles). Alex reviewed 30 from cycles 1-4 in one sprint but having to read multiple files is friction. A consolidated, prioritized view will get faster decisions.

### 5. Add "Give Up After N Attempts" Policy for Be Particular Calls
**Category:** workflow
**Priority:** LOW
**Effort:** trivial
**Files affected:** Be Particular skill/cron config, AGENTS.md

**What:** After 3 failed call attempts for the same session, pause the cron and notify Alex instead of scheduling attempt #5, #6, etc. Let Alex decide whether to try again or pivot to a different approach (text-based prompts, different time slot, etc.).
**Why:** Session 2 has had 4 attempts without completion. Each attempt costs an ElevenLabs call + a cron slot + context-switching. Diminishing returns after 3 tries.

### 6. Benchmark Gemma 4 for Dream Cycle Phases 1-2
**Category:** infrastructure
**Priority:** LOW
**Effort:** moderate
**Files affected:** dream-cycle SKILL.md, gateway config

**What:** Test Google's Gemma 4 open model (256K context, agentic-focused) as an alternative to Sonnet for dream cycle scan and reflection phases. Could reduce costs for batch work.
**Why:** Gemma 4 is designed for agentic workflows and is open-source. If quality is comparable to Sonnet for scanning/reflection tasks, we could save significantly on nightly batch runs.

## Deferred / Watching

- **Claude Desktop Control / Dispatch:** Interesting but needs more maturity. Wait for stable release and test when VisionClaw is further along.
- **Cursor 3 Agent Fleets:** Alex has Cursor in his post-Boston workflow queue. Will naturally evaluate when that task comes up.
- **ChatGPT in CarPlay:** Note for car shopping phase. Low priority.
- **Anthropic "Emotion Concepts" paper:** Fascinating for Mirror product but no immediate action needed. File for Alex's product architecture sessions.
- **Anthropic Mythos security concerns:** Monitor but no action needed. We're behind OpenClaw's security boundary.
- **OpenAI IPO / TBPN acquisition:** Industry awareness, no direct impact.

## Meta
- Research scan: 8 findings, 8 kept
- Self-reflection: 5 issues identified (process narration #1, proposal backlog #2, Be Particular scheduling #3, yearbook oversight #4, memory-before-acting #5)
- Memory verification: 8 probes, 8 passed, 0 flagged
- Deep dives: 3 topics researched (Claude Agent SDK, TurboQuant, HA 2026.4)
- Proposals: 6 changes suggested (1 HIGH, 3 MEDIUM, 2 LOW)
- No changes auto-applied
- Cycle duration: ~20 min
