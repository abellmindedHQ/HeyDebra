/**
 * caller.js - Initiate outbound calls via Twilio
 *
 * Uses the Twilio REST API to place calls and configure TwiML callback URLs
 * for call flow management. Supports international numbers.
 */

const twilio = require('twilio');
const fs = require('fs');
const path = require('path');
const { log } = require('./utils');

const client = twilio(process.env.TWILIO_ACCOUNT_SID, process.env.TWILIO_AUTH_TOKEN);

// Load IVR scripts
const SCRIPTS_PATH = path.join(__dirname, '..', 'config', 'ivr-scripts.json');
let ivrScripts = {};
try {
  ivrScripts = JSON.parse(fs.readFileSync(SCRIPTS_PATH, 'utf-8'));
} catch (err) {
  log(`[CALLER] Warning: Could not load IVR scripts: ${err.message}`);
}

/**
 * Parse a navigate string like "1,0,rep" into IVR steps.
 * Numbers become DTMF, text becomes speech.
 */
function parseNavigateString(navString) {
  if (!navString) return [];

  return navString.split(',').map(item => {
    const trimmed = item.trim();

    // Pure digits = DTMF
    if (/^\d+$/.test(trimmed)) {
      return { action: 'dtmf', digit: trimmed, label: `Press ${trimmed}` };
    }

    // Special shortcuts
    const shortcuts = {
      'rep': 'representative',
      'agent': 'agent',
      'human': 'operator',
      'op': 'operator',
      'help': 'help'
    };

    const speechText = shortcuts[trimmed.toLowerCase()] || trimmed;
    return { action: 'speech', text: speechText, label: `Say "${speechText}"` };
  }).reduce((steps, step, i) => {
    // Insert waits between steps
    if (i > 0) {
      steps.push({ action: 'wait', seconds: 3 });
    }
    steps.push(step);
    return steps;
  }, [{ action: 'wait', seconds: 5 }]); // Always wait 5s at start
}

/**
 * Initiate an outbound call.
 *
 * @param {Object} options
 * @param {string} options.to - Phone number to call
 * @param {string} [options.script] - Name of IVR script from config (e.g., "lufthansa")
 * @param {string} [options.navigate] - Navigation string (e.g., "1,0,rep")
 * @param {string} options.alertNumber - Phone number to alert when human detected
 * @param {string} options.baseUrl - Base URL for webhooks
 * @returns {Object} Call state object
 */
async function initCall({ to, script, navigate, alertNumber, baseUrl }) {
  // Determine target number and IVR steps
  let targetNumber = to;
  let ivrSteps = [];
  let context = '';

  if (script && ivrScripts[script]) {
    const scriptConfig = ivrScripts[script];
    targetNumber = targetNumber || scriptConfig.number;
    ivrSteps = scriptConfig.steps;
    context = scriptConfig.context || '';
    log(`[CALLER] Using IVR script: ${script}`);
    log(`[CALLER] Steps: ${ivrSteps.map(s => s.label || s.action).join(' -> ')}`);
  } else if (navigate) {
    ivrSteps = parseNavigateString(navigate);
    log(`[CALLER] Using navigate string: ${navigate}`);
  }

  if (!targetNumber) {
    throw new Error('No target phone number provided');
  }

  log(`[CALLER] Initiating call to ${targetNumber}`);
  log(`[CALLER] Alert number: ${alertNumber}`);
  log(`[CALLER] Context: ${context || 'none'}`);

  const call = await client.calls.create({
    to: targetNumber,
    from: process.env.TWILIO_PHONE_NUMBER,
    url: `${baseUrl}/voice/outbound`,
    statusCallback: `${baseUrl}/voice/status`,
    statusCallbackEvent: ['initiated', 'ringing', 'answered', 'completed'],
    statusCallbackMethod: 'POST',
    record: true,
    machineDetection: 'Enable',
    timeout: 60
  });

  log(`[CALLER] Call created: ${call.sid} (status: ${call.status})`);

  return {
    callSid: call.sid,
    to: targetNumber,
    alertNumber,
    ivrSteps,
    context,
    status: call.status,
    startedAt: new Date().toISOString(),
    recorder: null,
    recordingUrl: null,
    recordingSid: null
  };
}

module.exports = { initCall, parseNavigateString };
