# v0 Prompt: Hannah Aldridge Music Studio Platform

## Paste this into v0.dev:

---

Build a complete music lesson studio platform for "Hannah Aldridge Music Studio" — a private music instruction business in Knoxville, TN run by touring musician Hannah Aldridge.

**Design:** Dark, elegant, warm. Think high-end music studio meets boutique wellness. Color palette: deep black (#0d0d0d), warm cream (#e8e4df), gold accent (#c9a96e), muted brown (#8a8278). Use Cormorant Garamond for headings, Inter for body. No corporate vibes. Musician energy.

**Pages needed:**

### 1. Landing Page
- Hero with name, tagline "Learn from a working, touring musician", and Book Now CTA
- "The Approach" section: honest, confident, grounded teaching philosophy
- Services: Guitar, Piano, Voice, Performance Coaching — each with icon and brief description
- "Who This Is For" — 3 cards: Adult Beginners, Vocalists, Performing Artists
- Pricing: 3 tiers (30/45/60 min) with single lesson and monthly package prices
- Testimonials section (placeholder)
- About Hannah: bio section with photo placeholder, Muscle Shoals heritage, touring credentials, MTSU Music Business degree
- Footer with contact, social links, location (Rush's Music, Knoxville TN)

### 2. Booking System
- Calendar view showing available lesson slots (Mon-Thu afternoons/evenings)
- Lesson type selector (Guitar/Piano/Voice/Performance)
- Duration selector (30/45/60 min)
- New student intake form (name, email, phone, experience level, goals, any vocal concerns)
- Returning student quick-book flow
- Stripe checkout integration for single lessons
- Monthly subscription signup with recurring billing
- Confirmation page with calendar invite download (.ics)
- Email confirmation with lesson details and studio address

### 3. Student Dashboard
- Upcoming lessons with reschedule/cancel options
- Lesson history with notes from instructor
- Payment history and receipts
- Monthly subscription management (upgrade/downgrade/cancel)
- Practice log (student can track what they worked on)
- Resources section (shared files, sheet music, recordings from lessons)

### 4. Instructor Dashboard (Hannah)
- Daily/weekly schedule view with all booked lessons
- Student roster with contact info and lesson history
- Lesson notes — add notes after each session (what was covered, homework, progress)
- Revenue tracking: daily/weekly/monthly income, subscription vs single lesson breakdown
- Cancellation and reschedule management
- Waitlist for full slots
- Quick actions: send reminder, share resource, reschedule

### 5. Lesson Planning
- Template library for common lesson structures
- Per-student lesson plan (what to cover next, goals, notes)
- Progress tracking per student (skills checklist)
- Shareable practice assignments

### 6. Notifications & Reminders
- Automated email reminders (24h and 1h before lesson)
- SMS reminders via Twilio (optional)
- New booking notifications
- Payment reminders for overdue invoices
- Cancellation notifications

**Tech stack:** Next.js 14+ App Router, Tailwind CSS, shadcn/ui components, Prisma ORM, PostgreSQL (Supabase or Neon), Stripe for payments, NextAuth for authentication, Resend for email.

**Key features:**
- Mobile-first responsive design
- Stripe subscriptions for monthly packages
- Google Calendar integration (sync lessons)
- Student self-service (book, reschedule, cancel)
- Instructor can block off times, set recurring availability
- Cancellation policy: 24h notice required, configurable

**Tone:** Professional but not corporate. Warm but not cutesy. Music studio, not SaaS dashboard.
