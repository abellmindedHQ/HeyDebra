// Quick two-way conversation mode
// Twilio calls -> Gather speech -> Whisper transcribe -> Claude respond -> ElevenLabs TTS -> Play back -> Loop

const express = require('express');
const twilio = require('twilio');
const fs = require('fs');
const path = require('path');
const https = require('https');
const http = require('http');

const app = express();
app.use(express.urlencoded({ extended: true }));
app.use(express.json());
app.use('/audio', express.static(path.join(__dirname, '..', 'public')));

const VoiceResponse = twilio.twiml.VoiceResponse;

const OPENAI_KEY = process.env.OPENAI_API_KEY;
const ELEVEN_KEY = process.env.ELEVEN_LABS_API_KEY;
const ELEVEN_VOICE = 'w6INrsHCejnExFzTH8Nm';
const BASE_URL = process.env.BASE_URL || 'https://cuddly-paths-learn.loca.lt';

const conversationHistory = [];

// Greeting when call connects
app.post('/convo/start', (req, res) => {
  console.log('[CONVO] Call connected, playing greeting');
  const twiml = new VoiceResponse();
  twiml.say({ voice: 'Polly.Joanna' }, 'Hey sugar, it is Debra. Go ahead and talk to me. I am listening.');
  const gather = twiml.gather({
    input: 'speech',
    speechTimeout: 3,
    action: '/convo/respond',
    method: 'POST',
    language: 'en-US'
  });
  gather.say({ voice: 'Polly.Joanna' }, '');
  // If no input, prompt again
  twiml.say({ voice: 'Polly.Joanna' }, 'You still there? Say something!');
  twiml.redirect('/convo/start');
  res.type('text/xml');
  res.send(twiml.toString());
});

// Handle speech input
app.post('/convo/respond', async (req, res) => {
  const speechResult = req.body.SpeechResult;
  console.log('[CONVO] User said:', speechResult);
  
  if (!speechResult) {
    const twiml = new VoiceResponse();
    twiml.say({ voice: 'Polly.Joanna' }, 'I did not catch that. Try again.');
    twiml.redirect('/convo/start');
    res.type('text/xml');
    return res.send(twiml.toString());
  }

  try {
    // Get Claude response
    conversationHistory.push({ role: 'user', content: speechResult });
    const claudeResponse = await getChatResponse(speechResult);
    console.log('[CONVO] Debra says:', claudeResponse);
    conversationHistory.push({ role: 'assistant', content: claudeResponse });

    // Generate ElevenLabs audio
    const audioFile = await generateSpeech(claudeResponse);
    const audioUrl = `${BASE_URL}/audio/${path.basename(audioFile)}`;
    console.log('[CONVO] Audio URL:', audioUrl);

    // Play audio then gather again
    const twiml = new VoiceResponse();
    twiml.play(audioUrl);
    const gather = twiml.gather({
      input: 'speech',
      speechTimeout: 3,
      action: '/convo/respond',
      method: 'POST',
      language: 'en-US'
    });
    gather.say({ voice: 'Polly.Joanna' }, '');
    twiml.say({ voice: 'Polly.Joanna' }, 'You still there hon?');
    twiml.redirect('/convo/start');
    res.type('text/xml');
    res.send(twiml.toString());
  } catch (err) {
    console.error('[CONVO] Error:', err.message);
    const twiml = new VoiceResponse();
    twiml.say({ voice: 'Polly.Joanna' }, 'Oops, something went wrong on my end. Let me try again.');
    twiml.redirect('/convo/start');
    res.type('text/xml');
    res.send(twiml.toString());
  }
});

async function getChatResponse(userMessage) {
  const messages = [
    { 
      role: 'system', 
      content: 'You are Debra, a retro-futuristic AI executive assistant. You are on a PHONE CALL right now with Alex, your boss. Keep responses SHORT (1-3 sentences max). Be warm, sassy, natural. No emojis (this is voice). No markdown. Talk like a real person on the phone. You have sass, humor, and genuine warmth.'
    },
    ...conversationHistory.slice(-10),
    { role: 'user', content: userMessage }
  ];

  return new Promise((resolve, reject) => {
    const data = JSON.stringify({ model: 'gpt-4o-mini', messages, max_tokens: 150 });
    const options = {
      hostname: 'api.openai.com',
      path: '/v1/chat/completions',
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${OPENAI_KEY}`,
        'Content-Type': 'application/json'
      }
    };
    const req = https.request(options, (res) => {
      let body = '';
      res.on('data', d => body += d);
      res.on('end', () => {
        try {
          const json = JSON.parse(body);
          resolve(json.choices[0].message.content);
        } catch (e) { reject(e); }
      });
    });
    req.on('error', reject);
    req.write(data);
    req.end();
  });
}

async function generateSpeech(text) {
  const filename = `response_${Date.now()}.mp3`;
  const filepath = path.join(__dirname, '..', 'public', filename);
  
  return new Promise((resolve, reject) => {
    const data = JSON.stringify({
      text,
      model_id: 'eleven_multilingual_v2',
      voice_settings: { stability: 0.35, similarity_boost: 0.85 }
    });
    const options = {
      hostname: 'api.elevenlabs.io',
      path: `/v1/text-to-speech/${ELEVEN_VOICE}`,
      method: 'POST',
      headers: {
        'xi-api-key': ELEVEN_KEY,
        'Content-Type': 'application/json'
      }
    };
    const req = https.request(options, (res) => {
      const stream = fs.createWriteStream(filepath);
      res.pipe(stream);
      stream.on('finish', () => resolve(filepath));
    });
    req.on('error', reject);
    req.write(data);
    req.end();
  });
}

const PORT = 3979;
app.listen(PORT, () => {
  console.log(`[CONVO] Conversation server on port ${PORT}`);
  console.log(`[CONVO] Base URL: ${BASE_URL}`);
});
