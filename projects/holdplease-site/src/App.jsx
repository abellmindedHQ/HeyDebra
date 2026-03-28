import { motion, useInView } from 'framer-motion'
import { useRef, useState, useEffect, useCallback } from 'react'

// ─── Animations ───
const fadeUp = {
  hidden: { opacity: 0, y: 30 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.6, ease: 'easeOut' } },
}

const stagger = {
  visible: { transition: { staggerChildren: 0.1 } },
}

function Section({ children, className = '', id }) {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true, margin: '0px' })
  return (
    <motion.section
      ref={ref}
      id={id}
      initial="hidden"
      animate={isInView ? 'visible' : 'hidden'}
      variants={stagger}
      className={className}
    >
      {children}
    </motion.section>
  )
}

// ─── Phone Visual ───
function PhoneVisual({ compact = false }) {
  return (
    <div className={`relative mx-auto ${compact ? 'w-48 h-56' : 'w-64 h-80'}`}>
      {/* Glow */}
      <div className="absolute inset-0 rounded-3xl bg-teal-500/10 blur-3xl" />
      {/* Phone body */}
      <div className="relative w-full h-full rounded-3xl border border-teal-500/20 bg-dark-800/80 backdrop-blur-sm flex flex-col items-center justify-center gap-4 overflow-hidden">
        {/* Screen content */}
        <div className="text-center z-10">
          <div className={`text-teal-400/60 uppercase tracking-widest mb-1.5 ${compact ? 'text-[10px]' : 'text-xs'}`}>On Hold</div>
          <div className={`font-semibold text-white/90 ${compact ? 'text-base' : 'text-lg'}`}>Xfinity Support</div>
          <div className={`text-white/40 mt-1 ${compact ? 'text-xs' : 'text-sm'}`}>23:47 and counting...</div>
        </div>
        {/* Sound waves being cancelled */}
        <div className="flex items-center gap-1 z-10">
          {[16, 26, 36, 22, 42, 30, 18].map((h, i) => (
            <div
              key={i}
              className={`rounded-full bg-teal-400/60 wave-bar ${compact ? 'w-0.5' : 'w-1'}`}
              style={{ height: compact ? h * 0.7 : h }}
            />
          ))}
        </div>
        {/* Cancel line */}
        <motion.div
          className="absolute inset-0 flex items-center justify-center z-20"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.5, duration: 0.5 }}
        >
          <div className={`h-0.5 bg-gradient-to-r from-transparent via-red-500/80 to-transparent rotate-[-25deg] ${compact ? 'w-28' : 'w-40'}`} />
        </motion.div>
        {/* HoldPlease taking over */}
        <motion.div
          className="absolute bottom-5 text-center z-20"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 2, duration: 0.6 }}
        >
          <div className={`text-teal-400 font-medium uppercase tracking-wider ${compact ? 'text-[9px]' : 'text-xs'}`}>HoldPlease handling it</div>
          <div className={`text-white/30 mt-0.5 ${compact ? 'text-[8px]' : 'text-[10px]'}`}>You'll get a text when it's done</div>
        </motion.div>
      </div>
    </div>
  )
}

