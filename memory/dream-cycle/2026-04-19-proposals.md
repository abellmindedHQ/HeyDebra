# Dream Cycle Proposals — 2026-04-19

## Summary
Tonight's cycle was productive. 8 findings kept from scan (5 high, 3 medium), strong self-reflection catching 4 stale memory entries and confirming a repeating correction pattern (message fragmentation at 3x). Three deep dives: Karpathy's LLM Wiki validates our SecondBrain architecture and suggests a "wiki linting" addition; GitHub agent prompt injection is a real security concern for Claude Code usage; Mem0 benchmarks show our full-context memory approach costs 14x more tokens than alternatives. Six proposals below.

## Proposed Changes

### 1. Fix Stale Memory Entries
**Category:** memory
**Priority:** high
**Effort:** trivial
**Files affected:** MEMORY.md, TOOLS.md, active-context.md

**What:** Update stale entries discovered in memory verification:
- MEMORY.md: Update primary model from "openrouter/auto" to "anthropic/claude-opus-4-6" (Alex's switch on Apr 19)
- MEMORY.md: Update BB attachment bug status to "FIXED in 2026.4.19-beta.2"
- TOOLS.md: Update OpenClaw version from 2026.4.11 to 2026.4.19-beta.2
- active-context.md: Update Gateway version, update lipoma removal to "NEEDS RESCHEDULING"

**Why:** Memory verification found 4/6 probes had stale data. Stale memory causes wrong assumptions and wasted Alex-time.

**Diff preview:**
```
MEMORY.md:
- Primary model: openrouter/auto (changed Apr 16, was openai/gpt-5.4)
+ Primary model: anthropic/claude-opus-4-6 (changed Apr 19, was openrouter/auto)

- BB Attachment Bug: patches will be overwritten...
+ BB Attachment Bug: FIXED in OpenClaw 2026.4.19-beta.2. Images confirmed working Apr 19.

TOOLS.md:
+ OpenClaw: 2026.4.19-beta.2 (updated from 2026.4.11 on Apr 19)
```

### 2. Promote "Message Consolidation" to MEMORY.md Critical Lessons
**Category:** memory/workflow
**Priority:** high
**Effort:** trivial
**Files affected:** MEMORY.md

**What:** Add a critical lesson: "ONE message per response. Never fragment into 3-5 messages. Compose internally, send ONE clean result." This pattern has hit 3x: process-narration-group-chat (2x in corrections.md) + Apr 19 "one message not five" correction.

**Why:** 3x correction threshold met. This keeps getting repeated because it's not prominent enough in the critical lessons section. Currently only says "NO emdashes. ONE message per response in iMessage." Should be broader — applies to ALL channels, not just iMessage.

**Diff preview:**
```
MEMORY.md Critical Lessons:
+ **ONE message per response. ALL channels.** Never send 3-5 fragments. Compose internally, verify, send ONE clean message. This applies to iMessage, WhatsApp, Discord, and TUI. (3x correction: Apr 1, Apr 19)
```

### 3. Add Corrections from Apr 19 to corrections.md
**Category:** memory
**Priority:** high
**Effort:** trivial
**Files affected:** memory/corrections.md

**What:** Append three new correction entries from today's session:
- `execution.stop-asking-start-doing` — execute unambiguous instructions immediately
- `workflow.verify-before-reporting` — always verify URLs/outputs before claiming success
- `workflow.one-message-not-five` — consolidate responses (links to existing pattern)

**Why:** Corrections were identified in today's daily notes but never formally captured in corrections.md.

### 4. Add "Wiki Linting" Step to Dream Cycle
**Category:** skill
**Priority:** medium
**Effort:** moderate
**Files affected:** skills/dream-cycle/SKILL.md

**What:** Add Phase 2.75: Wiki Linting. After memory verification, scan 10 random SecondBrain pages for:
- Stale information (dates passed, status changed)
- Missing wikilinks to known People/Projects
- Contradictions with recent daily notes
- Broken links or empty stubs

Inspired by Karpathy's LLM Wiki "linting pass." This is the first step toward automated knowledge base maintenance.

**Why:** Memory verification tonight found 4 stale entries in our *own* workspace files. SecondBrain vault (1300+ files) likely has many more. A periodic linting pass catches drift before it causes problems.

### 5. Security Audit: Claude Code Permissions
**Category:** infrastructure/security
**Priority:** medium
**Effort:** trivial
**Files affected:** TOOLS.md (documentation), potentially coding-agent SKILL.md

**What:** Audit Claude Code usage:
- List all repos where Claude Code runs
- Check if any accept external PRs
- Document the permission model (currently `--permission-mode bypassPermissions`)
- Evaluate sandboxing options
- Add a note to TOOLS.md about the "Comment and Control" vulnerability

**Why:** Demonstrated attack vector (Apr 15-19 disclosure) where malicious PR content can exfiltrate API keys from Claude Code GitHub Actions. We use Claude Code with maximum permissions. Even though we're not running it as a GitHub Action, the prompt injection vector applies to any Claude Code run on untrusted code.

### 6. Dan Janowski Enrichment — Complete Before Friday
**Category:** workflow
**Priority:** medium
**Effort:** moderate
**Files affected:** SecondBrain/People/Dan-Janowski.md, Google Contacts, Neo4j

**What:** Complete Tier 1 + Tier 2 enrichment for Dan Janowski before Friday Apr 25 meeting:
- Web search for ORNL profile, publications, LinkedIn
- Cross-reference with ORNL org chart
- Update SecondBrain People card
- Create Google Contact on both accounts
- Add to Neo4j graph

**Why:** Alex has a demo meeting with Dan on Friday. Walking in with context > walking in cold.

## Deferred / Watching

- **Mem0 Graph Memory:** Monitor for OpenClaw integration. If our memory files exceed 100 entries or token costs spike, revisit as an upgrade path.
- **Claude Managed Agents:** Interesting architecture but we're already running our own stack on OpenClaw. No action needed unless pricing becomes attractive.
- **Neo4j ai.* Cypher procedures:** Worth exploring after Neo4j upgrade, but not urgent. QMD handles our search needs.
- **Opus 4 deprecation:** Need to check our model strings. If we're using "claude-opus-4" anywhere, update to "claude-opus-4-6" or "claude-opus-4-7" before retirement date.

## Meta
- Research scan: ~30 sources scanned, 8 kept
- Self-reflection: 5 issues identified, 3 new corrections
- Memory verification: 6 probes, 2 passed, 4 stale
- Deep dives: 3 topics researched (Karpathy Wiki, GitHub agent security, Mem0)
- Proposals: 6 changes suggested (3 high priority, 3 medium)
- Estimated cost: ~$3-4 (Opus for deep research + Gemini for search/embeddings)
- Cycle duration: ~25 min
