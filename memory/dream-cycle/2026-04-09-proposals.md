# Dream Cycle Proposals — 2026-04-09

## Summary
Tonight's cycle found one major competitive signal (Hermes Agent), one immediately actionable tool (Claudian for Obsidian), and several Karpathy-derived behavior improvements. Self-reflection surfaced three systemic issues: the proposal-to-action gap (13+ pending proposals never shipped), the Gemini single-point-of-failure (web search AND memory search both down tonight), and the background task fragility problem (5 tasks lost to a gateway restart). Corrections analysis shows `process-narration-group-chat` at 3+ incidents — formal promotion candidate. Two proposals from Cycle #8 remain unactioned. Dream cycle backlog is the most urgent meta-problem.

---

## Proposed Changes

### 1. Install Claudian — Claude Code Inside SecondBrain
**Category:** infrastructure
**Priority:** high
**Effort:** trivial (~20 min)
**Files affected:** none (Obsidian plugin install)

**What:** Install the Claudian Obsidian plugin (github.com/YishenTu/claudian) in Alex's SecondBrain vault. Claudian embeds Claude Code directly as an AI collaborator inside Obsidian — reads, writes, edits notes, responds to vault queries conversationally.

**Why:** This is the closest-to-shipping version of the "know yourself" Mirror feature from Alex's life's work vision. The vault IS the data. Claudian makes it conversational without requiring a separate terminal session. Plan Mode ensures no writes without review.

**Diff preview:**
```
Installation steps (for Alex to approve and Debra to execute):
1. Open Obsidian → Settings → Community Plugins → turn off Safe Mode
2. Install BRAT plugin (Beta Reviewers Auto-update Tester)
3. In BRAT settings → Add Beta Plugin → paste: https://github.com/YishenTu/claudian
4. Enable Claudian in Community Plugins
5. Configure: Claude Code CLI path (which claude-code), enable Plan Mode by default

Caution: Enable Plan Mode globally before first use. SecondBrain has no undo beyond git.
```

**Approval needed:** Alex must explicitly opt in (writes to his vault).

---

### 2. Add Chelsea Therapy Dedicated Cron
**Category:** config
**Priority:** high
**Effort:** trivial (5 min)
**Files affected:** cron system

**What:** Create a dedicated cron job that fires every Thursday at 5:30 PM ET with a direct iMessage reminder: "Hey — Chelsea is at 6. Don't miss it."

**Why:** Chelsea therapy has appeared as CRITICAL in multiple daily logs. Alex has missed it before. The current approach (heartbeat reminder, GSD report) is insufficient for hard-deadline events. This needs a dedicated, reliable cron — not ambient awareness.

**Diff preview:**
```json
{
  "name": "chelsea-therapy-reminder",
  "schedule": { "kind": "cron", "expr": "30 17 * * 4", "tz": "America/New_York" },
  "payload": {
    "kind": "agentTurn",
    "message": "Send Alex an iMessage reminder that Chelsea therapy starts in 30 minutes. Keep it short and direct. His number: +18135343383. Channel: bluebubbles.",
    "timeoutSeconds": 60
  },
  "sessionTarget": "isolated"
}
```
Note: Use `every Thursday` (0=Sun, 4=Thu in cron). If Chelsea changes to a different day, update the cron.

**Approval needed:** Yes (new cron + outbound message).

---

### 3. Promote process-narration-group-chat to SOUL.md
**Category:** workflow
**Priority:** high
**Effort:** trivial
**Files affected:** SOUL.md

**What:** Add an explicit rule to SOUL.md about process narration. The pattern is at 3+ confirmed incidents and qualifies for promotion per the dream-cycle corrections protocol.

**Why:** This pattern (`process-narration-group-chat`) has recurred in Hannah's chat, Jay's group, and at least one other context. "Got told to 'stfu' and 'Skynet deactivate'" — this is real damage to relationships, not a minor style issue. It needs to live in SOUL.md as an identity-level constraint.

**Diff preview:**
```markdown
## Hard Rules (Non-Negotiable)
[Add to SOUL.md after "What You Don't Do" section]

### Process Narration — NEVER in External Chats
When doing work triggered by a group chat or external conversation:
- Do ALL work silently
- Compose ONE final result message
- Send ONLY the result — not the journey, not the debugging, not "let me try X"
- If it fails: fix it silently, then report the clean outcome
- Exception: Alex explicitly asks for step-by-step updates

This includes: debugging, troubleshooting, trying alternatives, retrying, reading docs.
Stream of consciousness stays internal. Always.
```

