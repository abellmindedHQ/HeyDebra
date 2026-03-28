# HoldPlease 📞

**An AI phone agent that calls, navigates IVR menus, waits on hold, and alerts you when a human picks up.**

No more wasting your life listening to hold music. HoldPlease calls the number, presses the right buttons, waits on hold for you, and the moment a real human picks up, it texts you and conferences you into the call.

## How It Works

```
You run HoldPlease → It dials the number → Navigates IVR menus →
Waits on hold → Detects human speech → Texts you →
Conferences you in → You talk to the human
```

### The Detection Pipeline

1. **Twilio Media Streams** sends real-time audio over WebSocket
2. **Audio analysis** checks energy patterns (hold music = repetitive, speech = variable)
3. **Whisper transcription** runs every 8 seconds on audio chunks
4. **Phrase matching** checks transcripts for human indicators ("how can I help", "what is your name")
5. **Dual confirmation** requires 2 consecutive positive detections to avoid false positives
6. **Alert + Conference** sends SMS and bridges you into the call

## Quick Start

### Prerequisites

- Node.js 18+
- [Twilio account](https://www.twilio.com/) with a phone number
- [OpenAI API key](https://platform.openai.com/) (for Whisper)
- [ngrok](https://ngrok.com/) or similar tunnel (Twilio needs public URLs)

### Setup

```bash
# Clone and install
cd holdplease
npm install

# Configure
cp .env.example .env
# Edit .env with your credentials

# Start ngrok (in another terminal)
ngrok http 3978

# Update .env with your ngrok URL
# BASE_URL=https://xxxx.ngrok.io

# Start the server
npm start
```

### Make a Call

```bash
# Using the test script
node test/test-call.js --number "+18005452200" --navigate "1,0,rep" --alert "+18135343383"

# Using a pre-configured IVR script
node test/test-call.js --script lufthansa

# Dry run (see the plan without calling)
node test/test-call.js --script lufthansa --dry-run

# Via API
curl -X POST http://localhost:3978/api/call \
  -H "Content-Type: application/json" \
  -d '{"number": "+18005452200", "script": "lufthansa"}'
```

## Configuration

### Environment Variables

| Variable | Description |
|----------|-------------|
| `TWILIO_ACCOUNT_SID` | Your Twilio Account SID |
| `TWILIO_AUTH_TOKEN` | Your Twilio Auth Token |
| `TWILIO_PHONE_NUMBER` | Your Twilio phone number (E.164 format) |
| `OPENAI_API_KEY` | OpenAI API key for Whisper transcription |
| `ALERT_PHONE_NUMBER` | Default phone number to alert/conference |
| `PORT` | Server port (default: 3978) |
| `BASE_URL` | Public URL for Twilio webhooks (ngrok URL) |

### IVR Scripts

Pre-configure navigation sequences in `config/ivr-scripts.json`:

```json
{
  "lufthansa": {
    "number": "+18005452200",
    "steps": [
      {"action": "wait", "seconds": 5},
      {"action": "dtmf", "digit": "1", "label": "English"},
      {"action": "wait", "seconds": 3},
      {"action": "speech", "text": "existing claim", "label": "Existing claim"},
      {"action": "wait", "seconds": 3},
      {"action": "speech", "text": "representative", "label": "Get human"}
    ],
    "context": "Calling about lost baggage claim"
  }
}
```

### Navigation String Format

The `--navigate` flag accepts a comma-separated string:
- **Numbers** → DTMF tones (press buttons)
- **Text** → Speech (say words into IVR)
- **Shortcuts:** `rep` = representative, `agent` = agent, `op` = operator

Examples:
- `"1,0,rep"` → Press 1, Press 0, Say "representative"
- `"2,3,existing claim,rep"` → Press 2, Press 3, Say "existing claim", Say "representative"

## Project Structure

```
holdplease/
├── src/
│   ├── index.js           # Express server + WebSocket + Twilio webhooks
│   ├── caller.js          # Outbound call initiation via Twilio REST API
│   ├── ivr-navigator.js   # DTMF and speech-based IVR navigation
│   ├── hold-detector.js   # Audio analysis + Whisper-based human detection
│   ├── alerter.js         # SMS alert + Twilio Conference bridging
│   ├── transcriber.js     # OpenAI Whisper API integration
│   ├── recorder.js        # Call recording download + transcription
│   └── utils.js           # Shared utilities (logging, sleep)
├── config/
│   └── ivr-scripts.json   # Pre-configured IVR navigation trees
├── test/
│   └── test-call.js       # CLI test tool
├── recordings/            # Saved recordings + transcripts (gitignored)
├── .env.example           # Environment template
└── package.json
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/call` | Initiate a new call |
| POST | `/voice/outbound` | Twilio webhook: call answered |
| POST | `/voice/status` | Twilio webhook: call status updates |
| POST | `/voice/join-conference` | TwiML: user joins conference |
| POST | `/voice/bridge-to-conference` | TwiML: move call to conference |
| POST | `/recording-status` | Twilio webhook: recording completed |
| POST | `/conference/events` | Twilio webhook: conference events |
| GET | `/health` | Health check + active call count |
| WS | `/media-stream` | Twilio Media Streams WebSocket |

## How Human Detection Works

HoldPlease uses a multi-layered approach:

1. **Energy Analysis**: Hold music has consistent, repetitive energy. Human speech has variable energy with natural pauses.

2. **Whisper Transcription**: Every 8 seconds, audio is sent to OpenAI Whisper. The transcript is checked against:
   - **Human phrases**: "how can I help", "what is your name", "thank you for holding"
   - **IVR phrases**: "press 1", "your call is important" (filtered out)

3. **Dual Confirmation**: Requires 2 consecutive positive detections to avoid false positives from brief IVR prompts that sound conversational.

## Recordings

Call recordings and transcripts are saved to the `recordings/` directory:
- `{callSid}-{timestamp}.wav` - Audio recording
- `{callSid}-{timestamp}-transcript.txt` - Timestamped transcript

## License

MIT
