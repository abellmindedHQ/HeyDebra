# Research: LinkedIn Cleanup Skill Spec
*Researched 2026-03-23 for building the linkedin-cleanup skill*

## The Problem
- 9,685 conversations to archive (9,527 one-touch + 158 spam)
- Need to do it safely without getting flagged/banned
- Need to be token-efficient (daddy got bills)
- Need to be consistent and automated via cron

## Key Research Findings

### LinkedIn Rate Limits (2026)
- LinkedIn actively detects automation via behavioral patterns, acceptance rates, response rates
- Archiving is LESS monitored than outbound actions (messages, connections)
- No official rate limit for archiving, but general guidance: 50-75 actions per session is safe
- 25-40% of cloud-based automation users get restricted within 6 months
- Key triggers: rapid actions, no delays, consistent timing, weekend activity, sudden spikes

### Community Insight: Cookie-Based Approach
- A community member on r/openclaw is building a skill that uses LinkedIn cookies (`li_at`, `jsession`) to manage inbox WITHOUT full browser automation
- This would be DRAMATICALLY more token efficient — no screenshots, no DOM parsing, no click simulation
- Just HTTP requests with auth cookies
- Worth investigating but adds security risk (storing session cookies)

### Token Cost Optimization Strategies

1. **Model Cascading** (biggest savings, 60-87% reduction):
   - Browser automation clicks/archiving = cheap model (Gemini Flash, GPT-4o mini, Haiku)
   - Decision making (classify conversations) = already DONE via analysis, no AI needed at runtime
   - Summary/reporting = cheap model
   
2. **Caching**: Cache DOM snapshots, selector patterns. Cached tokens 75-90% cheaper.

3. **Structured outputs**: Request JSON, not prose. Less output tokens.

4. **Disable unnecessary tools/skills**: Each tool schema adds to system prompt. LinkedIn cleanup cron should load MINIMAL tools (browser only).

5. **Light context**: Use `lightContext: true` on the cron to skip loading AGENTS.md, SOUL.md, etc.

### Model Pricing Comparison (per million tokens)

| Model | Input | Output | Best For |
|-------|-------|--------|----------|
| Gemini 2.0 Flash Lite | $0.08 | $0.30 | Cheapest. browser clicking. |
| GPT-4o mini | $0.15 | $0.60 | Good balance. |
| Claude Haiku | $0.80 | $4.00 | Fast, good reasoning. |
| Claude Sonnet | $3.00 | $15.00 | Current default. overkill for clicking. |
| Claude Opus | $15.00 | $75.00 | DEFINITELY overkill for clicking. |

**Recommendation**: Use Gemini Flash or GPT-4o mini for the cron job. We're literally just clicking archive buttons. No need for Opus-level reasoning.

## Proposed Architecture

### Approach 1: Browser Automation (Safe, Proven)
```
Cron (3x daily, business hours) →
  Light context (browser tool only) →
  Cheap model (Gemini Flash) →
  Open LinkedIn messages →
  Load pre-generated cleanup queue →
  Archive next batch (50 conversations) →
  Random delays 3-10s between each →
  Log results →
  Update progress tracker →
  Stop
```

### Approach 2: Cookie API (Faster, Riskier, WAY Cheaper)
```
Cron →
  Extract li_at cookie from browser session →
  Make direct API calls to archive endpoint →
  No browser needed, no screenshots, minimal tokens →
  Much faster throughput →
  BUT: if LinkedIn detects API pattern, higher ban risk
```

### Recommendation
**Start with Approach 1** (browser automation with cheap model). It's safer and proven. If it's too slow or too expensive, investigate Approach 2 later.

### Safeguards (Built Into Skill)
1. Daily action counter (hard limit, persisted to disk)
2. Random delays 3-10s between actions
3. Session time limits (max 15 min per run)
4. Cool-down: skip every 3rd day
5. Business hours only (9am-5pm ET, weekdays)
6. Stop on ANY error/captcha/unusual response
7. Progress log with full audit trail
8. Batch pre-approved by Alex (first run requires explicit approval)
9. Never delete, only archive (reversible)

### Cron Configuration
```json
{
  "schedule": { "kind": "cron", "expr": "0 10,13,16 * * 1-5", "tz": "America/New_York" },
  "payload": { "kind": "agentTurn", "model": "google/gemini-2.0-flash-lite" },
  "sessionTarget": "isolated"
}
```
Runs at 10am, 1pm, 4pm ET, weekdays only. Uses cheapest model available.

## Timeline Estimate
- 50 archives per run × 3 runs/day × 5 days/week = 750/week
- 9,685 conversations ÷ 750/week = **~13 weeks** (3 months)
- With cool-down days factored in: **~15 weeks**

Not fast, but safe. and it runs itself while you sleep.