// ─── Hero ───
function Hero() {
  return (
    <section className="flex items-center justify-center px-5 sm:px-6 pt-24 pb-8 md:pt-28 md:pb-20 lg:min-h-screen lg:pt-20 lg:pb-16 relative">
      {/* Background gradient */}
      <div className="absolute inset-0 bg-gradient-to-b from-teal-500/5 via-transparent to-transparent" />
      <div className="max-w-6xl mx-auto grid lg:grid-cols-2 gap-6 lg:gap-16 items-center relative z-10">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
        >
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-teal-500/20 bg-teal-500/5 text-teal-400 text-xs font-medium mb-4 sm:mb-6">
            <span className="w-1.5 h-1.5 rounded-full bg-teal-400 animate-pulse" />
            Private Beta
          </div>
          <h1 className="text-3xl sm:text-5xl md:text-6xl lg:text-7xl font-extrabold leading-[1.1] tracking-tight mb-4 sm:mb-5 text-white">
            Stop Wasting Your Life{' '}
            <span className="gradient-text">on Hold</span>
          </h1>
          <p className="text-sm sm:text-lg md:text-xl text-white/50 max-w-lg mb-6 sm:mb-8 leading-relaxed">
            You text what you need. HoldPlease handles the call, the hold music, and the conversation. You get a text when it's resolved.
          </p>
          <div className="flex flex-col sm:flex-row gap-3">
            <a
              href="#demo"
              className="px-6 py-3 sm:px-7 sm:py-3.5 rounded-xl bg-teal-500 text-dark-900 font-semibold hover:bg-teal-400 transition-colors text-center text-sm sm:text-base"
            >
              Listen to the Demo
            </a>
            <a
              href="#waitlist"
              className="px-6 py-3 sm:px-7 sm:py-3.5 rounded-xl border border-white/15 text-white/80 font-semibold hover:bg-white/5 transition-colors text-center text-sm sm:text-base"
            >
              Join the Waitlist
            </a>
          </div>
        </motion.div>

        {/* Desktop only: phone visual (hidden on mobile/tablet) */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 1, delay: 0.3 }}
          className="hidden lg:block"
        >
          <PhoneVisual />
        </motion.div>
      </div>
    </section>
  )
}

// ─── Problem ───
const painPoints = [
  { icon: '✈️', title: 'Airline lost your bags?', desc: '4 months of runaround' },
  { icon: '💳', title: 'Need to dispute a charge?', desc: '45 min hold time' },
  { icon: '🏥', title: "Doctor's office?", desc: 'Phone tag for days' },
  { icon: '📺', title: 'Cable bill too high?', desc: 'Transfer, transfer, transfer...' },
  { icon: '🍽️', title: 'No online reservations?', desc: 'Who has time to call?' },
]

function Problem() {
  return (
    <Section className="py-12 md:py-24 px-6 sm:px-6">
      <div className="max-w-5xl mx-auto">
        <motion.div variants={fadeUp} className="text-center mb-8 md:mb-16">
          <h2 className="text-xl sm:text-3xl md:text-5xl font-bold mb-3 sm:mb-4">
            We've all been there.
          </h2>
          <p className="text-white/40 text-sm sm:text-lg max-w-2xl mx-auto leading-relaxed">
            The hold music. The transfers. The <span className="italic text-white/50">"your call is important to us"</span> lie.
            Americans spend <span className="text-teal-400 font-semibold">43 days</span> of their lives on hold.
          </p>
        </motion.div>
        <div className="grid grid-cols-2 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4">
          {painPoints.map((p, i) => (
            <motion.div
              key={i}
              variants={fadeUp}
              className="card-glass rounded-xl sm:rounded-2xl p-4 sm:p-6 hover:border-teal-500/20 transition-colors"
            >
              <span className="text-xl sm:text-2xl mb-2 sm:mb-3 block">{p.icon}</span>
              <h3 className="text-white font-semibold text-sm sm:text-base mb-1">{p.title}</h3>
              <p className="text-white/40 text-xs sm:text-sm">{p.desc}</p>
            </motion.div>
          ))}
          <motion.div
            variants={fadeUp}
            className="card-glass rounded-xl sm:rounded-2xl p-4 sm:p-6 flex items-center justify-center"
          >
            <p className="text-teal-400 font-medium text-center text-sm sm:text-base">
              Sound familiar?<br />
              <span className="text-white/30 text-xs sm:text-sm font-normal">It doesn't have to be this way.</span>
            </p>
          </motion.div>
        </div>
      </div>
    </Section>
  )
}

// ─── How It Works ───
const steps = [
  {
    num: '01',
    title: 'Tell HoldPlease what you need',
    desc: 'Send a text or voice message. "Call Xfinity and dispute the $47 charge on my last bill."',
    icon: '💬',
  },
  {
    num: '02',
    title: 'HoldPlease makes the call',
    desc: 'Navigates phone menus, waits on hold, talks to the rep. All without you lifting a finger.',
    icon: '📞',
  },
  {
    num: '03',
    title: 'You get the results',
    desc: 'Text summary, full recording, and resolution details. Done in one message.',
    icon: '✅',
  },
]

