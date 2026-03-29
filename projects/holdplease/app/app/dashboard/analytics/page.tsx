import { auth } from '@/lib/auth';
import { db } from '@/lib/db';
import { issues, calls, callCosts } from '@/lib/db/schema';
import { eq, sum, count, sql } from 'drizzle-orm';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { formatCents, formatDuration } from '@/lib/utils/format';
import { BarChart2, Clock, DollarSign, TrendingUp, Phone, CheckCircle } from 'lucide-react';

export default async function AnalyticsPage() {
  const session = await auth();
  const userId = session!.user.id;
  
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
  const totalHoldSecs = Number(s?.totalHoldSecs ?? 0);
  const resolvedIssues = Number(s?.resolvedIssues ?? 0);
  const totalIssues = Number(s?.totalIssues ?? 0);
  const totalCalls = Number(s?.totalCalls ?? 0);
  
  const resolutionRate = totalIssues > 0
    ? Math.round((resolvedIssues / totalIssues) * 100)
    : 0;
  
  const avgCostPerResolution = resolvedIssues > 0
    ? Math.round(totalCost / resolvedIssues)
    : 0;
    
  const roi = totalCost > 0
    ? Math.round(((totalValue - totalCost) / totalCost) * 100)
    : 0;
    
  const holdHours = Math.round(totalHoldSecs / 3600 * 10) / 10;
  
  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Analytics</h1>
        <p className="text-sm text-slate-400 mt-1">Your HoldPlease ROI breakdown</p>
      </div>
      
      {/* Key Metrics */}
      <div className="grid grid-cols-2 lg:grid-cols-3 gap-4">
        {[
          {
            label: 'Total Issues',
            value: String(totalIssues),
            sub: `${resolvedIssues} resolved`,
            icon: <Phone className="h-5 w-5 text-blue-400" />,
          },
          {
            label: 'Resolution Rate',
            value: `${resolutionRate}%`,
            sub: `${totalCalls} total calls`,
            icon: <CheckCircle className="h-5 w-5 text-green-400" />,
          },
          {
            label: 'Hold Time Saved',
            value: `${holdHours}h`,
            sub: formatDuration(totalHoldSecs),
            icon: <Clock className="h-5 w-5 text-amber-400" />,
          },
          {
            label: 'Total AI Cost',
            value: formatCents(totalCost),
            sub: avgCostPerResolution > 0 ? `${formatCents(avgCostPerResolution)} per resolution` : 'No resolutions yet',
            icon: <DollarSign className="h-5 w-5 text-slate-400" />,
          },
          {
            label: 'Value Recovered',
            value: formatCents(totalValue),
            sub: 'From resolved issues',
            icon: <TrendingUp className="h-5 w-5 text-emerald-400" />,
          },
          {
            label: 'Net ROI',
            value: roi > 0 ? `${roi}%` : 'N/A',
            sub: totalValue > 0
              ? `${formatCents(totalValue - totalCost)} net gain`
              : 'Track outcomes to unlock',
            icon: <BarChart2 className="h-5 w-5 text-purple-400" />,
          },
        ].map((metric) => (
          <Card key={metric.label}>
            <CardContent className="pt-5 pb-5">
              <div className="flex items-start justify-between mb-3">
                <p className="text-xs text-slate-400 font-medium">{metric.label}</p>
                {metric.icon}
              </div>
              <p className="text-2xl font-bold text-white">{metric.value}</p>
              <p className="text-xs text-slate-500 mt-1">{metric.sub}</p>
            </CardContent>
          </Card>
        ))}
      </div>
      
      {/* Empty State */}
      {totalIssues === 0 && (
        <Card>
          <CardContent className="py-16 text-center">
            <BarChart2 className="h-10 w-10 text-slate-600 mx-auto mb-4" />
            <p className="text-lg font-semibold text-white mb-2">No data yet</p>
            <p className="text-sm text-slate-400 max-w-sm mx-auto">
              Create issues and let AI make calls to start seeing your ROI analytics here.
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
