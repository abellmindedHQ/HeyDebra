# Archived Lessons & Details (moved from MEMORY.md 2026-04-01)

## Technical Lessons (reference when needed, not loaded every session)

### Weaver/Zettelkasten (2026-03-24)
- Short entity names (<5 chars) require exact case match to avoid false wikilinks
- Always test skills manually before scheduling crons
- Build → Run → QA → Fix → THEN schedule

### Weaver Concept Card Quality (2026-03-29)
- Weaver auto-generates STUB cards with placeholder text
- 20/21 concept cards were empty stubs before we fixed them
- Future: Weaver should generate real content or flag stubs for review

### Google Contacts API (2026-03-24)
- Rate limits aggressively on deletes (429 after ~50-100)
- Use batchDeleteContacts API for bulk operations (500 per request)
- Always verify web research phone/email against Google Contacts (source of truth)

### Kroger Rate Limiting
- Don't spam rapid-fire searches/adds. Space out requests.

### BlueBubbles Webhook (2026-03-24)
- Use **127.0.0.1** not localhost in BB webhook URL
- BB proxy must be set to **"lan-url"** through UI
- After gateway restarts, BlueBubbles needs restart too
- BB UI overrides sqlite config on restart

### Voice Messages in iMessage (2026-03-28)
- Native iMessage voice bubbles from OpenClaw: BROKEN (GitHub #33377)
- Workaround: send mp3 as audio attachment
- Wait for upstream OC fix

### Git Security (2026-03-28)
- NEVER commit API keys, tokens, or passwords to git
- Use .env files (gitignored) + 1Password for all secrets
- git-filter-repo can scrub secrets from entire history
- GitHub push protection blocks pushes containing secrets

### ElevenLabs Conversational AI (2026-03-28)
- Native Twilio integration: import number + SID + token, assign agent
- Agent can't send DTMF tones. IVR navigation via speech only
- Transcript only available after call ends
- Cost: ~$0.12/min. Hold time = same cost (bad for long holds)
- Hybrid approach: cheap Twilio hold detection → switch to ElevenLabs on human detect
- Debra agent: agent_5201kmtfqfv9etgtafvgw16pjpza, phone: phnum_6601kmtfr2scffj9rv4fb7fcfrtj
- Avery agent: agent_4801kmvj9ffmfwf9vymzafkj4nm2, voice: l9irhEnWKSUzVNW28WNn

### ElevenLabs Prank Call Lessons (2026-03-30)
- dynamic_variables first_message does NOT override agent default greeting. Create NEW agents per call.
- Agents talk to voicemail/IVR forever unless told not to. Add rules.
- Keep prompts focused on SHORT responses and LISTENING
- Created agents: Debra KBUDDS (Marshall), Debra Coaching (Roxanne), Debra Stories (Sallijo), Debra Lee Baird

### v0 API (2026-03-29)
- v0 SDK + REST API both work for programmatic design generation
- API key in 1Password as "v0 API Key"
- v0 credits are SEPARATE from Vercel Pro subscription
- Use node v0-sdk for reliable results

### AI Image Consistency (2026-03-29)
- Basic Flux has ZERO character memory between generations
- For consistent characters: Flux Kontext, LoRA fine-tuning, or Instant Character (all fal.ai)
- Never brute-force character consistency with prompts alone

### Obsidian Sync (2026-03-25)
- Files created programmatically may not trigger Obsidian Sync
- Touch files after creation to force FSEvents
- Large imports can cause sync backlog

### Voice Notes: AssemblyAI vs Whisper (2026-03-31)
- AssemblyAI credits depleted after ~120 files
- OpenAI Whisper API works as fallback (25MB limit)
- Files over 25MB: compress with ffmpeg to mono 16kHz 32kbps MP3
- Corrupted m4a files (missing moov atom) are unrecoverable

### ChatGPT Re-Import Pipeline (2026-03-31)
- Personal: 135 convos, ORNL: 211 convos processed via GPT-4o API
- Scripts: scripts/chatgpt-reimport.py and scripts/chatgpt-ornl-reimport.py
- State files prevent re-processing
- Wikilink normalization needed after each run

### VisionClaw / Ray-Ban Meta (2026-03-30)
- Repo: VisionClaw/ in workspace
- iOS + Android app for Meta Ray-Ban smart glasses
- Streams camera + mic to Gemini Live via WebSocket → delegates to OpenClaw
- Session key: agent:main:glass
- Next: Alex needs Xcode build to iPhone, enable Developer Mode in Meta AI app

### ORNL: SEEK
- Rebuilt from original enterprise search ("Search Sucks")
- Knowledge management problem > search technology problem

### System Text Leak Prevention (2026-03-25)
- Internal system notes CAN leak into outbound messages (Jim Biggs incident)
- NEVER include meta-commentary in chat messages

### Restaurant/Venue Verification (2026-03-25)
- ALWAYS verify a restaurant still exists before recommending
- Check hours match the use case
- Verify phone numbers via Google Places API
