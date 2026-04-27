# Dream Cycle #20 Proposals — 2026-04-26

## Summary
DC#20 is a milestone cycle — our 20th nightly run. This week's dominant theme is **execution over ideation**: Opus 4.7 is now GA and addresses our top correction pattern, the OC upgrade has been proposed 3 cycles in a row, and 30+ proposals sit unreviewed. The research landscape confirms our memory architecture is sound but could benefit from provenance tracking and graph retrieval. The biggest win available right now is simply upgrading to Opus 4.7 and OC 2026.4.24 — both low-risk, high-value changes that directly address known pain points.

## Proposed Changes

### 1. Upgrade to Opus 4.7 (Sandboxed Test → Full Rollout)
**Category:** infrastructure
**Priority:** high
**Effort:** moderate
**Files affected:** gateway config, TOOLS.md, MEMORY.md

**What:** Run representative workload on Opus 4.7 in isolated session. If quality/cost are acceptable, switch primary model from `anthropic/claude-opus-4-6` to `anthropic/claude-opus-4-7`.
**Why:** Native self-verification addresses our #1 correction pattern (report-without-verifying, 6 occurrences). xhigh reasoning improves multi-step task execution. 13% coding benchmark improvement helps Paperclip. Same pricing. GA since Apr 16 — no longer preview risk. Post-mortem confirms early "vulnerability" reports were artifacts of harness bugs.
**Risk:** Unknown behavioral differences. Mitigate with sandboxed test.
**When:** Monday (test), Tuesday (rollout if approved).

### 2. Upgrade OpenClaw to 2026.4.24
**Category:** infrastructure
**Priority:** high
**Effort:** moderate
**Files affected:** system (npm global), gateway config backup

**What:** Upgrade from 2026.4.19-beta.2 to 2026.4.24.
**Why:** 3rd consecutive cycle proposing this. Browser automation improvements, TTS upgrade, heartbeat timer fix. We're now 7+ days behind stable. The longer we wait, the larger the delta.
**Risk:** Breaking plugin SDK change (registerEmbeddedExtensionFactory removed). macOS mixed-version reports. Mitigate: backup config, off-hours, verify skills.
**When:** Monday or Tuesday, after Opus 4.7 test.

### 3. Send Dream Cycle Summary Directly (Fix Delivery)
**Category:** workflow
**Priority:** high
**Effort:** trivial
**Files affected:** skills/dream-cycle/SKILL.md

**What:** Have the dream cycle send the iMessage summary immediately upon completion (~midnight) instead of staging for morning delivery. Alex's phone is in DND overnight — he reads it when he wakes up.
**Why:** DC#17, DC#18, and DC#19 summaries were all staged but delivery was unreliable. 3 consecutive failures. The staging mechanism is broken. Direct send is simpler and more reliable.
**Diff preview:**
```
# In SKILL.md Delivery section:
- "Deliver summary via iMessage to Alex in the morning (or announce in session)"
+ "Send summary via iMessage to Alex immediately upon completion. DND handles timing."
```

### 4. Add TourSpec to MEMORY.md Active Projects
**Category:** memory
**Priority:** medium
**Effort:** trivial
**Files affected:** MEMORY.md

**What:** Add TourSpec project entry with details from Hannah interview (Apr 25).
**Diff preview:**
```
- **TourSpec** (NEW Apr 25 — Hannah's touring logistics MVP. Day sheets, advancing tracker, 
  venue DB, financial dashboard, asset portal. Target: Hannah's May 4 tour. GitHub repo TBD.
  Key pain points from Hannah interview: advancing grind, everything in inbox/head, bad routing, 
  payment tracking, merch management, content promotion burden.)
```

### 5. Add Memory Provenance Tags
**Category:** workflow
**Priority:** medium
**Effort:** trivial
**Files affected:** AGENTS.md (add guideline), new memory entries going forward

