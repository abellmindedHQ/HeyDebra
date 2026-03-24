# Source Guide — API Shapes & Field Reference

## Email (gog gmail)

### List messages
```bash
gog gmail list --account alexander.o.abell@gmail.com --max-results 30 --unread
```

Output fields: `id`, `threadId`, `subject`, `from`, `date`, `snippet`

### Fetch full message
```bash
gog gmail get --account alexander.o.abell@gmail.com --id [message_id]
```

Output fields: `id`, `subject`, `from`, `to`, `date`, `body` (plain text)

**Extraction strategy:**
1. Scan `snippet` for trigger keywords first
2. Only fetch full body if keywords hit
3. Focus on: body paragraphs containing "I will", "please", "action", "deadline", "by [date]"
4. Ignore: auto-generated footers, unsubscribe links, quoted email history (look for `>` prefixes)

**Source tag format:** `email:[subject_first_40_chars]:[from_domain]`

---

## iMessage (BlueBubbles API)

### List recent chats
```bash
curl -s "http://localhost:1234/api/v1/chats?limit=10" \
  -H "Content-Type: application/json"
```

Response shape:
```json
{
  "status": 200,
  "data": [
    {
      "guid": "chat284576019517930648",
      "display_name": "Hannah",
      "participants": [{"handle": {"id": "+16158101319"}}],
      "last_message": {"text": "...", "date_created": 1234567890000}
    }
  ]
}
```

### Fetch messages from a chat
```bash
curl -s "http://localhost:1234/api/v1/chat/[guid]/message?limit=20" \
  -H "Content-Type: application/json"
```

Response shape:
```json
{
  "data": [
    {
      "guid": "message-guid",
      "text": "Can you pick up Avie on Thursday?",
      "handle": {"id": "+16158101319"},
      "is_from_me": false,
      "date_created": 1234567890000
    }
  ]
}
```

**Filtering by time:**
- `date_created` is in milliseconds since epoch
- Lookback 12h: `after = (Date.now() - 12*3600*1000)`
- Or: `curl -s "http://localhost:1234/api/v1/chat/[guid]/message?limit=20&after=[ms_timestamp]"`

**Extraction strategy:**
- `is_from_me: true` → Alex's commitments (high value)
- `is_from_me: false` → requests made TO Alex (capture as assigned-to-Alex)
- Extract the handle ID and map to known contacts (see TOOLS.md)

**Source tag format:** `imessage:[display_name]:[last_6_of_guid]`

**Known priority chats:**
| Name | GUID | Why |
|------|------|-----|
| Jay (boss) | `91468caf20824cd696f30436e54c004a` | Work commitments |
| Annika | `9a04d0b72baf4d03b88b9fddaead4dc3` | Co-parenting commitments |
| Hannah | `chat284576019517930648` | Personal commitments |
| Brad Greenfield | `a6c108054d66442e81bf09d56a1205c6` | Professional |

---

## Calendar (gog calendar)

### List events
```bash
gog calendar list --account alexander.o.abell@gmail.com --days-ahead 3 --days-behind 1
```

Output fields: `id`, `summary` (title), `description`, `start`, `end`, `attendees`, `location`

**Extraction strategy:**
- Scan `description` for action items (often added in notes: "Action items: ...")
- For past events (<24h ago): extract what was decided / assigned
- For future events (<72h): extract any prep tasks in the description
- Check `attendees` — if Jay is in the attendees, weight the meeting higher

**Date handling:**
- `start.dateTime` is ISO 8601: `2026-03-24T10:00:00-04:00`
- Past events = `start.dateTime` < now → mine for action items
- Future events = `start.dateTime` > now → mine for prep tasks

**Source tag format:** `calendar:[event_summary_first_30_chars]:[start_date]`

---

## Drop Folder

**Path:** `/Users/debra/SecondBrain/GTD/scan/`
**Processed:** `/Users/debra/SecondBrain/GTD/scan/processed/`

Accepted file types: `.md`, `.txt`, `.json` (for LLM exports)

For `.json` (LLM exports): look for `mapping` (ChatGPT) or `messages` arrays, extract `content` fields.
For `.md` / `.txt`: read full text, run extraction prompt on the whole thing.

After processing:
```bash
mv /Users/debra/SecondBrain/GTD/scan/[filename] /Users/debra/SecondBrain/GTD/scan/processed/[filename]
```

**Source tag format:** `file:[filename]`

---

## Timestamp Reference

All captured items use local Eastern time: `YYYY-MM-DD HH:MM EDT`

Convert BlueBubbles timestamps (ms epoch) to human date:
```bash
date -r $((timestamp_ms / 1000)) "+%Y-%m-%d %H:%M"
```
