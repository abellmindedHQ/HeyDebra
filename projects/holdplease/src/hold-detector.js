/**
 * hold-detector.js - Detect hold music vs human speech from audio stream
 *
 * Receives mulaw audio from Twilio Media Streams, buffers it, and periodically
 * sends chunks to Whisper for transcription. Uses both audio analysis (energy
 * variance, speech patterns) and transcript content to detect when a human
 * picks up.
 *
 * Emits 'humanDetected' event when a real person is detected on the line.
 */

const EventEmitter = require('events');
const { Transcriber } = require('./transcriber');
const { log } = require('./utils');

// Phrases that strongly indicate a human agent has picked up
const HUMAN_PHRASES = [
  'how can i help',
  'how may i help',
  'how can i assist',
  'how may i assist',
  'thank you for calling',
  'thank you for holding',
  'thanks for holding',
  'thanks for waiting',
  'what is your',
  'what\'s your',
  'can i have your',
  'may i have your',
  'my name is',
  'this is',
  'who am i speaking with',
  'what can i do for you',
  'i understand',
  'let me look into',
  'let me check',
  'one moment please',
  'your reference number',
  'your booking',
  'your reservation',
  'your claim',
  'your account',
  'how are you today',
  'good morning',
  'good afternoon',
  'good evening'
];

// Phrases that indicate IVR / automated system (ignore these)
const IVR_PHRASES = [
  'press 1',
  'press 2',
  'press 3',
  'press 4',
  'press 5',
  'press 6',
  'press 7',
  'press 8',
  'press 9',
  'press 0',
  'press star',
  'press pound',
  'for english',
  'para español',
  'your call is important',
  'please continue to hold',
  'estimated wait time',
  'you are caller number',
  'all of our representatives',
  'agents are currently busy',
  'high call volume',
  'leave a message',
  'this call may be recorded',
  'this call may be monitored',
  'please listen carefully as our menu',
  'menu options have changed'
];

class HoldDetector extends EventEmitter {
  constructor(options = {}) {
    super();

    this.transcriber = new Transcriber();
    this.audioBuffer = [];
    this.bufferStartTime = null;
    this.totalBytes = 0;
    this.isShutdown = false;

    // Config
    this.analyzeIntervalMs = options.analyzeIntervalMs || 8000; // Transcribe every 8 seconds
    this.minBufferBytes = options.minBufferBytes || 16000; // ~1 second of mulaw audio at 8kHz
    this.energyThreshold = options.energyThreshold || 30; // Min energy to consider as non-silence

    // Audio analysis state
    this.silenceCount = 0;
    this.speechCount = 0;
    this.lastAnalysisTime = Date.now();
    this.consecutiveHumanHits = 0;
    this.requiredHumanHits = 2; // Need 2 consecutive positive detections to trigger

    // Stats
    this.stats = {
      chunksProcessed: 0,
      transcriptionsRun: 0,
      totalAudioSeconds: 0,
      holdMusicDetections: 0,
      silenceDetections: 0,
      speechDetections: 0
    };

    log('[DETECT] Hold detector initialized');
    log(`[DETECT] Analysis interval: ${this.analyzeIntervalMs}ms`);
  }

  /**
   * Process incoming audio from Twilio Media Stream.
   * Audio is base64-encoded mulaw at 8kHz.
   */
  processAudio(base64Audio, timestamp) {
    if (this.isShutdown) return;

    const audioBytes = Buffer.from(base64Audio, 'base64');
    this.audioBuffer.push(audioBytes);
    this.totalBytes += audioBytes.length;
    this.stats.chunksProcessed++;

    if (!this.bufferStartTime) {
      this.bufferStartTime = Date.now();
    }

    // Quick energy analysis on each chunk
    const energy = this.calculateEnergy(audioBytes);
    if (energy < this.energyThreshold) {
      this.silenceCount++;
    } else {
      this.speechCount++;
    }

    // Check if it's time to run transcription
    const elapsed = Date.now() - this.lastAnalysisTime;
    if (elapsed >= this.analyzeIntervalMs && this.totalBytes >= this.minBufferBytes) {
      this.analyzeBuffer();
    }
  }

  /**
   * Calculate RMS energy of mulaw audio buffer.
   * Mulaw samples are 8-bit unsigned, centered around 128.
   */
  calculateEnergy(audioBytes) {
    let sumSquares = 0;
    for (let i = 0; i < audioBytes.length; i++) {
      // Convert mulaw byte to linear approximation
      const sample = audioBytes[i] - 128;
      sumSquares += sample * sample;
    }
    return Math.sqrt(sumSquares / audioBytes.length);
  }

