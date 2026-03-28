/**
 * recorder.js - Call recording and post-call transcript generation
 *
 * Handles fetching Twilio call recordings and running them through
 * Whisper for full post-call transcription.
 */

const twilio = require('twilio');
const fs = require('fs');
const path = require('path');
const https = require('https');
const { Transcriber } = require('./transcriber');
const { log } = require('./utils');

const client = twilio(process.env.TWILIO_ACCOUNT_SID, process.env.TWILIO_AUTH_TOKEN);

// Directory for saved recordings and transcripts
const OUTPUT_DIR = path.join(__dirname, '..', 'recordings');

class Recorder {
  constructor() {
    this.transcriber = new Transcriber();

    // Ensure output directory exists
    if (!fs.existsSync(OUTPUT_DIR)) {
      fs.mkdirSync(OUTPUT_DIR, { recursive: true });
    }
  }

  /**
   * Download a Twilio recording and transcribe it.
   *
   * @param {string} recordingUrl - Twilio recording URL
   * @param {string} callSid - Call SID for file naming
   * @returns {Object} { audioPath, transcriptPath, transcript }
   */
  async transcribeRecording(recordingUrl, callSid) {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const audioFilename = `${callSid}-${timestamp}.wav`;
    const transcriptFilename = `${callSid}-${timestamp}-transcript.txt`;
    const audioPath = path.join(OUTPUT_DIR, audioFilename);
    const transcriptPath = path.join(OUTPUT_DIR, transcriptFilename);

    log(`[RECORDER] Downloading recording for call ${callSid}`);

    // Download the recording
    try {
      await this.downloadRecording(`${recordingUrl}.wav`, audioPath);
      log(`[RECORDER] Recording saved: ${audioPath}`);
    } catch (err) {
      log(`[RECORDER] Download failed: ${err.message}`);
      throw err;
    }

    // Transcribe
    try {
      const result = await this.transcriber.transcribeFile(audioPath);
      const transcript = this.formatTranscript(result, callSid);

      fs.writeFileSync(transcriptPath, transcript, 'utf-8');
      log(`[RECORDER] Transcript saved: ${transcriptPath}`);

      return { audioPath, transcriptPath, transcript };
    } catch (err) {
      log(`[RECORDER] Transcription failed: ${err.message}`);
      throw err;
    }
  }

  /**
   * Download a file from a URL.
   */
  downloadRecording(url, outputPath) {
    return new Promise((resolve, reject) => {
      // Twilio recordings need authentication
      const authUrl = url.includes('?')
        ? `${url}&AccountSid=${process.env.TWILIO_ACCOUNT_SID}`
        : url;

      const file = fs.createWriteStream(outputPath);

      https.get(authUrl, {
        auth: `${process.env.TWILIO_ACCOUNT_SID}:${process.env.TWILIO_AUTH_TOKEN}`
      }, (response) => {
        // Handle redirects
        if (response.statusCode === 301 || response.statusCode === 302) {
          https.get(response.headers.location, (redirected) => {
            redirected.pipe(file);
            file.on('finish', () => {
              file.close();
              resolve();
            });
          }).on('error', reject);
          return;
        }

        if (response.statusCode !== 200) {
          reject(new Error(`Download failed: HTTP ${response.statusCode}`));
          return;
        }

        response.pipe(file);
        file.on('finish', () => {
          file.close();
          resolve();
        });
      }).on('error', (err) => {
        fs.unlink(outputPath, () => {}); // Clean up partial file
        reject(err);
      });
    });
  }

  /**
   * Format a Whisper transcription result into a readable transcript.
   */
  formatTranscript(whisperResult, callSid) {
    const lines = [
      `HoldPlease Call Transcript`,
      `Call SID: ${callSid}`,
      `Date: ${new Date().toISOString()}`,
      `${'─'.repeat(60)}`,
      ''
    ];

    if (whisperResult.segments) {
      for (const segment of whisperResult.segments) {
        const startTime = this.formatTime(segment.start);
        const endTime = this.formatTime(segment.end);
        lines.push(`[${startTime} - ${endTime}] ${segment.text.trim()}`);
      }
    } else if (whisperResult.text) {
      lines.push(whisperResult.text);
    }

    lines.push('');
    lines.push(`${'─'.repeat(60)}`);
    lines.push(`End of transcript`);

    return lines.join('\n');
  }

  /**
   * Format seconds to MM:SS.
   */
  formatTime(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  }
}

module.exports = { Recorder };
