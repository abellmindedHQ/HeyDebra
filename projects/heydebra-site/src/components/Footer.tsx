import { motion } from 'framer-motion'

export function Footer() {
  return (
    <footer className="relative py-20 px-4 border-t border-dark-border overflow-hidden bg-dark-surface">
      {/* Background */}
      <div className="absolute inset-0 grid-bg opacity-20 pointer-events-none" />
      <div className="absolute inset-0 pointer-events-none"
        style={{ background: 'radial-gradient(ellipse at 50% 0%, rgba(255,0,110,0.06) 0%, transparent 60%)' }} />

      <div className="max-w-5xl mx-auto">
        {/* Main footer content */}
        <div className="flex flex-col items-center text-center gap-8">
          {/* Logo */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
          >
            <div className="font-display text-6xl text-gradient-pink glow-pink mb-2">HEYDEBRA</div>
            <p className="text-white/60 text-sm">The AI executive assistant who runs the damn show.</p>
          </motion.div>

          {/* Links */}
          <motion.nav
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, delay: 0.2 }}
            aria-label="Footer links"
            className="flex flex-wrap justify-center gap-6 text-sm"
          >
            <a href="https://github.com/abellmindedHQ/HeyDebra" target="_blank" rel="noopener noreferrer"
              aria-label="View HeyDebra on GitHub (opens in new tab)"
              className="flex items-center gap-2 text-white/50 hover:text-white transition-colors duration-200 focus:outline-none focus-visible:ring-2 focus-visible:ring-white focus-visible:ring-offset-2 focus-visible:ring-offset-dark-surface rounded">
              <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
                <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/>
              </svg>
              GitHub
            </a>
            <a href="https://openclaw.ai" target="_blank" rel="noopener noreferrer"
              aria-label="Visit OpenClaw website (opens in new tab)"
              className="text-white/50 hover:text-teal transition-colors duration-200 focus:outline-none focus-visible:ring-2 focus-visible:ring-teal focus-visible:ring-offset-2 focus-visible:ring-offset-dark-surface rounded">
              OpenClaw
            </a>
            <a href="https://abellminded.com" target="_blank" rel="noopener noreferrer"
              aria-label="Visit Abellminded website (opens in new tab)"
              className="text-white/50 hover:text-gold transition-colors duration-200 focus:outline-none focus-visible:ring-2 focus-visible:ring-gold focus-visible:ring-offset-2 focus-visible:ring-offset-dark-surface rounded">
              Abellminded
            </a>
          </motion.nav>

          {/* Divider */}
          <div className="w-full h-px bg-gradient-to-r from-transparent via-dark-border to-transparent" />

          {/* Signoff */}
          <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, delay: 0.4 }}
            className="space-y-2"
          >
            <p className="text-white/70 italic text-lg">
              "Stay fabulous, sugar. I've got it from here."
            </p>
            <p className="text-white/50 text-xs font-mono">— Debra 💁🏽‍♀️</p>
          </motion.div>

          {/* Built on */}
          <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, delay: 0.5 }}
            className="flex items-center gap-2 text-xs text-white/50 font-mono"
          >
            <span>Built by</span>
            <a href="https://abellminded.com" target="_blank" rel="noopener noreferrer"
              className="text-white/60 hover:text-gold transition-colors duration-200">
              Alex Abell / Abellminded
            </a>
            <span>•</span>
            <span>Powered by</span>
            <a href="https://openclaw.ai" target="_blank" rel="noopener noreferrer"
              className="text-white/60 hover:text-teal transition-colors duration-200">
              OpenClaw
            </a>
          </motion.div>
        </div>
      </div>
    </footer>
  )
}
