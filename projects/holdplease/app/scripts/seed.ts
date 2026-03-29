#!/usr/bin/env npx tsx
/**
 * Seed database from existing data/calls.json
 * Usage: npx tsx scripts/seed.ts
 */

import Database from 'better-sqlite3';
import { drizzle } from 'drizzle-orm/better-sqlite3';
import { migrate } from 'drizzle-orm/better-sqlite3/migrator';
import { eq } from 'drizzle-orm';
import path from 'path';
import fs from 'fs';
import * as schema from '../lib/db/schema';
import bcrypt from 'bcryptjs';

const DB_PATH = process.env.DATABASE_PATH ||
  path.join(__dirname, '..', '..', 'data', 'holdplease.db');

const CALLS_JSON_PATH = path.join(__dirname, '..', '..', 'data', 'calls.json');

console.log(`🌱 Seeding database: ${DB_PATH}`);
console.log(`📂 Reading calls from: ${CALLS_JSON_PATH}`);

const sqlite = new Database(DB_PATH);
sqlite.pragma('journal_mode = WAL');
sqlite.pragma('foreign_keys = ON');

const db = drizzle(sqlite, { schema });

// Run migrations first
migrate(db, {
  migrationsFolder: path.join(__dirname, '..', 'lib', 'db', 'migrations'),
});
console.log('✅ Migrations done');

async function seed() {
  // Create default admin user (Alex)
  const adminEmail = process.env.ADMIN_EMAIL || 'alexander.o.abell@gmail.com';
  const adminPassword = process.env.ADMIN_PASSWORD || 'holdplease2026';
  
  let adminUser = await db.query.users.findFirst({
    where: eq(schema.users.email, adminEmail),
  });
  
  if (!adminUser) {
    const passwordHash = await bcrypt.hash(adminPassword, 12);
    const userId = `usr_${Date.now()}_seed`;
    
    await db.insert(schema.users).values({
      id: userId,
      email: adminEmail,
      name: 'Alex Abell',
      passwordHash,
    });
    
    adminUser = await db.query.users.findFirst({
      where: eq(schema.users.email, adminEmail),
    });
    
    console.log(`✅ Created admin user: ${adminEmail}`);
  } else {
    console.log(`ℹ️  Admin user already exists: ${adminEmail}`);
  }
  
  // Read existing calls.json
  if (!fs.existsSync(CALLS_JSON_PATH)) {
    console.log('ℹ️  No calls.json found, skipping call migration');
    return;
  }
  
  const v1Calls = JSON.parse(fs.readFileSync(CALLS_JSON_PATH, 'utf-8'));
  console.log(`📞 Found ${v1Calls.length} calls to migrate`);
  
  let created = 0;
  let skipped = 0;
  
  for (const v1Call of v1Calls) {
    // Check if call already exists
    if (v1Call.callSid) {
      const existing = await db.query.calls.findFirst({
        where: eq(schema.calls.callSid, v1Call.callSid),
      });
      if (existing) {
        skipped++;
        continue;
      }
    }
    
    // Create issue for this call
    const issueId = `iss_${Date.now()}_${Math.random().toString(36).slice(2, 7)}`;
    const callId = `cal_${Date.now()}_${Math.random().toString(36).slice(2, 7)}`;
    
    const isResolved = v1Call.status === 'completed' && v1Call.mode === 'conversation';
    
    await db.insert(schema.issues).values({
      id: issueId,
      userId: adminUser!.id,
      title: `${v1Call.company} — ${(v1Call.task || '').substring(0, 80)}`,
      company: v1Call.company || 'Unknown',
      companyPhone: v1Call.phoneNumber || null,
      description: v1Call.task || null,
      status: isResolved ? 'resolved' : 'closed',
      totalCalls: 1,
      resolvedAt: isResolved ? (v1Call.endedAt || v1Call.startedAt) : null,
    });
    
    await db.insert(schema.calls).values({
      id: callId,
      issueId,
      callSid: v1Call.callSid || null,
      phoneNumber: v1Call.phoneNumber || '',
      status: v1Call.status === 'completed' ? 'completed' : 'failed',
      mode: v1Call.mode || 'hold',
      transcriptRaw: v1Call.transcript || [],
      outcome: isResolved ? 'resolved' : 'unknown',
      startedAt: v1Call.startedAt || new Date().toISOString(),
    });
    
    created++;
  }
  
  console.log(`✅ Migration complete: ${created} created, ${skipped} skipped`);
}

seed()
  .then(() => {
    console.log('🎉 Seed done!');
    sqlite.close();
  })
  .catch((err) => {
    console.error('❌ Seed error:', err);
    sqlite.close();
    process.exit(1);
  });
