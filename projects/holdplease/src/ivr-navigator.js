/**
 * ivr-navigator.js - IVR menu navigation via DTMF and speech
 *
 * Sends DTMF tones and speech inputs to navigate phone menus.
 * Supports configurable sequences with waits between steps.
 */

const twilio = require('twilio');
const { log, sleep } = require('./utils');

const client = twilio(process.env.TWILIO_ACCOUNT_SID, process.env.TWILIO_AUTH_TOKEN);

class IVRNavigator {
  constructor(callSid) {
    this.callSid = callSid;
    this.currentStep = 0;
    this.aborted = false;
  }

  /**
   * Execute a sequence of IVR navigation steps.
   *
   * @param {Array} steps - Array of step objects:
   *   { action: 'wait', seconds: 5 }
   *   { action: 'dtmf', digit: '1', label: 'English' }
   *   { action: 'speech', text: 'representative', label: 'Get human' }
   */
  async executeSteps(steps) {
    log(`[IVR] Starting navigation: ${steps.length} steps for call ${this.callSid}`);

    for (let i = 0; i < steps.length; i++) {
      if (this.aborted) {
        log(`[IVR] Navigation aborted at step ${i + 1}`);
        return;
      }

      const step = steps[i];
      this.currentStep = i;

      try {
        switch (step.action) {
          case 'wait':
            log(`[IVR] Step ${i + 1}/${steps.length}: Waiting ${step.seconds}s${step.label ? ` (${step.label})` : ''}`);
            await sleep(step.seconds * 1000);
            break;

          case 'dtmf':
            log(`[IVR] Step ${i + 1}/${steps.length}: Sending DTMF '${step.digit}'${step.label ? ` (${step.label})` : ''}`);
            await this.sendDTMF(step.digit);
            break;

          case 'speech':
            log(`[IVR] Step ${i + 1}/${steps.length}: Speaking "${step.text}"${step.label ? ` (${step.label})` : ''}`);
            await this.sendSpeech(step.text);
            break;

          default:
            log(`[IVR] Step ${i + 1}/${steps.length}: Unknown action '${step.action}', skipping`);
        }
      } catch (err) {
        log(`[IVR] Error at step ${i + 1}: ${err.message}`);
        // Continue to next step on error
      }
    }

    log(`[IVR] Navigation complete for call ${this.callSid}`);
  }

  /**
   * Send DTMF tones to the call.
   * Uses Twilio's call update API to play digits.
   */
  async sendDTMF(digits) {
    try {
      // Use TwiML to play DTMF tones
      const twiml = `<Response><Play digits="${digits}"/><Pause length="7200"/></Response>`;
      await client.calls(this.callSid).update({ twiml });
      log(`[IVR] DTMF '${digits}' sent to call ${this.callSid}`);
    } catch (err) {
      log(`[IVR] Failed to send DTMF '${digits}': ${err.message}`);
      throw err;
    }
  }

  /**
   * Send speech to the call.
   * Uses Twilio's TwiML <Say> to speak text into the call.
   */
  async sendSpeech(text) {
    try {
      const twiml = `<Response><Say voice="alice">${text}</Say><Pause length="7200"/></Response>`;
      await client.calls(this.callSid).update({ twiml });
      log(`[IVR] Speech "${text}" sent to call ${this.callSid}`);
    } catch (err) {
      log(`[IVR] Failed to send speech "${text}": ${err.message}`);
      throw err;
    }
  }

  /**
   * Abort the current navigation sequence.
   */
  abort() {
    this.aborted = true;
    log(`[IVR] Aborting navigation for call ${this.callSid}`);
  }
}

module.exports = { IVRNavigator };
