/**
 * holdplease-api.js - HoldPlease Web API
 *
 * Web interface backend for HoldPlease. Accepts call requests via REST API,
 * uses ElevenLabs Conversational AI to make the call with Debra's voice,
 * monitors call progress, and saves outcomes.
 */

require('dotenv').config();
const express = require('express');
const path = require('path');
const fs = require('fs');
const https = require('https');
const { log } = require('./utils');

const app = express();
app.use(express.json());
app.use(express.static(path.join(__dirname, '..', 'web')));

const PORT = process.env.HOLDPLEASE_PORT || 3981;

const ELEVEN_API_KEY = process.env.ELEVEN_LABS_API_KEY;
const ELEVEN_AGENT_ID = process.env.ELEVEN_AGENT_ID || 'agent_5201kmtfqfv9etgtafvgw16pjpza';
const ELEVEN_PHONE_ID = process.env.ELEVEN_PHONE_ID || 'phnum_6601kmtfr2scffj9rv4fb7fcfrtj';

// In-memory call store (persists to JSON file)
const CALLS_FILE = path.join(__dirname, '..', 'data', 'calls.json');
let calls = loadCalls();

function loadCalls() {
  try {
    const dir = path.dirname(CALLS_FILE);
    if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
    if (fs.existsSync(CALLS_FILE)) {
      return JSON.parse(fs.readFileSync(CALLS_FILE, 'utf-8'));
    }
  } catch (err) {
    log(`[API] Error loading calls: ${err.message}`);
  }
  return [];
}

function saveCalls() {
  try {
    const dir = path.dirname(CALLS_FILE);
    if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
    fs.writeFileSync(CALLS_FILE, JSON.stringify(calls, null, 2));
  } catch (err) {
    log(`[API] Error saving calls: ${err.message}`);
  }
}

// ─── Helper: ElevenLabs API call ───────────────────────────────────────────
function elevenLabsRequest(method, path, body) {
  return new Promise((resolve, reject) => {
    const data = body ? JSON.stringify(body) : null;
    const options = {
      hostname: 'api.elevenlabs.io',
      path,
      method,
      headers: {
        'xi-api-key': ELEVEN_API_KEY,
        'Content-Type': 'application/json'
      }
    };

    const req = https.request(options, (res) => {
      let responseBody = '';
      res.on('data', d => responseBody += d);
      res.on('end', () => {
        try {
          resolve(JSON.parse(responseBody));
        } catch (e) {
          resolve(responseBody);
        }
      });
    });
    req.on('error', reject);
    if (data) req.write(data);
    req.end();
  });
}

// ─── Build context prompt for a call ───────────────────────────────────────
function buildCallPrompt(callData) {
  let prompt = `You are Debra, calling ${callData.company || 'a company'} on behalf of Alex Abell.\n\n`;
  prompt += `TASK: ${callData.task}\n\n`;

  if (callData.reference) {
    prompt += `REFERENCE NUMBERS/ACCOUNT INFO: ${callData.reference}\n\n`;
  }

  prompt += `RULES:\n`;
  prompt += `- Be polite but firm. You are calling as Alex's assistant.\n`;
  prompt += `- Navigate any IVR/phone tree to reach a human.\n`;
  prompt += `- State clearly what you need and provide reference numbers when asked.\n`;
  prompt += `- If they need to verify identity and you don't have the info, say "Let me check with Alex and call back."\n`;
  prompt += `- Take detailed notes of everything the representative says.\n`;
  prompt += `- Get the representative's name and any new reference/confirmation numbers.\n`;
  prompt += `- Summarize the outcome at the end of the call.\n`;
  prompt += `- Keep it professional but warm. You're Debra.\n`;

  return prompt;
}

