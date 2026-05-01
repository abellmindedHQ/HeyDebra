# Dream Cycle #25 Proposals — 2026-04-30

## Summary
25th consecutive nightly cycle. The Claude vs OpenClaw drama is the headline: Anthropic is actively restricting Claude Code interactions involving OpenClaw. We're safe on API billing but should monitor. Supply chain attacks continue to escalate (PyTorch Lightning today, npm last week). We're 10+ OC releases behind and should upgrade. On the self-improvement side: 11+ days without corrections, but the message-fragmentation pattern persists structurally, and the proposal delivery pipeline remains broken (25 cycles, zero reviews). Biggest operational risk: Alex's reorg comms plan is due May 1 with no draft.

## Proposed Changes

### 1. Upgrade OpenClaw to 2026.4.29
**Category:** infrastructure
**Priority:** high
**Effort:** moderate
**Files affected:** gateway config, package.json (global)

**What:** Upgrade from 2026.4.19-beta.2 to 2026.4.29 (10 releases). Includes WhatsApp fixes, people-aware wiki memory, active-run steering, security patches.
**Why:** 10 releases behind is a security and stability risk. WhatsApp cycling disconnects, BB channel improvements, and faster gateway boot all address current pain points. CVE patches accumulate.
**Diff preview:**
```bash
# Backup
cp ~/.openclaw/openclaw.json ~/.openclaw/openclaw.json.bak
# Upgrade
npm update -g openclaw
# Restart
openclaw gateway restart
# Verify
openclaw gateway status
```
**Risk:** Breaking changes across 10 releases. Need Alex's approval before executing.

### 2. Run npm + pip Security Audit
**Category:** infrastructure
**Priority:** high
**Effort:** trivial
**Files affected:** none (read-only audit)

**What:** Run `npm audit` and `pip audit` (or `pip-audit`) to check for known vulnerabilities in installed packages. Set up weekly cron.
**Why:** PyTorch Lightning supply chain attack (Apr 30) + npm campaigns (SAP, axios, Bitwarden) make this urgent. Our Mac mini has API keys, SSH keys, 1Password CLI access — a compromised package could exfiltrate everything.
**Diff preview:**
```bash
npm audit --global 2>&1 | head -50
pip install pip-audit && pip-audit 2>&1 | head -50
```

### 3. Fix Proposal Delivery: Embed in GSD Reports
**Category:** workflow
**Priority:** high
**Effort:** trivial
**Files affected:** skills/gsd-agent/SKILL.md

**What:** Instead of writing standalone proposal files that Alex never reads, embed the top 1-2 proposals as a "Quick Wins" section in the morning GSD report. Format: one-liner description + one-liner justification + effort estimate.
**Why:** 25 cycles of proposals, zero reviews. The delivery mechanism is broken. Alex reads GSD reports. If proposals ride the GSD, they might actually get seen.
**Diff preview:**
```markdown
# Add to GSD report template after "🎯 TOP 3 RIGHT NOW":

### 💡 Quick Wins (from last night's dream cycle)
- **[Title]** — [one-liner why] | Effort: [trivial/moderate]
- **[Title]** — [one-liner why] | Effort: [trivial/moderate]
```

### 4. Fix TOOLS.md BB Port Confusion
**Category:** memory
**Priority:** medium
**Effort:** trivial
**Files affected:** TOOLS.md

**What:** Update the BlueBubbles section header from "localhost:1235" to "localhost:1234". Add clarification that 1235 was Alex's disabled account.
**Why:** Flagged in DC #23 and DC #25 memory verification probes. The header says 1235 but actual server is 1234. This causes confusion in any session that reads TOOLS.md.
**Diff preview:**
```
- Server: localhost:1235 (same machine)
+ Server: localhost:1234 (same machine). Note: port 1235 was Alex's second BB account, now disabled.
```

### 5. Document Anthropic vs OpenClaw Risk in TOOLS.md
**Category:** memory
**Priority:** medium
**Effort:** trivial
**Files affected:** TOOLS.md

**What:** Add a note about the Claude Code/OpenClaw tension. Note: we use API keys (unaffected by subscription ban), but monitor for changes.
**Why:** HN frontpage story today (1001 pts). If Anthropic extends restrictions to API customers, our entire stack is at risk.
**Diff preview:**
```markdown
### ⚠️ Anthropic vs OpenClaw (Noted 2026-04-30)
- Anthropic cut Claude Pro/Max subscription support for OC on Apr 4, 2026
- Claude Code reportedly refuses/throttles requests with "OpenClaw" in commits
- We use API keys (pay-as-you-go), NOT subscriptions — currently unaffected
- Monitor Anthropic ToS for any API-level restrictions
- Ensure model fallbacks (Gemini, local) are available for coding tasks
```

### 6. Self-Fix Infrastructure Items
**Category:** infrastructure
**Priority:** medium
**Effort:** trivial
**Files affected:** various services

**What:** During next maintenance window, do the things I keep flagging but not doing:
- Restart Neo4j (`brew services start neo4j`) — down 33 days
- Restart BB (`brew services restart bluebubbles`) — send endpoint hanging
- Triage workspace inbox (100+ items, 24 days stale)
**Why:** AGENTS.md explicitly allows me to start/restart services and organize files without asking. I've been too deferential. These are all safe, reversible operations.

### 7. Set Up Local Model Fallback via Ollama
**Category:** infrastructure
**Priority:** low
**Effort:** moderate
**Files affected:** OC config, Ollama setup

**What:** Install IBM Granite 4.1 8B via Ollama as a local fallback model. Configure in OC as a secondary provider for when Gemini API goes down (our recurring SPOF issue).
**Why:** Granite 4.1 8B is Apache 2.0, runs on M2, supports tool calling and 131K context. Good enough for basic agent tasks when primary models are unavailable. Our Gemini SPOF has been flagged in 10+ dream cycles.
**Diff preview:**
```bash
ollama pull ibm/granite4.1:8b
# Then add to openclaw.json providers
```

## Deferred / Watching

- **Anthropic Managed Memory:** Cool architecture but our DIY system is more flexible and model-agnostic. No action.
- **Honker (SQLite queues):** Interesting for future batch pipelines. Not needed today.
- **Chrome Prompt API:** Mozilla opposing. Won't be a standard soon. Watch only.
- **Claude Agent SDK rename:** Signals Anthropic's broader agent ambitions. No action.
- **Alignment Whack-a-Mole research:** Academic interest only.

## Meta
- Research scan: 10 findings, 10 kept
- Self-reflection: 5 issues identified, 0 new corrections
- Memory verification: 10 probes, 9 passed, 1 flagged (BB port)
- Deep dives: 5 topics researched
- Proposals: 7 changes suggested (3 high, 2 medium, 1 low, 1 self-fix)
- Cycle duration: ~25m
- Correction streak: 11+ days without new patterns
