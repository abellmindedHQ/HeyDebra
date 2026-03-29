import { NextRequest, NextResponse } from 'next/server';
import { eq } from 'drizzle-orm';
import { auth } from '@/lib/auth';
import { db } from '@/lib/db';
import { calls, issues } from '@/lib/db/schema';

export async function GET(
  req: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const session = await auth();
  if (!session?.user) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }
  
  const { id } = await params;
  
  const call = await db.query.calls.findFirst({
    where: eq(calls.id, id),
  });
  
  if (!call) {
    return NextResponse.json({ error: 'Not found' }, { status: 404 });
  }
  
  // Verify user owns the issue
  const issue = await db.query.issues.findFirst({
    where: eq(issues.id, call.issueId),
  });
  
  if (!issue || issue.userId !== session.user.id) {
    return NextResponse.json({ error: 'Not found' }, { status: 404 });
  }
  
  return NextResponse.json(call);
}
