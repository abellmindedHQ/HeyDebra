# Dream Cycle Proposals — 2026-04-28 (DC #22)

## Summary
22nd consecutive nightly cycle. Alex has been silent 4 days. Key findings: Opus 4.7 GA with self-verification behavior, Claude 4.0 deprecation June 15, Anthropic's Project Deal agent-to-agent commerce, HA 2026.4 release (we're 5 versions behind), VibeVoice open-source TTS. Self-reflection found 0 new corrections (8-day clean streak), but systemic issues persist: 30+ unreviewed proposals, payment failures aging 21+ days, infrastructure stagnation. Proposing 7 changes.

## Proposed Changes

### 1. Upgrade to Claude Opus 4.7
**Category:** config
**Priority:** high
**Effort:** trivial
**Files affected:** OpenClaw gateway config (openclaw.json)

**What:** Change default model from `anthropic/claude-opus-4-6` to `anthropic/claude-opus-4-7`.
**Why:** Opus 4.7 offers self-verification (addresses our #2 correction pattern), efficiency gains ("low-effort 4.7 ≈ medium-effort 4.6"), better vision, stronger instruction following. Same pricing. Direct upgrade.
**Diff preview:**
```
- "model": "anthropic/claude-opus-4-6"
+ "model": "anthropic/claude-opus-4-7"
```
**Note:** Requires Alex approval per AGENTS.md (gateway config change). Suggest 24h test period.

### 2. Audit Model Strings for Deprecation
**Category:** infrastructure
**Priority:** high
**Effort:** trivial
**Files affected:** Any files with hardcoded model strings

**What:** Run grep audit across workspace, Paperclip config, and scripts for deprecated model strings (claude-opus-4-0, claude-sonnet-4-0, anthropic-beta max-tokens headers). Update any found.
**Why:** Claude 4.0 retires June 15. 1M context beta retires April 30 (TOMORROW). Need to ensure nothing breaks.
**Diff preview:** Grep + replace any matches. Can self-apply the audit (read-only), but fixes need review.

### 3. Fix Dream Cycle Delivery Workflow
**Category:** workflow
**Priority:** high
**Effort:** moderate
**Files affected:** skills/dream-cycle/SKILL.md, AGENTS.md

**What:** Change iMessage morning summary from "proposals ready for review when you want em" to including the top 3 proposals as actionable items directly in the message. Stop saying "check the files" — put the substance in the message.
**Why:** 22 cycles, 30+ proposals, 0 reviewed. The current delivery mechanism demonstrably doesn't work. Alex doesn't check files unless the content is compelling in the notification itself.
**Diff preview:**
```markdown
# Current morning message format:
🌙 Dream cycle ran last night
Found X things, proposing Z changes.
Proposals ready for review when you want em.

# Proposed format:
🌙 Dream cycle ran. Top 3:
1. [Specific proposal] — [one line why] — say "yes" to apply
2. [Specific proposal] — [one line why] — say "yes" to apply  
3. [Specific proposal] — [one line why] — say "yes" to apply
X more in the vault if you're curious.
```

### 4. Schedule Home Assistant Update
**Category:** infrastructure
**Priority:** medium
**Effort:** moderate
**Files affected:** HA config, TOOLS.md

**What:** Plan and execute HA upgrade from 2025.11.3 to 2026.4.4. Full backup first, staged if needed.
**Why:** 5 major releases behind. Missing IR control (projector, Samsung TV), AI agent debugging, Matter locks, security patches, modern dashboard features.
**Note:** Needs Alex's OK and a dedicated maintenance window (weekend preferred).

### 5. Add Deprecation Timeline to TOOLS.md
**Category:** memory
**Priority:** medium
**Effort:** trivial
**Files affected:** TOOLS.md

**What:** Add a "Model Deprecation Timeline" section to TOOLS.md noting Claude 4.0 retirement June 15, 1M beta retirement April 30, and current model versions.
**Why:** This is the kind of operational knowledge that should be in TOOLS.md for quick reference.
**Diff preview:**
```markdown
### Model Deprecation Timeline
- Claude Opus 4.0 / Sonnet 4.0: **retired June 15, 2026** (we're on 4.6, safe)
- 1M context beta (Sonnet 4.5/4.0): **retired April 30, 2026** (4.6+ has 1M standard)
- Current: anthropic/claude-opus-4-6 (consider 4.7 upgrade)
```

### 6. Create "Silent Human" Protocol
**Category:** workflow
**Priority:** medium
**Effort:** moderate
**Files affected:** AGENTS.md

**What:** Add a protocol for when Alex hasn't responded in N days. Tiers:
- **24h:** Normal. Keep working, log context.
- **48h:** Flag in GSD. Check calendar for conflicts.
- **72h:** Send a simple "hey, checking in" via iMessage. No task dump.
- **5+ days:** Consider reaching out to Hannah or checking HA presence sensors.
**Why:** We're at day 4 with no protocol. I've been sending GSD reports into the void. A tiered escalation prevents both over-nagging and under-alerting.

### 7. Evaluate VibeVoice as ElevenLabs Alternative
**Category:** infrastructure
**Priority:** low
**Effort:** significant
**Files affected:** TTS config, skills

**What:** Benchmark Microsoft VibeVoice (MIT, open-source) against ElevenLabs for our use cases: short iMessage voice memos, Be Particular audiobook chapters, general TTS.
**Why:** Open-source = no per-token cost after setup. 90-minute multi-speaker TTS could handle audiobook production. But ElevenLabs quality is proven and our custom voice is already trained there.
**Note:** Not urgent. Queue for a future exploration session.

## Deferred / Watching

- **Anthropic Project Deal:** Agent-to-agent commerce. Relevant to HeyDebra/Pools vision but not actionable now.
- **Neo4j Aura Agent:** Managed graph-powered agents. Could replace our local Neo4j (down 31 days). Watch for pricing/self-hosted options.
- **Claude Mythos Preview:** Most powerful model but limited release + cyber safeguards. Not available to general API users yet.
- **HuggingFace LeRobot RCE:** Not using it, but reminder to audit our own supply chain security.
- **GitHub Copilot billing change (June 1):** Track if we enable Copilot on private repos.

## Meta
- Research scan: 10 findings, 10 kept (3 high, 5 medium, 2 low)
- Self-reflection: 5 issues identified, 0 new corrections (8-day streak)
- Memory verification: 10 probes, 9 passed, 1 new info captured
- Deep dives: 4 topics researched (Opus 4.7, Project Deal, HA 2026.4, deprecation audit)
- Proposals: 7 changes suggested (3 high, 3 medium, 1 low)
- Cycle duration: ~25m
