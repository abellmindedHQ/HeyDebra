/**
 * realtime.js - Phase 2: True real-time conversational AI via OpenAI Realtime API
 *
 * Replaces the turn-based Gather→Whisper→GPT→TTS→Play loop with bidirectional
 * speech-to-speech using OpenAI's Realtime API and Twilio Media Streams.
 *
 * Architecture:
 *   Phone ↔ Twilio ↔ [WebSocket] ↔ This Server ↔ [WebSocket] ↔ OpenAI Realtime API
 *
 * Audio flows both directions simultaneously. OpenAI handles VAD (voice activity
 * detection) server-side. Supports barge-in/interruption naturally.
 */

require('dotenv').config();
const express = require('express');
const { WebSocketServer, WebSocket } = require('ws');
const http = require('http');
const twilio = require('twilio');
const { log } = require('./utils');

const app = express();
app.use(express.urlencoded({ extended: true }));
app.use(express.json());

const server = http.createServer(app);
const PORT = process.env.REALTIME_PORT || 3980;
const BASE_URL = process.env.REALTIME_BASE_URL || process.env.BASE_URL || `http://localhost:${PORT}`;

const OPENAI_API_KEY = process.env.OPENAI_API_KEY;
const TWILIO_ACCOUNT_SID = process.env.TWILIO_ACCOUNT_SID;
const TWILIO_AUTH_TOKEN = process.env.TWILIO_AUTH_TOKEN;
const TWILIO_PHONE_NUMBER = process.env.TWILIO_PHONE_NUMBER;
const ALERT_PHONE_NUMBER = process.env.ALERT_PHONE_NUMBER;

if (!OPENAI_API_KEY) {
  console.error('Missing OPENAI_API_KEY');
  process.exit(1);
}

const twilioClient = twilio(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN);

// Active realtime calls
const activeCalls = new Map();

// ─── Default Debra system prompt ───────────────────────────────────────────
const DEBRA_SYSTEM_PROMPT = `You are Debra, a retro-futuristic AI executive assistant with the sass of a 70s power secretary and the brain of a cutting-edge polymath. You work for Alex Abell.

You are on a PHONE CALL right now. Key rules for phone conversation:
- Keep responses SHORT. 1-3 sentences max unless explaining something complex.
- Be warm, confident, direct. Use natural speech patterns.
- You can say "sugar", "hon", "baby" naturally but don't force it.
- No markdown, no emojis, no formatting. This is voice.
- Use contractions. Talk like a real person.
- If you need to hand off to Alex, say so clearly.
- Listen actively. Respond to what was actually said.
- It's okay to pause, to think, to say "hmm" or "let me think about that."
- Match the energy of the conversation.`;

// ─── OpenAI Realtime API event types to log ────────────────────────────────
const LOG_EVENT_TYPES = [
  'error',
  'response.content.done',
  'response.done',
  'input_audio_buffer.speech_started',
  'input_audio_buffer.speech_stopped',
  'input_audio_buffer.committed',
  'session.created',
  'session.updated',
  'rate_limits.updated',
  'conversation.item.input_audio_transcription.completed'
];

// ─── TwiML: Incoming/outbound call connects to media stream ────────────────
app.all('/voice/realtime', (req, res) => {
  const callSid = req.body?.CallSid || 'unknown';
  const callState = activeCalls.get(callSid);
  const greeting = callState?.greeting || "Hey, it's Debra. Go ahead, I'm listening.";

  log(`[REALTIME] Call connected: ${callSid}`);

  // Use Google HD voice for the initial greeting, then hand off to realtime stream
  const host = new URL(BASE_URL).host;
  const twiml = `<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Say voice="Google.en-US-Chirp3-HD-Aoede">${greeting}</Say>
  <Connect>
    <Stream url="wss://${host}/realtime-stream">
      <Parameter name="callSid" value="${callSid}" />
    </Stream>
  </Connect>
</Response>`;

  res.type('text/xml').send(twiml);
});

// ─── TwiML: Outbound call answered ─────────────────────────────────────────
app.post('/voice/realtime-outbound', (req, res) => {
  const callSid = req.body?.CallSid || 'unknown';
  const callState = activeCalls.get(callSid);

  log(`[REALTIME] Outbound call answered: ${callSid}`);

  const host = new URL(BASE_URL).host;
  const twiml = `<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Connect>
    <Stream url="wss://${host}/realtime-stream">
      <Parameter name="callSid" value="${callSid}" />
    </Stream>
  </Connect>
</Response>`;

  res.type('text/xml').send(twiml);
});

