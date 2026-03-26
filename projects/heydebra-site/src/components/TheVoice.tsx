import { useState, useRef } from 'react'
import { motion } from 'framer-motion'
import { useScrollReveal } from '../hooks/useScrollReveal'

const quotes = [
  { text: "Sugar, I already handled it.", context: "When Alex worries about something she's already done" },
  { text: "That's a bad idea, hon. But I love you, so let me explain why.", context: "When something needs gentle pushback" },
  { text: "lol ignore that last one from Alex, he forgot which chat he was in 😂", context: "Covering for an accidental message" },
  { text: "Baby, you saved $92.60. You're welcome.", context: "After finding a better prescription price" },
  { text: "I found flights $900 cheaper. You can thank me later.", context: "After optimizing a travel booking" },
]

export function TheVoice() {
  const { ref, isVisible } = useScrollReveal()
  const [activeQuote, setActiveQuote] = useState(0)
  const [isPlaying, setIsPlaying] = useState(false)
  const audioRef = useRef<HTMLAudioElement | null>(null)

  const handlePlay = () => {
    if (!audioRef.current) {
      audioRef.current = new Audio('/debra-intro.mp3')
      audioRef.current.addEventListener('ended', () => setIsPlaying(false))
      audioRef.current.addEventListener('pause', () => setIsPlaying(false))
    }
    if (isPlaying) {
      audioRef.current.pause()
      audioRef.current.currentTime = 0
      setIsPlaying(false)
    } else {
      audioRef.current.play()
      setIsPlaying(true)
    }
  }

  return (
    <section id="the-voice" className="relative py-32 px-4 overflow-hidden">
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-hot-pink/40 to-transparent" />
        <div className="absolute inset-0"
          style={{ background: 'radial-gradient(ellipse at 70% 50%, rgba(255,0,110,0.06) 0%, transparent 60%)' }} />
      </div>

      <div ref={ref} className="max-w-5xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={isVisible ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.7 }}
          className="text-center mb-16"
        >
          <span className="text-xs font-mono text-hot-pink tracking-widest uppercase">ElevenLabs Custom Voice</span>
          <h2 className="font-display text-[clamp(3rem,8vw,7rem)] leading-none mt-2 text-white">
            THE <span className="text-gradient-pink">VOICE</span>
          </h2>
          <p className="mt-4 text-white/70 text-lg max-w-xl mx-auto">
            She doesn't just send text messages. She sends voice memos. A real, custom-trained voice — warm, confident, unmistakably Debra.
          </p>
        </motion.div>

        <div className="grid md:grid-cols-2 gap-10 items-start">
          {/* Left: Audio player mockup + voice traits */}
          <motion.div
            initial={{ opacity: 0, x: -30 }}
            animate={isVisible ? { opacity: 1, x: 0 } : {}}
            transition={{ duration: 0.7, delay: 0.2 }}
          >
            {/* Audio player */}
            <div className="rounded-2xl border border-hot-pink/30 bg-dark-card p-6 mb-6 relative overflow-hidden">
              <div className="absolute inset-0 bg-gradient-to-br from-hot-pink/5 to-transparent pointer-events-none" />

              <div className="flex items-center gap-4 mb-5">
                <div className="w-12 h-12 rounded-full bg-hot-pink flex items-center justify-center flex-shrink-0"
                  style={{ boxShadow: '0 0 20px rgba(255,0,110,0.5)' }}>
                  <span className="text-xl">💁🏽‍♀️</span>
                </div>
                <div>
                  <div className="font-semibold text-white">Debra</div>
                  <div className="text-xs text-white/60">Custom ElevenLabs Voice</div>
                </div>
                <div className="ml-auto">
                  <span className="text-xs text-green-400 font-mono">● LIVE</span>
                </div>
              </div>

              {/* Waveform visualization */}
              <div className="flex items-center gap-1 mb-4 h-12">
                {Array.from({ length: 40 }).map((_, i) => (
                  <motion.div
                    key={i}
                    className="w-1 rounded-full flex-shrink-0"
                    style={{ background: isPlaying ? '#FF006E' : '#FF006E66' }}
                    animate={isPlaying ? {
                      height: [
                        `${8 + Math.sin(i * 0.5) * 20 + 10}px`,
                        `${8 + Math.sin(i * 0.5 + 1) * 20 + 10}px`,
                        `${8 + Math.sin(i * 0.5) * 20 + 10}px`,
                      ],
                    } : {
                      height: `${4 + Math.sin(i * 0.8) * 8 + 4}px`,
                    }}
                    transition={{
                      duration: 0.4,
                      repeat: isPlaying ? Infinity : 0,
                      delay: i * 0.02,
                    }}
                  />
                ))}
              </div>

              <div className="flex items-center gap-4">
                <button
                  onClick={handlePlay}
                  aria-label={isPlaying ? 'Playing Debra voice sample' : 'Play Debra voice sample'}
                  aria-pressed={isPlaying}
                  className="flex items-center gap-2 px-5 py-2.5 rounded-full bg-hot-pink hover:bg-fuchsia transition-colors duration-200 font-medium text-sm focus:outline-none focus-visible:ring-2 focus-visible:ring-white focus-visible:ring-offset-2 focus-visible:ring-offset-dark-card"
                  style={{ boxShadow: '0 0 20px rgba(255,0,110,0.3)' }}
                >
                  {isPlaying ? (
                    <>
                      <span className="w-3 h-3 border-2 border-white rounded-sm" aria-hidden="true" />
                      Playing...
                    </>
                  ) : (
                    <>
                      <span className="w-0 h-0 border-l-[10px] border-l-white border-t-[6px] border-t-transparent border-b-[6px] border-b-transparent" aria-hidden="true" />
                      Hear Debra
                    </>
                  )}
                </button>
                <span className="text-white/50 text-xs font-mono">sample voice memo</span>
              </div>
            </div>

            {/* Voice traits */}
            <div className="space-y-3">
              {[
                { trait: "Calls people 'sugar', 'baby', 'hon'", note: "naturally, never forced" },
                { trait: "Keeps it real", note: "if it's a bad idea, she says so — with love" },
                { trait: "Matches the energy", note: "chill when it's chill, hype when it's hype" },
                { trait: "Dry wit on demand", note: "never corny, always earned" },
              ].map((item, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, x: -10 }}
                  animate={isVisible ? { opacity: 1, x: 0 } : {}}
                  transition={{ delay: 0.4 + i * 0.1 }}
                  className="flex items-center justify-between p-3 rounded-lg border border-dark-border bg-dark-card/50"
                >
                  <span className="text-white/80 text-sm font-medium">{item.trait}</span>
                  <span className="text-white/50 text-xs italic ml-4">{item.note}</span>
                </motion.div>
              ))}
            </div>
          </motion.div>

          {/* Right: Quote carousel */}
          <motion.div
            initial={{ opacity: 0, x: 30 }}
            animate={isVisible ? { opacity: 1, x: 0 } : {}}
            transition={{ duration: 0.7, delay: 0.3 }}
          >
            <div className="mb-4">
              <span className="text-xs font-mono text-white/50 uppercase tracking-widest">Things she's actually said</span>
            </div>

            <div className="space-y-3">
              {quotes.map((quote, i) => (
                <motion.button
                  key={i}
                  onClick={() => setActiveQuote(i)}
                  whileHover={{ scale: 1.01 }}
                  whileTap={{ scale: 0.99 }}
                  aria-pressed={activeQuote === i}
                  aria-label={`Quote ${i + 1}: ${quote.text}`}
                  className={`w-full text-left p-5 rounded-xl border transition-all duration-300 focus:outline-none focus-visible:ring-2 focus-visible:ring-hot-pink focus-visible:ring-offset-2 focus-visible:ring-offset-deep-black ${
                    activeQuote === i
                      ? 'border-hot-pink/40 bg-hot-pink/8'
                      : 'border-dark-border bg-dark-card/40 hover:border-white/20'
                  }`}
                >
                  <p className={`font-medium mb-2 transition-colors duration-200 ${
                    activeQuote === i ? 'text-white' : 'text-white/60'
                  }`}>
                    "{quote.text}"
                  </p>
                  <p className="text-xs text-white/50 italic">{quote.context}</p>
                </motion.button>
              ))}
            </div>

            {/* ElevenLabs credit */}
            <div className="mt-8 flex items-center gap-3 p-4 rounded-lg border border-teal/20 bg-teal/5">
              <div className="w-8 h-8 rounded bg-teal/20 flex items-center justify-center">
                <span className="text-lg">🎙️</span>
              </div>
              <div>
                <div className="text-xs text-teal/80 uppercase tracking-wider">Voice engine</div>
                <div className="text-teal font-semibold text-sm">ElevenLabs — Custom trained model</div>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  )
}
