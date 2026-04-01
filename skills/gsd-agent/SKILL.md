---
name: gsd-agent
description: Accountability enforcement engine. Reviews the GTD inbox and backlog, checks completion status via Things 3, runs completion debrief, surfaces overdue and stale items, and generates a prioritized GSD Report. The anti-procrastination engine. Use when asked to "check my todos", "what do I owe people", "run GSD report", "what's overdue", "accountability check", or automatically via cron (2-3x daily). Can send the report via iMessage to Alex or post in session. Celebrates wins. Nags about stale items. Escalates when something overdue was promised to a real person.
---

# gsd-agent

Read Things 3, the GTD files, and the completion journal. Run debrief first (celebrate wins). Then figure out what's stale, what's overdue, what's blocking. Generate a clear, no-bullshit report with a concrete TOP 3 action list.

**Things 3 is the source of truth for active tasks.** inbox.md is the staging buffer. done.md is the completion journal.

## Inputs

- **report_style** (optional): `full` (all items) | `summary` (just the highlights, default) | `top3` (just the three most critical things right now)
- **notify** (optional): `session` (default) | `imessage` (send report to Alex via BlueBubbles)
- **scope** (optional): `all` | `overdue` | `stale` | `promised` — filter what to analyze
- **skip_debrief** (optional): skip the completion debrief step (for quick checks)

## Quick Invocation

```
Run gsd-agent — full report, post in session
```

Notifying Alex via iMessage:
```
Run gsd-agent — summary report, send to Alex via iMessage
```

Just the urgent list:
```
Run gsd-agent — top3 only
```

## Source of Truth Hierarchy

| Source | Role | Tool |
|--------|------|------|
| **Things 3** | Active tasks, completed tasks, areas | `things` CLI |
| **inbox.md** | Staging buffer (capture agent writes here) | File read |
| **done.md** | Completion journal (append-only) | File read |
| **backlog.md** | Legacy triaged items | File read |
| **waiting.md** | Waiting on someone else | File read |
| **active-context.md** | Current working state | File read |

## Workflow

### 0. 🎉 COMPLETION DEBRIEF (Run First!)

Before anything else, check for new completions:

```bash
python3 ~/.openclaw/workspace/skills/gsd-agent/scripts/completion-debrief.py
```

This script:
1. Reads completed tasks from Things 3 (`things logtoday --json`)
2. Compares against state file at `~/.openclaw/workspace/memory/debrief-state.json`
3. For newly completed tasks:
   - Logs them to `/Users/debra/SecondBrain/GTD/done.md`
   - Returns a summary with velocity metrics
4. Updates the state file

Parse the JSON output. If `count > 0`:
- **Celebrate first!** Lead the report with wins.
- If `notify: imessage`: Send the `summary_text` from the debrief output to Alex via BlueBubbles
- The debrief text asks: "nice work on these. anything spawn from them or any context worth noting?"
- If Alex replies with follow-ups, the capture-agent will pick them up on next run

If the debrief script fails or isn't available, fall back to reading done.md directly for recent `- [x]` entries.

### 1. Pull Active Tasks from Things 3

Things 3 is the source of truth. Pull from multiple views:

```bash
things today --json 2>/dev/null
things upcoming --json --limit 20 2>/dev/null
things inbox --json 2>/dev/null
```

Parse each task for: `uuid`, `title`, `status`, `start_date`, `stop_date`, `created`, `area_title`, `tags`, `notes`, `deadline`.

### 1.5 🔍 Oracle Validation (Prevent False Flags)

Before composing the report, cross-reference multiple sources to avoid flagging resolved items:

