# Dream Cycle Proposals — 2026-03-28

## Summary
First dream cycle run. Found 10 relevant developments (agent sandboxing, coding workflow frameworks, memory coordination research, GitHub privacy changes). Self-reflection surfaced a pattern of outbound comms mistakes, infrastructure debt accumulation, and missing accountability loops. Deep dives on jai (not macOS-ready), Superpowers (immediately useful coding workflow), and MemMA (memory probe-repair concept worth adopting). Proposing 7 changes across skills, security, and workflow.

## Proposed Changes

### 1. GitHub Private Repo Opt-Out — URGENT by Apr 24
**Category:** security
**Priority:** HIGH
**Effort:** trivial (5 min)
**Files affected:** None (GitHub settings)

**What:** Opt out of GitHub's new ToS that allows training on private repositories. Deadline is April 24, 2026.
**Why:** Alex has private repos containing OpenClaw/HeyDebra/HoldPlease source code, API patterns, and potentially sensitive business logic. Found via HN scan tonight (710 upvotes, #3 story).
**Action:** Navigate to GitHub.com → Settings → Copilot → disable "Allow GitHub to use my code snippets for product improvements" (or equivalent new setting). Verify for all private repos.

### 2. Outbound Message Confirmation Gate
**Category:** workflow
**Priority:** HIGH
**Effort:** trivial
**Files affected:** `AGENTS.md` (Red Lines section)

**What:** Add an explicit pre-send checklist to AGENTS.md for any outbound message to anyone other than Alex:
```
Before sending to non-Alex recipients, confirm:
1. Channel (group vs direct)
2. Timing (is now the right moment?)
3. Content (would Alex approve this exact message?)
4. If ANY doubt → ask Alex first
```
**Why:** Three incidents in 6 days (Jay text, Sallijo tech dump, Merle routing). The pattern isn't being broken by informal lessons.

### 3. Add Memory Probe Phase to Dream Cycle
**Category:** skill
**Priority:** MEDIUM
**Effort:** moderate
**Files affected:** `skills/dream-cycle/SKILL.md`

**What:** Add a Phase 2.5 "Memory Verification" step that:
- Generates 5-10 factual QA pairs from the last 3 days of daily notes
- Queries memory_search for each answer
- Flags discrepancies, contradictions, or missing information
- Reports issues in the reflection file
**Why:** Inspired by MemMA paper. We currently never verify our memory is accurate. Stale info (like outdated phone numbers, old project statuses, wrong people connections) could cause real problems.
**Diff preview:** Addition of ~30 lines to SKILL.md between Phase 2 and Phase 3.

### 4. Upgrade Coding-Agent Skill with Two-Stage Review
**Category:** skill
**Priority:** MEDIUM
**Effort:** moderate
**Files affected:** `skills/coding-agent/SKILL.md`

**What:** Update coding-agent skill to include:
- Mandatory spec validation before coding begins (for tasks > 30 min)
- Fresh agent per task (no session reuse for independent subtasks)
- Two-stage post-completion review: (a) does it match the spec? (b) code quality
- CWD-scoping: always set explicit `cwd` to project directory, never home
**Why:** Superpowers framework demonstrates this pattern produces dramatically better autonomous coding. Our current "spawn and hope" approach has no quality gate.

### 5. Schedule GSD + Capture Agents
**Category:** config (cron)
**Priority:** MEDIUM
**Effort:** trivial
**Files affected:** Cron jobs (gateway config)

**What:** Schedule the already-built GSD agent and capture agent:
- Capture agent: 3x daily (8am, 1pm, 8pm ET) — scans email, iMessage, calendar for action items
- GSD agent: 2x daily (9am, 5pm ET) — reviews inbox, surfaces overdue items, generates accountability report
**Why:** Both agents are designed and have SKILL.md files but were never scheduled. This is the missing accountability loop identified in self-reflection. Pending items are accumulating with no enforcement.

### 6. Fix Search API Quota
**Category:** infrastructure
**Priority:** MEDIUM
**Effort:** trivial-moderate
**Files affected:** Gateway config (search provider)

**What:** Either upgrade Gemini API to paid tier or configure a backup search provider (Brave Search API). The free tier (20 requests/day) is insufficient for dream cycle + daily usage.
**Why:** Hit 429 rate limits on 4/5 searches tonight. Dream cycle Phase 1 was severely hampered. This will happen every night.
**Options:**
- Gemini paid: ~$0.30 per 1K searches (very cheap)
- Brave Search API: 2K free searches/month, paid tiers available
- Both: primary + fallback

### 7. 1Password CLI Troubleshooting Session
**Category:** infrastructure
**Priority:** MEDIUM
**Effort:** moderate (30-60 min)
**Files affected:** `TOOLS.md` (update with working auth pattern)

**What:** Dedicated session to fix 1Password CLI timeout issue. Test desktop app integration, biometric unlock, service account tokens as alternative.
**Why:** Blocked since at least Mar 28. Every sudo command is harder without it. Infrastructure debt that compounds daily.

## Deferred / Watching

| Item | Why Deferred | Check Back |
|------|-------------|------------|
| jai sandbox for macOS | Linux-only, not usable on our Mac mini | When/if jai adds macOS support or we deploy to Linux |
| Full Superpowers port to OpenClaw skills | Overkill for current task sizes | When we start building real product code (Mirror, Pools) |
| MemMA full multi-agent memory | Research-grade, too complex for current needs | After memory probe phase proves valuable |
| Chandra OCR integration | No immediate document scanning need | When SecondBrain adds physical document pipeline |
| Dexter financial agent patterns | Need Monarch/YNAB set up first | After financial tools are integrated |
| Claude Code web scheduled tasks | OpenClaw cron is more capable | Monitor for Claude-native features we should leverage |

## Meta
- Research scan: ~40 sources checked, 10 findings kept
- Self-reflection: 6 issues identified, 3 patterns surfaced
- Deep dives: 3 topics researched (jai, Superpowers, MemMA)
- Proposals: 7 changes suggested (2 high, 5 medium priority)
- Search API rate limited (4/5 queries failed) — addressed in Proposal #6
- Cycle duration: ~25 min
- Model: anthropic/claude-opus-4-6 (all phases, isolated session)
