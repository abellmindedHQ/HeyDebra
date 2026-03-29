import Link from 'next/link';
import { PhoneForwarded, Clock, Zap, Shield } from 'lucide-react';

export default function LandingPage() {
  return (
    <main className="min-h-screen bg-[#0a0a0a] text-white">
      {/* Header */}
      <header className="border-b border-slate-800/50 px-6 py-4">
        <div className="mx-auto max-w-6xl flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-amber-500">
              <PhoneForwarded className="h-4 w-4 text-black" />
            </div>
            <span className="text-sm font-bold tracking-tight">HoldPlease</span>
          </div>
          <div className="flex items-center gap-3">
            <Link
              href="/login"
              className="text-sm text-slate-400 hover:text-white transition-colors"
            >
              Sign in
            </Link>
            <Link
              href="/register"
              className="rounded-lg bg-amber-500 px-4 py-2 text-sm font-semibold text-black hover:bg-amber-400 transition-colors"
            >
              Get started
            </Link>
          </div>
        </div>
      </header>

      {/* Hero */}
      <section className="mx-auto max-w-6xl px-6 py-24 text-center">
        <div className="inline-flex items-center gap-2 rounded-full border border-amber-500/30 bg-amber-500/10 px-3 py-1 text-xs text-amber-400 mb-8">
          <Zap className="h-3 w-3" />
          AI-powered phone agent
        </div>
        <h1 className="text-5xl font-bold tracking-tight text-white leading-tight mb-6">
          Stop waiting on hold.
          <br />
          <span className="text-amber-400">We'll handle it.</span>
        </h1>
        <p className="text-xl text-slate-400 max-w-2xl mx-auto mb-10">
          HoldPlease dials in, navigates the IVR, waits on hold, and patches you in
          the moment a real human picks up. Your time is too valuable for hold music.
        </p>
        <div className="flex items-center justify-center gap-4">
          <Link
            href="/register"
            className="rounded-lg bg-amber-500 px-6 py-3 font-semibold text-black hover:bg-amber-400 transition-colors"
          >
            Start for free
          </Link>
          <Link
            href="/login"
            className="rounded-lg border border-slate-700 px-6 py-3 font-semibold text-slate-300 hover:border-slate-600 hover:text-white transition-colors"
          >
            Sign in
          </Link>
        </div>
      </section>

      {/* Features */}
      <section className="mx-auto max-w-6xl px-6 py-16">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {[
            {
              icon: <Clock className="h-5 w-5 text-amber-400" />,
              title: 'We hold, you live',
              desc: 'AI waits on hold indefinitely. You get a callback the second a human answers.',
            },
            {
              icon: <Zap className="h-5 w-5 text-amber-400" />,
              title: 'Smart conversation',
              desc: 'ElevenLabs AI handles the entire conversation based on your instructions.',
            },
            {
              icon: <Shield className="h-5 w-5 text-amber-400" />,
              title: 'Full transcript',
              desc: 'Every call is recorded and transcribed. Smart highlights surface what matters.',
            },
          ].map((feature) => (
            <div
              key={feature.title}
              className="rounded-xl border border-slate-800 bg-slate-900/30 p-6"
            >
              <div className="mb-4">{feature.icon}</div>
              <h3 className="font-semibold text-white mb-2">{feature.title}</h3>
              <p className="text-sm text-slate-400">{feature.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-slate-800/50 px-6 py-8 mt-16">
        <div className="mx-auto max-w-6xl text-center text-xs text-slate-600">
          © {new Date().getFullYear()} HoldPlease. Built to reclaim your time.
        </div>
      </footer>
    </main>
  );
}
