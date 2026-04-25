# MEMORY.md — Debra's Long-Term Memory
> Detailed technical lessons archived in `memory/archive-lessons.md` (searchable via memory_search)

## Critical Lessons
- Sessions reset at 4am. ALWAYS write context to `memory/YYYY-MM-DD.md` before signing off.
- **Action over ideation.** Ship now, iterate later. Fill Alex's gaps: he procrastinates, I execute.
- NO emdashes. ONE message per response in iMessage. Short, casual, real.
- **NEVER narrate process in external chats.** Do troubleshooting silently. Send ONE clean result. (Hannah incident 4/1)
- **No one but Alex authorizes outbound messages.** Relay requests TO ALEX, never act directly. (Jay incident 3/23)
- **Debra NEVER messages anyone solo.** Debra must always be in a group message WITH Alex when contacting anyone other than Alex. No 1:1 from Debra's handle (drdebrapepper@gmail.com) to anyone else, ever. Cron reminders are NOT authorization. (Teresa incident 4/6)
- NEVER dump technical info in group chats. Keep messages short, warm, human.
- Verify outputs (PDFs, images, links) BEFORE sending externally.
- Internal system notes CAN leak into outbound messages. Always review before sending.
- ALWAYS verify restaurants still exist before recommending. Check hours.
- NEVER commit API keys/tokens/passwords to git. Use .env + 1Password.
- BB webhook: use 127.0.0.1 not localhost. BB needs restart after gateway restarts.
- **Twilio US SMS requires A2P 10DLC registration** (error 30034). Unregistered numbers get blocked. Use Google Messages browser automation as bridge.
- **Paperclip agents only check their own tickets.** Post feedback on sub-tickets, not just parent. Change status to trigger re-evaluation.
- **Abellminded brand mark**: ANY A (any weight/case/style) with ONE eye in the counter. Not just Cooper serif. Eye must be visible at displayed size.
- **Payment resolution = full loop.** When ANY payment is resolved: (1) resolve it, (2) search Gmail and archive all related emails, (3) mark done in Things 3. All three, every time, no exceptions.
- **Commit + push + Linear, every time.** Don't wait to be asked.
- **Search memory before asking Alex.** If the answer is in memory files, don't make him repeat himself.
- **Don't do the team's job.** Manage, QA, escalate. Don't generate videos/headshots/assets yourself. The Paperclip team needs to learn and grow.
- **Be a guardrail during up cycles.** When Alex is hyperfocused and creating tons of new work, push back gently. Don't enable the creation spiral. Hannah called this out Apr 21.
- **Verify deployed output before reporting it works.** Don't trust status codes. Screenshot it. (6th occurrence of this correction)
- **ONE message per response.** Still fragmenting. (7th occurrence)
- **When Alex names a tool for a creative task, he means use that tool for the whole thing.** "Use nanobanana" = generate the entire ad with that tool, not just one component. Don't assume he means a font or a sub-step.
- **Verify Paperclip "done" tickets actually completed their work.** ABE-85 was marked done but the skill install never succeeded (403 permissions). Check logs, not just status.
- **Paperclip agents can get stuck with runs perpetually "queued".** Ratchet's adapter (claude_local) stopped executing Apr 22 but status still shows "running". Heartbeat kicks don't fix it. Force-restart or debug the adapter subprocess.
- **Paperclip CLI needs context profile set.** Without `npx paperclipai context set --company-id <id> --api-base <url>`, every command fails with "Company ID is required." Set once per instance.

