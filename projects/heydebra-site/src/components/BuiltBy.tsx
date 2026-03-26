import { motion } from 'framer-motion'
import { useScrollReveal } from '../hooks/useScrollReveal'

export function BuiltBy() {
  const { ref, isVisible } = useScrollReveal()

  return (
    <section id="built-by" className="relative py-32 px-4 overflow-hidden">
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-gold/30 to-transparent" />
        <div className="absolute inset-0"
          style={{ background: 'radial-gradient(ellipse at 30% 50%, rgba(255,215,0,0.05) 0%, transparent 60%)' }} />
      </div>

      <div ref={ref} className="max-w-5xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={isVisible ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.7 }}
          className="text-center mb-20"
        >
          <span className="text-xs font-mono text-gold tracking-widest uppercase">The creator</span>
          <h2 className="font-display text-[clamp(3rem,8vw,7rem)] leading-none mt-2">
            <span className="text-gradient-pink">BUILT BY</span>
            <br />
            <span className="text-white">ABELLMINDED</span>
          </h2>
        </motion.div>

        <div className="grid md:grid-cols-2 gap-12 items-center">
          {/* Left: About */}
          <motion.div
            initial={{ opacity: 0, x: -30 }}
            animate={isVisible ? { opacity: 1, x: 0 } : {}}
            transition={{ duration: 0.7, delay: 0.2 }}
            className="space-y-6"
          >
            <div className="p-6 rounded-2xl border border-gold/20 bg-gold/5">
              <div className="text-4xl mb-4">🏗️</div>
              <p className="text-white/80 text-lg leading-relaxed">
                Debra is part of the <span className="text-gold font-semibold">Abellminded ecosystem</span> — a framework for AI companions that actually know you.
              </p>
            </div>

            <p className="text-white/60 leading-relaxed">
              Built by <span className="text-white font-semibold">Alex Abell</span> — transformation group lead, ex-founder, and the guy who thought "what if my executive assistant was also a 70s icon who never sleeps."
            </p>

            <a
              href="https://abellminded.com"
              target="_blank"
              rel="noopener noreferrer"
              aria-label="Visit Abellminded website (opens in new tab)"
              className="inline-flex items-center gap-2 text-gold hover:text-white transition-colors duration-200 font-medium focus:outline-none focus-visible:ring-2 focus-visible:ring-gold focus-visible:ring-offset-2 focus-visible:ring-offset-deep-black rounded"
            >
              <span>abellminded.com</span>
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
              </svg>
            </a>
          </motion.div>

          {/* Right: Ecosystem */}
          <motion.div
            initial={{ opacity: 0, x: 30 }}
            animate={isVisible ? { opacity: 1, x: 0 } : {}}
            transition={{ duration: 0.7, delay: 0.3 }}
            className="space-y-4"
          >
            <div className="text-xs font-mono text-white/30 uppercase tracking-widest mb-6">The ecosystem</div>

            {[
              {
                name: 'Mirror',
                tagline: 'Know yourself',
                desc: 'Deep self-knowledge and personal insight framework.',
                icon: '🪞',
                color: '#FF006E',
              },
              {
                name: 'Pools',
                tagline: 'Know your world',
                desc: 'Network intelligence and relationship graph tools.',
                icon: '🌊',
                color: '#00F5FF',
              },
              {
                name: 'AI Companion',
                tagline: 'Your sherpa',
                desc: 'The framework that powers Debra — and agents like her.',
                icon: '🤖',
                color: '#FFD700',
                active: true,
              },
            ].map((item, i) => (
              <motion.div
                key={item.name}
                initial={{ opacity: 0, y: 10 }}
                animate={isVisible ? { opacity: 1, y: 0 } : {}}
                transition={{ delay: 0.5 + i * 0.1 }}
                className={`flex items-center gap-4 p-4 rounded-xl border transition-all duration-300 ${
                  item.active
                    ? 'border-gold/30 bg-gold/5'
                    : 'border-dark-border bg-dark-card'
                }`}
              >
                <div className="w-12 h-12 rounded-xl flex items-center justify-center text-2xl flex-shrink-0"
                  style={{ background: item.color + '20' }}>
                  {item.icon}
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-semibold text-white">{item.name}</span>
                    {item.active && (
                      <span className="text-xs px-2 py-0.5 rounded-full bg-gold/20 text-gold font-mono">active</span>
                    )}
                  </div>
                  <div className="text-xs mt-0.5" style={{ color: item.color }}>{item.tagline}</div>
                  <div className="text-xs text-white/40 mt-1">{item.desc}</div>
                </div>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </div>
    </section>
  )
}