function HowItWorks() {
  return (
    <Section className="py-12 md:py-24 px-6 sm:px-6">
      <div className="max-w-5xl mx-auto">
        <motion.div variants={fadeUp} className="text-center mb-8 md:mb-16">
          <h2 className="text-xl sm:text-3xl md:text-5xl font-bold mb-3 sm:mb-4">Dead simple.</h2>
          <p className="text-white/40 text-sm sm:text-lg">Three steps. Zero phone calls.</p>
        </motion.div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 md:gap-8">
          {steps.map((s, i) => (
            <motion.div key={i} variants={fadeUp} className="relative card-glass rounded-xl p-5 md:p-0 md:bg-transparent md:border-0 md:backdrop-blur-0">
              <div className="flex md:block items-start gap-3">
                <div className="shrink-0 flex md:block items-center gap-2">
                  <span className="text-2xl md:text-3xl block">{s.icon}</span>
                  <div className="text-sm md:text-6xl font-extrabold text-teal-500/20 md:text-teal-500/10">{s.num}</div>
                </div>
                <div className="min-w-0">
                  <h3 className="text-base md:text-xl font-bold text-white mb-1 sm:mb-2">{s.title}</h3>
                  <p className="text-white/40 leading-relaxed text-xs md:text-base">{s.desc}</p>
                </div>
              </div>
              {i < 2 && (
                <div className="hidden md:block absolute top-12 -right-4 text-white/10 text-3xl">→</div>
              )}
            </motion.div>
          ))}
        </div>
      </div>
    </Section>
  )
}

// ─── Demo ───
const demos = [
  {
    id: 'billing',
    icon: '💳',
    title: 'Billing Dispute',
    desc: 'A mystery $47 charge on an Xfinity bill. Debra calls, navigates the menu, holds for 34 minutes, talks to Marcus in billing, gets the charge credited.',
    timeSaved: '47 minutes saved',
    src: 'https://www.abellminded.com/holdplease-demo.mp3',
  },
  {
    id: 'baggage',
    icon: '✈️',
    title: 'Lost Baggage',
    desc: 'Lufthansa lost the bags 4 months ago. Debra calls, waits 52 minutes on hold, cites international regulations, gets the claim escalated to priority processing.',
    timeSaved: '52 minutes saved',
    src: 'https://www.abellminded.com/holdplease-demo-airline.mp3',
  },
  {
    id: 'restaurant',
    icon: '🍽️',
    title: 'Restaurant Reservation',
    desc: 'Table for two at Stock & Barrel, Saturday at 7:30. Dietary note added. Calendar updated. Done in 45 seconds.',
    timeSaved: '45 seconds vs. phone tag',
    src: 'https://www.abellminded.com/holdplease-demo-restaurant.mp3',
  },
]

function formatTime(sec) {
  if (!sec || !isFinite(sec)) return '0:00'
  const m = Math.floor(sec / 60)
  const s = Math.floor(sec % 60)
  return `${m}:${s.toString().padStart(2, '0')}`
}

