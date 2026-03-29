import { NextRequest, NextResponse } from 'next/server';
import { eq, and } from 'drizzle-orm';
import { auth } from '@/lib/auth';
import { db } from '@/lib/db';
import { issues } from '@/lib/db/schema';

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
  
  return NextResponse.json(issue);
}

export async function PATCH(
  req: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const session = await auth();
  if (!session?.user) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }
  
  const { id } = await params;
  
  const existing = await db.query.issues.findFirst({
    where: and(eq(issues.id, id), eq(issues.userId, session.user.id)),
  });
  
  if (!existing) {
    return NextResponse.json({ error: 'Not found' }, { status: 404 });
  }
  
  const body = await req.json();
  const allowedFields = [
    'title', 'status', 'description', 'desiredOutcome', 'company',
    'companyPhone', 'department', 'referenceNumbers', 'priority',
    'resolutionNotes', 'outcomeType', 'outcomeValueCents', 'outcomeDescription',
  ];
  
  const updates: Record<string, unknown> = {};
  for (const field of allowedFields) {
    if (body[field] !== undefined) {
      updates[field] = body[field];
    }
  }
  
  // Handle special status transitions
  if (body.status === 'resolved' && !existing.resolvedAt) {
    updates.resolvedAt = new Date().toISOString();
  }
  if (body.status === 'closed' && !existing.closedAt) {
    updates.closedAt = new Date().toISOString();
  }
  
  updates.updatedAt = new Date().toISOString();
  
  await db.update(issues).set(updates).where(eq(issues.id, id));
  
  const updated = await db.query.issues.findFirst({
    where: eq(issues.id, id),
  });
  
  return NextResponse.json(updated);
}

export async function DELETE(
  req: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const session = await auth();
  if (!session?.user) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }
  
  const { id } = await params;
  
  const existing = await db.query.issues.findFirst({
    where: and(eq(issues.id, id), eq(issues.userId, session.user.id)),
  });
  
  if (!existing) {
    return NextResponse.json({ error: 'Not found' }, { status: 404 });
  }
  
  // Soft delete — set status to closed
  await db.update(issues).set({
    status: 'closed',
    closedAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  }).where(eq(issues.id, id));
  
  return NextResponse.json({ success: true });
}
