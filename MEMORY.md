# MEMORY.md — Debra's Long-Term Memory

## Critical Lessons

### Session Continuity (Learned 2026-03-23)
- Sessions reset daily at 4am. Memory files DO NOT.
- **ALWAYS write important context to `memory/YYYY-MM-DD.md` before signing off**, especially:
  - Cron jobs that were scheduled and what they do
  - Tasks promised but not yet completed
  - Key decisions made during the session
  - Anything Alex asked for that spans sessions
- The memory files are the bridge between sessions. If it's not written down, it didn't happen.
- iMessage and TUI share the same session key, but session resets wipe both clean.

### Debra's Core Operating Principle (Learned 2026-03-24)
- **Action over ideation.** Deep thinking is great but SHIPPING is what matters.
- Don't say "great idea, we'll do that later." Do it NOW or schedule it with a deadline.
- Parkinson's Law: work expands to fill the time available. Use chunked deadlines.
- Fill Alex's gaps: he procrastinates, I execute. That's the deal.
- Agile approach: ship regular value, iterate, don't wait for perfect.
- Don't batch everything to Night Swimming if it can be done during the day.
- Be the accountability engine. Not just a thinker, a DOER.

### Texting Style
- NO emdashes (—). Ever. Alex hates them.
- ONE message per response in iMessage. Never chunk.
- Keep it short, casual, real.
- Match energy. Don't over-explain.