function DemoPlayer() {
  const [active, setActive] = useState(0)
  const [playing, setPlaying] = useState(false)
  const [currentTime, setCurrentTime] = useState(0)
  const [duration, setDuration] = useState(0)
  const audioRef = useRef(null)
  const progressRef = useRef(null)

  const switchDemo = useCallback((idx) => {
    setActive(idx)
    setPlaying(false)
    setCurrentTime(0)
    setDuration(0)
    if (audioRef.current) {
      audioRef.current.pause()
      audioRef.current.currentTime = 0
    }
  }, [])

  useEffect(() => {
    const audio = audioRef.current
    if (!audio) return

    audio.src = demos[active].src
    audio.load()

    const onLoaded = () => setDuration(audio.duration)
    const onTime = () => setCurrentTime(audio.currentTime)
    const onEnded = () => setPlaying(false)

    audio.addEventListener('loadedmetadata', onLoaded)
    audio.addEventListener('timeupdate', onTime)
    audio.addEventListener('ended', onEnded)

    return () => {
      audio.removeEventListener('loadedmetadata', onLoaded)
      audio.removeEventListener('timeupdate', onTime)
      audio.removeEventListener('ended', onEnded)
    }
  }, [active])

  const togglePlay = () => {
    const audio = audioRef.current
    if (!audio) return
    if (playing) {
      audio.pause()
    } else {
      audio.play()
    }
    setPlaying(!playing)
  }

  const seek = (e) => {
    const bar = progressRef.current
    const audio = audioRef.current
    if (!bar || !audio || !duration) return
    const rect = bar.getBoundingClientRect()
    const pct = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width))
    audio.currentTime = pct * duration
    setCurrentTime(audio.currentTime)
  }

  const progress = duration ? (currentTime / duration) * 100 : 0

  return (
    <Section className="py-12 md:py-24 px-6 sm:px-6" id="demo">
      <div className="max-w-4xl mx-auto">
        <motion.div variants={fadeUp} className="text-center mb-8 md:mb-14">
          <h2 className="text-xl sm:text-3xl md:text-5xl font-bold mb-3 sm:mb-4">Hear it in action.</h2>
          <p className="text-white/40 text-sm sm:text-lg max-w-2xl mx-auto">Real calls. Real hold times. Real results. Press play and hear Debra handle it.</p>
        </motion.div>

        {/* Demo tabs */}
        <motion.div variants={fadeUp} className="grid grid-cols-1 sm:grid-cols-3 gap-3 mb-6">
          {demos.map((d, i) => (
            <button
              key={d.id}
              onClick={() => switchDemo(i)}
              className={`relative text-left rounded-xl p-4 sm:p-5 transition-all duration-300 cursor-pointer group ${
                active === i
                  ? 'bg-teal-500/10 border-2 border-teal-500/40 shadow-[0_0_30px_rgba(20,184,166,0.12)]'
                  : 'card-glass hover:border-teal-500/15'
              }`}
            >
              <div className="flex items-start gap-3">
                <span className="text-2xl shrink-0">{d.icon}</span>
                <div className="min-w-0">
                  <h3 className={`font-semibold text-sm sm:text-base mb-1 transition-colors ${active === i ? 'text-teal-400' : 'text-white/80 group-hover:text-white'}`}>
                    {d.title}
                  </h3>
                  <p className="text-white/35 text-xs leading-relaxed line-clamp-2 hidden sm:block">{d.desc}</p>
                </div>
              </div>
              <div className={`inline-block mt-3 px-2.5 py-1 rounded-full text-[10px] sm:text-xs font-semibold ${
                active === i ? 'bg-teal-500/20 text-teal-400' : 'bg-white/5 text-white/40'
              }`}>
                ⏱ {d.timeSaved}
              </div>
              {active === i && playing && (
                <div className="absolute top-3 right-3 flex items-center gap-0.5">
                  {[1,2,3].map(b => (
                    <div key={b} className="w-0.5 bg-teal-400 rounded-full animate-pulse" style={{ height: 8 + b * 3, animationDelay: `${b * 0.15}s` }} />
                  ))}
                </div>
              )}
            </button>
          ))}
        </motion.div>

        {/* Description (mobile only, since hidden on sm+ in tabs) */}
        <motion.div variants={fadeUp} className="sm:hidden card-glass rounded-xl p-4 mb-4">
          <p className="text-white/40 text-xs leading-relaxed">{demos[active].desc}</p>
        </motion.div>

        {/* Audio Player */}
        <motion.div variants={fadeUp} className="card-glass rounded-2xl p-5 sm:p-6 mb-8">
          <audio ref={audioRef} preload="metadata" />
          <div className="flex items-center gap-4">
            <button
              onClick={togglePlay}
              className="w-14 h-14 sm:w-16 sm:h-16 rounded-full bg-teal-500 flex items-center justify-center hover:bg-teal-400 transition-all hover:scale-105 active:scale-95 shrink-0 shadow-[0_0_24px_rgba(20,184,166,0.3)]"
            >
              {playing ? (
                <svg width="18" height="20" viewBox="0 0 18 20" fill="none">
                  <rect x="2" y="1" width="5" height="18" rx="1" fill="#0a0e17" />
                  <rect x="11" y="1" width="5" height="18" rx="1" fill="#0a0e17" />
                </svg>
              ) : (
                <svg width="18" height="20" viewBox="0 0 20 22" fill="none">
                  <path d="M3 2L18 11L3 20V2Z" fill="#0a0e17" />
                </svg>
              )}
            </button>
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-3 mb-2">
                <span className="text-sm font-medium text-white/70 truncate">{demos[active].icon} {demos[active].title}</span>
              </div>
              <div
                ref={progressRef}
                onClick={seek}
                className="h-2 bg-white/10 rounded-full overflow-hidden cursor-pointer group relative"
              >
                <div
                  className="h-full bg-gradient-to-r from-teal-500 to-teal-400 rounded-full transition-[width] duration-100 relative"
                  style={{ width: `${progress}%` }}
                >
                  <div className="absolute right-0 top-1/2 -translate-y-1/2 w-3.5 h-3.5 rounded-full bg-teal-400 shadow-lg opacity-0 group-hover:opacity-100 transition-opacity" />
                </div>
              </div>
              <div className="flex justify-between text-xs text-white/30 mt-1.5 font-mono">
                <span>{formatTime(currentTime)}</span>
                <span>{formatTime(duration)}</span>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Before/After */}
        <motion.div variants={fadeUp} className="grid grid-cols-2 gap-3 sm:gap-4">
          <div className="card-glass rounded-xl sm:rounded-2xl p-4 sm:p-6 text-center border-red-500/10">
            <div className="text-red-400/60 text-[10px] sm:text-sm font-medium mb-1.5 sm:mb-2">Without HoldPlease</div>
            <div className="text-2xl sm:text-4xl font-bold text-white mb-1">47 min</div>
            <div className="text-white/30 text-[10px] sm:text-sm">of your life, gone</div>
          </div>
          <div className="card-glass rounded-xl sm:rounded-2xl p-4 sm:p-6 text-center border-teal-500/20 glow-teal">
            <div className="text-teal-400 text-[10px] sm:text-sm font-medium mb-1.5 sm:mb-2">With HoldPlease</div>
            <div className="text-2xl sm:text-4xl font-bold text-white mb-1">1 text</div>
            <div className="text-white/30 text-[10px] sm:text-sm">and you're done</div>
          </div>
        </motion.div>
      </div>
    </Section>
  )
}

