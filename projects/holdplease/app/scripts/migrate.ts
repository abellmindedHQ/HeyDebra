#!/usr/bin/env npx tsx
/**
 * Run database migrations
 * Usage: npx tsx scripts/migrate.ts
 */

import Database from 'better-sqlite3';
import { drizzle } from 'drizzle-orm/better-sqlite3';
import { migrate } from 'drizzle-orm/better-sqlite3/migrator';
import path from 'path';

const DB_PATH = process.env.DATABASE_PATH ||
  path.join(__dirname, '..', '..', 'data', 'holdplease.db');

console.log(`📦 Running migrations on: ${DB_PATH}`);

const sqlite = new Database(DB_PATH);
sqlite.pragma('journal_mode = WAL');
sqlite.pragma('foreign_keys = ON');

const db = drizzle(sqlite);

migrate(db, {
  migrationsFolder: path.join(__dirname, '..', 'lib', 'db', 'migrations'),
});

console.log('✅ Migrations complete!');
sqlite.close();
