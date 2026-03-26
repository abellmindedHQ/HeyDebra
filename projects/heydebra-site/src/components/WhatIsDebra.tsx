import { motion } from 'framer-motion'
import { useScrollReveal } from '../hooks/useScrollReveal'

const stats = [
  { value: '17', label: 'Automated Cron Jobs', icon: '⚡', color: 'text-gold' },
  { value: '8', label: 'Capture Streams', icon: '📡', color: 'text-teal' },
  { value: '3+', label: 'Messaging Channels', icon: '💬', color: 'text-hot-pink' },
  { value: '24/7', label: 'Always On', icon: '🔮', color: 'text-gold' },
]

export function WhatIsDebra() {
  const { ref, isVisible } = useScrollReveal()

  return (
    <section id="what-is-debra" className="relative py-32 px-4 overflow-hidden">
      {/* Background accent */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-hot-pink/40 to-transparent" />
        <div className="absolute bottom-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-teal/40 to-transparent" />
        <div className="absolute top-20 right-0 w-96 h-96"
          style={{ background: 'radial-gradient(circle, rgba(0,245,255,0.04) 0%, transparent 70%)' }} />
      </div>

      <div ref={ref} className="max-w-6xl mx-auto">
        {/* Section header */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={isVisible ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.7 }}
          className="text-center mb-20"
        >
          <span className="text-xs font-mono text-hot-pink tracking-widest uppercase">Who is she</span>
          <h2 className="font-display text-[clamp(3rem,8vw,7rem)] leading-none mt-2 text-gradient-pink">
            WHAT IS DEBRA?
          </h2>
        </motion.div>

        {/* Main description */}
        <div className="grid md:grid-cols-2 gap-12 items-center mb-24">
          <motion.div
            initial={{ opacity: 0, x: -40 }}
            animate={isVisible ? { opacity: 1, x: 0 } : {}}
            transition={{ duration: 0.7, delay: 0.2 }}
          >
            {/* Not this */}
            <div className="mb-8 p-5 rounded-xl border border-white/10 bg-white/3 relative overflow-hidden">
              <div className="absolute top-0 left-0 right-0 h-full opacity-5"
                style={{ background: 'repeating-linear-gradient(45deg, #fff 0px, #fff 1px, transparent 1px, transparent 10px)' }} />
              <div className="flex items-start gap-3">
                <span className="text-2xl">🚫</span>
                <div>
                  <p className="text-white/40 text-sm font-mono uppercase tracking-wider mb-1">Not this</p>
                  <p className="text-white/50 line-through text-lg">"Hi! I'm your AI assistant. How can I help you today?"</p>
                </div>
              </div>
            </div>

            {/* This */}
            <div className="p-5 rounded-xl border border-hot-pink/30 bg-hot-pink/5 relative overflow-hidden">
              <div className="absolute inset-0 bg-gradient-to-br from-hot-pink/5 to-transparent pointer-events-none" />
              <div className="flex items-start gap-3">
                <span className="text-2xl">✨</span>
                <div>
                  <p className="text-hot-pink text-sm font-mono uppercase tracking-wider mb-2">Debra</p>
                  <p className="text-white text-lg leading-relaxed">
                    "Sugar, I already handled it. Flights are booked, your boss knows about the time off, and I saved you $92 on that prescription. You're welcome."
                  </p>
                </div>
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, x: 40 }}
            animate={isVisible ? { opacity: 1, x: 0 } : {}}
            transition={{ duration: 0.7, delay: 0.3 }}
            className="space-y-6"
          >
            <p className="text-white/80 text-xl leading-relaxed">
              Debra is a <span className="text-hot-pink font-semibold">retro-futuristic AI executive assistant</span> with the sass of a 70s power secretary and the brain of a cutting-edge polymath.
            </p>
            <p className="text-white/60 text-lg leading-relaxed">
              She's not a chatbot. She's not a widget. She's a fully autonomous agent that manages communications, memory, logistics, and life — across every channel, around the clock.
            </p>
            <p className="text-white/60 text-lg leading-relaxed">
              Built on{' '}
              <a
                href="https://openclaw.ai"
                target="_blank"
                rel="noopener noreferrer"
                className="text-teal hover:text-white transition-colors underline underline-offset-4"
              >
                OpenClaw
              </a>
              {' '}— the open-source AI agent runtime for people who mean business.
            </p>

            {/* Built-on badge */}
            <div className="inline-flex items-center gap-3 px-4 py-3 rounded-lg border border-teal/20 bg-teal/5">
              <div className="w-8 h-8 rounded bg-teal/20 flex items-center justify-center">
                <span className="text-teal text-lg">🦞</span>
              </div>
              <div>
                <div className="text-xs text-teal/60 uppercase tracking-wider">Powered by</div>
                <div className="text-teal font-semibold">OpenClaw Runtime</div>
              </div>
            </div>
          </motion.div>
        </div>

        {/* Stats grid */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={isVisible ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.7, delay: 0.5 }}
          className="grid grid-cols-2 md:grid-cols-4 gap-4"
        >
          {stats.map((stat, i) => (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, y: 20 }}
              animate={isVisible ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.5, delay: 0.6 + i * 0.1 }}
              className="relative group p-6 rounded-xl border border-dark-border bg-dark-card hover:border-hot-pink/30 transition-all duration-300 text-center overflow-hidden"
            >
              <div className="absolute inset-0 bg-gradient-to-b from-hot-pink/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
              <div className="text-3xl mb-2">{stat.icon}</div>
              <div className={`font-display text-5xl ${stat.color} glow-pink`}>{stat.value}</div>
              <div className="text-xs text-white/40 uppercase tracking-wider mt-1">{stat.label}</div>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  )
}
