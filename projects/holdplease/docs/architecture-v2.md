# HoldPlease v2 — Technical Architecture

> **Version:** 2.0 Draft  
> **Date:** 2026-03-29  
> **Author:** Debra (architecture subagent)  
> **Status:** Blueprint — ready to build from

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Tech Stack](#2-tech-stack)
3. [Database Schema](#3-database-schema)
4. [API Design](#4-api-design)
5. [Real-Time Architecture](#5-real-time-architecture)
6. [AI Pipelines](#6-ai-pipelines)
7. [Cost Tracking System](#7-cost-tracking-system)
8. [Auth System](#8-auth-system)
9. [File & Folder Structure](#9-file--folder-structure)
10. [Deployment Strategy](#10-deployment-strategy)
11. [Migration Plan from MVP](#11-migration-plan-from-mvp)

---

## 1. Executive Summary

HoldPlease v2 evolves from a single-user CLI/API tool into a multi-user SaaS product. The core phone engine (Twilio hold mode → ElevenLabs conversation mode) remains unchanged. We wrap it with:

- **User accounts** (Google SSO + email/password)
- **Issue tracker** — each customer service problem is an "Issue" with multiple call attempts
- **Smart Highlights** — AI extracts the 2 minutes that matter from a 30-minute call
- **Analytics dashboard** — ROI tracking, cost breakdowns, company difficulty rankings
- **Copywriter bot** — internal tool for product copy generation

### Architecture Philosophy

- **Keep the working engine.** `hybrid.js` is battle-tested. We refactor it into modules but don't rewrite the Twilio/ElevenLabs plumbing.
- **Next.js full-stack.** Single deployment, SSR for SEO (landing page), API routes for backend, React for dashboard.
- **Postgres for everything.** Structured data with JSONB for flexibility. No NoSQL complexity.
- **Start monolith, extract later.** One deployable unit. The phone engine runs as a separate process that shares the DB.

---

## 2. Tech Stack

| Layer | Choice | Why |
|-------|--------|-----|
| **Framework** | Next.js 15 (App Router) | Full-stack React, SSR for landing page, API routes, great DX |
| **Language** | TypeScript | Type safety across the stack, existing Node.js code ports easily |
| **Database** | PostgreSQL 16 (via Neon or Supabase) | Rock-solid relational DB, JSONB for flexible fields, full-text search |
| **ORM** | Drizzle ORM | Type-safe, lightweight, SQL-first (no magic), great migrations |
| **Auth** | NextAuth.js v5 (Auth.js) | Google SSO + credentials provider out of the box, JWT sessions |
| **Real-time** | Socket.IO (or PartyKit for serverless) | Already using WS, Socket.IO adds rooms/namespaces/reconnection |
| **File Storage** | Cloudflare R2 (S3-compatible) | Cheap object storage for recordings, no egress fees |
| **AI/LLM** | OpenAI GPT-4o-mini (highlights), Whisper (transcription) | Already integrated, cost-effective |
| **Voice** | Twilio (telephony) + ElevenLabs (conversation) | Proven in MVP, no change |
| **CSS** | Tailwind CSS + shadcn/ui | Rapid UI development, dark theme built in |
| **Hosting** | Vercel (web) + Railway/Fly.io (phone engine) | Vercel for Next.js, long-running process needs non-serverless host |
| **Queue** | BullMQ + Redis | Background jobs: highlight extraction, recording processing |
| **Monitoring** | Sentry + Axiom (or Vercel Analytics) | Error tracking + structured logging |

### Why Not...

- **tRPC?** Overkill for this scale. REST is simpler and more portable.
- **Prisma?** Drizzle is faster, lighter, and doesn't need a binary engine.
- **MongoDB?** Our data is highly relational (users → issues → calls → highlights). Postgres wins.
- **Supabase Realtime?** We need custom WebSocket logic for call streaming. Socket.IO gives us full control.

---

## 3. Database Schema

### Entity Relationship Diagram

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────────┐
│  users   │────<│  issues   │────<│  calls   │────<│  highlights  │
└──────────┘     └──────────┘     └──────────┘     └──────────────┘
                      │                │
                      │                └────<┌──────────────┐
                      │                     │ call_costs    │
                      │                     └──────────────┘
                      └────<┌──────────────┐
                           │ issue_notes   │
                           └──────────────┘
```

### Schema Definitions (Drizzle)

```typescript
// src/db/schema.ts

import { pgTable, text, uuid, timestamp, integer, numeric,
         jsonb, pgEnum, boolean, index, varchar } from 'drizzle-orm/pg-core';

// ─── Enums ─────────────────────────────────────────────────────────────

export const issueStatusEnum = pgEnum('issue_status', [
  'new',
  'researching',
  'calling',
  'waiting_on_them',
  'waiting_on_me',
  'resolved',
  'closed'
]);

export const callStatusEnum = pgEnum('call_status', [
  'queued',
  'connecting',
  'hold_mode',
  'ivr_navigating',
  'conversation_mode',
  'completed',
  'failed',
  'canceled'
]);

export const callOutcomeEnum = pgEnum('call_outcome', [
  'resolved',
  'partial',
  'callback_needed',
  'transferred',
  'no_answer',
  'busy',
  'disconnected',
  'failed',
  'unknown'
]);

export const highlightCategoryEnum = pgEnum('highlight_category', [
  'introduction',
  'the_ask',
  'key_information',
  'commitment',
  'resolution',
  'action_item',
  'escalation',
  'other'
]);

// ─── Users ─────────────────────────────────────────────────────────────

export const users = pgTable('users', {
  id: uuid('id').primaryKey().defaultRandom(),
  email: varchar('email', { length: 255 }).notNull().unique(),
  name: varchar('name', { length: 255 }),
  avatarUrl: text('avatar_url'),
  passwordHash: text('password_hash'),           // null for Google SSO users
  googleId: varchar('google_id', { length: 255 }).unique(),
  plan: varchar('plan', { length: 50 }).default('free'),  // free, pro, enterprise
  createdAt: timestamp('created_at').defaultNow().notNull(),
  updatedAt: timestamp('updated_at').defaultNow().notNull(),
}, (table) => ({
  emailIdx: index('users_email_idx').on(table.email),
  googleIdx: index('users_google_id_idx').on(table.googleId),
}));

// ─── Issues ────────────────────────────────────────────────────────────

export const issues = pgTable('issues', {
  id: uuid('id').primaryKey().defaultRandom(),
  userId: uuid('user_id').notNull().references(() => users.id, { onDelete: 'cascade' }),
  title: varchar('title', { length: 500 }).notNull(),
  company: varchar('company', { length: 255 }).notNull(),
  phoneNumber: varchar('phone_number', { length: 20 }),
  department: varchar('department', { length: 255 }),
  status: issueStatusEnum('status').default('new').notNull(),
  description: text('description'),               // user's description of the problem
  desiredOutcome: text('desired_outcome'),         // what success looks like
  referenceNumbers: jsonb('reference_numbers').$type<string[]>().default([]),
  accountInfo: jsonb('account_info').$type<Record<string, string>>().default({}),
  // AI-generated fields
  aiSummary: text('ai_summary'),                   // AI summary after calls
  resolutionNotes: text('resolution_notes'),
  // Aggregates (denormalized for fast reads)
  totalCalls: integer('total_calls').default(0),
  totalCostCents: integer('total_cost_cents').default(0),  // stored in cents
  totalHoldMinutes: integer('total_hold_minutes').default(0),
  totalConvoMinutes: integer('total_convo_minutes').default(0),
  valueSavedCents: integer('value_saved_cents').default(0),
  // Timestamps
  createdAt: timestamp('created_at').defaultNow().notNull(),
  updatedAt: timestamp('updated_at').defaultNow().notNull(),
  resolvedAt: timestamp('resolved_at'),
  closedAt: timestamp('closed_at'),
}, (table) => ({
  userIdx: index('issues_user_id_idx').on(table.userId),
  statusIdx: index('issues_status_idx').on(table.status),
  companyIdx: index('issues_company_idx').on(table.company),
}));

// ─── Calls ─────────────────────────────────────────────────────────────

export const calls = pgTable('calls', {
  id: uuid('id').primaryKey().defaultRandom(),
  issueId: uuid('issue_id').notNull().references(() => issues.id, { onDelete: 'cascade' }),
  userId: uuid('user_id').notNull().references(() => users.id, { onDelete: 'cascade' }),
  // Twilio identifiers
  callSid: varchar('call_sid', { length: 64 }).unique(),
  conferenceSid: varchar('conference_sid', { length: 64 }),
  // ElevenLabs identifiers
  elevenLabsConversationId: varchar('elevenlabs_conversation_id', { length: 128 }),
  // Call metadata
  phoneNumber: varchar('phone_number', { length: 20 }).notNull(),
  company: varchar('company', { length: 255 }),
  task: text('task').notNull(),                     // what the agent should do
  status: callStatusEnum('status').default('queued').notNull(),
  outcome: callOutcomeEnum('outcome').default('unknown'),
  // Mode tracking
  currentMode: varchar('current_mode', { length: 20 }).default('hold'),  // hold | conversation
  holdStartedAt: timestamp('hold_started_at'),
  humanDetectedAt: timestamp('human_detected_at'),
  // Transcript (full, ordered)
  transcript: jsonb('transcript').$type<TranscriptEntry[]>().default([]),
  // Recordings
  recordingUrl: text('recording_url'),              // R2/S3 URL
  recordingLocalPath: text('recording_local_path'),
  twilioRecordingUrl: text('twilio_recording_url'),
  recordingDurationSec: integer('recording_duration_sec'),
  // Outcome details
  outcomeNotes: text('outcome_notes'),              // AI-generated summary
  repName: varchar('rep_name', { length: 255 }),    // customer service rep name
  newReferenceNumbers: jsonb('new_reference_numbers').$type<string[]>().default([]),
  callbackScheduled: timestamp('callback_scheduled'),
  // Timestamps
  startedAt: timestamp('started_at').defaultNow().notNull(),
  completedAt: timestamp('completed_at'),
  durationSec: integer('duration_sec'),
}, (table) => ({
  issueIdx: index('calls_issue_id_idx').on(table.issueId),
  userIdx: index('calls_user_id_idx').on(table.userId),
  callSidIdx: index('calls_call_sid_idx').on(table.callSid),
  statusIdx: index('calls_status_idx').on(table.status),
}));

// ─── Call Costs ────────────────────────────────────────────────────────

export const callCosts = pgTable('call_costs', {
  id: uuid('id').primaryKey().defaultRandom(),
  callId: uuid('call_id').notNull().references(() => calls.id, { onDelete: 'cascade' }),
  // Individual cost components (in cents)
  twilioCallCents: integer('twilio_call_cents').default(0),
  twilioRecordingCents: integer('twilio_recording_cents').default(0),
  whisperCents: integer('whisper_cents').default(0),
  elevenLabsCents: integer('elevenlabs_cents').default(0),
  openaiAnalysisCents: integer('openai_analysis_cents').default(0),
  totalCents: integer('total_cents').default(0),
  // Duration breakdowns (seconds)
  holdDurationSec: integer('hold_duration_sec').default(0),
  convoDurationSec: integer('convo_duration_sec').default(0),
  ivrDurationSec: integer('ivr_duration_sec').default(0),
  // Metadata
  calculatedAt: timestamp('calculated_at').defaultNow().notNull(),
  rateCard: jsonb('rate_card').$type<RateCard>(),   // snapshot of rates used
}, (table) => ({
  callIdx: index('call_costs_call_id_idx').on(table.callId),
}));

// ─── Highlights ────────────────────────────────────────────────────────

export const highlights = pgTable('highlights', {
  id: uuid('id').primaryKey().defaultRandom(),
  callId: uuid('call_id').notNull().references(() => calls.id, { onDelete: 'cascade' }),
  category: highlightCategoryEnum('category').notNull(),
  title: varchar('title', { length: 255 }).notNull(),
  summary: text('summary').notNull(),
  // Transcript location
  transcriptStartIdx: integer('transcript_start_idx'),
  transcriptEndIdx: integer('transcript_end_idx'),
  transcriptExcerpt: text('transcript_excerpt'),
  // Audio clip
  audioClipUrl: text('audio_clip_url'),             // R2 URL for extracted clip
  startTimeSec: numeric('start_time_sec'),          // seconds from call start
  endTimeSec: numeric('end_time_sec'),
  // Metadata
  confidence: numeric('confidence'),                 // AI confidence 0-1
  isActionable: boolean('is_actionable').default(false),
  createdAt: timestamp('created_at').defaultNow().notNull(),
}, (table) => ({
  callIdx: index('highlights_call_id_idx').on(table.callId),
  categoryIdx: index('highlights_category_idx').on(table.category),
}));

// ─── Issue Notes (user + system) ───────────────────────────────────────

export const issueNotes = pgTable('issue_notes', {
  id: uuid('id').primaryKey().defaultRandom(),
  issueId: uuid('issue_id').notNull().references(() => issues.id, { onDelete: 'cascade' }),
  userId: uuid('user_id').references(() => users.id),
  content: text('content').notNull(),
  isSystemGenerated: boolean('is_system_generated').default(false),
  createdAt: timestamp('created_at').defaultNow().notNull(),
}, (table) => ({
  issueIdx: index('issue_notes_issue_id_idx').on(table.issueId),
}));

// ─── Company Directory (crowdsourced over time) ────────────────────────

export const companies = pgTable('companies', {
  id: uuid('id').primaryKey().defaultRandom(),
  name: varchar('name', { length: 255 }).notNull(),
  normalizedName: varchar('normalized_name', { length: 255 }).notNull().unique(),
  phoneNumbers: jsonb('phone_numbers').$type<CompanyPhone[]>().default([]),
  avgHoldMinutes: numeric('avg_hold_minutes'),
  avgCallsToResolve: numeric('avg_calls_to_resolve'),
  difficultyScore: numeric('difficulty_score'),      // 1-10
  totalCalls: integer('total_calls').default(0),
  totalIssues: integer('total_issues').default(0),
  ivrNotes: text('ivr_notes'),                       // crowdsourced IVR navigation tips
  updatedAt: timestamp('updated_at').defaultNow().notNull(),
}, (table) => ({
  nameIdx: index('companies_normalized_name_idx').on(table.normalizedName),
}));

// ─── Types ─────────────────────────────────────────────────────────────

export type TranscriptEntry = {
  role: 'agent' | 'rep' | 'ivr' | 'system';
  text: string;
  timestamp: string;           // ISO 8601
  offsetSec?: number;          // seconds from call start
};

export type RateCard = {
  twilioPerMinute: number;     // e.g., 0.02
  whisperPerMinute: number;    // e.g., 0.006
  elevenLabsPerMinute: number; // e.g., 0.13
  openaiPerToken: number;      // e.g., 0.00015
};

export type CompanyPhone = {
  number: string;
  department: string;
  verified: boolean;
  lastCalledAt?: string;
};
```

### Key Design Decisions

1. **Costs in cents (integers).** Never use floats for money. `$1.25` → `125` cents.
2. **Denormalized aggregates on issues.** `totalCalls`, `totalCostCents`, etc. are updated via triggers or application-level hooks. Avoids expensive aggregation queries on the dashboard.
3. **JSONB for flexible fields.** Transcript, reference numbers, account info — structured but variable.
4. **Company directory.** Builds over time as users make calls. Enables difficulty rankings and IVR tips.
5. **Soft timestamps everywhere.** `createdAt`, `updatedAt`, `resolvedAt`, `closedAt` — full audit trail.

---

## 4. API Design

### Base URL: `/api/v1`

All endpoints require authentication (JWT in `Authorization: Bearer <token>` header) unless marked **[public]**.

### Auth

```
POST   /api/auth/google          # Google SSO callback
POST   /api/auth/register        # Email/password registration
POST   /api/auth/login           # Email/password login
POST   /api/auth/refresh         # Refresh JWT token
POST   /api/auth/logout          # Invalidate refresh token
GET    /api/auth/me              # Current user profile
PATCH  /api/auth/me              # Update profile
```

### Issues

```
GET    /api/v1/issues                    # List user's issues (paginated, filterable)
       ?status=calling,waiting_on_them
       ?company=lufthansa
       ?sort=updatedAt:desc
       ?page=1&limit=20

POST   /api/v1/issues                    # Create new issue
       {
         "title": "Lufthansa lost baggage reimbursement",
         "company": "Lufthansa",
         "phoneNumber": "+18005811488",
         "department": "Baggage Claims",
         "description": "Filed claim #LH-38291 on March 15...",
         "desiredOutcome": "Full reimbursement of $450 for lost bag contents",
         "referenceNumbers": ["LH-38291", "BOOKING-9X2K4"],
         "accountInfo": { "bookingRef": "9X2K4", "frequentFlyer": "LH-1234567" }
       }

GET    /api/v1/issues/:id                # Get issue details + calls + highlights
PATCH  /api/v1/issues/:id                # Update issue (status, notes, etc.)
DELETE /api/v1/issues/:id                # Soft delete (set status=closed)

POST   /api/v1/issues/:id/notes          # Add note to issue
GET    /api/v1/issues/:id/notes          # List issue notes

POST   /api/v1/issues/:id/calls          # Trigger a new call for this issue
       {
         "task": "Follow up on claim #LH-38291, ask for reimbursement status",
         "callback": "+18135343383"
       }
```

### Calls

```
GET    /api/v1/calls                     # List user's calls (paginated)
       ?issueId=uuid
       ?status=completed
       ?sort=startedAt:desc

GET    /api/v1/calls/:id                 # Call details + transcript + costs + highlights
POST   /api/v1/calls/:id/end            # Manually end an active call

GET    /api/v1/calls/:id/recording       # Stream call recording (audio)
GET    /api/v1/calls/:id/recording/download  # Download recording

GET    /api/v1/calls/:id/highlights      # List highlights for a call
GET    /api/v1/calls/:id/highlights/:hid/audio  # Stream highlight audio clip
```

### Analytics

```
GET    /api/v1/analytics/dashboard       # Main dashboard metrics
       Response:
       {
         "totalIssues": 12,
         "resolvedIssues": 8,
         "totalCalls": 34,
         "totalHoldTimeSavedMinutes": 487,
         "totalCostCents": 4250,
         "totalValueSavedCents": 125000,
         "avgCostPerResolutionCents": 531,
         "streakDays": 3
       }

GET    /api/v1/analytics/costs           # Cost breakdown over time
       ?period=30d|90d|all
       Response: time series of cost components

GET    /api/v1/analytics/companies       # Company difficulty rankings
       ?sort=difficultyScore:desc
       &limit=20

GET    /api/v1/analytics/roi             # ROI analysis
       Response:
       {
         "hoursSaved": 8.1,
         "moneyRecovered": 1250.00,
         "costToRecover": 42.50,
         "roi": 2841   // percent
       }
```

### Phone (Internal, used by phone engine)

```
POST   /api/internal/calls/:callSid/status       # Twilio status webhook
POST   /api/internal/calls/:callSid/transcript    # Append transcript entry
POST   /api/internal/calls/:callSid/human-detected  # Trigger mode switch
POST   /api/internal/calls/:callSid/completed     # Call completed, trigger post-processing
POST   /api/internal/calls/:callSid/cost          # Update cost breakdown
```

### Webhooks (Twilio)

```
POST   /webhooks/twilio/voice-connect    # TwiML for call connect
POST   /webhooks/twilio/voice-status     # Call status updates
POST   /webhooks/twilio/recording-status # Recording ready notification
```

### Lookup (Public utilities)

```
POST   /api/v1/lookup/company            # AI phone number lookup
       { "company": "Lufthansa" }
       Response: { "results": [{ "name": "...", "phone": "...", "department": "..." }] }
```

### Copywriter Bot

```
POST   /api/v1/copywriter/generate
       {
         "type": "landing_hero" | "email_welcome" | "email_call_complete" | "in_app_empty_state" | "social_post",
         "context": { ... },             // optional context data
         "tone": "confident" | "playful" | "professional"
       }
       Response: { "copy": "...", "alternatives": ["...", "..."] }
```

---

## 5. Real-Time Architecture

### WebSocket Events (Socket.IO)

The client connects to a Socket.IO namespace and joins rooms based on their user ID and active issue/call IDs.

```
Connection: wss://holdplease.app/ws
Auth: JWT token in handshake auth
```

#### Client → Server

```typescript
// Join rooms for real-time updates
socket.emit('subscribe:issue', { issueId: 'uuid' });
socket.emit('subscribe:call', { callId: 'uuid' });
socket.emit('unsubscribe:issue', { issueId: 'uuid' });
socket.emit('unsubscribe:call', { callId: 'uuid' });
```

#### Server → Client

```typescript
// Call lifecycle events
'call:status'         → { callId, status, statusMessage, mode }
'call:mode_switch'    → { callId, from: 'hold', to: 'conversation', humanDetectedAt }
'call:transcript'     → { callId, entry: { role, text, timestamp, offsetSec } }
'call:completed'      → { callId, outcome, durationSec, costCents }
'call:recording_ready'→ { callId, recordingUrl }

// Issue lifecycle events
'issue:status'        → { issueId, status, updatedAt }
'issue:updated'       → { issueId, changes: { ... } }

// Highlight events (after post-processing)
'call:highlights_ready' → { callId, highlightCount, highlights: [...] }

// Dashboard events
'dashboard:update'    → { totalCalls, totalHoldTimeSaved, totalCost, ... }
```

### Architecture Diagram

```
┌─────────────┐     ┌─────────────────────────┐     ┌───────────────┐
│   Browser    │◄───►│  Next.js (Vercel)        │     │  Phone Engine  │
│  Socket.IO   │     │  API Routes + Socket.IO  │◄───►│  (Railway)     │
│  client      │     │  Auth, DB, Business Logic │     │  Twilio WS     │
└─────────────┘     └────────┬────────────────┘     │  ElevenLabs    │
                             │                       │  Hold Detector │
                             ▼                       └───────┬───────┘
                    ┌─────────────────┐                      │
                    │   PostgreSQL    │◄─────────────────────┘
                    │   (Neon)        │     (shared DB access)
                    └─────────────────┘
                             ▲
                             │
                    ┌─────────────────┐
                    │   Redis/BullMQ  │  ← Job queue for highlight
                    │   (Upstash)     │    extraction, cost calc,
                    └─────────────────┘    recording processing
```

### How Real-Time Updates Flow

1. **Phone engine** (running on Railway) processes a Twilio media stream
2. Human detected → engine writes to DB + publishes event to Redis pub/sub
3. **Next.js server** subscribes to Redis pub/sub, relays to correct Socket.IO room
4. **Browser** receives event, updates UI instantly

For the initial launch (simpler): skip Redis pub/sub. Phone engine calls an internal webhook on the Next.js server, which emits the Socket.IO event directly.

---

## 6. AI Pipelines

### 6.1 Smart Highlight Extraction

Triggered as a BullMQ job after a call completes.

```
┌────────────┐    ┌─────────────┐    ┌─────────────────┐    ┌───────────┐
│ Call        │───►│ Fetch full  │───►│ GPT-4o-mini     │───►│ Store     │
│ completes   │    │ transcript  │    │ Highlight prompt │    │ highlights│
└────────────┘    │ + recording │    │ + JSON output    │    │ in DB     │
                  └─────────────┘    └────────┬────────┘    └───────────┘
                                              │
                                     ┌────────▼────────┐
                                     │ ffmpeg: extract  │
                                     │ audio clips per  │
                                     │ highlight range  │
                                     └────────┬────────┘
                                              │
                                     ┌────────▼────────┐
                                     │ Upload clips    │
                                     │ to R2           │
                                     └─────────────────┘
```

#### Highlight Extraction Prompt

```typescript
const HIGHLIGHT_SYSTEM_PROMPT = `You are analyzing a customer service phone call transcript.
Extract the key moments a busy person needs to know about.

For each highlight, provide:
- category: one of [introduction, the_ask, key_information, commitment, resolution, action_item, escalation]
- title: short label (3-8 words)
- summary: 1-2 sentence summary of this moment
- transcript_start_idx: index of first transcript entry in this highlight
- transcript_end_idx: index of last transcript entry
- transcript_excerpt: the relevant dialogue (verbatim from transcript)
- is_actionable: true if this requires follow-up from the caller
- confidence: 0.0-1.0 how confident you are this is a real highlight

Rules:
- Always include "the_ask" (what the caller requested)
- Always include "resolution" if one was reached
- Extract ALL commitments/promises made by the rep (e.g., "I'll send a confirmation email")
- Flag any reference numbers, case IDs, or names mentioned
- Keep highlights focused — each one should be 15-60 seconds of call time
- Output valid JSON array. No markdown.`;

const userPrompt = `Call context:
Company: ${call.company}
Task: ${call.task}

Transcript (${transcript.length} entries):
${transcript.map((t, i) => `[${i}] ${t.role}: ${t.text}`).join('\n')}`;
```

#### Audio Clip Extraction

```bash
# Extract a clip from the full recording
# startSec and endSec come from mapping transcript indices to timestamps
ffmpeg -i recording.wav -ss ${startSec} -to ${endSec} -c:a libopus -b:a 48k highlight_${id}.ogg
```

### 6.2 Call Outcome Analysis

Run after highlights are extracted. Updates the call and issue records.

```typescript
const OUTCOME_PROMPT = `Based on this call transcript and highlights, determine:
1. outcome: resolved | partial | callback_needed | transferred | disconnected | failed
2. rep_name: the customer service rep's name (if given)
3. new_reference_numbers: any new case/reference/confirmation numbers
4. summary: 2-3 sentence summary of what happened
5. next_steps: what needs to happen next (if anything)
6. value_saved_cents: estimated monetary value recovered/saved (0 if none)

Output valid JSON.`;
```

### 6.3 Copywriter Bot Pipeline

Simple single-prompt pipeline with template injection:

```typescript
const COPYWRITER_SYSTEM = `You are the HoldPlease brand copywriter.
Brand voice: Confident, slightly cheeky, empathetic. We hate hold music as much as you do.
Think: "What if your most competent friend handled your annoying phone calls?"

Never be: corporate, stiff, apologetic, or use "leverage", "synergy", or "streamline".
Always be: human, specific, a little funny, action-oriented.`;

// Templates per copy type
const templates = {
  landing_hero: 'Write a hero headline + subhead for the landing page. Max 10 words headline, 20 words subhead.',
  email_call_complete: 'Write a notification email for when a call is done. Include: what happened, highlights summary, next steps.',
  // ... etc
};
```

---

## 7. Cost Tracking System

### Rate Card (configurable, stored in DB or env)

```typescript
const RATE_CARD: RateCard = {
  // Twilio
  twilioPerMinuteOutbound: 0.014,   // per minute, US calls
  twilioPerMinuteRecording: 0.0025, // per minute of recording storage
  twilioPerSms: 0.0079,             // if we add SMS notifications

  // OpenAI
  whisperPerMinute: 0.006,          // Whisper API per minute of audio
  gpt4oMiniInputPer1kTokens: 0.00015,
  gpt4oMiniOutputPer1kTokens: 0.0006,

  // ElevenLabs
  elevenLabsConvoPerMinute: 0.13,   // Conversational AI per minute

  // Infrastructure (amortized estimates, optional)
  cloudflareR2PerGb: 0.015,         // storage per GB/month
};
```

### Cost Calculation Flow

```typescript
// Runs after call completion
async function calculateCallCost(callId: string) {
  const call = await db.query.calls.findFirst({ where: eq(calls.id, callId) });
  if (!call) return;

  const holdSec = call.humanDetectedAt && call.holdStartedAt
    ? (new Date(call.humanDetectedAt).getTime() - new Date(call.holdStartedAt).getTime()) / 1000
    : call.durationSec || 0;

  const convoSec = call.humanDetectedAt && call.completedAt
    ? (new Date(call.completedAt).getTime() - new Date(call.humanDetectedAt).getTime()) / 1000
    : 0;

  const holdMin = holdSec / 60;
  const convoMin = convoSec / 60;
  const totalMin = (call.durationSec || 0) / 60;

  const costs = {
    twilioCallCents: Math.ceil(totalMin * RATE_CARD.twilioPerMinuteOutbound * 100),
    twilioRecordingCents: Math.ceil(totalMin * RATE_CARD.twilioPerMinuteRecording * 100),
    whisperCents: Math.ceil(holdMin * RATE_CARD.whisperPerMinute * 100),  // only hold mode uses Whisper
    elevenLabsCents: Math.ceil(convoMin * RATE_CARD.elevenLabsConvoPerMinute * 100),
    openaiAnalysisCents: 2, // ~$0.02 for highlight extraction, rough estimate
  };

  costs.totalCents = Object.values(costs).reduce((a, b) => a + b, 0);

  // Insert cost record
  await db.insert(callCosts).values({
    callId,
    ...costs,
    holdDurationSec: Math.round(holdSec),
    convoDurationSec: Math.round(convoSec),
    rateCard: RATE_CARD,
  });

  // Update issue aggregates
  await db.execute(sql`
    UPDATE issues SET
      total_cost_cents = total_cost_cents + ${costs.totalCents},
      total_hold_minutes = total_hold_minutes + ${Math.round(holdMin)},
      total_convo_minutes = total_convo_minutes + ${Math.round(convoMin)},
      total_calls = total_calls + 1,
      updated_at = NOW()
    WHERE id = ${call.issueId}
  `);

  return costs;
}
```

### Dashboard Aggregation Query

```sql
-- User's ROI dashboard
SELECT
  COUNT(DISTINCT i.id) as total_issues,
  COUNT(DISTINCT i.id) FILTER (WHERE i.status = 'resolved') as resolved_issues,
  COUNT(c.id) as total_calls,
  COALESCE(SUM(cc.hold_duration_sec), 0) / 60 as total_hold_minutes,
  COALESCE(SUM(cc.total_cents), 0) as total_cost_cents,
  COALESCE(SUM(i.value_saved_cents), 0) as total_value_saved_cents,
  CASE
    WHEN COUNT(DISTINCT i.id) FILTER (WHERE i.status = 'resolved') > 0
    THEN COALESCE(SUM(cc.total_cents), 0) / COUNT(DISTINCT i.id) FILTER (WHERE i.status = 'resolved')
    ELSE 0
  END as avg_cost_per_resolution_cents
FROM issues i
LEFT JOIN calls c ON c.issue_id = i.id
LEFT JOIN call_costs cc ON cc.call_id = c.id
WHERE i.user_id = $1;
```

---

## 8. Auth System

### NextAuth.js v5 Configuration

```typescript
// src/lib/auth.ts
import NextAuth from 'next-auth';
import Google from 'next-auth/providers/google';
import Credentials from 'next-auth/providers/credentials';
import { DrizzleAdapter } from '@auth/drizzle-adapter';
import bcrypt from 'bcryptjs';

export const { handlers, signIn, signOut, auth } = NextAuth({
  adapter: DrizzleAdapter(db),
  session: { strategy: 'jwt', maxAge: 30 * 24 * 60 * 60 }, // 30 days
  providers: [
    Google({
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
    }),
    Credentials({
      credentials: {
        email: { type: 'email' },
        password: { type: 'password' },
      },
      async authorize(credentials) {
        const user = await db.query.users.findFirst({
          where: eq(users.email, credentials.email as string),
        });
        if (!user?.passwordHash) return null;
        const valid = await bcrypt.compare(
          credentials.password as string,
          user.passwordHash,
        );
        return valid ? { id: user.id, email: user.email, name: user.name } : null;
      },
    }),
  ],
  callbacks: {
    jwt({ token, user }) {
      if (user) token.userId = user.id;
      return token;
    },
    session({ session, token }) {
      session.user.id = token.userId as string;
      return session;
    },
  },
});
```

### Auth Middleware

```typescript
// src/middleware.ts
import { auth } from '@/lib/auth';

export default auth((req) => {
  const isApiRoute = req.nextUrl.pathname.startsWith('/api/v1');
  const isAuthRoute = req.nextUrl.pathname.startsWith('/api/auth');
  const isWebhook = req.nextUrl.pathname.startsWith('/webhooks');
  const isPublic = req.nextUrl.pathname === '/' ||
                   req.nextUrl.pathname.startsWith('/login') ||
                   req.nextUrl.pathname.startsWith('/register');

  if (isAuthRoute || isWebhook || isPublic) return;

  if (!req.auth && isApiRoute) {
    return new Response('Unauthorized', { status: 401 });
  }
  if (!req.auth && !isPublic) {
    return Response.redirect(new URL('/login', req.url));
  }
});

export const config = {
  matcher: ['/((?!_next/static|_next/image|favicon.ico).*)'],
};
```

---

## 9. File & Folder Structure

```
holdplease/
├── src/
│   ├── app/                          # Next.js App Router
│   │   ├── layout.tsx                # Root layout (providers, theme)
│   │   ├── page.tsx                  # Landing page (public, SSR)
│   │   ├── login/
│   │   │   └── page.tsx
│   │   ├── register/
│   │   │   └── page.tsx
│   │   ├── dashboard/
│   │   │   ├── layout.tsx            # Authenticated layout (sidebar, nav)
│   │   │   ├── page.tsx              # Main dashboard (analytics, hero metrics)
│   │   │   ├── issues/
│   │   │   │   ├── page.tsx          # Issue list (filterable, sortable)
│   │   │   │   ├── new/
│   │   │   │   │   └── page.tsx      # New issue form
│   │   │   │   └── [id]/
│   │   │   │       ├── page.tsx      # Issue detail (calls, highlights, timeline)
│   │   │   │       └── call/
│   │   │   │           └── page.tsx  # Active call view (live transcript)
│   │   │   ├── calls/
│   │   │   │   └── [id]/
│   │   │   │       └── page.tsx      # Call detail (transcript, highlights, recording)
│   │   │   ├── analytics/
│   │   │   │   └── page.tsx          # Full analytics page
│   │   │   └── settings/
│   │   │       └── page.tsx          # User settings, callback number, etc.
│   │   └── api/
│   │       ├── auth/
│   │       │   └── [...nextauth]/
│   │       │       └── route.ts
│   │       ├── v1/
│   │       │   ├── issues/
│   │       │   │   ├── route.ts              # GET (list), POST (create)
│   │       │   │   └── [id]/
│   │       │   │       ├── route.ts          # GET, PATCH, DELETE
│   │       │   │       ├── calls/
│   │       │   │       │   └── route.ts      # POST (start call)
│   │       │   │       └── notes/
│   │       │   │           └── route.ts      # GET, POST
│   │       │   ├── calls/
│   │       │   │   ├── route.ts              # GET (list)
│   │       │   │   └── [id]/
│   │       │   │       ├── route.ts          # GET
│   │       │   │       ├── end/
│   │       │   │       │   └── route.ts      # POST
│   │       │   │       ├── recording/
│   │       │   │       │   └── route.ts      # GET (stream), GET /download
│   │       │   │       └── highlights/
│   │       │   │           └── route.ts      # GET
│   │       │   ├── analytics/
│   │       │   │   ├── dashboard/
│   │       │   │   │   └── route.ts
│   │       │   │   ├── costs/
│   │       │   │   │   └── route.ts
│   │       │   │   ├── companies/
│   │       │   │   │   └── route.ts
│   │       │   │   └── roi/
│   │       │   │       └── route.ts
│   │       │   ├── lookup/
│   │       │   │   └── route.ts
│   │       │   └── copywriter/
│   │       │       └── route.ts
│   │       ├── internal/                     # Phone engine → web server
│   │       │   └── calls/
│   │       │       └── [callSid]/
│   │       │           ├── status/route.ts
│   │       │           ├── transcript/route.ts
│   │       │           └── completed/route.ts
│   │       └── webhooks/
│   │           └── twilio/
│   │               ├── voice-connect/route.ts
│   │               ├── voice-status/route.ts
│   │               └── recording-status/route.ts
│   │
│   ├── components/
│   │   ├── ui/                       # shadcn/ui components
│   │   │   ├── button.tsx
│   │   │   ├── card.tsx
│   │   │   ├── dialog.tsx
│   │   │   └── ...
│   │   ├── layout/
│   │   │   ├── sidebar.tsx
│   │   │   ├── header.tsx
│   │   │   └── mobile-nav.tsx
│   │   ├── issues/
│   │   │   ├── issue-card.tsx
│   │   │   ├── issue-form.tsx
│   │   │   ├── issue-timeline.tsx
│   │   │   ├── status-badge.tsx
│   │   │   └── status-pipeline.tsx
│   │   ├── calls/
│   │   │   ├── call-card.tsx
│   │   │   ├── live-transcript.tsx
│   │   │   ├── call-status-indicator.tsx
│   │   │   └── audio-player.tsx
│   │   ├── highlights/
│   │   │   ├── highlight-card.tsx
│   │   │   ├── highlight-timeline.tsx
│   │   │   └── highlight-player.tsx   # Mini audio player per highlight
│   │   ├── analytics/
│   │   │   ├── hero-metric.tsx
│   │   │   ├── cost-breakdown-chart.tsx
│   │   │   ├── company-rankings.tsx
│   │   │   └── roi-card.tsx
│   │   └── common/
│   │       ├── phone-input.tsx
│   │       ├── company-search.tsx
│   │       └── loading-skeleton.tsx
│   │
│   ├── lib/
│   │   ├── auth.ts                   # NextAuth config
│   │   ├── db/
│   │   │   ├── index.ts              # Drizzle client
│   │   │   ├── schema.ts             # Schema definitions
│   │   │   └── migrations/           # Drizzle migration files
│   │   ├── ai/
│   │   │   ├── highlights.ts         # Highlight extraction pipeline
│   │   │   ├── outcome-analysis.ts   # Call outcome analysis
│   │   │   ├── copywriter.ts         # Copy generation
│   │   │   └── prompts.ts            # All AI prompts in one place
│   │   ├── cost/
│   │   │   ├── calculator.ts         # Cost calculation logic
│   │   │   └── rate-card.ts          # Rate definitions
│   │   ├── queue/
│   │   │   ├── index.ts              # BullMQ setup
│   │   │   ├── workers/
│   │   │   │   ├── highlight-worker.ts
│   │   │   │   ├── cost-worker.ts
│   │   │   │   └── recording-worker.ts
│   │   │   └── jobs.ts               # Job type definitions
│   │   ├── realtime/
│   │   │   ├── socket-server.ts      # Socket.IO server setup
│   │   │   └── events.ts             # Event type definitions
│   │   ├── storage/
│   │   │   └── r2.ts                 # Cloudflare R2 client
│   │   └── utils/
│   │       ├── format.ts             # Currency, time formatting
│   │       └── phone.ts              # Phone number parsing/formatting
│   │
│   ├── hooks/
│   │   ├── use-socket.ts             # Socket.IO React hook
│   │   ├── use-call-status.ts        # Real-time call status
│   │   └── use-dashboard-stats.ts    # Dashboard auto-refresh
│   │
│   └── types/
│       └── index.ts                  # Shared TypeScript types
│
├── phone-engine/                     # Extracted from current src/
│   ├── index.ts                      # Entry point
│   ├── hybrid.ts                     # Core hold → convo engine (ported from hybrid.js)
│   ├── hold-detector.ts              # Audio analysis for human detection
│   ├── ivr-navigator.ts              # DTMF navigation
│   ├── recorder.ts                   # Local recording management
│   ├── transcriber.ts                # Whisper integration
│   ├── alerter.ts                    # Callback notifications
│   └── db-client.ts                  # Direct DB access for the engine
│
├── drizzle.config.ts
├── next.config.ts
├── tailwind.config.ts
├── tsconfig.json
├── package.json
├── .env.local                        # Local env vars
├── .env.example
│
├── docs/
│   ├── architecture-v2.md            # This file
│   └── api-reference.md
│
├── demo/                             # Existing demo assets
├── recordings/                       # Local recording cache (gitignored)
└── data/                             # Legacy JSON storage (removed after migration)
```

---

## 10. Deployment Strategy

### Phase 1: Single-Server (Launch)

Everything on one Railway/Fly.io instance to keep it simple.

```
┌─────────────────────────────────────────┐
│  Railway / Fly.io (1 instance)          │
│                                         │
│  ┌──────────┐  ┌──────────────────┐    │
│  │ Next.js  │  │  Phone Engine    │    │
│  │ (port    │  │  (child process  │    │
│  │  3000)   │  │   or same proc)  │    │
│  └────┬─────┘  └────────┬─────────┘    │
│       │                  │              │
│       └──────┬───────────┘              │
│              ▼                          │
│  ┌──────────────────┐                   │
│  │ PostgreSQL (Neon) │ (external)       │
│  └──────────────────┘                   │
│  ┌──────────────────┐                   │
│  │ Redis (Upstash)  │ (external)        │
│  └──────────────────┘                   │
└─────────────────────────────────────────┘
```

**Why not Vercel?** The phone engine needs persistent WebSocket connections (Twilio media streams) and long-running processes. Vercel serverless functions have a 30-second timeout. We need a traditional server.

**Alternative:** Deploy the Next.js frontend on Vercel (with serverless API routes for everything except real-time), and only the phone engine on Railway. This works but adds complexity. Start simple, split later.

### Phase 2: Split Architecture (Scale)

When traffic justifies it:

```
Vercel (Next.js frontend + API)
  ↕ Redis pub/sub
Railway (Phone Engine — autoscaling)
  ↕
Neon (PostgreSQL)  +  Upstash (Redis)  +  R2 (Recordings)
```

### Domain & SSL

- **Production:** `holdplease.app` (or `.com`)
- **Staging:** `staging.holdplease.app`
- **Twilio webhooks:** Must use HTTPS with valid SSL. Railway/Fly provide this automatically.

### Environment Variables

```bash
# Database
DATABASE_URL=postgresql://...

# Auth
NEXTAUTH_URL=https://holdplease.app
NEXTAUTH_SECRET=...
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...

# Twilio
TWILIO_ACCOUNT_SID=...
TWILIO_AUTH_TOKEN=...
TWILIO_PHONE_NUMBER=+18653915873

# OpenAI
OPENAI_API_KEY=...

# ElevenLabs
ELEVEN_LABS_API_KEY=...
ELEVEN_AGENT_ID=...

# Redis
REDIS_URL=redis://...

# Storage
R2_ACCOUNT_ID=...
R2_ACCESS_KEY_ID=...
R2_SECRET_ACCESS_KEY=...
R2_BUCKET=holdplease-recordings

# Internal
INTERNAL_API_KEY=...  # Phone engine → web server auth
PHONE_ENGINE_URL=http://localhost:3981  # or internal URL
```

---

## 11. Migration Plan from MVP

### Phase 0: Prep (Day 1)

1. **Set up the new project** alongside the existing one
   ```bash
   npx create-next-app@latest holdplease-v2 --typescript --tailwind --app --src-dir
   ```
2. **Provision infrastructure:**
   - Neon Postgres database
   - Upstash Redis
   - Cloudflare R2 bucket
3. **Run initial Drizzle migrations** to create all tables
4. **Configure NextAuth** with Google SSO

### Phase 1: Port the Phone Engine (Days 2-4)

1. Convert `hybrid.js` → `phone-engine/hybrid.ts` (TypeScript port)
2. Replace JSON file store with Postgres writes
3. Keep the same Twilio webhook URLs but point them at the new codebase
4. Test: make a call, verify it writes to Postgres correctly
5. **Validate:** Call lifecycle works end-to-end with new DB

### Phase 2: Build Core UI (Days 5-10)

1. Auth pages (login, register, Google SSO)
2. Dashboard layout (sidebar, header)
3. Issue list + create form
4. Issue detail page
5. Call status page with live transcript (Socket.IO)
6. Call history with recording playback

### Phase 3: Smart Highlights (Days 11-14)

1. Implement BullMQ workers
2. Highlight extraction pipeline (GPT-4o-mini)
3. Audio clip extraction (ffmpeg)
4. Upload clips to R2
5. Highlight UI components (timeline, mini player)

### Phase 4: Analytics & Polish (Days 15-18)

1. Dashboard metrics queries
2. Cost tracking system
3. ROI calculations
4. Company rankings
5. Charts (recharts or similar)

### Phase 5: Data Migration (Day 19)

Migrate existing `data/calls.json` records:

```typescript
// scripts/migrate-v1-calls.ts
import v1Calls from '../data/calls.json';

for (const v1Call of v1Calls) {
  // Create a default issue for each v1 call
  const issue = await db.insert(issues).values({
    userId: ADMIN_USER_ID,  // Alex's account
    title: `${v1Call.company} - ${v1Call.task.slice(0, 60)}`,
    company: v1Call.company,
    phoneNumber: v1Call.phoneNumber,
    status: v1Call.status === 'completed' ? 'resolved' : 'new',
    description: v1Call.task,
  }).returning();

  // Create the call record
  await db.insert(calls).values({
    issueId: issue[0].id,
    userId: ADMIN_USER_ID,
    callSid: v1Call.callSid,
    phoneNumber: v1Call.phoneNumber,
    company: v1Call.company,
    task: v1Call.task,
    status: v1Call.status === 'completed' ? 'completed' : 'failed',
    transcript: v1Call.transcript || [],
    startedAt: new Date(v1Call.startedAt),
    completedAt: v1Call.completedAt ? new Date(v1Call.completedAt) : null,
    // Map existing recording paths
    recordingLocalPath: v1Call.recordingPath,
  });
}
```

### Phase 6: Copywriter Bot + Launch (Day 20)

1. Implement copywriter API
2. Generate landing page copy
3. Deploy to production
4. Cut over DNS

### Rollback Plan

Keep the v1 codebase running on the current port (3981) throughout migration. The v2 app runs on port 3000. Twilio webhook URLs are the switch — point them back to v1 if anything breaks.

---

## Appendix A: Key Technical Decisions Log

| Decision | Choice | Alternatives Considered | Rationale |
|----------|--------|------------------------|-----------|
| Framework | Next.js | Remix, SvelteKit, separate backend | Alex already deploys on Vercel, SSR for landing page, single codebase |
| Database | PostgreSQL | SQLite, MongoDB, Supabase | Relational data, JSONB flexibility, proven scale |
| ORM | Drizzle | Prisma, Kysely, raw SQL | Type-safe + lightweight, no binary engine |
| Auth | NextAuth v5 | Clerk, Supabase Auth, custom | Free, flexible, Google SSO built-in |
| Queue | BullMQ | Inngest, Trigger.dev, pg-boss | Simple, Redis-backed, good DX |
| Storage | Cloudflare R2 | S3, Supabase Storage | Zero egress fees, S3-compatible |
| Hosting | Railway (monolith) | Fly.io, Render, EC2 | Good DX, persistent processes, easy deploy |

## Appendix B: Cost Estimate Per Call

| Component | Hold Mode (30 min) | Convo Mode (5 min) | Total |
|-----------|-------------------|-------------------|-------|
| Twilio outbound | $0.42 | (included) | $0.42 |
| Twilio recording | $0.09 | (included) | $0.09 |
| Whisper transcription | $0.18 | — | $0.18 |
| ElevenLabs conversation | — | $0.65 | $0.65 |
| GPT-4o-mini (analysis) | — | — | ~$0.02 |
| **Total** | | | **~$1.36** |

Typical call cost: **$0.80 - $2.00** depending on hold time and conversation length.

## Appendix C: Future Considerations

- **Multi-agent:** Different AI personas for different companies/situations
- **SMS/Email follow-up:** Automated follow-ups when in "Waiting on Them" status
- **Calendar integration:** Schedule calls during company business hours
- **Browser extension:** "Call this number for me" button on any website
- **Mobile app:** Push notifications when call connects, listen in on live calls
- **Team/enterprise:** Shared issues, delegation, audit logs
- **IVR crowdsourcing:** Users share IVR navigation paths, we auto-navigate faster
- **Voice cloning:** Call as "you" (with consent) for identity verification
