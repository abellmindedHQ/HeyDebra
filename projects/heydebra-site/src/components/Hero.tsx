import { motion } from 'framer-motion'
import { useTypewriter } from '../hooks/useTypewriter'

const typingTexts = [
  'saved $92.60 on your prescription',
  'handled your boss email',
  'found flights $900 cheaper',
  'transcribed your doctor visit',
  'sent a haiku via voice note',
  'cleaned 6,329 junk contacts',
  'covered for your wrong-chat slip',
  'built your medical records',
  'ran 17 cron jobs overnight',
  'processed 20 years of your data',
]

export function Hero() {
  const typed = useTypewriter(typingTexts, 55, 2200)

  const scrollToNext = () => {
    document.getElementById('what-is-debra')?.scrollIntoView({ behavior: 'smooth' })
  }

  return (
    <section className="relative min-h-screen flex flex-col items-center justify-center overflow-hidden grid-bg">
      {/* Radial glow background */}
      <div className="absolute inset-0 bg-hero-glow pointer-events-none" />

      {/* Scanline effect */}
      <div
        className="absolute left-0 right-0 h-px pointer-events-none scanline-overlay"
        style={{ background: 'linear-gradient(90deg, transparent, rgba(0,245,255,0.3), transparent)' }}
      />

      {/* Corner decorations */}
      <div className="absolute top-8 left-8 w-16 h-16 border-l-2 border-t-2 border-hot-pink opacity-40" />
      <div className="absolute top-8 right-8 w-16 h-16 border-r-2 border-t-2 border-teal opacity-40" />
      <div className="absolute bottom-8 left-8 w-16 h-16 border-l-2 border-b-2 border-gold opacity-40" />
      <div className="absolute bottom-8 right-8 w-16 h-16 border-r-2 border-b-2 border-hot-pink opacity-40" />

      {/* Pulsing orbs */}
      <div className="absolute top-1/4 left-1/4 w-64 h-64 rounded-full pointer-events-none"
        style={{ background: 'radial-gradient(circle, rgba(255,0,110,0.08) 0%, transparent 70%)' }} />
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 rounded-full pointer-events-none"
        style={{ background: 'radial-gradient(circle, rgba(0,245,255,0.06) 0%, transparent 70%)' }} />

      {/* Main content */}
      <div className="relative z-10 text-center px-4 max-w-6xl mx-auto">
        {/* Status badge */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="inline-flex items-center gap-2 mb-8 px-4 py-2 rounded-full border border-hot-pink/30 bg-hot-pink/5"
        >
          <span className="w-2 h-2 rounded-full bg-hot-pink animate-pulse" />
          <span className="text-xs font-mono text-hot-pink tracking-widest uppercase">Live & Running 24/7</span>
        </motion.div>

        {/* Main title */}
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.8, delay: 0.2 }}
        >
          <h1 className="font-display text-[clamp(5rem,18vw,16rem)] leading-none tracking-tight text-gradient-pink glow-pink">
            HEY<br />DEBRA
          </h1>
        </motion.div>

        {/* Tagline */}
        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.5 }}
          className="mt-4 mb-10 text-[clamp(1rem,3vw,1.6rem)] text-white/70 font-light tracking-wide max-w-2xl mx-auto"
        >
          She doesn't just assist.{' '}
          <span className="text-gold font-semibold">She runs the damn show.</span>
        </motion.p>

        {/* Typewriter */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.8 }}
          className="mb-12 px-6 py-4 rounded-lg border border-dark-border bg-dark-card/60 backdrop-blur-sm inline-block min-w-[280px] max-w-full"
        >
          <span className="text-xs font-mono text-teal/60 tracking-widest uppercase block mb-1">Right now, she&apos;s</span>
          <div className="flex items-center gap-2">
            <span className="text-lg font-mono text-teal">{typed}</span>
            <span className="w-0.5 h-5 bg-teal cursor-blink inline-block" />
          </div>
        </motion.div>

        {/* CTA */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 1 }}
        >
          <button
            onClick={scrollToNext}
            aria-label="Meet Debra — scroll down to learn more"
            className="group relative inline-flex items-center gap-3 px-10 py-4 rounded-full font-semibold text-lg transition-all duration-300 overflow-hidden focus:outline-none focus-visible:ring-2 focus-visible:ring-white focus-visible:ring-offset-2 focus-visible:ring-offset-deep-black"
            style={{
              background: 'linear-gradient(135deg, #FF006E, #FF2D78)',
              boxShadow: '0 0 30px rgba(255, 0, 110, 0.4)',
            }}
          >
            <span className="relative z-10">Meet Debra</span>
            <svg className="w-5 h-5 relative z-10 group-hover:translate-y-1 transition-transform duration-300" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
            <div className="absolute inset-0 bg-gradient-to-r from-fuchsia to-gold opacity-0 group-hover:opacity-100 transition-opacity duration-300" aria-hidden="true" />
          </button>
        </motion.div>

        {/* Stat pills */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.8, delay: 1.3 }}
          className="flex flex-wrap justify-center gap-4 mt-12"
        >
          {[
            { label: '17', sub: 'cron jobs' },
            { label: '8', sub: 'capture streams' },
            { label: '24/7', sub: 'always on' },
            { label: '4', sub: 'days old' },
          ].map((stat) => (
            <div key={stat.label} className="text-center px-5 py-2 rounded border border-white/10 bg-white/5">
              <div className="font-display text-2xl text-gold">{stat.label}</div>
              <div className="text-xs text-white/40 uppercase tracking-widest">{stat.sub}</div>
            </div>
          ))}
        </motion.div>
      </div>

      {/* Scroll indicator */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 2, duration: 1 }}
        className="absolute bottom-8 left-1/2 -translate-x-1/2"
        aria-hidden="true"
      >
        <div className="w-6 h-10 rounded-full border-2 border-white/20 flex justify-center pt-2">
          <motion.div
            animate={{ y: [0, 12, 0] }}
            transition={{ repeat: Infinity, duration: 1.5, ease: 'easeInOut' }}
            className="w-1 h-2 rounded-full bg-hot-pink"
          />
        </div>
      </motion.div>
    </section>
  )
}
