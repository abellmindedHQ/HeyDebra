import { useState, useEffect } from 'react'

export function useTypewriter(texts: string[], speed = 60, pause = 2000) {
  const prefersReducedMotion = typeof window !== 'undefined'
    ? window.matchMedia('(prefers-reduced-motion: reduce)').matches
    : false

  const [displayText, setDisplayText] = useState(prefersReducedMotion ? texts[0] : '')
  const [textIndex, setTextIndex] = useState(0)
  const [charIndex, setCharIndex] = useState(prefersReducedMotion ? texts[0]?.length ?? 0 : 0)
  const [isDeleting, setIsDeleting] = useState(false)

  useEffect(() => {
    // If reduced motion, just show first text statically
    if (prefersReducedMotion) return

    const currentText = texts[textIndex]

    const timeout = setTimeout(() => {
      if (!isDeleting) {
        if (charIndex < currentText.length) {
          setDisplayText(currentText.slice(0, charIndex + 1))
          setCharIndex(c => c + 1)
        } else {
          // Pause at end of word
          setTimeout(() => setIsDeleting(true), pause)
        }
      } else {
        if (charIndex > 0) {
          setDisplayText(currentText.slice(0, charIndex - 1))
          setCharIndex(c => c - 1)
        } else {
          setIsDeleting(false)
          setTextIndex(i => (i + 1) % texts.length)
        }
      }
    }, isDeleting ? speed / 2 : speed)

    return () => clearTimeout(timeout)
  }, [charIndex, isDeleting, textIndex, texts, speed, pause])

  return displayText
}
