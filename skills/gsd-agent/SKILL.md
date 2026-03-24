---
name: gsd-agent
description: Accountability enforcement engine. Reviews the GTD inbox and backlog, checks completion status, surfaces overdue and stale items, and generates a prioritized GSD Report. The anti-procrastination engine. Use when asked to "check my todos", "what do I owe people", "run GSD report", "what's overdue", "accountability check", or automatically via cron (2-3x daily). Can send the report via iMessage to Alex or post in session. Celebrates wins. Nags about stale items. Escalates when something overdue was promised to a real person.
---

# gsd-agent

Read every GTD file. Figure out what's stale, what's overdue, what's blocking. Generate a clear, no-bullshit report with a concrete TOP 3 action list. Celebrate what's done. Escalate what's critical.

## Inputs

- **report_style** (optional): `full` (all items) | `summary` (just the highlights, default) | `top3` (just the three most critical things right now)
- **notify** (optional): `session` (default) | `imessage` (send report to Alex via BlueBubbles)
- **scope** (optional): `all` | `overdue` | `stale` | `promised` — filter what to analyze

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

## GTD File Map

| File | Purpose | Written by |
|------|---------|------------|
| `/Users/debra/SecondBrain/GTD/inbox.md` | Raw captures, untriaged | capture-agent |
| `/Users/debra/SecondBrain/GTD/backlog.md` | Triaged, prioritized items | Manual triage |
| `/Users/debra/SecondBrain/GTD/done.md` | Completed items archive | Manual / gsd-agent |
| `/Users/debra/SecondBrain/GTD/waiting.md` | Waiting on someone else | Manual triage |
| `/Users/debra/SecondBrain/GTD/someday.md` | Not now, don't forget | Manual |
| `/Users/debra/.openclaw/workspace/PROJECTS.md` | Project-level tracking | Manual |
| `/Users/debra/.openclaw/workspace/active-context.md` | Current working state | Every session |

## Workflow

### 1. Read All GTD Files

```bash
cat /Users/debra/SecondBrain/GTD/inbox.md
cat /Users/debra/SecondBrain/GTD/backlog.md
cat /Users/debra/SecondBrain/GTD/done.md
cat /Users/debra/SecondBrain/GTD/waiting.md
cat /Users/debra/.openclaw/workspace/PROJECTS.md 2>/dev/null
cat /Users/debra/.openclaw/workspace/active-context.md 2>/dev/null
```

Parse all `- [ ]` (open) and `- [x]` (done) items.

For each open item, extract:
- Action text
- Due date (from `due:` field)
- Assigned to (from `assigned to:` field)
- Captured date (from `captured:` field)
- Priority (from `priority:` field)
- Source (from `source:` field)
- Last modified — infer from `captured:` or explicit `updated:` if present

### 2. Classify Each Open Item

Run each open item through these checks (in order of severity):

**🔴 OVERDUE**
- Has a `due:` date AND that date is in the past
- OR is marked `priority: urgent` and was captured > 48 hours ago with no progress signal

**🟡 STALE**
- No progress in > 3 days (captured date is > 3 days ago, still open)
- Has no due date but has been in inbox > 7 days (should have been triaged)
- In backlog with no due date and captured > 5 days ago

**🟢 ON TRACK**
- Has a future due date
- OR was captured < 3 days ago
- OR is in backlog with a due date that's still in the future

**👥 PROMISED TO SOMEONE** (flag regardless of other status)
- `assigned to:` references a real person (not "Alex" or "me")
- OR source contains a person's name + a commitment phrase
- These get an extra escalation flag if also overdue

**⏳ WAITING**
- Items in waiting.md — check if they've been waiting > 5 days

### 3. Stats Calculation

From `done.md`:
- Count `- [x]` items with `completed:` date in the last 7 days → **completed this week**
- Count `- [x]` items with `completed:` date in the last 24h → **completed today**

From `inbox.md` + `backlog.md`:
- Count `- [ ]` items with `captured:` in the last 7 days → **added this week**
- Total open items → **open count**

**Velocity** = completed this week / added this week (express as a ratio or %)
- If < 0.5: "you're falling behind — more coming in than going out"
- If > 1.0: "crushing it — clearing faster than new stuff arrives"
- If 0.5–1.0: "keeping pace"

### 4. Parkinson's Law Check

