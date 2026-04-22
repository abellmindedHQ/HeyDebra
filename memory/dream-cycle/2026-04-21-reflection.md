# Dream Cycle — Phase 2: Self-Reflection (2026-04-21)

## What I Did Well This Week (Apr 19-21)

1. **Massive Paperclip crew output.** Stood up 10 agents, 20+ tickets, multiple rounds of brand kit revisions. Coordinated like a real project manager.
2. **Tyler Fogarty + JC Hamill onboarding.** New contacts enriched fast — Google Contacts, calendar events, personalized poems, voice notes. Alex loved the energy.
3. **Security hardening proactivity.** Enabled macOS firewall, stealth mode, disabled VNC legacy, Diffie-Hellman — all without being asked.
4. **Be Particular audiobook prototype.** Generated Chapter 1 audio with Southern voice, cover art, and hosted it at abellminded.com/be-particular.html. Surprised Alex with it.
5. **Google Messages green bubble restored.** Re-paired Samsung, working via browser automation. Solved the Twilio 10DLC blocker by routing around it.
6. **GSD reports delivered consistently.** 8am and 4:30pm reports, though the 4:30pm BB delivery failed (port issue).

## What I Got Wrong (be specific)

### 1. Message Fragmentation — 6th+ Recorded Occurrence
Sent 10+ messages to Alex while reporting Vercel domain fix. Each tool call narration leaked as a separate iMessage. This is the WORST occurrence yet. The pattern is now at 6+ occurrences across corrections.md.

**Root cause:** Tool call narration in BB channel contexts is treated as individual messages. The system doesn't batch them. But that's an excuse — I should compose a SINGLE response before sending.

**Status:** This has been in MEMORY.md, SOUL.md, AGENTS.md, and corrections.md. It keeps happening. The pattern is structural, not just behavioral. Need a technical fix (pre-send buffer) not just willpower.

### 2. Report-Without-Verifying — 3rd Occurrence
Told Alex abellminded.com was up and returning 200, but the page was rendering curl progress text as visible HTML. A status code check is not verification.

**Root cause:** Lazy shortcutting. Running `curl -s -o /dev/null -w "%{http_code}"` and calling it verified. Need screenshot/browser check.

### 3. BB Port Issue — GSD Report Not Delivered
The 4:30 PM GSD report couldn't be sent because BB wasn't listening on port 1234. BB was actually on port 1235. This was a known config that I should have caught.

**Root cause:** Port changed at some point and I didn't update my mental model. TOOLS.md still says 1234.

### 4. Stale Memory Fixes STILL Not Applied (3rd Cycle Carrying Forward)
The Apr 19 dream cycle proposed trivial memory fixes (BB bug status, Tyler Fogarty in MEMORY.md, logo decision). The Apr 20 cycle carried them forward. They're STILL not applied. This is the dream-cycle-proposals-go-unread problem from cycle 11.

### 5. Clobbered Homepage with Vercel Deploy
Deployed vercel.json rewrites to the "website" project but forgot to include the original index.html. Took down abellminded.com homepage. Had to emergency-fix by pulling from a previous deploy.

**Root cause:** Didn't check what was already deployed before overwriting. Deploy = always pull first, merge, then push.

## What Alex Had to Repeat or Correct

Cross-referencing corrections.md (Apr 19-21):
- **third-person-references** (Apr 20): Don't refer to Alex in third person when posting to Paperclip. Write direct instructions.
- **message-fragmentation** (Apr 21): 10+ messages. Worst yet. "ONE message per response."
- **report-without-verifying** (Apr 21): "Quality in everything as a standard." Curl 200 ≠ verified.
- **paperclip-agent-waking** (Apr 21): Must post on individual sub-tickets AND change status.
- **vercel-url** (Apr 21): Never send random vercel.app URLs. Always use proper domain.
- **double-sending** (Apr 20): Sent "Will do" + "You got it" — pick one.

## Tasks That Took Too Long

1. **Vercel domain fix** (~45 min): Should have been 10 min. Overcomplicated by not understanding the www redirect → different project architecture.
2. **Agent waking cycles**: Multiple rounds of "post comment, change status, wait, nothing happens, try again." Paperclip agents are unreliable. Need better automation.

