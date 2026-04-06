---
name: capture-agent
description: Universal action item extractor. Scans email, iMessage, and calendar for concrete action items. Uses context-aware classification (strict mode for conversational sources, blocks stale LLM exports). Hash-based dedup prevents duplicates across runs. Writes verified items to GTD inbox and auto-promotes to Things 3. Use when asked to "scan for action items", "capture todos", "check for commitments", "run capture agent", or automatically via cron (2x daily). Never overwrites — appends only.
---

# capture-agent

Scan email, iMessage, and calendar for concrete commitments and action items. Uses a **context-aware classification pipeline** with strict filtering for conversational sources (voice notes, meeting transcripts) and automatic blocking of stale LLM export artifacts. Hash-based dedup prevents the same item from appearing twice across runs. Routes verified items to both the GTD inbox AND Things 3.

## Critical Rules (v2)

1. **Voice notes / meeting transcripts**: STRICT mode. Requires action verb + concrete deliverable noun + (deadline OR named person). "I'll send the report to Jay by Friday" passes. "I'll tell you what I think" does not.
2. **LLM exports (ChatGPT, Claude, Gemini)**: BLOCKED from inbox entirely. These are archived for knowledge in SecondBrain, not routed as live tasks. Old conversations are not action items.
3. **Hash-based dedup**: Every item gets fingerprinted. State file at `memory/capture-dedup-state.json` tracks last 2000 items. Same item never appears twice.
4. **Quality over quantity**: 5 real action items > 50 noise items. When in doubt, DON'T add it.

## Inputs

- **sources** (optional): comma-separated list — `email`, `imessage`, `calendar`, `scanfolder`, `all` (default: `all`). NOTE: `llm` source is DISABLED — LLM exports go to SecondBrain archive only, not inbox.
- **lookback** (optional): how many hours back to scan (default: `12` for cron, `48` for manual runs)
- **keywords** (optional): extra trigger words to watch for (always includes defaults — see Config)
- **dry_run** (optional): if true, classify but don't write to inbox or Things 3

## Quick Invocation

```
Run capture-agent — scan all sources, last 12 hours, write to GTD inbox.
```

For a manual catch-up:
```
Run capture-agent — sources: all, lookback: 48 hours
```

## Config

| Setting | Default | Notes |
|---------|---------|-------|
| `lookback_hours` | 12 | Hours back to scan in cron mode |
| `lookback_manual` | 48 | Hours back on manual invocation |
| `dedup_state` | `memory/capture-dedup-state.json` | Hash fingerprints for dedup |
| `inbox_file` | `/Users/debra/.openclaw/workspace/inbox/inbox.md` | Staging area (append target) |
| `scan_folder` | `/Users/debra/.openclaw/workspace/inbox/scan/` | Drop files here to auto-scan |
| `meeting_insights` | `/Users/debra/.openclaw/workspace/inbox/meeting-insights-archive.md` | Non-actionable items route here |
| `classifier_script` | `scripts/classify-item.py` | LLM classification gate |
| `model` | `gemini` (via gemini CLI) | Cheap model for classification |
| `email_max_messages` | 30 | Cap on emails pulled per run |
| `imessage_max_chats` | 10 | Cap on chat threads scanned |

**Default trigger keywords** (always active):
`todo`, `action item`, `follow up`, `follow-up`, `remind me`, `don't forget`, `please`, `can you`, `could you`, `will you`, `I'll`, `I will`, `we need to`, `need to`, `deadline`, `by [date]`, `EOD`, `EOW`, `ASAP`, `urgent`, `committed`, `promised`, `owe you`

## Architecture: The Three-Gate Pipeline

```
Source Scan → Keyword Extraction → HEURISTIC GATE → LLM GATE → inbox.md + Things 3
                                        ↓                ↓
                                    (discard)     (discard or archive)
```

**Gate 1 — Keyword Match** (existing): Scan sources for trigger keywords. This produces CANDIDATES.