// ─── API: Look up a company phone number ──────────────────────────────────
app.post('/api/lookup', async (req, res) => {
  try {
    const { company } = req.body;
    if (!company) {
      return res.status(400).json({ success: false, error: 'Company name required' });
    }

    log(`[HP] Looking up phone number for: ${company}`);

    // Use OpenAI to extract phone numbers from a web search query
    const searchQuery = `${company} customer service phone number USA`;

    // Hit OpenAI with a smart extraction prompt
    const extractionResult = await new Promise((resolve, reject) => {
      const data = JSON.stringify({
        model: 'gpt-4o-mini',
        messages: [{
          role: 'system',
          content: 'You find customer service phone numbers. Return ONLY a JSON array of objects with "name", "phone", and "department" fields. No markdown, no explanation. If you know the number from training data, return it. Format phone as +1XXXXXXXXXX. Max 3 results, most relevant first.'
        }, {
          role: 'user',
          content: `Find the customer service phone number(s) for: ${company}`
        }],
        max_tokens: 300,
        temperature: 0
      });

      const options = {
        hostname: 'api.openai.com',
        path: '/v1/chat/completions',
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${process.env.OPENAI_API_KEY}`,
          'Content-Type': 'application/json'
        }
      };

      const req = https.request(options, (res) => {
        let body = '';
        res.on('data', d => body += d);
        res.on('end', () => {
          try {
            const json = JSON.parse(body);
            const content = json.choices[0].message.content.trim();
            // Parse the JSON array from the response
            const cleaned = content.replace(/```json\n?/g, '').replace(/```\n?/g, '').trim();
            resolve(JSON.parse(cleaned));
          } catch (e) { resolve(null); }
        });
      });
      req.on('error', reject);
      req.write(data);
      req.end();
    });

    if (extractionResult && Array.isArray(extractionResult) && extractionResult.length > 0) {
      const results = extractionResult.map(r => ({
        name: r.name || company,
        phone: r.phone,
        address: r.department || ''
      }));
      log(`[HP] Found ${results.length} numbers for ${company}`);
      return res.json({ success: true, results });
    }

    // Fallback: goplaces for local businesses
    const { execSync } = require('child_process');
    try {
      const result = execSync(
        `goplaces search "${company.replace(/"/g, '\\"')}" --fields name,phone,address --json 2>/dev/null`,
        { encoding: 'utf-8', timeout: 10000 }
      ).trim();

      if (result) {
        const places = JSON.parse(result);
        if (places && places.length > 0) {
          const matches = places.filter(p => p.phone).slice(0, 3).map(p => ({
            name: p.name, phone: p.phone, address: p.address || ''
          }));
          if (matches.length > 0) {
            return res.json({ success: true, results: matches });
          }
        }
      }
    } catch (e) {
      log(`[HP] goplaces fallback error: ${e.message}`);
    }

    res.json({ success: false, error: 'Could not find a phone number. Please enter it manually.' });
  } catch (err) {
    log(`[HP] Lookup error: ${err.message}`);
    res.status(500).json({ success: false, error: err.message });
  }
});

