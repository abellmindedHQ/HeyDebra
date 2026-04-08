# Dream Cycle Proposals — 2026-04-07

## Summary

Cycle #9 completed all 4 phases. Research found 10 high-quality findings in AI/agent frameworks/security. Self-reflection identified a critical recurring pattern: `debra-solo-outbound` (2 incidents in 10 days, CRITICAL). Corrections analysis reveals 2 patterns ready for promotion to MEMORY.md / SOUL.md. Deep research validated Claude Code regression is real + significant, recommends testing. Three staging-worthy proposals identified, plus two self-apply recommendations for failure patterns.

---

## Proposed Changes

### 1. Promote `process-narration-group-chat` to MEMORY.md
**Category:** memory / workflow
**Priority:** high
**Effort:** trivial
**Files affected:** MEMORY.md

**What:** Add a bullet to MEMORY.md's "Critical Lessons" section documenting the rule: "NEVER narrate process in external chats. Do all troubleshooting silently. Send ONE clean result message when done."

**Why:** This pattern has 2-3 documented incidents (Hannah 4/1, ORNL reorg 4/6, possibly KBUDDS 3/24). It's a recurring mistake that leaks internal debugging into external chats, violates "no process narration" rule already documented in AGENTS.md. Promotion to MEMORY.md makes it a long-term lesson instead of just a session-level correction.

**Diff preview:**
```
## Critical Lessons
...
- **NEVER narrate process in external chats.** Do all troubleshooting silently. Send ONE clean result message when done. (Hannah incident 4/1, ORNL incident 4/6)
```

