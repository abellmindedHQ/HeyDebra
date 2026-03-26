# Native iMessage Voice Memos — Fix Documentation

**Status:** PR-ready patches prepared  
**Date:** 2026-03-25  
**Repos:** openclaw/openclaw + BlueBubblesApp/bluebubbles-server  

---

## Problem Summary

When OpenClaw generates a TTS voice response for a BlueBubbles (iMessage) conversation, it should send the audio as a native iMessage **voice memo** — the little waveform bubble that plays inline. Instead:

1. **OpenClaw side:** The TTS pipeline never activates "voice mode" for BlueBubbles because `bluebubbles` isn't in `VOICE_BUBBLE_CHANNELS`, and even when `audioAsVoice` is set manually, the `sendMedia` handler doesn't forward it as `asVoice: true` to `sendBlueBubblesMedia`.

2. **BlueBubbles Server side:** Even when `isAudioMessage=true` is properly set, using `method=private-api` on macOS Tahoe/Sequoia produces broken 0-second voice memos. The apple-script method (which converts MP3→CAF using `afconvert`) works correctly.

---

## Architecture — How TTS Voice Delivery Works

```
TTS generates audio
    ↓
resolveOutputFormat(channelId)
    → for VOICE_BUBBLE_CHANNELS: voiceCompatible=true, target="voice-note"
    → for others: voiceCompatible=false, no voice target
    ↓
maybeApplyTtsToPayload()
    → if voiceCompatible AND channel in VOICE_BUBBLE_CHANNELS:
       sets audioAsVoice=true on the ReplyPayload
    ↓
deliverPayloads() in deliver.ts
    → sendOverrides.audioAsVoice = payload.audioAsVoice
    → calls handler.sendMedia(caption, mediaUrl, sendOverrides)
    ↓
BlueBubbles sendMedia(ctx)
    → ctx.audioAsVoice is available but NOT currently forwarded
    → calls sendBlueBubblesMedia({ ..., asVoice: ??? })  ← MISSING
    ↓
sendBlueBubblesAttachment({ asVoice })
    → wantsVoice = asVoice === true
    → isAudioMessage = wantsVoice
    → form POST to /api/v1/message/attachment with isAudioMessage=true
    ↓
BlueBubbles Server
    → sendAttachmentSync → method=private-api (if enabled)
    → ⚠️ BUG: private-api produces 0-second voice memo on macOS Tahoe
    → ✅ apple-script: converts MP3→CAF, plays correctly
```

---

## OpenClaw Patches

### Patch 1: `openclaw-01-voice-bubble-channels.patch`
**File:** `src/tts/tts.ts`

