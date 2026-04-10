# 📋 PROJECTS

Active and someday/maybe projects. GTD style.

## 🔥 Active (has a next action, happening now)

### Second Brain Pipeline v3
- 8-stream capture system architecture designed
- Neo4j graph database running with schema — **3,067 clean Person nodes** (down from 7,677)
- Obsidian vault at /Users/debra/SecondBrain/
- ChatGPT export processed (139 convos, Night Swimming Day 1)
- Claude personal export processed (135 convos, Day 3)
- Claude ORNL export processed (316 convos, Day 3)
- ChatGPT personal re-import: 135 convos via GPT-4o, 54 people enrichments, 120 action items ✅
- ChatGPT ORNL re-import: 211 convos via GPT-4o, 72 high importance, 225 action items ✅
- Voice notes: 125/126 processed (1 corrupted), Whisper API fallback after AssemblyAI depleted ✅
- 491 meeting notes in SecondBrain/Meetings/ (Otter + Apple Notes)
- Google Takeout downloaded (2GB+) — NOT YET PROCESSED
- Instagram processed (711 DMs, 1525 following, Day 3)
- Facebook processed (6007 convos, 161K messages, 20 years, Day 3)
- 334 artifacts extracted from Claude exports
- Weaver v3 built (combined regex + incremental, 12s vs timeout)
- vault_indexer.py built (0.6s searchable index)
- Weekly maintenance scripted: neo4j_weekly_cleanup.py
- **Next**: Process Google Takeout, ORNL wikilink normalization, run Otter notes through extraction pipeline, process LinkedIn full export, iMazing text capture, set up Monarch/YNAB APIs

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
- End-of-day / pre-4am memory flush pattern actively in use ✅
- **Next**: Monitor and iterate. Ensure memory bridges sessions consistently.

### People Intelligence Pipeline
- people-intel skill built with auto-watch behavior
- 94 active People profiles (30 new from Facebook Day 3)
- 240 LinkedIn noise archived to _archived/
- Dedup checker built and running clean
- Google Contacts purged: 7,612 → 1,283
- **Next**: Finish contact sync to drdebrapepper, cross-ref Instagram mutuals

### Knowledge Architecture Deep Dive
- Opus research sub-agent completed full GAN analysis (6 web searches, 3,067 Neo4j nodes audited, latest memory framework research)
- Report saved: memory/knowledge-architecture-report.md
- **Key recommendation:** Hibernate Neo4j → migrate to knowledge.sqlite, reorganize vault with _raw/ prefix, extend memory_search, bring Neo4j back for Mirror dev
- Covers: Neo4j vs Obsidian vs vector DB, staging layer design, voice embeddings, RAG improvements, cost/complexity, Mirror product connections
- **Next**: Alex reviews report, makes architectural decisions

### ORNL Transformation Group Reorg
- **Status**: Awaiting Jay Eckles' approval to greenlight Brad Greenfield as interim GL
- **Scope**: Rename Web Services team → Knowledge Products, formalize Transformation Group within App Dev
- **Deliverables**: (1) Staff list compiled, (2) Reorg communication drafted, (3) Sarah Glei notification
- **Blocking**: Jay's 1:1 + greenlight on Brad interim assignment
- **Next**: Compile staff list, draft communication package, schedule 1:1 with Jay

### Roxanne's App Project (Silicon Systems)
- **Status**: CRITICAL — 32 days blocked on NDA/app decision email from Alex
- **Scope**: $8K app dev pitch, Roxanne co-founder coaching business app
- **Blocking**: NDA execution + Alex decision on scope/timing
- **Next**: Alex to review + send NDA decision email (high priority this week)

### Food Inventory Tracking System
- **Status**: Initialized Apr 8, awaiting usage/feedback
- **Purpose**: Grocery receipt scanning + photo parsing + markdown tracking
- **Location**: ~/.openclaw/workspace/food-inventory.md
- **Architecture**: Receipt → photo → OCR/parser → markdown table
- **Next**: Alex tests with first grocery receipt, feedback on UX/format

