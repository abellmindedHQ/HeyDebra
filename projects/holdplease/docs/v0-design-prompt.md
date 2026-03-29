# HoldPlease v0 Design Prompt

## Copy this into v0.dev

---

Design a complete web app UI for **HoldPlease** — a feature of an AI companion named Debra. HoldPlease lets your AI assistant make phone calls on your behalf: navigating IVR menus, waiting on hold, having conversations with customer service reps, and delivering transcripts + highlights when done.

## Brand Context

HoldPlease is NOT a generic SaaS tool. It's part of **Debra** — a retro-futuristic AI executive assistant with 70s power secretary energy. Think: warm, confident, no-nonsense, unapologetically fabulous. She has a voice, opinions, and a personality. The UI should feel like watching Debra work, not like using a tool.

**Brand parent:** Abellminded
**Color palette:** Dark mode primary. Rich blacks (#0a0a0a, #111), warm ambers/golds for accents, slate grays for secondary text. NOT cold/corporate blue. Think warm, confident, slightly retro-luxe.
**Typography:** Clean, modern, slightly bold. Not playful, not corporate. Confident.
**Personality in UI:** Debra's voice should come through in microcopy, empty states, and status messages. She's witty and direct. "No issues yet. Give me someone to call." not "Create your first issue to get started."

## Pages Needed

### 1. Landing Page (/)
- Hero: bold headline about never waiting on hold again
- Subtext: Debra handles the call. You get the highlights.
- CTA: "Let Debra handle it" / "Sign in"
- Social proof section: stats (900M hours Americans spend on hold/year, average 43 min wait)
- How it works: 3 steps (1. Tell Debra the issue, 2. She calls and handles it, 3. You get the transcript + outcome)
- Feature cards: hold detection, smart conversation, full transcript, IVR navigation, conference handoff
- Footer with Abellminded branding

### 2. Login Page (/login)
- Google OAuth button (use the PROPER Google branded button with the "G" logo and "Sign in with Google" text in the official Google style — white background, dark text, Google colors on the G)
- Email/password as secondary option
- Dark theme consistent with landing
- Debra personality in the copy

### 3. Registration Page (/register)  
- Same Google OAuth branded button
- Name, email, password fields
- Link to login

### 4. Dashboard (/dashboard)
- Sidebar navigation (dark, minimal): Dashboard, Issues, Analytics, Settings
- Debra's avatar/icon in sidebar header
- Stats cards: Total Issues, Hold Time Saved, Total Cost, Value Recovered (with ROI)
- Recent issues list with status badges (active/calling/on-hold/resolved/failed)
- "New Issue" CTA button
- Empty state with Debra personality: "Nothing here yet. Give me a company to call and watch me work."

### 5. New Issue Page (/dashboard/issues/new)
- Form: Company name, phone number (optional — Debra can look it up), description of the issue
- "Context" section: paste email threads, reference numbers, previous call notes
- "How aggressive should Debra be?" slider (polite → firm → nuclear)
- Preview of what Debra will say
- "Let Debra call" CTA

### 6. Issue Detail Page (/dashboard/issues/[id])
- Issue header: company, status, created date
- Call history timeline (each call attempt with duration, outcome, cost)
- Live call status when active: animated waveform/pulse showing Debra is on the phone
- Transcript viewer (collapsible, with AI-highlighted key moments)
- Highlights section: extracted commitments, promises, reference numbers
- Action items: what was agreed, follow-up dates
- Cost breakdown per call
- "Call again" / "Escalate" buttons

### 7. Active Call View (/dashboard/issues/[id]/call)
- FULL SCREEN dark view
- Large animated visualization (audio waveform or abstract pulse) showing call is active
- Status: "Navigating IVR..." → "On hold (12:34)" → "Speaking with representative" → "Call complete"
- Real-time transcript streaming (like subtitles)
- "Join call" button (conference bridge — patches user in)
- "End call" button
- Debra's avatar with subtle animation when she's "speaking"
- Hold timer counting up
- Company name and phone number displayed

### 8. Analytics Page (/dashboard/analytics)
- Time saved chart (bar chart by month)
- Cost per call trends
- Resolution rate
- Company leaderboard (hardest companies to deal with, avg hold times)
- Total ROI calculator

### 9. Settings Page (/dashboard/settings)
- Profile (name, email, avatar)
- Phone preferences (callback number, timezone)
- Debra personality settings (communication style, aggression level default)
- Connected accounts
- Billing/subscription

## Technical Stack
- Next.js 15+ with App Router
- TypeScript
- Tailwind CSS
- shadcn/ui components
- Lucide icons
- Framer Motion for animations (especially the active call view)

## Design Principles
1. **Dark and warm** — not cold corporate dark mode. Warm blacks, amber accents.
2. **Debra's personality everywhere** — microcopy, empty states, loading states, error messages should all sound like her.
3. **The call view is the hero** — when a call is active, it should feel cinematic. Like watching your assistant work in real-time.
4. **Data-rich but not cluttered** — show ROI, time saved, transcripts, highlights. But breathe.
5. **Mobile-first** — people will check call status from their phone.
6. **Proper OAuth buttons** — Google sign-in button must follow Google's brand guidelines (white bg, multicolor G, "Sign in with Google" text).

## Microcopy Examples
- Empty dashboard: "No calls yet. Tell me who's giving you trouble."
- On hold status: "On hold with Delta. 23 minutes and counting. Their hold music is terrible."  
- Call complete: "Done. Got a reference number and they agreed to a $550 refund. Full transcript below."
- Error state: "Call dropped. Their phone system is a mess. Want me to try again?"
- Loading: "Dialing in..."
