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
const { Recorder } = require('./recorder');
const { log } = require('./utils');

const recorder = new Recorder();

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
  const session = holdSessions.get(callSid);

  // Check if call has IVR digits to navigate before streaming
  let ivrTwiml = '';
  if (session && session.callData && session.callData.ivrDigits) {
    const digits = session.callData.ivrDigits;
    log(`[HYBRID] Pre-navigating IVR with digits: ${JSON.stringify(digits)}`);
    for (const step of digits) {
      ivrTwiml += `  <Pause length="${step.pause || 12}" />\n  <Play digits="${step.digit}" />\n`;
    }
  }

  const twiml = `<?xml version="1.0" encoding="UTF-8"?>
<Response>
${ivrTwiml}  <Start>
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
    // Auto-fetch and save recording after call completes
    if (CallStatus === 'completed') {
      fetchAndSaveRecording(CallSid);
    }
  }
  res.sendStatus(200);
});

// ─── Phase 2: Switch to CONVERSATION MODE (ElevenLabs) ────────────────────
// Instead of hanging up + redialing, we bridge the ElevenLabs agent INTO
// the existing Twilio call using the register-call API. The call to the
// company never drops — we just swap who's talking on our end.
async function switchToConversationMode(callSid, session) {
  log(`[HYBRID] 🚨 HUMAN DETECTED! Switching to conversation mode for ${callSid}`);

  const callRecord = calls.find(c => c.callId === session.callId);
  if (callRecord) {
    callRecord.status = 'conversation-mode';
    callRecord.statusMessage = 'Human detected! Bridging Debra into the call...';
    callRecord.humanDetectedAt = new Date().toISOString();
    callRecord.mode = 'conversation';
    saveCalls();
  }

  // Update ElevenLabs agent with this call's context + end_call system tool
  const prompt = buildCallPrompt(session.callData);
  try {
    await elevenLabsRequest('PATCH', `/v1/convai/agents/${ELEVEN_AGENT_ID}`, {
      conversation_config: {
        agent: {
          prompt: {
            prompt: prompt + `\n\nIMPORTANT: When the conversation is complete and you've said goodbye, use the end_call tool to disconnect the call. Do not just say goodbye and wait.`,
            tools: [
              {
                type: 'system',
                name: 'end_call',
                description: 'End the phone call when the conversation is complete, task is done, or the other party says goodbye.'
              }
            ]
          },
          first_message: `Hi, this is Debra calling on behalf of Alex Abell. ${session.callData.task.split('.')[0]}.`
        }
      }
    });
    log(`[HYBRID] Agent updated with call context and end_call tool`);
  } catch (e) {
    log(`[HYBRID] Error updating agent config: ${e.message}`);
  }

  // Register the call with ElevenLabs to get TwiML for WebSocket connection
  // This returns TwiML with <Connect><Stream> pointing to ElevenLabs' WebSocket
  try {
    const registerResult = await elevenLabsRequest('POST', '/v1/convai/twilio/register-call', {
      agent_id: ELEVEN_AGENT_ID,
      from_number: TWILIO_PHONE_NUMBER,
      to_number: session.callData.phoneNumber,
      direction: 'outbound'
    });

    log(`[HYBRID] Register-call response type: ${typeof registerResult}`);

    // registerResult should be TwiML (XML string) or an object with twiml
    let twiml = null;
    if (typeof registerResult === 'string' && registerResult.includes('<')) {
      twiml = registerResult;
    } else if (registerResult && registerResult.twiml) {
      twiml = registerResult.twiml;
    } else if (registerResult && registerResult.conversation_id) {
      // Some versions return conversation_id; build TwiML ourselves
      log(`[HYBRID] Got conversation_id: ${registerResult.conversation_id}, building TwiML`);
      if (callRecord) {
        callRecord.conversationId = registerResult.conversation_id;
        saveCalls();
      }
    }

    if (twiml) {
      log(`[HYBRID] Got TwiML from register-call, redirecting existing call`);

      // Redirect the EXISTING Twilio call to use the ElevenLabs TwiML
      // This swaps the audio stream from our hold-detector to the ElevenLabs agent
      // WITHOUT dropping the connection to the company
      await twilioClient.calls(callSid).update({ twiml });

      log(`[HYBRID] Call ${callSid} redirected to ElevenLabs conversation mode`);

      // Extract conversation_id from TwiML if present (it's usually in a parameter)
      const convoIdMatch = twiml.match(/conversation[_-]id[^>]*value="([^"]+)"/i) ||
                           twiml.match(/conversationId[^>]*value="([^"]+)"/i);
      if (convoIdMatch && callRecord) {
        callRecord.conversationId = convoIdMatch[1];
        saveCalls();
      }

      // Track the active call for cleanup when conversation ends
      activeConversationCalls.set(callSid, {
        callId: session.callId,
        startedAt: Date.now()
      });

      // Poll for conversation completion
      if (callRecord?.conversationId) {
        pollElevenLabsConversation(session.callId, callRecord.conversationId, callSid);
      } else {
        // Poll via call status instead
        pollCallCompletion(session.callId, callSid);
      }

      return;
    }

    // Fallback: If register-call didn't return usable TwiML,
    // try the redirect-to-TwiML-endpoint approach
    log(`[HYBRID] Register-call didn't return TwiML directly, using redirect endpoint`);
    await useRedirectFallback(callSid, session, callRecord);

  } catch (err) {
    log(`[HYBRID] Register-call failed: ${err.message}`);
    // Ultimate fallback: call Alex
    await fallbackCallAlex(session, callRecord);
  }
}

