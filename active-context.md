# Active Context — Updated 2026-03-31 3:30am (pre-reset flush)

## Tuesday March 31 Schedule
- **7am**: Lufthansa baggage retry (1-877-234-3449) — DTMF FIX STILL NEEDED
- **Avie**: Little Entrepreneurs Shop at school 11:35am (Rebecca Henderson's class)
- Pack for Boston (flight Thu Apr 2 at 7:30am)

## Wednesday April 1
- Lipoma consult 2:30pm
- Patti appointment 3:30pm
- Chelsea therapy (video, Heart Connected Healing)
- Avie pickup (Sallijo handling)

## Active Projects

### Voice Notes Pipeline
- 12 of 126 Apple Notes voice memos processed (batch running overnight)
- 336 Otter transcripts extracted (2.3GB), not yet imported to Obsidian
- AssemblyAI API key configured from DEBRA vault
- Voice embedding extraction added (resemblyzer)
- Speaker labeling tool built (label-speaker.py)

### Be Particular Book (SECRET)
- Session 1 complete (10 min call with Sallijo)
- Chapter 1 drafted ("Two Words")
- 13-chapter outline written
- 35 topics queued for future sessions
- Cron: every other day at 2pm, texts Sallijo, calls if she responds
- DO NOT mention book to Sallijo or anyone

### SecondBrain People Cards
- 116 people cards rewritten in Wikipedia style
- 7 concept cards extracted
- Relationship map built (eras, tiers, themes)
- Migrated from SecondBrain-OLD to new SecondBrain

### Voice Clones
- Debra clone: working (Chatterbox-TTS, reference from Angie poem)
- Alex clone v2: generated from Otter meeting audio, sent for review
- Voxtral TTS: installed (MLX 4-bit), preset voices only (no clone on Mac)
- Alex wants better clone — needs clean 30s solo recording

### LinkedIn Cleanup
- PAUSED — was archiving real convos (Angelo Nappi incident)
- Smart classifier built (classify-conversations.py)
- Need to run classifier before resuming
- 4,957 conversations in queue, cron DISABLED
- Profile=openclaw (NOT user), Chrome LaunchAgent installed

### Prank Calls
- Marshall Goldman KBUDDS call: SUCCESS (4m43s, hilarious)
- Roxanne coaching call: voicemail (Cloaked AI screener), text sent awaiting reply
- Sallijo stories call: SUCCESS (10m2s, book material)
- Lee Baird call: voicemail, need to text via RCS tomorrow
- ElevenLabs agents created for each

### Contacts
- Marshall Goldman: (865) 306-0896 ✅ FIXED
- Everett Hirche: (865) 250-4862 ✅ FIXED
- Mike Shell: (865) 742-2288 ✅ ADDED
- James Lee Baird: (850) 933-9968 ✅ ADDED
- Jay contacts merged (deleted "Jay ORNL Boss" stub)
- Marshall duplicate deleted
- Merle + Marco SecondBrain files created
- 27 "stub" contacts are NOT empty — gog CLI limitation, data exists on phone

## Infrastructure
- ✅ 1Password DEBRA vault operational
- ✅ Google Messages/RCS bridge (needs restart, tab died)
- ✅ Chrome LaunchAgent for auto-start
- ✅ AssemblyAI pipeline
- ✅ Chatterbox-TTS voice cloning
- ✅ Voxtral TTS (MLX)
- ❌ Neo4j still DOWN
- ❌ Lufthansa DTMF approach broken
- ⚠️ Gemini search quota hitting 429s (3rd dream cycle in a row)

## Pending Decisions (Need Alex)
- Batman v6 frame selection (contact sheets sent)
- Apple Notes export approach for iCloud contacts (gog CLI limitation)
- 22 dream cycle proposals pending review
- LinkedIn classifier: run it?
- Voice clone quality: Alex needs to send 30s recording
