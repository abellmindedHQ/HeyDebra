import { NextRequest, NextResponse } from 'next/server';
import { eq, sum, count, sql } from 'drizzle-orm';
import { auth } from '@/lib/auth';
import { db } from '@/lib/db';
import { issues } from '@/lib/db/schema';

export async function GET(req: NextRequest) {
  const session = await auth();
  if (!session?.user) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }
  
  const userId = session.user.id;
  
  const stats = await db
    .select({
      totalIssues: count(issues.id),
      resolvedIssues: sql<number>`count(case when ${issues.status} = 'resolved' then 1 end)`,
      totalCalls: sum(issues.totalCalls),
      totalCostCents: sum(issues.totalCostCents),
      totalHoldSecs: sum(issues.totalHoldSecs),
      totalDurationSecs: sum(issues.totalDurationSecs),
      totalValueCents: sum(issues.outcomeValueCents),
    })
    .from(issues)
    .where(eq(issues.userId, userId));
  
  const s = stats[0];
  const totalCost = Number(s?.totalCostCents ?? 0);
  const totalValue = Number(s?.totalValueCents ?? 0);
  const resolvedIssues = Number(s?.resolvedIssues ?? 0);
  const totalIssues = Number(s?.totalIssues ?? 0);
  const totalCalls = Number(s?.totalCalls ?? 0);
  const totalHoldSecs = Number(s?.totalHoldSecs ?? 0);
  
  const avgCostPerResolution = resolvedIssues > 0
    ? Math.round(totalCost / resolvedIssues)
    : 0;
    
  const roi = totalCost > 0
    ? Math.round(((totalValue - totalCost) / totalCost) * 100)
    : 0;
  
  return NextResponse.json({
    totalIssues,
    resolvedIssues,
    totalCalls,
    totalHoldSecs,
    totalHoldMins: Math.round(totalHoldSecs / 60),
    totalCostCents: totalCost,
    totalValueCents: totalValue,
    avgCostPerResolutionCents: avgCostPerResolution,
    roi,
    resolutionRate: totalIssues > 0
      ? Math.round((resolvedIssues / totalIssues) * 100)
      : 0,
  });
}
