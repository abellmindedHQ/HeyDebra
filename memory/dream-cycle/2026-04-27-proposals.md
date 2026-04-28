# Dream Cycle Proposals — 2026-04-27

## Summary
Dream cycle #21. OC v2026.4.25 and v2026.4.26 both dropped since our last check, adding ElevenLabs v3 TTS, full OTel observability, asymmetric embeddings, Google Meet integration, and transcript compaction. SWE-bench Verified was officially retired due to benchmark contamination. Opus 4.7 "nerfed" reports validate our wait-and-see. Mem0 benchmarks show graph-enhanced memory outperforms plain RAG by 7%. Self-reflection: 7+ day correction streak, but dream cycle delivery still broken (4th cycle flagging this), 30+ proposals unreviewed, and payment failures aging 20+ days.

## Proposed Changes

### 1. Upgrade OpenClaw to v2026.4.26
**Category:** infrastructure
**Priority:** high
**Effort:** moderate
**Files affected:** gateway config, TOOLS.md

**What:** Upgrade from 2026.4.19-beta.2 to 2026.4.26 (stable). This jumps 7 releases.
**Why:** ElevenLabs v3 TTS improves voice pipeline. OTel gives us token/cost visibility we've never had. Asymmetric embeddings improve memory search. Transcript compaction prevents session bloat. EPIPE crash fix addresses Discord delivery bugs. Google Meet audio pinning solves what we tried to do manually on Apr 1.
**Implementation:**
```
openclaw update
# Verify: openclaw --version → 2026.4.26
# Test: TTS, memory_search, browser, BB webhook
# Enable: OTel metrics, ElevenLabs v3 config
```
**Risk:** Jumping 7 versions. Scan intermediate changelogs for breaking changes before pulling trigger. Schedule during low-activity window.

### 2. Fix Dream Cycle Delivery (SEND, DON'T STAGE)
**Category:** workflow
**Priority:** high
**Effort:** trivial
**Files affected:** skills/dream-cycle/SKILL.md, cron config

**What:** Dream cycle should send the iMessage summary directly as part of Phase 4, not "stage" it for a future session to pick up. The staging model has failed for 4+ consecutive cycles.
**Why:** "Stage and hope" doesn't work. The summary sits in a file no session reads. The fix is embarrassingly simple: just send it.
**Diff preview (SKILL.md delivery section):**
```markdown
## Delivery
- After Phase 4, send morning summary via iMessage directly from the dream cycle session
- Do NOT stage for later delivery
- Send time: immediately after cycle completes (11:30 PM - 12:30 AM)
- Alex will see it when he wakes up
```

### 3. Restart Neo4j
**Category:** infrastructure
**Priority:** medium
**Effort:** trivial
**Files affected:** none (service restart)

**What:** Neo4j has been down for weeks. Restart the service.
**Why:** Mem0 benchmarks show graph-enhanced memory (Mem0g) outperforms plain semantic search by 7% accuracy. Our Neo4j graph data exists (SecondBrain people, relationships, projects). We're leaving free performance on the table by not running it.
**Implementation:**
```
brew services start neo4j
# Verify: curl http://localhost:7474 → Neo4j browser
# Test: qmd query with graph-backed results
```

### 4. Compose Per-Payment Billing Sweep
**Category:** workflow
**Priority:** medium
**Effort:** moderate
**Files affected:** inbox/inbox.md, Things 3

**What:** Instead of listing "8+ payment failures" in every GSD report, compose a specific action plan per payment: what's owed, to whom, what card to use, and whether to cancel or renew. Send as a standalone message to Alex during an engaged window.
**Why:** Listing the same failures every report for 20+ days isn't working. Alex needs a "here's exactly what to do for each one" plan, not another reminder.
**Draft plan:**
```
Payment failures — action needed for each:
1. Notion — renew? Which card?
2. DeepLearning.AI — cancel or update?
3. Runway ($157) — still using it? Cancel?
4. GCP — which project? Update billing?
5. Anthropic — API usage. Update card.
6. AudioTheme — cancel or keep?
7. YMCA — membership active? Update?
8. Midjourney — keep or cancel?
9. Costco Visa — separate issue (locked card)
```

### 5. Defer Opus 4.7 Evaluation
**Category:** config
**Priority:** medium
**Effort:** trivial
**Files affected:** MEMORY.md (status update)

**What:** Update Opus 4.7 status from "proposed for evaluation" to "deferred pending stability reports." HN "nerfed" thread + ongoing harness-layer concerns make it premature to switch.
**Why:** This has been proposed for 4 cycles. The evidence now points to waiting. Stop reproposing it and mark it as deferred with conditions for re-evaluation (Anthropic blog post addressing performance, or 2 weeks of stable community reports).
**Diff preview (MEMORY.md):**
```
- **Opus 4.7:** Deferred. HN reports inconsistent reasoning (Apr 27). 
  Wait for: Anthropic stability confirmation OR 2+ weeks stable community reports.
  Re-evaluate: May 15 or when conditions met.
```

### 6. Verify Claude Code Security Patch
**Category:** infrastructure/security
**Priority:** medium
**Effort:** trivial
**Files affected:** TOOLS.md (version note)

**What:** Check `claude --version` and confirm it includes the prompt injection fix from the source code leak incident. Document the version in TOOLS.md.
**Why:** Paperclip agents run Claude Code with shell access on our machine. If the patch isn't applied, we have a theoretical attack vector via malicious repo contents.
**Implementation:**
```
claude --version
# Compare against post-leak patch version
# Update TOOLS.md with confirmed version
```

### 7. Add Model Evaluation Criteria to MEMORY.md
**Category:** memory
**Priority:** low
**Effort:** trivial
**Files affected:** MEMORY.md

**What:** Add a "Model Evaluation" section noting: (1) don't trust benchmarks (SWE-bench contamination), (2) test on our workloads, (3) evaluation criteria: dream cycle quality, GSD accuracy, code gen, message formatting, tool calling reliability.
**Why:** Every time we consider switching models, we start from scratch. A documented evaluation framework saves time and prevents benchmark-chasing.

## Deferred / Watching

- **Mem0 / Letta evaluation:** Our manual memory system passed 10/10 verification probes. Graph memory would help, but Neo4j restart is the simpler first step. Revisit after OC upgrade + Neo4j restart.
- **AI memory biological decay:** Interesting concept. Not ready for production. Watch for open-source implementations.
- **NVIDIA NemoClaw:** Relevant if we move to GPU-equipped hardware. Not actionable on Mac Mini.
- **DeepSeek V4 Flash as fallback model:** OC 2026.4.24 made it the default. Worth testing as a cheap fallback for heartbeats/crons after upgrade.
- **Home Assistant upgrade (2025.11.3 → 2026.4):** IR first-class support, Matter locks. Lower priority than OC upgrade. Queue for when Alex is ready to invest in HA.

## Meta
- Research scan: 10 findings, 10 kept (4 high, 4 medium, 2 low)
- Self-reflection: 5 issues identified, 0 new corrections (7+ day streak)
- Memory verification: 10 probes, 10 passed, 0 flagged
- Deep dives: 4 topics researched
- Proposals: 7 changes suggested (2 high, 4 medium, 1 low)
- Cycle duration: ~25 min
- 21st consecutive nightly cycle
