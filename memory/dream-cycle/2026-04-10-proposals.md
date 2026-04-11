# Dream Cycle Proposals — 2026-04-10

## Summary
Cycle #11. Three strong research threads tonight: Hermes Agent (major competitive signal with OpenClaw migration command), Multica (managed agents platform with explicit OpenClaw support — possible ORNL Transformation pitch), and Karpathy's four coding principles (immediately applicable, trivial to ship). Self-reflection surfaced a recurring theme: I know what to fix but I'm not fixing it fast enough. Proposal backlog is now 13+ items over multiple cycles. Tonight's proposals are capped at 6, tightly ranked by impact/effort ratio. Three are genuinely trivial. Corrections analysis: `process-narration-group-chat` is a 3x+ promotion candidate but it's already in MEMORY.md — the issue is the framing needs to be more visceral and the enforcement needs to be structural, not just a rule.

---

## Proposed Changes

### 1. Add Pre-Task Protocol to AGENTS.md (Karpathy Principle)
**Category:** workflow
**Priority:** high
**Effort:** trivial (~10 min)
**Files affected:** `AGENTS.md`

**What:** Add a "Pre-Task Protocol" section to AGENTS.md that requires explicit assumption-stating, ambiguity surfacing, and success criteria definition before starting any non-trivial task. Derived from Karpathy's "Think Before Coding" and "Goal-Driven Execution" principles.

**Why:** The two most expensive mistakes this week (solo messaging, narration leaking into group chats) both involved me silently assuming context and running with it. This protocol forces me to surface ambiguity before acting, not after.

**Diff preview:**
```markdown
## Pre-Task Protocol (Non-Trivial Work)

Before starting any task that involves: external communication, code changes, 
file destructive operations, or multi-step workflows:

1. **State your understanding** of what's being asked (one sentence)
2. **Surface ambiguities** — name what's unclear, ask before assuming
3. **Define success criteria** — what does done look like?
4. **Estimate scope** — if it's bigger than 20 min, say so upfront

Skip for: quick lookups, obvious 1-liners, simple questions.
Apply for: anything that could go wrong in an irreversible way.
```

---

### 2. Fix Gemini Single-Point-of-Failure — Add Startup Health Check
**Category:** workflow / infrastructure
**Priority:** high
**Effort:** trivial (~15 min)
**Files affected:** `AGENTS.md` (startup instructions section)

**What:** Add a Gemini API health check to session startup instructions. If Gemini is returning 403, log it immediately and note which tools are degraded. Also add a note to MEMORY.md that Gemini outages silently kill BOTH web_search AND memory_search simultaneously — this is a critical dependency that many sessions don't realize until they're mid-task.

**Why:** Gemini 403 has been running for 3+ days. I've been noting it every night but not doing anything about it. The actual fix (top up Google Cloud billing) is Alex's — but I can make the failure louder so he can't ignore it.

**Diff preview:**
```markdown
## Session Startup — Add to step 5:
Run `memory_search` probe on startup. If it returns `disabled=true` or 403:
- Log: "⚠️ Gemini API down — web_search AND memory_search are degraded"
- Tell Alex in the first response of the session
- Do NOT silently proceed as if search is working

Note for MEMORY.md addition:
"Gemini API failure = BOTH web_search AND memory_search go down simultaneously. 
Check Google Cloud billing at console.cloud.google.com. This is the #1 silent 
infrastructure failure mode."
```

---

### 3. Install Karpathy Skills Plugin for Claude Code
**Category:** infrastructure
**Priority:** high
**Effort:** trivial (1 command)
**Files affected:** Claude Code plugin registry

**What:** Install the andrej-karpathy-skills plugin into Claude Code. Makes four coding principles (Think Before Coding, Simplicity First, Surgical Changes, Goal-Driven Execution) available system-wide across all Claude Code sessions.

**Why:** 1,450 stars/day today, derived from Karpathy's analysis of LLM coding pitfalls that apply directly to how I write code and how our coding-agent skill spawns sub-agents. Directly addresses the "touches too much code" and "silent wrong assumption" failure modes.

**Diff preview:**
```bash
# Run in Claude Code session:
/plugin marketplace add forrestchang/andrej-karpathy-skills
/plugin install andrej-karpathy-skills@karpathy-skills
```
Note: Alex approves. Debra executes.

---

### 4. Escalate Roxanne NDA — Draft the Email
**Category:** workflow (operational)
**Priority:** high
**Effort:** trivial (write the draft, surface to Alex)
**Files affected:** none permanent (iMessage/email draft)

**What:** Stop flagging "Roxanne NDA 34 days stale" in GSD reports and actually do something about it. Draft a concise check-in message that Alex can review and send. The NDA blocks a ~$8K app decision. Every extra day of silence is a signal Roxanne may interpret as disinterest.

**Why:** Flagging isn't helping. Doing is. If I have enough context to flag it, I have enough context to draft it. The draft should be warm, specific, and reference the app pitch. Alex reviews and approves before anything goes out.