For any open-ended task (no due date, in backlog > 3 days):
- Suggest a chunked deadline: "This has been sitting since [date]. Want to time-box it? Suggest: [task] → done by [3 days from now]."
- Include 1-3 of these suggestions in the report under a "Set a Deadline?" section.

### 5. Top 3 Right Now

Rank all open items by:
1. Overdue AND promised to someone → top priority
2. Overdue → high priority
3. Urgent priority + promised → high priority
4. Stale AND promised → medium-high
5. Stale → medium
6. On track + urgent → medium

Pick the top 3 and make them concrete:
- Lead with the action verb
- Include the who/what/when
- Keep it one line each

### 6. Win Celebration

If any items were completed in the last 24h (check done.md), lead the report with a shoutout:

```
🎉 WINS TODAY: [list completed items]
```

If nothing in 24h but wins in the last week:
```
✅ WINS THIS WEEK: [N] items shipped — [list if ≤ 3, or "see done.md" if more]
```

If the done.md has zero entries ever: skip the section, don't shame.

### 7. Generate the Report

```markdown
# 🗂 GSD Report — [Day, Date Time]

## 🎉 WINS
[wins or "Nothing completed yet — let's fix that."]

---

## 🔴 OVERDUE ([N] items)
[list each overdue item, one per line, with due date]
[⚠️ ESCALATE if promised to someone: "PROMISED TO [name] — flag this!"]

## 🟡 STALE ([N] items)
[list each stale item with how many days it's been sitting]

## 🟢 ON TRACK ([N] items)
[brief list — next due date first]

## ⏳ WAITING ([N] items)
[items waiting on someone — with how long they've been waiting]

---

## 📊 STATS
- Open items: [N]
- Completed this week: [N]
- Added this week: [N]
- Velocity: [ratio + verdict]

---

## 🎯 TOP 3 RIGHT NOW
1. [most critical action]
2. [second most critical]
3. [third most critical]

---

## ⏰ SET A DEADLINE?
[1-3 Parkinson's Law nudges for open-ended items]
```

### 8. Escalation Protocol

If ANY item is both:
- Overdue (past due date or urgent + >48h old)
- AND has `assigned to:` referencing a real named person (not Alex himself)

Then:
1. Flag it loudly in the report with ⚠️
2. If `notify: imessage` mode: prepend the iMessage with "⚠️ ESCALATION: [item] — you owe [person] this and it's overdue"

### 9. Deliver the Report

**Session mode** (default): Post the formatted report directly in the chat.

**iMessage mode**: Send a compressed version via BlueBubbles:

```bash
# Use the message tool with channel=bluebubbles, target=Alex's phone
```

iMessage format (compressed — texts, not essays):

```
GSD check [time] 🗂

🔴 Overdue: [N] — [most critical one]
🟡 Stale: [N] items sitting
📊 [N] done this week, [N] open

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
target: Alex  (or use phone +18135343383)
message: [compressed report]
```

### 10. Triage Prompt (if inbox has untriaged items)

If `inbox.md` has > 5 uncaptured items that have been there > 24 hours, append to the report:

```
📥 INBOX NEEDS TRIAGE: [N] raw items sitting in inbox.md for >24h. 
Run: "triage my inbox" to move items to backlog/waiting/someday.
```

## Output Summary

At the end of the run (for cron logs):

```
GSD Report generated — [timestamp]
- Overdue: [N]
- Stale: [N]
- On track: [N]
- Waiting: [N]
- Wins today: [N]
- Velocity: [ratio]
- Delivered: [session|imessage]
```

## Cron Setup

Recommended: 3x daily — morning briefing, midday nudge, EOD wrap.

```
# GSD Report — morning briefing
0 9 * * *   openclaw run gsd-agent --notify imessage --report_style summary

# Midday nudge (session only)
0 13 * * *  openclaw run gsd-agent --report_style top3

# EOD accountability check
0 17 * * *  openclaw run gsd-agent --notify imessage --report_style summary
```

Or set up via OpenClaw:
```
Schedule gsd-agent to run at 9am, 1pm, and 5pm daily, send summary to Alex via iMessage
```

## Reference Files

- **`references/gtd-triage-guide.md`**: Decision tree for triaging inbox items into backlog / waiting / someday. What makes something "urgent" vs. "normal" vs. parking-lot material.
- **`references/escalation-patterns.md`**: Examples of "promised to someone" patterns — phrasing that signals a commitment to a named person vs. a general task.
