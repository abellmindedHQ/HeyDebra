import {
  sqliteTable,
  text,
  integer,
  real,
  index,
} from 'drizzle-orm/sqlite-core';
import { sql } from 'drizzle-orm';

// ─── Enums (as text with checks for SQLite) ────────────────────────────────

export const ISSUE_STATUSES = [
  'new',
  'researching',
  'calling',
  'waiting_on_them',
  'waiting_on_me',
  'resolved',
  'closed',
] as const;

export const CALL_STATUSES = [
  'queued',
  'connecting',
  'hold_mode',
  'ivr_navigating',
  'conversation_mode',
  'completed',
  'failed',
  'canceled',
] as const;

export const CALL_OUTCOMES = [
  'resolved',
  'partial',
  'callback_needed',
  'transferred',
  'no_answer',
  'busy',
  'disconnected',
  'failed',
  'unknown',
] as const;

export const HIGHLIGHT_CATEGORIES = [
  'introduction',
  'the_ask',
  'key_information',
  'commitment',
  'resolution',
  'action_item',
  'escalation',
  'other',
] as const;

export const CALL_COST_COMPONENTS = [
  'twilio',
  'whisper',
  'elevenlabs',
  'openai',
] as const;

// ─── Users ─────────────────────────────────────────────────────────────────

export const users = sqliteTable('users', {
  id: text('id').primaryKey(),
  email: text('email').notNull().unique(),
  name: text('name'),
  image: text('image'),
  googleId: text('google_id').unique(),
  passwordHash: text('password_hash'),
  plan: text('plan').default('free'),
  createdAt: text('created_at').default(sql`(datetime('now'))`).notNull(),
  updatedAt: text('updated_at').default(sql`(datetime('now'))`).notNull(),
}, (table) => [
  index('users_email_idx').on(table.email),
  index('users_google_id_idx').on(table.googleId),
]);

// NextAuth required tables
export const accounts = sqliteTable('accounts', {
  userId: text('userId').notNull().references(() => users.id, { onDelete: 'cascade' }),
  type: text('type').notNull(),
  provider: text('provider').notNull(),
  providerAccountId: text('providerAccountId').notNull(),
  refresh_token: text('refresh_token'),
  access_token: text('access_token'),
  expires_at: integer('expires_at'),
  token_type: text('token_type'),
  scope: text('scope'),
  id_token: text('id_token'),
  session_state: text('session_state'),
});

export const sessions = sqliteTable('sessions', {
  sessionToken: text('sessionToken').primaryKey(),
  userId: text('userId').notNull().references(() => users.id, { onDelete: 'cascade' }),
  expires: text('expires').notNull(),
});

export const verificationTokens = sqliteTable('verificationTokens', {
  identifier: text('identifier').notNull(),
  token: text('token').notNull(),
  expires: text('expires').notNull(),
});

// ─── Companies ─────────────────────────────────────────────────────────────

export const companies = sqliteTable('companies', {
  id: text('id').primaryKey(),
  name: text('name').notNull(),
  normalizedName: text('normalized_name').notNull().unique(),
  mainPhone: text('main_phone'),
  departments: text('departments', { mode: 'json' }).$type<Array<{ name: string; phone: string }>>().default([]),
  avgHoldMins: real('avg_hold_mins'),
  avgResolutionCalls: real('avg_resolution_calls'),
  successRate: real('success_rate'),
  ivrTree: text('ivr_tree', { mode: 'json' }).$type<Record<string, unknown>>().default({}),
  notes: text('notes'),
  totalCalls: integer('total_calls').default(0),
  totalIssues: integer('total_issues').default(0),
  createdAt: text('created_at').default(sql`(datetime('now'))`).notNull(),
  updatedAt: text('updated_at').default(sql`(datetime('now'))`).notNull(),
}, (table) => [
  index('companies_normalized_name_idx').on(table.normalizedName),
]);

// ─── Issues ────────────────────────────────────────────────────────────────

export const issues = sqliteTable('issues', {
  id: text('id').primaryKey(),
  userId: text('user_id').notNull().references(() => users.id, { onDelete: 'cascade' }),
  title: text('title').notNull(),
  description: text('description'),
  company: text('company').notNull(),
  companyPhone: text('company_phone'),
  department: text('department'),
  status: text('status').default('new').notNull(),
  priority: integer('priority').default(3), // 1=urgent, 2=high, 3=normal, 4=low
  desiredOutcome: text('desired_outcome'),
  referenceNumbers: text('reference_numbers', { mode: 'json' }).$type<string[]>().default([]),
  accountInfo: text('account_info', { mode: 'json' }).$type<Record<string, string>>().default({}),
  aiSummary: text('ai_summary'),
  resolutionNotes: text('resolution_notes'),
  // Aggregates
  totalCalls: integer('total_calls').default(0),
  totalCostCents: integer('total_cost_cents').default(0),
  totalDurationSecs: integer('total_duration_secs').default(0),
  totalHoldSecs: integer('total_hold_secs').default(0),
  // Outcome
  outcomeType: text('outcome_type'),
  outcomeValueCents: integer('outcome_value_cents').default(0),
  outcomeDescription: text('outcome_description'),
  // Timestamps
  createdAt: text('created_at').default(sql`(datetime('now'))`).notNull(),
  updatedAt: text('updated_at').default(sql`(datetime('now'))`).notNull(),
  resolvedAt: text('resolved_at'),
  closedAt: text('closed_at'),
}, (table) => [
  index('issues_user_id_idx').on(table.userId),
  index('issues_status_idx').on(table.status),
  index('issues_company_idx').on(table.company),
]);

