# Dream Cycle Proposals — 2026-04-22

## Summary
Cycle #16. Top story: Forbes reports Claude Opus 4.7 has 52% vulnerability rate in code generation — DO NOT upgrade from 4.6. MCP STDIO vulnerability now at 200K instances (Anthropic says "by design"). Claude Code Pro briefly removed from $20 tier. Tiago Forte launches "AI Second Brain" concept that validates our architecture. Reflection: same recurring issues (message fragmentation, stale memory), proposal backlog growing to 21+ unreviewed items. Recommending self-apply for trivial memory fixes.

## Proposed Changes

### 1. Self-Apply Stale Memory Fixes (TRIVIAL, CARRY-FORWARD x4)
**Category:** memory
**Priority:** high
**Effort:** trivial
**Files affected:** TOOLS.md, MEMORY.md

**What:** Fix the same stale data that has been proposed for 4 consecutive cycles:
- TOOLS.md: BB port 1234 → 1235
- MEMORY.md: Update Paperclip team from "7 agents active" to "10 agents active" with full roster
- MEMORY.md: Update BB Attachment Bug section status

**Why:** 4th consecutive cycle proposing this. Per AGENTS.md self-apply policy: "Trivial effort (starting services, adding notes to TOOLS.md/MEMORY.md, file organization, typo fixes)" are allowed. These are factual corrections, not behavioral changes. Waiting for Alex to review a memory fix file is not a productive use of anyone's time.
**Self-apply:** YES (within AGENTS.md policy scope)

### 2. DO NOT Upgrade to Opus 4.7
**Category:** infrastructure
**Priority:** high
**Effort:** trivial (just don't do it)
**Files affected:** none

**What:** Based on Forbes/Veracode data showing 52% vulnerability rate in Opus 4.7 code generation (vs OpenAI's ~30%), stay on Opus 4.6 until Anthropic addresses the quality regression.
**Why:** We're a code-heavy operation (Paperclip agents, website generation, tool building). A 52% vulnerability rate is unacceptable. Anthropic admitted reducing thinking effort — the model may improve after they fix this.

### 3. Run Security Scan on Paperclip-Generated Code
**Category:** infrastructure
**Priority:** high
**Effort:** moderate
**Files affected:** abellminded repos

**What:** Audit the code that Paperclip agents (especially Ratchet) have generated for the brand kit, homepage, and platform. Check for common vulnerabilities (XSS, injection, SSRF, exposed secrets).
**Why:** If Opus 4.6 has a similar (or even slightly lower) vulnerability rate to 4.7, the code our agents have shipped likely contains security issues. The brand kit is public-facing at abellminded.com/identity.

### 4. Bind Kapture MCP to Localhost
**Category:** infrastructure
**Priority:** high
**Effort:** trivial
**Files affected:** Kapture MCP config

**What:** Change Kapture MCP (port 61822) from binding on all interfaces to localhost only. This was already flagged in the Apr 21 security audit.
**Why:** MCP STDIO vulnerability is architectural and Anthropic won't fix it. Any MCP service exposed on all interfaces is a risk. This was already recommended — just hasn't been done.
**Self-apply:** CANDIDATE (binding a port is a service change, not just a note — ask Alex)

### 5. Implement "Reply 1/2/3 to Approve" in Morning Summary
**Category:** workflow
**Priority:** medium
**Effort:** moderate
**Files affected:** skills/dream-cycle/SKILL.md

**What:** Change morning iMessage from "proposals ready for review" to a numbered list of top 3 proposals with "reply 1/2/3 to approve" mechanism. When Alex replies with a number, self-apply that proposal.
**Why:** 21+ proposals accumulated across 4 cycles with 0 reviewed. The delivery mechanism is broken. Alex responds to actionable asks in iMessage, not "go read a file." This is the #1 meta-problem with the dream cycle.

### 6. Add Verification Checklist to AGENTS.md (CARRY-FORWARD x2)
**Category:** workflow
**Priority:** medium
**Effort:** trivial
**Files affected:** AGENTS.md

**What:** Add formal "Pre-Report Verification" checklist alongside the existing Pre-Send Verification:
```markdown
### Pre-Report Verification (MANDATORY)
Before reporting anything as "done", "live", or "working":
1. Open the URL / file / output yourself
2. Visually confirm content renders correctly
3. Check for: broken links, placeholder text, curl artifacts, 404s
4. If you can't verify, say "deployed but not yet visually confirmed"
```
**Why:** report-without-verifying is at 6+ occurrences. Proposed last cycle. Still not applied.
**Self-apply:** CANDIDATE (non-destructive AGENTS.md addition, within policy)

### 7. Track Claude API Spending
**Category:** infrastructure
**Priority:** medium
**Effort:** moderate
**Files affected:** new monitoring script or dashboard

**What:** Set up weekly token usage reporting from the Anthropic API dashboard. Track costs by session type (cron, interactive, Paperclip).
**Why:** Claude Code Pro tier change signals pricing pressure. With 10 Paperclip agents + aggressive cron schedule + dream cycles, we could be spending more than we realize. Need visibility before it becomes a problem.

### 8. Share HN Design Homogenization with Brand Team
**Category:** workflow
**Priority:** low
**Effort:** trivial
**Files affected:** Paperclip ticket comment

**What:** Post the HN Show HN discussion about vibe-coded design monoculture to ABE-35 or ABE-43 as brand philosophy reinforcement. Alex's retrofuture aesthetic is explicitly the antidote.
**Why:** Good signal for the team. Validates the direction. Low effort, high alignment value.

## Deferred / Watching
- **Opus 4.7**: Monitor Anthropic's response to Forbes article. May improve after they address the thinking effort reduction.
- **Qwen3.6-27B**: Promising local model for simple agent tasks. Test when we have bandwidth.
- **Cognee knowledge graph**: Could automate SecondBrain imports. Watch for production readiness.
- **Anthropic Mythos breach**: Security signal. No immediate action but reinforces hardening.
- **Claude Code pricing**: Monitor for Pro/API tier changes over next 2-4 weeks.
- **OpenClaw upgrade**: Last cycle proposed upgrading to 2026.4.20. Still valid but not urgent given surgery week and Avie recovery. Schedule for this weekend.

## Self-Apply Decisions
Per AGENTS.md dream cycle self-apply policy, the following changes qualify as trivial/non-destructive:
- **#1 (stale memory)**: YES — factual corrections to TOOLS.md and MEMORY.md
- **#4 (Kapture bind)**: ASK — service configuration change
- **#6 (verification checklist)**: CANDIDATE — non-destructive AGENTS.md addition
- All others: require Alex review

## Meta
- Research scan: 10 findings, 10 kept
- Self-reflection: 5 issues identified, 8 correction patterns analyzed
- Memory verification: 8 probes, 5 passed, 3 flagged
- Deep dives: 4 topics researched
- Proposals: 8 changes suggested (3 high, 3 medium, 1 low, 1 meta)
- Carry-forwards from last cycle: 3 (stale memory, verification checklist, pricing monitoring)
- Cumulative unreviewed proposals: ~24 across 4 cycles
- Cycle duration: ~20m
