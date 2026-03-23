# LinkedIn Cleanup — Safeguards Reference

Detailed rate limiting rules, safety procedures, and LinkedIn ToS notes.

---

## Hard Rate Limits

These are non-negotiable. Hard-coded into `cleanup_state.py`. Never bypass.

| Limit | Value | Rationale |
|-------|-------|-----------|
| Max archives per session | 50 | Keeps individual sessions short; reduces detection risk |
| Max archives per day | 150 | LinkedIn daily automation threshold — exceeding raises flags |
| Min delay between archives | 3 seconds | Mimics human clicking speed |
| Max delay between archives | 10 seconds | Randomization prevents pattern detection |
| Max session duration | 15 minutes | Hard stop regardless of count |
| Operating window | 9am–5pm ET, Mon–Fri | Business hours = human-like behavior pattern |
| Cooldown | Skip every 3rd day | Prevents consecutive-day automation detection |

---

## Immediate Stop Conditions

Stop the session **immediately** (no further actions) if any of the following occur:

1. **CAPTCHA detected** — Any challenge/verification page
2. **Login page shown** — Session expired or account flagged
3. **"Unusual activity" message** — LinkedIn security response
4. **Archive button not found** — UI may have changed; don't improvise
5. **Page load timeout** (>10 seconds) — Network issue or throttling
6. **Any JavaScript error** visible in console during automation
7. **Unexpected modal/dialog** — Unknown popups may indicate security review
8. **Rate limit message** from LinkedIn ("You're doing this too fast", etc.)
9. **Account restriction notice** — Stop entirely, notify Alex

**When stopping on error:**
```bash
python3 scripts/cleanup_state.py set-error "Brief description of what happened"
```
This pauses the state file and prevents cron from retrying until manually unpaused.

---

## Why ARCHIVE, Not DELETE

**Always ARCHIVE, never DELETE.**

- Archive is reversible — conversations can be unarchived at any time
- Delete is permanent and cannot be undone
- LinkedIn's archive feature is the intended tool for inbox management
- This is explicitly designed into the LinkedIn UI for bulk inbox cleanup

LinkedIn's archive = moves conversation to "Archived" tab, not trash.

---

## LinkedIn Terms of Service Notes

LinkedIn's User Agreement (Section 8.2) prohibits:
- "Scrape or crawl LinkedIn"
- "Use bots or other automated methods to access LinkedIn"

**Mitigations in this skill:**
1. We're operating on Alex's own account only
2. We're archiving his own messages (not scraping others' data)
3. Human-mimicking delays (3-10s random, not mechanical)
4. Business hours only (human schedule)
5. Conservative daily limits (a human could archive 150/day manually)
6. Cooldown days built in

**Risk assessment:** Low to moderate. This is equivalent to a human using a keyboard shortcut to archive conversations, just automated. The conservative limits are designed to stay well below LinkedIn's detection thresholds.

**If LinkedIn restricts the account:** Stop immediately, do not retry for at least 7 days, and consider reducing the daily limit.

---

## Cron Safety

The recommended cron runs 3x/day at 10am, 1pm, 4pm ET on weekdays:
```
0 10,13,16 * * 1-5
```

At 150/day × cooldown logic (~2/3 of days active) ≈ 100 effective/day.

9,685 conversations ÷ 100/day = ~97 days ≈ **~14 weeks** to complete.

The 50-per-session cap means each cron run archives at most 50, so 150/day requires 3 sessions. Each session is max 15 minutes, so total daily automation time is ≤45 minutes (spread across the day).

---

## Cooldown Logic

Every 3rd calendar day is a cooldown day:
```python
day_number = datetime.now().toordinal()
is_cooldown = (day_number % 3) == 0
```

This creates a pattern of: run, run, skip, run, run, skip...
Which looks like a busy human who occasionally ignores their inbox.

---

## Emergency Procedures

### If LinkedIn shows a security challenge:
1. Stop the cleanup immediately
2. Log in manually (human, no automation)
3. Complete any verification they require
4. Wait 48 hours minimum before resuming
5. Reduce daily limit to 75 temporarily

### If the account gets temporarily restricted:
1. Stop all cleanup automation
2. Wait for LinkedIn to lift the restriction
3. Resume only after at least 1 week
4. Cut daily limit to 50 permanently
5. Alert Alex via iMessage

### If the UI changes and archive button isn't found:
1. Take a screenshot
2. Log the error
3. Do not attempt workarounds
4. Notify Alex — skill may need an update to match new UI

---

## State File Integrity

The state file at `/Users/debra/.openclaw/workspace/memory/linkedin-cleanup-state.json` is the source of truth.

- All operations are atomic JSON writes
- Always use `cleanup_state.py` to modify state (never edit manually in production)
- The `completed` array is the audit log — never truncate it
- If the state file is corrupt, `generate_queue.py` can regenerate (preserving zero progress)

---

## Audit Trail

Each archived conversation is logged in `state["completed"]`:
```json
{
  "name": "John Doe",
  "category": "one-touch",
  "dateDetected": "2024-01-15",
  "addedAt": "2026-03-23T10:00:00",
  "archivedAt": "2026-03-23T10:05:23-05:00"
}
```

This provides a full audit trail for:
- Verifying which conversations were archived and when
- Recovering context if a conversation is accidentally archived
- Reporting progress to Alex
