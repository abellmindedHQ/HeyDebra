import { NextRequest, NextResponse } from 'next/server';
import { eq } from 'drizzle-orm';
import { db } from '@/lib/db';
import { calls, issues } from '@/lib/db/schema';

// Internal endpoint — phone engine calls this when a call finishes
// Protected by INTERNAL_API_KEY env var
export async function POST(
  req: NextRequest,
  { params }: { params: Promise<{ callSid: string }> }
) {
  const { callSid } = await params;
  
  // Verify internal API key
  const apiKey = req.headers.get('x-internal-key');
  if (process.env.INTERNAL_API_KEY && apiKey !== process.env.INTERNAL_API_KEY) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }
  
  try {
    const body = await req.json();
    const {
      callId,
      status = 'completed',
      outcome = 'unknown',
      durationSecs,
      holdDurationSecs,
      conversationDurationSecs,
      transcriptRaw,
      transcriptFormatted,
      humanAgentName,
      costTotalCents,
      recordingPath,
      recordingUrl,
    } = body;
    
    // Find call by callSid OR callId
    const call = callSid !== 'unknown'
      ? await db.query.calls.findFirst({ where: eq(calls.callSid, callSid) })
      : callId
        ? await db.query.calls.findFirst({ where: eq(calls.id, callId) })
        : null;
    
    if (!call) {
      return NextResponse.json({ error: 'Call not found' }, { status: 404 });
    }
    
    // Update call record
    await db.update(calls).set({
      status,
      outcome,
      durationSecs: durationSecs ?? null,
      holdDurationSecs: holdDurationSecs ?? null,
      conversationDurationSecs: conversationDurationSecs ?? null,
      transcriptRaw: transcriptRaw ?? [],
      transcriptFormatted: transcriptFormatted ?? null,
      humanAgentName: humanAgentName ?? null,
      costTotalCents: costTotalCents ?? 0,
      recordingPath: recordingPath ?? null,
      recordingUrl: recordingUrl ?? null,
      endedAt: new Date().toISOString(),
    }).where(eq(calls.id, call.id));
    
    // Update issue aggregates
    await db.update(issues).set({
      totalCalls: db.run(
        `UPDATE issues SET total_calls = total_calls + 1 WHERE id = '${call.issueId}'`
      ) as any,
      updatedAt: new Date().toISOString(),
    });
    
    // More surgical update for aggregates
    const updateSql = `
      UPDATE issues SET
        total_calls = total_calls + 1,
        total_cost_cents = total_cost_cents + ${costTotalCents ?? 0},
        total_duration_secs = total_duration_secs + ${durationSecs ?? 0},
        total_hold_secs = total_hold_secs + ${holdDurationSecs ?? 0},
        status = CASE 
          WHEN status = 'calling' THEN 'waiting_on_them'
          ELSE status
        END,
        updated_at = datetime('now')
      WHERE id = '${call.issueId}'
    `;
    
    // Use raw sqlite for the aggregate update
    const rawDb = (db as any).session?.client;
    if (rawDb) {
      rawDb.prepare(updateSql.replace(/\n\s+/g, ' ')).run();
    }
    
    return NextResponse.json({ success: true, callId: call.id });
  } catch (error) {
    console.error('Call complete webhook error:', error);
    return NextResponse.json({ error: 'Internal error' }, { status: 500 });
  }
}
