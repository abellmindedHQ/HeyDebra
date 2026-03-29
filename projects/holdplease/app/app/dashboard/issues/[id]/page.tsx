import { notFound, redirect } from 'next/navigation';
import { auth } from '@/lib/auth';
import { db } from '@/lib/db';
import { issues, calls } from '@/lib/db/schema';
import { eq, and, desc } from 'drizzle-orm';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { StatusBadge } from '@/components/issues/status-badge';
import { Button } from '@/components/ui/button';
import {
  formatCents,
  formatDuration,
  formatPhone,
  formatRelativeDate,
} from '@/lib/utils/format';
import {
  ArrowLeft,
  Phone,
  Clock,
  DollarSign,
  FileText,
  PhoneCall,
} from 'lucide-react';
import Link from 'next/link';

const ISSUE_STATUS_PIPELINE = [
  'new',
  'researching',
  'calling',
  'waiting_on_them',
  'waiting_on_me',
  'resolved',
];

export default async function IssueDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const session = await auth();
  
  const issue = await db.query.issues.findFirst({
    where: and(eq(issues.id, id), eq(issues.userId, session!.user.id)),
  });
  
  if (!issue) notFound();
  
  const issueCalls = await db.query.calls.findMany({
    where: eq(calls.issueId, id),
    orderBy: [desc(calls.startedAt)],
  });
  
  const currentStepIndex = ISSUE_STATUS_PIPELINE.indexOf(issue.status);
  
  return (
    <div className="p-6 space-y-6 max-w-4xl">
      {/* Back + Header */}
      <div>
        <Link
          href="/dashboard/issues"
          className="inline-flex items-center gap-1.5 text-sm text-slate-400 hover:text-white transition-colors mb-4"
        >
          <ArrowLeft className="h-3.5 w-3.5" />
          All Issues
        </Link>
        
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-3 mb-2">
              <StatusBadge status={issue.status} />
              <span className="text-xs text-slate-500">{issue.company}</span>
            </div>
            <h1 className="text-2xl font-bold text-white">{issue.title}</h1>
            {issue.description && (
              <p className="text-sm text-slate-400 mt-2 leading-relaxed">
                {issue.description}
              </p>
            )}
          </div>
          <Link
            href={`/dashboard/issues/${id}/call`}
            className="inline-flex items-center gap-2 rounded-lg bg-amber-500 px-4 py-2 text-sm font-semibold text-black hover:bg-amber-400 transition-colors shrink-0"
          >
            <Phone className="h-4 w-4" />
            Start Call
          </Link>
        </div>
      </div>
      
      {/* Status Pipeline */}
      {issue.status !== 'closed' && (
        <Card>
          <CardContent className="py-5">
            <div className="flex items-center">
              {ISSUE_STATUS_PIPELINE.map((step, i) => {
                const isCompleted = i < currentStepIndex;
                const isCurrent = i === currentStepIndex;
                const labels: Record<string, string> = {
                  new: 'New',
                  researching: 'Research',
                  calling: 'Calling',
                  waiting_on_them: 'Waiting',
                  waiting_on_me: 'Your Move',
                  resolved: 'Resolved',
                };
                return (
                  <div key={step} className="flex items-center flex-1">
                    <div className="flex flex-col items-center">
                      <div
                        className={`h-7 w-7 rounded-full flex items-center justify-center text-xs font-bold
                          ${isCompleted ? 'bg-amber-500 text-black' : ''}
                          ${isCurrent ? 'bg-amber-500/20 border-2 border-amber-500 text-amber-400' : ''}
                          ${!isCompleted && !isCurrent ? 'bg-slate-800 text-slate-600' : ''}
                        `}
                      >
                        {isCompleted ? '✓' : i + 1}
                      </div>
                      <span
                        className={`text-[10px] mt-1 font-medium
                          ${isCurrent ? 'text-amber-400' : isCompleted ? 'text-slate-400' : 'text-slate-600'}
                        `}
                      >
                        {labels[step]}
                      </span>
                    </div>
                    {i < ISSUE_STATUS_PIPELINE.length - 1 && (
                      <div
                        className={`flex-1 h-0.5 mx-1 ${
                          i < currentStepIndex ? 'bg-amber-500/50' : 'bg-slate-800'
                        }`}
                      />
                    )}
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>
      )}
      
      {/* Stats */}
      <div className="grid grid-cols-3 gap-4">
        <Card>
          <CardContent className="py-4">
            <div className="flex items-center gap-2 mb-1">
              <PhoneCall className="h-4 w-4 text-blue-400" />
              <span className="text-xs text-slate-400">Calls</span>
            </div>
            <p className="text-xl font-bold text-white">{issue.totalCalls ?? 0}</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="py-4">
            <div className="flex items-center gap-2 mb-1">
              <Clock className="h-4 w-4 text-amber-400" />
              <span className="text-xs text-slate-400">Hold Time</span>
            </div>
            <p className="text-xl font-bold text-white">
              {formatDuration(issue.totalHoldSecs ?? 0)}
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="py-4">
            <div className="flex items-center gap-2 mb-1">
              <DollarSign className="h-4 w-4 text-green-400" />
              <span className="text-xs text-slate-400">AI Cost</span>
            </div>
            <p className="text-xl font-bold text-white">
              {formatCents(issue.totalCostCents ?? 0)}
            </p>
          </CardContent>
        </Card>
      </div>
      
      {/* Details */}
      {(issue.desiredOutcome || (issue.referenceNumbers as string[])?.length > 0 || issue.companyPhone) && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <FileText className="h-4 w-4 text-slate-400" />
              Details
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {issue.companyPhone && (
              <div>
                <p className="text-xs text-slate-400 mb-1">Phone</p>
                <p className="text-sm font-mono text-white">{formatPhone(issue.companyPhone)}</p>
              </div>
            )}
            {issue.desiredOutcome && (
              <div>
                <p className="text-xs text-slate-400 mb-1">Desired Outcome</p>
                <p className="text-sm text-white">{issue.desiredOutcome}</p>
              </div>
            )}
            {(issue.referenceNumbers as string[])?.length > 0 && (
              <div>
                <p className="text-xs text-slate-400 mb-2">Reference Numbers</p>
                <div className="flex flex-wrap gap-2">
                  {(issue.referenceNumbers as string[]).map((ref) => (
                    <span
                      key={ref}
                      className="font-mono text-xs bg-slate-800 text-slate-300 px-2 py-1 rounded border border-slate-700"
                    >
                      {ref}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}
      
      {/* Call History */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Call History</CardTitle>
        </CardHeader>
        {issueCalls.length === 0 ? (
          <CardContent>
            <p className="text-sm text-slate-500 text-center py-6">
              No calls yet. Hit "Start Call" to let AI handle this issue.
            </p>
          </CardContent>
        ) : (
          <div className="divide-y divide-slate-800">
            {issueCalls.map((call) => (
              <div key={call.id} className="px-6 py-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <StatusBadge status={call.status} type="call" />
                    <span className="text-sm text-white font-mono text-xs">
                      {formatPhone(call.phoneNumber)}
                    </span>
                  </div>
                  <div className="flex items-center gap-4 text-xs text-slate-500">
                    {call.durationSecs && (
                      <span>{formatDuration(call.durationSecs)}</span>
                    )}
                    <span>{formatRelativeDate(call.startedAt)}</span>
                  </div>
                </div>
                {call.humanAgentName && (
                  <p className="text-xs text-slate-500 mt-2">Spoke with: {call.humanAgentName}</p>
                )}
                {call.outcome && call.outcome !== 'unknown' && (
                  <p className="text-xs text-slate-400 mt-1 capitalize">
                    Outcome: {call.outcome.replace(/_/g, ' ')}
                  </p>
                )}
              </div>
            ))}
          </div>
        )}
      </Card>
    </div>
  );
}
