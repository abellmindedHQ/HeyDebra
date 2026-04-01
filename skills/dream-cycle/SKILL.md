---
name: dream-cycle
description: Nightly autonomous self-improvement cycle. Scans AI/tech developments, reflects on recent performance, researches relevant findings in depth, and proposes staged changes to skills, config, and workflows. Use when asked to "run dream cycle", "night swim research", "self-improve", "what's new in AI", or automatically via late-night cron. Inspired by iterative AI self-improvement loops.
---

# Dream Cycle

Autonomous nightly research + self-reflection + improvement proposal pipeline.

Runs in 4 phases. Each phase feeds the next. Output is a staged changelog for human review, never auto-applied.

**Model:** Use `anthropic/claude-sonnet-4-6` for phases 1-2 (scanning/reflection). Use `anthropic/claude-opus-4-6` for phase 3 (deep research). Phase 4 synthesis can use either.

---

## Phase 1: Research Scan (~5 min)

Scan for developments relevant to our stack and interests.

### Sources (check all, skip if unreachable)

```
- GitHub Trending (daily, weekly)
- HuggingFace papers (daily)
- arXiv cs.AI + cs.CL (last 24h)
- r/LocalLLaMA, r/MachineLearning (top/day)
- Hacker News (top 30)
- OpenClaw GitHub releases/issues
- Anthropic blog, OpenAI blog, Google AI blog
- web_search: "AI agent framework" OR "Claude" OR "OpenClaw" (last 24h)
```

### Filter Criteria

Keep only items matching ≥1:
- Directly relevant to OpenClaw, Claude, or our tooling
- New technique for agent memory, planning, or tool use
- Breakthrough in areas Alex works on (knowledge graphs, second brain, NLP)
- Security/privacy developments affecting our setup
- Cost reduction or performance improvement for our stack
- Home automation / smart home AI integration

### Output

Write findings to: `memory/dream-cycle/YYYY-MM-DD-scan.md`

Format per finding:
```markdown
### [Title](url)
**Source:** GitHub/arXiv/HN/etc | **Relevance:** high/medium
**Summary:** 2-3 sentences
**Why it matters for us:** 1-2 sentences connecting to our specific setup
```

Cap at 10 findings. Quality over quantity.

---

## Phase 2: Self-Reflection (~3 min)

Review recent performance and identify improvement opportunities.

### Data Sources

1. Read `memory/YYYY-MM-DD.md` for last 3 days
2. Read `active-context.md`
3. Read `MEMORY.md` critical lessons section
4. **Read `memory/corrections.md`** — online corrections captured during sessions
5. Search session transcripts (via `memory_search`) for:
   - "mistake", "wrong", "fix", "oops", "sorry"
   - "slow", "took too long", "repeated"
   - "should have", "next time", "lesson"
6. Review any error logs or failed cron runs

### Corrections Analysis (NEW)

After reading `memory/corrections.md`:
1. Group entries by `pattern-key`
2. Count occurrences per pattern in the last 7 days
3. For any pattern with **3+ occurrences**: propose promotion to MEMORY.md, AGENTS.md, SOUL.md, or TOOLS.md (whichever is most appropriate)
4. For any pattern with **2 occurrences**: flag as "watch" in proposals
5. Use `memory_search` to find related corrections (semantic similarity) — patterns may use different keys but describe the same issue
6. Include a "Corrections Summary" section in the reflection output:
   - Total corrections since last cycle
   - Top 3 pattern-keys by frequency
   - Promotion candidates (3x+)
   - Watch list (2x)

### Reflection Questions

- What did I do well this week?
- What mistakes did I make? (be specific, not vague)
- What did Alex have to repeat or correct? (cross-reference corrections.md)
- What tasks took too long? Why?
- What knowledge gaps did I hit?
- Are there patterns in my failures?
- What skills or workflows feel clunky?
- Did any cron jobs fail or produce bad output?

### Output

Write to: `memory/dream-cycle/YYYY-MM-DD-reflection.md`

Be honest and specific. "I was slow at X because Y" not "I could improve."

---

## Phase 2.5: Memory Verification (~3 min)

Verify memory accuracy by probing recent facts against stored memory.

### Process

1. Read the last 3 days of `memory/YYYY-MM-DD.md` files
2. Generate 5-10 factual QA pairs from those files, e.g.:
   - "What is Neo4j's current status?" → expected: "down since Mar 28"
   - "When is Alex's Boston flight?" → expected: "Apr 2, 7:30am"
   - "Who is Avie's co-parent?" → expected: "Annika Abell"
3. Query `memory_search` for each answer
4. Compare search results against expected answers
5. Flag:
   - **Contradictions**: memory says X, daily notes say Y
   - **Stale info**: memory has outdated status (e.g., project marked active but completed)
   - **Missing info**: important facts from recent days not findable via search
   - **Wrong associations**: people/project connections that are incorrect

### Output

Append to: `memory/dream-cycle/YYYY-MM-DD-reflection.md` under a `## Memory Verification` section

