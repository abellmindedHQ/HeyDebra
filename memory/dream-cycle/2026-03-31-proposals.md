# Dream Cycle Proposals — 2026-03-31

## Summary
Fourth dream cycle. Found 8 interesting developments (Claude Code source leak, Letta memory architecture, DeerFlow 2.0, new agent browser). Reflected on 6 issues (session context bloat, 22 unreviewed proposals, Gemini quota 4th cycle, Neo4j 4th day down, Google Messages bridge dead). Deep-dived 3 topics. Key theme tonight: the dream cycle's proposal pipeline is broken. Generating great ideas that nobody reviews. This cycle's proposals prioritize self-service fixes and changing the delivery model.

## Proposed Changes

### 1. Self-Apply Trivial Fixes (Break the Proposal Bottleneck)
**Category:** workflow
**Priority:** high
**Effort:** trivial
**Files affected:** AGENTS.md

**What:** Add a rule to AGENTS.md: "Dream cycle may self-apply changes rated as trivial effort that don't modify SOUL.md, gateway config, or outbound communication behavior. Log all self-applied changes in the proposals file."
**Why:** 22 proposals pending across 4 cycles. Zero reviewed. The "propose → wait for Alex" model is broken. Trivial fixes (typo corrections, new memory entries, file organization) should just happen. Alex reviews the log, not each individual change.
**Diff preview:**
```
Add to AGENTS.md under "Red Lines" or new "Dream Cycle Self-Apply" section:
+ ## Dream Cycle Self-Apply Policy
+ Dream cycle may self-apply changes that are:
+ - Trivial effort (typo fixes, new memory entries, file organization)
+ - Do NOT modify SOUL.md, AGENTS.md, USER.md, or gateway config
+ - Do NOT change outbound communication behavior
+ - All self-applied changes are logged in the proposals file for review
```

### 2. Structure active-context.md with Formal Sections
**Category:** memory/workflow
**Priority:** high
**Effort:** trivial
**Files affected:** active-context.md

**What:** Restructure active-context.md into labeled sections with target character limits, inspired by Letta's Core Memory blocks. Sections: Active Tasks (max 500 chars), Pending Decisions (max 300 chars), Infrastructure Status (max 300 chars), Schedule (max 400 chars), Channel Context (max 200 chars).
**Why:** active-context.md has grown to ~100+ lines. It was supposed to be a 50-line sticky note. Formal sections prevent bloat and ensure consistent structure across session resets. Letta's research validates this approach.
**Diff preview:**
```markdown
# Active Context — [date]
## Active Tasks (target: 500 chars)
[Current work items, max 5]
## Schedule (target: 400 chars)
[Next 48h of calendar items]
## Pending Decisions (target: 300 chars)
[Things waiting on Alex]
## Infrastructure (target: 300 chars)
[What's up/down/broken]
## Channel Context (target: 200 chars)
[Active conversations, recent channel state]
```

### 3. Start Neo4j (Self-Service Fix)
**Category:** infrastructure
**Priority:** high
**Effort:** trivial
**Files affected:** none (service start)

**What:** Run `brew services start neo4j` during next heartbeat. It's been down 4+ days. Night Swimming contact triage, social data processing, and knowledge graph operations are all blocked.
**Why:** I identified this in cycle #3 and noted I should "just do it." Still haven't. This is within my safe-to-do-freely zone (it's a service I use, on our machine, that was previously running). No destructive potential.
**Diff preview:** `brew services start neo4j`

### 4. Fix Gemini Search Quota (Backup Search Provider)
**Category:** infrastructure/config
**Priority:** high
**Effort:** moderate
**Files affected:** gateway config (needs Alex approval)

**What:** Investigate adding a backup search provider to OpenClaw config. The v2026.3.28 update added Grok web search support. If no config change needed, add Brave Search or SerpAPI as fallback. If config change needed, prepare the patch for Alex.
**Why:** 4 consecutive dream cycles degraded by Gemini 429 errors. Free tier limit is 5 requests/minute. This is the most-proposed, never-fixed issue in dream cycle history. Even adding a 40-second delay between searches would help, but a backup provider is the real fix.
**Diff preview:** Need to investigate OC config schema for search providers first.