  /**
   * Calculate variance of energy across audio buffer.
   * Hold music tends to have consistent, repetitive energy patterns.
   * Human speech has more variable energy.
   */
  calculateEnergyVariance(audioBytes) {
    const chunkSize = 160; // 20ms chunks at 8kHz
    const energies = [];

    for (let i = 0; i < audioBytes.length - chunkSize; i += chunkSize) {
      const chunk = audioBytes.slice(i, i + chunkSize);
      energies.push(this.calculateEnergy(chunk));
    }

    if (energies.length < 2) return 0;

    const mean = energies.reduce((a, b) => a + b, 0) / energies.length;
    const variance = energies.reduce((sum, e) => sum + Math.pow(e - mean, 2), 0) / energies.length;

    return variance;
  }

  /**
   * Analyze buffered audio: run transcription and audio analysis.
   */
  async analyzeBuffer() {
    if (this.audioBuffer.length === 0) return;

    this.lastAnalysisTime = Date.now();

    // Concatenate buffered audio
    const combinedAudio = Buffer.concat(this.audioBuffer);
    const audioSeconds = combinedAudio.length / 8000; // 8kHz sample rate
    this.stats.totalAudioSeconds += audioSeconds;

    // Audio-level analysis
    const energyVariance = this.calculateEnergyVariance(combinedAudio);
    const overallEnergy = this.calculateEnergy(combinedAudio);
    const speechRatio = this.speechCount / (this.speechCount + this.silenceCount || 1);

    log(`[DETECT] Audio analysis: energy=${overallEnergy.toFixed(1)}, variance=${energyVariance.toFixed(1)}, speechRatio=${speechRatio.toFixed(2)}, buffer=${audioSeconds.toFixed(1)}s`);

    // Reset counters
    this.speechCount = 0;
    this.silenceCount = 0;

    // Classify based on audio characteristics
    let audioClassification = 'unknown';
    if (overallEnergy < this.energyThreshold) {
      audioClassification = 'silence';
      this.stats.silenceDetections++;
    } else if (energyVariance < 100 && speechRatio > 0.8) {
      audioClassification = 'hold-music';
      this.stats.holdMusicDetections++;
    } else if (energyVariance > 200 && speechRatio > 0.3) {
      audioClassification = 'possible-speech';
      this.stats.speechDetections++;
    }

    log(`[DETECT] Classification: ${audioClassification}`);

    // Run transcription for content analysis
    try {
      this.stats.transcriptionsRun++;
      const transcript = await this.transcriber.transcribeChunk(combinedAudio);

      if (transcript && transcript.trim().length > 0) {
        log(`[DETECT] Transcript: "${transcript}"`);

        const analysis = this.analyzeTranscript(transcript);
        log(`[DETECT] Transcript analysis: ${JSON.stringify(analysis)}`);

        if (analysis.isHuman) {
          this.consecutiveHumanHits++;
          log(`[DETECT] Human indicator detected (${this.consecutiveHumanHits}/${this.requiredHumanHits})`);

          if (this.consecutiveHumanHits >= this.requiredHumanHits) {
            this.emit('humanDetected', {
              reason: analysis.reason,
              transcript,
              audioClassification,
              stats: { ...this.stats }
            });
          }
        } else {
          this.consecutiveHumanHits = 0;
        }
      } else {
        log('[DETECT] No transcription content (silence or unintelligible)');
        this.consecutiveHumanHits = 0;
      }
    } catch (err) {
      log(`[DETECT] Transcription error: ${err.message}`);
    }

    // Clear buffer
    this.audioBuffer = [];
    this.totalBytes = 0;
    this.bufferStartTime = null;
  }

  /**
   * Analyze transcript text for human vs automated indicators.
   */
  analyzeTranscript(transcript) {
    const lower = transcript.toLowerCase();

    // Check for IVR phrases first (these are definitely automated)
    for (const phrase of IVR_PHRASES) {
      if (lower.includes(phrase)) {
        return { isHuman: false, reason: `IVR phrase detected: "${phrase}"`, confidence: 0.9 };
      }
    }

    // Check for human phrases
    for (const phrase of HUMAN_PHRASES) {
      if (lower.includes(phrase)) {
        return { isHuman: true, reason: `Human phrase detected: "${phrase}"`, confidence: 0.85 };
      }
    }

    // Heuristic: if transcript has conversational, non-repetitive content
    // and contains a question mark, it's likely human
    if (lower.includes('?') && lower.length > 20) {
      return { isHuman: true, reason: 'Conversational question detected', confidence: 0.6 };
    }

    return { isHuman: false, reason: 'No strong indicators', confidence: 0.3 };
  }

  /**
   * Get current detection stats.
   */
  getStats() {
    return {
      ...this.stats,
      bufferSize: this.totalBytes,
      consecutiveHumanHits: this.consecutiveHumanHits,
      isShutdown: this.isShutdown
    };
  }

  /**
   * Shut down the detector and flush buffers.
   */
  shutdown() {
    this.isShutdown = true;
    this.audioBuffer = [];
    this.totalBytes = 0;
    log(`[DETECT] Shutdown. Final stats: ${JSON.stringify(this.stats)}`);
  }
}

module.exports = { HoldDetector, HUMAN_PHRASES, IVR_PHRASES };
