# Voice Agent Phase 2 Research: Custom Voice + Real-Time Conversation

> **Date:** 2026-03-28
> **Goal:** Find the best path to get Debra's custom ElevenLabs voice into real-time phone conversations

---

## The Problem

We have two things that work separately but not together:
1. **Debra's voice** (ElevenLabs custom clone, voice_id: w6INrsHCejnExFzTH8Nm) — sounds like Debra
2. **Real-time conversation** (OpenAI Realtime API) — natural, interruptible, but uses OpenAI's built-in voices only

We need both: Debra's actual voice + natural real-time conversation.

---

## Options Ranked (Best → Worst)

### 🏆 Option 1: ElevenLabs Conversational AI 2.0 + Twilio Native Integration
**Winner. This is the path.**

ElevenLabs launched "Conversational AI 2.0" in March 2026. It does EXACTLY what we need:
- **Custom voice support** — use any voice in your library, including cloned voices (Debra's!)
- **Sub-second latency** — real-time conversation, not turn-based
- **Natural turn-taking** — handles interruptions/barge-in natively
- **70+ language support** — auto-detects and switches
- **Native Twilio integration** — just import your Twilio number, assign an agent, done
- **Outbound calls** — can initiate calls via API
- **LLM integration** — can use their built-in LLM or connect to Claude/GPT

**How it works:**
1. Create an agent in ElevenLabs dashboard (or API)
2. Set system prompt (Debra's personality)
3. Assign Debra's cloned voice
4. Import Twilio number (+18653915873) with SID + auth token
5. Assign agent to phone number
6. Done. Calls in and out use Debra's real voice with real-time conversation.

**Cost:** ~$0.12/min overage on Pro plan ($99/mo). LLM costs extra 10-30%.

**Docs:**
- https://elevenlabs.io/docs/eleven-agents/phone-numbers/twilio-integration/native-integration
- https://elevenlabs.io/conversational-ai
- https://elevenlabs.io/agents

---

### Option 2: Twilio ConversationRelay + ElevenLabs TTS
**Good alternative if we want more control.**

Twilio's ConversationRelay is a service that handles the bidirectional audio bridge. It sends you text (from STT) via WebSocket, you process it, send text back, and it uses ElevenLabs as the TTS provider.

**Architecture:**
```
Phone → Twilio → ConversationRelay → WebSocket → Our Server
                                                    ↓
                                              Claude/GPT (LLM)
                                                    ↓
                                    Text → ElevenLabs TTS → Audio
                                                    ↓
                              WebSocket → ConversationRelay → Phone
```

**Pros:**
- Full control over the LLM (can use Claude with Debra's personality)
- ElevenLabs custom voice with our voice_id
- Interruption handling built into ConversationRelay
- We control the system prompt, context injection, everything

**Cons:**
- More code to write (WebSocket server, LLM integration, audio handling)
- Higher latency than Option 1 (STT → LLM → TTS chain vs ElevenLabs' optimized pipeline)
- Audio format must be μ-law 8000 Hz to match Twilio
- Need to handle turn detection ourselves

**Key requirement:** Audio format MUST be set to mulaw 8000Hz on both Twilio and ElevenLabs sides. This is likely why we got static on the OpenAI Realtime API test.

**Docs:**
- https://www.twilio.com/en-us/blog/integrate-elevenlabs-voices-with-twilios-conversationrelay
- https://elevenlabs.io/blog/twilio-conversation-relay

---

### Option 3: LiveKit Agents + ElevenLabs + Twilio SIP
**Most powerful but most complex.**

LiveKit is an open-source real-time media platform with an Agents framework. Can do voice, video, screen share, etc.

**How it works:**
- Twilio SIP trunk routes calls into LiveKit rooms
- LiveKit Agent processes audio with STT → LLM → TTS pipeline
- ElevenLabs plugin for TTS (supports custom voices)
- Handles turn detection, interruptions, multimodal input

**Pros:**
- Open source, most flexible
- Can add video later (Mirror product integration?)
- Supports custom and cloned ElevenLabs voices via plugin
- Strong developer community

**Cons:**
- Requires running LiveKit server (or using LiveKit Cloud)
- Most complex setup
- SIP trunking config between Twilio and LiveKit
- Overkill for our current needs

**Docs:**
- https://docs.livekit.io/agents/
- https://docs.livekit.io/telephony/
- https://docs.livekit.io/agents/models/tts/elevenlabs/

---

### Option 4: Vapi
**Managed platform, easiest but least control.**

Vapi is an API-first voice AI platform. BYO models for STT, LLM, TTS.

**Pros:**
- Very fast setup (10 min to working phone agent)
- Can use ElevenLabs custom voices
- Sub-500ms latency target
- Handles telephony, turn-taking, barge-in

**Cons:**
- Another SaaS dependency
- Less control than building ourselves
- $0.05/min platform fee PLUS all model costs on top
- We lose the "built it ourselves" story for HoldPlease

---

### Option 5: Retell AI
**Full-stack phone agent platform.**

Similar to Vapi but more enterprise-focused.

**Pros:**
- Complete real-time voice stack
- Integrates with ElevenLabs for premium voices
- Branded calls, batch campaigns
- ~800ms latency

**Cons:**
- $0.13-0.31/min total cost
- Less hacker-friendly than building ourselves
- Another platform dependency

---

## Recommendation

**Start with Option 1 (ElevenLabs Conversational AI 2.0)** because:
1. We already have an ElevenLabs account with Debra's voice
2. Native Twilio integration = minimal code
3. Sub-second latency out of the box
4. Custom voice is a first-class feature, not a bolt-on
5. Fastest path to "Debra sounds like Debra on the phone"

**Graduate to Option 2 (ConversationRelay)** when we need:
- Full control over the LLM (using Claude with deep Debra context)
- Custom call flows (hold detection + conversation hybrid)
- Cost optimization at scale

**Keep Option 3 (LiveKit) on the radar** for when HoldPlease becomes a real product and needs video, multimodal, or white-label capabilities.

---

## Static Audio Bug (from today's test)

The loud static on the OpenAI Realtime API call was likely an **audio format mismatch**. OpenAI Realtime API uses pcmu (mulaw 8kHz) but there may be issues with how we're configuring the bidirectional stream format, or the Twilio stream wasn't set to the right track mode. This is a known gotcha in Twilio + OpenAI integrations.

Fix: Ensure `track: 'both_tracks'` or proper bidirectional stream configuration in the TwiML `<Connect><Stream>` element. Also verify the OpenAI session config audio format matches exactly.

---

## Next Steps

1. **Upgrade ElevenLabs plan** to Pro ($99/mo) if not already — need conversational AI access
2. **Create a Debra agent** in ElevenLabs dashboard with system prompt + voice
3. **Import Twilio number** (+18653915873) into ElevenLabs
4. **Test inbound + outbound calls**
5. **If we need more LLM control**, build the ConversationRelay integration
