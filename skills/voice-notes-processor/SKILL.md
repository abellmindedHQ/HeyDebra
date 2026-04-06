---
name: voice-notes-processor
description: >
  Voice notes and meeting recording processor. Watches ~/SecondBrain/Imports/voice-notes/
  for audio files, transcribes them with AssemblyAI (speaker diarization, chapters, entities,
  sentiment, action items), saves formatted Obsidian notes to ~/SecondBrain/Meetings/,
  appends action items to the GTD inbox, and moves processed audio to /processed/.
  Use when asked to "process voice note", "transcribe audio", "process meeting recording",
  "check voice notes", or "run voice notes processor".
---

# voice-notes-processor

Transcribe and process voice notes and meeting recordings into structured SecondBrain content using AssemblyAI's full feature suite.

## Triggers

- "process voice note"
- "transcribe audio"
- "process meeting recording"
- "check voice notes"
- "run voice notes processor"
- "transcribe [filename]"
- "what's in my voice notes"

## Requirements

- `ASSEMBLYAI_API_KEY` environment variable set (get one at assemblyai.com)
- Python 3.9+
- `assemblyai` Python package (auto-installed if missing)

## Paths

| Path | Purpose |
|------|---------|
| `~/SecondBrain/Imports/voice-notes/` | Drop folder — put audio files here |
| `~/SecondBrain/Imports/voice-notes/processed/` | Processed audio files moved here |
| `~/SecondBrain/Meetings/` | Generated Obsidian notes |
| `~/.openclaw/workspace/inbox/inbox.md` | Action items appended here |
| `~/.openclaw/workspace/memory/voice-notes-state.json` | Processing state / dedup log |

## Supported Formats

`.m4a`, `.mp3`, `.wav`, `.ogg`, `.webm`, `.mp4`

## Features

AssemblyAI processes each file with:
- ✅ **Best model transcription** (`SpeechModel.best`)
- ✅ **Speaker diarization** (labeled utterances)
- ✅ **Auto chapters** (headline + summary per section)
- ✅ **Entity detection** (people, orgs, locations, dates, etc.)
- ✅ **Sentiment analysis** (per segment + overall)
- ✅ **Auto highlights** (key phrases, used for action item extraction)

## Output

### Obsidian Note (`~/SecondBrain/Meetings/YYYY-MM-DD-filename.md`)

```markdown
---
title: "..."
date: YYYY-MM-DD
time: HH:MM
source_file: recording.m4a
duration: 12m 34s
speakers: ["Speaker A", "Speaker B"]
speaker_count: 2
dominant_sentiment: positive
tags: [voice-note, meeting, transcription]
---

# Title

> 📅 date | ⏱️ duration | 🎙️ speakers

## 📑 Chapters
### 1. Headline
*00:00* — summary

## 📝 Transcript
**Speaker A** _00:00_
> ...

## 😊 Sentiment
- 😊 Positive: 65%
...

## ✨ Key Highlights
- **phrase** (mentioned 3x, rank 0.85)

## 🏷️ Entities
**👤 Person Name:** Alice Smith, Bob Jones
**🏢 Organization:** Acme Corp
...

## 👥 People Mentioned
- [[Alice Smith]]
- [[Bob Jones]]
```

### GTD Inbox (`~/.openclaw/workspace/inbox/inbox.md`)

Action items appended in capture-agent format:
```
- [ ] Follow up with Alice about the proposal — assigned to: Alex, due: not specified, assigned by: voice note, priority: normal, source: voice-note:recording.m4a, captured: YYYY-MM-DD HH:MM
```

## Scripts

### `scripts/process-audio.py`
**Single file processor.** Pass an audio file path; handles transcription, note creation, inbox append, file move, and state update.

```bash
ASSEMBLYAI_API_KEY=your_key python3 scripts/process-audio.py /path/to/recording.m4a
```

### `scripts/process-backlog.py`
**Batch processor.** Scans the drop folder and processes all unprocessed files.

```bash
ASSEMBLYAI_API_KEY=your_key python3 scripts/process-backlog.py

# Dry run (list files without processing):
ASSEMBLYAI_API_KEY=your_key python3 scripts/process-backlog.py --dry-run
```

### `scripts/watch-folder.py`
**Continuous watcher.** Polls the drop folder every 30 seconds and processes new files as they appear.

```bash
ASSEMBLYAI_API_KEY=your_key python3 scripts/watch-folder.py

# Custom poll interval (seconds):
ASSEMBLYAI_API_KEY=your_key python3 scripts/watch-folder.py --poll-interval 60
```

## Agent Workflow

When a user asks to process voice notes, check the API key, then run the appropriate script:

### Manual: process a specific file
```bash
ASSEMBLYAI_API_KEY="$(op item get 'AssemblyAI API Key' --fields credential --reveal 2>/dev/null || echo $ASSEMBLYAI_API_KEY)" \
python3 ~/.openclaw/workspace/skills/voice-notes-processor/scripts/process-audio.py \
  ~/SecondBrain/Imports/voice-notes/recording.m4a
```

### Manual: process all backlog
```bash
ASSEMBLYAI_API_KEY=$ASSEMBLYAI_API_KEY \
python3 ~/.openclaw/workspace/skills/voice-notes-processor/scripts/process-backlog.py
```

### Check what's pending
```bash
ls ~/SecondBrain/Imports/voice-notes/*.{m4a,mp3,wav,ogg,webm,mp4} 2>/dev/null | wc -l
```

### Check state
```bash
cat ~/.openclaw/workspace/memory/voice-notes-state.json
```

## Cron Setup

To run the backlog processor automatically (e.g., every 30 minutes):

```bash
# Add to crontab (crontab -e):
*/30 * * * * ASSEMBLYAI_API_KEY=your_key_here /usr/bin/python3 /Users/debra/.openclaw/workspace/skills/voice-notes-processor/scripts/process-backlog.py >> /tmp/voice-notes-processor.log 2>&1
```

Or for the watcher as a LaunchAgent, create `~/Library/LaunchAgents/com.openclaw.voice-notes-watcher.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.openclaw.voice-notes-watcher</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/Users/debra/.openclaw/workspace/skills/voice-notes-processor/scripts/watch-folder.py</string>
    </array>
    <key>EnvironmentVariables</key>
    <dict>
        <key>ASSEMBLYAI_API_KEY</key>
        <string>YOUR_KEY_HERE</string>
    </dict>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/tmp/voice-notes-watcher.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/voice-notes-watcher.err</string>
</dict>
</plist>
```

## Error Handling

- Missing API key → clear error message, exit 1
- Transcription failure → AssemblyAI error printed, file NOT moved (retry safe)
- File already processed → skipped (state-based dedup)
- Duplicate filename in /processed/ → timestamped suffix added
- Unstable file (still writing) → watcher skips until stable
- assemblyai SDK missing → auto-installed via pip

## API Cost Estimate

AssemblyAI charges per audio hour. With all features enabled, estimate ~$0.37–$0.65/hour of audio (check assemblyai.com/pricing for current rates).
