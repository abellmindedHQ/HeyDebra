# HeyDebra — Landing Page

> She doesn't just assist. She runs the damn show.

A retro-futuristic, nightclub-energy landing page for Debra — the AI executive assistant built on OpenClaw.

## Stack

- **React 18** + **Vite 5** + **TypeScript**
- **Tailwind CSS** for styling
- **Framer Motion** for animations
- Deployed on **Vercel**

## Features

- 🌟 Full-screen hero with animated typewriter effect
- 🎨 Deep black / hot pink / gold / teal color palette
- ✨ Canvas particle system (background floating dots in brand colors)
- 📱 Mobile-first responsive design
- 🔀 Interactive tab-based "What She Does" section with 5 categories
- 🎙️ Voice section with animated waveform player mockup
- 🔧 Stack grid with tier grouping
- 🧭 Sticky navbar with smooth scroll
- 🔆 Scroll-reveal animations throughout
- ⚡ Corner decorations + scanline effects for retro-futuristic vibe

## Dev

```bash
npm install
npm run dev       # http://localhost:5173
npm run build     # production build to /dist
npm run preview   # preview production build
```

## Deploy to Vercel

```bash
npx vercel
```

Or connect the GitHub repo and Vercel auto-deploys on push.

## Structure

```
src/
  components/
    Navbar.tsx         # sticky nav with smooth scroll
    Hero.tsx           # big hero with typewriter
    WhatIsDebra.tsx    # description + stats
    WhatSheDoes.tsx    # tabbed real examples
    TheVoice.tsx       # voice section with waveform mockup
    TheStack.tsx       # tech stack grid
    BuiltBy.tsx        # Abellminded section
    Footer.tsx         # signoff
    Particles.tsx      # canvas particle system
  hooks/
    useTypewriter.ts   # typewriter hook
    useScrollReveal.ts # intersection observer hook
  App.tsx
  index.css            # Tailwind + custom CSS
```

---

Built by [Abellminded](https://abellminded.com) · Powered by [OpenClaw](https://openclaw.ai)
