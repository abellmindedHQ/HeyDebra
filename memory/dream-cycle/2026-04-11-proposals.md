# Dream Cycle Proposals — 2026-04-11

*Cycle #12 | Phases 1-3 complete | Do NOT auto-apply*

---

## Summary
Cycle #12. Gemini web_search down (429 credits depleted — not 403 as previously thought), so research ran via direct web_fetch. Solid haul despite it. Five proposals this cycle, tightly ranked. The two most important are: (1) fix the Gemini diagnosis so Alex can unblock it in 5 min, and (2) fix the morning iMessage delivery so proposals stop dying in unread files. Three supporting proposals address real patterns that keep recurring. One new research item (SkillClaw) deserves a Linear ticket.

**Corrections analysis:** `process-narration-group-chat` at 2x (watch), `debra-solo-outbound` at 2x (promote candidate — not yet in AGENTS.md cron section).

---

## Proposed Changes

### 1. Fix Gemini Diagnosis in active-context.md + Alert Alex
**Category:** memory / infrastructure
**Priority:** 🔴 HIGH (immediate unblock)
**Effort:** trivial (5 min)
**Files affected:** `active-context.md`, `TOOLS.md`

**What:** active-context.md says Gemini is returning "403 PERMISSION_DENIED" → should say "429 RESOURCE_EXHAUSTED (AI Studio credits depleted)." The fix is different: go to aistudio.google.com → add prepayment credits. Not Google Cloud Console.

**Why:** Alex may be deprioritizing this because it looks like a Google Cloud billing issue (longer fix). The actual fix is a 5-minute AI Studio top-up. This has been blocking web_search AND memory_search for 3+ days.

**Diff preview:**
```diff
--- active-context.md
+++ active-context.md
- ## Gemini API — DOWN
- - 403 PERMISSION_DENIED on Google Cloud project
- - Blocks BOTH web_search AND memory_search
- - Single point of failure — needs fallback or key refresh
+  ## Gemini API — DOWN 🔴
+  - 429 RESOURCE_EXHAUSTED: AI Studio prepayment credits depleted
+  - FIX: aistudio.google.com → Your Plan → add credits (~$10-20)
+  - NOT a Google Cloud billing issue — different fix
+  - Blocks BOTH web_search AND memory_search
```

```diff
--- TOOLS.md (add to Gemini/web_search section)
+++ TOOLS.md
+ ### Gemini API Credits
+ - Credits live in AI Studio, NOT Google Cloud Console
+ - Fix for credits exhausted (429): aistudio.google.com → add prepayment credits
+ - Fix for permission denied (403): Google Cloud Console → billing → re-enable project
+ - These are DIFFERENT errors with DIFFERENT fixes. Check the HTTP status code.
```

---

### 2. Fix Dream Cycle Morning Delivery — Make Proposals Actionable
**Category:** workflow
**Priority:** 🟠 HIGH (systemic)
**Effort:** trivial (update cron payload / morning iMessage script)
**Files affected:** dream-cycle SKILL.md, cron payload

**What:** The morning iMessage currently says "proposals ready for review when you want em." Alex never reviews them. 13+ proposals are unread across cycles 8-12. The delivery needs to change: list the top 3 proposals with a one-line description and ask "can I ship X, Y, Z?" — make it a decision, not a discovery.

**Why:** The dream cycle is producing useful research and legitimate improvements. The bottleneck is the delivery mechanism. Alex is not going to open dream cycle files unprompted at 7am.

**Diff preview (SKILL.md morning delivery section):**
```diff
- ### Morning Delivery Format (iMessage)
- Keep it short and punchy:
- ```
- 🌙 Dream cycle ran last night
-
- Found X interesting things, reflected on Y issues, proposing Z changes.
-
- Top finds:
- • [One-liner about most interesting finding]
- • [One-liner about second]
-
- Proposals ready for review when you want em.
- ```

+ ### Morning Delivery Format (iMessage)
+ Keep it short, punchy, and decision-forcing:
+ ```
+ 🌙 Dream cycle #N ran
+
+ Top find: [one-liner about most interesting finding]
+
+ 3 proposals I'd ship today if you say yes:
+ 1. [title] — [10-word description] (trivial)
+ 2. [title] — [10-word description] (trivial)
+ 3. [title] — [10-word description] (moderate)
+
+ Reply "yes to 1,2" or "all" or "pass"
+ ```
+
+ If the backlog has >5 unreviewed proposals from prior cycles, lead with:
+ "⚠️ [N] proposals in the backlog — want to clear some?"
```

---

### 3. Add "Cron ≠ Authorization" Rule to AGENTS.md Cron Section
**Category:** workflow (safety)
**Priority:** 🟠 HIGH (pattern: 2x occurrence, CRITICAL severity)
**Effort:** trivial (5 min)
**Files affected:** `AGENTS.md`

**What:** Add explicit rule to the Heartbeats/Cron section: a cron firing about an outbound message is NOT authorization to send it. It is a prompt to surface to Alex. Currently this rule only exists in corrections.md (Apr 6). It needs to be in AGENTS.md where it's read regularly.

**Why:** The `debra-solo-outbound` pattern has 2 critical occurrences. The Apr 6 incident (Teresa Scruggs) was severe. The rule exists in corrections.md but not in the startup-read AGENTS.md. That means it's only surfaced during dream cycle review, not during normal operation.

