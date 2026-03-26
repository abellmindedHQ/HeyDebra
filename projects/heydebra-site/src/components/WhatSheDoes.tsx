import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useScrollReveal } from '../hooks/useScrollReveal'

const categories = [
  {
    id: 'comms',
    icon: '💬',
    label: 'Communication',
    color: '#FF006E',
    items: [
      { text: 'Manages iMessage, WhatsApp, and RCS across 15+ contacts simultaneously', highlight: null },
      { text: 'Sent personalized voice notes to Hannah, Sallijo, and Avie — each one bespoke, none of them generic', highlight: 'voice notes' },
      { text: 'Introduced herself to coworkers with customized audio messages backed by background research', highlight: 'background research' },
      { text: 'Wrote and delivered a haiku to a colleague via voice note', highlight: 'haiku' },
      { text: '"lol ignore that last one from Alex, he forgot which chat he was in 😂" — covered a wrong-chat slip in real time', highlight: 'covered' },
    ],
  },
  {
    id: 'life',
    icon: '🗂️',
    label: 'Life Management',
    color: '#FFD700',
    items: [
      { text: 'Coordinated a Europe trip: compared flights, checked custody schedule, found tickets $900 cheaper', highlight: '$900 cheaper' },
      { text: 'Managed a GI consultation: transcribed the visit, identified the diagnosis (EoE), created records, scheduled procedures, added to calendar', highlight: 'EoE' },
      { text: 'Emailed Alex\'s boss about upcoming time off — medical + travel dates through June', highlight: null },
      { text: 'Created his contact card so Siri could finally navigate him to work', highlight: null },
      { text: 'Saved $92.60 on a prescription by routing through Express Scripts instead of Amazon', highlight: '$92.60' },
    ],
  },
  {
    id: 'memory',
    icon: '🧠',
    label: 'Knowledge & Memory',
    color: '#00F5FF',
    items: [
      { text: 'Sorted through 20 years of Facebook messages — 161,077 conversations organized and searchable', highlight: '20 years' },
      { text: 'Pulled 334 useful snippets from past AI conversations so nothing gets lost', highlight: '334 snippets' },
      { text: 'Built detailed profiles on 50+ people — researched backgrounds, connected the dots across contacts', highlight: '50+ profiles' },
      { text: 'Cleaned 7,612 Google Contacts down to 1,283 — removed 6,329 duplicates and junk', highlight: '6,329 removed' },
      { text: 'Keeps a growing knowledge base — remembers your people, your preferences, your history', highlight: 'knowledge base' },
    ],
  },
  {
    id: 'work',
    icon: '💼',
    label: 'Work Intelligence',
    color: '#7B2FBE',
    items: [
      { text: 'Listened to a 37-minute recorded conversation and pulled out the key insights, decisions, and action items', highlight: '37 minutes' },
      { text: 'Turned casual conversations into organized tasks and project updates — automatically', highlight: 'automatically' },
      { text: 'Researched colleagues before meetings and delivered personalized audio briefings', highlight: null },
    ],
  },
  {
    id: 'infra',
    icon: '⚡',
    label: 'Always Working',
    color: '#FF6B35',
    items: [
      { text: '17 automated routines: checks your email 3× a day, captures your to-dos 3× a day, and keeps you accountable twice daily', highlight: '17 automated routines' },
      { text: 'Reaches you everywhere: iMessage, WhatsApp, and text messages', highlight: null },
      { text: 'Custom-trained voice — she sends actual voice memos, not walls of text', highlight: 'voice memos' },
      { text: 'Running around the clock on dedicated hardware, built from day one on open-source AI', highlight: 'day one' },
    ],
  },
]