// Track active conversation calls (callSid -> { callId, startedAt })
const activeConversationCalls = new Map();

// Fallback: redirect to our own TwiML endpoint that does the register-call
async function useRedirectFallback(callSid, session, callRecord) {
  try {
    // Store session data for the redirect endpoint
    pendingRedirects.set(callSid, {
      callId: session.callId,
      callData: session.callData
    });

    // Redirect existing call to our bridge endpoint
    await twilioClient.calls(callSid).update({
      url: `${BASE_URL}/voice/hybrid-bridge`,
      method: 'POST'
    });

    log(`[HYBRID] Call ${callSid} redirected to bridge endpoint`);

    activeConversationCalls.set(callSid, {
      callId: session.callId,
      startedAt: Date.now()
    });

    pollCallCompletion(session.callId, callSid);
  } catch (e) {
    log(`[HYBRID] Redirect fallback failed: ${e.message}`);
    await fallbackCallAlex(session, callRecord);
  }
}

// Store pending redirects for the bridge endpoint
const pendingRedirects = new Map();

// TwiML endpoint: bridges existing call to ElevenLabs via register-call
app.post('/voice/hybrid-bridge', async (req, res) => {
  const callSid = req.body.CallSid;
  log(`[HYBRID] Bridge endpoint hit for call ${callSid}`);

  const pending = pendingRedirects.get(callSid);
  pendingRedirects.delete(callSid);

  try {
    // Register with ElevenLabs to get TwiML
    const registerResult = await elevenLabsRequest('POST', '/v1/convai/twilio/register-call', {
      agent_id: ELEVEN_AGENT_ID,
      from_number: TWILIO_PHONE_NUMBER,
      to_number: pending?.callData?.phoneNumber || req.body.To,
      direction: 'outbound'
    });

    let twiml = null;
    if (typeof registerResult === 'string' && registerResult.includes('<')) {
      twiml = registerResult;
    } else if (registerResult?.twiml) {
      twiml = registerResult.twiml;
    }

    if (twiml) {
      log(`[HYBRID] Bridge: returning ElevenLabs TwiML`);

      // Track conversation_id
      if (pending) {
        const convoIdMatch = twiml.match(/conversation[_-]id[^>]*value="([^"]+)"/i);
        if (convoIdMatch) {
          const callRecord = calls.find(c => c.callId === pending.callId);
          if (callRecord) {
            callRecord.conversationId = convoIdMatch[1];
            saveCalls();
            pollElevenLabsConversation(pending.callId, convoIdMatch[1], callSid);
          }
        }
      }

      res.type('text/xml').send(twiml);
    } else {
      // Last resort: connect the call to ElevenLabs phone number via <Dial>
      log(`[HYBRID] Bridge: register-call failed, using Dial fallback`);
      const dialTwiml = `<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Dial callerId="${TWILIO_PHONE_NUMBER}" timeout="10">
    <Number>${TWILIO_PHONE_NUMBER}</Number>
  </Dial>
</Response>`;
      res.type('text/xml').send(dialTwiml);
    }
  } catch (err) {
    log(`[HYBRID] Bridge error: ${err.message}`);
    // Emergency: just play a message
    res.type('text/xml').send(`<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Say voice="Google.en-US-Chirp3-HD-Aoede">I'm sorry, I'm having trouble connecting. Please hold while I get Alex on the line.</Say>
  <Pause length="7200"/>
</Response>`);
  }
});

