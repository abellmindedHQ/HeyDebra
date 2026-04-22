# Dream Cycle Proposals — 2026-04-21

## Summary
Tonight's cycle found 10 items (4 high, 5 medium, 1 low). OpenClaw 2026.4.20 is the most actionable — per-group BB systemPrompt is a game-changer for chat behavior. OpenAI Chronicle validates our memory architecture. Claude Code Pro removal is an ecosystem signal to monitor. Reflection found message-fragmentation at 6+ occurrences (structural problem), 4/7 memory probes stale/contradictory/missing. 4 deep dives completed, 8 proposals below.

## Proposed Changes

### 1. Upgrade OpenClaw to 2026.4.20 (SCHEDULE: Thu/Fri)
**Category:** infrastructure
**Priority:** high
**Effort:** moderate
**Files affected:** gateway install, openclaw.json

**What:** Upgrade from 2026.4.19-beta.2 to 2026.4.20. Key features: BB per-group systemPrompt, cron state split, session pruning, stronger agent prompts.
**Why:** Per-group systemPrompt alone justifies it. Session pruning prevents OOM from our aggressive cron schedule. Stronger agent prompts may reduce report-without-verifying.
**Timing:** NOT during surgery week (Wed). Schedule for Thu evening or Fri.

### 2. Configure BB Per-Group SystemPrompts (AFTER upgrade)
**Category:** config
**Priority:** high
**Effort:** moderate
**Files affected:** openclaw.json

**What:** Define custom systemPrompts for each known group chat to tailor behavior.
**Why:** Different chats need different energy. KBUDDS is bro talk, Family is gentle, Chelsea is clinical. One-size-fits-all has caused tone mismatches.

**Diff preview:**
```json
// openclaw.json plugins.bluebubbles.groups
"any;+;26496e31a52b4d7091da7b17a5a1380d": { "systemPrompt": "KBUDDS chat..." },
"any;+;63d1dbe0006d46abbc3aa07a4fb38c8b": { "systemPrompt": "Family chat..." },
"any;+;a96e1f6eaaba404abd15b7b1a1a1cdea": { "systemPrompt": "Chelsea chat..." },
"*": { "systemPrompt": "Default casual..." }
```

### 3. Fix Stale Memory (CARRY-FORWARD x3)
**Category:** memory
**Priority:** high
**Effort:** trivial
**Files affected:** MEMORY.md, TOOLS.md, active-context.md

**What:** Apply 5 memory fixes identified in Phase 2.5:
1. Update TOOLS.md BB port from 1234 to 1235
2. Update MEMORY.md BB Attachment Bug section to "RESOLVED in 2026.4.19-beta.2"
3. Add Paperclip team roster (10 agents) to MEMORY.md
4. Update active-context.md brand kit URL to abellminded.com/identity
5. Add Avie surgery details to MEMORY.md Pending Action Items

**Why:** 3rd cycle carrying this forward. Stale data causes wrong assumptions and wastes time. The BB port issue directly caused a GSD report delivery failure today.

**Diff preview:**
```markdown
# TOOLS.md
- Server: localhost:1234 (same machine)
+ Server: localhost:1235 (same machine)

# MEMORY.md
- ## BB Attachment Bug (Apr 8-9)
- [entire section about intermittent detection...]
+ ## BB Attachment Bug (RESOLVED)
+ - Fixed in OpenClaw 2026.4.19-beta.2. WhatsApp images confirmed working Apr 19.
+ - iMessage attachments still need upstream BB fix for SSRF guard.

+ ## Paperclip Team (Abellminded)
+ 10 agents: Steve McGoober (Coordinator), Sable Voss (CDO), Ratchet Varma (CTO),
+ Kit Ballard (CWO), Maren Lys (CPO/Philosophy), Wren Kowalski (CQO),
+ Cass Meridian (CRO), Pax Holloway (CPO/Product), Devi Sato (CHRO),
+ Ren Otieno (CIO)
```

