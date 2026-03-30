# Dream Cycle Proposals — 2026-03-29

## Summary
Second dream cycle. Competitive landscape is heating up — Claude Code Channels directly targets OpenClaw's messaging paradigm, NousResearch hermes-agent offers a full self-improving agent with migration tooling, and the "personal AI agent" market is clearly growing. Found a critical Claude Code bug (silent git reset every 10 min) that could affect our coding workflow. Microsoft VibeVoice offers free local ASR that could replace Whisper. The 1M token context at standard pricing unlocks better context loading. Self-reflection shows same patterns as last cycle: speed > quality, infrastructure debt compounding, proposal review bottleneck.

## Proposed Changes

### 1. Claude Code git reset Warning — URGENT
**Category:** skill
**Priority:** HIGH
**Effort:** trivial (5 min)
**Files affected:** `skills/coding-agent/SKILL.md`

**What:** Add warning about Claude Code v2.1.87 silently running `git reset --hard origin/main` every 10 minutes. Instruct agents to commit early/often, and consider using git worktrees for isolation.
**Why:** This could destroy uncommitted work in any project repo where we spawn Claude Code. HN #9 story, 194 points, confirmed reproduction. GitHub issue #40710.
**Diff preview:**
```
Add to SKILL.md "Safety" section:
⚠️ KNOWN BUG (Claude Code v2.1.87): CC silently runs `git reset --hard origin/main`
every 10 minutes, destroying uncommitted changes to tracked files. Untracked files
and git worktrees are immune.
ALWAYS: commit frequently, verify CC version, consider git worktrees for isolation.
Monitor: https://github.com/anthropics/claude-code/issues/40710
```

### 2. Expand Context Window Usage
**Category:** config/workflow
**Priority:** HIGH
**Effort:** trivial
**Files affected:** `AGENTS.md` (Session Startup section)

**What:** With 1M token context now at standard pricing, expand session startup to load:
- Last 7 days of daily notes (up from 2)
- Full MEMORY.md in all sessions (not just main)
- active-context.md (already loaded)
**Why:** 1M context at no surcharge means we can preload much more context, reducing memory_search dependency and improving cross-session continuity. Cost increase is minimal for the quality improvement.
**Diff preview:**
```
Update AGENTS.md Session Startup:
4. Read `memory/YYYY-MM-DD.md` (today + last 7 days) for recent context
5. Read `MEMORY.md` in all sessions (security review: redact sensitive fields for shared contexts)
```

### 3. Install last30days-skill for Dream Cycle Research
**Category:** skill/infrastructure
**Priority:** MEDIUM
**Effort:** trivial (clawhub install)
**Files affected:** Dream cycle SKILL.md Phase 1

**What:** Install `last30days-skill` from ClawHub to enhance Phase 1 research scanning. It searches Reddit, X, YouTube, HN, Polymarket, Bluesky, and web — exactly what we need for the research scan. The comparative mode ("X vs Y") is useful for product analysis.
**Why:** Our current Phase 1 manually fetches HN and GitHub, then gets rate-limited on web_search. last30days-skill handles multi-source research natively with citation tracking. 1,308 stars/day on GitHub — community validated.
**Action:** `clawhub install last30days-official`

### 4. Add Delivery Quality Gate
**Category:** workflow
**Priority:** MEDIUM
**Effort:** trivial
**Files affected:** `AGENTS.md` (External vs Internal section)

**What:** Before ANY external delivery (iMessage, email, file send), run a 3-point check:
1. Does the content exist and is it correct? (verify file, check facts)
2. Is the recipient right? (channel vs DM, correct person)
3. Would Alex approve this exact message right now?
**Why:** Pattern from reflection: speed > quality keeps causing issues (Batman video QC, GSD report inaccuracy, Merle text routing). This is Proposal #2 from last cycle refined with the additional "content verification" step.
**Diff preview:**
```
Add to AGENTS.md "External vs Internal":
## Delivery Quality Gate (before ANY external send)
✅ Content verified: file exists, facts checked against active-context.md
✅ Recipient confirmed: right channel (group vs DM), right person
✅ Alex-approved: would he be okay with this exact message?
If ANY check fails → pause and verify before sending.
```