// ─── Use Cases ───
const useCases = [
  'Customer service disputes',
  'Restaurant reservations',
  'Doctor & dentist appointments',
  'Bill negotiations',
  'Government offices',
  'Travel changes',
  'Local business inquiries',
  'Insurance claims',
  'Utility setup & cancellation',
]

function UseCases() {
  return (
    <Section className="py-12 md:py-24 px-6 sm:px-6">
      <div className="max-w-5xl mx-auto">
        <motion.div variants={fadeUp} className="text-center mb-8 md:mb-16">
          <h2 className="text-xl sm:text-3xl md:text-5xl font-bold mb-3 sm:mb-4">If it requires a phone call,<br /><span className="gradient-text">HoldPlease handles it.</span></h2>
        </motion.div>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-2.5 sm:gap-3">
          {useCases.map((uc, i) => (
            <motion.div
              key={i}
              variants={fadeUp}
              className="card-glass rounded-xl px-3 sm:px-5 py-3 sm:py-4 text-center text-xs sm:text-sm font-medium text-white/70 hover:text-teal-400 hover:border-teal-500/20 transition-colors"
            >
              {uc}
            </motion.div>
          ))}
        </div>
      </div>
    </Section>
  )
}

// ─── Waitlist ───
function Waitlist() {
  const [email, setEmail] = useState('')
  const [submitted, setSubmitted] = useState(false)

  const handleSubmit = (e) => {
    e.preventDefault()
    if (email) setSubmitted(true)
  }

  return (
    <Section className="py-12 md:py-24 px-6 sm:px-6" id="waitlist">
      <div className="max-w-2xl mx-auto text-center">
        <motion.div variants={fadeUp}>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-teal-500/20 bg-teal-500/5 text-teal-400 text-xs font-medium mb-4 sm:mb-6">
            <span className="w-1.5 h-1.5 rounded-full bg-teal-400 animate-pulse" />
            Exclusive Access
          </div>
          <h2 className="text-xl sm:text-3xl md:text-5xl font-bold mb-3 sm:mb-4">HoldPlease is in private beta.</h2>
          <p className="text-white/40 text-sm sm:text-lg mb-6 sm:mb-10">
            We're letting people in slowly. Drop your email and we'll text you when it's your turn.
          </p>
        </motion.div>
        <motion.div variants={fadeUp}>
          {!submitted ? (
            <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row gap-3 max-w-md mx-auto">
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="your@email.com"
                className="flex-1 px-5 py-3.5 rounded-xl bg-white/5 border border-white/10 text-white placeholder-white/30 focus:outline-none focus:border-teal-500/40 transition-colors text-base"
                required
              />
              <button
                type="submit"
                className="px-8 py-3.5 rounded-xl bg-teal-500 text-dark-900 font-semibold hover:bg-teal-400 transition-colors whitespace-nowrap text-base"
              >
                Join Waitlist
              </button>
            </form>
          ) : (
            <div className="card-glass rounded-2xl p-6 max-w-md mx-auto">
              <div className="text-2xl mb-2">🎉</div>
              <p className="text-teal-400 font-medium">You're on the list.</p>
              <p className="text-white/40 text-sm mt-1">We'll be in touch soon.</p>
            </div>
          )}
        </motion.div>
        <motion.div variants={fadeUp} className="mt-10 sm:mt-12">
          <p className="text-white/30 text-sm">
            Built by <span className="text-white/50">Alex Abell</span>, the creator of{' '}
            <a href="https://abellminded.com/debra" target="_blank" rel="noopener" className="text-teal-400/70 hover:text-teal-400 transition-colors">
              HeyDebra
            </a>
          </p>
        </motion.div>
      </div>
    </Section>
  )
}

