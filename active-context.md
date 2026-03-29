# Active Context — Last Updated 2026-03-29 02:00am

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

## Tomorrow's Agenda (Sunday Mar 29)
1. **Things 3 integration** — get a real task manager wired up
2. **Fix combined calendars** — ORNL calendar read-only via iPhone share
3. **IP/CUI/COI thinking** — ORNL compliance, consulting blocker
4. **ServiceNow demo cleanup** — prep for Regina and Andrew at work
5. **Neo4j + Obsidian cleanup pass** — 7,677 Person nodes are mostly junk
6. **abellminded.com product architecture** — flesh out the full vision
7. **Backlog triage** — 70+ items in GTD inbox need sorting

## Active Projects
- **HoldPlease**: Phase 3 hybrid built. Web UI at port 3981. ElevenLabs agent live. Monday 7am Lufthansa retry.
- **AVERY**: SHIPPED! Live at abellminded.com/heyavery. Voice + expressions + SOUL.md done.
- **Consulting launch**: BLOCKED on ORNL IP/COI.
- **abellminded.com**: Brain map + /debra + /holdplease + /heyavery live. Need /consulting page.
- **Dream Cycle**: First run tonight 11:30pm.

## Critical Context
- Hannah is pregnant (secret)
- ORNL IP claim is a REAL blocker
- Boston trip Apr 2-5. Flight G4 1426 departs TYS 7:30am Apr 2. Hotel TBD!
- Hue Bridge Pro out for delivery today
- 1Password CLI auth timing out — needs troubleshooting
