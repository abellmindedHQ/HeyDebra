require('dotenv').config();
const express = require('express');
const { WebSocketServer } = require('ws');
const http = require('http');
const { HoldDetector } = require('./hold-detector');
const { Alerter } = require('./alerter');
const { IVRNavigator } = require('./ivr-navigator');
const { Recorder } = require('./recorder');
const { log } = require('./utils');

const app = express();
app.use(express.urlencoded({ extended: true }));
app.use(express.json());

const server = http.createServer(app);
const PORT = process.env.PORT || 3978;
const BASE_URL = process.env.BASE_URL || `http://localhost:${PORT}`;

// Track active calls
const activeCalls = new Map();

// ─── Twilio Webhook: Call answered ─────────────────────────────────────────
app.post('/voice/outbound', (req, res) => {
  const callSid = req.body.CallSid;
  const callState = activeCalls.get(callSid);
  log(`[WEBHOOK] Outbound call answered: ${callSid}`);

  // Start recording
  const recorder = new Recorder();
  if (callState) {
    callState.recorder = recorder;
  }

  // TwiML: start media stream + recording, then pause to keep call alive
  const twiml = `<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Start>
    <Stream url="wss://${new URL(BASE_URL).host}/media-stream" track="inbound_track">
      <Parameter name="callSid" value="${callSid}" />
    </Stream>
  </Start>
  <Record recordingStatusCallback="${BASE_URL}/recording-status" recordingStatusCallbackEvent="completed" />
  <Pause length="7200" />
</Response>`;

  res.type('text/xml').send(twiml);
});

// ─── Twilio Webhook: Call status updates ───────────────────────────────────
app.post('/voice/status', (req, res) => {
  const { CallSid, CallStatus, CallDuration } = req.body;
  log(`[STATUS] Call ${CallSid}: ${CallStatus} (duration: ${CallDuration || 'n/a'}s)`);

  if (['completed', 'failed', 'busy', 'no-answer', 'canceled'].includes(CallStatus)) {
    const callState = activeCalls.get(CallSid);
    if (callState) {
      callState.status = CallStatus;
      // Post-call transcription
      if (callState.recorder && callState.recordingUrl) {
        callState.recorder.transcribeRecording(callState.recordingUrl, CallSid)
          .then(transcript => log(`[TRANSCRIPT] Saved for call ${CallSid}`))
          .catch(err => log(`[ERROR] Transcription failed: ${err.message}`));
      }
      activeCalls.delete(CallSid);
    }
  }
  res.sendStatus(200);
});

// ─── Twilio Webhook: Recording completed ───────────────────────────────────
app.post('/recording-status', (req, res) => {
  const { CallSid, RecordingUrl, RecordingSid } = req.body;
  log(`[RECORDING] Call ${CallSid}: Recording ready at ${RecordingUrl}`);

  const callState = activeCalls.get(CallSid);
  if (callState) {
    callState.recordingUrl = RecordingUrl;
    callState.recordingSid = RecordingSid;
  }
  res.sendStatus(200);
});

// ─── Twilio Webhook: Conference events ─────────────────────────────────────
app.post('/conference/events', (req, res) => {
  const { ConferenceSid, StatusCallbackEvent, CallSid } = req.body;
  log(`[CONFERENCE] ${StatusCallbackEvent} - Conference: ${ConferenceSid}, Call: ${CallSid}`);
  res.sendStatus(200);
});

// ─── TwiML for conferencing the user in ────────────────────────────────────
app.post('/voice/join-conference', (req, res) => {
  const conferenceName = req.query.conference || 'holdplease-conference';
  log(`[CONFERENCE] User joining conference: ${conferenceName}`);

  const twiml = `<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Say voice="alice">Connecting you now. The representative is on the line.</Say>
  <Dial>
    <Conference endConferenceOnExit="true" statusCallback="${BASE_URL}/conference/events" statusCallbackEvent="join leave end">
      ${conferenceName}
    </Conference>
  </Dial>
</Response>`;

  res.type('text/xml').send(twiml);
});

// ─── TwiML to move original call into conference ───────────────────────────
app.post('/voice/bridge-to-conference', (req, res) => {
  const conferenceName = req.query.conference || 'holdplease-conference';
  log(`[CONFERENCE] Bridging original call to conference: ${conferenceName}`);

  const twiml = `<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Say voice="alice">Please hold one moment, I'm connecting you now.</Say>
  <Dial>
    <Conference endConferenceOnExit="false" statusCallback="${BASE_URL}/conference/events" statusCallbackEvent="join leave end">
      ${conferenceName}
    </Conference>
  </Dial>
</Response>`;

  res.type('text/xml').send(twiml);
});

