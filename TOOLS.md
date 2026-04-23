# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

### Debra's Android Phone (Samsung Galaxy A10e)
- Number: (865) 287-0278 / +18652870278
- Carrier: Mint Mobile (trial)
- Use for: WhatsApp, Google Messages RCS/SMS, 2FA
- Lives plugged in next to Mac mini on wifi
- This is Debra's "real" phone number

### Google Voice
- Number: (865) 309-5235 / +18653095235
- Linked to Alex's phone (+18135343383)
- Account: alexander.o.abell@gmail.com
- Use for: backup number, 2FA overflow

### Tailscale
- Account: alexander.o.abell@gmail.com
- Mac mini: 100.124.139.13 (debras-mac-mini-1)
- iPhone: 100.107.105.126 (iphone172) — offline since Apr 4
- Daemon: Homebrew-managed (`brew services start tailscale`), GUI app is just a frontend
- ⚠️ Gateway bind is currently `loopback` — NOT accessible via tailnet. Change `gateway.bind` to `tailnet` in openclaw.json to expose over tailnet.
- Old `debras-mac-mini` entry (100.69.97.27) was removed from tailnet admin on Apr 12

### ⚠️ Claude Code git reset Bug (Learned 2026-03-29)
- Claude Code v2.1.87 silently runs `git reset --hard origin/main` every ~10 min
- This DESTROYS uncommitted changes to tracked files
- Untracked files and git worktrees are immune
- ALWAYS: commit frequently when using Claude Code, verify CC version
- Use git worktrees for isolation on important repos
- Monitor: https://github.com/anthropics/claude-code/issues/40710

### Chrome Remote Debugging (Learned 2026-03-30)
- Chrome 136+ BLOCKS `--remote-debugging-port` on the default user data dir
- `profile=user` will NEVER work for browser automation. Use `profile=openclaw` instead
- OpenClaw browser has its own data dir at ~/.openclaw/browser/openclaw/user-data
- LinkedIn is logged in on the openclaw profile
- LaunchAgent installed: com.openclaw.browser.plist (auto-starts OpenClaw Chrome on boot)

### 1Password / sudo

- 1Password CLI (`op`) v2.33.0 installed, desktop app integration enabled
- Account: alex@abellminded.com on my.1password.com
- Vault: Personal
- Mac password item: "Debra's Mac Mini Login" (field: password)
- sudo pattern: `op item get "Debra's Mac Mini Login" --fields password --reveal | sudo -S <command>`
- ALWAYS run `op` commands inside a tmux session (fresh socket per use)
- ALWAYS text Alex before running sudo commands

### TTS / ElevenLabs
- My voice: voice_id `w6INrsHCejnExFzTH8Nm` (custom Debra voice)
- Use this for ALL voice messages
- Built-in `tts` tool now configured with full ElevenLabs config and sends playable voice memos
- For manual generation, use curl to ElevenLabs API with model eleven_multilingual_v2, stability 0.35, similarity 0.85

### ElevenLabs / TTS Pronunciation
- "Sallijo" → write as "Sally Jo" in TTS text (ElevenLabs mispronounces the spelled version)
- Always spell correctly in written messages, use phonetic spelling only for voice generation

### Linear
- API key stored (created Mar 22, 2026, "Debra Assistant", full access)
- Workspace: Abellminded (linear.app/abellminded)
- GraphQL API endpoint: https://api.linear.app/graphql

### ⚠️ Alex BB Account — DISABLED (DO NOT ENABLE)
- Alex BB account (localhost:1235) was enabled briefly on 3/29
- PROBLEM: OpenClaw treated incoming messages as conversations and REPLIED through Alex's iMessage, leaking internal commentary to Alex's contacts (Omar Shaheen incident)
- There is NO read-only/sendPolicy option in BB account config
- DO NOT re-enable until OpenClaw adds a sendPolicy:disabled feature or we build a polling-based scanner instead
- The correct approach for scanning Alex's iMessages: poll the BB API directly on a schedule, don't use the webhook/session model

