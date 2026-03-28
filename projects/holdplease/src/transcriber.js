/**
 * transcriber.js - OpenAI Whisper API integration
 *
 * Handles periodic audio transcription for hold detection and
 * post-call full transcript generation.
 */

const OpenAI = require('openai');
const fs = require('fs');
const path = require('path');
const { log } = require('./utils');

const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

class Transcriber {
  constructor() {
    this.totalTranscriptions = 0;
    this.totalTokens = 0;
  }

  /**
   * Transcribe a chunk of mulaw audio using Whisper.
   * Converts the raw mulaw buffer to a WAV file for the API.
   *
   * @param {Buffer} mulawBuffer - Raw mulaw audio at 8kHz
   * @returns {string} Transcription text
   */
  async transcribeChunk(mulawBuffer) {
    // Create a proper WAV header for mulaw audio
    const wavBuffer = this.createMulawWav(mulawBuffer);

    // Write to temp file (Whisper API requires a file)
    const tempFile = path.join('/tmp', `holdplease-chunk-${Date.now()}.wav`);

    try {
      fs.writeFileSync(tempFile, wavBuffer);

      const transcription = await openai.audio.transcriptions.create({
        file: fs.createReadStream(tempFile),
        model: 'whisper-1',
        language: 'en',
        response_format: 'text',
        temperature: 0.2
      });

      this.totalTranscriptions++;
      log(`[TRANSCRIBE] Chunk transcribed (${mulawBuffer.length} bytes -> "${transcription.substring(0, 100)}...")`);

      return transcription;
    } catch (err) {
      if (err.status === 429) {
        log('[TRANSCRIBE] Rate limited by Whisper API, will retry next cycle');
      } else {
        log(`[TRANSCRIBE] Error: ${err.message}`);
      }
      throw err;
    } finally {
      // Clean up temp file
      try { fs.unlinkSync(tempFile); } catch (e) { /* ignore */ }
    }
  }

  /**
   * Transcribe a complete audio file (for post-call transcription).
   *
   * @param {string} filePath - Path to audio file (wav, mp3, etc.)
   * @returns {string} Full transcription
   */
  async transcribeFile(filePath) {
    log(`[TRANSCRIBE] Transcribing file: ${filePath}`);

    try {
      const transcription = await openai.audio.transcriptions.create({
        file: fs.createReadStream(filePath),
        model: 'whisper-1',
        language: 'en',
        response_format: 'verbose_json',
        timestamp_granularities: ['segment']
      });

      this.totalTranscriptions++;
      log(`[TRANSCRIBE] File transcribed: ${transcription.text.length} chars`);

      return transcription;
    } catch (err) {
      log(`[TRANSCRIBE] File transcription error: ${err.message}`);
      throw err;
    }
  }

  /**
   * Create a WAV file from mulaw audio data.
   * Mulaw is 8-bit, 8kHz, mono.
   */
  createMulawWav(mulawData) {
    const sampleRate = 8000;
    const numChannels = 1;
    const bitsPerSample = 8;
    const dataSize = mulawData.length;
    const headerSize = 44;
    const fileSize = headerSize + dataSize;

    const buffer = Buffer.alloc(fileSize);

    // RIFF header
    buffer.write('RIFF', 0);
    buffer.writeUInt32LE(fileSize - 8, 4);
    buffer.write('WAVE', 8);

    // fmt chunk
    buffer.write('fmt ', 12);
    buffer.writeUInt32LE(16, 16);        // chunk size
    buffer.writeUInt16LE(7, 20);         // format: mulaw = 7
    buffer.writeUInt16LE(numChannels, 22);
    buffer.writeUInt32LE(sampleRate, 24);
    buffer.writeUInt32LE(sampleRate * numChannels * bitsPerSample / 8, 28); // byte rate
    buffer.writeUInt16LE(numChannels * bitsPerSample / 8, 32); // block align
    buffer.writeUInt16LE(bitsPerSample, 34);

    // data chunk
    buffer.write('data', 36);
    buffer.writeUInt32LE(dataSize, 40);
    mulawData.copy(buffer, 44);

    return buffer;
  }
}

module.exports = { Transcriber };
