import type { Config } from 'drizzle-kit';
import path from 'path';

const DB_PATH = process.env.DATABASE_PATH || 
  path.join(__dirname, '..', 'data', 'holdplease.db');

export default {
  schema: './lib/db/schema.ts',
  out: './lib/db/migrations',
  dialect: 'sqlite',
  dbCredentials: {
    url: DB_PATH,
  },
} satisfies Config;
