import { auth } from '@/lib/auth';
import { db } from '@/lib/db';
import { issues } from '@/lib/db/schema';
import { eq, desc } from 'drizzle-orm';
import { StatusBadge } from '@/components/issues/status-badge';
import { Card } from '@/components/ui/card';
import { formatCents, formatRelativeDate, formatPhone } from '@/lib/utils/format';
import { ArrowRight, PhoneCall } from 'lucide-react';
import Link from 'next/link';

export default async function IssuesPage() {
  const session = await auth();
  
  const allIssues = await db.query.issues.findMany({
    where: eq(issues.userId, session!.user.id),
    orderBy: [desc(issues.updatedAt)],
  });
  
  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Issues</h1>
          <p className="text-sm text-slate-400 mt-1">{allIssues.length} total issues</p>
        </div>
        <Link
          href="/dashboard/issues/new"
          className="inline-flex items-center gap-2 rounded-lg bg-amber-500 px-4 py-2 text-sm font-semibold text-black hover:bg-amber-400 transition-colors"
        >
          + New Issue
        </Link>
      </div>
      
      <Card>
        {allIssues.length === 0 ? (
          <div className="px-6 py-16 text-center">
            <PhoneCall className="h-10 w-10 text-slate-600 mx-auto mb-4" />
            <p className="text-lg font-semibold text-white mb-2">No issues yet</p>
            <p className="text-sm text-slate-400 mb-6 max-w-sm mx-auto">
              Create an issue for each customer service problem you need help with.
              AI will call, wait on hold, and negotiate on your behalf.
            </p>
            <Link
              href="/dashboard/issues/new"
              className="inline-flex items-center gap-2 rounded-lg bg-amber-500 px-4 py-2 text-sm font-semibold text-black hover:bg-amber-400 transition-colors"
            >
              Create your first issue
            </Link>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-slate-800">
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
                    Issue
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
                    Company
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
                    Calls
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
                    Cost
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
                    Updated
                  </th>
                  <th className="px-6 py-3" />
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/50">
                {allIssues.map((issue) => (
                  <tr
                    key={issue.id}
                    className="hover:bg-slate-800/20 transition-colors"
                  >
                    <td className="px-6 py-4">
                      <div>
                        <p className="text-sm font-medium text-white truncate max-w-xs">
                          {issue.title}
                        </p>
                        {issue.companyPhone && (
                          <p className="text-xs text-slate-500 font-mono mt-0.5">
                            {formatPhone(issue.companyPhone)}
                          </p>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <StatusBadge status={issue.status} />
                    </td>
                    <td className="px-6 py-4 text-sm text-slate-300">
                      {issue.company}
                    </td>
                    <td className="px-6 py-4 text-sm text-slate-300">
                      {issue.totalCalls ?? 0}
                    </td>
                    <td className="px-6 py-4 text-sm text-slate-300">
                      {formatCents(issue.totalCostCents ?? 0)}
                    </td>
                    <td className="px-6 py-4 text-xs text-slate-500">
                      {formatRelativeDate(issue.updatedAt)}
                    </td>
                    <td className="px-6 py-4">
                      <Link
                        href={`/dashboard/issues/${issue.id}`}
                        className="text-slate-500 hover:text-amber-400 transition-colors"
                      >
                        <ArrowRight className="h-4 w-4" />
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>
    </div>
  );
}