**Gate 2 — Heuristic Pre-Filter** (NEW): Fast, no-API-call filter. Rejects:
- Text < 20 characters
- Pure greetings ("hey", "thanks", "ok", "lol", etc.)
- Pure questions under 80 chars
- Social filler ("I'll talk to you later", "I'll see you", "love you")

**Gate 3 — LLM Classification** (NEW): Remaining candidates go to `scripts/classify-item.py` in batches. The LLM determines:
- Is this a concrete, actionable task with a clear owner and outcome? (yes/no)
- Priority: urgent / normal / low
- Assignee: who's responsible
- Due date: if mentioned
- Clean title: concise task description

Items that fail Gate 3 are either discarded or routed to `meeting-insights-archive.md`.

### Classification Examples

| Candidate | Actionable? | Why |
|-----------|------------|-----|
| "I'll talk to you later" | ❌ No | Social filler, no concrete outcome |
| "Yeah that's fair" | ❌ No | Agreement, not a task |
| "We should get together sometime" | ❌ No | Vague, no timeline or outcome |
| "Can you send me the link?" | ❌ No | Simple request, not a tracked task |
| "I'll get those quotes together and send them to you by Friday" | ✅ Yes | Concrete deliverable, deadline, clear owner |
| "Need to schedule Avie's dentist appointment" | ✅ Yes | Concrete task, clear outcome |
| "Follow up with Jay about the budget review" | ✅ Yes | Named person, specific action |
| "ASAP: review the security audit report" | ✅ Yes | Urgent, specific deliverable |

## Workflow

### 1. Dedup Prep

Read the last 100 lines of inbox to build dedup fingerprints:

```bash
tail -100 /Users/debra/.openclaw/workspace/inbox/inbox.md
```

Also check recent Things 3 tasks to avoid duplicating existing items:

```bash
things today --json 2>/dev/null | python3 -c "import sys,json; [print(t['title']) for t in json.load(sys.stdin)]"
things inbox --json 2>/dev/null | python3 -c "import sys,json; [print(t['title']) for t in json.load(sys.stdin)]"
```

### 2. Scan: Email

```bash
gog gmail list --account alexander.o.abell@gmail.com --max-results 30 --unread
```

For each email:
- Check sender, subject, snippet for trigger keywords
- For flagged emails, fetch full body: `gog gmail get --account ... --id [message_id]`
- Extract candidate action items using extraction prompt (see §Extraction Prompt)
- **🗓️ APPOINTMENT DETECTION**: If an email contains appointment/meeting details (date, time, provider/location), also create a calendar event (see §Auto-Calendar below)
- Source tag: `email:[subject]:[sender]`

### 3. Scan: iMessage

**Authentication:** BlueBubbles API requires the server password as a query parameter on every request.
Read it from the OpenClaw config: `grep -m1 '"password"' /Users/debra/.openclaw/openclaw.json | sed 's/.*"password": "//;s/".*//'`
Store in a variable and append `?password=<BB_PASSWORD>` (or `&password=<BB_PASSWORD>` if other params exist) to ALL BB API calls.

```bash
BB_PASS=$(grep -m1 '"password"' /Users/debra/.openclaw/openclaw.json | sed 's/.*"password": "//;s/".*//')
# NOTE: BlueBubbles uses POST /chat/query — GET /chats returns 404
curl -s -X POST "http://localhost:1234/api/v1/chat/query?password=$BB_PASS" \
  -H "Content-Type: application/json" \
  -d '{"limit":20,"offset":0,"with":["lastMessage","participants"]}' \
  | jq '.data[] | {guid: .guid, display_name: .displayName}'
```

For each chat, fetch recent messages (include attachments):
```bash
curl -s "http://localhost:1234/api/v1/chat/[chat_guid]/message?limit=20&after=[lookback_timestamp]&with=attachment&password=$BB_PASS" \
  | jq '.data[] | {text: .text, handle: .handle.id, date: .date_created, attachments: [.attachments[]? | {mime: .mime_type, guid: .guid, transfer_name: .transfer_name}]}'
```

