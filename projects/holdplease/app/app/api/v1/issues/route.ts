import { NextRequest, NextResponse } from 'next/server';
import { eq, desc, and, like, sql } from 'drizzle-orm';
import { auth } from '@/lib/auth';
import { db } from '@/lib/db';
import { issues } from '@/lib/db/schema';
import { generateId } from '@/lib/utils/format';

export async function GET(req: NextRequest) {
  const session = await auth();
  if (!session?.user) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }
  
  const { searchParams } = req.nextUrl;
  const status = searchParams.get('status');
  const company = searchParams.get('company');
  const page = parseInt(searchParams.get('page') ?? '1');
  const limit = Math.min(parseInt(searchParams.get('limit') ?? '20'), 100);
  const offset = (page - 1) * limit;
  
  const conditions = [eq(issues.userId, session.user.id)];
  if (status) conditions.push(eq(issues.status, status));
  if (company) conditions.push(like(issues.company, `%${company}%`));
  
  const results = await db.query.issues.findMany({
    where: and(...conditions),
    orderBy: [desc(issues.updatedAt)],
    limit,
    offset,
  });
  
  const total = await db
    .select({ count: sql<number>`count(*)` })
    .from(issues)
    .where(and(...conditions));
  
  return NextResponse.json({
    items: results,
    total: total[0].count,
    page,
    limit,
    hasMore: offset + results.length < total[0].count,
  });
}

export async function POST(req: NextRequest) {
  const session = await auth();
  if (!session?.user) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }
  
  try {
    const body = await req.json();
    const { title, company, companyPhone, department, description, desiredOutcome, referenceNumbers, priority } = body;
    
    if (!title || !company) {
      return NextResponse.json({ error: 'title and company are required' }, { status: 400 });
    }
    
    const id = generateId('iss');
    
    await db.insert(issues).values({
      id,
      userId: session.user.id,
      title,
      company,
      companyPhone: companyPhone || null,
      department: department || null,
      description: description || null,
      desiredOutcome: desiredOutcome || null,
      referenceNumbers: referenceNumbers || [],
      priority: priority ?? 3,
      status: 'new',
    });
    
    const created = await db.query.issues.findFirst({
      where: eq(issues.id, id),
    });
    
    return NextResponse.json(created, { status: 201 });
  } catch (error) {
    console.error('Create issue error:', error);
    return NextResponse.json({ error: 'Failed to create issue' }, { status: 500 });
  }
}