// ─── Navbar ───
function Navbar() {
  return (
    <nav className="fixed top-0 inset-x-0 z-50 backdrop-blur-md bg-dark-900/70 border-b border-white/5">
      <div className="max-w-6xl mx-auto px-5 sm:px-6 h-14 sm:h-16 flex items-center justify-between">
        <a href="#" className="text-lg sm:text-xl font-bold text-white">
          Hold<span className="text-teal-400">Please</span>
        </a>
        <a
          href="#waitlist"
          className="px-4 sm:px-5 py-2 rounded-lg bg-teal-500/10 text-teal-400 text-sm font-medium hover:bg-teal-500/20 transition-colors"
        >
          Get Early Access
        </a>
      </div>
    </nav>
  )
}

// ─── Footer ───
function Footer() {
  return (
    <footer className="py-10 md:py-16 px-6 sm:px-6 border-t border-white/5">
      <div className="max-w-5xl mx-auto text-center">
        <p className="text-xl sm:text-2xl font-bold text-white mb-2">Stop waiting. Start living.</p>
        <p className="text-white/30 text-sm mb-6 sm:mb-8">A product of Abellminded</p>
        <div className="flex justify-center gap-6 text-white/30 text-sm">
          <a href="https://twitter.com/alexabell" target="_blank" rel="noopener" className="hover:text-teal-400 transition-colors">Twitter</a>
          <a href="https://linkedin.com/in/alexabell" target="_blank" rel="noopener" className="hover:text-teal-400 transition-colors">LinkedIn</a>
          <a href="https://abellminded.com" target="_blank" rel="noopener" className="hover:text-teal-400 transition-colors">Abellminded</a>
        </div>
      </div>
    </footer>
  )
}

// ─── App ───
export default function App() {
  return (
    <>
      <Navbar />
      <Hero />
      <Problem />
      <HowItWorks />
      <DemoPlayer />
      <UseCases />
      <Waitlist />
      <Footer />
    </>
  )
}
