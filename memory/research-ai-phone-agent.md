# AI Phone Agent for OpenClaw — Deep Research

> **Status:** Research Complete — March 26, 2026
> **Author:** Debra (subagent research task)
> **Purpose:** Comprehensive technical + product analysis for building an AI phone agent capability into OpenClaw/HeyDebra

---

## Table of Contents

1. [Product Vision: Never Make a Phone Call Again](#1-product-vision-never-make-a-phone-call-again)
2. [Technology Stack Options](#2-technology-stack-options)
3. [Architecture Design](#3-architecture-design)
4. [IVR Navigation](#4-ivr-navigation)
5. [Legal & Compliance](#5-legal--compliance)
6. [Competitive Landscape](#6-competitive-landscape)
7. [Use Cases](#7-use-cases)
8. [MVP Roadmap](#8-mvp-roadmap)
9. [OpenClaw Skill Design](#9-openclaw-skill-design)
10. [Immediate Action: Lufthansa Lost Baggage](#10-immediate-action-lufthansa-lost-baggage)

---

## 1. Product Vision: Never Make a Phone Call Again

### The Problem

Phone calls are the last unautomated chore. We can order food, schedule rides, manage finances, and control our homes without lifting a finger. But the moment something goes wrong with an airline, a doctor's office doesn't have online booking, or Comcast needs to be called to dispute a charge... you're back in 1997, sitting on hold listening to smooth jazz.

The average American spends **43 days of their life on hold**. Customer service calls average 13 minutes, with 75% of that being wait time. For complex issues (airlines, insurance, government), calls can run 45-90 minutes.

### The Vision: Debra as Your Voice

HeyDebra already manages your calendar, your messages, your projects. The missing piece is your **voice**. When Debra can pick up the phone and handle calls on your behalf, she becomes a true Life Operating System:

- "Debra, call Lufthansa and get my baggage claim resolved. Here's the case number."
- "Debra, book a table for 4 at Stock & Barrel Saturday at 7pm. Hannah's gluten-free."
- "Debra, call Comcast and negotiate my bill down. I'm paying $189/mo, I want $120."
- "Debra, my passport renewal has been stuck for 8 weeks. Call the State Department and find out what's going on."
- "Debra, call Dr. Chen's office and schedule my annual physical. Mornings work best."

This is **Google Duplex done right**. Google demoed this in 2018 and then... basically shelved it. It works for restaurant reservations through Google Assistant but that's it. The technology is 10x better now, the APIs exist, and nobody has built the personal version. Everyone is building AI phone agents for *businesses* (inbound call centers). Nobody is building them for *people* (outbound personal calls).

### Brand Extension

This positions HeyDebra as the premium AI life management layer:

- **Mirror** (know yourself) → self-knowledge, journaling, reflection
- **Pools** (know your world) → relationship intelligence, social graph
- **Debra** (your sherpa) → the agent that acts on your behalf in the world

Phone calls are the ultimate proof that your AI assistant is *real*. Not a chatbot. Not a prompt wrapper. A fully autonomous agent that handles the tedious, annoying, time-consuming parts of life so you can focus on what matters.

---

## 2. Technology Stack Options

### Overview Comparison

| Platform | Type | Cost/min (effective) | Latency | Best For | OpenClaw Fit |
|----------|------|---------------------|---------|----------|-------------|
| **Twilio + OpenAI Realtime** | DIY Stack | $0.05-0.15 | 300-600ms | Full control, custom logic | ⭐⭐⭐⭐⭐ |
| **Twilio ConversationRelay** | Managed orchestration | $0.08-0.18 | 400-600ms | Quick deployment, BYO-LLM | ⭐⭐⭐⭐ |
| **Vapi** | Voice AI platform | $0.18-0.33 | <500ms | Rapid prototyping | ⭐⭐⭐ |
| **Bland AI** | Turnkey AI calls | $0.11-0.14 | ~800ms | High volume outbound | ⭐⭐ |
| **Retell AI** | Conversational voice | $0.13-0.31 | Low | Developer-friendly | ⭐⭐⭐ |
| **ElevenLabs Conversational** | Voice-first AI | $0.08-0.10 | Low | Best voice quality | ⭐⭐⭐⭐ |
| **LiveKit + OpenAI** | Open source stack | $0.03-0.10 | <500ms | Self-hosted, full control | ⭐⭐⭐⭐⭐ |

### Detailed Analysis

#### A. Twilio + OpenAI Realtime API (⭐ RECOMMENDED for MVP)

**Why this wins for OpenClaw:**
- Twilio is the telephony backbone. Period. It handles numbers, routing, compliance, recording.
- OpenAI Realtime API provides native speech-to-speech (no STT→LLM→TTS chain = lower latency)
- Twilio has first-class OpenAI integration with official SDKs and tutorials
- Alex already knows Node.js; all examples are in Node.js
- Pay-as-you-go, no monthly minimums for low-volume personal use

**Cost breakdown per call:**
- Twilio outbound call: ~$0.014/min (US local)
- Twilio international (Germany/Lufthansa): ~$0.015-0.045/min
- OpenAI Realtime API: token-based, roughly $0.06-0.10/min for audio
- Total: **~$0.08-0.15/min** for a fully autonomous phone call
- A 30-minute Lufthansa hold + 10-minute conversation ≈ **$3.20-6.00**

**Architecture:**
```
OpenClaw Skill → Twilio API (outbound call) → Twilio Media Streams (WebSocket)
    ↕                                              ↕
Context/Goals                              Node.js Bridge Server
                                                   ↕
                                          OpenAI Realtime API (WebSocket)
                                                   ↕
                                          GPT-4o S2S (speech-to-speech)
```

**Two integration paths:**

1. **Media Streams** — Raw audio bidirectional WebSocket. You proxy audio between Twilio and OpenAI. Full control, handle your own STT/TTS if desired.

2. **ConversationRelay** — Twilio handles STT/TTS orchestration, sends you text transcripts via WebSocket, you respond with text. Simpler but less control over voice/latency.

**Recommendation:** Start with **ConversationRelay** for MVP (simpler), migrate to **Media Streams + OpenAI Realtime** for production (better latency, native S2S).

#### B. Vapi

- **Pros:** Fast to prototype, handles all orchestration, BYO models, good docs
- **Cons:** $0.18-0.33/min effective cost is 2-3x DIY, another vendor dependency
- **Verdict:** Good if you want something working in a weekend. Not ideal long-term for OpenClaw (too much vendor lock-in, Alex wants to own the stack).

#### C. Bland AI

- **Pros:** Purpose-built for AI phone calls, handles IVR nav
- **Cons:** 800ms latency (noticeable), $0.11-0.14/min + $299-499/mo subscription, enterprise-focused, recent price hikes
- **Verdict:** Built for outbound sales campaigns, not personal assistant use. Overkill and overpriced for this.

#### D. Retell AI

- **Pros:** Clean developer experience, modular pricing, good voice quality
- **Cons:** $0.13-0.31/min effective, still another platform layer
- **Verdict:** Solid alternative to Vapi. Worth keeping in mind but same vendor lock-in concern.

#### E. ElevenLabs Conversational AI

- **Pros:** Best-in-class voice quality (Debra already has a cloned voice here!), $0.08-0.10/min, supports phone integration
- **Cons:** Less mature for complex conversational flows, limited tool-calling compared to OpenAI
- **Verdict:** Could be excellent for TTS layer in a hybrid approach. Use ElevenLabs voice with OpenAI reasoning. **Debra's custom voice (voice_id: w6INrsHCejnExFzTH8Nm) is already in ElevenLabs.**

#### F. LiveKit (Open Source)

- **Pros:** Apache 2.0, self-hostable, SIP integration, full stack control, integrates with any STT/LLM/TTS
- **Cons:** More infrastructure to manage, steeper learning curve
- **Verdict:** Best long-term architecture for a product. Could run on Mac mini or VPS. Worth evaluating for Phase 2/3 when this becomes a real product feature.

### Recommended Stack (MVP)

```
Telephony:    Twilio (Programmable Voice + Media Streams)
Intelligence: OpenAI Realtime API (gpt-4o-realtime or gpt-realtime-mini)
Voice:        OpenAI native S2S (MVP) → ElevenLabs Debra voice (Phase 2)
Orchestration: Node.js server on Mac mini (or deployed to Vercel/Railway)
Integration:  OpenClaw skill triggers call, monitors progress, delivers results
```

### Recommended Stack (Production/Product)

```
Telephony:    Twilio (or direct SIP via LiveKit)
Intelligence: OpenAI Realtime API or Claude (when Anthropic ships voice)
Voice:        ElevenLabs (Debra's cloned voice for brand consistency)
Infrastructure: LiveKit (self-hosted, open source)
Orchestration: OpenClaw phone-agent skill with full context injection
Recording:    Twilio call recording + Whisper transcription
```

---

## 3. Architecture Design

### Call Flow

```
┌──────────────────────────────────────────────────────────────────┐
│                        OPENCLAW SKILL                            │
│  Trigger: "call Lufthansa about my lost bags"                   │
│  Parses: target company, issue, context, desired outcome        │
│  Loads: case numbers, account info, previous correspondence     │
└──────────────┬───────────────────────────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────────────────────────┐
│                     CALL ORCHESTRATOR                             │
│  1. Look up company phone number (or use provided number)       │
│  2. Prepare context prompt with all relevant details             │
│  3. Set goals: "Get reimbursement status for claim CPHLH52532"  │
│  4. Set escalation rules: "Loop in Alex if they need verbal OK" │
│  5. Initiate Twilio outbound call                                │
└──────────────┬───────────────────────────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────────────────────────┐
│                      TWILIO VOICE CALL                           │
│  Outbound call placed → IVR system answers                      │
│  Media Streams WebSocket opened to bridge server                │
└──────────────┬───────────────────────────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────────────────────────┐
│                     BRIDGE SERVER (Node.js)                       │
│                                                                  │
│  ┌─────────────┐    audio    ┌──────────────────────┐           │
│  │   Twilio     │◄──────────►│  OpenAI Realtime API │           │
│  │   WebSocket  │            │  (gpt-4o S2S)        │           │
│  └─────────────┘    audio    └──────────────────────┘           │
│                                                                  │
│  State Machine:                                                  │
│  ┌────────┐  ┌─────────┐  ┌──────┐  ┌─────────┐  ┌────────┐  │
│  │ IVR    │→ │ On Hold │→ │ Live │→ │ Resolve │→ │ Report │  │
│  │ Nav    │  │ Waiting │  │ Agent│  │         │  │        │  │
│  └────────┘  └─────────┘  └──────┘  └─────────┘  └────────┘  │
│       │           │            │          │            │         │
│       │     Notify Alex   Conference  Record all   Transcribe  │
│       │     "on hold,     Alex in if  outcomes     & summarize │
│       │      ETA 15min"   auth needed              to OpenClaw │
│       │                                                         │
│  DTMF Engine: sends touch-tones for IVR menu navigation        │
│  Hold Detector: identifies hold music/silence patterns          │
│  Human Detector: identifies when a live person picks up         │
└──────────────────────────────────────────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────────────────────────┐
│                      RESULTS & REPORTING                         │
│  - Full call recording saved (Twilio)                           │
│  - Transcription via Whisper                                    │
│  - Summary generated by GPT-4o                                  │
│  - Action items extracted                                       │
│  - Results delivered to Alex via iMessage/session               │
│  - Follow-up tasks created if needed                            │
└──────────────────────────────────────────────────────────────────┘
```

### Context Injection System

The AI agent needs to know everything relevant before making the call. This is injected as the system prompt:

```javascript
const callContext = {
  // WHO we're calling
  company: "Lufthansa",
  phone: "+1-800-645-3880",
  department: "Baggage Claims",
  
  // WHO we are
  caller: {
    name: "Alex Abell",
    role: "Passenger / Claimant",
    // Only share what's needed
    email: "alexander.o.abell@gmail.com",
  },
  
  // WHAT we need
  issue: "Lost baggage reimbursement claim follow-up",
  references: {
    "Property Irregularity Report": "CPHLH52532",
    "Case Number": "C-130009-K8N5",
    "Feedback ID": "FB ID 42383344",
    "Flight": "Nov 29, 2025, Munich → Copenhagen → Knoxville",
    "Receipts Submitted": "$552.52 (Nike) plus Uber and taxi receipts"
  },
  
  // WHAT we want
  desiredOutcome: "Get status on reimbursement. Escalate if no resolution. Reference EU regulation EC 261/2004 and threaten DOT complaint if needed.",
  
  // RULES
  authorization: "Alex Abell authorizes Debra to speak on his behalf regarding this claim",
  escalation: "If they need verbal authorization from Alex, conference him in",
  tone: "Firm but professional. This has been 4 months. Express frustration politely.",
  maxHoldTime: "45 minutes",
  
  // CONVERSATION HISTORY
  previousInteractions: [
    "Multiple emails sent, receipts submitted",
    "Lufthansa has been non-responsive for 4+ months",
    "Alex threatened DOT and EU EC 261/2004 escalation"
  ]
};
```

### Conference / Transfer Capability

Critical feature: the AI should be able to loop Alex in when needed.

```javascript
// When the agent detects authorization is needed:
async function conferenceInAlex(callSid) {
  // 1. Text Alex first
  await sendiMessage("Alex", "Hey, Lufthansa rep needs verbal authorization. Conferencing you in now. Pick up!");
  
  // 2. Add Alex to the call
  await twilioClient.calls(callSid)
    .participants
    .create({
      from: TWILIO_NUMBER,
      to: ALEX_PHONE,
      earlyMedia: true,
      statusCallback: '/call-status'
    });
  
  // 3. AI stays on the line to help/take notes
  // 4. When Alex hangs up, AI resumes solo
}
```

### Real-Time Status Updates

While on hold or during the call, Debra should be able to update Alex:

```
📞 Calling Lufthansa Baggage Claims...
🔢 Navigating IVR: Selected "Existing Claim" → "Baggage" → "Speak to Agent"
⏳ On hold. Estimated wait: 22 minutes. I'll let you know when someone picks up.
... (15 minutes later) ...
🙋 Live agent connected! Speaking with "Marcus" from baggage claims.
📋 Update: Marcus confirmed receipt of claim CPHLH52532. Checking status...
💰 Resolution: Reimbursement of $552.52 approved. Check will be mailed in 7-10 business days.
✅ Call complete. Full transcript and recording saved. Summary below:
```

---

## 4. IVR Navigation

### The Challenge

Most customer service lines use Interactive Voice Response (IVR) systems. These range from simple ("Press 1 for English") to complex multi-level menus with speech recognition.

### Detection Strategies

#### DTMF (Touch-Tone) Navigation
```javascript
// Send DTMF tones through Twilio
function sendDTMF(callSid, digits) {
  return twilioClient.calls(callSid).update({
    twiml: `<Response><Play digits="${digits}"/></Response>`
  });
}

// Common patterns
const IVR_PATTERNS = {
  language: { detect: /press \d+ for english/i, action: '1' },
  existing_claim: { detect: /existing (claim|case|ticket)/i, action: () => findMenuOption() },
  representative: { detect: /speak.*(representative|agent|person)/i, action: '0' },
  account_number: { detect: /enter your (account|case|reference)/i, action: () => enterNumber() },
};
```

#### Speech-Based IVR
Modern IVRs use speech recognition. The AI agent can respond naturally:

```javascript
// System prompt for IVR navigation
const ivrPrompt = `
You are navigating an automated phone system (IVR). Your goal is to reach a human 
agent in the baggage claims department.

STRATEGIES:
1. When asked to choose a department, say "baggage claims" or "lost baggage"
2. When asked for a case number, say: "C-130009-K8N5" (spell it out: C as in Charlie...)
3. If asked "how can I help you today?", say "I need to follow up on a lost baggage claim"
4. If stuck in a loop, say "representative" or "agent" or press 0
5. If asked for language preference, say "English"

AVOID:
- Don't give personal information to the IVR (save for the human agent)
- Don't press random buttons
- If the system doesn't understand after 2 tries, try "operator" or "0"
`;
```

#### Hold Music Detection

```javascript
// Detect hold music vs. silence vs. human speech
const HOLD_INDICATORS = [
  'silence_longer_than_5s',          // Long silence = still on hold
  'repeating_audio_pattern',         // Music loops
  'periodic_message',                // "Your call is important to us"
  'estimated_wait_time_announcement' // "Estimated wait: 15 minutes"
];

// When hold is detected:
// 1. Switch to low-power monitoring mode (reduce API costs)
// 2. Notify Alex with estimated wait time
// 3. Wake up when human speech pattern detected
```

#### Human Detection

The moment a real person picks up, the AI needs to snap to attention:

```javascript
// Signals that a human agent has joined:
const HUMAN_SIGNALS = [
  'greeting_pattern',      // "Thank you for calling, my name is..."
  'question_pattern',      // "How can I help you today?"
  'name_introduction',     // "This is Marcus with baggage claims"
  'absence_of_hold_music', // Music stops, natural speech begins
];

// When human detected:
// 1. Alert Alex: "🙋 Live agent connected!"
// 2. Switch to full conversation mode
// 3. Begin recording/transcription
// 4. Execute conversation strategy
```

### IVR Database (Future Enhancement)

Build a community-sourced database of IVR trees for common companies:

```json
{
  "lufthansa_us": {
    "number": "+1-800-645-3880",
    "language_prompt": { "type": "speech", "response": "English" },
    "main_menu": [
      { "option": "1", "description": "New booking" },
      { "option": "2", "description": "Existing reservation" },
      { "option": "3", "description": "Baggage" },
      { "option": "4", "description": "Miles & More" }
    ],
    "baggage_menu": [
      { "option": "1", "description": "Report missing baggage" },
      { "option": "2", "description": "Existing claim status" }
    ],
    "shortcut_to_agent": "Press 3, then 2, then say 'agent'",
    "avg_hold_time_minutes": 25,
    "best_time_to_call": "Tuesday 10am-12pm EST"
  }
}
```

---

## 5. Legal & Compliance

### Call Recording Consent

#### One-Party vs. Two-Party States

| Consent Type | States | Implication |
|-------------|--------|-------------|
| **One-Party** | Tennessee (where Alex is), + 38 other states | Only one party needs to consent. If Debra is a party to the call (acting on Alex's behalf), recording is legal. |
| **Two-Party / All-Party** | California, Florida, Illinois, Maryland, Massachusetts, Montana, New Hampshire, Oregon, Pennsylvania, Washington, Connecticut, Delaware | Both parties must consent. However: customer service lines almost always announce "this call may be recorded," which constitutes blanket consent. |

**Tennessee is one-party consent.** Alex (through Debra) consenting is sufficient for recording.

**Key nuance:** When calling a company that announces "this call may be recorded for quality purposes," they have given consent for recording. This covers two-party states as well.

#### International Considerations (Lufthansa / EU)

- **GDPR:** Applies when calling EU-based call centers. Recording conversations with EU representatives requires a lawful basis. Best approach: inform the rep that you're also recording.
- **Germany:** Two-party consent for recording. Since Lufthansa's US number likely routes to a US or India call center, this may not apply. If routed to Germany, the "this call may be recorded" announcement covers it.

### Representing Someone on a Call

#### Authorization Levels

1. **Informal verbal authorization** — Most customer service calls accept "I'm calling on behalf of [person]" + ability to verify identity (name, DOB, address, booking reference). This is standard and sufficient for most airline/utility calls.

2. **Account-level authorization** — Some companies let you add authorized callers to an account. Alex could add "Debra" or use his own name with Debra acting as his representative.

3. **Power of Attorney** — Only needed for legal/financial matters. Not required for customer service calls.

4. **Three-way call authorization** — The gold standard: Alex joins the call, authorizes Debra to speak on his behalf, then drops off. The conference feature handles this perfectly.

#### Practical Approach for AI Agent

```
AI: "Hi, I'm calling on behalf of Alex Abell regarding baggage claim CPHLH52532. 
     I have all his case details and he's authorized me to handle this."

Rep: "Can I verify the passenger's information?"

AI: "Of course. The passenger is Alex Abell. The flight was November 29, 2025, 
     Munich to Copenhagen to Knoxville. The Property Irregularity Report number 
     is CPHLH52532."

Rep: "And can I get the date of birth / email on the account?"

AI: [Provides verification details from context]
```

If the rep insists on speaking with Alex directly → conference him in.

### FCC / TCPA Considerations

**Critical distinction:** The FCC's 2024 ruling on AI-generated voices applies to **unsolicited outbound calls** (robocalls, telemarketing). Debra calling a customer service line on behalf of a user is fundamentally different:

- **Not telemarketing** — Debra is a consumer calling a business, not a business calling a consumer
- **Not unsolicited** — Debra is calling in response to an existing issue/relationship
- **Not mass-dialing** — One call at a time, specific purpose
- **Consent is irrelevant** — The TCPA requires consent from the *recipient*. When calling a business customer service line, the business has implicitly consented to receive calls by publishing their phone number

**However, best practices:**
- Debra should identify as an AI assistant when asked directly ("I'm Alex's AI assistant, Debra")
- Don't proactively volunteer AI status (it can confuse reps and trigger script deviations)
- If a rep asks "Are you a real person?" — be honest but frame it well: "I'm an AI assistant authorized to handle this on Alex's behalf"

### Tennessee ELVIS Act

Tennessee's ELVIS Act (Ensuring Likeness, Voice and Image Security) prohibits commercial use of AI-generated voices that replicate a real person's voice without consent. This applies to:
- Using a cloned celebrity voice for commercial purposes
- NOT relevant to Debra's own synthetic voice making phone calls

**No issue here.** Debra's voice is her own (custom ElevenLabs voice), not cloning anyone.

---

## 6. Competitive Landscape

### Consumer-Facing AI Phone Agents

| Product | What It Does | Status | Pricing | Notes |
|---------|-------------|--------|---------|-------|
| **Google Duplex** | Restaurant reservations via Google Assistant | Live but limited | Free (Google Assistant) | Only handles restaurant bookings and simple appointments. Hasn't evolved much since 2018 demo. |
| **DoNotPay** | "Robot lawyer" — disputes, cancellations | Active, controversial | $36/2 months | FTC complaint in 2024 for "deceptive advertising as AI lawyer." Features often don't work as advertised. |
| **Pine AI** | AI assistant for customer service calls | Active | Free tier + premium | Newer entrant, specifically targets "call on your behalf" use case |
| **Lindy AI** | No-code AI agent platform with phone calling | Active | $29.99-$299.99/mo, $0.19/min calls | Business-focused, not personal assistant. Could adapt. |
| **Air AI** | Autonomous phone conversations | Active | $0.11-0.32/min + $25K-100K licensing | Enterprise only. Absurd pricing for personal use. |

### Business-Focused (Inbound) AI Phone Agents

| Product | Focus | Notes |
|---------|-------|-------|
| **Bland AI** | Outbound sales campaigns | High latency (800ms), enterprise pricing |
| **Retell AI** | Call center automation | Good developer experience, growing |
| **Vapi** | Developer voice AI platform | Most flexible, but pricey |
| **Dialpad AI** | Business communications | Corporate tool, not personal |
| **Observe AI** | Call center analytics | Post-call analysis, not real-time agent |

### Gap Analysis: Why Nobody's Doing This Well

1. **Google Duplex** proved the concept but Google didn't push it. Limited to basic reservations. No complex conversations, no hold-waiting, no negotiation.

2. **DoNotPay** tried the "fight on your behalf" angle but execution is poor and they got in trouble with the FTC.

3. **Pine AI** is the closest competitor but it's a standalone app, not integrated into a broader AI assistant ecosystem.

4. **Everyone else** is building for businesses (inbound call handling), not for consumers (outbound personal calls).

**The opportunity:** Build the consumer-facing AI phone agent that actually works, integrated into a personal AI assistant that already knows your life, your accounts, your preferences, and your communication style. That's Debra.

---

## 7. Use Cases

### Tier 1: Customer Service & Disputes (Highest Value)

These are the calls people dread most. Long holds, frustrating IVRs, repetitive transfers.

#### Airlines (Lufthansa, United, etc.)
- Lost/delayed baggage claims and follow-up
- Flight changes, cancellations, rebooking
- Upgrade requests and standby management
- Compensation claims (EU EC 261/2004, DOT complaints)
- Miles/points account issues

#### Utilities & Telecom (Comcast, AT&T, insurance)
- **Bill negotiation:** "I'm paying $189/mo, I want $120 or I'm switching"
- Service cancellation (navigating retention departments)
- Account updates (address changes, adding features)
- Outage reporting and status checks
- Insurance claim follow-up

#### Banks & Financial Services
- Dispute charges
- Fee reversals
- Account inquiries that require phone verification
- Credit limit increases

### Tier 2: Appointments & Reservations (Highest Frequency)

The Google Duplex use case, but actually comprehensive.

#### Restaurant Reservations
```
"Book a table for 4 at Stock & Barrel, Saturday at 7pm. 
 One person is gluten-free. If they're full, try OliBea or Kaizen."
```
- Call ahead, not just OpenTable
- Handle dietary restrictions and special requests
- Confirm reservations day-of
- Many restaurants (especially local spots) still only take phone reservations

#### Doctor / Dentist / Specialist
```
"Schedule my annual physical with Dr. Chen. Mornings preferred, 
 not Fridays. My insurance is Anthem Blue Cross, member ID XYZ."
```
- Many practices don't have online scheduling
- Handle insurance verification questions
- Schedule follow-ups
- Request prescription refills

#### Hair Salon / Barber
```
"Book a haircut at Scout's Barbershop for Saturday morning."
```

#### Auto Repair / Service
```
"Schedule an oil change at Firestone on Kingston Pike. 
 I drive a 2021 Toyota RAV4. Thursday or Friday works."
```

### Tier 3: Travel Management (High Complexity)

#### Hotels
- Book rooms at places without online booking
- Request upgrades ("I'm a Marriott Bonvoy Platinum member")
- Handle issues (room changes, complaints, late checkout)
- Cancel/modify reservations

#### Car Rentals
- Price match negotiations
- Reservation changes
- Damage dispute resolution
- Return logistics

#### Complex Itinerary Changes
- Multi-leg flight rebooking
- Hotel chains that require phone calls for points stays
- Cruise line modifications

### Tier 4: Government & Bureaucracy (Longest Holds)

#### DMV
- Appointment scheduling
- Registration renewal status
- Title transfer inquiries

#### IRS
- Refund status checks
- Payment plan inquiries
- Tax transcript requests
- Average hold time: **30-90 minutes** — perfect Debra use case

#### Passport Office
- Application status
- Expedited processing requests
- Renewal inquiries

#### Social Security
- Benefits inquiries
- Address updates
- Average hold time: **45-120 minutes**

### Tier 5: Local Business Queries (Quick Calls)

#### Stock Checks
```
"Call Home Depot on Pellissippi and ask if they have 
 a 6ft pre-lit Christmas tree in stock."
```

#### Hours & Availability
```
"What time does the Tailor on Market Square close today? 
 Can they hem pants by Thursday?"
```

#### Hold Items
```
"Call REI and ask them to hold that Osprey Atmos 65 backpack 
 in size Large. I'll pick it up by 5pm."
```

### Use Case Priority Matrix

| Use Case | Frequency | Pain Level | Complexity | MVP Priority |
|----------|-----------|-----------|------------|-------------|
| Customer service disputes | Monthly | 🔴 Extreme | High | Phase 2 |
| Bill negotiation | Quarterly | 🔴 High | High | Phase 2 |
| Restaurant reservations | Weekly | 🟡 Medium | Low | Phase 2 |
| Doctor appointments | Monthly | 🟡 Medium | Medium | Phase 2 |
| Government offices | Rare | 🔴 Extreme | Medium | Phase 1 (hold & alert) |
| Local business queries | Weekly | 🟢 Low | Low | Phase 2 |
| Flight changes | Occasional | 🔴 High | High | Phase 3 |
| **Hold + Alert (any call)** | **Any** | **🔴 High** | **Low** | **Phase 1** |

---

## 8. MVP Roadmap

### Phase 1: Hold For Me (2-3 weeks)

**Goal:** Debra calls a number, navigates basic IVR, waits on hold, and alerts Alex when a human picks up.

**Scope:**
- Outbound call via Twilio
- Basic DTMF IVR navigation (press 1, press 2)
- Hold music detection
- Human voice detection → alert Alex via iMessage
- Conference Alex into the call when human answers
- Call recording (Twilio built-in)

**What Alex does:** Takes over the call when the human answers. Debra handled the 30 minutes of IVR + hold.

**Tech:**
- Twilio Programmable Voice + Media Streams
- Simple audio analysis for hold detection (can use VAD — voice activity detection)
- OpenAI Whisper for periodic transcription checks
- No complex AI conversation needed yet

**Estimated build:** 2-3 weekends
**Estimated cost per use:** $0.50-2.00 (mostly Twilio minutes on hold)

```javascript
// Phase 1: Minimal viable "hold for me" agent
const express = require('express');
const WebSocket = require('ws');
const twilio = require('twilio');

const app = express();
const client = twilio(ACCOUNT_SID, AUTH_TOKEN);

// 1. Initiate outbound call
app.post('/call', async (req, res) => {
  const { phoneNumber, ivrSequence, context } = req.body;
  
  const call = await client.calls.create({
    to: phoneNumber,
    from: TWILIO_NUMBER,
    url: `${BASE_URL}/twiml/connect`,
    statusCallback: `${BASE_URL}/call-status`,
    record: true
  });
  
  res.json({ callSid: call.sid, status: 'initiated' });
});

// 2. Connect call to Media Stream
app.post('/twiml/connect', (req, res) => {
  const twiml = new twilio.twiml.VoiceResponse();
  
  // Optional: play DTMF sequence for IVR
  if (ivrSequence) {
    twiml.play({ digits: ivrSequence });
  }
  
  // Connect to WebSocket for audio monitoring
  const connect = twiml.connect();
  connect.stream({
    url: `wss://${BASE_URL}/media-stream`,
    track: 'both_tracks'
  });
  
  res.type('text/xml');
  res.send(twiml.toString());
});

// 3. Monitor audio stream for human detection
const wss = new WebSocket.Server({ server });
wss.on('connection', (ws) => {
  let holdDetected = false;
  let silenceCounter = 0;
  
  ws.on('message', (data) => {
    const msg = JSON.parse(data);
    
    if (msg.event === 'media') {
      // Analyze audio for speech patterns
      const audioData = Buffer.from(msg.media.payload, 'base64');
      
      // Simple energy-based voice activity detection
      const energy = calculateEnergy(audioData);
      
      if (energy < SILENCE_THRESHOLD) {
        silenceCounter++;
      } else {
        // Speech detected! Is it hold music or a human?
        if (isLikelySpeech(audioData) && !isRepeatingPattern(audioData)) {
          // Human detected!
          notifyAlex("🙋 Someone picked up! Conferencing you in...");
          conferenceInAlex(callSid);
        }
        silenceCounter = 0;
      }
    }
  });
});
```

### Phase 2: IVR + Basic Conversation (4-6 weeks after Phase 1)

**Goal:** Debra can navigate complex IVR systems AND have basic conversations with customer service reps.

**New capabilities:**
- OpenAI Realtime API integration for live conversation
- Speech-based IVR navigation
- Context-aware conversation (knows the case details, what to ask for)
- Transcript and summary generation
- Conference-in-Alex when authorization needed
- Real-time status updates via iMessage

**Tech additions:**
- OpenAI Realtime API (WebSocket, speech-to-speech)
- System prompt injection with full case context
- State machine for call phases (IVR → Hold → Agent → Resolution)
- ElevenLabs for Debra's voice (optional, OpenAI voices work too)

**Estimated build:** 4-6 weekends
**Estimated cost per use:** $2-8 depending on call length

### Phase 3: Full Autonomous Resolution (8-12 weeks after Phase 2)

**Goal:** Debra handles the entire call autonomously, from IVR to resolution, including negotiation strategies.

**New capabilities:**
- Negotiation tactics engine (bill negotiation, upgrade requests)
- Escalation strategies ("I'd like to speak with a supervisor")
- Multi-call campaigns ("Call back tomorrow if not resolved")
- IVR tree database (community-sourced, auto-learning)
- Success/failure tracking and strategy refinement
- Scheduled calls (call at optimal times for shorter hold)
- Post-call action items (follow up in 7 days, file DOT complaint if no check)

**Product features:**
- Call history and outcome tracking
- Template library (common scenarios pre-configured)
- Voice selection (Debra voice, neutral voice, authoritative voice)
- Priority queue (urgent vs. can-wait)

**Estimated build:** 8-12 weeks
**Estimated cost per use:** $2-10 depending on complexity

### Phase 4: Product / Platform (Ongoing)

**Goal:** Package as a standalone product feature or service.

- **HeyDebra Phone** — Premium feature of HeyDebra platform
- API for other AI assistant platforms
- IVR tree sharing / community database
- Analytics dashboard (calls made, time saved, money saved/recovered)
- Multi-user support (Debra calls for Alex's mom Sallijo too)

### Cost Summary

| Phase | Build Time | Per-Call Cost | Monthly (est. 10 calls) |
|-------|-----------|---------------|------------------------|
| Phase 1: Hold For Me | 2-3 weeks | $0.50-2.00 | $5-20 |
| Phase 2: IVR + Conversation | 4-6 weeks | $2-8 | $20-80 |
| Phase 3: Full Autonomous | 8-12 weeks | $2-10 | $20-100 |

**Infrastructure costs:**
- Twilio phone number: $1/month
- Twilio voice minutes: ~$0.014/min (US)
- OpenAI Realtime API: ~$0.06-0.10/min
- Server: Can run on Mac mini (free) or Railway/Render ($5-20/mo)

---

## 9. OpenClaw Skill Design

### Skill Structure

```
skills/
  phone-agent/
    SKILL.md
    scripts/
      bridge-server.js     # WebSocket bridge (Twilio ↔ OpenAI)
      call-orchestrator.js  # Call management, state machine
      ivr-navigator.js      # IVR detection and navigation
      hold-detector.js      # Hold music / human detection
      context-builder.js    # Build system prompts from context
    references/
      ivr-database.json     # Known IVR trees
      negotiation-playbook.md
    config.example.json
```

### SKILL.md (Draft)

```markdown
# Phone Agent Skill

Make outbound phone calls on behalf of the user. Navigate IVR systems, 
wait on hold, and have conversations with customer service representatives.

## Prerequisites
- Twilio account with Programmable Voice
- OpenAI API key with Realtime API access  
- Twilio phone number (provisioned via skill setup)

## Configuration
```json
{
  "twilio": {
    "accountSid": "AC...",
    "authToken": "...",
    "phoneNumber": "+1..."
  },
  "openai": {
    "apiKey": "sk-...",
    "model": "gpt-4o-realtime-preview"
  },
  "bridge": {
    "port": 8765,
    "host": "localhost"
  },
  "defaults": {
    "maxHoldMinutes": 60,
    "recordCalls": true,
    "alertChannel": "imessage",
    "alertContact": "+18135343383"
  }
}
```

## Trigger Patterns
- "call [company] about [issue]"
- "phone [company] and [action]"
- "hold for me while I wait for [company]"
- "book a table at [restaurant]"
- "schedule an appointment with [provider]"
- "negotiate my [company] bill"
- "check on my [claim/order/application]"

## Usage
```
/call Lufthansa about my lost baggage claim CPHLH52532
/call Comcast and negotiate my bill down from $189 to $120
/call Dr. Chen's office and schedule annual physical, mornings preferred
/call Stock & Barrel and book a table for 4, Saturday 7pm, one gluten-free
/hold-for-me +1-800-829-1040 (IRS) — just wait for a human and text me
```
```

### Integration with OpenClaw

```javascript
// How the skill integrates with OpenClaw's message handling

// 1. User sends: "Debra, call Lufthansa about my lost bags"
// 2. OpenClaw routes to phone-agent skill
// 3. Skill parses intent and builds context

async function handleCallRequest(message, context) {
  // Parse the request
  const parsed = await parseCallIntent(message);
  // { company: "Lufthansa", topic: "lost baggage", sentiment: "frustrated" }
  
  // Look up company info
  const companyInfo = await lookupCompany(parsed.company);
  // { phone: "+1-800-645-3880", ivrTree: {...}, avgHold: 25 }
  
  // Build context from user's files, previous conversations, etc.
  const callContext = await buildContext(parsed, context);
  
  // Notify user
  await notify("📞 Calling Lufthansa Baggage Claims at +1-800-645-3880...");
  
  // Initiate call
  const call = await initiateCall({
    to: companyInfo.phone,
    context: callContext,
    onIVR: (step) => notify(`🔢 IVR: ${step}`),
    onHold: (est) => notify(`⏳ On hold. Est. wait: ${est} min`),
    onHuman: (name) => notify(`🙋 Live agent: ${name}!`),
    onComplete: (summary) => deliverResults(summary),
    onNeedAuth: () => conferenceInUser()
  });
  
  return call;
}
```

---

## 10. Immediate Action: Lufthansa Lost Baggage

### Call Plan

**Target:** Lufthansa US Customer Service — Baggage Claims
**Number:** +1-800-645-3880
**Alternative:** +1-516-296-9650 (Lufthansa Baggage Service Center)

**Context to provide:**
- Passenger: Alex Abell
- Flight: Nov 29, 2025, Munich (MUC) → Copenhagen (CPH) → Knoxville (TYS)
- Issue: Bags delayed/lost in Copenhagen during connection
- Property Irregularity Report: CPHLH52532
- Case Number: C-130009-K8N5
- Feedback ID: FB ID 42383344
- Receipts submitted: $552.52 (Nike purchases) + Uber and taxi receipts
- Status: 4+ months with no resolution, multiple emails sent

**Conversation Strategy:**
1. Navigate to Baggage Claims → Existing Claim
2. Provide case number CPHLH52532
3. Ask for current status of reimbursement
4. If "still processing" → express that 4 months is unacceptable
5. Reference EC 261/2004 (EU regulation for delayed baggage compensation)
6. Mention intent to file DOT complaint if not resolved
7. Ask for supervisor if frontline agent can't help
8. Get a specific timeline and confirmation number for resolution
9. Ask for direct contact (email/extension) for follow-up

**Escalation references:**
- EU Regulation EC 261/2004: Airlines must compensate for delayed baggage expenses
- Montreal Convention: International liability for delayed baggage up to ~$1,700 USD (1,288 SDR)
- US DOT complaint: https://www.transportation.gov/airconsumer/file-consumer-complaint
- Lufthansa is required to respond to DOT complaints within 60 days

### Before Building: Manual Test

Before building the full skill, Alex could test the concept:
1. Use Twilio's built-in outbound call API to dial Lufthansa
2. Connect via Media Streams to a simple Node.js server
3. Proxy audio to OpenAI Realtime API with the Lufthansa context prompt
4. See how it handles the IVR and conversation

This would validate the approach in ~1-2 days of tinkering before committing to the full skill build.

---

## Appendix A: Key Resources

### Twilio
- [Twilio + OpenAI Realtime (Node.js tutorial)](https://www.twilio.com/en-us/blog/voice-ai-assistant-openai-realtime-api-node)
- [Outbound calls with OpenAI Realtime](https://www.twilio.com/en-us/blog/outbound-calls-node-openai-realtime-api-voice)
- [ConversationRelay docs](https://www.twilio.com/docs/voice/twiml/connect/conversationrelay)
- [GitHub: speech-assistant-openai-realtime-api-node](https://github.com/twilio-samples/speech-assistant-openai-realtime-api-node)
- [Media Streams docs](https://www.twilio.com/docs/voice/media-streams)

### OpenAI
- [Realtime API guide](https://developers.openai.com/api/docs/guides/realtime)
- [Voice agents guide](https://developers.openai.com/api/docs/guides/voice-agents)
- [Realtime SIP integration](https://developers.openai.com/api/docs/guides/realtime-sip)
- [Agents SDK with Twilio transport](https://openai.github.io/openai-agents-js/extensions/twilio/)

### LiveKit (for Phase 2+)
- [LiveKit Agents framework](https://docs.livekit.io/agents/)
- [Telephony integration](https://docs.livekit.io/telephony/)
- [GitHub: livekit/agents](https://github.com/livekit/agents)

### Legal
- [Tennessee recording law (one-party consent)](https://www.dmlp.org/legal-guide/tennessee-recording-law)
- [FCC ruling on AI voices in calls](https://docs.fcc.gov/public/attachments/DOC-400393A1.pdf)
- [EU EC 261/2004 passenger rights](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32004R0261)
- [DOT airline complaint form](https://www.transportation.gov/airconsumer/file-consumer-complaint)

### Competitors to Watch
- [Pine AI](https://www.19pine.ai/) — closest competitor in consumer AI calling
- [Lindy AI](https://www.lindy.ai/) — no-code AI agent platform with phone calling
- [Vapi](https://vapi.ai/) — developer voice AI platform

---

## Appendix B: Quick Cost Calculator

```
COST PER CALL = (Twilio minutes × $0.014) + (OpenAI minutes × $0.08) + Twilio recording

Example: 30-min hold + 10-min conversation = 40 total minutes
  Twilio:  40 × $0.014 = $0.56
  OpenAI:  40 × $0.08  = $3.20  (could optimize: only run AI during active portions)
  Total:   $3.76

Optimized (AI only during IVR + conversation, not hold):
  Twilio:  40 × $0.014 = $0.56
  OpenAI:  15 × $0.08  = $1.20  (5 min IVR + 10 min conversation)
  Hold monitoring: minimal (simple audio analysis, no LLM)
  Total:   $1.76

10 calls/month: $17.60 - $37.60
```

---

*This document is a living reference. Update as research continues and implementation begins.*