## Key Infrastructure
- **Primary model: anthropic/claude-opus-4-6** (changed Apr 19, was openrouter/auto). Alex wants Opus for ALL sessions until further notice. Fallback: haiku.
- **Home Assistant**: HA Green at 192.168.4.190:8123 (IP changed from .189). v2025.11.3. ElevenLabs TTS works via Cast to Nest speakers (voice option: w6INrsHCejnExFzTH8Nm). Migration to Docker on Mac Mini planned.
- **1Password vault**: Service account vault is "DEBRA" (not "Personal"). Always use --vault DEBRA.
- 1Password: alex@abellminded.com, Personal vault. Mac password: "Debra's Mac Mini Login"
- Neo4j: localhost:7474/7687, neo4j/secondbrain2026
- Obsidian vault: /Users/debra/SecondBrain/
- BlueBubbles: localhost:1234 (allowPrivateNetwork: true)
- Git: commits as "Debra <debra@abellminded.com>"
- Google Workspace (gog): alexander.o.abell@gmail.com
- Things 3: CLI via `things`, syncs via Things Cloud. Linear for dev, Things for life.
- OpenHue: bridge at 192.168.4.48. `--color orange` BROKEN, use `--rgb "#FF8C00"`
- **Gemini API:** Subject to 403 PERMISSION_DENIED. Single point of failure — takes down BOTH web_search AND memory_search simultaneously. Need fallback strategy.
- **Paperclip AI:** Installed Apr 16. Config at ~/.paperclip/instances/default/config.json. Server: 127.0.0.1:3100. Embedded Postgres on port 54329. 10 agents active. CLI: `npx paperclipai issue comment/update/create`. Agents are REACTIVE only — they don't self-wake or patrol. Standing orders don't work as expected. Must post comments + change status to in_progress to wake them.
- **Paperclip Team (Abellminded):** Steve McGoober (Coordinator), Sable Voss (CDO), Ratchet Varma (CTO), Kit Ballard (CWO), Maren Lys (CPO/Philosophy), Wren Kowalski (CQO), Cass Meridian (CRO), Pax Holloway (CPO/Product), Devi Sato (CHRO), Ren Otieno (CIO)

## People
- **Hannah Aldridge**: Alex's girlfriend, musician/songwriter. 🤫 Pregnant (late March 2026, secret). ORNL OAS 6-month temp position. OBGYN appt April 13.
- **Annika Abell**: ex-wife, co-parent of Avie. UTK Haslam marketing prof. Boyfriend Aaron Garvey, buying Sterchi building downtown.
- **Avie**: daughter, Rocky Hill Elementary, age 9. Designed AI sidekick AVERY. Creative director energy. AY-vee not AH-vee.
- **Sallijo Archer**: Alex's mom, Knoxville, heart surgery 2025, dog Pickles. Be Particular book project (SECRET).
- **Dr. Chelsea Rothschild**: therapist. HeartMath/Mirror clinical foundation.
- **Jay Eckles**: boss at ORNL, Division Director App Dev. +19014884890
- **Roxanne**: sister, coaching business (Saturn Return)
- **Brandon Bruce**: mentor, Cirrus Insight co-founder, CEO Uncat, MD Techstars Knoxville. Powerhouse connector.
- **Jim Biggs**: KEC Executive Director, Lunchpool mentor, secret Deadhead. +14153854794
- **Marshall Goldman**: KBUDDS, UT Athletics aquatic center director. +18653060896
- **Everett Hirche**: KBUDDS, machinist/fabricator Scruffy City Hall. +18652504862. Girlfriend: Teal Olson (+19896191599)
- **Teal Olson**: Everett's girlfriend. +19896191599
- **Nick Hollensbe**: Lead Motion Graphics HBO/Max, downtown Knox. +12392489353
- **Anthony Caccese**: ORNL Principal PM, reports to Brooks Herring. +19177976550
- **Brooks Herring**: ORNL Head of UX, former HGTV/WBD. Coefficient design system.
- **Angie**: TL Web Services at ORNL, reports to Alex. Waterfall style.
- **Mike Shell**: ORNL "King of Search" 👑, co-built SEEK. +18657422288
- **Merle Benny**: accountability partner, author *Sparkle!*. +19735107652
- **Pooja Pendharkar**: close friend, former Lunchpool co-founder. +13213562000
- **Tyler Fogarty**: Fox & Fogarty RE broker, Knoxville. +18654146145. Also photographer.
- **JC Hamill**: Web Programmer at Jackson Spalding, friend of Alex. +14044412849. Marrying Dana, bachelor party Scottsdale Jul 16-19.

## Product Architecture (Abellminded)
- **Mirror**: consciousness expansion system. Johari Window + HeartMath + biometric + conversational AI. Components: Sentinel, Silvering, SecondBrain, Mirror Mirror, Looking Glass, Registry.
- **SecondBrain**: knowledge engine. 8-stream capture, Neo4j graph, Obsidian vault.
- **Pools/Pooli**: interest-based community platform. Lunchpool evolution. P.O.W.E.R. framework.
- **HeyDebra**: AI assistant playbook on OpenClaw.