// Poll call completion via Twilio status (when we don't have a conversation_id)
function pollCallCompletion(callId, callSid) {
  let pollCount = 0;
  const maxPolls = 360; // 30 min

  const interval = setInterval(async () => {
    pollCount++;
    if (pollCount > maxPolls) {
      clearInterval(interval);
      updateCall(callId, { status: 'completed', statusMessage: 'Conversation ended (timeout)' });
      activeConversationCalls.delete(callSid);
      resetAgentPrompt();
      return;
    }

    try {
      const call = await twilioClient.calls(callSid).fetch();
      if (['completed', 'failed', 'canceled', 'busy', 'no-answer'].includes(call.status)) {
        clearInterval(interval);
        log(`[HYBRID] Call ${callSid} ended with status: ${call.status}`);
        updateCall(callId, {
          status: 'completed',
          statusMessage: `Conversation completed (${call.status})`,
          completedAt: new Date().toISOString()
        });
        activeConversationCalls.delete(callSid);
        resetAgentPrompt();
      }
    } catch (err) {
      log(`[HYBRID] Poll call status error: ${err.message}`);
    }
  }, 5000);
}

// Fallback: call Alex when everything else fails
async function fallbackCallAlex(session, callRecord) {
  if (session.callData.callback) {
    log(`[HYBRID] Calling Alex as fallback...`);
    try {
      await twilioClient.calls.create({
        to: session.callData.callback,
        from: TWILIO_PHONE_NUMBER,
        twiml: `<Response><Say voice="Google.en-US-Chirp3-HD-Aoede">Hey, this is Debra. A human picked up at ${session.callData.company} but I couldn't switch to conversation mode. You may want to call them back right now. The number is ${session.callData.phoneNumber}.</Say></Response>`
      });
    } catch (e) {
      log(`[HYBRID] Fallback call to Alex failed: ${e.message}`);
    }
  }
  if (callRecord) {
    callRecord.status = 'error';
    callRecord.statusMessage = 'Failed to bridge to conversation mode. Alex notified.';
    saveCalls();
  }
}

