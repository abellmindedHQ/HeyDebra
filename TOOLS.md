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

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.