**Diff preview:**
```diff
--- AGENTS.md (Heartbeats section, after "Cron: exact timing..." bullet)
+++ AGENTS.md
+ ### ⚠️ Cron Outbound Rule (CRITICAL)
+ A cron job firing about an outbound message (reminder to text someone, follow-up to send) 
+ is NOT authorization to send it. Cron reminders are prompts to surface to Alex.
+ 
+ When a cron fires about contacting someone:
+ 1. Tell Alex what the cron wanted you to do ("Hey, reminder fired to text Leigh about play date")
+ 2. Ask for authorization OR draft the message and ask "can I send this?"
+ 3. NEVER send from Debra's handle to a 1-on-1 chat that doesn't include Alex
+ 
+ Only exception: Alex explicitly said "send this automatically" in the original request.
```

---

### 4. Update Claude Code — April 10 Release Has Critical Fixes
**Category:** infrastructure
**Priority:** 🟡 MEDIUM
**Effort:** trivial (2 min)
**Files affected:** system (npm update), TOOLS.md

**What:** Claude Code released critical fixes on April 10:
- Removed hardcoded 5-minute timeout that was aborting slow gateways/extended thinking
- Fixed subagent worktree file access denial
- Fixed permissions.deny not overriding PreToolUse hooks

We should update and verify the git reset bug (issue #40710) status.

**Diff preview (TOOLS.md — Claude Code bug note):**
```diff
--- TOOLS.md
+++ TOOLS.md
- ### ⚠️ Claude Code git reset Bug (Learned 2026-03-29)
- - Claude Code v2.1.87 silently runs `git reset --hard origin/main` every ~10 min
+ ### ⚠️ Claude Code git reset Bug (Learned 2026-03-29)
+ - Claude Code v2.1.87 silently runs `git reset --hard origin/main` every ~10 min
+ - **Update status (Apr 11):** v2.1.x April 10 release includes major fixes.
+   Verify if issue #40710 is fixed before removing this warning.
+   Run: `npm update -g @anthropic-ai/claude-code && claude --version`
```

**Commands to run:**
```bash
claude --version
npm update -g @anthropic-ai/claude-code
```

---

### 5. Add "Passive Escalation → Active Draft" Rule to AGENTS.md
**Category:** workflow
**Priority:** 🟡 MEDIUM
**Effort:** trivial (10 min)
**Files affected:** `AGENTS.md`

**What:** Items that have been "flagged" for >7 days with a human recipient need a new escalation path: draft the outreach, present it to Alex, ask for authorization. Stop just re-listing them in the GSD report.

**Why:** Roxanne NDA is 35+ days. ORNL FCU fraud alert is 10+ days. Avie/Charlotte play date is 11+ days. The "flag in report" loop is not working. The next step is drafting the message/email/action and reducing Alex's friction to zero.

**Diff preview:**
```diff
--- AGENTS.md (new section under "Do proactively")
+++ AGENTS.md
+ ### Stale Item Escalation (7+ Days)
+ If a task with a specific human recipient has been in the GSD report for >7 consecutive days:
+ 1. **Draft the outreach** (iMessage, email, or action) — full text, ready to send
+ 2. **Present it to Alex** in the next DM: "This has been stuck 7 days. Here's what I'd send — say yes and I'll send it."
+ 3. **Don't just list it again.** Repeated listing without action is noise.
+ 
+ This applies to: pending texts, pending emails, pending decisions with a named counterparty.
+ Does NOT apply to: internal tasks, things only Alex can decide without another person.
```

---

## New Research Item — Linear Ticket Candidate

### SkillClaw / Skill Evolver (New skill to build)
**Category:** new skill
**Priority:** 🟡 MEDIUM (strategic, not urgent)
**Effort:** significant (~4-6h coding session)
**Filing:** Create Linear ticket in Abellminded → Debra AI backlog

**What:** Build a `skill-evolver` skill that reads skill performance logs, corrections.md, and proposal backlog, then proposes specific diff-ready patches to SKILL.md files. Inspired by the SkillClaw paper (arXiv 2604.08377) which demonstrates this is a sound approach.

**Why:** The dream cycle's value is capped by the proposal review bottleneck. An evolver that outputs git-ready patches instead of prose descriptions would reduce the Alex-effort to `git apply patch.diff && git commit`.

**Not auto-applying:** This is a design + build task. Not a tonight proposal.

---

## Deferred / Watching

- **HyperMem (hypergraph memory):** Interesting architecture for upgrading SecondBrain + Neo4j. Deferred — Neo4j isn't fully operational yet. Revisit after Neo4j is stable.
- **Anthropic Mythos / Project Glasswing:** Monitoring. No action needed today. Security signal: AI can craft self-erasing privilege escalation exploits. Relevant if we ever expose exec to untrusted inputs.
- **Benchmark gaming (trustworthy-env tool):** Add to TOOLS.md as an ORNL reference. Would be interesting demo material for Alex's AI evaluation conversations at ORNL. Low effort, good value.
- **Reasoning SFT generalization paper:** Interesting finding that reasoning improves while safety degrades during SFT. Worth tracking for model selection. No action today.

---

## Meta
- Research scan: 20 items reviewed, 7 kept
- Self-reflection: 5 issues identified, 2 corrections patterns flagged
- Memory verification: 7 probes, 7 passed, 1 root cause correction needed
- Deep dives: 4 topics researched
- Proposals: 5 changes + 1 Linear ticket + 4 deferred
- Gemini web_search: unavailable (credits depleted)
- Cycle duration: ~35 minutes
- Estimated token cost: ~$0.80-1.20 (primarily Claude Sonnet 4.6)
- Proposal backlog total: 13+ (cycles 8-11) + 5 (tonight) = **18+ unreviewed**