// ─── Poll ElevenLabs conversation ──────────────────────────────────────────
async function pollElevenLabsConversation(callId, conversationId, callSid) {
  const maxPolls = 360; // 30 min
  let pollCount = 0;

  const interval = setInterval(async () => {
    pollCount++;
    if (pollCount > maxPolls) {
      clearInterval(interval);
      updateCall(callId, { status: 'completed', statusMessage: 'Conversation ended (timeout)' });
      if (callSid) activeConversationCalls.delete(callSid);
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
        if (callSid) activeConversationCalls.delete(callSid);
        resetAgentPrompt();

        // End the Twilio call if still active (belt & suspenders with end_call tool)
        if (callSid) {
          try {
            const call = await twilioClient.calls(callSid).fetch();
            if (!['completed', 'failed', 'canceled'].includes(call.status)) {
              log(`[HYBRID] Ending Twilio call ${callSid} after conversation done`);
              await twilioClient.calls(callSid).update({ status: 'completed' });
            }
          } catch (e) {
            // Call may already be ended, that's fine
          }
        }
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

              // Cleanly shut down the hold detector — audio routing is about to change
              if (holdDetector) {
                log(`[HYBRID] Shutting down hold detector before mode switch`);
                holdDetector.shutdown();
                holdDetector = null;
                session.holdDetector = null;
              }

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
    const { company, phoneNumber, task, reference, callback, ivrDigits } = req.body;
    if (!phoneNumber || !task) return res.status(400).json({ success: false, error: 'Phone number and task required' });

    const result = await startHoldModeCall({ company, phoneNumber, task, reference, callback, ivrDigits });
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

// ─── Recording endpoints ───────────────────────────────────────────────────

const RECORDINGS_DIR = path.join(__dirname, '..', 'recordings');

// Serve a recording by callSid (stream from local file or proxy from Twilio)
app.get('/api/recordings/:callSid', async (req, res) => {
  await serveRecording(req, res, false);
});

// Download a recording by callSid
app.get('/api/recordings/:callSid/download', async (req, res) => {
  await serveRecording(req, res, true);
});

async function serveRecording(req, res, asDownload) {
  const { callSid } = req.params;

  // Check local recordings directory first
  const localFile = findLocalRecording(callSid);
  if (localFile) {
    if (asDownload) {
      res.setHeader('Content-Disposition', `attachment; filename="${path.basename(localFile)}"`);
    }
    res.setHeader('Content-Type', 'audio/wav');
    return fs.createReadStream(localFile).pipe(res);
  }

  // Fetch from Twilio
  try {
    const recordings = await twilioClient.recordings.list({ callSid, limit: 1 });
    if (!recordings || recordings.length === 0) {
      return res.status(404).json({ error: 'No recording found for this call' });
    }

    const recording = recordings[0];
    const twilioUrl = `https://api.twilio.com${recording.uri.replace('.json', '.wav')}`;

    if (asDownload) {
      res.setHeader('Content-Disposition', `attachment; filename="${callSid}.wav"`);
    }
    res.setHeader('Content-Type', 'audio/wav');

    // Proxy the Twilio recording
    const authString = Buffer.from(`${TWILIO_ACCOUNT_SID}:${TWILIO_AUTH_TOKEN}`).toString('base64');
    https.get(twilioUrl, { headers: { 'Authorization': `Basic ${authString}` } }, (twilioRes) => {
      if (twilioRes.statusCode === 301 || twilioRes.statusCode === 302) {
        https.get(twilioRes.headers.location, (redirected) => {
          redirected.pipe(res);
        }).on('error', (err) => {
          log(`[HYBRID] Recording redirect error: ${err.message}`);
          if (!res.headersSent) res.status(500).json({ error: 'Failed to fetch recording' });
        });
        return;
      }
      if (twilioRes.statusCode !== 200) {
        log(`[HYBRID] Twilio recording fetch returned ${twilioRes.statusCode}`);
        if (!res.headersSent) res.status(502).json({ error: `Twilio returned ${twilioRes.statusCode}` });
        return;
      }
      twilioRes.pipe(res);
    }).on('error', (err) => {
      log(`[HYBRID] Recording fetch error: ${err.message}`);
      if (!res.headersSent) res.status(500).json({ error: 'Failed to fetch recording' });
    });
  } catch (err) {
    log(`[HYBRID] Recording endpoint error: ${err.message}`);
    res.status(500).json({ error: err.message });
  }
}

// Check if a recording has been downloaded (exists locally or on Twilio)
app.get('/api/recordings/:callSid/status', async (req, res) => {
  const { callSid } = req.params;

  // Check local
  if (findLocalRecording(callSid)) {
    return res.json({ available: true, source: 'local' });
  }

  // Check Twilio
  try {
    const recordings = await twilioClient.recordings.list({ callSid, limit: 1 });
    if (recordings && recordings.length > 0) {
      return res.json({ available: true, source: 'twilio' });
    }
  } catch (err) {
    log(`[HYBRID] Recording status check error: ${err.message}`);
  }

  res.json({ available: false });
});

function findLocalRecording(callSid) {
  if (!fs.existsSync(RECORDINGS_DIR)) return null;
  const files = fs.readdirSync(RECORDINGS_DIR);
  const match = files.find(f => f.startsWith(callSid) && f.endsWith('.wav'));
  return match ? path.join(RECORDINGS_DIR, match) : null;
}

// Auto-fetch recording after call completes
async function fetchAndSaveRecording(callSid) {
  try {
    // Wait a bit for Twilio to process the recording
    await new Promise(resolve => setTimeout(resolve, 5000));

    const recordings = await twilioClient.recordings.list({ callSid, limit: 1 });
    if (!recordings || recordings.length === 0) {
      log(`[HYBRID] No recording available yet for ${callSid}`);
      return null;
    }

    const recording = recordings[0];
    const recordingUrl = `https://api.twilio.com${recording.uri.replace('.json', '')}`;
    log(`[HYBRID] Auto-fetching recording for ${callSid}`);

    const result = await recorder.transcribeRecording(recordingUrl, callSid);
    log(`[HYBRID] Recording saved: ${result.audioPath}`);

    // Update the call record with recording info
    const call = calls.find(c => c.callSid === callSid);
    if (call) {
      call.recordingPath = result.audioPath;
      call.hasRecording = true;
      saveCalls();
    }

    return result;
  } catch (err) {
    log(`[HYBRID] Auto-fetch recording error: ${err.message}`);
    return null;
  }
}

// ─── End Call webhook (server-side fallback for ending calls) ───────────────
// This can be called by ElevenLabs server tool or manually to terminate a call
app.post('/api/end-call', async (req, res) => {
  const { callSid, callId, conversation_id } = req.body;
  log(`[HYBRID] End-call webhook received: callSid=${callSid}, callId=${callId}, conversation_id=${conversation_id}`);

  let targetCallSid = callSid;

  // Find the call by various identifiers
  if (!targetCallSid && callId) {
    const call = calls.find(c => c.callId === callId);
    if (call) targetCallSid = call.callSid;
  }
  if (!targetCallSid && conversation_id) {
    const call = calls.find(c => c.conversationId === conversation_id);
    if (call) targetCallSid = call.callSid;
  }

  // Also check active conversation calls
  if (!targetCallSid) {
    // End the most recent active conversation
    for (const [sid, info] of activeConversationCalls) {
      targetCallSid = sid;
      break;
    }
  }

  if (targetCallSid) {
    try {
      await twilioClient.calls(targetCallSid).update({ status: 'completed' });
      log(`[HYBRID] Call ${targetCallSid} terminated via end-call webhook`);
      activeConversationCalls.delete(targetCallSid);
      res.json({ success: true, message: 'Call ended' });
    } catch (e) {
      log(`[HYBRID] End-call error: ${e.message}`);
      res.json({ success: true, message: 'Call may have already ended' });
    }
  } else {
    log(`[HYBRID] End-call: no active call found to end`);
    res.json({ success: false, error: 'No active call found' });
  }
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