### 4. Add Verification Checklist to AGENTS.md
**Category:** workflow
**Priority:** medium
**Effort:** trivial
**Files affected:** AGENTS.md

**What:** Add a "Pre-Report Verification" section under Red Lines:
```markdown
### Pre-Report Verification (MANDATORY for external-facing outputs)
Before telling Alex (or anyone) something is "done", "live", "working", or "shipped":
1. Open the URL / file / output yourself (browser or screenshot)
2. Visually confirm the content renders correctly
3. Check for: broken links, placeholder text, curl artifacts, 404s
4. If you can't visually verify, say "deployed but not yet visually confirmed"
```

**Why:** report-without-verifying is at 3 occurrences. It's in MEMORY.md but not as a mandatory checklist. Making it a formal pre-report step (like pre-send verification for messages) gives it structural weight.

### 5. Add "vercel-url" Rule to AGENTS.md
**Category:** workflow
**Priority:** medium
**Effort:** trivial
**Files affected:** AGENTS.md

**What:** Add rule: "Never share internal vercel.app URLs externally. Always use the proper production domain (abellminded.com). Internal staging URLs (*.vercel.app) are for development only."
**Why:** 2 occurrences of leaking random vercel.app URLs to Alex. On track for 3x promotion threshold.

### 6. Add "third-person-references" Rule to AGENTS.md
**Category:** workflow
**Priority:** medium
**Effort:** trivial
**Files affected:** AGENTS.md

**What:** Add rule: "When posting feedback on behalf of Alex (Paperclip tickets, external tools), write as direct instruction. Not 'Alex wants X' or 'Alex reviewed Y.' Just state the feedback. The team knows who the boss is."
**Why:** 2 occurrences (Apr 20-21). On watch list — one more and it gets promoted automatically.

### 7. Monitor Anthropic Pricing Changes
**Category:** infrastructure
**Priority:** low
**Effort:** trivial
**Files affected:** dream-cycle scan sources

**What:** Add "Anthropic pricing/subscription changes" to Phase 1 scan sources.
**Why:** Claude Code Pro removal is a canary for broader pricing pressure. We're API-dependent and need early warning of pricing shifts.

### 8. Dream Cycle Proposal Delivery Improvement
**Category:** workflow
**Priority:** medium
**Effort:** moderate
**Files affected:** skills/dream-cycle/SKILL.md, morning iMessage format

**What:** Change morning iMessage to include the TOP 3 proposals with one-line descriptions and a "reply 1/2/3 to approve" mechanism. Instead of "proposals ready for review when you want em" (which never gets reviewed), give Alex actionable options in the message itself.
**Why:** This is the 3rd+ cycle noting that proposals go unread. 13+ proposals accumulated across the last 3 cycles. The delivery mechanism is broken. Alex responds to short, actionable asks — not "go read a file."

**Diff preview (morning message):**
```
🌙 Dream cycle ran

Top proposals:
1. Upgrade to OC 2026.4.20 (BB per-group prompts, session pruning)
2. Fix stale memory (BB port, attachment bug status, team roster)
3. Add verification checklist to AGENTS.md

Reply 1/2/3 to approve, or "all" for everything.
```

## Deferred / Watching
- **OpenAI Chronicle:** Validates our architecture. No action unless they open-source components.
- **Google TurboQuant:** Lab breakthrough, not shipped. Watch for Gemini/Claude integration.
- **"Claudy Day" Claude session hijacking:** Monitor Anthropic response. No immediate action needed since OpenClaw provides isolation.
- **Meta employee keystroke capture:** Relevant to communitism narrative but no action item.
- **VisionClaw / passive capture:** Chronicle highlights our gap in passive context capture. VisionClaw remains stalled (needs Xcode build).

## Meta
- Research scan: 10 findings, 10 kept
- Self-reflection: 6 issues identified, 6 corrections analyzed
- Memory verification: 7 probes, 3 passed, 4 flagged
- Deep dives: 4 topics researched
- Proposals: 8 changes suggested (3 high, 4 medium, 1 low)
- Cycle duration: ~25m
