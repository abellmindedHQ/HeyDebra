# Dream Cycle Proposals — 2026-04-20

## Summary
Tonight's cycle found 8 items (5 high, 3 medium). Claude Design launch is the most exciting finding — could accelerate brand/design work significantly. MCP STDIO vulnerability is the most urgent — real security risk with our high-permission setup. Reflection showed message-fragmentation STILL recurring despite promotion, and the previous cycle's stale-memory fixes still haven't been applied (pending Alex review). 4 deep dives completed. 7 proposals below.

## Proposed Changes

### 1. Apply Last Cycle's Stale Memory Fixes (CARRY-FORWARD)
**Category:** memory
**Priority:** high
**Effort:** trivial
**Files affected:** MEMORY.md, TOOLS.md

**What:** Same as Proposal #1 from 2026-04-19. Still not applied:
- Update BB attachment bug status in MEMORY.md to "FIXED in 2026.4.19-beta.2"
- Add Tyler Fogarty to MEMORY.md People section
- Add ABE-32 logo decision to MEMORY.md Active Projects

**Why:** Stale data causes wrong assumptions. This was proposed last cycle and memory verification tonight confirmed it's still stale. Carrying forward with higher urgency.

**Diff preview:**
```markdown
MEMORY.md:
## BB Attachment Bug (Apr 8-9)
- [REMOVE entire section or replace with:]
- BB Attachment Bug: RESOLVED. Fixed in OpenClaw 2026.4.19-beta.2. WhatsApp images confirmed working Apr 19. iMessage attachments still broken upstream.

## People (cont.)
+ - **Tyler Fogarty**: real estate broker, Fox & Fogarty, Knoxville. 16+ years, 2000+ transactions. Photographer. +18654146145

## Active Projects
+ - ABE-32 Brand Identity: Recoleta wordmark + A-Eye mark (Cooper A3). LOCKED IN. Sent to Maren for thesis alignment, then ships.
```

### 2. MCP Security Audit
**Category:** infrastructure/security
**Priority:** high
**Effort:** trivial
**Files affected:** TOOLS.md

**What:** Audit and document MCP configuration on the Mac mini:
1. List all MCP servers/configs
2. Identify which use STDIO transport
3. Document risks in TOOLS.md
4. Add note to coding-agent skill about MCP prompt injection risks

**Why:** MCP STDIO vulnerability (CVE-2026-30623 et al.) enables arbitrary command execution. We run Claude Code with bypassPermissions. Compound risk with the GitHub agent prompt injection from last cycle. Our machine has access to email, contacts, messages, finances.

### 3. Upgrade to Opus 4.7 Discussion
**Category:** infrastructure
**Priority:** high
**Effort:** trivial
**Files affected:** openclaw.json (model config), MEMORY.md

**What:** Flag to Alex that Opus 4.7 is GA with same pricing as 4.6. Key improvements relevant to us:
- Self-verification before reporting (addresses our "verify-before-reporting" correction)
- Better vision (helps with screenshot/image analysis)
- 13% coding benchmark lift
- Better instruction following in agent workflows

Recommend upgrading after Avie's surgery week settles (post-Apr 23).

**Why:** We're paying the same price for 4.6. 4.7 is strictly better for our use cases. The self-verification behavior could reduce a correction pattern that's been recurring since Mar 28.

### 4. Pre-Send Compose Checkpoint
**Category:** workflow
**Priority:** medium
**Effort:** trivial
**Files affected:** AGENTS.md

**What:** Add a "Compose Before Send" rule to AGENTS.md Message Discipline section:
```
Before sending ANY external message:
1. Draft the full message internally (in your reasoning, not in the chat)
2. Review: Is this ONE message? Does it contain everything needed?
3. Check: Am I about to send a second message that should be part of this one?
4. Send ONE message. If you already sent one, do NOT send a follow-up "got it" or "will do."
```

**Why:** Message fragmentation has been corrected 4+ times. It was promoted to MEMORY.md last cycle. It STILL happened today (double-sending). The promotion didn't work because the rule was passive ("don't fragment") rather than active (a checklist to follow). An active checkpoint is more likely to stick.

### 5. Claude Design Evaluation (Post ABE-32)
**Category:** skill/workflow
**Priority:** medium
**Effort:** moderate
**Files affected:** New — could become a skill or workflow addition

**What:** After ABE-32 ships, run a parallel evaluation:
1. Feed BRAND.md + locked logo into Claude Design
2. Have it generate the same deliverables Paperclip is producing (business cards, merch mockups, signage)
3. Compare quality, speed, and iteration friction
4. Decision: use Claude Design for future design work, or keep Paperclip, or hybrid

**Why:** Claude Design could dramatically accelerate design iteration. The ABE-32 process revealed friction (QA failures, context drift, multi-round corrections). But don't disrupt the current pipeline mid-project.

### 6. Coding Agent GSD Enhancement
**Category:** skill
**Priority:** medium
**Effort:** moderate
**Files affected:** skills/coding-agent/SKILL.md

**What:** Add GSD Framework guidance to coding-agent skill:
- For projects with >5 features or multi-session scope, recommend Plan/Execute/Verify phases
- Add plan template and verify checklist
- Each phase runs as a separate agent spawn with clean context

**Why:** Addresses context degradation in long coding sessions. Validated by MindStudio's GSD framework and our own experience with Paperclip context drift.

### 7. Dream Cycle Auto-Diff for Stale Memory
**Category:** skill
**Priority:** low
**Effort:** moderate
**Files affected:** skills/dream-cycle/SKILL.md

**What:** Enhance Phase 2.5 (Memory Verification) to auto-generate ready-to-apply diffs when stale data is found, instead of just flagging it. Format:
```
STALE FIX READY — apply with `edit`:
File: MEMORY.md
Old: "BB Attachment Bug: patches will be overwritten..."
New: "BB Attachment Bug: RESOLVED in 2026.4.19-beta.2"
```

**Why:** Stale memory fixes have been proposed for 2 consecutive cycles now. The lag between "found stale" → "proposed fix" → "Alex reviews" → "applied" is too long. Pre-generating the exact edit reduces Alex's review friction from "read proposal and figure out the change" to "yes/no on a diff."

## Deferred / Watching

- **Cloudflare Agent Memory:** Interesting architecture, especially temporal logic and supersession handling. Our flat-file approach works but has supersession gaps. Monitor for OpenClaw integration or inspiration.
- **Claude Managed Agents:** We run our own agent infra on OpenClaw. No compelling reason to switch, but worth tracking pricing/features.
- **Detection Asymmetry (DeepMind):** Websites distinguishing AI agents from humans. Low priority but relevant if our browser automation encounters adversarial sites.
- **LanceDB cloud-backed memory:** Mentioned in OC release notes. Could be an upgrade path from flat files if memory grows past current scale.
- **Last cycle carry-forwards still pending:** Wiki linting (Proposal #4), Claude Code security audit (Proposal #5), Dan Janowski enrichment (Proposal #6).

## Meta
- Research scan: ~15 sources scanned, 8 findings kept (5 high, 3 medium)
- Self-reflection: 4 issues identified, 2 new corrections, message-fragmentation still recurring
- Memory verification: 7 probes, 5 passed, 2 flagged (1 stale, 1 missing)
- Deep dives: 4 topics researched (Claude Design, MCP STDIO security, GSD Framework, Cloudflare Agent Memory)
- Proposals: 7 changes suggested (3 high, 3 medium, 1 low)
- Estimated cost: ~$4-5 (Opus for deep research + Gemini for search/embeddings)
- Cycle duration: ~25 min