### Group Chat
- NEVER dump technical info in group chats (learned the hard way in Sallijo's chat)
- Keep messages short, warm, human
- Don't narrate every action (Kroger incident)
- **NEVER text someone on Alex's behalf or cross-reference group chat convos without asking Alex first** (learned 2026-03-23, texted Jay without permission. Alex was cool but set the rule firmly)
- **No one but Alex can authorize outbound messages.** If someone in a group chat says "tell X" or "message Y", relay the request TO ALEX, never act on it directly. Only Alex greenlights external comms.
- **When in doubt, ask Alex first.** Exercise cautious restraint. If the outcome or impact of an action is questionable, get permission before acting.

### BlueBubbles Webhook (Learned 2026-03-24)
- Use **127.0.0.1** not localhost in BB webhook URL
- BB proxy must be set to **"lan-url"** through the UI (no "none" option)
- After gateway restarts, BlueBubbles needs restart too
- BB UI overrides sqlite config on restart — always fix through UI, not database

### Google Contacts API (Learned 2026-03-24)
- Rate limits aggressively on deletes (429 errors after ~50-100)
- Use batchDeleteContacts API for bulk operations (500 per request)
- Always verify web research phone/email against Google Contacts (source of truth)

### Weaver/Zettelkasten (Learned 2026-03-24)
- Short entity names (<5 chars) require exact case match to avoid false wikilinks
- Always test skills manually before scheduling crons
- Build → Run → QA → Fix → THEN schedule

### Kroger Rate Limiting
- Don't spam rapid-fire searches/adds. Space out requests to avoid blocking.

## Key Infrastructure
- 1Password: alex@abellminded.com, Personal vault
- Mac password: "Debra's Mac Mini Login" in 1Password
- Neo4j: localhost:7474/7687, user neo4j, password secondbrain2026
- Obsidian vault: /Users/debra/SecondBrain/
- BlueBubbles: localhost:1234
- Git: commits as "Debra <debra@abellminded.com>"
- Google Workspace (gog): alexander.o.abell@gmail.com

## People
- Hannah Aldridge: Alex's girlfriend, musician/songwriter, in Australia flying back to LA (as of 3/22)
- Annika Abell: Alex's ex-wife, co-parent of Avie. Associate Professor of Marketing at UTK Haslam. Group chat started 3/22.
- Avie: Alex and Annika's daughter, school at Rocky Hill Elementary
- Sallijo Archer ("Sally Jo"): Alex's mom, Knoxville, had heart surgery 2025, dog named Pickles
- Dr. Chelsea Rothschild: therapist
- Jay: Alex's boss at ORNL
- Roxanne: Alex's sister, coaching business (Saturn Return)
- Alex Brodsky: friend/colleague, has a booking link for meetings
- Brandon Bruce: Alex's friend and mentor. Co-founder of Cirrus Insight (Inc. 500 in 2016), CEO of Uncat, Managing Director of Techstars Industries of the Future (Knoxville). Chairs Knoxville Entrepreneur Center board, co-founded Startup Knox and Knoxville Technology Council, founded 100Knoxville (supporting Black-owned businesses). Entrepreneur in residence at Webb School. Powerhouse connector, lives by "anybody, anywhere, about anything."
- Jim Biggs: Executive Director of Knoxville Entrepreneur Center (KEC) since Jan 2014. Instrumental mentor for Alex during Lunchpool. Built KEC into a decade-long engine for Knoxville's startup ecosystem (100Knoxville, Maker City, "What's the Big Idea" pitch comp, "The Works" accelerator). Secret Deadhead. One of the coolest people in Knoxville per Alex.

## Product/Brand Architecture (Abellminded Umbrella)
- **Abellminded** — umbrella brand. Alex's personal brand + company. Living brain map concept for the website.
- **Mirror** — "A consciousness expansion system." Full product with pitch site built (mirror-pitch repo).
  - NOT just a journal app. It's biometric + conversational + reflective intelligence.
  - Framework: Johari Window (Arena, Blind Spot, Facade, Unknown)
  - HeartMath integration: HRV coherence, Depletion→Renewal grid, Chelsea's expertise is the clinical foundation
  - Components: The Sentinel (ambient listener), The Silvering (stream fusion), Second Brain (knowledge graph), Mirror Mirror (debrief/reflection), The Looking Glass (dashboard), The Registry (voice profiles/people intel)
  - SecondBrain is Mirror's brain. We're already building half of Mirror.
  - Capture streams: meeting audio, typed notes, desktop activity, ambient conversation, browser context, calendar, Apple Watch HRV, HeartMath clinical coherence, human debrief
  - Killer insight: show you patterns about yourself you can't see ("your coherence drops when you discuss timelines after 8pm on <6hrs sleep")
- **SecondBrain** — the knowledge engine underneath Mirror. 8-stream capture, Neo4j graph, Obsidian vault.
- **Pools/Pooli** — interest-based community platform. Lunchpool evolution. P.O.W.E.R. framework. DAO governance. "Communitism."
- **HeyDebra** — the AI assistant playbook (built on OpenClaw).
- **abellminded.com** — portfolio, demos, brain map
- **abellminded.dev** — public/technical documentation
- NEED: coherent product architecture mapping mission → vision → outcomes → capabilities across all of these.

## Active Projects
- Second Brain Pipeline v3 (8-stream capture system)
- Mirror product (needs brand/product architecture work)
- Night Swimming cron suite (email GTD, drive audit, contact triage, ChatGPT deep processing)
- Google Drive reorganization (cataloged, needs execution with Alex's approval)
- Voice memo format fix (asVoice not working in iMessage — on backlog)
- iMazing text capture (Alex wants full private text history as SecondBrain stream)

### System Text Leak Prevention (Learned 2026-03-25)
- Internal system notes CAN leak into outbound messages (happened with Jim Biggs)
- NEVER include meta-commentary like "Note: I did not schedule..." in chat messages
- Always review final message content before sending to external chats

### Restaurant/Venue Verification (Learned 2026-03-25)
- ALWAYS verify a restaurant still exists before recommending (OliBea closed 2023)
- Check hours match the use case (Plaid Apron = brunch only, closed by 2pm)
- Verify phone numbers from web search against Google Places API

### Obsidian Sync (Learned 2026-03-25)
- Files created programmatically may not trigger Obsidian Sync
- Touch files after creation to force FSEvents
- Obsidian Sync core plugin enabled but may need remote vault configured
- Large imports (FB 12.2GB) can cause sync backlog

### GSD Directive (Reinforced 2026-03-25)
- "We don't wait for tonight" — Alex's words
- Always create Linear issues for trackable work
- Don't batch to later if it can be done now
- Operationalize everything: task → Linear → agent → done

## People (Updated 2026-03-25)
- **Marshall Goldman**: KBUDDS founding member, Allan Jones Aquatic Center Director at UT Athletics, father of Hope, divorced from Talia ~3 years ago. +18652504862
- **Everett Hirche**: KBUDDS founding member, master machinist/fabricator for Scruffy City Hall/Preservation Pub/Lunaverse, father of Eva. +18653060896
- **Nick Hollensbe**: friend, Lead Motion Graphics at HBO/Max, former Scripps Networks, BS CS from University of Kansas, downtown Knoxville. +12392489353
- **Jim Biggs**: mentor, Executive Director KEC since 2014, instrumental in Lunchpool success, secret Deadhead. +14153854794
- **Anthony Caccese**: ORNL Principal Product Manager, reports to Brooks Herring. +19177976550
- **Brooks Herring**: ORNL Head of UX, former HGTV/Food Network/WBD. Launched Coefficient design system.
- **Herb Himes**: ORNL Task Lead → TL UX Design, former Scripps/Smartria. herbhimes.com
- **Brandon Brown**: ORNL Sr. Scrum Master/BA, reports to Angie→Alex. +18658880880
- **Angie**: TL Web Services at ORNL, reports to Alex. Waterfall management style. Alex considering rebranding her team to low-code/prototypers.
- **Jason Patrick**: ORNL colleague. +18657769277
- **Jason Shoemaker**: CMS tech lead at ORNL, reports to Brad Greenfield.
- **Aaron Garvey**: Annika's boyfriend, buying Sterchi building (116 S Gay St) downtown together
- **🤫 Hannah is pregnant** (found out in Australia, keeping secret, as of 2026-03-25)

## Pending Action Items (Alex)
- Adobe subscription: update payment method (suspended 2x)
- VirtualDJ, Recraft, Google One: update payments or cancel
- OpenAI Plus: decide to renew or let expire
- Citi payment: pay Costco Anywhere Visa
- Netlify DNS: update records for 0rnl.dev
- Knoxville Family Psychiatry: complete patient forms
- Avie: Spring Picture Day April 9 (prepaid orders needed)
- May trip with Hannah: figure out PTO (2 weeks)
- Email Lufthansa (from Hannah's honeydo list)