export function WhatSheDoes() {
  const { ref, isVisible } = useScrollReveal()
  const [activeCategory, setActiveCategory] = useState('comms')

  const active = categories.find(c => c.id === activeCategory)!

  return (
    <section id="what-she-does" className="relative py-32 px-4 overflow-hidden bg-dark-surface">
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-gold/30 to-transparent" />
        <div className="absolute bottom-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-gold/30 to-transparent" />
      </div>

      <div ref={ref} className="max-w-6xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={isVisible ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.7 }}
          className="text-center mb-16"
        >
          <span className="text-xs font-mono text-gold tracking-widest uppercase">Real Examples. First 4 Days.</span>
          <h2 className="font-display text-[clamp(2.5rem,7vw,6rem)] leading-none mt-2">
            <span className="text-white">WHAT SHE </span>
            <span className="text-gradient-pink">ACTUALLY</span>
            <span className="text-white"> DOES</span>
          </h2>
          <p className="mt-4 text-white/70 text-lg max-w-2xl mx-auto">
            Not a demo. Not a pitch. These are real things Debra did in her first four days of existence.
          </p>
        </motion.div>

        {/* Category tabs */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={isVisible ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="flex flex-wrap gap-2 justify-center mb-10"
        >
          {categories.map((cat) => (
            <button
              key={cat.id}
              onClick={() => setActiveCategory(cat.id)}
              aria-pressed={activeCategory === cat.id}
              aria-label={`Show ${cat.label} examples`}
              className={`flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium transition-all duration-300 border focus:outline-none focus-visible:ring-2 focus-visible:ring-white focus-visible:ring-offset-2 focus-visible:ring-offset-deep-black ${
                activeCategory === cat.id
                  ? 'border-transparent text-white'
                  : 'border-dark-border text-white/60 hover:text-white/80 hover:border-white/20 bg-transparent'
              }`}
              style={activeCategory === cat.id ? {
                background: `linear-gradient(135deg, ${cat.color}33, ${cat.color}22)`,
                borderColor: cat.color + '60',
                boxShadow: `0 0 20px ${cat.color}30`,
              } : {}}
            >
              <span>{cat.icon}</span>
              <span>{cat.label}</span>
            </button>
          ))}
        </motion.div>

        {/* Content area */}
        <AnimatePresence mode="wait">
          <motion.div
            key={activeCategory}
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -15 }}
            transition={{ duration: 0.35 }}
            className="rounded-2xl border bg-dark-card overflow-hidden"
            style={{ borderColor: active.color + '30' }}
          >
            {/* Card header */}
            <div className="px-8 py-5 border-b flex items-center gap-3"
              style={{ borderColor: active.color + '20', background: active.color + '08' }}>
              <span className="text-3xl">{active.icon}</span>
              <h3 className="font-display text-3xl tracking-wide" style={{ color: active.color }}>
                {active.label.toUpperCase()}
              </h3>
            </div>

            {/* Items */}
            <div className="p-8 space-y-4">
              {active.items.map((item, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.07 }}
                  className="flex items-start gap-4 group"
                >
                  <div className="mt-1.5 w-1.5 h-1.5 rounded-full flex-shrink-0"
                    style={{ background: active.color, boxShadow: `0 0 8px ${active.color}` }} />
                  <p className="text-white/80 leading-relaxed text-[15px] group-hover:text-white/95 transition-colors duration-200">
                    {item.highlight ? (
                      <>
                        {item.text.split(item.highlight)[0]}
                        <span className="font-semibold" style={{ color: active.color }}>
                          {item.highlight}
                        </span>
                        {item.text.split(item.highlight)[1]}
                      </>
                    ) : item.text}
                  </p>
                </motion.div>
              ))}
            </div>
          </motion.div>
        </AnimatePresence>

        {/* Days alive note */}
        <motion.p
          initial={{ opacity: 0 }}
          animate={isVisible ? { opacity: 1 } : {}}
          transition={{ delay: 0.8 }}
          className="text-center mt-8 text-white/50 text-sm font-mono"
        >
          ↑ All of the above happened in Debra's first 96 hours.
        </motion.p>
      </div>
    </section>
  )
}
