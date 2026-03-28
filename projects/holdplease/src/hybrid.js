/**
 * hybrid.js - Phase 3: Hybrid Hold System
 *
 * Cost-optimized phone agent that uses TWO modes:
 *
 * HOLD MODE (cheap):
 *   - Twilio Media Streams + Whisper transcription (~$0.02/min)
 *   - Monitors audio for human detection (reuses hold-detector.js)
 *   - Navigates IVR menus via DTMF tones
 *   - Stays silent on hold (no ElevenLabs cost)
 *
 * CONVERSATION MODE (full):
 *   - Switches to ElevenLabs Conversational AI (~$0.12/min)
 *   - Only activates when a human agent picks up
 *   - Full bidirectional conversation with Debra's voice
 *
 * Cost comparison for a 30-min hold + 5-min conversation:
 *   Old way:  35 min × $0.13/min = $4.55
 *   Hybrid:   30 min × $0.02/min + 5 min × $0.13/min = $1.25
 *   Savings:  ~73%
 */

require('dotenv').config();
const express = require('express');
const { WebSocketServer, WebSocket } = require('ws');
const http = require('http');
const https = require('https');
const twilio = require('twilio');
const path = require('path');
const fs = require('fs');
const { HoldDetector } = require('./hold-detector');
const { log } = require('./utils');

const app = express();
app.use(express.urlencoded({ extended: true }));
app.use(express.json());
app.use(express.static(path.join(__dirname, '..', 'web')));

const server = http.createServer(app);
const PORT = process.env.HOLDPLEASE_PORT || 3981;
const BASE_URL = process.env.HYBRID_BASE_URL || `http://localhost:${PORT}`;

const OPENAI_API_KEY = process.env.OPENAI_API_KEY;
const ELEVEN_API_KEY = process.env.ELEVEN_LABS_API_KEY;
const ELEVEN_AGENT_ID = process.env.ELEVEN_AGENT_ID || 'agent_5201kmtfqfv9etgtafvgw16pjpza';
const ELEVEN_PHONE_ID = process.env.ELEVEN_PHONE_ID || 'phnum_6601kmtfr2scffj9rv4fb7fcfrtj';
const TWILIO_ACCOUNT_SID = process.env.TWILIO_ACCOUNT_SID;
const TWILIO_AUTH_TOKEN = process.env.TWILIO_AUTH_TOKEN;
const TWILIO_PHONE_NUMBER = process.env.TWILIO_PHONE_NUMBER || '+18653915873';

const twilioClient = twilio(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN);

// Call store
const CALLS_FILE = path.join(__dirname, '..', 'data', 'calls.json');
let calls = [];
try {
  const dir = path.dirname(CALLS_FILE);
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
  if (fs.existsSync(CALLS_FILE)) calls = JSON.parse(fs.readFileSync(CALLS_FILE, 'utf-8'));
} catch (e) { calls = []; }

function saveCalls() {
  try {
    const dir = path.dirname(CALLS_FILE);
    if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
    fs.writeFileSync(CALLS_FILE, JSON.stringify(calls, null, 2));
  } catch (e) { log(`[HYBRID] Save error: ${e.message}`); }
}

// Active hold sessions
const holdSessions = new Map();

// ─── Helper: ElevenLabs API ────────────────────────────────────────────────
function elevenLabsRequest(method, apiPath, body) {
  return new Promise((resolve, reject) => {
    const data = body ? JSON.stringify(body) : null;
    const options = {
      hostname: 'api.elevenlabs.io',
      path: apiPath,
      method,
      headers: { 'xi-api-key': ELEVEN_API_KEY, 'Content-Type': 'application/json' }
    };
    const req = https.request(options, (res) => {
      let responseBody = '';
      res.on('data', d => responseBody += d);
      res.on('end', () => { try { resolve(JSON.parse(responseBody)); } catch (e) { resolve(responseBody); } });
    });
    req.on('error', reject);
    if (data) req.write(data);
    req.end();
  });
}

// ─── IVR Navigation via DTMF ──────────────────────────────────────────────
async function sendDTMF(callSid, digits) {
  log(`[HYBRID] Sending DTMF: ${digits} to call ${callSid}`);
  try {
    // Use Twilio's play DTMF on the call
    await twilioClient.calls(callSid).update({
      twiml: `<Response><Play digits="${digits}"/><Pause length="7200"/></Response>`
    });
  } catch (err) {
    log(`[HYBRID] DTMF error: ${err.message}`);
  }
}