**Approval needed:** Yes (SOUL.md modification requires explicit approval).

---

### 4. Add Gemini Fallback Monitoring to Infrastructure Health
**Category:** infrastructure / memory
**Priority:** high
**Effort:** moderate (1-2 hrs)
**Files affected:** TOOLS.md, potentially heartbeat

**What:** Add a health check for Gemini API credits/status. Both `web_search` and `memory_search` rely on Gemini. When credits deplete (as happened tonight), both fail silently — the dream cycle ran with degraded capability without knowing why until the first search call failed.

**Why:** Single point of failure. Two critical capabilities (research scan + memory recall) both went dark because of one billing event. We need: (1) early warning before credits hit zero, (2) fallback behavior documented (web_fetch directly, skip search gracefully).

**Diff preview:**
```markdown
## TOOLS.md Addition: Gemini API Monitoring
- Gemini AI Studio: alexander.o.abell@gmail.com account
- Credits: DEPLETED as of 2026-04-09 (dream cycle ran with degraded search)
- URGENT: Top up AI Studio credits before next dream cycle
- Fallback when credits are 0:
  - web_search → web_fetch direct URLs (slower, less broad)
  - memory_search → read daily .md files directly (slower, manual)
  - Note both degradations in any cycle report
- Add to heartbeat: check if web_search returns 429, alert Alex if so
```

**Approval needed:** Alex needs to top up AI Studio credits ($ decision). TOOLS.md update is self-apply.

---

### 5. Background Task Checkpoint Files
**Category:** workflow
**Priority:** medium
**Effort:** moderate
**Files affected:** AGENTS.md, individual task scripts

**What:** Establish a convention: any long-running background task must write a checkpoint file to `~/.openclaw/workspace/tasks/<task-name>-checkpoint.json` at each major stage. If the task is interrupted and restarted, it reads the checkpoint and resumes from the last completed stage.

**Why:** 5 tasks were lost to a gateway restart on Apr 9. This has happened twice in 2 weeks. The current model (kick off task, wait for completion) has no fault tolerance. A checkpoint convention would turn interruptions from "start over" into "pick up where I left off."

