/**
 * alerter.js - Alert user and conference them into the call
 *
 * When a human is detected on the line:
 * 1. Send SMS alert to the user
 * 2. Move the original call into a Twilio Conference
 * 3. Call the user and bridge them into the same conference
 * 4. If user doesn't join within 60s, gracefully hang up
 */

const twilio = require('twilio');
const { log, sleep } = require('./utils');

const client = twilio(process.env.TWILIO_ACCOUNT_SID, process.env.TWILIO_AUTH_TOKEN);

class Alerter {
  constructor() {
    this.alertSent = false;
  }

  /**
   * Send SMS alert and conference the user into the call.
   *
   * @param {Object} options
   * @param {string} options.callSid - The active call SID
   * @param {string} options.alertNumber - Phone number to alert
   * @param {string} options.baseUrl - Base URL for webhooks
   * @param {string} options.context - Context about the call (e.g., "Lufthansa baggage claim")
   */
  async alertAndConference({ callSid, alertNumber, baseUrl, context }) {
    if (this.alertSent) {
      log('[ALERT] Alert already sent, skipping');
      return;
    }

    this.alertSent = true;
    const conferenceName = `holdplease-${callSid}`;

    log(`[ALERT] 🚨 HUMAN DETECTED! Alerting ${alertNumber}`);
    log(`[ALERT] Conference name: ${conferenceName}`);

    // Step 1: Send SMS alert
    try {
      await this.sendSMS({
        to: alertNumber,
        body: `🚨 HoldPlease: Human picked up on your call! ${context ? `(${context})` : ''} Calling you now to connect...`
      });
      log('[ALERT] SMS sent successfully');
    } catch (err) {
      log(`[ALERT] SMS failed (continuing with call): ${err.message}`);
    }

    // Step 2: Move original call into conference
    try {
      log('[ALERT] Moving original call into conference...');
      await client.calls(callSid).update({
        twiml: `<Response>
          <Say voice="alice">Please hold one moment, I'm connecting you now.</Say>
          <Dial>
            <Conference endConferenceOnExit="false" statusCallback="${baseUrl}/conference/events" statusCallbackEvent="join leave end">
              ${conferenceName}
            </Conference>
          </Dial>
        </Response>`
      });
      log('[ALERT] Original call moved to conference');
    } catch (err) {
      log(`[ALERT] Failed to move call to conference: ${err.message}`);
      throw err;
    }

    // Step 3: Call the user and connect them to the conference
    try {
      log(`[ALERT] Calling ${alertNumber} to join conference...`);
      const userCall = await client.calls.create({
        to: alertNumber,
        from: process.env.TWILIO_PHONE_NUMBER,
        url: `${baseUrl}/voice/join-conference?conference=${encodeURIComponent(conferenceName)}`,
        statusCallback: `${baseUrl}/voice/status`,
        statusCallbackEvent: ['initiated', 'ringing', 'answered', 'completed'],
        timeout: 60
      });
      log(`[ALERT] User call created: ${userCall.sid}`);

      // Step 4: Monitor for user join (timeout after 60s)
      this.monitorConference(conferenceName, callSid, baseUrl);

    } catch (err) {
      log(`[ALERT] Failed to call user: ${err.message}`);
      // Try to let the rep know we'll call back
      await this.gracefulHangup(callSid);
      throw err;
    }
  }

  /**
   * Send an SMS message.
   */
  async sendSMS({ to, body }) {
    const message = await client.messages.create({
      to,
      from: process.env.TWILIO_PHONE_NUMBER,
      body
    });
    log(`[ALERT] SMS sent: ${message.sid}`);
    return message;
  }

  /**
   * Monitor conference for user join. If they don't join within 60s,
   * gracefully hang up.
   */
  async monitorConference(conferenceName, callSid, baseUrl) {
    const timeout = 60000; // 60 seconds
    const checkInterval = 5000; // Check every 5 seconds
    const startTime = Date.now();

    log(`[ALERT] Monitoring conference ${conferenceName} for user join (${timeout / 1000}s timeout)`);

    const check = async () => {
      const elapsed = Date.now() - startTime;

      if (elapsed >= timeout) {
        log('[ALERT] User did not join within 60s, gracefully hanging up');
        await this.gracefulHangup(callSid);
        return;
      }

      try {
        // Check conference participants
        const conferences = await client.conferences.list({
          friendlyName: conferenceName,
          status: 'in-progress',
          limit: 1
        });

        if (conferences.length > 0) {
          const participants = await client.conferences(conferences[0].sid)
            .participants.list();

          if (participants.length >= 2) {
            log(`[ALERT] ✅ User joined conference! ${participants.length} participants connected.`);
            return; // Success - both parties are connected
          }
        }
      } catch (err) {
        log(`[ALERT] Conference check error: ${err.message}`);
      }

      // Check again after interval
      setTimeout(check, checkInterval);
    };

    // Start checking after a short delay
    setTimeout(check, checkInterval);
  }

  /**
   * Gracefully hang up: tell the rep we'll call back.
   */
  async gracefulHangup(callSid) {
    try {
      await client.calls(callSid).update({
        twiml: `<Response>
          <Say voice="alice">I apologize, but I'll need to call back shortly. Thank you for your time.</Say>
          <Hangup/>
        </Response>`
      });
      log('[ALERT] Graceful hangup executed');
    } catch (err) {
      log(`[ALERT] Graceful hangup failed: ${err.message}`);
      // Force hangup
      try {
        await client.calls(callSid).update({ status: 'completed' });
      } catch (e) {
        log(`[ALERT] Force hangup also failed: ${e.message}`);
      }
    }
  }
}

module.exports = { Alerter };