### Automation Suite (18 Cron Jobs)
- Email GTD: 7am, 12pm, 6pm daily
- Capture Agent: 7:30am, 2pm, 8pm daily
- GSD Agent: 8am, 3pm daily
- LinkedIn Cleanup: 10am daily
- Night Swimming: Sunday 9-10:30pm
- Weaver: Sunday 11pm
- Memory Flush: 3:30am x2
- First full production day mostly worked ✅
- Evening signals captured correctly: Runway payment failures, TurboTax doc follow-up, Dream Cycle #10
- **Next**: Monitor for misses and verify morning behavior after reset
- Includes: Capture Agent (3x), Email GTD (3x), GSD Agent (2x), Night Swimming suite (Sun), Dream Cycle (daily 11:30pm), Memory Consolidation (Sun), Sallijo Story Time (every other day 2pm), LinkedIn Cleanup (daily 10am), various reminders

### Multi-Channel Messaging
- iMessage (BlueBubbles): LIVE ✅
- WhatsApp (+18652870278): LIVE ✅
- RCS/SMS (Google Messages): LIVE ✅ (send working, inbound observer needs verification)
- Major current weakness: BlueBubbles attachment ingestion is intermittent and still under investigation
- **Next**: Verify SMS observer inbound, set up as persistent service, finish BB attachment fix

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
- Live pages: /debra, /holdplease, /heyavery, /hannah, /mirror
- Planned: /products, /consulting, /work, /writing, /about
- Local: /Users/debra/.openclaw/workspace/projects/abellminded/
- **Next**: Build /consulting page

### CAD Framework Interactive Site
- Chelsea Rothschild's Chronic Altruistic Dysregulation clinical framework
- Integrated into Mirror pitch site with interactive components
- Features: animated 4-stage cycle, breathing circle, reflection cards, population cards
- Deployed to abellminded.vercel.app/CAD-Framework/ (custom domain routing pending)
- Full credit to Dr. Chelsea Rothschild with heartconnectedhealing.com link
- **Next**: Fix custom domain routing (abellminded.com/CAD-Framework 404)

### HoldPlease (AI Phone Agent)
- Phase 1: Twilio outbound calling ✅
- Phase 2: OpenAI Realtime (built, had audio issues, not primary path)
- Phase 3: ElevenLabs Conversational AI 2.0 hybrid ✅ SHIPPED
- ElevenLabs agent: agent_5201kmtfqfv9etgtafvgw16pjpza (Debra's voice)
- Twilio phone: +18653915873 (phnum_6601kmtfr2scffj9rv4fb7fcfrtj)
- Web UI: port 3981 (dark theme, live transcripts, call history)
- Hybrid mode: Twilio hold-detection (~$0.02/min) → ElevenLabs on human detect (~$0.13/min)
- Lufthansa test calls: 3x (queue 75→61, no human Saturdays)
- Monday 7am cron for Lufthansa retry: c616beb3
- **Next**: Verify Monday call, tune IVR navigation, track success rates

### AVERY (Avie's AI Sidekick)
- SHIPPED ✅ Live at abellminded.com/heyavery
- Character: cool/unbothered teen, Carly x Phoebe x Bluey energy
- Voice: ElevenLabs voice_id l9irhEnWKSUzVNW28WNn, speed 1.15x
- Agent: agent_4801kmvj9ffmfwf9vymzafkj4nm2
- 6 expression sprites (happy/thinking/excited/silly/caring/laughing)
- Interactive prototype: talk.html with avatar reactions
- Avie is Creative Director (went through 5 voice rounds to get it right)
- Avery pronunciation: "AY-vee" (A.V. like the letters)
- **Next**: Build out full product, parental controls, age-appropriate guardrails, HeyX platform

### Hannah Aldridge Music Studio
- Landing page LIVE at abellminded.com/hannah ✅
- Business plan extracted from Dec 2025 Claude convo
- Pricing: $40/$60/$85 single lessons; $150/$240/$330 monthly packages
- Location: Rush's Music, Knoxville (Mon-Thu afternoons/evenings)
- Press photos from hannahaldridge.com (Michelle Fredericks + Amanda Chapman)
- v0 prompt written for full platform (booking, Stripe, dashboards)
- **Next**: Run v0 for full platform, integrate Stripe, launch booking

### Dream Cycle
- Nightly self-improvement pipeline (11:30pm ET cron)
- 4 phases: Research Scan → Self-Reflection → Deep Research → Proposals
- First run: 7 proposals generated (memory/dream-cycle/2026-03-28-proposals.md)
- 🚨 TOP PRIORITY: GitHub private repo opt-out by April 24
- All proposals staged for human review — nothing auto-applies
- **Next**: Alex review proposals, implement approved changes

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
