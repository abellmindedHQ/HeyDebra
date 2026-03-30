# Contact Enrichment Plan
> Created 2026-03-29. Systematic enrichment of 1,000 Google Contacts.

## Status
- [x] Delete 126 empty ghost contacts (done 3/29)
- [x] Check for Dex custom fields (none found — Dex was iCloud only)
- [x] Delete unknown Pooja Dutt
- [x] Enrich inner circle batch 1: Angelo Nappi, Brooks Herring, Herb Himes, Jay Eckles
- [ ] Enrich inner circle batch 2: remaining 26 known empties
- [ ] Full 1,000 contact enrichment pass (multi-day)
- [ ] Photo upload for inner circle (~30 people)
- [ ] iPhone: remove Dex app + iCloud duplicate cleanup

## Enrichment Sources (priority order)
1. **What Debra already knows** (MEMORY.md, People/ files, conversation context)
2. **Google Contacts existing data** (merge any iCloud-only fields in)
3. **LinkedIn** (title, org, location — browser scrape)
4. **iMessage/BlueBubbles history** (relationship context, last interaction)
5. **Google search** (for key people only)
6. **Facebook/Instagram archives** (relationship signals from SecondBrain-Archive)

## Enrichment Fields (per contact)
- Name (clean, no credential suffixes)
- Phone (E.164 format)
- Email
- Organization + Title
- Notes/Bio (relationship context, how Alex knows them)
- Photo (LinkedIn headshot or social media)
- Birthday (if known)
- Address (if known)

## Rate Limits
- Google People API: ~60 writes/min, 429 after ~100 rapid calls
- LinkedIn scraping: slow, 1 profile per 10-30 seconds
- Photo uploads: separate endpoint, ~30/min

## Batch Strategy
- **Tier 1 (tonight/tomorrow):** Inner circle 30 — full enrichment + photos
- **Tier 2 (this week):** Contacts with phone but no org/title (~400) — LinkedIn lookup
- **Tier 3 (next week):** Contacts with email only (~380) — basic cleanup
- **Tier 4 (ongoing):** As new contacts are created, enrich immediately

## Cron Approach
Schedule a nightly enrichment cron that:
1. Pulls contacts missing org/title
2. Looks up LinkedIn via browser (5-10 per night to avoid rate limits)
3. Updates Google Contacts
4. Logs progress to this file