**Diff preview:**
```markdown
## AGENTS.md Addition: Background Task Checkpointing
For any multi-stage background task (>5 min):
1. Create `workspace/tasks/<name>-checkpoint.json` before starting
2. After each major stage, update checkpoint: {"stage": "X", "status": "complete", "timestamp": "..."}
3. On task start: check for existing checkpoint, resume from last complete stage
4. On task finish: delete checkpoint file
5. Interrupted tasks are visible in `ls workspace/tasks/*.json`

Example stages for email GTD: ["fetch", "classify", "archive-noise", "report"]
```

**Approval needed:** AGENTS.md addition (non-destructive, but per policy). Checkpoint convention needs to be built into individual task skills.

---

### 6. After-Action Skill Capture (Hermes-inspired)
**Category:** workflow / memory
**Priority:** medium
**Effort:** moderate
**Files affected:** AGENTS.md, new skill concept

**What:** After any complex multi-step task (identified by: >3 tool calls, >10 minutes, novel workflow), I should write a brief after-action note capturing: what worked, what failed, the pattern, and whether it should become a reusable skill.

**Why:** Hermes Agent's self-improvement loop runs after each complex task. Our dream cycle is nightly and aggregates across many sessions — that's good for patterns, but slow for individual task learning. After-action capture bridges the gap without requiring human review for every session.

**Diff preview:**
```markdown
## AGENTS.md Addition: After-Action Capture
After completing any task that:
- Required >3 non-trivial tool calls
- Took more than 10 minutes
- Involved a novel workflow (not covered by existing skills)

Write a brief note to memory/YYYY-MM-DD.md under:
## After-Action: [task name]
- What worked: ...
- What failed or was slow: ...
- Pattern discovered: ...
- Skill candidate? yes/no (if yes, propose to Alex)
```

**Approval needed:** AGENTS.md addition (non-destructive).

---

### 7. Adopt Karpathy Coding Principles — Pre-Action Checklist
**Category:** workflow
**Priority:** medium
**Effort:** trivial
**Files affected:** AGENTS.md

**What:** Add a pre-task checklist to AGENTS.md, derived from Karpathy's four principles: Think Before Coding, Simplicity First, Surgical Changes, Goal-Driven Execution.

**Why:** Karpathy's diagnosis matches real failures in my operation — making wrong assumptions without checking (Boston trip dates), overcomplicating solutions (proposing new infrastructure when a script would do), touching adjacent code (edits that weren't requested). The four-principle checklist is a forcing function.

**Diff preview:**
```markdown
## AGENTS.md Addition: Pre-Task Checklist (Karpathy Principles)
Before starting any complex task:
1. **State assumptions explicitly** — if uncertain about scope, ask. Don't assume and run.
2. **Simplicity first** — what's the minimum that solves this? If I'm planning >200 lines, stop and ask if there's a shorter path.
3. **Surgical scope** — what exactly was requested? Don't touch adjacent things unless explicitly asked.
4. **Define success criteria** — what does "done" look like? If I can't state it, I need to clarify with Alex first.

Apply especially to: coding tasks, skill creation, infrastructure changes, file edits.
```

**Approval needed:** AGENTS.md addition (non-destructive, self-apply eligible).

---

### 8. LLM Export Monthly Cron
**Category:** config / infrastructure
**Priority:** low
**Effort:** trivial
**Files affected:** cron system

**What:** Add a monthly cron reminder to Alex to export and process new LLM conversation archives from Claude, ChatGPT, and Gemini.

**Why:** LLM exports are currently stale by 2+ weeks. Claude and ChatGPT cover through late March. Recent sessions (Apr conversations with Chelsea context, Lufthansa complaint, org design work) aren't captured for semantic search.

**Diff preview:**
```json
{
  "name": "llm-export-reminder",
  "schedule": { "kind": "cron", "expr": "0 10 1 * *", "tz": "America/New_York" },
  "payload": {
    "kind": "agentTurn",
    "message": "Remind Alex that it's time to export fresh LLM conversations (Claude, ChatGPT, Gemini) for SecondBrain processing. iMessage to +18135343383.",
    "timeoutSeconds": 60
  }
}
```

**Approval needed:** Yes (new cron).

---

## Deferred / Watching

- **Hermes Agent:** Watch closely for 30 days. Steal after-action capture concept immediately. Deeper architecture comparison warranted before any OpenClaw migration consideration.
- **VoxCPM2 TTS:** Self-hosted voice cloning is interesting but not a priority while ElevenLabs is working well. Revisit if ElevenLabs costs spike or quality issues appear.
- **MCP vs Skills debate:** Relevant for Alex's product vision. Not urgent for our current setup (Mac mini, local CLIs work fine). Revisit when designing HeyDebra API layer.
- **GitButler:** Early stage, no action needed yet. Watch for v1.0.
- **Proposal Backlog Triage:** 13+ proposals pending from previous cycles. Need Alex to do a 30-minute proposal review session. This is the meta-problem.

---

## Carryover from Cycle #8 (UNACTIONED — 2 cycles deferred)
These were marked "self-apply ready" in Cycle #8 but were not applied:
1. **Promote failure patterns to MEMORY/SOUL** → Partially captured in Proposal #3 above (process-narration). The `debra-solo-outbound` pattern also needs AGENTS.md promotion.
2. **GSD agent: read active-context.md before reporting** → Still not done. The GSD report should always cross-reference active-context.md so overdue items match current reality.

**Request to Alex:** Please explicitly approve or reject these two carryover items so they can be closed.

---

## Meta
- Research scan: ~20 findings evaluated, 10 kept (web_search unavailable — degraded scan)
- Self-reflection: 7 issues identified, 3 systemic patterns named
- Deep dives: 4 topics researched (Hermes Agent, Claudian, Karpathy principles, Project Glasswing)
- Proposals: 8 changes suggested (3 high, 3 medium, 2 low)
- Deferred: 5 items
- Estimated cost: ~$0.80-1.20 (Sonnet 4.6, ~80K tokens across 4 phases)
- Cycle duration: ~25 minutes
- Web search: ❌ UNAVAILABLE (Gemini credits depleted) — degraded Phase 1 scan
- Memory search: ❌ UNAVAILABLE (Gemini 403 error) — Phase 2 used direct file reads

**Highest priority action for Alex:** 
1. Top up Gemini AI Studio credits (both web_search and memory_search are down)
2. Review Claudian install proposal (Proposal #1 — this is the one to do first)
3. Schedule 30-min proposal review session to clear the growing backlog
