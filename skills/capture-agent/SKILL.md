---
name: capture-agent
description: Universal action item extractor. Scans ALL communication streams (email, iMessage, calendar, LLM exports, drop-folder text files) and writes extracted commitments, todos, follow-ups, and deadlines to the unified GTD inbox at /Users/debra/SecondBrain/GTD/inbox.md. Use when asked to "scan for action items", "capture todos", "check for commitments", "run capture agent", or automatically via cron (multiple times per day). Never overwrites — appends only. Deduplicates before writing.
---

# capture-agent

Scan every communication stream Alex touches, extract anything that looks like a commitment or action item, and drop it in the GTD inbox. The inbox is the catch-all; triage happens separately via gsd-agent.

## Inputs

- **sources** (optional): comma-separated list — `email`, `imessage`, `calendar`, `llm`, `scanfolder`, `all` (default: `all`)
- **lookback** (optional): how many hours back to scan (default: `12` for cron, `48` for manual runs)
- **keywords** (optional): extra trigger words to watch for (always includes defaults — see Config)

## Quick Invocation

```
Run capture-agent — scan all sources, last 12 hours, write to GTD inbox.
```

For a manual catch-up:
```
Run capture-agent — sources: all, lookback: 48 hours
```

## Config

Defaults baked in. Edit this file to change them.

| Setting | Default | Notes |
|---------|---------|-------|
| `lookback_hours` | 12 | Hours back to scan in cron mode |
| `lookback_manual` | 48 | Hours back on manual invocation |
| `inbox_file` | `/Users/debra/SecondBrain/GTD/inbox.md` | Append target |
| `scan_folder` | `/Users/debra/SecondBrain/GTD/scan/` | Drop files here to auto-scan |
| `model` | `claude-haiku-3-5` or `gemini-flash` | Cheap model — skim, don't deep-read |
| `email_max_messages` | 30 | Cap on emails pulled per run |
| `imessage_max_chats` | 10 | Cap on chat threads scanned |

**Default trigger keywords** (always active):
`todo`, `action item`, `follow up`, `follow-up`, `remind me`, `don't forget`, `please`, `can you`, `could you`, `will you`, `I'll`, `I will`, `we need to`, `need to`, `deadline`, `by [date]`, `EOD`, `EOW`, `ASAP`, `urgent`, `committed`, `promised`, `owe you`

## Workflow

### 1. Check the Inbox for Existing Items (Deduplication Prep)

Before scanning, read the last 100 lines of the inbox to build a dedup fingerprint list:

```bash
tail -100 /Users/debra/SecondBrain/GTD/inbox.md
```

Extract the core action phrase from each line. Hold in memory for dedup comparison during extraction.

### 2. Scan: Email

```bash
gog gmail list --account alexander.o.abell@gmail.com --max-results 30 --unread
```

For each email:
- Check sender, subject, snippet
- Flag if subject or body contains trigger keywords
- For flagged emails, fetch full body: `gog gmail get --account ... --id [message_id]`
- Extract action items using the extraction prompt (see §Extraction Prompt)
- Source tag: `email:[subject]:[sender]`

Don't read every email deeply. Skim subject + snippet first. Only pull full body if keywords hit.

### 3. Scan: iMessage

```bash
curl -s http://localhost:1234/api/v1/chats?limit=10 | jq '.data[] | {guid: .guid, display_name: .display_name}'
```

For each chat, fetch recent messages:
```bash
curl -s "http://localhost:1234/api/v1/chat/[chat_guid]/message?limit=20&after=[lookback_timestamp]" \
  | jq '.data[] | {text: .text, handle: .handle.id, date: .date_created}'
```

Focus on:
- Messages FROM Alex (his commitments)
- Messages directed TO Alex asking him to do something
- Any message containing trigger keywords

Source tag: `imessage:[contact_name]:[chat_guid_short]`

Known chats to prioritize (from TOOLS.md):
- Jay (boss): `91468caf20824cd696f30436e54c004a`
- Annika (co-parent): `9a04d0b72baf4d03b88b9fddaead4dc3`
- Hannah (girlfriend): `chat284576019517930648`

