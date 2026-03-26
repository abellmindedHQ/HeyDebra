import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'

const navLinks = [
  { label: 'Who Is She', href: '#what-is-debra' },
  { label: 'What She Does', href: '#what-she-does' },
  { label: 'The Voice', href: '#the-voice' },
  { label: 'How It Works', href: '#the-stack' },
]

export function Navbar() {
  const [scrolled, setScrolled] = useState(false)
  const [menuOpen, setMenuOpen] = useState(false)

  useEffect(() => {
    const handler = () => setScrolled(window.scrollY > 40)
    window.addEventListener('scroll', handler)
    return () => window.removeEventListener('scroll', handler)
  }, [])

  const handleNav = (href: string) => {
    setMenuOpen(false)
    document.querySelector(href)?.scrollIntoView({ behavior: 'smooth' })
  }

  return (
    <motion.nav
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, delay: 0.5 }}
      aria-label="Main navigation"
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        scrolled ? 'bg-deep-black/90 backdrop-blur-md border-b border-dark-border' : ''
      }`}
    >
      <div className="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">
        {/* Logo */}
        <button
          onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
          aria-label="HeyDebra — scroll to top"
          className="font-display text-2xl text-gradient-pink focus:outline-none focus-visible:ring-2 focus-visible:ring-hot-pink focus-visible:ring-offset-2 focus-visible:ring-offset-deep-black rounded"
        >
          HEYDEBRA
        </button>

        {/* Desktop nav */}
        <div className="hidden md:flex items-center gap-6" role="list">
          {navLinks.map(link => (
            <button
              key={link.href}
              onClick={() => handleNav(link.href)}
              role="listitem"
              className="text-sm text-white/70 hover:text-white transition-colors duration-200 focus:outline-none focus-visible:ring-2 focus-visible:ring-hot-pink focus-visible:ring-offset-2 focus-visible:ring-offset-deep-black rounded px-1 py-0.5"
            >
              {link.label}
            </button>
          ))}
          <a
            href="https://github.com/abellmindedHQ/HeyDebra"
            target="_blank"
            rel="noopener noreferrer"
            aria-label="View HeyDebra on GitHub (opens in new tab)"
            className="flex items-center gap-2 px-4 py-1.5 rounded-full border border-hot-pink/40 text-hot-pink text-sm hover:bg-hot-pink/10 transition-all duration-200 focus:outline-none focus-visible:ring-2 focus-visible:ring-hot-pink focus-visible:ring-offset-2 focus-visible:ring-offset-deep-black"
          >
            <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
              <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/>
            </svg>
            GitHub
          </a>
        </div>

        {/* Mobile menu button */}
        <button
          className="md:hidden text-white/60 hover:text-white focus:outline-none focus-visible:ring-2 focus-visible:ring-hot-pink focus-visible:ring-offset-2 focus-visible:ring-offset-deep-black rounded p-1"
          onClick={() => setMenuOpen(!menuOpen)}
          aria-expanded={menuOpen}
          aria-controls="mobile-menu"
          aria-label={menuOpen ? 'Close navigation menu' : 'Open navigation menu'}
        >
          <div className="space-y-1.5" aria-hidden="true">
            <span className={`block w-6 h-0.5 bg-current transition-all duration-300 ${menuOpen ? 'rotate-45 translate-y-2' : ''}`} />
            <span className={`block w-6 h-0.5 bg-current transition-all duration-300 ${menuOpen ? 'opacity-0' : ''}`} />
            <span className={`block w-6 h-0.5 bg-current transition-all duration-300 ${menuOpen ? '-rotate-45 -translate-y-2' : ''}`} />
          </div>
        </button>
      </div>

      {/* Mobile menu */}
      {menuOpen && (
        <motion.div
          id="mobile-menu"
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="md:hidden bg-dark-surface/95 backdrop-blur-md border-b border-dark-border px-4 pb-4"
        >
          {navLinks.map(link => (
            <button
              key={link.href}
              onClick={() => handleNav(link.href)}
              className="block w-full text-left py-3 text-white/70 hover:text-white transition-colors duration-200 border-b border-dark-border/50 last:border-0 focus:outline-none focus-visible:ring-2 focus-visible:ring-hot-pink focus-visible:ring-offset-2 focus-visible:ring-offset-dark-surface rounded"
            >
              {link.label}
            </button>
          ))}
        </motion.div>
      )}
    </motion.nav>
  )
}
