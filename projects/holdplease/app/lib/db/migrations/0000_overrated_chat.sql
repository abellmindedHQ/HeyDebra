CREATE TABLE `accounts` (
	`userId` text NOT NULL,
	`type` text NOT NULL,
	`provider` text NOT NULL,
	`providerAccountId` text NOT NULL,
	`refresh_token` text,
	`access_token` text,
	`expires_at` integer,
	`token_type` text,
	`scope` text,
	`id_token` text,
	`session_state` text,
	FOREIGN KEY (`userId`) REFERENCES `users`(`id`) ON UPDATE no action ON DELETE cascade
);
--> statement-breakpoint
CREATE TABLE `call_costs` (
	`id` text PRIMARY KEY NOT NULL,
	`call_id` text NOT NULL,
	`component` text NOT NULL,
	`duration_secs` integer,
	`unit_cost_micros` integer,
	`total_cost_cents` integer DEFAULT 0,
	`metadata` text DEFAULT '{}',
	`created_at` text DEFAULT (datetime('now')) NOT NULL,
	FOREIGN KEY (`call_id`) REFERENCES `calls`(`id`) ON UPDATE no action ON DELETE cascade
);
--> statement-breakpoint
CREATE INDEX `call_costs_call_id_idx` ON `call_costs` (`call_id`);--> statement-breakpoint
CREATE TABLE `calls` (
	`id` text PRIMARY KEY NOT NULL,
	`issue_id` text NOT NULL,
	`call_sid` text,
	`provider` text DEFAULT 'twilio',
	`phone_number` text NOT NULL,
	`status` text DEFAULT 'queued' NOT NULL,
	`mode` text DEFAULT 'hold',
	`duration_secs` integer,
	`hold_duration_secs` integer,
	`conversation_duration_secs` integer,
	`recording_url` text,
	`recording_path` text,
	`transcript_raw` text DEFAULT '[]',
	`transcript_formatted` text,
	`cost_total_cents` integer DEFAULT 0,
	`outcome` text DEFAULT 'unknown',
	`human_agent_name` text,
	`started_at` text DEFAULT (datetime('now')) NOT NULL,
	`ended_at` text,
	`created_at` text DEFAULT (datetime('now')) NOT NULL,
	FOREIGN KEY (`issue_id`) REFERENCES `issues`(`id`) ON UPDATE no action ON DELETE cascade
);
--> statement-breakpoint
CREATE UNIQUE INDEX `calls_call_sid_unique` ON `calls` (`call_sid`);--> statement-breakpoint
CREATE INDEX `calls_issue_id_idx` ON `calls` (`issue_id`);--> statement-breakpoint
CREATE INDEX `calls_call_sid_idx` ON `calls` (`call_sid`);--> statement-breakpoint
CREATE INDEX `calls_status_idx` ON `calls` (`status`);--> statement-breakpoint
CREATE TABLE `companies` (
	`id` text PRIMARY KEY NOT NULL,
	`name` text NOT NULL,
	`normalized_name` text NOT NULL,
	`main_phone` text,
	`departments` text DEFAULT '[]',
	`avg_hold_mins` real,
	`avg_resolution_calls` real,
	`success_rate` real,
	`ivr_tree` text DEFAULT '{}',
	`notes` text,
	`total_calls` integer DEFAULT 0,
	`total_issues` integer DEFAULT 0,
	`created_at` text DEFAULT (datetime('now')) NOT NULL,
	`updated_at` text DEFAULT (datetime('now')) NOT NULL
);
--> statement-breakpoint
CREATE UNIQUE INDEX `companies_normalized_name_unique` ON `companies` (`normalized_name`);--> statement-breakpoint
CREATE INDEX `companies_normalized_name_idx` ON `companies` (`normalized_name`);--> statement-breakpoint
CREATE TABLE `highlights` (
	`id` text PRIMARY KEY NOT NULL,
	`call_id` text NOT NULL,
	`category` text NOT NULL,
	`title` text NOT NULL,
	`summary` text NOT NULL,
	`transcript_excerpt` text,
	`start_time_secs` real,
	`end_time_secs` real,
	`audio_clip_url` text,
	`audio_clip_path` text,
	`confidence` real,
	`is_actionable` integer DEFAULT false,
	`created_at` text DEFAULT (datetime('now')) NOT NULL,
	FOREIGN KEY (`call_id`) REFERENCES `calls`(`id`) ON UPDATE no action ON DELETE cascade
);
--> statement-breakpoint
CREATE INDEX `highlights_call_id_idx` ON `highlights` (`call_id`);--> statement-breakpoint
CREATE INDEX `highlights_category_idx` ON `highlights` (`category`);--> statement-breakpoint
CREATE TABLE `issue_notes` (
	`id` text PRIMARY KEY NOT NULL,
	`issue_id` text NOT NULL,
	`user_id` text,
	`content` text NOT NULL,
	`is_system_generated` integer DEFAULT false,
	`created_at` text DEFAULT (datetime('now')) NOT NULL,
	FOREIGN KEY (`issue_id`) REFERENCES `issues`(`id`) ON UPDATE no action ON DELETE cascade,
	FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON UPDATE no action ON DELETE no action
);
--> statement-breakpoint
CREATE INDEX `issue_notes_issue_id_idx` ON `issue_notes` (`issue_id`);--> statement-breakpoint
CREATE TABLE `issues` (
	`id` text PRIMARY KEY NOT NULL,
	`user_id` text NOT NULL,
	`title` text NOT NULL,
	`description` text,
	`company` text NOT NULL,
	`company_phone` text,
	`department` text,
	`status` text DEFAULT 'new' NOT NULL,
	`priority` integer DEFAULT 3,
	`desired_outcome` text,
	`reference_numbers` text DEFAULT '[]',
	`account_info` text DEFAULT '{}',
	`ai_summary` text,
	`resolution_notes` text,
	`total_calls` integer DEFAULT 0,
	`total_cost_cents` integer DEFAULT 0,
	`total_duration_secs` integer DEFAULT 0,
	`total_hold_secs` integer DEFAULT 0,
	`outcome_type` text,
	`outcome_value_cents` integer DEFAULT 0,
	`outcome_description` text,
	`created_at` text DEFAULT (datetime('now')) NOT NULL,
	`updated_at` text DEFAULT (datetime('now')) NOT NULL,
	`resolved_at` text,
	`closed_at` text,
	FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON UPDATE no action ON DELETE cascade
);
--> statement-breakpoint
CREATE INDEX `issues_user_id_idx` ON `issues` (`user_id`);--> statement-breakpoint
CREATE INDEX `issues_status_idx` ON `issues` (`status`);--> statement-breakpoint
CREATE INDEX `issues_company_idx` ON `issues` (`company`);--> statement-breakpoint
CREATE TABLE `sessions` (
	`sessionToken` text PRIMARY KEY NOT NULL,
	`userId` text NOT NULL,
	`expires` text NOT NULL,
	FOREIGN KEY (`userId`) REFERENCES `users`(`id`) ON UPDATE no action ON DELETE cascade
);
--> statement-breakpoint
CREATE TABLE `users` (
	`id` text PRIMARY KEY NOT NULL,
	`email` text NOT NULL,
	`name` text,
	`image` text,
	`google_id` text,
	`password_hash` text,
	`plan` text DEFAULT 'free',
	`created_at` text DEFAULT (datetime('now')) NOT NULL,
	`updated_at` text DEFAULT (datetime('now')) NOT NULL
);
--> statement-breakpoint
CREATE UNIQUE INDEX `users_email_unique` ON `users` (`email`);--> statement-breakpoint
CREATE UNIQUE INDEX `users_google_id_unique` ON `users` (`google_id`);--> statement-breakpoint
CREATE INDEX `users_email_idx` ON `users` (`email`);--> statement-breakpoint
CREATE INDEX `users_google_id_idx` ON `users` (`google_id`);--> statement-breakpoint
CREATE TABLE `verificationTokens` (
	`identifier` text NOT NULL,
	`token` text NOT NULL,
	`expires` text NOT NULL
);