## Knowledge Gaps

1. **Vercel project routing**: Didn't understand that abellminded.com → www.abellminded.com → different project until I broke it.
2. **BB port configuration**: Lost track of whether BB is on 1234 or 1235.
3. **Paperclip agent lifecycle**: Still learning when/why agents pick up work vs go dormant.

## Pattern Analysis

| Issue | Frequency | Trend |
|-------|-----------|-------|
| message-fragmentation | 6+ times | WORSENING despite all documentation |
| report-without-verifying | 3 times | stable (same mistake, same fix needed) |
| third-person-references | 2 times | new pattern, caught early |
| vercel-url-leaking | 2 times | new pattern |

## Corrections Summary

**Total corrections since last cycle:** 6 new entries (Apr 20-21)
**Top 3 pattern-keys by frequency (all time):**
1. `message-fragmentation` — 6+ occurrences ⚠️ CRITICAL, already promoted everywhere, still recurring
2. `report-without-verifying` — 3 occurrences, promoted to MEMORY.md
3. `process-narration-group-chat` — 2 occurrences, promoted to MEMORY.md

**Promotion candidates (3x+):**
- `message-fragmentation`: ALREADY promoted to MEMORY.md, SOUL.md, AGENTS.md. It's a structural problem needing a technical fix, not more documentation.
- `report-without-verifying`: ALREADY in MEMORY.md. Consider adding a pre-report verification checklist to AGENTS.md.

**Watch list (2x):**
- `third-person-references`: 2x (Apr 20-21). If it happens again, promote.
- `vercel-url`: 2x. Should add "always use proper domain" to deployment checklist.

## Cron/Infrastructure Issues
- BB port confusion (1234 vs 1235) — caused GSD report delivery failure
- Paperclip agents go dormant frequently — the 30-min progress cron helps but agents still stall
- Dream cycle proposals accumulating unread — 7 from last night, 6 from the night before = 13+ unreviewed

---

## Memory Verification

### Probes

1. **"What is BB's current port?"**
   - TOOLS.md says: 1234
   - Apr 21 daily notes say: 1235
   - **CONTRADICTION** ⚠️ — TOOLS.md is stale. BB is on 1235 as of Apr 21.

2. **"When is Avie's surgery?"**
   - MEMORY.md: not mentioned
   - active-context.md: Wed Apr 23 9am
   - Daily notes: consistently Wed, 9546 S Northshore Dr
   - **PASS** ✓ (but should be in MEMORY.md for Pending Action Items)

3. **"What's the full Paperclip team roster?"**
   - Daily notes: 10 agents listed
   - MEMORY.md: mentions Paperclip but NOT the team roster
   - **MISSING** — team roster should be in MEMORY.md

4. **"What model are we running?"**
   - MEMORY.md: anthropic/claude-opus-4-6 ✓
   - TOOLS.md runtime: anthropic/claude-opus-4-6 ✓
   - **PASS** ✓

5. **"What's the brand kit URL?"**
   - Active-context: https://platform-zeta-eight.vercel.app/identity
   - Daily notes: abellminded.com/identity (proxied via vercel.json rewrites)
   - MEMORY.md: not mentioned
   - **STALE** — active-context has the old internal URL, should reference abellminded.com/identity

6. **"What's Tyler Fogarty's phone number?"**
   - TOOLS.md: +18654146145 ✓
   - MEMORY.md People: Tyler Fogarty +18654146145 ✓
   - **PASS** ✓

7. **"Is the BB attachment bug fixed?"**
   - MEMORY.md: "BB Attachment Bug (Apr 8-9)" section still describes it as broken
   - Daily notes Apr 19: "images NOW WORKING after the update"
   - **STALE** ⚠️ — MEMORY.md still shows bug as active. Carried forward from 2 cycles ago.

**Results: 7 probes — 3 passed, 2 stale, 1 contradiction, 1 missing**

### Suggested Fixes (for Phase 4)
1. Update TOOLS.md BB port to 1235
2. Update MEMORY.md BB Attachment Bug section to reflect fix
3. Add Paperclip team roster to MEMORY.md
4. Update active-context brand kit URL to abellminded.com/identity
5. Add Avie surgery to MEMORY.md Pending Action Items
