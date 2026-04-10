# Active Context — April 10, 2026 (Updated 3:36 AM EDT)

## 🔴 BB Attachment Bug — Deep Dive Complete, Still Not Fixed

**Status:** Strongest current theory is intermittent/timing-related webhook attachment population.

**What we know:**
1. `extractAttachments(message)` usually sees an empty array
2. Attachment data appeared once (`attachmentCount=7`), so the path is not fully dead
3. OpenClaw dist patches and debug logging are in place, but they live in built files and are not durable

**Most likely next move:** inspect BB webhook timing/version behavior and compare payload variants to see why attachment metadata is sometimes absent when OpenClaw processes the event.

**Patched files (temporary, overwritten on update):**
- `/opt/homebrew/lib/node_modules/openclaw/dist/monitor-normalize-DBiB1PcA.js`
- `/opt/homebrew/lib/node_modules/openclaw/dist/channel.runtime-BSXlY6sk.js`

---

## Config / Infrastructure State

- Primary model: **openai/gpt-5.4**
- Fallback: `anthropic/claude-haiku-4-5`
- Gateway version: `2026.4.9`
- Gemini API: **DOWN** with `403 PERMISSION_DENIED`
- `web_search` + `memory_search` degraded/unavailable because of Gemini billing/permissions issue
- WhatsApp cycling every ~30 min as expected
- Dream Cycle #10 completed, 8 proposals staged

---

## Schedule

**This morning (Apr 10):**
- Dentist 8:20 AM, East Tennessee Family Dentistry (Deane Hill), (865) 584-8630

**Upcoming:**
- Hannah ultrasound Mon Apr 13
- Student Led Conferences Apr 16
- Lipoma removal Apr 20
- Avie adenoidectomy Apr 22

---

## Active Tasks (Top 5)

1. **🔴 URGENT:** Roxanne NDA, now 34 days stale, tied to ~$8K decision
2. **🔴 URGENT:** ORNL FCU fraud alert, still unresolved
3. **🟠 HIGH:** Runway AI payment failures from evening email triage
4. **🟡 MEDIUM:** Google Cloud billing / Gemini permissions fix
5. **🟡 MEDIUM:** Permanent upstream-safe fix for BB attachment handling

---

## Pending Decisions (Alex)

- Roxanne NDA approval / response
- Gemini billing and API access fix
- Review Dream Cycle proposal backlog

---

## Channel Context

- Pre-4am memory flush completed
- Morning startup should assume continuity from `memory/2026-04-10.md`
- Biggest live blockers at reset: BB attachments, Gemini outage, Roxanne, ORNL FCU

---

**Last updated:** 2026-04-10 03:36 AM EDT by Debra
**Next review:** Morning startup
