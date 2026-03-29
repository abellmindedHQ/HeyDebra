import { auth } from '@/lib/auth';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Settings } from 'lucide-react';

export default async function SettingsPage() {
  const session = await auth();
  
  return (
    <div className="p-6 space-y-6 max-w-2xl">
      <div>
        <h1 className="text-2xl font-bold text-white">Settings</h1>
        <p className="text-sm text-slate-400 mt-1">Manage your HoldPlease account</p>
      </div>
      
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Account</CardTitle>
          <CardDescription>Your profile information</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <p className="text-xs text-slate-400 mb-1">Name</p>
            <p className="text-sm text-white">{session?.user?.name ?? '—'}</p>
          </div>
          <div>
            <p className="text-xs text-slate-400 mb-1">Email</p>
            <p className="text-sm text-white font-mono">{session?.user?.email ?? '—'}</p>
          </div>
        </CardContent>
      </Card>
      
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Phone Engine</CardTitle>
          <CardDescription>Connection to the AI phone engine</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-2">
            <div className="h-2 w-2 rounded-full bg-green-500 animate-pulse" />
            <span className="text-sm text-slate-300">Engine running on port 3978</span>
          </div>
          <p className="text-xs text-slate-500 mt-2">
            The phone engine handles Twilio calls and ElevenLabs conversations separately from the web app.
          </p>
        </CardContent>
      </Card>
      
      <Card>
        <CardHeader>
          <CardTitle className="text-base">More settings coming soon</CardTitle>
          <CardDescription>Callback number, notification preferences, API keys</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-2 text-slate-500">
            <Settings className="h-4 w-4" />
            <span className="text-sm">Settings are being built out in Day 2 of the sprint.</span>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