**What:** Tag new memory entries with source and date: `[source: alex|web|inference|cron] [date: YYYY-MM-DD]`. Enables staleness detection and trust assessment.
**Why:** Memory verification (Phase 2.5) keeps flagging stale entries. With provenance tags, we can automatically identify entries that haven't been verified in 30+ days or that came from inference (lower trust) vs. Alex's words (higher trust). Mem0 benchmark report and HN discussion both emphasize provenance as critical for multi-agent memory.
**Diff preview:**
```
# Add to AGENTS.md Memory section:
### Provenance Tags
When writing to MEMORY.md or daily logs, tag entries with source:
- `[alex]` — Alex said it directly
- `[web]` — Found via web search
- `[inferred]` — Debra's inference or assumption
- `[cron]` — Captured by automated scan
- `[agent]` — From Paperclip or other agent output
```

### 6. Billing Sweep — Structured Escalation
**Category:** workflow
**Priority:** medium
**Effort:** trivial
**Files affected:** inbox/inbox.md or Things 3

**What:** Instead of flagging "8+ payment failures" daily in GSD reports, compose a single structured billing sweep message with specific action per payment: cancel, update card, dispute, or pay. Send to Alex as one batch.
**Why:** 20+ days of flagging the same items hasn't driven action. The problem is presentation, not awareness. A structured list with specific asks ("cancel Runway $157, update Notion card, dispute ORNL FCU $20") is actionable; "8 payment failures" is not.
**When:** Include in Monday morning GSD or send standalone.

### 7. Paperclip Diagnostic Checklist
**Category:** workflow
**Priority:** low
**Effort:** trivial
**Files affected:** TOOLS.md (new section)

**What:** Add a standard Paperclip diagnostic checklist to TOOLS.md so future investigations don't start from scratch.
**Diff preview:**
```
### Paperclip Diagnostic Checklist
When agents are stuck:
1. Check server health: curl http://127.0.0.1:3100/health
2. Check CLI context: npx paperclipai context show
3. Check for zombie processes: ps aux | grep -E 'claude|curl' | grep -v grep
4. Check agent heartbeats: npx paperclipai agents list
5. Check run queue: npx paperclipai runs list --status queued
6. Kill zombies if found: kill -9 <pids>
7. Verify git remote: cd <workspace> && git remote -v
8. Check adapter health: verify Claude Code version ≥ v2.1.116
```

## Deferred / Watching

| Item | Why Deferred | Revisit |
|------|-------------|---------|
| MEMORY.md split into focused files | Works fine at current size (~200 lines). Split when it hits 300+. | June |
| Paperclip agent persistent memory | Agents need to stabilize first. Architecture validated by MindStudio guide. | Post-Amsterdam |
| Neo4j revival + graph retrieval | Infrastructure debt. Not blocking anything yet. | May |
| Claude Design for Paperclip visual work | Interesting but Sable's adapter needs fixing first | When Paperclip is stable |
| DeepSeek V4 Flash for non-critical tasks | Cost savings potential. Evaluate after OC upgrade. | Post-upgrade |
| Self-benchmark (LOCOMO-style memory eval) | Overkill for single-user assistant at current scale | Quarterly review |
| MemMachine integration | Requires Neo4j running + evaluation. Cool tech, not urgent. | June |
| Prompt injection protection for Linear tickets | Security concern from HN discussion. Low probability, high impact. | Security review sprint |

## Meta
- Research scan: 10 findings, 10 kept (4 high, 4 medium, 2 low-medium)
- Self-reflection: 5 issues identified (delivery lag, proposal backlog, stale payments, Amsterdam PTO, dropped audio thread)
- Memory verification: 10 probes, 9 passed, 1 flagged (Opus 4.7 assessment stale — 3rd cycle)
- Deep dives: 4 topics researched (Opus 4.7, persistent memory architecture, OC 2026.4.24, agent memory benchmarks)
- Proposals: 7 changes suggested (3 high, 3 medium, 1 low)
- Corrections: 0 new (6+ day clean streak)
- Estimated cost: ~$4.00 (Opus 4.6 for full research cycle)
- Cycle duration: ~22 min
- **Cycle milestone: DC#20. 20 consecutive nightly cycles since launch.**