**What it does:**
- Adds `"bluebubbles"` to `VOICE_BUBBLE_CHANNELS`
- Adds `BLUEBUBBLES_VOICE_OUTPUT` constant (MP3, not opus — iMessage doesn't support opus natively)
- Updates `resolveOutputFormat()` to return MP3 for BlueBubbles while still setting `voiceCompatible: true`

**Key difference from Telegram:** Telegram uses opus (`.opus`). BlueBubbles/iMessage uses MP3 → the server converts to CAF. So BlueBubbles needs its own output format.

### Patch 2: `openclaw-02-bluebubbles-send-media-asvoice.patch`
**File:** `extensions/bluebubbles/src/channel.ts`

**What it does:**
- Destructures `audioAsVoice` from the sendMedia context
- Passes `asVoice: audioAsVoice === true ? true : undefined` to `sendBlueBubblesMedia`

This is the **minimum required fix** alongside patch 1. With both patches, the flow works:
1. TTS for bluebubbles channel → MP3 with `voiceCompatible: true`
2. `audioAsVoice: true` set on payload
3. `sendMedia` extracts and forwards `asVoice: true`
4. `sendBlueBubblesAttachment` sends with `isAudioMessage: true`

### Patch 3: `openclaw-03-deliver-sendpayload-gate.patch`
**File:** `src/infra/outbound/deliver.ts`

**What it does (optional enhancement):**
- Extends the `sendPayload` gate to also fire when `effectivePayload.audioAsVoice === true`
- Enables channel plugins to implement `sendPayload` for clean voice-memo handling

**Status:** Optional. Patches 1+2 are sufficient because `audioAsVoice` already flows through `sendOverrides` to `sendMedia`. This patch only matters if you add a `sendPayload` implementation to BlueBubbles.

---

## BlueBubbles Server Patch

### Patch: `bluebubbles-server-01-audio-message-applescript-fallback.patch`
**File:** `packages/server/src/server/api/interfaces/messageInterface.ts`
**Method:** `sendAttachmentSync`

**What it does:**
- When `isAudioMessage=true` AND `method=private-api`, falls back to `apple-script`
- Logs a warning explaining the fallback
- Apple-script path: uploads MP3 → `FileSystem.convertMp3ToCaf()` → sends CAF → plays correctly

**Root cause of the bug:** The private-api agent on macOS Tahoe doesn't correctly set the audio duration/metadata when sending voice memos. The resulting message shows 0 seconds and fails to play. Apple-script relies on Messages.app's native file drag behavior which handles CAF correctly.

---

## Applying the Patches

### OpenClaw (requires source access)

```bash
# Clone the repo
git clone https://github.com/openclaw/openclaw
cd openclaw

# Apply patches
patch -p1 < /path/to/openclaw-01-voice-bubble-channels.patch
patch -p1 < /path/to/openclaw-02-bluebubbles-send-media-asvoice.patch
# Optional:
patch -p1 < /path/to/openclaw-03-deliver-sendpayload-gate.patch

# Build
npm install && npm run build
```

### BlueBubbles Server (requires source access)

```bash
git clone https://github.com/BlueBubblesApp/bluebubbles-server
cd bluebubbles-server

patch -p1 < /path/to/bluebubbles-server-01-audio-message-applescript-fallback.patch

npm install && npm run build
```

---

## Testing

### Step 1: Verify TTS activates voice mode for BlueBubbles

Enable verbose logging in OpenClaw config and send a TTS message. Look for:
```
TTS: conversion succeeded (provider=elevenlabs, format=mp3_44100_128, voiceCompatible=true)
```
The `voiceCompatible=true` confirms the voice path activated.

### Step 2: Verify asVoice reaches the attachment endpoint

Enable debug logs in BlueBubbles server. When a voice memo is sent, you should see:
```
Sending attachment "Audio Message.mp3" to iMessage;xxx@xxx.com (isAudioMessage=true)
```
And for the fallback:
```
Audio message requested via private-api; falling back to apple-script...
```

### Step 3: End-to-end test

1. Configure OpenClaw with TTS enabled (`tts.auto: always` or `inbound`)
2. Send a message to a BlueBubbles-connected conversation
3. The reply should appear in iMessage as a waveform voice memo bubble (not a file attachment)
4. Tap it — it should play audio

### Step 4: Verify no regression

- Regular file attachments (images, documents) should still work without `asVoice`
- TTS on Telegram/WhatsApp should still use opus and still work
- Non-TTS BlueBubbles responses should be unaffected

---

## Workaround (No Code Change Needed)

While waiting for patches to land, you can manually trigger voice memo delivery using the `sendAttachment` tool with `asVoice: true`:

```
/send --channel bluebubbles --to +1234567890 --attachment /path/to/audio.mp3 --asVoice true
```

This already works (the `sendBlueBubblesAttachment` bottom layer is correct). The bug is only in the TTS auto-pipeline not passing the voice flag through.

---

## Related Issues

- OpenClaw GitHub issue: #16848 — "BlueBubbles TTS sends as file attachment, not voice memo"
- BlueBubbles Server GitHub issue: #773 — "isAudioMessage=true + private-api produces 0-second voice memo on macOS Tahoe"

---

## Files in This Directory

```
patches/
  openclaw-01-voice-bubble-channels.patch      # Add bluebubbles to VOICE_BUBBLE_CHANNELS
  openclaw-02-bluebubbles-send-media-asvoice.patch  # Forward audioAsVoice in sendMedia
  openclaw-03-deliver-sendpayload-gate.patch   # Optional: expand sendPayload gate
  bluebubbles-server-01-audio-message-applescript-fallback.patch  # Force apple-script for audio msgs
README.md  # This file
```
