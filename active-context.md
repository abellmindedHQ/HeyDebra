# Active Context — April 10, 2026 (Updated 3:30 AM EDT)

## 🔴 BB Attachment Bug — Deep Dive Complete, Not Yet Fixed

**Status:** Root cause narrowed to TWO issues:
1. `extractAttachments(message)` returns empty array — `message.attachments` exists as a key but contains no data
2. When attachments DO populate (intermittent — 7 appeared once at 14:05), download code fires but results may not reach session

**What was done Apr 9:**
- Patched `monitor-normalize-DBiB1PcA.js` line 934 with fallback (`?? payload`)
- Patched `channel.runtime-BSXlY6sk.js` line 2108 to attach mediaPaths to message before enqueue
- Added debug logging at line 1357 (baseUrl/password/attachmentCount)
- Added WARNING logging when message.attachments is undefined vs empty
- Registered sniffer webhook in BB's SQLite database (port 18791)
- **Key finding:** `attachmentCount=0` on most sends, but `attachmentCount=7` appeared once — intermittent

**Next step:** Need to understand WHY attachments array is sometimes empty. May be a BB timing issue (webhook fires before attachment processing completes). Check BB server version and webhook dispatch timing.

**Files modified (will be overwritten on `npm update`):**
- `/opt/homebrew/lib/node_modules/openclaw/dist/monitor-normalize-DBiB1PcA.js`
- `/opt/homebrew/lib/node_modules/openclaw/dist/channel.runtime-BSXlY6sk.js`

---

## Config Changes Made Apr 9

- **Primary model switched to openai/gpt-5.4** (was anthropic/claude-sonnet-4-6)
- Fallback: anthropic/claude-haiku-4-5
- OpenAI auth profile added: openai:default (api_key mode)

---

## Schedule

**TODAY (Apr 10):**
- Dentist 8:20 AM, East Tennessee Family Dentistry (Deane Hill), (865) 584-8630

**Upcoming:**
- Hannah ultrasound Mon Apr 13
- Student Led Conferences Apr 16
- Lipoma removal Apr 20
- Avie adenoidectomy Apr 22

---

## Active Tasks (Top 5)

1. **🔴 URGENT:** Roxanne NDA — 34 days stale, $8K decision, she's family
2. **🔴 URGENT:** ORNL FCU fraud alert — still unresolved
3. **🟠 HIGH:** Runway AI payment failures (5 emails)
4. **🟡 MEDIUM:** Google Cloud billing — project suspension risk
5. **🟡 MEDIUM:** Top up Gemini API credits — web_search + memory_search both DOWN

---

## Infrastructure

- Gateway: 2026.4.9, model openai/gpt-5.4
- Gemini API: **DOWN** (403 PERMISSION_DENIED) — blocks web_search AND memory_search
- WhatsApp: cycling every 30 min (normal keepalive)
- BB: localhost:1234, patched webhook handler (debug logging active)
- Dream Cycle #10: Complete, 8 proposals staged, morning iMessage delivered

---

## Pending Decisions (Alex)

- Roxanne NDA approval ($8K)
- Gemini API key refresh / Google Cloud billing
- Review 8 dream cycle proposals (13+ total backlog)
- Muse Luncheon guest name (may be moot now)

---

**Last updated:** 2026-04-10 03:30 AM EDT by Debra
**Next review:** Morning startup
