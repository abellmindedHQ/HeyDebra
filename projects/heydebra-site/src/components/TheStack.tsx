import { motion } from 'framer-motion'
import { useScrollReveal } from '../hooks/useScrollReveal'

const stackItems = [
  {
    name: 'OpenClaw',
    role: 'The Brain',
    description: 'Open-source AI agent runtime. Debra\'s nervous system.',
    url: 'https://openclaw.ai',
    icon: '🦞',
    color: '#FF006E',
    tier: 'core',
  },
  {
    name: 'ElevenLabs',
    role: 'The Voice',
    description: 'Custom-trained voice model. Real audio, real memos.',
    url: 'https://elevenlabs.io',
    icon: '🎙️',
    color: '#FFD700',
    tier: 'core',
  },
  {
    name: 'Neo4j',
    role: 'Knowledge Graph',
    description: 'Graph database for people, relationships, and memory.',
    url: 'https://neo4j.com',
    icon: '🕸️',
    color: '#00F5FF',
    tier: 'core',
  },
  {
    name: 'BlueBubbles',
    role: 'iMessage Bridge',
    description: 'Routes Apple Messages to and from Debra\'s stack.',
    url: 'https://bluebubbles.app',
    icon: '💬',
    color: '#5AC8FA',
    tier: 'channel',
  },
  {
    name: 'WhatsApp',
    role: 'Messaging',
    description: 'Global messaging. Full send and receive.',
    icon: '📱',
    color: '#25D366',
    tier: 'channel',
  },
  {
    name: 'Google Messages',
    role: 'RCS / SMS',
    description: 'RCS-enabled messaging via Android device.',
    icon: '💭',
    color: '#4285F4',
    tier: 'channel',
  },
  {
    name: 'Obsidian',
    role: 'Second Brain',
    description: 'Note-taking and knowledge base. The human-readable layer.',
    icon: '🔮',
    color: '#7B2FBE',
    tier: 'memory',
  },
  {
    name: 'Linear',
    role: 'Project Management',
    description: 'Issues, sprints, and action items — created in real time.',
    url: 'https://linear.app',
    icon: '📋',
    color: '#5E6AD2',
    tier: 'work',
  },
  {
    name: 'Google Workspace',
    role: 'Email / Calendar / Drive',
    description: 'Full Gmail, Calendar, Contacts, and Drive integration.',
    icon: '🗂️',
    color: '#EA4335',
    tier: 'work',
  },
]

const tierLabels: Record<string, string> = {
  core: 'Core Infrastructure',
  channel: 'Messaging Channels',
  memory: 'Memory & Knowledge',
  work: 'Work & Productivity',
}

const tierOrder = ['core', 'channel', 'memory', 'work']

export function TheStack() {
  const { ref, isVisible } = useScrollReveal()

  const grouped = tierOrder.map(tier => ({
    tier,
    label: tierLabels[tier],
    items: stackItems.filter(i => i.tier === tier),
  }))

  return (
    <section id="the-stack" className="relative py-32 px-4 overflow-hidden bg-dark-surface">
      <div className="absolute inset-0 pointer-events-none grid-bg opacity-30" />
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-teal/30 to-transparent" />
        <div className="absolute bottom-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-teal/30 to-transparent" />
      </div>

      <div ref={ref} className="max-w-6xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={isVisible ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.7 }}
          className="text-center mb-20"
        >
          <span className="text-xs font-mono text-teal tracking-widest uppercase">How she works</span>
          <h2 className="font-display text-[clamp(3rem,8vw,7rem)] leading-none mt-2">
            <span className="text-gradient-teal">THE STACK</span>
          </h2>
          <p className="mt-4 text-white/50 text-lg max-w-xl mx-auto">
            Nine tools, one brain, zero excuses.
          </p>
        </motion.div>

        {/* Center node */}
        <motion.div
          initial={{ opacity: 0, scale: 0.5 }}
          animate={isVisible ? { opacity: 1, scale: 1 } : {}}
          transition={{ duration: 0.8, delay: 0.2, type: 'spring' }}
          className="flex justify-center mb-16"
        >
          <div className="relative">
            {/* Pulse rings */}
            <div className="absolute inset-0 rounded-full animate-pulse-ring"
              style={{ background: 'rgba(255, 0, 110, 0.15)' }} />
            <div className="absolute inset-0 rounded-full animate-pulse-ring"
              style={{ background: 'rgba(255, 0, 110, 0.08)', animationDelay: '0.5s' }} />

            <div className="relative w-28 h-28 rounded-full border-2 border-hot-pink bg-dark-card flex flex-col items-center justify-center"
              style={{ boxShadow: '0 0 40px rgba(255,0,110,0.4), inset 0 0 30px rgba(255,0,110,0.05)' }}>
              <span className="text-4xl">💁🏽‍♀️</span>
              <span className="text-xs font-mono text-hot-pink mt-1 tracking-wider">DEBRA</span>
            </div>
          </div>
        </motion.div>

        {/* Stack tiers */}
        <div className="space-y-10">
          {grouped.map((group, gi) => (
            <motion.div
              key={group.tier}
              initial={{ opacity: 0, y: 20 }}
              animate={isVisible ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.6, delay: 0.3 + gi * 0.1 }}
            >
              <div className="flex items-center gap-4 mb-4">
                <div className="h-px flex-1 bg-dark-border" />
                <span className="text-xs font-mono text-white/30 uppercase tracking-widest whitespace-nowrap">
                  {group.label}
                </span>
                <div className="h-px flex-1 bg-dark-border" />
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
                {group.items.map((item, i) => (
                  <motion.div
                    key={item.name}
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={isVisible ? { opacity: 1, scale: 1 } : {}}
                    transition={{ duration: 0.4, delay: 0.4 + gi * 0.1 + i * 0.08 }}
                    whileHover={{ scale: 1.03, y: -2 }}
                    className="relative group"
                  >
                    {item.url ? (
                      <a href={item.url} target="_blank" rel="noopener noreferrer" className="block">
                        <StackCard item={item} />
                      </a>
                    ) : (
                      <StackCard item={item} />
                    )}
                  </motion.div>
                ))}
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}

function StackCard({ item }: { item: typeof stackItems[0] }) {
  return (
    <div
      className="p-4 rounded-xl border bg-dark-card transition-all duration-300 h-full"
      style={{
        borderColor: item.color + '25',
      }}
    >
      <div className="flex items-start gap-3">
        <div className="w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0 text-xl"
          style={{ background: item.color + '20' }}>
          {item.icon}
        </div>
        <div className="min-w-0">
          <div className="font-semibold text-white text-sm truncate">{item.name}</div>
          <div className="text-xs font-mono mt-0.5" style={{ color: item.color }}>{item.role}</div>
        </div>
      </div>
      <p className="mt-3 text-xs text-white/40 leading-relaxed">{item.description}</p>
    </div>
  )
}
