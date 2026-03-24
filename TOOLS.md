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
- Mac mini: 100.69.97.27 (debras-mac-mini)
- iPhone: 100.107.105.126 (iphone172)
- OpenClaw accessible at: http://debras-mac-mini:18789 from any tailnet device

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

### BlueBubbles

- Server: localhost:1234 (same machine)
- Group chats: open policy, requireMention for unknown groups
- Known groups:
  - Hannah: chat_guid:any;+;chat284576019517930648
  - Chelsea: chat_guid:any;+;a96e1f6eaaba404abd15b7b1a1a1cdea
  - Sallijo (mom): chat_guid:any;+;93ad04d9a3a349b3b6f506025d691001
  - Brandon Bruce: chat_guid:any;+;2e9da308ff6d4eaaa3d5377dc45c2270
  - Annika: chat_guid:any;+;9a04d0b72baf4d03b88b9fddaead4dc3
  - Jay (boss): chat_guid:any;+;91468caf20824cd696f30436e54c004a
  - Brad Greenfield: chat_guid:any;+;a6c108054d66442e81bf09d56a1205c6

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

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.