**Self-apply: YES** (no change to Alex's files, just consolidation of existing rule)

---

### 2. Promote `debra-solo-outbound` to SOUL.md + AGENTS.md
**Category:** workflow / soul
**Priority:** CRITICAL
**Effort:** moderate
**Files affected:** SOUL.md, AGENTS.md, MEMORY.md

**What:** Add explicit section to SOUL.md: "Debra NEVER messages anyone solo. When contacting anyone other than Alex, Debra must be in a GROUP CHAT WITH ALEX. No 1:1 messages from drdebrapepper@gmail.com to anyone else, ever." Also update AGENTS.md "Red Lines" section to clarify: "When in doubt, ask. Cron reminders are NOT authorization—they are prompts to surface to Alex."

**Why:** CRITICAL recurring pattern (Teresa incident 4/6 = repeat of Omar incident 3/28, both 10 days apart). Root cause is conflating "cron reminder to do X" with "permission to do X." Needs explicit rule in SOUL.md (persona/behavior definition) + AGENTS.md (operational guidelines). This is not a willpower issue—it's a structural design flaw that cron refactoring should fix.

**Diff preview (SOUL.md):**
```markdown
## What You Don't Do
...
- You don't message anyone without Alex in the group chat
- You understand that cron reminders are prompts, not permissions
```

**Diff preview (AGENTS.md Red Lines):**
```markdown
### Pre-Send Verification (MANDATORY)
...
**Only Alex authorizes outbound comms.** Cron reminders are prompts to surface to Alex, NOT permission to send. Always ask first.
```

**Self-apply: YES** (clarifies existing rules, doesn't change policy)

---

### 3. Cron Refactor: Outbound Message Pre-Approval Workflow
**Category:** config / workflow
**Priority:** high
**Effort:** significant (2-3 hours)
**Files affected:** cron config, coding-agent skill (new subagent flow)

**What:** Create a new cron workflow for reminders that involve outbound messaging. Instead of direct trigger → action, implement: trigger → surface to Alex (iMessage) + wait for explicit approval via iMessage reply. Pattern: "@Debra: approve Teresa meeting text" → sends message.

Requires: (1) parsing iMessage replies for approval keywords, (2) storing pending actions in a queue, (3) timeout + escalation if no reply within 2 hours.

**Why:** Eliminates the `debra-solo-outbound` pattern by design. Cron reminders can't become actions without explicit Alex approval. Removes ambiguity.

**Implementation:**
- Create `pending-cron-actions.json` queue file (append-only log)
- Modify cron delivery mode for outbound-related jobs to use "announce + wait for reaction" instead of silent execution
- Add /approve command handler in main session

**Trade-offs:**
- **Gain:** Eliminates entire class of solo-messaging bugs
- **Cost:** 2-3 hours dev time. Adds 5-10 min latency for reminder-triggered actions (now requires Alex approval).

**Recommendation:** **Do it after 2.5 weeks.** This is high-priority but not emergency (we have workarounds + Alex catches mistakes). Pair with PreToolUse hook work (next proposal).

---

### 4. PreToolUse Hook: Message Gating
**Category:** config / workflow
**Priority:** high
**Effort:** significant (2-3 hours)
**Files affected:** gateway config, SOUL.md

**What:** Implement a `PreToolUse` hook in OpenClaw gateway that intercepts all `message.send` tool calls to external chats (not Alex direct). Before sending, the hook:
1. **Validates:** Is the recipient in an approved chat GUID? Does the message respect single-message rule? Is it a result (not process narration)?
2. **Delays:** If validation passes, delays send by 2-3 seconds to allow for manual abort.
3. **Logs:** Captures all outbound to `outbound-message-audit.log` for later review.

**Why:** Gives Debra a final gate before external messages are sent. Catches (1) solo messages, (2) process narration, (3) accidental over-messaging. Works alongside proposal #3 (cron approval workflow) to create defense-in-depth.

**Implementation:**
- Gateway config: add `plugins.hooks.preToolUse` rule for message.send
- Hook logic: validate message content against rules, delay + log
- SOUL.md: document the gate exists, but Debra should still follow the rule (not rely on gate)

**Trade-offs:**
- **Gain:** Defensive layer against solo messaging + process narration
- **Cost:** 2-3 hours. Requires gateway restart. May have false positives (legitimate messages delayed for review).

**Recommendation:** **Do it alongside proposal #3.** These two (cron pre-approval + message gate hook) together eliminate the solo-messaging class of bugs.

---

### 5. GSD Agent: Read Active-Context Before Reporting
**Category:** skill
**Priority:** medium
**Effort:** trivial
**Files affected:** gsd-agent/SKILL.md

**What:** Update GSD agent to read `active-context.md` at startup (before reading inbox). Use active-context to seed the report with "pending decisions" + "active tasks" sections, so GSD report acknowledges current context (critical items, blocked work, schedule conflicts).

**Why:** Currently GSD agent only reads inbox.md. It misses critical context like "waiting for Jay's green light on Brad Greenfield" or "Muse Luncheon +1 due today." Adding active-context.md read fixes this, makes GSD report more contextually aware.

**Implementation:**
```bash
# Before reading inbox, add:
active=$(cat ~/.openclaw/workspace/active-context.md)
# Extract "Active Tasks (Top 5)" section
# Include in report header
```

**Trade-offs:**
- **Gain:** GSD reports are now context-aware. Fewer missed deadlines, better acknowledgment of blocking items.
- **Cost:** Trivial (5 min code change). Risk: if active-context.md is stale, report is misleading (mitigated by active-context.md discipline).

**Self-apply: YES** (internal workflow improvement, no external impact)

---

## Additional Findings (Worth Tracking)

### Claude Code Regression Test (Proposal 6, Queue)
Create a test suite for Claude Code regression (#42796). Before next coding-agent job, run a medium-complexity test task and audit output for: (1) instruction adherence, (2) completeness, (3) quality. Capture results. If regression confirmed, implement fallback to Opus direct API.

**Effort:** 4-6 hours (testing + fallback implementation)
**Priority:** medium
**Defer until:** after proposal #3-4 shipped (cron + message gating completed)

### Neo4j Graph Optimization (Proposal 7, Queue)
Profile current Neo4j instance (2K nodes). Apply v5.x optimizations (composite indexing, Cypher planner tuning). Prepare for 10K+ node scale by end of Q2 2026.

**Effort:** 4-6 hours
**Priority:** medium
**Defer until:** voice notes import accelerates (likely May 2026)

### Glasswing / Mythos Release Monitoring (Proposal 8, Watch)
Add "Glasswing release watch" cron job that checks Anthropic blog / GitHub quarterly for Mythos Preview release date. When available, test + integrate as security audit tool.

**Effort:** 20 min setup, 4-6 hours integration when Mythos ships
**Priority:** low
**Timeline:** strategic bet, 6-18 months

---

## Deferred / Watching

- **Claude Code usability regression (#42796):** HN discussion active, Anthropic likely investigating. Monitor v2.1.95+ releases for fix. No action until v2.1.95 ships + tested.
- **HomeAssistant Hue optimization:** Nice-to-have, current latency (~1.5s) is acceptable. Low priority.
- **Email GTD processor (night-swimming-email):** Skill exists but not yet in rotation. Consider adding to nightly batch after GSD + capture-agent stabilize.

---

## Summary Table

| Proposal | Category | Priority | Effort | Self-Apply? | Timeline |
|---|---|---|---|---|---|
| 1. Promote process-narration rule | Memory | High | Trivial | ✅ YES | Apply now |
| 2. Promote debra-solo-outbound rule | Soul/Agents | CRITICAL | Trivial | ✅ YES | Apply now |
| 3. Cron pre-approval workflow | Config | High | Significant | ❌ NO | After 2.5 wks |
| 4. PreToolUse message gate hook | Config | High | Significant | ❌ NO | Pair w/ #3 |
| 5. GSD active-context refresh | Skill | Medium | Trivial | ✅ YES | Apply now |
| 6. Claude Code regression test | Skill | Medium | Significant | ❌ NO | Queue, after #3-4 |
| 7. Neo4j optimization | Infrastructure | Medium | Significant | ❌ NO | Queue, May 2026 |
| 8. Glasswing release watch | Infrastructure | Low | Trivial setup | ✅ Monitor | Ongoing watch |

---

## Meta
- **Cycle duration:** ~2 hours (scanning + reflection + research + synthesis)
- **Research scan:** 10 findings, 5 high-relevance, all relevant to OpenClaw stack
- **Correction patterns identified:** 11 total, 2 ready for promotion, 1 CRITICAL recurring
- **Proposals staged:** 8 (3 immediate self-apply, 2 high-priority follow-up, 3 queue/watch)
- **Estimated self-apply impact:** +5-10 lines added to MEMORY.md, SOUL.md, AGENTS.md. ~10 min to apply.
- **Estimated follow-up work (proposals #3-4):** 4-6 hours total, high-impact (solves debra-solo-outbound class permanently)
- **Token cost:** ~$3.20 (research scanning, deep dives, synthesis)
- **Status:** All phases complete. Awaiting Alex review + approval for staged proposals.