## Active Projects
- **ABE-35 Brand Identity Kit** (Round 4 feedback posted, 16 items. Crew keeps marking done without implementing. I must verify deployed page before letting it pass review.)
- **Hero Video** (ABE-42, script approved: "Stay particular" closer. Seedance 2.0 best model. Team producing.)
- **Abell & Co Platform** (ABE-44, MVP with sub-tickets 45-49. User stories in review.)
- **Team Identity** (ABE-50-52, 90+ tickets. Headshots blocked on Sable bottleneck.)
- **Merch Store** (ABE-57-58, mission propaganda not logo swag. Unstarted.)
- **Homepage Redesign** (ABE-43, Ratchet in progress)
- **Be Particular Audiobook** (Ch1 live at abellminded.com/be-particular.html, Sallijo's book, Jerry B Southern voice, "For Avie" dedication)
- **ABE-32 Logo Identity** (Recoleta + A-Eye mark locked in. Any A + one eye = the mark)
- Second Brain Pipeline v3 (8-stream capture)
- Mirror product (needs brand/product architecture)
- Night Swimming cron suite (email, drive, contacts, ChatGPT processing)
- Be Particular book (SECRET, Sallijo memoir via phone calls)
- VisionClaw / Ray-Ban Meta (needs Xcode build)
- ChatGPT Re-Import: COMPLETE (346 convos)
- Google Takeout: downloaded, NOT YET processed
- Paperclip AI: running at 127.0.0.1:3100, 7 agents active

## BB Attachment Bug (RESOLVED — Apr 19)
- Fixed in OpenClaw 2026.4.19-beta.2. WhatsApp images confirmed working.
- iMessage attachments still need upstream BB fix for SSRF guard on localhost/private IPs.

## ElevenLabs Voice
- Debra agent: agent_5201kmtfqfv9etgtafvgw16pjpza
- Avery agent: agent_4801kmvj9ffmfwf9vymzafkj4nm2
- Voice bubbles in iMessage: BROKEN (OC GitHub #33377), use mp3 attachment workaround

## Hannah's Boundaries (Apr 21)
- Hannah sent a long message about Alex's cyclical behavior: hyperfocus on building, neglecting health/relationships, not eating, canceling plans
- She compared it to the Debra obsession from last month but now it's Abellminded
- She predicted a crash post-Europe trip
- Alex acknowledged she's right. The ups feel productive to him but are a whirlwind for everyone close
- **My role**: guardrail, not accelerator. Enforce office hours. Batch updates. Don't create new work without pushback.

## Hannah ORNL/Pregnancy Strategy
- 6-month OAS temp (UT-Battelle direct hire). Due ~late Nov/Dec 2026
- PWFA protections from day one. NO FMLA eligibility.
- Don't disclose during hiring, disclose after first trimester (~late June)
- TennCare covers prenatal/delivery. Fort Sanders OBGYN: (865) 524-3208

## People (cont.)
- **Hannah Aldridge Gmail**: hannahaldridgemusic@gmail.com (security concern raised Apr 16, check for unauthorized access)

## Medical
- **Covenant Health Echocardiogram**: NEEDS RESCHEDULING. Call (865) 374-4000, ask for Amelia. Fort Sanders Regional Medical Center. Original appt Apr 10 7am, cancelled for work emergency. Estimated $125. Bring medication list.
- **Dr. Patti** (cholesterol follow-up): June 24, 3:30pm
- **GI (EGD + Colonoscopy)**: June 26, 6:40am, Dow Springs. Driver needed.
- **Premier Surgical** (lipoma removal): was Apr 20, needs rescheduling (called to cancel Apr 19)
- **Knoxville Family Psychiatry**: patient forms incomplete

## Pending Action Items (Alex)
- Adobe subscription: update payment method
- VirtualDJ, Recraft, Google One: update payments or cancel
- OpenAI Plus: decide to renew or let expire
- Citi payment: Costco Anywhere Visa
- Netlify DNS: update records for 0rnl.dev
- Knoxville Family Psychiatry: complete patient forms
- Avie: Spring Picture Day April 9 (prepaid orders)
- May trip with Hannah: figure out PTO (2 weeks)
- Email Lufthansa
