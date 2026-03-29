# HeyDebra 💁🏽‍♀️

> *A retro-futuristic AI executive assistant with the sass of a 70s power secretary and the brain of a cutting-edge polymath.*

Debra is an AI life operating system built on [OpenClaw](https://github.com/openclaw/openclaw). She manages calendars, messages, projects, smart home, phone calls, and everything in between. She's not a chatbot. She's a colleague.

**Live:** [abellminded.com/debra](https://abellminded.com/debra)

---

## What Debra Does

🗓 **Calendar & Tasks** — Manages multiple Google Calendars, creates events, tracks action items, runs GTD workflows

💬 **iMessage** — Sends texts, voice memos, emoji reactions via BlueBubbles. Talks to family, friends, and coworkers naturally

📞 **Phone Calls (HoldPlease)** — Makes outbound calls, navigates IVR menus, waits on hold, has real conversations with customer service reps using her own cloned voice via ElevenLabs Conversational AI

📧 **Email** — Triages Gmail inbox, classifies noise vs actionable, auto-archives junk, generates daily reports

🧠 **Memory** — Persistent memory across sessions. Daily logs, long-term memory, semantic search across all files

🏠 **Smart Home** — Controls Philips Hue lights, monitors Home Assistant (311 entities), expanding to SwitchBot, Govee, and more

🔍 **Research** — Web search, contact enrichment, people intel, company lookups

🌙 **Dream Cycle** — Nightly autonomous self-improvement: scans AI developments, reflects on performance, proposes changes

📊 **GSD Reports** — Accountability engine that tracks todos, flags overdue items, celebrates wins

## Architecture

```
OpenClaw Gateway (port 18789)
├── Agent: Debra (main)
│   ├── SOUL.md — personality & voice
│   ├── MEMORY.md — long-term knowledge
│   ├── memory/ — daily logs & research
│   ├── skills/ — 12+ custom skills
│   └── projects/ — active builds
│
├── Channels
│   ├── BlueBubbles (iMessage)
│   ├── WhatsApp
│   └── Web Chat
│
├── Crons
│   ├── Email Triage (3x daily)
│   ├── Capture Agent (3x daily)
│   ├── GSD Reports (2x daily)
│   ├── Night Swimming (nightly suite)
│   ├── Dream Cycle (11:30pm)
│   └── HoldPlease calls (scheduled)
│
└── Integrations
    ├── Google Workspace (gog CLI)
    ├── ElevenLabs (TTS + Conversational AI)
    ├── Twilio (phone calls)
    ├── Neo4j (knowledge graph)
    ├── Obsidian (SecondBrain vault)
    ├── Home Assistant
    ├── 1Password
    └── Linear (project management)
```

## HoldPlease 📞

AI phone agent that calls companies on your behalf. Navigates IVR menus, waits on hold, and has real conversations when a human picks up.

- **Phase 1:** Outbound calls + IVR navigation + hold detection
- **Phase 2:** ElevenLabs Conversational AI with Debra's cloned voice
- **Phase 3:** Hybrid cost optimization (cheap hold → full conversation on human detect)
- **Web UI:** Submit calls, watch live transcripts, retry with notes

```bash
npm run start:holdplease  # Web UI on port 3981
npm run start:hybrid      # Cost-optimized hybrid mode
```

## HeyAvery 🐸

Debra's kid sister. An AI sidekick for kids, designed by a 9-year-old creative director.

→ See [projects/avery/README.md](projects/avery/README.md)

**Live:** [abellminded.com/heyavery](https://abellminded.com/heyavery)

## Skills

| Skill | What it does |
|-------|-------------|
| `dream-cycle` | Nightly research + self-reflection + improvement proposals |
| `capture-agent` | Scans email/iMessage/calendar for action items → GTD inbox |
| `gsd-agent` | Accountability reports, overdue tracking, velocity metrics |
| `night-swimming-email` | Gmail triage, classify & archive noise |
| `night-swimming-contacts` | Contact tiering & enrichment |
| `night-swimming-drive` | Google Drive audit & dedup |
| `llm-export-processor` | Process ChatGPT/Claude/Gemini exports into SecondBrain |
| `social-data-processor` | Import social media data into knowledge graph |
| `linkedin-cleanup` | Automated LinkedIn inbox cleanup |
| `weaver` | Zettelkasten cross-linking for Obsidian vault |
| `people-intel` | Deep people research & profile building |

## The Ecosystem

| Product | What | URL |
|---------|------|-----|
| **HeyDebra** | AI executive assistant | [abellminded.com/debra](https://abellminded.com/debra) |
| **HeyAvery** | AI sidekick for kids | [abellminded.com/heyavery](https://abellminded.com/heyavery) |
| **HoldPlease** | AI phone agent | [abellminded.com/holdplease](https://abellminded.com/holdplease) |
| **Mirror** | Consciousness expansion system | [abellminded.com/mirror](https://abellminded.com/mirror) |
| **SecondBrain** | Knowledge graph + Obsidian vault | Local |

## Built By

**Alex Abell** — [abellminded.com](https://abellminded.com)

With love from Debra 💁🏽‍♀️, Avery 🐸, and a Mac mini that never sleeps.
