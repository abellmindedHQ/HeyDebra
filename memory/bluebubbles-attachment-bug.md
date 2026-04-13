# BlueBubbles Attachment Bug — Diagnostic Report

**Status:** 🔴 CONFIRMED UPSTREAM BUG — Fix on `main` but NOT in any release (as of 2026.4.11)  
**Date Identified:** 2026-04-09  
**Updated:** 2026-04-12 (definitive root cause confirmed)  
**Severity:** HIGH — All inbound iMessage images silently dropped  
**Workaround:** Polling script (see below) OR wait for next OpenClaw release

---

## Root Cause (Definitive)

**Two stacked bugs:**

### Bug 1: `mediaPaths is not defined` (ReferenceError)
- Present in BB plugin webhook handler (`channel.runtime-BSXlY6sk.js`)
- Caused every webhook with attachments to crash with `[plugins] plugin http route failed (bluebubbles): ReferenceError: mediaPaths is not defined`
- **Fixed** by OpenClaw 2026.4.11 update + gateway restart (no longer appears after 11:27 AM Apr 12)

### Bug 2: SSRF Guard Blocks Attachment Downloads (THE REAL BLOCKER)
- After Bug 1 is fixed, messages get through but **media files are never downloaded**
- The `fetchRemoteMedia()` function applies strict SSRF policy that blocks `127.0.0.1` and all RFC1918 IPs
- Zero download errors logged — the download simply doesn't execute
- Agent generates `tool-attachments/image-1-<uuid>.png` references but the file is never written
- **Error:** `[tools] image failed: Local media file not found: /Users/debra/.openclaw/media/tool-attachments/image-1-*.png`

### Upstream Fix Status
- **GitHub Issues:** #34749, #26831, #24457, #24948
- **Fix commits:** `7d9397099b` and `dd41a78` (merged to `main`)
- **Fix approach:** Auto-allowlist the configured BB `serverUrl` hostname for SSRF policy
- **NOT in any release** as of 2026.4.11. Monitor releases for inclusion.

### Why `allowPrivateNetwork` Config Doesn't Work
The BB plugin manifest has `configSchema: { type: "object", additionalProperties: false, properties: {} }`. Any custom config keys (including `allowPrivateNetwork`) are **silently rejected** by schema validation. The key was removed from our config on Apr 12.

---

## Evidence Timeline (Apr 12)

| Time | Event |
|------|-------|
| 10:35–11:27 | `mediaPaths is not defined` errors (Bug 1) |
| ~11:27 | Gateway restarted; Bug 1 stops |
| 12:50 | Config hot-reload, BB channel restarts |
| 12:52–13:13 | `image failed: Local media file not found` (Bug 2 — files never downloaded) |

- `media/tool-attachments/` — empty (files never written)
- `media/inbound/` — last file from Apr 6 (worked before SSRF regression ~v2026.2.20)

---

## Workaround Options

### Option A: Install Pre-Release (if available)
```bash
npm install -g openclaw@next
openclaw gateway restart
```
The fix is on `main` — a pre-release channel may include it.

### Option B: BB API Polling Script
A local script that polls BB API for new attachments and downloads them directly, bypassing OpenClaw's SSRF guard. See `workspace/scripts/bb-attachment-poll.js` (if created).

### Option C: Wait for Next Release
Monitor https://github.com/openclaw/openclaw/releases for a version that includes commits `7d93970` or `dd41a78`.

---

## Config State (Clean)

After cleanup on Apr 12:
- Removed all `allowPrivateNetwork: true` keys (schema-rejected, no effect)
- Removed `network.dangerouslyAllowPrivateNetwork` (not a real config key)
- Reverted `serverUrl` to `127.0.0.1` (LAN IP made no difference since SSRF blocks both)
- `mediaLocalRoots` kept as-is (needed for local file access once downloads work)

---

## Files & References

- Config: `~/.openclaw/openclaw.json`
- Gateway err log: `~/.openclaw/logs/gateway.err.log`
- Gateway main log: `~/.openclaw/logs/gateway.log`
- BB Server: `http://127.0.0.1:1234` (Debra), `http://127.0.0.1:1235` (Alex)
- GitHub: openclaw/openclaw#34749, #26831, #24457

---

**Logged by:** Claude (Cowork session with Alex) | **Time spent:** 3+ hours across sessions | **Resolution:** Awaiting upstream release
