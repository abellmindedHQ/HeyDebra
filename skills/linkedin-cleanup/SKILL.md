# linkedin-cleanup

Automates archiving spam and one-touch LinkedIn message conversations via browser automation with strict rate limiting and safety safeguards.

**Triggers on:** "clean up LinkedIn", "archive LinkedIn messages", "LinkedIn inbox cleanup", "run LinkedIn cleanup", "cleanup queue status"

**⚠️ Use cheapest model:** `google/gemini-2.0-flash-lite` — this skill clicks buttons, not think.

---

## Quick Start

1. **Generate queue** (first time only): `python3 scripts/generate_queue.py`
2. **Review & approve** the queue when prompted
3. **Run cleanup**: follow the Browser Automation Flow below
4. **Set up cron** for automated daily batches

---

## State File

All progress is persisted at:
`/Users/debra/.openclaw/workspace/memory/linkedin-cleanup-state.json`

```json
{
  "totalQueued": 9685,
  "totalArchived": 0,
  "todayArchived": 0,
  "todayDate": "2026-03-23",
  "lastRunAt": null,
  "lastError": null,
  "queue": [],
  "completed": [],
  "paused": false
}
```

Use `python3 scripts/cleanup_state.py status` to check progress at any time.

---

## Rate Limiting (HARD LIMITS — never bypass)

| Limit | Value |
|-------|-------|
| Max archives per session | **50** |
| Max archives per day | **150** |
| Delay between archives | **3–10 seconds (random)** |
| Max session duration | **15 minutes** |
| Operating hours | **9am–5pm ET, weekdays only** |

**Stop immediately on:** any error, captcha, unusual response, slow page load, or unexpected UI.

**Never DELETE** — only ARCHIVE (reversible action).

See `references/safeguards.md` for full details and LinkedIn ToS notes.

---

## Browser Automation Flow

When asked to run cleanup, follow these steps exactly:

### Step 1 — Load State
```python
# Run to get current state
python3 scripts/cleanup_state.py status
```

Check:
- Is `paused` = false?
- Is `todayArchived` < 150?
- Is the queue non-empty?
- Is current time 9am–5pm ET on a weekday?

If any check fails, report to user and stop.

### Step 2 — Open LinkedIn
1. Use `browser` tool: `action=open, url=https://www.linkedin.com/messaging/, profile=user`
2. Take a snapshot: `action=snapshot`
3. Verify you see the conversation list (NOT a login page or CAPTCHA)
4. If not logged in → stop, tell user to log in manually

### Step 3 — Archive Loop

For each conversation at the top of the queue:

```
a. Record start time
b. Find conversation in the list (scroll/search by name if needed)
c. Hover over conversation row to reveal options
d. Click the "⋯" (three-dot / ellipsis) menu on the conversation
e. Click "Archive" from the dropdown
f. Take snapshot to confirm conversation is gone from active list
g. Log: { name, timestamp, status: "archived" }
h. Call: python3 scripts/cleanup_state.py mark-done "<name>"
i. Wait random 3–10 seconds
j. Check limits:
   - sessionCount >= 50 → stop
   - todayArchived >= 150 → stop
   - elapsed >= 15 min → stop
   - Any error/unexpected UI → stop immediately
```

**On ANY unexpected state:** take a screenshot, log the error, call `python3 scripts/cleanup_state.py set-error "<description>"`, and stop the session.

### Step 4 — Save & Report
```
python3 scripts/cleanup_state.py status
```
Report: archived this session, archived today, total remaining, estimated days to completion.

---

## Cron Setup

Recommended schedule — runs 3x/day on weekdays, skipping every 3rd day via the state file cooldown logic:

```json
{
  "name": "🧹 LinkedIn Cleanup",
  "schedule": {
    "kind": "cron",
    "expr": "0 10,13,16 * * 1-5",
    "tz": "America/New_York"
  },
  "payload": {
    "kind": "agentTurn",
    "model": "google/gemini-2.0-flash-lite",
    "message": "Run LinkedIn cleanup: archive next batch from the queue. Use the linkedin-cleanup skill."
  },
  "sessionTarget": "isolated"
}
```

**Cooldown:** The state helper enforces a cooldown skip every 3rd day automatically. At 150/day × 5 days/week × ~2/3 active days = ~500/week → ~19 weeks to clear 9,685 conversations.

---

## Generate Queue (First Time)

```bash
cd /Users/debra/.openclaw/workspace/skills/linkedin-cleanup
python3 scripts/generate_queue.py \
  --input "/Users/debra/SecondBrain/Documents/LinkedIn Message Analysis.md" \
  --output "/Users/debra/.openclaw/workspace/memory/linkedin-cleanup-state.json"
```

Script will:
1. Parse the analysis report for ⚪ spam and 🟢 one-touch conversations
2. Sort: spam first, then one-touch (oldest first)
3. Show a summary and ask for confirmation before writing
4. Initialize the state file

**First run requires explicit approval.** The script will not write without typing `yes`.

---

## Commands Reference

| Command | Description |
|---------|-------------|
| `python3 scripts/cleanup_state.py status` | Show full progress summary |
| `python3 scripts/cleanup_state.py mark-done "<name>"` | Mark a conversation archived |
| `python3 scripts/cleanup_state.py set-error "<msg>"` | Log an error and pause |
| `python3 scripts/cleanup_state.py unpause` | Resume after a paused/error state |
| `python3 scripts/cleanup_state.py reset-today` | Reset daily counter (use carefully) |
| `python3 scripts/generate_queue.py --preview` | Preview queue without writing |

---

## Safety Checklist (Before Each Run)

- [ ] State file exists and `paused` is false
- [ ] `todayArchived` < 150
- [ ] Queue is non-empty
- [ ] Time is 9am–5pm ET, weekday
- [ ] LinkedIn is accessible (not showing login or CAPTCHA)
- [ ] No recent errors in `lastError` field