// ─── Build context prompt ──────────────────────────────────────────────────
function buildCallPrompt(callData) {
  let prompt = `You are Debra, calling ${callData.company || 'a company'} on behalf of Alex Abell.\n\n`;
  prompt += `TASK: ${callData.task}\n\n`;
  if (callData.reference) prompt += `REFERENCE NUMBERS: ${callData.reference}\n\n`;
  prompt += `RULES:\n- Be polite but firm. You're Alex's assistant.\n- State clearly what you need.\n- Get the representative's name and any new reference numbers.\n- If they need identity verification you can't provide, say "Let me check with Alex and call back."\n- Summarize the outcome clearly.\n`;
  return prompt;
}

// ─── Phase 1: Start call in HOLD MODE (cheap) ─────────────────────────────
async function startHoldModeCall(callData) {
  const callId = `hp_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;

  log(`[HYBRID] Starting HOLD MODE call ${callId} to ${callData.phoneNumber}`);

  // Create Twilio call that connects to our WebSocket for monitoring
  const call = await twilioClient.calls.create({
    to: callData.phoneNumber,
    from: TWILIO_PHONE_NUMBER,
    url: `${BASE_URL}/voice/hybrid-connect`,
    statusCallback: `${BASE_URL}/voice/hybrid-status`,
    statusCallbackEvent: ['initiated', 'ringing', 'answered', 'completed'],
    record: true,
    timeout: 60
  });

  const record = {
    callId,
    callSid: call.sid,
    company: callData.company || callData.phoneNumber,
    phoneNumber: callData.phoneNumber,
    task: callData.task,
    reference: callData.reference,
    callback: callData.callback,
    status: 'hold-mode',
    statusMessage: 'Connecting (hold mode - low cost)...',
    mode: 'hold',
    startedAt: new Date().toISOString(),
    transcript: [],
    holdStartedAt: null,
    humanDetectedAt: null,
    conversationId: null,
    costEstimate: { holdMinutes: 0, convoMinutes: 0, totalCost: 0 }
  };

  // Store IVR navigation context
  holdSessions.set(call.sid, {
    callId,
    callData,
    ivrPhase: true,
    holdDetector: null,
    humanDetected: false,
    holdStartTime: null
  });

  calls.unshift(record);
  saveCalls();

  return { callId, callSid: call.sid };
}

// ─── TwiML: Connect call to media stream for monitoring ────────────────────
app.post('/voice/hybrid-connect', (req, res) => {
  const callSid = req.body.CallSid;
  log(`[HYBRID] Call answered, starting media stream: ${callSid}`);

  const host = new URL(BASE_URL).host;
  const twiml = `<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Start>
    <Stream url="wss://${host}/hybrid-stream" track="inbound_track">
      <Parameter name="callSid" value="${callSid}" />
    </Stream>
  </Start>
  <Pause length="7200" />
</Response>`;

  res.type('text/xml').send(twiml);
});

// ─── Twilio: Call status updates ───────────────────────────────────────────
app.post('/voice/hybrid-status', (req, res) => {
  const { CallSid, CallStatus, CallDuration } = req.body;
  log(`[HYBRID] Call ${CallSid}: ${CallStatus} (${CallDuration || '?'}s)`);

  if (['completed', 'failed', 'busy', 'no-answer', 'canceled'].includes(CallStatus)) {
    const session = holdSessions.get(CallSid);
    if (session) {
      updateCall(session.callId, {
        status: 'completed',
        statusMessage: `Call ended (${CallStatus}). Duration: ${CallDuration || '?'}s`
      });
      if (session.holdDetector) session.holdDetector.shutdown();
      holdSessions.delete(CallSid);
    }
  }
  res.sendStatus(200);
});

// ─── Phase 2: Switch to CONVERSATION MODE (ElevenLabs) ────────────────────
async function switchToConversationMode(callSid, session) {
  log(`[HYBRID] 🚨 HUMAN DETECTED! Switching to conversation mode for ${callSid}`);

  const callRecord = calls.find(c => c.callId === session.callId);
  if (callRecord) {
    callRecord.status = 'conversation-mode';
    callRecord.statusMessage = 'Human detected! Switching to Debra voice...';
    callRecord.humanDetectedAt = new Date().toISOString();
    callRecord.mode = 'conversation';
    saveCalls();
  }

  // Update ElevenLabs agent with this call's context
  const prompt = buildCallPrompt(session.callData);
  await elevenLabsRequest('PATCH', `/v1/convai/agents/${ELEVEN_AGENT_ID}`, {
    conversation_config: {
      agent: {
        prompt: { prompt },
        first_message: `Hi, this is Debra calling on behalf of Alex Abell. ${session.callData.task.split('.')[0]}.`
      }
    }
  });

  // Hang up the Twilio hold call
  try {
    await twilioClient.calls(callSid).update({ status: 'completed' });
  } catch (e) {
    log(`[HYBRID] Error ending hold call: ${e.message}`);
  }

  // Immediately call back on ElevenLabs (the human is waiting!)
  const result = await elevenLabsRequest('POST', '/v1/convai/twilio/outbound-call', {
    agent_id: ELEVEN_AGENT_ID,
    agent_phone_number_id: ELEVEN_PHONE_ID,
    to_number: session.callData.phoneNumber
  });

  if (result.success) {
    log(`[HYBRID] ElevenLabs conversation started: ${result.conversation_id}`);
    if (callRecord) {
      callRecord.conversationId = result.conversation_id;
      saveCalls();
    }

    // Poll for conversation completion
    pollElevenLabsConversation(session.callId, result.conversation_id);
  } else {
    log(`[HYBRID] Failed to start ElevenLabs conversation: ${JSON.stringify(result)}`);
    // Fallback: call Alex to take over
    if (session.callData.callback) {
      log(`[HYBRID] Calling Alex as fallback...`);
      await twilioClient.calls.create({
        to: session.callData.callback,
        from: TWILIO_PHONE_NUMBER,
        twiml: `<Response><Say voice="Google.en-US-Chirp3-HD-Aoede">Hey, this is Debra. A human picked up at ${session.callData.company} but I couldn't switch to conversation mode. You may want to call them back right now. The number is ${session.callData.phoneNumber}.</Say></Response>`
      });
    }
  }
}