Focus on messages FROM Alex (his commitments) and messages directed TO Alex with requests.

#### 🖼️ Image Attachment Processing

When messages contain image attachments (mime_type starts with `image/`):
1. Download the attachment: `curl -s "http://localhost:1234/api/v1/attachment/[guid]/download?password=$BB_PASS" -o /tmp/capture-img-[guid].jpg`
2. Run vision analysis to extract text/appointment info:
   - Use the `image` tool with prompt: "Extract ALL text from this image. If it contains appointment/scheduling info (dates, times, locations, doctor/provider names, confirmation numbers), return structured data: {is_appointment: true/false, title, date, time, location, provider, notes}. Also extract any action items or commitments."
3. Feed extracted text back into the normal candidate pipeline (keyword matching → classification → inbox)
4. If appointment data found, also route to auto-calendar creation (see §Auto-Calendar)
5. Clean up temp file after processing

**Priority image sources** (most likely to contain appointments/schedules):
- Annika group chat: screenshots of school events, doctor appointments, Avie schedule
- Any chat with medical/provider screenshots (Healow, MyChart, SimplePractice)
- Calendar screenshots, event flyers, invitations

**Skip**: memes, reaction images, photos without text (if vision returns no meaningful text, move on)

#### 🗓️ iMessage → Calendar Events

Apply the SAME appointment detection logic as email scanning (see §Auto-Calendar) to iMessage text AND image-extracted text:

**Text-based triggers in messages:**
- "appointment is at [time]", "tomorrow at [time]", "this [day] at [time]"
- "can you be there", "don't forget", "scheduled for"
- Addresses, doctor names, school event times

**Process:**
1. Extract appointment details from message text or image-extracted text
2. Dedup against existing calendar events (same as email flow)
3. Create calendar event via `gog calendar create`
4. Log: `- iMessage calendar events created: [N]`

Known priority chats (from TOOLS.md):
- Jay (boss): `91468caf20824cd696f30436e54c004a`
- Annika (co-parent): `9a04d0b72baf4d03b88b9fddaead4dc3`
- Hannah (girlfriend): `chat284576019517930648`

Source tag: `imessage:[contact_name]:[chat_guid_short]`

### 4. Scan: Calendar

```bash
gog calendar list --account alexander.o.abell@gmail.com --days-ahead 3 --days-behind 1
```

Extract action items from recently completed meetings and prep tasks for upcoming events.
Source tag: `calendar:[event_title]:[date]`

### 5. Scan: Drop Folder

```bash
ls /Users/debra/.openclaw/workspace/inbox/scan/ 2>/dev/null
```

Read each file, extract candidates, move processed files to `scan/processed/`.
Source tag: `file:[filename]`

### 6. LLM Exports — BLOCKED

**DO NOT scan LLM exports for inbox routing.** The LLM export processor (`night-swimming-llm`) archives these to SecondBrain for knowledge retrieval. Old ChatGPT/Claude/Gemini conversations contain stale "action items" from months ago that pollute the inbox. If source contains `chatgpt`, `claude-export`, `gemini-export`, or `llm-export`, skip entirely.

### 6b. Classification Gate (Heuristic Pre-Filter)

After extracting candidates from any source, run them through the local heuristic classifier before writing to inbox or sending to the LLM gate:

```bash
echo '[{"text": "candidate text", "source": "email:subject:sender"}]' | python3 scripts/classify-item.py --actionable-only
```

