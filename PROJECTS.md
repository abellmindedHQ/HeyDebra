# 📋 PROJECTS

Active and someday/maybe projects. GTD style.

## 🔥 Active (has a next action, happening now)

### Second Brain Pipeline v3
- 8-stream capture system architecture designed
- Neo4j graph database running with schema
- Obsidian vault at /Users/debra/SecondBrain/
- ChatGPT export processed (139 convos, Night Swimming Day 1)
- Claude personal export processed (135 convos, Day 3)
- Claude ORNL export processed (316 convos, Day 3)
- Instagram processed (711 DMs, 1525 following, Day 3)
- Facebook processed (6007 convos, 161K messages, 20 years, Day 3)
- 334 artifacts extracted from Claude exports
- Weaver v2 built and run (1,255 wikilinks, 22 concept cards)
- **Next**: Process LinkedIn full export, iMazing text capture, set up Monarch/YNAB APIs

### LinkedIn Inbox Cleanup (Manual)
- 52 spam/noise threads archived via browser automation (Mar 27-28 late night session)
- 18 real conversations kept (see memory/2026-03-28.md for full list)
- Cleaned through Jul 2025. Older messages (pre-Jul 2025) still need review.
- Using openclaw managed browser profile, target ID: 9F3AE192EC7919605F65D11818930DF3
- Pending replies: Angelo Nappi (Mar 23), Tom Harper (Mar 10), William Schilling (Feb 5), Cledon Pancham (Nov '25), Matthew Bruce (Oct '25), Mitch Lee (Dec '25), Michael Dimmitt (Jan '26)
- **Next**: Resume cleanup from Jun 2025 and older in next session. Draft replies to key contacts.

### Cognitive Memory Architecture
- active-context.md created (hippocampus pattern)
- Session memory indexing enabled
- Temporal decay + MMR + hybrid search configured
- Pre-compaction memory flush enabled
- **Next**: Monitor and iterate. Ensure memory bridges sessions consistently.

### People Intelligence Pipeline
- people-intel skill built with auto-watch behavior
- 94 active People profiles (30 new from Facebook Day 3)
- 240 LinkedIn noise archived to _archived/
- Dedup checker built and running clean
- Google Contacts purged: 7,612 → 1,283
- **Next**: Finish contact sync to drdebrapepper, cross-ref Instagram mutuals

### Automation Suite (17 Cron Jobs)
- Email GTD: 7am, 12pm, 6pm daily
- Capture Agent: 7:30am, 2pm, 8pm daily
- GSD Agent: 8am, 3pm daily
- LinkedIn Cleanup: 10am daily
- Night Swimming: Sunday 9-10:30pm
- Weaver: Sunday 11pm
- Memory Flush: 3:30am x2
- **Next**: Monitor first full day of crons, verify all working

### Multi-Channel Messaging
- iMessage (BlueBubbles): LIVE ✅
- WhatsApp (+18652870278): LIVE ✅
- RCS/SMS (Google Messages): LIVE ✅ (send working, inbound observer needs verification)
- **Next**: Verify SMS observer inbound, set up as persistent service