// ─── Poll ElevenLabs conversation ──────────────────────────────────────────
async function pollElevenLabsConversation(callId, conversationId) {
  const maxPolls = 360; // 30 min
  let pollCount = 0;

  const interval = setInterval(async () => {
    pollCount++;
    if (pollCount > maxPolls) {
      clearInterval(interval);
      updateCall(callId, { status: 'completed', statusMessage: 'Conversation ended (timeout)' });
      resetAgentPrompt();
      return;
    }

    try {
      const convo = await elevenLabsRequest('GET', `/v1/convai/conversations/${conversationId}`);
      if (convo.status === 'done' || convo.status === 'failed') {
        clearInterval(interval);

        const transcript = (convo.transcript || []).map(t => ({
          role: t.role === 'agent' ? 'debra' : 'them',
          text: t.message || t.text || ''
        }));

        updateCall(callId, {
          status: 'completed',
          statusMessage: convo.status === 'done' ? 'Call completed with human' : 'Call failed',
          transcript,
          completedAt: new Date().toISOString()
        });

        log(`[HYBRID] Conversation completed. ${transcript.length} entries.`);
        resetAgentPrompt();
      }
    } catch (err) {
      log(`[HYBRID] Poll error: ${err.message}`);
    }
  }, 5000);
}

async function resetAgentPrompt() {
  try {
    await elevenLabsRequest('PATCH', `/v1/convai/agents/${ELEVEN_AGENT_ID}`, {
      conversation_config: {
        agent: {
          prompt: {
            prompt: `You are Debra, Alex Abell's executive assistant. Warm, grounded, caring. Keep phone responses to 1-3 sentences. Use contractions. Talk like a real person.`
          },
          first_message: "Hey, it's Debra. How can I help you?"
        }
      }
    });
  } catch (e) { log(`[HYBRID] Reset error: ${e.message}`); }
}

// ─── WebSocket: Monitor audio during HOLD MODE ────────────────────────────
const wss = new WebSocketServer({ server, path: '/hybrid-stream' });

wss.on('connection', (ws) => {
  log('[HYBRID] Media stream connected');

  let streamSid = null;
  let callSid = null;
  let session = null;
  let holdDetector = null;

  ws.on('message', async (data) => {
    try {
      const msg = JSON.parse(data);

      switch (msg.event) {
        case 'start':
          streamSid = msg.start.streamSid;
          callSid = msg.start.customParameters?.callSid;
          session = callSid ? holdSessions.get(callSid) : null;

          log(`[HYBRID] Stream started: ${streamSid} (call: ${callSid})`);

          if (session) {
            holdDetector = new HoldDetector({ analyzeIntervalMs: 10000 });
            session.holdDetector = holdDetector;
            session.holdStartTime = Date.now();

            updateCall(session.callId, {
              status: 'hold-mode',
              statusMessage: 'Connected. Listening for IVR/hold/human...',
              holdStartedAt: new Date().toISOString()
            });

            // Human detection → switch to conversation mode
            holdDetector.on('humanDetected', async (info) => {
              if (session.humanDetected) return;
              session.humanDetected = true;

              log(`[HYBRID] 🚨 HUMAN DETECTED: ${info.reason}`);
              log(`[HYBRID] Transcript: "${info.transcript}"`);

              // Add to call transcript
              const call = calls.find(c => c.callId === session.callId);
              if (call) {
                call.transcript.push(
                  { role: 'them', text: `[Human detected: ${info.transcript}]` }
                );
                saveCalls();
              }

              switchToConversationMode(callSid, session);
            });
          }
          break;

        case 'media':
          if (holdDetector && session && !session.humanDetected) {
            holdDetector.processAudio(msg.media.payload, msg.media.timestamp);
          }
          break;

        case 'stop':
          log(`[HYBRID] Stream stopped: ${streamSid}`);
          if (holdDetector) holdDetector.shutdown();
          break;
      }
    } catch (err) {
      log(`[HYBRID] WS error: ${err.message}`);
    }
  });

  ws.on('close', () => {
    log(`[HYBRID] Stream disconnected: ${streamSid}`);
    if (holdDetector) holdDetector.shutdown();
  });
});

