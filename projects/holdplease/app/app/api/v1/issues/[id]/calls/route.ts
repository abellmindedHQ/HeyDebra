import { NextRequest, NextResponse } from 'next/server';
import { eq, and, desc } from 'drizzle-orm';
import { auth } from '@/lib/auth';
import { db } from '@/lib/db';
import { issues, calls } from '@/lib/db/schema';
import { generateId } from '@/lib/utils/format';

export async function GET(
  req: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const session = await auth();
  if (!session?.user) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }
  
  const { id } = await params;
  
  const issue = await db.query.issues.findFirst({
    where: and(eq(issues.id, id), eq(issues.userId, session.user.id)),
  });
  
  if (!issue) {
    return NextResponse.json({ error: 'Not found' }, { status: 404 });
  }
  
  const issueCalls = await db.query.calls.findMany({
    where: eq(calls.issueId, id),
    orderBy: [desc(calls.startedAt)],
  });
  
  return NextResponse.json({ items: issueCalls });
}

export async function POST(
  req: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const session = await auth();
  if (!session?.user) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }
  
  const { id } = await params;
  
  const issue = await db.query.issues.findFirst({
    where: and(eq(issues.id, id), eq(issues.userId, session.user.id)),
  });
  
  if (!issue) {
    return NextResponse.json({ error: 'Not found' }, { status: 404 });
  }
  
  const body = await req.json();
  const { task, phoneNumber, callback } = body;
  
  const phone = phoneNumber || issue.companyPhone;
  if (!phone) {
    return NextResponse.json(
      { error: 'phone number required — either in the issue or in the request body' },
      { status: 400 }
    );
  }
  
  if (!task) {
    return NextResponse.json({ error: 'task is required' }, { status: 400 });
  }
  
  // Create a call record in DB
  const callId = generateId('cal');
  await db.insert(calls).values({
    id: callId,
    issueId: id,
    phoneNumber: phone,
    status: 'queued',
    transcriptRaw: [],
  });
  
  // Update issue status to 'calling'
  await db.update(issues).set({
    status: 'calling',
    updatedAt: new Date().toISOString(),
  }).where(eq(issues.id, id));
  
  // Forward to phone engine
  const engineUrl = process.env.PHONE_ENGINE_URL || 'http://localhost:3978';
  
  try {
    const engineRes = await fetch(`${engineUrl}/api/calls`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        callId,
        issueId: id,
        phoneNumber: phone,
        task,
        callback: callback || process.env.ALERT_PHONE_NUMBER,
        webhookUrl: `${process.env.NEXTAUTH_URL || 'http://localhost:3000'}/api/internal/calls`,
      }),
    });
    
    if (engineRes.ok) {
      const engineData = await engineRes.json();
      // Update call with Twilio SID if engine returned it
      if (engineData.callSid) {
        await db.update(calls).set({
          callSid: engineData.callSid,
          status: 'connecting',
        }).where(eq(calls.id, callId));
      }
    }
  } catch (err) {
    // Engine may not be running in dev — call is still queued
    console.warn('Phone engine not reachable:', err);
  }
  
  const created = await db.query.calls.findFirst({
    where: eq(calls.id, callId),
  });
  
  return NextResponse.json(created, { status: 201 });
}
