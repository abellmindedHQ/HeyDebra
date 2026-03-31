# Dream Cycle Proposals — 2026-03-30

## Summary
Third dream cycle. Research quality limited by Gemini quota (4/7 queries rate-limited — same issue three cycles running). Deep dived Anthropic's long-running agent patterns, memory frameworks, and underused Opus 4.6 features. Self-reflection surfaced the same top pattern: outbound message misrouting (3 incidents in 8 days). Highest-impact proposals target quality gates and infrastructure debt that keeps getting deferred.

## Proposed Changes

### 1. Pre-Send Recipient Verification Gate
**Category:** workflow
**Priority:** HIGH
**Effort:** trivial
**Files affected:** AGENTS.md

**What:** Add a mandatory self-check before ANY outbound message: verify chat GUID matches intended recipient by name. Never send to a GUID from memory — always look it up.
**Why:** Three wrong-recipient incidents in 8 days (Jay text, Omar Shaheen leak, Angie voice note to wrong chat). This is the #1 trust risk.
**Diff preview:**
```
Add to AGENTS.md under "Red Lines":

## Pre-Send Verification (MANDATORY)
Before every outbound message via BlueBubbles or any channel:
1. Confirm recipient name matches the intended target
2. Look up chat GUID from TOOLS.md — never rely on memory
3. If sending to a group chat, verify the GUID contains the expected participants
4. For voice notes: double-check the chat before and after recording
```

### 2. GSD Agent Oracle Validation
**Category:** skill
**Priority:** HIGH
**Effort:** moderate
**Files affected:** skills/gsd-agent/SKILL.md

**What:** Before generating the GSD report, GSD agent must read active-context.md AND query Things 3 CLI for current completion status. Cross-reference pending items against both sources. Flag any item that active-context marks as resolved.
**Why:** GSD report incorrectly flagged resolved items (Boston hotel, ORNL Isaac). Stale data reduces trust in automated reports. Anthropic's "test oracle" pattern directly applies here.
**Diff preview:**
```
Add to SKILL.md Phase 1 (Data Collection):

### Oracle Validation Step
Before composing the report:
1. Read active-context.md for latest status updates
2. Run `things today --json` and `things completed --since yesterday --json`
3. Cross-reference: if an item appears in both pending AND completed/resolved, mark it resolved
4. If active-context.md contradicts a memory file, active-context.md wins (it's more recent)
```

### 3. Auto-Summarize Old Daily Memory Files
**Category:** workflow
**Priority:** medium
**Effort:** moderate
**Files affected:** New cron job + AGENTS.md

**What:** Create a weekly cron (Sunday midnight) that reads daily memory files older than 5 days, generates a condensed summary (max 30 lines per day), and appends key facts to MEMORY.md. Original files preserved but flagged as summarized.
**Why:** Daily memory files grow to 300+ lines (March 28 = ~350 lines). Loading 3 days of context burns significant tokens. Progressive summarization (inspired by Zep) would keep recent files detailed and old files compact.
**Diff preview:**
```json
{
  "name": "memory-summarizer",
  "schedule": { "kind": "cron", "expr": "0 0 * * 0", "tz": "America/New_York" },
  "payload": {
    "kind": "agentTurn",
    "message": "Read all memory/YYYY-MM-DD.md files older than 5 days that haven't been summarized. For each, create a 20-30 line summary preserving: key decisions, lessons learned, people interactions, task completions, and open items. Write summary to memory/summaries/YYYY-MM-DD-summary.md. Add a '## Summarized' header to original. Update MEMORY.md with any new long-term insights.",
    "model": "anthropic/claude-sonnet-4-6"
  },
  "sessionTarget": "isolated"
}
```

### 4. Fix Gemini Search Quota (THIRD TIME PROPOSING)
**Category:** infrastructure
**Priority:** HIGH
**Effort:** trivial
**Files affected:** Gateway config (search provider)

**What:** Either upgrade Gemini API to paid tier ($0.15/1K queries) or add a backup search provider (Brave Search API has 2K free queries/month).
**Why:** Three consecutive dream cycles degraded by 429 rate limits. Daytime usage exhausts the 20/day free quota before nightly crons run. This is the most repeatedly-identified infra issue.
**Diff preview:**
```
Option A: Upgrade Gemini to paid tier
  - Add billing to Google AI Studio project
  - Cost: ~$5-10/month at our usage level

Option B: Add Brave Search as backup
  - Sign up at api.search.brave.com (free tier: 2K queries/month)
  - Configure as fallback in OpenClaw gateway
```

### 5. Start Neo4j on Boot
**Category:** infrastructure
**Priority:** medium
**Effort:** trivial
**Files affected:** LaunchAgent plist

**What:** Create a LaunchAgent (com.debra.neo4j.plist) that starts Neo4j on boot, similar to the OpenClaw browser LaunchAgent we created on March 30.
**Why:** Neo4j has been down for 3+ days. Night Swimming contact triage, social data processing, and weaver entity linking all depend on it. Every cycle it's down, the knowledge graph falls further behind.
**Diff preview:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.debra.neo4j</string>
    <key>ProgramArguments</key>
    <array>
        <string>/opt/homebrew/bin/brew</string>
        <string>services</string>
        <string>start</string>
        <string>neo4j</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>
```

### 6. Proposal Review Batching System
**Category:** workflow
**Priority:** medium
**Effort:** trivial
**Files affected:** active-context.md, dream cycle delivery format

**What:** Instead of dumping all proposals in a single file, categorize them:
- **Auto-apply:** Trivial fixes I can safely do myself (typo fixes, adding notes to TOOLS.md, starting Neo4j)
- **Quick approve:** Low-risk changes that need a thumbs-up (new crons, AGENTS.md updates)  
- **Discuss:** High-impact changes that need Alex's input (config changes, new integrations)
Morning summary should say "3 auto-applied, 2 need thumbs-up, 1 needs discussion" instead of "6 proposals ready."
**Why:** 15 proposals pending across 3 cycles. Alex hasn't reviewed any. The current format requires him to read everything. Batching by effort level reduces review burden.

### 7. Capture Agent BlueBubbles Auth Fix
**Category:** skill
**Priority:** medium
**Effort:** trivial
**Files affected:** skills/capture-agent/SKILL.md or config

**What:** Fix the BlueBubbles authentication issue that prevented iMessage scanning in today's capture agent run. The server password needs to be configured in the capture agent's BB API calls.
**Why:** Capture agent scanned email and calendar but skipped iMessage (the richest source of action items). This means commitments made via text aren't being tracked.

## Deferred / Watching

- **Mem0 / Letta adoption**: Our manual memory system works well. Monitor for when OpenClaw adds native memory framework support.
- **Microsoft Agent Framework + Claude SDK**: Multi-agent orchestration patterns are interesting but we already have sub-agents via OpenClaw. Monitor.
- **Claude Mythos model**: Leaked vulnerability-focused model from Anthropic. Security implications worth watching.
- **Financial app browser automation (YNAB/Monarch)**: Queue for after LinkedIn cleanup completes (~2 weeks).
- **Neo4j → memory_search bridge**: Queue for after Neo4j is stable and running consistently.

## Meta
- Research scan: 15 evaluated, 7 kept
- Self-reflection: 6 issues identified, 4 patterns recognized
- Deep dives: 3 topics researched (long-running agents, memory frameworks, Opus 4.6 features)
- Proposals: 7 changes suggested (2 high, 5 medium)
- Total pending proposals: 22 (15 from cycles #1-2 + 7 new)
- Gemini quota status: 3/7 searches succeeded (same problem, third cycle)
- Cycle duration: ~20 min