// ─── Shared API endpoints (same as holdplease-api.js) ──────────────────────

// Phone number lookup
app.post('/api/lookup', async (req, res) => {
  const { company } = req.body;
  if (!company) return res.status(400).json({ success: false, error: 'Company name required' });

  log(`[HYBRID] Looking up: ${company}`);
  try {
    const data = JSON.stringify({
      model: 'gpt-4o-mini',
      messages: [
        { role: 'system', content: 'Find customer service phone numbers. Return ONLY a JSON array of objects with "name", "phone", "department" fields. No markdown. Format phone as +1XXXXXXXXXX. Max 3 results.' },
        { role: 'user', content: `Find the customer service phone number(s) for: ${company}` }
      ],
      max_tokens: 300, temperature: 0
    });

    const result = await new Promise((resolve, reject) => {
      const req = https.request({
        hostname: 'api.openai.com', path: '/v1/chat/completions', method: 'POST',
        headers: { 'Authorization': `Bearer ${OPENAI_API_KEY}`, 'Content-Type': 'application/json' }
      }, (res) => {
        let body = '';
        res.on('data', d => body += d);
        res.on('end', () => { try { resolve(JSON.parse(body)); } catch (e) { resolve(null); } });
      });
      req.on('error', reject);
      req.write(data);
      req.end();
    });

    if (result?.choices?.[0]?.message?.content) {
      const cleaned = result.choices[0].message.content.replace(/```json\n?/g, '').replace(/```\n?/g, '').trim();
      const parsed = JSON.parse(cleaned);
      if (Array.isArray(parsed) && parsed.length > 0) {
        return res.json({ success: true, results: parsed.map(r => ({ name: r.name || company, phone: r.phone, address: r.department || '' })) });
      }
    }
  } catch (e) { log(`[HYBRID] Lookup error: ${e.message}`); }
  res.json({ success: false, error: 'Could not find phone number.' });
});

// Start call (uses hybrid mode)
app.post('/api/holdplease', async (req, res) => {
  try {
    const { company, phoneNumber, task, reference, callback } = req.body;
    if (!phoneNumber || !task) return res.status(400).json({ success: false, error: 'Phone number and task required' });

    const result = await startHoldModeCall({ company, phoneNumber, task, reference, callback });
    res.json({ success: true, callId: result.callId });
  } catch (err) {
    log(`[HYBRID] Error: ${err.message}`);
    res.status(500).json({ success: false, error: err.message });
  }
});

// Call history
app.get('/api/holdplease/history', (req, res) => {
  res.json({ calls: calls.slice(0, 20) });
});

// Call status
app.get('/api/holdplease/:callId', (req, res) => {
  const call = calls.find(c => c.callId === req.params.callId);
  if (!call) return res.status(404).json({ success: false, error: 'Call not found' });
  res.json(call);
});

// Health
app.get('/api/health', (req, res) => {
  res.json({
    status: 'ok',
    mode: 'hybrid-phase3',
    activeCalls: holdSessions.size,
    totalCalls: calls.length
  });
});

// Serve UI
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, '..', 'web', 'index.html'));
});

function updateCall(callId, updates) {
  const call = calls.find(c => c.callId === callId);
  if (call) { Object.assign(call, updates); saveCalls(); }
}

// ─── Start ─────────────────────────────────────────────────────────────────
server.listen(PORT, () => {
  log(`[HYBRID] HoldPlease Phase 3 (Hybrid) running on port ${PORT}`);
  log(`[HYBRID] Mode: Hold detection (cheap) → ElevenLabs conversation (when human detected)`);
  log(`[HYBRID] Base URL: ${BASE_URL}`);
  log(`[HYBRID] Calls stored: ${calls.length}`);
});

module.exports = { app, server };
