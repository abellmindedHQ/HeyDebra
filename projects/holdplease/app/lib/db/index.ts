import Database from 'better-sqlite3';
import { drizzle } from 'drizzle-orm/better-sqlite3';
import * as schema from './schema';
import path from 'path';

// Use a DB file in the project root (shared with phone engine)
const DB_PATH = process.env.DATABASE_PATH || 
  path.join(process.cwd(), '..', 'data', 'holdplease.db');

const sqlite = new Database(DB_PATH);

// Enable WAL mode for better concurrent access (phone engine writes too)
sqlite.pragma('journal_mode = WAL');
sqlite.pragma('foreign_keys = ON');

export const db = drizzle(sqlite, { schema });

export type DB = typeof db;