Format:
```markdown
## Memory Verification
- Probes: X total, Y passed, Z flagged
- Contradictions: [list specific ones]
- Stale entries: [list with suggested fixes]
- Missing from memory: [facts that should be searchable but aren't]
```

If issues are found, include memory fix proposals in Phase 4.

---

## Phase 3: Deep Research (~10 min)

Take the top 3-5 findings from Phase 1 and research them deeply.

### Process

For each selected finding:
1. `web_fetch` the full source (paper, repo, blog post)
2. If it's a repo, examine the README, architecture, key files
3. If it's a paper, read abstract + introduction + results + conclusion
4. Cross-reference with our current setup: what would change?
5. Assess implementation difficulty (trivial / moderate / significant / major)
6. Estimate cost impact if applicable

### Output

Append deep analysis to: `memory/dream-cycle/YYYY-MM-DD-research.md`

Format:
```markdown
## Deep Dive: [Title]

### What It Is
[Detailed explanation]

### How It Applies to Us
[Specific connections to our stack, workflows, skills]

### Implementation Path
[Concrete steps to adopt, with difficulty rating]

### Trade-offs
[What we gain vs what it costs — tokens, complexity, maintenance]

### Recommendation
[Do it now / Queue it / Watch it / Skip it]
```

---

## Phase 4: Proposal & Changelog (~5 min)

Synthesize phases 1-3 into actionable proposals.

### Categories of Changes

1. **Skill improvements** — updates to existing SKILL.md files
2. **New skills** — things we should build
3. **Config changes** — OpenClaw gateway config, cron schedules
4. **Memory updates** — lessons to add to MEMORY.md
5. **Workflow changes** — how I operate day-to-day (AGENTS.md, SOUL.md)
6. **Infrastructure** — tools, integrations, dependencies

### Output

Write to: `memory/dream-cycle/YYYY-MM-DD-proposals.md`

Format:
```markdown
# Dream Cycle Proposals — YYYY-MM-DD

## Summary
[3-5 sentence overview of tonight's cycle]

## Proposed Changes

### 1. [Change Title]
**Category:** skill/config/memory/workflow/infrastructure
**Priority:** high/medium/low
**Effort:** trivial/moderate/significant
**Files affected:** [list]

**What:** [Description of the change]
**Why:** [Justification from research or reflection]
**Diff preview:**
\```
[Show the actual proposed edit if small, or describe it if large]
\```

### 2. [Next change...]
...

## Deferred / Watching
[Items worth tracking but not acting on yet]

## Meta
- Research scan: X findings, Y kept
- Self-reflection: X issues identified
- Deep dives: X topics researched
- Proposals: X changes suggested
- Estimated cost: ~$X.XX (model usage)
- Cycle duration: ~Xm
```

---

## Delivery

After all phases complete:

1. Save all outputs to `memory/dream-cycle/`
2. Write a brief summary to `memory/YYYY-MM-DD.md` (daily log)
3. **Do NOT auto-apply any changes**
4. Deliver summary via iMessage to Alex in the morning (or announce in session)
5. Stage proposals for review. Alex approves, rejects, or modifies each one.

### Morning Delivery Format (iMessage)

Keep it short and punchy:
```
🌙 Dream cycle ran last night

Found X interesting things, reflected on Y issues, proposing Z changes.

Top finds:
• [One-liner about most interesting finding]
• [One-liner about second]

Proposals ready for review when you want em.
```

---

## Cron Setup

Recommended schedule: 11:30 PM ET nightly

```json
{
  "name": "dream-cycle",
  "schedule": { "kind": "cron", "expr": "30 23 * * *", "tz": "America/New_York" },
  "payload": {
    "kind": "agentTurn",
    "message": "Run the dream-cycle skill. Complete all 4 phases. Save outputs to memory/dream-cycle/. Do NOT auto-apply any changes. Deliver morning summary via iMessage to Alex (+18135343383).",
    "model": "anthropic/claude-opus-4-6",
    "timeoutSeconds": 1800
  },
  "sessionTarget": "isolated",
  "delivery": { "mode": "announce" }
}
```

---

## File Structure

```
memory/dream-cycle/
├── YYYY-MM-DD-scan.md        (Phase 1: research findings)
├── YYYY-MM-DD-reflection.md  (Phase 2: self-assessment)
├── YYYY-MM-DD-research.md    (Phase 3: deep dives)
└── YYYY-MM-DD-proposals.md   (Phase 4: staged changelog)
```

---

## Safety Rails

- **Never auto-apply changes.** All proposals are staged for human review.
- **Never modify SOUL.md, AGENTS.md, or gateway config** without explicit approval.
- **Cap spending:** If estimated token usage exceeds $5 in a single cycle, stop after Phase 2 and note it.
- **Don't hallucinate improvements.** If nothing interesting was found, say so. A "nothing notable tonight" report is perfectly valid.
- **Rate limit web requests.** Space fetches 2-3 seconds apart. Don't hammer any single source.
