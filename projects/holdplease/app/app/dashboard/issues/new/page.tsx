'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input, Textarea } from '@/components/ui/input';
import { ArrowLeft, Plus, X } from 'lucide-react';
import Link from 'next/link';

export default function NewIssuePage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [refNumbers, setRefNumbers] = useState<string[]>(['']);
  
  const [form, setForm] = useState({
    title: '',
    company: '',
    companyPhone: '',
    department: '',
    description: '',
    desiredOutcome: '',
    priority: '3',
  });
  
  function updateForm(key: string, value: string) {
    setForm((prev) => ({ ...prev, [key]: value }));
  }
  
  function addRefNumber() {
    setRefNumbers((prev) => [...prev, '']);
  }
  
  function updateRefNumber(index: number, value: string) {
    setRefNumbers((prev) => prev.map((n, i) => (i === index ? value : n)));
  }
  
  function removeRefNumber(index: number) {
    setRefNumbers((prev) => prev.filter((_, i) => i !== index));
  }
  
  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError('');
    setLoading(true);
    
    try {
      const res = await fetch('/api/v1/issues', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...form,
          priority: parseInt(form.priority),
          referenceNumbers: refNumbers.filter(Boolean),
        }),
      });
      
      const data = await res.json();
      
      if (!res.ok) {
        setError(data.error || 'Failed to create issue.');
        return;
      }
      
      router.push(`/dashboard/issues/${data.id}`);
    } finally {
      setLoading(false);
    }
  }
  
  return (
    <div className="p-6 max-w-2xl">
      <div className="mb-6">
        <Link
          href="/dashboard/issues"
          className="inline-flex items-center gap-1.5 text-sm text-slate-400 hover:text-white transition-colors mb-4"
        >
          <ArrowLeft className="h-3.5 w-3.5" />
          Back to Issues
        </Link>
        <h1 className="text-2xl font-bold text-white">New Issue</h1>
        <p className="text-sm text-slate-400 mt-1">
          Tell AI what to handle. The more context, the better the call.
        </p>
      </div>
      
      <form onSubmit={handleSubmit} className="space-y-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Issue Details</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <Input
              label="Title"
              value={form.title}
              onChange={(e) => updateForm('title', e.target.value)}
              placeholder="e.g. Lufthansa baggage reimbursement claim"
              required
            />
            <div className="grid grid-cols-2 gap-4">
              <Input
                label="Company"
                value={form.company}
                onChange={(e) => updateForm('company', e.target.value)}
                placeholder="e.g. Lufthansa"
                required
              />
              <Input
                label="Phone Number"
                value={form.companyPhone}
                onChange={(e) => updateForm('companyPhone', e.target.value)}
                placeholder="+1 (800) 555-1234"
                type="tel"
              />
            </div>
            <Input
              label="Department (optional)"
              value={form.department}
              onChange={(e) => updateForm('department', e.target.value)}
              placeholder="e.g. Baggage Claims, Customer Service"
            />
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1.5">
                Priority
              </label>
              <select
                value={form.priority}
                onChange={(e) => updateForm('priority', e.target.value)}
                className="w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-amber-500/50"
              >
                <option value="1">🔴 Urgent</option>
                <option value="2">🟠 High</option>
                <option value="3">🟡 Normal</option>
                <option value="4">⚪ Low</option>
              </select>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <CardTitle className="text-base">The Problem</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <Textarea
              label="Description"
              value={form.description}
              onChange={(e) => updateForm('description', e.target.value)}
              placeholder="Describe the situation in detail. Include dates, amounts, what happened, what you've already tried..."
              rows={5}
            />
            <Textarea
              label="Desired Outcome"
              value={form.desiredOutcome}
              onChange={(e) => updateForm('desiredOutcome', e.target.value)}
              placeholder="What does success look like? e.g. Full refund of $450, account credited, ticket reissued..."
              rows={3}
            />
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="text-base">Reference Numbers</CardTitle>
              <button
                type="button"
                onClick={addRefNumber}
                className="text-xs text-amber-400 hover:text-amber-300 flex items-center gap-1"
              >
                <Plus className="h-3 w-3" /> Add more
              </button>
            </div>
          </CardHeader>
          <CardContent className="space-y-3">
            {refNumbers.map((ref, i) => (
              <div key={i} className="flex gap-2">
                <Input
                  value={ref}
                  onChange={(e) => updateRefNumber(i, e.target.value)}
                  placeholder={`e.g. Case #12345, Order #ABC-789, Booking ref...`}
                  className="flex-1"
                />
                {refNumbers.length > 1 && (
                  <button
                    type="button"
                    onClick={() => removeRefNumber(i)}
                    className="text-slate-600 hover:text-red-400 transition-colors mt-0 flex-shrink-0 h-10 flex items-center"
                  >
                    <X className="h-4 w-4" />
                  </button>
                )}
              </div>
            ))}
            <p className="text-xs text-slate-500">
              Case numbers, order IDs, booking refs — anything the rep might ask for
            </p>
          </CardContent>
        </Card>
        
        {error && (
          <p className="text-sm text-red-400 bg-red-900/20 border border-red-700/30 rounded-lg px-4 py-3">
            {error}
          </p>
        )}
        
        <div className="flex gap-3">
          <Button type="submit" loading={loading}>
            Create Issue
          </Button>
          <Button
            type="button"
            variant="ghost"
            onClick={() => router.push('/dashboard/issues')}
          >
            Cancel
          </Button>
        </div>
      </form>
    </div>
  );
}