1. Read `active-context.md` for latest status updates
2. Run `things completed --since yesterday --json` for recently completed tasks
3. Cross-reference: if an item appears in BOTH pending sources (inbox.md, backlog.md) AND completed/resolved sources (Things 3 completed, active-context.md marked done), **mark it resolved and skip it**
4. If `active-context.md` contradicts a memory file or inbox.md, **active-context.md wins** (it's more recent)
5. Check for items manually completed outside Things 3 (e.g., "Annika filled the form" in recent iMessage/session context)

**Why this matters:** Without validation, the report flags already-resolved items (e.g., Boston hotel after it was booked, ORNL Isaac after it was verified). Stale flags erode trust in the report.

### 2. Cross-Reference inbox.md

Read the inbox staging buffer:

```bash
cat /Users/debra/SecondBrain/GTD/inbox.md
```

Compare inbox items against Things 3 tasks (by title similarity). Flag any inbox items NOT yet in Things 3:

```
⚠️ UNPROMOTED: [N] items in inbox.md not yet in Things 3
[list them]
```

These should be reviewed. Either:
- Promote to Things 3 (if actionable)
- Archive to meeting-insights (if not actionable)
- Delete from inbox (if stale/irrelevant)

### 3. Read Supporting GTD Files

```bash
cat /Users/debra/SecondBrain/GTD/backlog.md 2>/dev/null
cat /Users/debra/SecondBrain/GTD/waiting.md 2>/dev/null
cat /Users/debra/.openclaw/workspace/active-context.md 2>/dev/null
```

### 4. Classify Each Open Task

Run each open task (from Things 3 + any unmatched inbox items) through these checks:

**🔴 OVERDUE**
- Has a `deadline` AND that date is in the past
- OR is tagged `urgent` and was created > 48 hours ago with no progress

**🟡 STALE**
- No progress in > 3 days (created > 3 days ago, still open, no modification)
- In inbox (either Things 3 inbox or inbox.md) > 7 days without triage

**🟢 ON TRACK**
- Has a future deadline
- OR was created < 3 days ago
- OR has recent activity

**👥 PROMISED TO SOMEONE** (flag regardless of other status)
- Notes or title reference a real person's name + a commitment
- These get extra escalation if also overdue

**⏳ WAITING**
- Items in waiting.md or tagged as "waiting" in Things 3

### 5. Velocity Stats from done.md

Read the completion journal:

```bash
cat /Users/debra/SecondBrain/GTD/done.md
```

Calculate:
- **Completed today**: entries with today's date
- **Completed this week**: entries within last 7 days
- **Average velocity**: mean days from creation to completion (from `velocity:` field)
- **By area**: count completions per area
- **Completion rate**: completed this week vs. open items (items out / items in)

Velocity verdicts:
- Rate < 0.5: "falling behind. more coming in than going out"
- Rate 0.5-1.0: "keeping pace"
- Rate > 1.0: "crushing it. clearing faster than new stuff arrives"

### 6. Parkinson's Law Check

For any open-ended task (no deadline, open > 3 days):
- Suggest a chunked deadline: "This has been sitting since [date]. Time-box it? Suggest done by [3 days from now]."
- Include 1-3 of these in the report

### 7. Top 3 Right Now

Rank all open items by:
1. Overdue AND promised to someone → top priority
2. Overdue → high priority
3. Urgent + promised → high priority
4. Stale AND promised → medium-high
5. Stale → medium
6. On track + urgent → medium

Pick the top 3. Lead with action verb. Include who/what/when. One line each.

### 8. Generate the Report

```markdown
# 🗂 GSD Report — [Day, Date Time]

## 🎉 WINS
[debrief results — completed tasks with velocity]
[or "Nothing completed yet. let's fix that."]

---

## 📊 VELOCITY
- Completed today: [N]
- Completed this week: [N]
- Avg velocity: [N] days creation-to-done
- By area: [area breakdown]
- Rate: [verdict]

---

## 🔴 OVERDUE ([N] items)
[list each overdue item with deadline]
[⚠️ ESCALATE if promised to someone: "PROMISED TO [name]. flag this!"]

## 🟡 STALE ([N] items)
[list with days sitting]

## 🟢 ON TRACK ([N] items)
[brief list, next deadline first]

## ⏳ WAITING ([N] items)
[items waiting on someone, how long]

---

## 🎯 TOP 3 RIGHT NOW
1. [most critical action]
2. [second most critical]
3. [third most critical]

---

## ⏰ SET A DEADLINE?
[1-3 Parkinson's Law nudges]

## ⚠️ UNPROMOTED ([N] inbox items not in Things 3)
[list or "All inbox items synced to Things 3"]
```

### 9. Escalation Protocol

If ANY item is both overdue AND has a named person referenced:
1. Flag loudly with ⚠️
2. If `notify: imessage`: prepend "⚠️ ESCALATION: [item]. you owe [person] this and it's overdue"

### 10. Deliver the Report

**Session mode** (default): Post formatted report in chat.

**iMessage mode**: Compressed version via BlueBubbles:

```
GSD check [time] 🗂

🎉 Wins: [N completed] — [top win]
🔴 Overdue: [N] — [most critical]
🟡 Stale: [N] items sitting
📊 velocity: [avg]d, [verdict]

🎯 Top 3:
1. [action]
2. [action]
3. [action]

[⚠️ ESCALATE line if applicable]
```

Use the `message` tool:
```
action: send
channel: bluebubbles
target: Alex
message: [compressed report]
```

### 11. Triage Prompt

If inbox.md has > 5 items sitting > 24 hours:

```
📥 INBOX NEEDS TRIAGE: [N] raw items in inbox.md for >24h.
Run: "triage my inbox" to move items to backlog/waiting/someday.
```

## Output Summary

```
GSD Report generated — [timestamp]
- Wins: [N] (debrief)
- Overdue: [N]
- Stale: [N]
- On track: [N]
- Waiting: [N]
- Velocity: [avg days], [rate verdict]
- Unpromoted inbox items: [N]
- Delivered: [session|imessage]
```

## Cron Setup

```
# GSD Report — morning briefing (includes debrief of yesterday's completions)
0 9 * * *   openclaw run gsd-agent --notify imessage --report_style summary

# Midday nudge (session only, skip debrief)
0 13 * * *  openclaw run gsd-agent --report_style top3 --skip_debrief

# EOD accountability check (includes debrief)
0 17 * * *  openclaw run gsd-agent --notify imessage --report_style summary
```

## Reference Files

- **`scripts/completion-debrief.py`**: Completion debrief script. Reads Things 3, updates done.md, returns summary.
- **`references/gtd-triage-guide.md`**: Decision tree for triaging inbox items.
- **`references/escalation-patterns.md`**: Patterns for "promised to someone" detection.