### Android/RCS Messaging
- Google Messages skill reviewed and approved (safe to install)
- WhatsApp also an option
- **Next**: Set up Google Messages (need Alex's Android phone for QR pairing) or WhatsApp

### Consulting Business Launch (abellminded.com)
- Concept doc: /Users/debra/.openclaw/workspace/projects/abellminded/consulting-concept.md
- Positioning: "You already have the superpower. I find it. Technology amplifies it."
- 3-tier offer: Superpower Session ($500) → Amplify Retainer ($3k/mo) → Embedded Transformation ($8-15k/mo)
- 90-day plan: 5 sessions at $250 for testimonials first
- abellminded.com redesigned with D3 brain map, deployed to Vercel ✅
- HeyDebra OG image + twitter card generated + deployed ✅
- **BLOCKER**: ORNL IP/COI resolution required before taking paying clients
  - Must read ORNL employment agreement re: IP assignment
  - Must consult lawyer about IP carve-out
  - Innovation Crossroads at ORNL may be path to fund startup
- **Next**: Build /consulting page, resolve ORNL IP question

### abellminded.com Site Architecture
- Brain map hero (D3.js force-directed, 7 nodes) live on Vercel ✅
- Planned pages: /products, /consulting, /work, /writing, /about
- Local: /Users/debra/.openclaw/workspace/projects/abellminded/
- **Next**: Build /consulting page

## 📅 Planned (committed but not started)

### Google Drive Reorganization
- Audit complete (310 files cataloged, duplicates identified)
- Recommended folder structure documented
- **Blocked**: Needs Alex's approval before moving files

### Night Swimming v2
- Email GTD, Drive Audit, Contact Triage, ChatGPT processing all working
- **Next**: Add LinkedIn processing, Facebook processing when exports arrive
- Consider adding more streams as data sources come online

### WhatsApp Channel Setup
- Researched, production-ready in OpenClaw
- **Next**: Alex scans QR code to link WhatsApp

## 💭 Someday/Maybe (want to do, no commitment yet)

### LiveJournal Account Recovery
- Username: slim (created ~2001, age 15)
- Emails: somatic@loveable.com or invisible_pants@hotmail.com (no access to either)
- Could try recovering Hotmail account through Microsoft first
- Support ticket draft ready in memory
- Would be amazing to get those old posts into SecondBrain

### SMS Bouncer / Text Message Triage
- Filter spam texts, extract actionable info (appointments, deliveries, 2FA)
- Needs iMazing or similar on Mac mini to access SMS stream
- Design as capture stream with filter/triage, not raw dump

### Debra Avatar / Video Presence
- Tavus/Simli/HeyGen research done (from day 1)
- Would give Debra a visual presence in video calls

### Voice Memo Fix
- asVoice:true not working in iMessage (sends audio but won't play as voice bubble)
- Tried MP3, CAF, various codecs. On backlog.

### Suno Integration
- Alex wants Debra to be able to generate music directly
- Currently manual (Alex generates in Suno, sends to Debra)
- Would need Suno API access or browser automation

### iMazing SMS Capture Stream
- Would give Debra access to all SMS/iMessage history on phone
- Needs careful design to filter noise vs signal

### Tailscale Remote Access
- Not yet set up
- Would allow Debra to be accessed from outside home network

### Contacts Cleanup / Personal CRM
- Pipedrive CRM contacts from Lunchpool merged with personal contacts
- Tried Dex as personal CRM, didn't stick
- Autofill pulls random prospects instead of own email
- Want: clean contacts, birthday reminders, nudges to call/text friends/family
- Could be built into SecondBrain or use Dex

### Abellminded.com — Living Brain Map
- NOT a consulting website. Real-time public visualization of Alex's mind
- Interactive graph view showing topics, projects, concepts, connections
- Easter egg: clicking "mind" in "abellminded" goes to live graph
- Feeds from SecondBrain pipeline (filtered for public content)
- Consulting becomes an offshoot entity, not the main brand
- The website IS the mind. The brand IS the person.

### OpenClaw PR — ElevenLabs + iMessage Voice Memo Guide
- Document working config for custom ElevenLabs voice + iMessage via BlueBubbles
- Repo forked to alex-abell/openclaw, ready to branch

### LiveJournal Account Recovery
- Username: slim (created ~2001, age 15)
- Emails: somatic@loveable.com or invisible_pants@hotmail.com (no access)
- Could try recovering Hotmail via Microsoft first
- Support ticket draft ready

### Recurring: Avie's Clothes Return
- Every time Avie goes back to Annika's, check if there are clothes to send back
- Co-parenting logistics pain point

## ✅ Done (completed, for reference)

### Day 1 Infrastructure (2026-03-22)
- 1Password CLI, Neo4j, Obsidian, BlueBubbles, Chrome control, Google Workspace (gog), ElevenLabs voice, GitHub repos

### Night Swimming v1 (2026-03-22)
- Email GTD (149 emails triaged), Google Drive Audit (310 files), Contact Triage (295 contacts), ChatGPT Deep Processing (139 convos)

### "Can't Afford Me" Single (2026-03-23)
- Lyrics written, Suno track generated, album art created, music video sent to Jay 🎤💅

### "In the Stream" Single (2026-03-23)
- Jonathan Wilson haiku remix, lyrics + album art + track delivered

## 🗑️ Dropped (decided not to pursue)

(nothing yet)
