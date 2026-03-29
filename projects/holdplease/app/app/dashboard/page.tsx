import { auth } from '@/lib/auth';
import { db } from '@/lib/db';
import { issues, calls, callCosts } from '@/lib/db/schema';
import { eq, count, sum, sql } from 'drizzle-orm';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { formatCents, formatDuration } from '@/lib/utils/format';
import { StatusBadge } from '@/components/issues/status-badge';
import { Clock, PhoneCall, DollarSign, TrendingUp, ArrowRight } from 'lucide-react';
import Link from 'next/link';

async function getDashboardData(userId: string) {
  const userIssues = await db.query.issues.findMany({
    where: eq(issues.userId, userId),
    orderBy: (t, { desc }) => [desc(t.updatedAt)],
    limit: 5,
  });
  
  const stats = await db
    .select({
      totalIssues: count(issues.id),
      resolvedIssues: sql<number>`count(case when ${issues.status} = 'resolved' then 1 end)`,
      totalCalls: sum(issues.totalCalls),
      totalCostCents: sum(issues.totalCostCents),
      totalHoldSecs: sum(issues.totalHoldSecs),
      totalValueCents: sum(issues.outcomeValueCents),
    })
    .from(issues)
    .where(eq(issues.userId, userId));
  
  return { issues: userIssues, stats: stats[0] };
}

export default async function DashboardPage() {
  const session = await auth();
  const { issues: recentIssues, stats } = await getDashboardData(session!.user.id);
  
  const totalHoldHours = Math.round(Number(stats.totalHoldSecs ?? 0) / 3600 * 10) / 10;
  const totalCost = Number(stats.totalCostCents ?? 0);
  const totalValue = Number(stats.totalValueCents ?? 0);
  const roi = totalCost > 0 ? Math.round((totalValue - totalCost) / totalCost * 100) : 0;
  
  const metricsCards = [
    {
      label: 'Total Issues',
      value: String(stats.totalIssues ?? 0),
      subtext: `${stats.resolvedIssues ?? 0} resolved`,
      icon: <PhoneCall className="h-5 w-5 text-amber-400" />,
    },
    {
      label: 'Hold Time Saved',
      value: `${totalHoldHours}h`,
      subtext: `${stats.totalCalls ?? 0} calls made`,
      icon: <Clock className="h-5 w-5 text-blue-400" />,
    },
    {
      label: 'Total Cost',
      value: formatCents(totalCost),
      subtext: 'AI phone time',
      icon: <DollarSign className="h-5 w-5 text-green-400" />,
    },
    {
      label: 'Value Recovered',
      value: formatCents(totalValue),
      subtext: roi > 0 ? `${roi}% ROI` : 'Track outcomes to see ROI',
      icon: <TrendingUp className="h-5 w-5 text-purple-400" />,
    },
  ];
  
  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Dashboard</h1>
          <p className="text-sm text-slate-400 mt-1">
            Welcome back, {session?.user?.name?.split(' ')[0] ?? 'there'}
          </p>
        </div>
        <Link
          href="/dashboard/issues/new"
          className="inline-flex items-center gap-2 rounded-lg bg-amber-500 px-4 py-2 text-sm font-semibold text-black hover:bg-amber-400 transition-colors"
        >
          + New Issue
        </Link>
      </div>
      
      {/* Stats Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {metricsCards.map((card) => (
          <Card key={card.label}>
            <CardContent className="pt-5 pb-5">
              <div className="flex items-start justify-between mb-3">
                <p className="text-xs text-slate-400 font-medium">{card.label}</p>
                {card.icon}
              </div>
              <p className="text-2xl font-bold text-white">{card.value}</p>
              <p className="text-xs text-slate-500 mt-1">{card.subtext}</p>
            </CardContent>
          </Card>
        ))}
      </div>
      
      {/* Recent Issues */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Recent Issues</CardTitle>
            <Link
              href="/dashboard/issues"
              className="flex items-center gap-1 text-xs text-amber-400 hover:text-amber-300"
            >
              View all <ArrowRight className="h-3 w-3" />
            </Link>
          </div>
        </CardHeader>
        <div className="divide-y divide-slate-800">
          {recentIssues.length === 0 ? (
            <div className="px-6 py-10 text-center">
              <PhoneCall className="h-8 w-8 text-slate-600 mx-auto mb-3" />
              <p className="text-slate-400 font-medium mb-1">No issues yet</p>
              <p className="text-sm text-slate-500 mb-4">
                Create your first issue to let AI handle a customer service call.
              </p>
              <Link
                href="/dashboard/issues/new"
                className="inline-flex items-center gap-2 rounded-lg bg-amber-500 px-4 py-2 text-sm font-semibold text-black hover:bg-amber-400 transition-colors"
              >
                Create issue
              </Link>
            </div>
          ) : (
            recentIssues.map((issue) => (
              <Link
                key={issue.id}
                href={`/dashboard/issues/${issue.id}`}
                className="flex items-center justify-between px-6 py-4 hover:bg-slate-800/30 transition-colors"
              >
                <div className="flex items-center gap-3 min-w-0">
                  <StatusBadge status={issue.status} />
                  <div className="min-w-0">
                    <p className="text-sm font-medium text-white truncate">{issue.title}</p>
                    <p className="text-xs text-slate-500 truncate">{issue.company}</p>
                  </div>
                </div>
                <div className="flex items-center gap-4 text-xs text-slate-500 shrink-0 ml-4">
                  <span>{issue.totalCalls} calls</span>
                  <span>{formatCents(issue.totalCostCents ?? 0)}</span>
                  <ArrowRight className="h-3 w-3 text-slate-600" />
                </div>
              </Link>
            ))
          )}
        </div>
      </Card>
    </div>
  );
}
