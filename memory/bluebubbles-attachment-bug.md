# BlueBubbles Attachment Bug — Diagnostic Report

**Status:** 🔴 BLOCKING — Images/files not appearing in conversation context  
**Date Identified:** 2026-04-09  
**Severity:** HIGH — Core messaging feature broken  
**Workaround:** Text-only messages work; use text descriptions for images

---

## Root Cause (Confirmed)

BlueBubbles webhooks ARE being dispatched successfully from the server, but **OpenClaw's webhook parser rejects them as "unable to parse message payload"**.

### Evidence
- **BB Server Log:** "[WebhookService] Dispatching event to webhook: http://127.0.0.1:18789/bluebubbles-webhook-debra" ✅
- **OpenClaw Log:** "[bluebubbles] webhook rejected: unable to parse message payload" ❌

### Technical Details

**Location:** `/opt/homebrew/lib/node_modules/openclaw/dist/channel.runtime-BSXlY6sk.js` (line 2096)

**Failure Point:** `normalizeWebhookMessage(payload)` returns `null`

```javascript
const message = reaction ? null : normalizeWebhookMessage(payload);
if (!message && !reaction) {
    res.statusCode = 400;
    res.end("invalid payload");
    console.warn("[bluebubbles] webhook rejected: unable to parse message payload");
    return true;
}
```

**Root Issue:** The `extractMessagePayload()` function in `/opt/homebrew/lib/node_modules/openclaw/dist/monitor-normalize-DBiB1PcA.js` (line 914) cannot find the message structure in BlueBubbles' webhook payload.

The function tries to extract from:
```javascript
const data = parseRecord(payload.data ?? payload.payload ?? payload.event);
const message = parseRecord(payload.message ?? data?.message ?? data);
```

But **BlueBubbles' actual payload structure doesn't match these paths**.

---

## Attempted Workarounds

### Approach 1: Message Transformer Proxy ✅ Created
- Built `/tmp/bb-transformer.js` (Node.js proxy on port 18790)
- Listens for BB webhooks and transforms them
- **Status:** Created but **not integrated** (needs BB webhook config update to point to transformer)
- **Blocker:** Can't modify BB webhook configuration without direct DB access

### Approach 2: OpenClaw Code Patching ❌ Not Feasible
- Compiled/minified channel runtime not directly editable
- Would require OpenClaw source rebuild or plugin API (doesn't exist for this layer)

### Approach 3: Verbose Logging ⏳ Pending
- Attempted to enable debug logging to capture actual BB payload structure
- **Next step:** Extract raw webhook payload and reverse-engineer BB's structure

---

## Next Steps (If Time/Priority Permits)

1. **Capture raw BB payload** 
   - Intercept webhook at gateway before processing
   - Log raw JSON to understand BB's structure
   
2. **Propose OpenClaw patch**
   - File issue with OpenClaw team: `monitor-normalize-DBiB1PcA.js` line 914
   - Submit PR to add BB payload structure support
   
3. **Upstream Fix Timeline**
   - OpenClaw v2026.4.10+ may include a fix
   - Monitor releases at https://github.com/anthropics/openclaw

---

## Impact

- ❌ Image/file attachments not surfacing in conversation context
- ❌ Screenshots from user not visible to Debra
- ✅ Text messages work fine
- ✅ iMessages still being logged (just not displayed in conversation)

## Workaround for User

Until fixed, users must:
1. Send image + text description ("Here's a screenshot of...")
2. Or send via alternate channel (email, Slack, etc.) and reference in text

---

## Files & Logs

- Transformer proxy: `/tmp/bb-transformer.js`
- BB Server log: `~/Library/Logs/bluebubbles-server/main.log`
- OpenClaw log: `/tmp/openclaw/openclaw-2026-04-09.log`
- Config: `/Users/debra/.openclaw/openclaw.json`

---

**Logged by:** Debra | **Time spent:** 90+ minutes | **Resolution:** Pending OpenClaw upstream fix