// ─── Health check ──────────────────────────────────────────────────────────
app.get('/health', (req, res) => {
  res.json({
    status: 'ok',
    activeCalls: activeCalls.size,
    uptime: process.uptime()
  });
});

// ─── API: Initiate a call ──────────────────────────────────────────────────
app.post('/api/call', async (req, res) => {
  try {
    const { number, script, navigate, alertNumber } = req.body;
    const { initCall } = require('./caller');

    const callState = await initCall({
      to: number,
      script,
      navigate,
      alertNumber: alertNumber || process.env.ALERT_PHONE_NUMBER,
      baseUrl: BASE_URL
    });

    activeCalls.set(callState.callSid, callState);
    log(`[API] Call initiated: ${callState.callSid} -> ${number}`);

    res.json({
      success: true,
      callSid: callState.callSid,
      to: number,
      status: 'initiating'
    });
  } catch (err) {
    log(`[ERROR] Failed to initiate call: ${err.message}`);
    res.status(500).json({ success: false, error: err.message });
  }
});

// ─── WebSocket: Twilio Media Streams ───────────────────────────────────────
const wss = new WebSocketServer({ server, path: '/media-stream' });

wss.on('connection', (ws, req) => {
  log('[WS] Media stream connected');

  let streamSid = null;
  let callSid = null;
  let holdDetector = null;
  let alerter = null;
  let ivrNavigator = null;
  let humanDetected = false;

  ws.on('message', async (data) => {
    try {
      const msg = JSON.parse(data);

      switch (msg.event) {
        case 'connected':
          log('[WS] Media stream: connected event');
          break;

        case 'start':
          streamSid = msg.start.streamSid;
          callSid = msg.start.customParameters?.callSid;
          log(`[WS] Stream started: ${streamSid} for call ${callSid}`);

          // Initialize detectors
          holdDetector = new HoldDetector();
          alerter = new Alerter();

          // Get call state for IVR navigation
          const callState = callSid ? activeCalls.get(callSid) : null;
          if (callState && callState.ivrSteps) {
            ivrNavigator = new IVRNavigator(callSid);
            ivrNavigator.executeSteps(callState.ivrSteps)
              .then(() => log(`[IVR] Navigation complete for ${callSid}`))
              .catch(err => log(`[IVR] Navigation error: ${err.message}`));
          }

          // Set up human detection callback
          holdDetector.on('humanDetected', async (info) => {
            if (humanDetected) return; // Only alert once
            humanDetected = true;

            log(`[DETECT] 🚨 HUMAN DETECTED on call ${callSid}! Reason: ${info.reason}`);
            log(`[DETECT] Transcript: "${info.transcript}"`);

            const alertNumber = callState?.alertNumber || process.env.ALERT_PHONE_NUMBER;
            try {
              await alerter.alertAndConference({
                callSid,
                alertNumber,
                baseUrl: BASE_URL,
                context: callState?.context || 'Your call'
              });
            } catch (err) {
              log(`[ERROR] Alert/conference failed: ${err.message}`);
            }
          });
          break;

        case 'media':
          // Feed audio to hold detector
          if (holdDetector && !humanDetected) {
            const audioPayload = msg.media.payload; // base64 mulaw audio
            holdDetector.processAudio(audioPayload, msg.media.timestamp);
          }
          break;

        case 'stop':
          log(`[WS] Stream stopped: ${streamSid}`);
          if (holdDetector) {
            holdDetector.shutdown();
          }
          break;
      }
    } catch (err) {
      log(`[WS] Error processing message: ${err.message}`);
    }
  });

  ws.on('close', () => {
    log(`[WS] Media stream disconnected: ${streamSid}`);
    if (holdDetector) {
      holdDetector.shutdown();
    }
  });

  ws.on('error', (err) => {
    log(`[WS] Media stream error: ${err.message}`);
  });
});

// ─── Start server ──────────────────────────────────────────────────────────
server.listen(PORT, () => {
  log(`[SERVER] HoldPlease running on port ${PORT}`);
  log(`[SERVER] Base URL: ${BASE_URL}`);
  log(`[SERVER] WebSocket path: /media-stream`);
  log(`[SERVER] Health check: ${BASE_URL}/health`);
  log(`[SERVER] Alert number: ${process.env.ALERT_PHONE_NUMBER || 'NOT SET'}`);
});

module.exports = { app, server, activeCalls };

// Serve static audio files
const path = require('path');
app.use('/audio', require('express').static(path.join(__dirname, '..', 'public')));
