'use client';

import { useParams, useRouter } from 'next/navigation';
import { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input, Textarea } from '@/components/ui/input';
import { StatusBadge } from '@/components/issues/status-badge';
import { ArrowLeft, Phone, PhoneOff } from 'lucide-react';
import Link from 'next/link';

interface Issue {
  id: string;
  title: string;
  company: string;
  companyPhone?: string;
  description?: string;
  referenceNumbers?: string[];
}

export default function StartCallPage() {
  const params = useParams();
  const router = useRouter();
  const issueId = params.id as string;
  
  const [issue, setIssue] = useState<Issue | null>(null);
  const [loading, setLoading] = useState(false);
  const [callStatus, setCallStatus] = useState<string | null>(null);
  const [task, setTask] = useState('');
  const [phone, setPhone] = useState('');
  
  useEffect(() => {
    fetch(`/api/v1/issues/${issueId}`)
      .then((r) => r.json())
      .then((data) => {
        setIssue(data);
        setPhone(data.companyPhone ?? '');
        if (data.description) {
          setTask(
            `${data.description}${data.referenceNumbers?.length ? `\n\nReference numbers: ${data.referenceNumbers.join(', ')}` : ''}`
          );
        }
      });
  }, [issueId]);
  
  async function handleStartCall(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setCallStatus('connecting');
    
    try {
      const res = await fetch(`/api/v1/issues/${issueId}/calls`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ task, phoneNumber: phone }),
      });
      
      const data = await res.json();
      
      if (!res.ok) {
        setCallStatus(null);
        alert(data.error || 'Failed to start call.');
        return;
      }
      
      // Redirect back to issue page to see call in progress
      router.push(`/dashboard/issues/${issueId}`);
    } finally {
      setLoading(false);
    }
  }
  
  if (!issue) {
    return (
      <div className="p-6 flex items-center justify-center min-h-64">
        <div className="text-slate-400">Loading...</div>
      </div>
    );
  }
  
  return (
    <div className="p-6 max-w-xl">
      <Link
        href={`/dashboard/issues/${issueId}`}
        className="inline-flex items-center gap-1.5 text-sm text-slate-400 hover:text-white transition-colors mb-6"
      >
        <ArrowLeft className="h-3.5 w-3.5" />
        Back to Issue
      </Link>
      
      <h1 className="text-2xl font-bold text-white mb-1">Start a Call</h1>
      <p className="text-sm text-slate-400 mb-6">{issue.company} — {issue.title}</p>
      
      <form onSubmit={handleStartCall} className="space-y-5">
        <Card>
          <CardContent className="pt-5 space-y-4">
            <Input
              label="Phone Number to Call"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              placeholder="+1 (800) 555-1234"
              type="tel"
              required
            />
            <Textarea
              label="Task Instructions"
              value={task}
              onChange={(e) => setTask(e.target.value)}
              placeholder="What should the AI do on this call? Be specific — include your name, reference numbers, what outcome you want..."
              rows={8}
              hint="More detail = better call. Include everything the rep might need."
            />
          </CardContent>
        </Card>
        
        <div className="bg-amber-500/10 border border-amber-500/20 rounded-lg px-4 py-3">
          <p className="text-xs text-amber-400 font-medium mb-1">What happens next</p>
          <p className="text-xs text-slate-400">
            AI will dial the number, navigate the IVR menu, wait on hold, and handle the
            conversation using your instructions. You'll get a full transcript + highlights
            when the call ends.
          </p>
        </div>
        
        <Button
          type="submit"
          loading={loading}
          className="w-full"
          size="lg"
        >
          <Phone className="h-4 w-4" />
          {loading ? 'Connecting...' : 'Start Call'}
        </Button>
      </form>
    </div>
  );
}