The classifier (`scripts/classify-item.py`) runs **locally with zero API calls**:
1. **Length filter**: Rejects items < 20 characters
2. **Greeting filter**: Rejects pure greetings, reactions, filler
3. **Question filter**: Rejects pure questions under 80 chars
4. **Social filler filter**: Rejects "I'll talk to you later", "love you", etc.
5. **Action verb detection**: Looks for concrete verbs (send, call, schedule, buy, fix, review...)
6. **Commitment pattern matching**: Detects "I'll", "I need to", "we need to", "promised", etc.
7. **Area mapping**: Keywords to Things 3 areas (ORNL, Health & Money, Build, People, Life Ops)

**Only write items where `is_actionable: true` to inbox.md.**

For each actionable item, also auto-promote to Things 3:
```bash
things add --title "[action]" --notes "Source: [source_tag]" --when today --area "[area from classifier]"
```

Items where `is_actionable: false` can be:
- Discarded (greetings, filler, too short)
- Routed to meeting-insights-archive.md (if they had some content but no action verb)

This gate runs BEFORE the LLM gate (step 8) and eliminates 60-80% of noise at zero cost.

### 7. Extraction Prompt (Pre-Classification)

Use a cheap model to extract CANDIDATES from each source chunk:

```
You are extracting potential action items from a conversation/email/text.

Rules:
- Extract anything that MIGHT be a commitment, todo, follow-up, or deadline
- Include the full context phrase (not just keywords)
- For each item: {"text": "full phrase", "source": "source_tag"}
- Cast a wide net here — the classifier will filter downstream
- Return JSON array. If nothing found, return []

TEXT:
[paste chunk here]
```

### 8. 🚦 CLASSIFICATION GATE (The Key Step)

Collect ALL candidates from all sources into a single batch. Run through the classifier:

```bash
echo '[candidates_json]' | python3 scripts/classify-item.py
```

The classifier script (`scripts/classify-item.py`) runs:
1. **Heuristic pre-filter**: Rejects greetings, short text, questions, social filler (zero API cost)
2. **LLM classification**: Batches remaining candidates to gemini CLI for yes/no actionability + metadata
3. **Area mapping**: Maps each actionable item to a Things 3 area

Output: JSON array of only actionable items with `priority`, `assignee`, `due`, `area`, `clean_title`.

**If the classifier script is not available**, fall back to inline classification: use the extraction prompt but with stricter rules asking the model to determine actionability. Never skip classification entirely.

### 9. Write to Inbox (Staging)

For each classified actionable item:

1. **Dedup check**: Skip if title closely matches existing inbox or Things 3 items
2. **Format the line**:

```markdown
- [ ] [clean_title] // assigned to: [assignee], due: [due or "not specified"], priority: [priority], source: [source_tag], area: [area], captured: [YYYY-MM-DD HH:MM]
```

3. **Append** to `/Users/debra/.openclaw/workspace/inbox/inbox.md`

### 10. 🎯 Auto-Promote to Things 3

For each actionable item, also create in Things 3:

```bash
things add --title "[clean_title]" --notes "Source: [source_tag]. Captured: [timestamp]" --when today --list "[area]" --tags "[priority]"
```

**Area mapping for `--list` flag:**
| Context Keywords | Things 3 Area |
|-----------------|---------------|
| ORNL, work, meeting, oak ridge | 🏢 ORNL |
| finance, money, insurance, health, doctor, budget, tax | 💊 Health & Money |
| hannah, annika, avie, sallijo, chelsea, merle, birthday | 👨‍👧 People |
| code, build, openclaw, deploy, github, linear, api, skill | 🚀 Build |
| everything else | 🏠 Life Ops |

**Priority tag mapping:**
- `urgent` → `--tags "urgent"`
- `normal` → `--tags "normal"`
- `low` → `--tags "low"`

If `--when` has a specific due date from classification, use that instead of "today".

### 11. Route Non-Actionable Items

Items that fail LLM classification but contain potentially useful context (meeting notes, observations, discussion points) get appended to:

```
/Users/debra/.openclaw/workspace/inbox/meeting-insights-archive.md
```

Format: `- [context snippet] // source: [source_tag], captured: [timestamp]`