// ─── Calls ─────────────────────────────────────────────────────────────────

export const calls = sqliteTable('calls', {
  id: text('id').primaryKey(),
  issueId: text('issue_id').notNull().references(() => issues.id, { onDelete: 'cascade' }),
  callSid: text('call_sid').unique(),
  provider: text('provider').default('twilio'),
  phoneNumber: text('phone_number').notNull(),
  status: text('status').default('queued').notNull(),
  mode: text('mode').default('hold'), // hold | conversation
  durationSecs: integer('duration_secs'),
  holdDurationSecs: integer('hold_duration_secs'),
  conversationDurationSecs: integer('conversation_duration_secs'),
  recordingUrl: text('recording_url'),
  recordingPath: text('recording_path'),
  transcriptRaw: text('transcript_raw', { mode: 'json' }).$type<Array<{ role: string; text: string; timestamp?: string }>>().default([]),
  transcriptFormatted: text('transcript_formatted'),
  costTotalCents: integer('cost_total_cents').default(0),
  outcome: text('outcome').default('unknown'),
  humanAgentName: text('human_agent_name'),
  startedAt: text('started_at').default(sql`(datetime('now'))`).notNull(),
  endedAt: text('ended_at'),
  createdAt: text('created_at').default(sql`(datetime('now'))`).notNull(),
}, (table) => [
  index('calls_issue_id_idx').on(table.issueId),
  index('calls_call_sid_idx').on(table.callSid),
  index('calls_status_idx').on(table.status),
]);

// ─── Call Costs ────────────────────────────────────────────────────────────

export const callCosts = sqliteTable('call_costs', {
  id: text('id').primaryKey(),
  callId: text('call_id').notNull().references(() => calls.id, { onDelete: 'cascade' }),
  component: text('component').notNull(), // twilio | whisper | elevenlabs | openai
  durationSecs: integer('duration_secs'),
  unitCostMicros: integer('unit_cost_micros'), // cost per second in microcents
  totalCostCents: integer('total_cost_cents').default(0),
  metadata: text('metadata', { mode: 'json' }).$type<Record<string, unknown>>().default({}),
  createdAt: text('created_at').default(sql`(datetime('now'))`).notNull(),
}, (table) => [
  index('call_costs_call_id_idx').on(table.callId),
]);

// ─── Highlights ────────────────────────────────────────────────────────────

export const highlights = sqliteTable('highlights', {
  id: text('id').primaryKey(),
  callId: text('call_id').notNull().references(() => calls.id, { onDelete: 'cascade' }),
  category: text('category').notNull(),
  title: text('title').notNull(),
  summary: text('summary').notNull(),
  transcriptExcerpt: text('transcript_excerpt'),
  startTimeSecs: real('start_time_secs'),
  endTimeSecs: real('end_time_secs'),
  audioClipUrl: text('audio_clip_url'),
  audioClipPath: text('audio_clip_path'),
  confidence: real('confidence'),
  isActionable: integer('is_actionable', { mode: 'boolean' }).default(false),
  createdAt: text('created_at').default(sql`(datetime('now'))`).notNull(),
}, (table) => [
  index('highlights_call_id_idx').on(table.callId),
  index('highlights_category_idx').on(table.category),
]);

// ─── Issue Notes ───────────────────────────────────────────────────────────

export const issueNotes = sqliteTable('issue_notes', {
  id: text('id').primaryKey(),
  issueId: text('issue_id').notNull().references(() => issues.id, { onDelete: 'cascade' }),
  userId: text('user_id').references(() => users.id),
  content: text('content').notNull(),
  isSystemGenerated: integer('is_system_generated', { mode: 'boolean' }).default(false),
  createdAt: text('created_at').default(sql`(datetime('now'))`).notNull(),
}, (table) => [
  index('issue_notes_issue_id_idx').on(table.issueId),
]);

// ─── Types ─────────────────────────────────────────────────────────────────

export type User = typeof users.$inferSelect;
export type Issue = typeof issues.$inferSelect;
export type Call = typeof calls.$inferSelect;
export type CallCost = typeof callCosts.$inferSelect;
export type Highlight = typeof highlights.$inferSelect;
export type Company = typeof companies.$inferSelect;
export type IssueNote = typeof issueNotes.$inferSelect;

export type IssueStatus = typeof ISSUE_STATUSES[number];
export type CallStatus = typeof CALL_STATUSES[number];
export type CallOutcome = typeof CALL_OUTCOMES[number];
export type HighlightCategory = typeof HIGHLIGHT_CATEGORIES[number];