// ─── API: Start a HoldPlease call ──────────────────────────────────────────
app.post('/api/holdplease', async (req, res) => {
  try {
    const { company, phoneNumber, task, reference, callback } = req.body;

    if (!phoneNumber || !task) {
      return res.status(400).json({ success: false, error: 'Phone number and task are required' });
    }

    const callId = `hp_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
    const callPrompt = buildCallPrompt({ company, task, reference });

    log(`[HP] Starting call ${callId} to ${phoneNumber}`);
    log(`[HP] Task: ${task}`);

    // Update agent prompt for this specific call
    await elevenLabsRequest('PATCH', `/v1/convai/agents/${ELEVEN_AGENT_ID}`, {
      conversation_config: {
        agent: {
          prompt: {
            prompt: callPrompt
          },
          first_message: `Hi, this is Debra calling on behalf of Alex Abell. ${task.split('.')[0]}.`
        }
      }
    });

    // Make the outbound call
    const callResult = await elevenLabsRequest('POST', '/v1/convai/twilio/outbound-call', {
      agent_id: ELEVEN_AGENT_ID,
      agent_phone_number_id: ELEVEN_PHONE_ID,
      to_number: phoneNumber
    });

    if (!callResult.success) {
      throw new Error(callResult.message || 'Failed to initiate call');
    }

    const callRecord = {
      callId,
      conversationId: callResult.conversation_id,
      callSid: callResult.callSid,
      company: company || phoneNumber,
      phoneNumber,
      task,
      reference,
      callback,
      status: 'in-progress',
      statusMessage: 'Calling...',
      startedAt: new Date().toISOString(),
      transcript: [],
      outcome: null
    };

    calls.unshift(callRecord);
    saveCalls();

    // Start polling ElevenLabs for conversation status
    pollConversation(callId, callResult.conversation_id);

    res.json({
      success: true,
      callId,
      conversationId: callResult.conversation_id
    });
  } catch (err) {
    log(`[HP] Error: ${err.message}`);
    res.status(500).json({ success: false, error: err.message });
  }
});

// ─── API: Call history (MUST be before :callId route) ──────────────────────
app.get('/api/holdplease/history', (req, res) => {
  res.json({ calls: calls.slice(0, 20) });
});

// ─── API: Get call status ──────────────────────────────────────────────────
app.get('/api/holdplease/:callId', (req, res) => {
  const call = calls.find(c => c.callId === req.params.callId);
  if (!call) {
    return res.status(404).json({ success: false, error: 'Call not found' });
  }
  res.json(call);
});

// ─── Poll ElevenLabs conversation for updates ──────────────────────────────
async function pollConversation(callId, conversationId) {
  const maxPolls = 120; // 10 min max
  let pollCount = 0;

  const interval = setInterval(async () => {
    pollCount++;
    if (pollCount > maxPolls) {
      clearInterval(interval);
      updateCall(callId, { status: 'completed', statusMessage: 'Call ended (timeout)' });
      return;
    }

    try {
      const convo = await elevenLabsRequest('GET', `/v1/convai/conversations/${conversationId}`);

      if (convo.status === 'done' || convo.status === 'failed') {
        clearInterval(interval);

        // Extract transcript
        const transcript = [];
        if (convo.transcript) {
          for (const turn of convo.transcript) {
            transcript.push({
              role: turn.role === 'agent' ? 'debra' : 'them',
              text: turn.message || turn.text || ''
            });
          }
        }

        updateCall(callId, {
          status: convo.status === 'done' ? 'completed' : 'failed',
          statusMessage: convo.status === 'done' ? 'Call completed' : 'Call failed',
          transcript,
          completedAt: new Date().toISOString()
        });

        log(`[HP] Call ${callId} completed. ${transcript.length} transcript entries.`);

        // Reset agent to default prompt after call
        resetAgentPrompt();
      }
    } catch (err) {
      log(`[HP] Poll error for ${callId}: ${err.message}`);
    }
  }, 5000);
}

function updateCall(callId, updates) {
  const call = calls.find(c => c.callId === callId);
  if (call) {
    Object.assign(call, updates);
    saveCalls();
  }
}

async function resetAgentPrompt() {
  try {
    await elevenLabsRequest('PATCH', `/v1/convai/agents/${ELEVEN_AGENT_ID}`, {
      conversation_config: {
        agent: {
          prompt: {
            prompt: `You are Debra, Alex Abell's executive assistant. You are warm, grounded, and genuinely caring. Think of yourself as a trusted friend who happens to be incredibly competent.\n\nPersonality:\n- Warm and friendly first, witty second. Never snarky or sarcastic.\n- You say things like sugar, hon, baby naturally but sparingly.\n- You are confident but never condescending.\n- You listen more than you talk. Short responses unless someone needs detail.\n- You genuinely care about the people you talk to.\n\nPhone call rules:\n- Keep responses to 1-3 sentences. Shorter is better.\n- No markdown, no emojis. This is voice.\n- Use contractions. Talk like a real person.\n- If someone asks who you are, say you're Debra, Alex's assistant.`
          },
          first_message: "Hey, it's Debra. How can I help you?"
        }
      }
    });
  } catch (err) {
    log(`[HP] Error resetting agent: ${err.message}`);
  }
}

// ─── Health check ──────────────────────────────────────────────────────────
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', mode: 'holdplease', calls: calls.length });
});

// ─── Serve the web UI ──────────────────────────────────────────────────────
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, '..', 'web', 'index.html'));
});

// ─── Start ─────────────────────────────────────────────────────────────────
app.listen(PORT, () => {
  log(`[HP] HoldPlease web UI running on http://localhost:${PORT}`);
  log(`[HP] Agent: ${ELEVEN_AGENT_ID}`);
  log(`[HP] Phone: ${ELEVEN_PHONE_ID}`);
  log(`[HP] Calls stored: ${calls.length}`);
});

module.exports = { app };