### 5. Benchmark VibeVoice-ASR Against Whisper
**Category:** infrastructure
**Priority:** MEDIUM
**Effort:** moderate (2-3 hours)
**Files affected:** None initially (benchmark only)

**What:** Install VibeVoice-ASR via HuggingFace Transformers, test on our HoldPlease call recordings (Eris + Charlotte calls from 3/29), compare accuracy and diarization quality against Whisper API output.
**Why:** VibeVoice-ASR is free, local, and offers speaker diarization (who said what) which Whisper lacks. If quality is comparable, we save API costs and gain better transcripts for HoldPlease.
**Prerequisite:** Need to check if Mac mini M4 can run the model efficiently.

### 6. Fix Search API Quota (Carry-Forward from Last Cycle)
**Category:** infrastructure
**Priority:** MEDIUM
**Effort:** trivial
**Files affected:** Gateway config

**What:** Either upgrade Gemini API to paid tier (~$0.30/1K searches) or configure Brave Search API as backup. Free tier (20/day) is insufficient — both dream cycles hit 429 limits.
**Why:** This was Proposal #6 last cycle. Still not implemented. Two consecutive dream cycles degraded by rate limits.
**Options:** Gemini paid ($0.30/1K) or Brave Search API (2K free/month) or both.

### 7. Review and Close Last Cycle's Proposals
**Category:** workflow
**Priority:** MEDIUM
**Effort:** trivial (10 min review)
**Files affected:** `memory/dream-cycle/2026-03-28-proposals.md`

**What:** Explicitly review last cycle's 7 proposals. Accept, reject, or defer each one. Close the loop.
**Why:** Proposals accumulate without review. 7 from last cycle + 8 from this cycle = 15 pending changes. The backlog itself becomes a problem. Recommend Alex spend 10 min triaging these in the morning.

### 8. Schedule GSD + Capture Agents (Carry-Forward)
**Category:** config (cron)
**Priority:** MEDIUM
**Effort:** trivial
**Files affected:** Cron jobs

**What:** Schedule the already-built GSD agent (2x daily: 9am, 5pm) and capture agent (3x daily: 8am, 1pm, 8pm). Both have SKILL.md files ready.
**Why:** Carry-forward from last cycle Proposal #5. The accountability loop is still missing. Pending items accumulate with no enforcement mechanism.

## Deferred / Watching

| Item | Why Deferred | Check Back |
|------|-------------|------------|
| hermes-agent migration | OC is better for our use case. Cherry-pick ideas instead | If OC stagnates or hermes adds iMessage |
| Honcho user modeling for Mirror | Good concept but Mirror isn't being built yet | When Mirror development starts |
| Auto-skill creation (hermes concept) | Nice idea but not urgent | After core workflows stabilize |
| VibeVoice TTS for AVERY | No voice cloning, ElevenLabs stays for custom voices | If VibeVoice adds cloning |
| Claude Code Channels impact | Not a threat to our use case (coding-only, no life management) | Monitor adoption quarterly |
| Git worktree adoption | Not needed until parallel multi-agent builds | When HoldPlease v2 or Mirror enters heavy dev |
| Claude Code version pin | Wait for Anthropic's fix to #40710 first | Check issue weekly |

## Meta
- Research scan: ~15 sources checked, 10 findings kept (rate-limited on 3/5 searches)
- Self-reflection: 5 issues identified, 4 patterns surfaced (same patterns as last cycle — concerning)
- Deep dives: 4 topics researched (CC git bug, hermes-agent, VibeVoice, 1M context)
- Proposals: 8 changes suggested (2 high, 6 medium priority), 3 carry-forward from last cycle
- Search API rate limited again (Proposal #6 is literally proving itself)
- Cycle duration: ~20 min
- Model: anthropic/claude-opus-4-6 (all phases, isolated session)