**Diff preview (draft for Alex's approval):**
```
Hey Rox — I know I've been slow on this. I want to make sure we protect both 
of us on the Saturn Return app project. Can we find 20 minutes this week to 
talk through the NDA? I'll have something simple prepped. 

[Alex sends this, not Debra]
```

---

### 5. Explore Multica for ORNL Transformation Pitch
**Category:** infrastructure / workflow
**Priority:** medium
**Effort:** moderate (1-2 hours exploration, 30 min brief)
**Files affected:** none (exploration task)

**What:** Stand up Multica locally, connect it to OpenClaw daemon, run 2-3 agent tasks through it, and write a 1-page brief on whether it's viable as a Transformation Group tool at ORNL. The pitch: open-source managed agents platform that turns coding agents into trackable team members, self-hosted, works with OpenClaw already.

**Why:** Alex leads 30 web devs at ORNL with a transformation mandate. Multica explicitly supports OpenClaw as a runtime. This is the most concrete "AI in dev teams" tool that connects directly to Alex's ORNL role and his broader platform vision. If it's good, it could become the infrastructure layer under HeyDebra for team deployments.

**Diff preview:**
```bash
# Exploration commands (when Alex approves):
docker compose -f docker-compose.selfhost.yml up -d  # self-hosted option
# OR: brew tap multica-ai/tap && brew install multica  # cloud option
multica daemon start  # connects to local OpenClaw
```
Write brief to: `~/.openclaw/workspace/research-multica-ornl.md`

---

### 6. File Upstream BB Attachment Bug Report
**Category:** infrastructure
**Priority:** medium
**Effort:** moderate (30 min to write, 5 min to file)
**Files affected:** github.com/openclaw/openclaw (external issue tracker)

**What:** Write and file an upstream GitHub issue for the BB attachment bug. Current patches in dist files will be wiped on next `npm update`. The issue should include: exact code locations (extractAttachments() line 562, download logic lines 1378-1400, enqueue line 2108), sample log output showing attachmentCount=0 vs. occasional attachmentCount=7, and the reproduction steps.

**Why:** We've been debugging this for 3 days. We have enough information to file a quality report. Without an upstream fix, every `npm update` will silently revert our workarounds and the bug will reappear. This is the cheapest way to get a durable fix.

**Diff preview:**
```markdown
Title: [bluebubbles] Attachments not surfaced in session context — extractAttachments() 
returns empty array on webhook delivery

Body:
- BB webhook fires, `message["attachments"]` is empty despite attachments being 
  present in BB database
- Workaround: manual fetch via /api/v1/attachment/{guid}/download works
- Intermittent: attachmentCount=7 observed once, suggesting timing or payload-shape issue
- Key code locations: extractAttachments() line 562, download logic 1378-1400, 
  enqueue 2108 (channel.runtime-BSXlY6sk.js)
- Patched dist files as temporary workaround (will be overwritten on npm update)
```

---

## Deferred / Watching

- **Hermes Agent migration risk**: `hermes claw migrate` exists. Watch 30 days. If OpenClaw release cadence or Gemini stability doesn't improve, revisit. Not switching — too much custom work here — but the signal is real.
- **agentskills.io compatibility**: Check if our SKILL.md format is compatible. Could be free discoverability. Low effort when we have spare cycles.
- **Checkpoint mechanism for background tasks**: 5 tasks lost to Apr 9 restart. Need a pattern for persisting task state across gateway restarts. Punted — too architectural for tonight.
- **Multica for personal projects (Abellminded)**: Lower priority than ORNL use case. Queue behind ORNL exploration.
- **OpenAI Codex pay-as-you-go pricing**: Relevant if Alex decides to renew OpenAI Plus or evaluate team use at ORNL. Note for next ORNL Transformation planning conversation.
- **Supply chain security sweep**: JSON Formatter compromise + Axios dev tools + CPUID site hack = active threat cluster. Alex's Chrome extensions should be audited. Low priority unless the healthcheck skill runs first.
- **OpenAI acquires TBPN (Apr 2)**: Interesting for AI media/content landscape but not directly actionable.

---

## Meta

- Research scan: 9 findings, 9 kept (all relevant)
- Self-reflection: 6 issues identified, 2 corrections to watch
- Deep dives: 3 topics (Hermes Agent, Multica, Karpathy Skills)
- Proposals: 6 changes suggested (3 trivial, 2 moderate, 1 operational)
- web_search: DOWN (Gemini API 403) — used web_fetch fallback throughout
- memory_search: DOWN (same Gemini dependency)
- Estimated cost: ~$0.80–1.20 (sonnet + fetches, no Opus used this cycle)
- Cycle duration: ~25 min

**Backlog status:** Previous cycle proposals (2026-04-09) include 8 items still awaiting Alex review. Please carve out 15 min to triage. Recommend: approve/reject each with a thumbs up/down, no need for detailed discussion unless one is unclear.