### 5. Modular Rules Directory (from Claude Code Architecture)
**Category:** workflow
**Priority:** medium
**Effort:** trivial
**Files affected:** new directory: workspace/rules/

**What:** Create a `rules/` directory with focused rule files, inspired by Claude Code's .claude/rules/*.md pattern. Start with: `rules/outbound-comms.md` (verification checklist before sending messages), `rules/group-chat.md` (behavior rules for group chats), `rules/memory-management.md` (when/how to update memory files).
**Why:** AGENTS.md, SOUL.md, and USER.md are getting long. Modular rules keep context focused and make it easier to update specific behaviors without touching core identity files. Claude Code re-reads these per query iteration.
**Diff preview:**
```
rules/
├── outbound-comms.md    (pre-send verification gate)
├── group-chat.md        (speaking rules, reaction usage)
└── memory-management.md (tier definitions, flush triggers)
```

### 6. Sleep-Time Memory Consolidation Skill
**Category:** skill (new)
**Priority:** medium
**Effort:** moderate
**Files affected:** new skill: skills/memory-consolidation/SKILL.md

**What:** Create a skill that runs during idle periods (late night or heartbeat gaps) to: (1) read recent daily files, (2) identify significant events worth long-term retention, (3) update MEMORY.md with distilled insights, (4) prune stale entries from active-context.md, (5) archive old daily files that have been consolidated.
**Why:** Inspired by Letta's "sleep-time compute" concept. We currently do memory consolidation manually during heartbeats, inconsistently. A dedicated skill formalizes this and ensures memory quality improves over time. The dream cycle already does self-reflection; this skill handles the memory hygiene that reflection identifies as needed.

### 7. Sub-Agent Strategy for Heavy Processing
**Category:** workflow
**Priority:** medium
**Effort:** trivial (behavioral change, no code)
**Files affected:** AGENTS.md (add guidance)

**What:** Add explicit guidance: "For batch processing tasks (GTD triage, file imports, bulk operations), always spawn a sub-agent. Main session is for conversation and coordination." Today's session bloat was caused by running heavy processing in the main session.
**Why:** Alex was frustrated by session lag today. This is a recurring pattern — heavy batch work in main session consumes context and slows response times. Sub-agents are free to use and keep main session responsive.

### 8. Investigate Pardus Browser for Agent Automation
**Category:** infrastructure (research)
**Priority:** low
**Effort:** moderate (evaluation)
**Files affected:** none yet

**What:** Evaluate the Pardus browser (purpose-built for AI agents, no Chromium dependency) as a replacement for our Chrome-based browser automation. Our Chrome setup has chronic issues: profile blocking (Chrome 136+), LaunchAgent workarounds, profile=openclaw vs user confusion.
**Why:** If Pardus solves the "browser for agents" problem natively, it eliminates an entire class of infrastructure issues. But it's new (Show HN today), so maturity is a concern.

## Deferred / Watching

- **Claude Code fork model for sub-agents:** Interesting cost optimization (prompt cache reuse across spawned agents). Needs investigation into OC's sub-agent prompt caching behavior. Not urgent.
- **DeerFlow progressive skill loading:** Good pattern but we already load skills on-demand via read. Could formalize with relevance scoring later.
- **RankClaw security scanner:** Should periodically scan our ClawHub skills. Not urgent but good hygiene.
- **Cognee (open-source knowledge graph + memory layer):** Potential Neo4j alternative or complement. Research when Neo4j is running and we can compare.

## Meta
- Research scan: 15 items scanned, 8 kept
- Self-reflection: 6 issues identified (session bloat, proposal backlog, Gemini quota, Neo4j, Google Messages bridge, BB encoding)
- Deep dives: 3 topics (Claude Code leak architecture, Letta memory, DeerFlow 2.0)
- Proposals: 8 changes suggested (3 high, 3 medium, 1 low, 1 meta)
- Gemini search quota: hit 429 after 6/8 queries (4th consecutive cycle)
- Cycle duration: ~25m
- **Total pending proposals: 22 (previous) + 8 (new) = 30**
- **CRITICAL META-ISSUE: 30 proposals, 0 reviewed. Proposal #1 (self-apply trivial fixes) is the most important proposal in this entire backlog.**