### Contact Sync Rule
- ALWAYS create/update contacts on BOTH accounts:
  - alexander.o.abell@gmail.com (Alex's primary)
  - drdebrapepper@gmail.com (Debra's address book)
- When enriching a contact, mirror changes to both

### Google Contacts Lookup
- **ALWAYS search by NAME first**, not phone number
- `gog contacts search` does NOT fuzzy-match phone numbers (formatting differences like "+1 (229) 834-9204" vs "2298349204" will miss)
- If you have a phone number but no name, search for partial area code or use `gog contacts list --max 500 --json` and grep
- For incoming unknown numbers: check area code context (229=Valdosta/South GA, 865=Knoxville, 813=Tampa, 615=Nashville)

### BlueBubbles

- Server: localhost:1235 (same machine)
- Group chats: open policy, requireMention for unknown groups
- ⚠️ **Attachment bug (CONFIRMED — awaiting upstream fix):** Inbound iMessage images are silently dropped. Two bugs: (1) `mediaPaths is not defined` ReferenceError — fixed by 2026.4.11 restart. (2) SSRF guard blocks all attachment downloads from localhost/private IPs — fix is on OpenClaw `main` (commits 7d93970, dd41a78) but NOT in any release as of 2026.4.11. The `allowPrivateNetwork` config key does nothing (schema rejects it). Monitor releases or try `openclaw@next`. See memory/bluebubbles-attachment-bug.md for full diagnostic.
- Known chats (auto-discovered from BB API, keep updated):
  - Hannah (Alex+Hannah): any;+;chat284576019517930648 | +16158101319
  - Chelsea (Alex+Chelsea): any;+;a96e1f6eaaba404abd15b7b1a1a1cdea | +16159745363
  - Sallijo (Alex+Mom): any;+;93ad04d9a3a349b3b6f506025d691001 | +12292247731
  - Annika (Alex+Annika): any;+;9a04d0b72baf4d03b88b9fddaead4dc3 | +18479220634
  - Jay (Alex+Boss): any;+;91468caf20824cd696f30436e54c004a | +19014884890
  - Angie (Alex+Angie ORNL): any;+;d4333767f9534f77ab1356e31263b030 | +18653358853
  - Roxanne (Alex+Sister): any;+;80e5f82469ec473bb4f627ea599aff04 | +17063402692
  - Brandon Bruce (Alex+Brandon): any;+;2e9da308ff6d4eaaa3d5377dc45c2270 | +18657890127
  - Brad Greenfield (Alex+Brad): any;+;a6c108054d66442e81bf09d56a1205c6 | +19313202403
  - Marshall Goldman (Alex+Marshall): any;+;2db16e0c2fb7441c9237aa7693d43354 | +18653060896
  - Jim Biggs (Alex+Jim): any;+;5665413a1cdd4931a5b9c90de92a9442 | +14153854794
  - Jason Patrick (Alex+Jason): any;+;68815c5f87cd4ca6be5d858362301d38 | +18657769277
  - Nick Hollensbe (Alex+Nick): any;+;157a6e892de64215addb31a37d051b60 | +12392489353
  - Merle Benny (Alex+Merle): any;+;ecbda845b6444c06a27cd6ff09561ab8 | +19735107652
  - Anthony Caccese (Alex+Anthony): any;+;dccab0976b7a4fda947f7511b0e894a4 | +19177976550
  - Pooja (Alex+Pooja): any;+;6de2840aad1545bd92ef14a922597596 | +18133682433
  - KBUDDS (Alex+Marshall+Everett): any;+;26496e31a52b4d7091da7b17a5a1380d
  - Family (Alex+Hannah+Sallijo): any;+;63d1dbe0006d46abbc3aa07a4fb38c8b
  - Boston Group (Alex+Hannah+Marshall+Everett+Teal): any;+;4f2f085160984776b670fa9624a8560f
  - Unknown +12298349204 group: any;+;2860f2e3259a413caf773b3bee24ff81
  - Unknown +12298349204 direct: any;+;c4d604f1e18c4ccaa3347f3dc0677a4c
  - Unknown +14234807506: any;+;3c6168b0319e4494bec54f0dfefd1c2b
  - Tyler Fogarty (Alex+Tyler): any;+;2720177a61404fa0b516166434b09136 | +18654146145

### Monarch
- API docs: https://status.monarch.com/public-api
- Needs: API key setup
- Use for: transaction monitoring, budget alerts, financial summaries

### YNAB
- API docs: https://api.ynab.com/
- Needs: API key (Personal Access Token from app.ynab.com/settings)
- Use for: budget tracking, category monitoring, spending alerts

### Vercel
- abellminded.com deployed on Vercel
- DNS pointed from Netlify to Vercel
- Used with v0 for rapid prototyping

### Suno
- Music generation (manual, Alex generates tracks)
- Debra voice profile saved in memory for Suno prompts

### QMD (Quick Markdown Search)
- Version: 2.0.1
- Index: ~/.cache/qmd/index.sqlite (46MB)
- 1,321 files indexed, 9,634 vectors embedded
- Models: embeddinggemma-300M (328MB), qmd-query-expansion-1.7B (1.2GB)
- Reranker model (Qwen3 0.6B, 639MB): still downloading, use `vsearch` until complete
- Collections:
  - `people` → ~/SecondBrain/People (116 files)
  - `projects` → ~/SecondBrain/Projects (22)
  - `concepts` → ~/SecondBrain/Concepts (31)
  - `areas` → ~/SecondBrain/Areas (7)
  - `gtd` → REMOVED (GTD inbox moved to ~/.openclaw/workspace/inbox/)
  - `journal` → ~/SecondBrain/Journal (11)
  - `reflections` → ~/SecondBrain/Reflections (369)
  - `meetings` → ~/SecondBrain/Meetings (492)
  - `conversations` → ~/SecondBrain/Conversations (211)
  - `debra-memory` → ~/.openclaw/workspace/memory (50)
  - `health` → ~/SecondBrain/Health (3)
  - `resources` → ~/SecondBrain/Resources (5)
- Search hierarchy: memory_search (workspace, fast) → qmd (vault-wide, semantic) → Neo4j (graph/relationships)
- Commands: `qmd search` (BM25 keyword), `qmd vsearch` (semantic), `qmd query` (hybrid+rerank, needs reranker model)
- Cron: daily re-index at 4am ET (last run: Apr 19, 2432 chunks / 356 docs, 2m53s)
- Use `-c <collection>` to scope searches to specific collections

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.

### Twilio
- Account email: alexander.o.abell@gmail.com
- Recovery code: REDACTED_TWILIO_RECOVERY
- Password: stored in session (will save to 1Password)
- Use for: HoldPlease phone agent, outbound calls

### Home Assistant
- URL: http://homeassistant.local:8123 (local IP: 192.168.4.190 — changed from .189)
- Running on: HA Green (ARM, low power). Migration to Docker on Mac Mini planned.
- Username: abellminded
- API Token: stored in 1Password as "Home Assistant Access Token" (vault: DEBRA, field: credential)
- Token retrieval: `op item get "Home Assistant Access Token" --vault DEBRA --fields credential --reveal`
- **Must use tmux for op commands** (hangs in direct exec)
- Version: 2025.11.3, 197 components loaded
- Devices: Philips Hue (49 lights), LG OLED 65" + projector (Nebula 4K), Nest speakers/hubs (every room), Samsung TV, SwitchBot (NOT YET in HA), Ecobee (NOT YET), Govee (NOT YET)
- Speakers: living room, bedroom display, kitchen display, office, hallway, bathroom, Avie's room, Nest Audio, Nest Hub, Nest Hub Max, Nest Mini
- Voice: ElevenLabs TTS working via Cast. Pass voice option: `"options": {"voice": "w6INrsHCejnExFzTH8Nm"}`
- Also has: Faster Whisper STT, OpenWakeWord, ESPHome, HA Voice Preview Edition (unplugged), Google Generative AI Conversation
- Google Home now uses Gemini (not Google Assistant). "Ask Home Assistant" broken. Opt out via Profile → Public Preview → Leave.
- Projector: Nebula 4K — bedroom primary, portable for rooftop movie nights
- Missing/broken: SwitchBot blinds integration, Ecobee, Govee, several unavailable entities
- Low batteries: bedroom dimmer 20%, living room dimmer knobs 20%, Hue switch 15%
