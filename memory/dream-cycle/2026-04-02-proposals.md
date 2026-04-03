# Dream Cycle Proposals — 2026-04-02

## Summary
Sixth dream cycle. Found 8 developments (Claude Code source leak, Mem0g memory benchmarks, 1-bit Bonsai LLM, OpenClaw task brain, HA 2026.4, Neo4j Aura Agent, AI compute economics). Reflected on 3 issues: process narration still #1 failure (3x in one day), proposal pipeline backlog, Sallijo scheduling pattern. Deep-dived 3 topics: Mem0g graph memory, Bonsai 8B local LLM, OpenClaw task brain. Key theme: our process narration problem might be solvable with hard permission gates rather than behavioral guidelines.

## Proposed Changes

### 1. Investigate OpenClaw Task Brain for Message Permission Gates
**Category:** infrastructure
**Priority:** high
**Effort:** moderate
**Files affected:** gateway config, AGENTS.md

**What:** Check current OpenClaw version, review task brain feature set, evaluate whether outbound message sending can be gated behind a permission/approval step. If yes, implement as hard enforcement for the "no process narration in external chats" rule.
**Why:** Process narration in external chats is our #1 recurring failure (3 incidents Apr 1 alone). Behavioral guidelines aren't working. Need enforcement at the tool level. The task brain's permission system may provide exactly this.
**Diff preview:** Depends on task brain API. Would add permission config to gateway, update AGENTS.md to reference enforcement mechanism instead of just behavioral rules.

### 2. Add Sallijo Morning Call Preference to Memory
**Category:** memory
**Priority:** low
**Effort:** trivial
**Files affected:** MEMORY.md (People section)

**What:** Update Sallijo's entry in MEMORY.md to note: "Prefers morning calls (10am). Evening calls consistently fail (driving, social plans)."
**Why:** Two failed evening call attempts. Pattern identified. Should be in long-term memory so future sessions don't repeat the mistake.
**Diff preview:**
```
- **Sallijo Archer**: Alex's mom, Knoxville, heart surgery 2025, dog Pickles. Be Particular book project (SECRET).
+ **Sallijo Archer**: Alex's mom, Knoxville, heart surgery 2025, dog Pickles. Be Particular book project (SECRET). Prefers morning calls (~10am). Evening calls don't work (she's often driving or out).
```

### 3. Bookmark Mem0g for Post-Architecture-Decision Evaluation
**Category:** memory
**Priority:** low
**Effort:** trivial
**Files affected:** MEMORY.md or active-context.md

**What:** Add a note to the knowledge architecture decision queue: "After Alex makes Neo4j/Obsidian/vector DB decisions, evaluate Mem0g graph-enhanced memory as supplementary layer. Paper: arXiv:2504.19413. Benchmark shows 68.4% accuracy at 91% less latency than full-context."
**Why:** The knowledge architecture report is waiting for Alex's review. Mem0g could be relevant to that decision, but adding it now would be premature complexity. Bookmark for later.

### 4. Pin Claude Code Version + Verify npm Integrity
**Category:** security
**Priority:** medium
**Effort:** trivial
**Files affected:** TOOLS.md

**What:** Check current Claude Code version, pin it in package.json or install command, and add `npm audit` to periodic health checks. The source code leak came from v2.1.88's source map. We should ensure we're on a known-good version and not auto-updating to compromised packages.
**Why:** The CC leak exposed 500K lines of code. While our usage isn't directly affected, it's good hygiene to pin versions and verify integrity, especially since we use CC for coding tasks daily.

### 5. Add Bonsai 8B to Linear Backlog
**Category:** infrastructure
**Priority:** low
**Effort:** trivial
**Files affected:** Linear (new ticket)

**What:** Create a Linear ticket for "Evaluate Bonsai 8B local LLM for classification tasks" with details from deep dive. Tag as future/optimization. Not urgent.
**Why:** Local LLM for email triage, message classification, and quick extraction could save API costs and add offline capability. But it's not a priority over current roadmap.

## Deferred / Watching

- **Home Assistant 2026.4 infrared support:** Could bring Nebula projector + LG OLED into HA. Defer until Alex has time for smart home tinkering.
- **Neo4j Aura Agent:** No-code graph agents could simplify our people graph queries. Defer until knowledge architecture decision.
- **Claude Code Skills 2.0:** Self-improving eval loops interesting for our dream-cycle model. Watch for adoption patterns.
- **AI compute economics:** $65/user at $20/mo pricing. File for HeyDebra business model thinking.

## Meta
- Research scan: 15 items reviewed, 8 kept
- Self-reflection: 3 issues identified (process narration, proposal backlog, scheduling)
- Memory verification: 8 probes, 7 passed, 1 flagged (AssemblyAI status stale)
- Deep dives: 3 topics researched (Mem0g, Bonsai 8B, OpenClaw task brain)
- Proposals: 5 changes suggested (1 high, 1 medium, 3 low)
- Estimated cost: ~$3.50 (Opus for deep research + Sonnet-equivalent scan work)
- Cycle duration: ~20 min
- Previous unreviewed proposals: ~33 total from cycles 1-5 (various review states)