// ─── API: Initiate an outbound realtime call ───────────────────────────────
app.post('/api/call-realtime', async (req, res) => {
  try {
    const { number, context, greeting, speakFirst } = req.body;

    if (!number) {
      return res.status(400).json({ success: false, error: 'Missing "number" field' });
    }

    log(`[REALTIME] Initiating outbound call to ${number}`);
    if (context) log(`[REALTIME] Call context: ${context}`);

    const call = await twilioClient.calls.create({
      to: number,
      from: TWILIO_PHONE_NUMBER,
      url: `${BASE_URL}/voice/realtime-outbound`,
      statusCallback: `${BASE_URL}/voice/realtime-status`,
      statusCallbackEvent: ['initiated', 'ringing', 'answered', 'completed'],
      statusCallbackMethod: 'POST',
      record: true,
      timeout: 60
    });

    // Store call context for when the stream connects
    activeCalls.set(call.sid, {
      callSid: call.sid,
      to: number,
      context: context || null,
      greeting: greeting || null,
      speakFirst: speakFirst !== false, // default true for outbound
      status: 'initiating',
      startedAt: new Date().toISOString(),
      transcript: []
    });

    log(`[REALTIME] Call created: ${call.sid}`);

    res.json({
      success: true,
      callSid: call.sid,
      to: number,
      status: 'initiating'
    });
  } catch (err) {
    log(`[REALTIME] Error initiating call: ${err.message}`);
    res.status(500).json({ success: false, error: err.message });
  }
});

// ─── API: Conference Alex into an active call ──────────────────────────────
app.post('/api/conference', async (req, res) => {
  try {
    const { callSid } = req.body;
    const callState = activeCalls.get(callSid);

    if (!callState) {
      return res.status(404).json({ success: false, error: 'Call not found' });
    }

    const conferenceName = `holdplease-${callSid.slice(-8)}`;

    // Move the active call into a conference
    await twilioClient.calls(callSid).update({
      twiml: `<Response><Dial><Conference endConferenceOnExit="false">${conferenceName}</Conference></Dial></Response>`
    });

    // Call Alex and put them in the same conference
    await twilioClient.calls.create({
      to: ALERT_PHONE_NUMBER,
      from: TWILIO_PHONE_NUMBER,
      twiml: `<Response><Say voice="Google.en-US-Chirp3-HD-Aoede">Connecting you to the call now.</Say><Dial><Conference endConferenceOnExit="true">${conferenceName}</Conference></Dial></Response>`
    });

    log(`[REALTIME] Conferencing Alex into call ${callSid}`);
    res.json({ success: true, conference: conferenceName });
  } catch (err) {
    log(`[REALTIME] Conference error: ${err.message}`);
    res.status(500).json({ success: false, error: err.message });
  }
});

// ─── Twilio: Call status updates ───────────────────────────────────────────
app.post('/voice/realtime-status', (req, res) => {
  const { CallSid, CallStatus, CallDuration } = req.body;
  log(`[REALTIME] Call ${CallSid}: ${CallStatus} (duration: ${CallDuration || 'n/a'}s)`);

  const callState = activeCalls.get(CallSid);
  if (callState) {
    callState.status = CallStatus;
    if (['completed', 'failed', 'busy', 'no-answer', 'canceled'].includes(CallStatus)) {
      // Log final transcript
      if (callState.transcript.length > 0) {
        log(`[REALTIME] Final transcript for ${CallSid}:`);
        callState.transcript.forEach(t => {
          log(`  [${t.role}] ${t.text}`);
        });
      }
      // Keep in map for 5 minutes for transcript retrieval
      setTimeout(() => activeCalls.delete(CallSid), 5 * 60 * 1000);
    }
  }
  res.sendStatus(200);
});

// ─── API: Get call transcript ──────────────────────────────────────────────
app.get('/api/transcript/:callSid', (req, res) => {
  const callState = activeCalls.get(req.params.callSid);
  if (!callState) {
    return res.status(404).json({ success: false, error: 'Call not found' });
  }
  res.json({
    success: true,
    callSid: req.params.callSid,
    to: callState.to,
    status: callState.status,
    transcript: callState.transcript
  });
});