### 4. Scan: Calendar

```bash
gog calendar list --account alexander.o.abell@gmail.com --days-ahead 3 --days-behind 1
```

For each event in the past 24h (recently completed meetings):
- Extract the event description and attendees
- Look for embedded action items in the description
- For future events: extract any prep tasks mentioned

Source tag: `calendar:[event_title]:[date]`

### 5. Scan: Drop Folder

```bash
ls /Users/debra/SecondBrain/GTD/scan/ 2>/dev/null
```

If files exist, read each one:
```bash
cat /Users/debra/SecondBrain/GTD/scan/[filename]
```

Extract action items from the full text (these are intentionally dropped for processing, so read fully).
After successful extraction, move file to `/Users/debra/SecondBrain/GTD/scan/processed/[filename]`.

Source tag: `file:[filename]`

### 6. Scan: LLM Export (if present)

Look for recent LLM export files:
```bash
ls -t ~/Downloads/*.json ~/Downloads/*.md 2>/dev/null | head -5
ls -t /Users/debra/SecondBrain/GTD/scan/*.json 2>/dev/null
```

If `conversations.json` or similar is present, run a targeted grep before deep-reading:
```bash
grep -i "action item\|todo\|follow up\|remind\|deadline\|I'll\|we need" [file] | head -50
```

Source tag: `llm:[filename]`

### 7. Extraction Prompt

Use a cheap model (Haiku or Gemini Flash). Feed it each source chunk with this prompt:

```
You are extracting action items from a conversation/email/text.

Rules:
- Extract ONLY concrete commitments, todos, follow-ups, and deadlines
- Ignore small talk, observations, and general discussion
- For each item, identify: WHO is responsible, WHAT needs to happen, WHEN (if mentioned), ASSIGNED BY (if applicable)
- Priority: urgent = explicit deadline <48h or "ASAP"; low = vague future; normal = everything else
- Return JSON array, each item: {"action": "...", "assignee": "...", "due": "...", "assigned_by": "...", "priority": "urgent|normal|low"}
- If nothing actionable, return []

TEXT:
[paste chunk here]
```

Keep chunks small (< 2000 chars). Skim, don't dump entire inboxes.

### 8. Write to Inbox

For each extracted item:

1. **Dedup check**: Does the action text closely match anything already in the inbox tail? If yes, skip.
2. **Format the line**:

```markdown
- [ ] [action text] — assigned to: [assignee], due: [due or "not specified"], assigned by: [who], priority: [urgent/normal/low], source: [source_tag], captured: [YYYY-MM-DD HH:MM]
```

3. **Append** to `/Users/debra/SecondBrain/GTD/inbox.md` — never overwrite, always append.

```bash
echo "- [ ] [formatted line]" >> /Users/debra/SecondBrain/GTD/inbox.md
```

### 9. Create Scan Folder if Missing

```bash
mkdir -p /Users/debra/SecondBrain/GTD/scan/processed
```

## Output Summary

After each run, report:

```
📥 Capture complete — [timestamp]
- Email: [N] messages scanned, [N] items extracted
- iMessage: [N] chats scanned, [N] items extracted
- Calendar: [N] events scanned, [N] items extracted
- Drop folder: [N] files processed
- Total new items added to inbox: [N]
- Dupes skipped: [N]
- Inbox: /Users/debra/SecondBrain/GTD/inbox.md
```

If zero items extracted from everything: "All clear — no new action items captured."

## Cron Setup

Recommended schedule (3x daily + overnight catch-up):

```
# Capture agent — 3x daily
0 8,13,18 * * *  openclaw run capture-agent
# Overnight full sweep
0 4 * * *        openclaw run capture-agent --lookback 12
```

Or set up via OpenClaw:
```
Schedule capture-agent to run every 6 hours
```

## Reference Files

- **`references/extraction-examples.md`**: Sample extractions showing good vs. bad captures, edge cases, and tricky patterns (promises vs. observations, questions vs. commitments).
- **`references/source-guide.md`**: API shapes for each source — BlueBubbles response format, gog gmail output, calendar event fields.