This prevents total information loss while keeping the inbox clean.

### 12. 🗓️ Auto-Calendar: Create Events from Appointment Emails

When scanning emails, detect appointment/scheduling patterns:

**Trigger patterns** (subject or body):
- "appointment", "scheduled", "confirmed", "reminder", "booking"
- "your visit", "your session", "telehealth", "video visit"
- Dates + times in structured format (e.g., "April 1, 2026 at 7:00 PM")
- Provider names (doctor, therapist, dentist, etc.)

**Extraction prompt** (add to the email extraction step):
```
Also check: does this email contain a scheduled appointment or meeting?
If yes, extract: {"is_appointment": true, "title": "...", "start": "ISO8601", "end": "ISO8601 or null", "location": "... or 'Video' or null", "description": "provider + any prep notes or links"}
If no clear date/time, set is_appointment: false.
Default duration: 60 minutes if no end time specified.
```

**Dedup against calendar**: Before creating, check existing events:
```bash
gog calendar list --account alexander.o.abell@gmail.com --from [event_date] --to [event_date+1] --plain
```
Skip if a matching event already exists (fuzzy match on title + time within 30 min).

**Create the event**:
```bash
gog calendar create primary --account alexander.o.abell@gmail.com \
  --summary "[title]" \
  --from "[start_iso8601]" \
  --to "[end_iso8601]" \
  --description "[description]" \
  --location "[location if applicable]"
```

**Log it**: Add to the output summary:
```
- Calendar events created: [N] (list titles)
```

### 13. Create Folders if Missing

```bash
mkdir -p /Users/debra/.openclaw/workspace/inbox/scan/processed
```

### 14. 🗑️ Auto-Archive Resolved Emails

After processing, check if any flagged emails have already been resolved (Alex completed the action, payment updated, form submitted, etc.):

1. Cross-reference email action items against:
   - Things 3 completed tasks (`things completed --since yesterday --json`)
   - Recent session context (did Alex say he handled it?)
   - active-context.md for status updates
2. If the action is confirmed complete, archive the email AND any related past notifications:
```bash
gog gmail archive --account alexander.o.abell@gmail.com --id [message_id]
```
3. Search for related older notifications on the same topic and archive those too:
```bash
gog gmail list --account alexander.o.abell@gmail.com --query "from:[sender] subject:[related keywords]" --max-results 10
# Archive any that are clearly about the same resolved issue
```
4. Log: `- Auto-archived: [N] resolved emails ([list subjects])`

**Safety:** Only archive if resolution is CONFIRMED (completed task, Alex explicitly said he did it, or payment confirmation email exists). When in doubt, keep it.

## Output Summary

```
📥 Capture complete — [timestamp]
- Email: [N] messages scanned, [N] candidates found
- iMessage: [N] chats scanned, [N] candidates found
- Calendar: [N] events scanned, [N] candidates found
- Drop folder: [N] files processed

Classification results:
- Heuristic rejected: [N] (greetings, filler, too short)
- LLM rejected: [N] (not actionable)
- Actionable items: [N]
- Dupes skipped: [N]

Routed:
- inbox.md: [N] new items
- Things 3: [N] tasks created
- Meeting insights archive: [N] items
```

If zero actionable items: "All clear. Scanned [N] candidates, nothing actionable."

## Cron Setup

```
# Capture agent — 2x daily (morning + evening)
30 7 * * *   capture-agent (morning sweep)
0 18 * * *   capture-agent (evening sweep)
```

Reduced from 3x to 2x daily. Morning catch catches overnight, evening catches the workday.

## Reference Files

- **`scripts/classify-item.py`**: The LLM classification gate script. Heuristic + LLM pipeline.
- **`references/extraction-examples.md`**: Sample extractions showing good vs. bad captures.
- **`references/source-guide.md`**: API shapes for each source (BlueBubbles, gog gmail, calendar).