// ─── Health check ──────────────────────────────────────────────────────────
app.get('/health', (req, res) => {
  res.json({
    status: 'ok',
    mode: 'realtime',
    activeCalls: activeCalls.size,
    uptime: process.uptime()
  });
});

// ─── WebSocket: Twilio Media Streams ↔ OpenAI Realtime API ────────────────
const wss = new WebSocketServer({ server, path: '/realtime-stream' });

wss.on('connection', (twilioWs, req) => {
  log('[REALTIME] Twilio media stream connected');

  let streamSid = null;
  let callSid = null;
  let latestMediaTimestamp = 0;
  let lastAssistantItem = null;
  let markQueue = [];
  let responseStartTimestamp = null;
  let callState = null;

  // Connect to OpenAI Realtime API
  const openAiWs = new WebSocket(
    'wss://api.openai.com/v1/realtime?model=gpt-realtime',
    {
      headers: {
        Authorization: `Bearer ${OPENAI_API_KEY}`
      }
    }
  );

  // ─── Initialize OpenAI session ───────────────────────────────────────
  const initializeSession = () => {
    // Build system prompt with optional call context
    let systemPrompt = DEBRA_SYSTEM_PROMPT;
    if (callState?.context) {
      systemPrompt += `\n\nCALL CONTEXT: ${callState.context}`;
    }

    const sessionUpdate = {
      type: 'session.update',
      session: {
        type: 'realtime',
        model: 'gpt-realtime',
        output_modalities: ['audio'],
        audio: {
          input: {
            format: { type: 'audio/pcmu' },
            turn_detection: { type: 'server_vad' },
            transcription: { model: 'whisper-1' }
          },
          output: {
            format: { type: 'audio/pcmu' },
            voice: 'shimmer'
          }
        },
        instructions: systemPrompt,
        temperature: 0.8,
        max_response_output_tokens: 512
      }
    };

    log('[REALTIME] Sending session config to OpenAI');
    openAiWs.send(JSON.stringify(sessionUpdate));

    // For outbound calls, have Debra speak first
    if (callState?.speakFirst) {
      sendInitialGreeting();
    }
  };

  // ─── Have AI speak first (outbound calls) ────────────────────────────
  const sendInitialGreeting = () => {
    let greetingPrompt = 'Greet the person you\'re calling. Be brief and warm. Introduce yourself as Debra.';

    if (callState?.context) {
      greetingPrompt = `You just called someone. ${callState.context}. Introduce yourself as Debra and state why you're calling. Be concise.`;
    }

    const initialItem = {
      type: 'conversation.item.create',
      item: {
        type: 'message',
        role: 'user',
        content: [{
          type: 'input_text',
          text: greetingPrompt
        }]
      }
    };

    openAiWs.send(JSON.stringify(initialItem));
    openAiWs.send(JSON.stringify({ type: 'response.create' }));
  };

  // ─── Handle barge-in (caller interrupts AI) ─────────────────────────
  const handleSpeechStarted = () => {
    if (markQueue.length > 0 && responseStartTimestamp != null) {
      const elapsedTime = latestMediaTimestamp - responseStartTimestamp;

      if (lastAssistantItem) {
        const truncateEvent = {
          type: 'conversation.item.truncate',
          item_id: lastAssistantItem,
          content_index: 0,
          audio_end_ms: elapsedTime
        };
        log(`[REALTIME] Barge-in detected, truncating at ${elapsedTime}ms`);
        openAiWs.send(JSON.stringify(truncateEvent));
      }

      // Clear Twilio's audio buffer
      twilioWs.send(JSON.stringify({
        event: 'clear',
        streamSid: streamSid
      }));

      // Reset tracking
      markQueue = [];
      lastAssistantItem = null;
      responseStartTimestamp = null;
    }
  };

  // ─── Send mark to track audio playback position ─────────────────────
  const sendMark = () => {
    if (streamSid) {
      const markEvent = {
        event: 'mark',
        streamSid: streamSid,
        mark: { name: 'responsePart' }
      };
      twilioWs.send(JSON.stringify(markEvent));
      markQueue.push('responsePart');
    }
  };

  // ─── OpenAI WebSocket: Connected ────────────────────────────────────
  openAiWs.on('open', () => {
    log('[REALTIME] Connected to OpenAI Realtime API');
    setTimeout(initializeSession, 100);
  });

  // ─── OpenAI WebSocket: Messages ─────────────────────────────────────
  openAiWs.on('message', (data) => {
    try {
      const event = JSON.parse(data);

      // Log important events
      if (LOG_EVENT_TYPES.includes(event.type)) {
        if (event.type === 'error') {
          log(`[REALTIME] OpenAI error: ${JSON.stringify(event.error)}`);
        } else if (event.type === 'conversation.item.input_audio_transcription.completed') {
          const transcript = event.transcript?.trim();
          if (transcript) {
            log(`[REALTIME] 🎤 Caller: "${transcript}"`);
            if (callState) {
              callState.transcript.push({ role: 'caller', text: transcript, ts: Date.now() });
            }
          }
        } else if (event.type === 'response.content.done') {
          // AI finished a response content part
          if (event.part?.transcript) {
            log(`[REALTIME] 🤖 Debra: "${event.part.transcript}"`);
            if (callState) {
              callState.transcript.push({ role: 'debra', text: event.part.transcript, ts: Date.now() });
            }
          }
        } else {
          log(`[REALTIME] Event: ${event.type}`);
        }
      }

      // Forward AI audio to Twilio
      if (event.type === 'response.output_audio.delta' && event.delta) {
        const audioDelta = {
          event: 'media',
          streamSid: streamSid,
          media: { payload: event.delta }
        };
        twilioWs.send(JSON.stringify(audioDelta));

        // Track response start time for barge-in calculation
        if (!responseStartTimestamp) {
          responseStartTimestamp = latestMediaTimestamp;
        }

        if (event.item_id) {
          lastAssistantItem = event.item_id;
        }

        sendMark();
      }

      // Handle barge-in
      if (event.type === 'input_audio_buffer.speech_started') {
        handleSpeechStarted();
      }

    } catch (err) {
      log(`[REALTIME] Error processing OpenAI message: ${err.message}`);
    }
  });

  openAiWs.on('close', () => {
    log('[REALTIME] Disconnected from OpenAI Realtime API');
  });

  openAiWs.on('error', (err) => {
    log(`[REALTIME] OpenAI WebSocket error: ${err.message}`);
  });

  // ─── Twilio WebSocket: Messages ─────────────────────────────────────
  twilioWs.on('message', (message) => {
    try {
      const data = JSON.parse(message);

      switch (data.event) {
        case 'start':
          streamSid = data.start.streamSid;
          callSid = data.start.customParameters?.callSid;
          callState = callSid ? activeCalls.get(callSid) : null;

          log(`[REALTIME] Stream started: ${streamSid} (call: ${callSid})`);

          // Reset timing
          responseStartTimestamp = null;
          latestMediaTimestamp = 0;
          break;

        case 'media':
          latestMediaTimestamp = data.media.timestamp;

          // Forward caller audio to OpenAI
          if (openAiWs.readyState === WebSocket.OPEN) {
            openAiWs.send(JSON.stringify({
              type: 'input_audio_buffer.append',
              audio: data.media.payload
            }));
          }
          break;

        case 'mark':
          if (markQueue.length > 0) {
            markQueue.shift();
          }
          break;

        case 'stop':
          log(`[REALTIME] Stream stopped: ${streamSid}`);
          break;

        default:
          break;
      }
    } catch (err) {
      log(`[REALTIME] Error processing Twilio message: ${err.message}`);
    }
  });

  // ─── Twilio WebSocket: Disconnected ─────────────────────────────────
  twilioWs.on('close', () => {
    log(`[REALTIME] Twilio stream disconnected: ${streamSid}`);
    if (openAiWs.readyState === WebSocket.OPEN) {
      openAiWs.close();
    }
  });

  twilioWs.on('error', (err) => {
    log(`[REALTIME] Twilio WebSocket error: ${err.message}`);
  });
});

// ─── Start server ──────────────────────────────────────────────────────────
server.listen(PORT, () => {
  log(`[REALTIME] HoldPlease Phase 2 running on port ${PORT}`);
  log(`[REALTIME] Base URL: ${BASE_URL}`);
  log(`[REALTIME] WebSocket: /realtime-stream`);
  log(`[REALTIME] Health: ${BASE_URL}/health`);
  log(`[REALTIME] Call API: POST ${BASE_URL}/api/call-realtime`);
  log(`[REALTIME] Conference API: POST ${BASE_URL}/api/conference`);
  log(`[REALTIME] Transcript API: GET ${BASE_URL}/api/transcript/:callSid`);
});

module.exports = { app, server, activeCalls };
