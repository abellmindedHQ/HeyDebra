# Active Context — Last Updated 2026-03-29 3:30am (pre-reset flush)

## Overnight Vault Optimization (Mar 28-29)
- Weaver v3: full scan 64s (was timeout), incremental 12s — combined regex + mtime mode
- Neo4j: 7677 → 3067 Person nodes (-60%), all junk/null/concept nodes cleaned
- New scripts: neo4j_weekly_cleanup.py, vault_indexer.py
- New indexes: SocialProfile.platform/.username, Person.phone/.email
- Vault index: .vault-index.json + MOCs/VAULT-INDEX.md
- Scale plan documented: memory/vault-scale-architecture-2026.md
- 5 git commits pushed to origin master
- Full report: memory/vault-optimization-report-2026-03-29.md

## What Just Happened (Sat Mar 28 — MASSIVE build day)
- Dream cycle skill, HoldPlease Phase 2+3, ElevenLabs voice agent, web UI
- Lufthansa calls (3x): navigated full IVR, queue pos 75→61, no human Saturday
- AVERY shipped! Avie's AI sidekick live at abellminded.com/heyavery
- Avery voice selected (cool/unbothered teen), ElevenLabs agent created
- Git history scrubbed of all secrets, CI/CD pipeline added, pushed to GitHub
- READMEs overhauled for both HeyDebra and Avery
- Merle Benny call Monday 2:30pm, David Byrne IG DM sent
- Debra personality tuned on phone (less snarky, more warm)

## Monday Crons
- **7am ET:** Lufthansa HoldPlease call (hybrid mode) — cron c616beb3
- **2:30pm ET:** Call with Merle Benny — on calendar with invite
- **11:30pm ET:** Dream Cycle first run — cron 135acf6e

## Pending Actions
- ✅ Hannah reimbursed $1,100 (Alex Venmo'd today)
- Reconnect Capital One to Venmo
- Pay Costco Citi card (PAST DUE!)
- Fix Apple Pay Lost Mode (iCloud.com)
- Text Leigh re: Avie can't do Charlotte's Apr 3 party (Boston trip)
- Pay KUB bill
- Fix Adobe billing
- Labcorp lab results review
- Avie Spring Picture Day April 9 — prepay
- Roxanne NDA/app email — 31 days unanswered, Alex needs to process
- SwitchBot API token needed from Alex (for HA integration)
- Brandon Bruce Muse for All luncheon Apr 7 — RSVP pending
- ORNL Isaac compute roadmap — due Tue Mar 31

## Sunday's Agenda (Mar 29)
1. **Things 3 integration** — get a real task manager wired up
2. **Fix combined calendars** — ORNL calendar read-only via iPhone share
3. **IP/CUI/COI thinking** — ORNL compliance, consulting blocker
4. **ServiceNow demo cleanup** — prep for Regina and Andrew at work
5. ✅ **Neo4j + Obsidian cleanup** — DONE overnight (7,677→3,067 nodes, Weaver 12s incremental)
6. **abellminded.com product architecture** — flesh out the full vision
7. **Backlog triage** — 70+ items in GTD inbox need sorting
8. **Hannah music studio** — review landing page, maybe run v0 for full platform
9. **Anne's birthday** — Hannah's mom, March 29 (TODAY). Did Alex get the book?
10. **Review dream cycle proposals** — 7 changes staged (GitHub opt-out by Apr 24 is urgent)
11. **Review vault optimization report** — memory/vault-optimization-report-2026-03-29.md

## Active Projects
- **HoldPlease**: Phase 3 hybrid built. Web UI at port 3981. ElevenLabs agent live. Monday 7am Lufthansa retry.
- **AVERY**: SHIPPED! Live at abellminded.com/heyavery. Voice + expressions + SOUL.md done. Agent: agent_4801kmvj9ffmfwf9vymzafkj4nm2
- **Hannah Music Studio**: Landing page live at abellminded.com/hannah. v0 prompt ready for full platform.
- **Consulting launch**: BLOCKED on ORNL IP/COI.
- **abellminded.com**: /debra + /holdplease + /heyavery + /hannah + /mirror all live. Need /consulting.
- **Dream Cycle**: First run completed! Proposals in memory/dream-cycle/2026-03-28-proposals.md
- **Vault Optimization**: Weaver v3 + Neo4j cleanup + indexer all DONE. Weekly maintenance scripted.

## Critical Context
- Hannah is pregnant (secret)
- ORNL IP claim is a REAL blocker
- Boston trip Apr 2-5. Flight G4 1426 departs TYS 7:30am Apr 2. Hotel TBD!
- Hue Bridge Pro out for delivery today
- 1Password CLI auth timing out — needs troubleshooting
