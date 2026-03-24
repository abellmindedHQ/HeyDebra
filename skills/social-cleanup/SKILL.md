---
name: social-cleanup
description: Curate following lists across social networks (Instagram, LinkedIn, Twitter/X) by cross-referencing with real contacts and relationship data, then executing unfollows in batches with rate limiting. Use when asked to "clean up Instagram following", "curate my Twitter follows", "unfollow noise on LinkedIn", or "run social cleanup". Modeled after linkedin-cleanup skill.
---

# social-cleanup

Analyze following lists across social networks, cross-reference with real relationships, generate a cleanup queue, and execute unfollows in safe batches.

**Supported networks:**
- LinkedIn (following + connections)
- Instagram (following)
- Twitter/X (following)

**Model recommendation:** `google/gemini-2.0-flash-lite` for the execution phase (clicks buttons, doesn't think hard). Use a smarter model for the analysis/classification phase.

---

## Quick Start

1. **Run analysis**: `social-cleanup analyze --network [instagram|linkedin|twitter]`
2. **Review the queue** (required before any unfollows execute)
3. **Approve**: Tell Debra "looks good, run the cleanup"
4. **Execute in batches**: Follow the Browser Automation Flow below
5. **Optional: set up cron** for ongoing maintenance

---

## State File

All progress persisted at:
`/Users/debra/.openclaw/workspace/memory/social-cleanup-state.json`

```json
{
  "networks": {
    "instagram": {
      "totalFollowing": 0,
      "toUnfollow": 0,
      "unfollowedTotal": 0,
      "unfollowedToday": 0,
      "lastRunDate": null,
      "lastError": null,
      "queue": [],
      "completed": [],
      "skipped": [],
      "paused": false
    },
    "linkedin": { ... },
    "twitter": { ... }
  },
  "lastUpdated": null
}
```

---

## Rate Limits (HARD LIMITS — never bypass)

### Instagram

| Limit | Value |
|-------|-------|
| Max unfollows per session | **20** |
| Max unfollows per day | **60** |
| Delay between unfollows | **15–45 seconds (random)** |
| Max session duration | **20 minutes** |
| Operating hours | **Any time (spread across day)** |

⚠️ Instagram is aggressive about unfollow automation. Keep it slow.

### LinkedIn

| Limit | Value |
|-------|-------|
| Max unfollows per session | **50** |
| Max unfollows per day | **150** |
| Delay between unfollows | **3–10 seconds (random)** |
| Max session duration | **15 minutes** |
| Operating hours | **9am–5pm ET, weekdays** |

### Twitter/X

| Limit | Value |
|-------|-------|
| Max unfollows per session | **30** |
| Max unfollows per day | **100** |
| Delay between unfollows | **5–15 seconds (random)** |
| Max session duration | **20 minutes** |
| Operating hours | **Any time** |

**Stop immediately on:** CAPTCHA, unusual challenge, "something went wrong", rate limit warning, or any unexpected UI state.

---

## Analysis Phase

### Step 1 — Pull Following List

**From social data export** (preferred — no scraping needed):

```bash
# Instagram — from a processed export
cat /Users/debra/SecondBrain/Social/instagram/social-graph-*.md | grep -A1000 "DM Relationship Map"
```

Or parse directly from export:
```python
# Instagram following from export
import json
with open(f"{export_path}/followers_and_following/following.json") as f:
    data = json.load(f)
following = [item['string_list_data'][0]['value'] 
             for entry in data.get('relationships_following', [])
             for item in entry.get('string_list_data', [])]
```

**From browser** (if no export available):
Use browser automation to scrape the following list from the network's UI. Navigate to profile → following → scroll through list, capturing usernames and display names.

### Step 2 — Load Known Relationships

Pull data from all three relationship stores:

```bash
# Google Contacts
gog contacts list --account alexander.o.abell@gmail.com --format json

# Neo4j people
cypher-shell -a bolt://localhost:7687 -u neo4j -p secondbrain2026 \
  "MATCH (p:Person)-[:HAS_PROFILE]->(sp:SocialProfile {platform: '[network]'}) RETURN p.name, sp.username"

# Also get all Person names for fuzzy matching
cypher-shell -a bolt://localhost:7687 -u neo4j -p secondbrain2026 \
  "MATCH (p:Person) RETURN p.name, p.instagram, p.twitter, p.linkedin"
```

Build lookup maps:
- `instagram_usernames: Set` — all known Instagram handles from contacts + Neo4j
- `real_names: Set` — all known real people names (for display name matching)
- `dm_contacts: Dict` — username → message count from social data processing

### Step 3 — Classify Each Account

For each account in following list, assign a category:

**KEEP:**
- Username or display name matches a Google Contact
- Username or display name matches a Neo4j Person node
- Has 5+ DM messages with Alex (from social-data-processor results)
- Is a notable person or organization Alex cares about (check manually)
- Mutual follow + in contacts → definitely keep

**REVIEW (ask before unfollowing):**
- Mutual follow but NOT in contacts — might be real relationship not yet added
- No match found but username suggests someone known (looks like a real name)
- Recently followed (< 30 days)

**UNFOLLOW:**
- No name match + no DM history + not mutual follow → likely noise/discovery/spam follow
- Account is clearly a brand/company with no personal connection
- Account appears inactive (username patterns like random numbers, clearly a bot)
- LinkedIn: connection exists purely from mass-import, no real interaction signal

### Step 4 — Build Cleanup Queue

Generate the queue — sort by: most noise-like first.

```python
queue = [
    {
        "username": "username",
        "display_name": "Display Name",
        "category": "UNFOLLOW",
        "reason": "No contact match, no DMs, not mutual",
        "profile_url": "https://instagram.com/username/",
        "status": "pending"
    },
    ...
]
```

Save to state file under `networks.[network].queue`.

### Step 5 — Present Queue for Approval

**Required before any execution.** Generate a summary:

```
📋 Instagram Cleanup Queue — YYYY-MM-DD

Following: 847
- KEEP: 143 (known contacts, real relationships, valuable content)
- REVIEW: 23 (mutual follows with no contact match — listing below)
- UNFOLLOW: 681 (noise, no connection, brands, dead accounts)

⚠️ REVIEW REQUIRED (23 accounts — mutual follows not in contacts):
1. @[username] ([display name]) — mutual follow, no contact match
2. @[username] ([display name]) — mutual follow, no contact match
...

Ready to queue 681 unfollows.
Estimated time: ~34 days at 20/day.

Approve to proceed: "looks good, run cleanup"
```

**Do not execute any unfollows until Alex explicitly approves.**

---

## Execution Phase (Browser Automation)

### Pre-flight Checklist

Before each session:
- [ ] State file exists, `paused` is false
- [ ] `unfollowedToday` is below daily limit
- [ ] Queue is non-empty
- [ ] Correct rate limits for the network
- [ ] Browser is logged into the target network

### Instagram Unfollow Flow

```
1. Open: browser action=open, url=https://www.instagram.com/[username]/, profile=user
2. Snapshot: verify profile loaded, not an error page
3. Find the "Following" button (indicates Alex follows this person)
4. Click "Following"
5. Confirm "Unfollow" in the dialog that appears
6. Snapshot: verify button now shows "Follow" (not "Following")
7. Log: { username, timestamp, status: "unfollowed" }
8. Wait: random 15–45 seconds
9. Check limits — stop if hit
10. Navigate to next profile
```

**On any unexpected state (CAPTCHA, challenge, missing button):**
- Screenshot the page
- Log the error: `"unexpected_ui": "description"`
- Set `paused: true` in state file
- Stop the session
- Report to Alex

### LinkedIn Unfollow Flow

LinkedIn has two concepts: **Connections** (mutual) and **Following** (one-way).
- For noise-only follows (not a connection): unfollow via the Following list in Settings
- For connections: don't disconnect — just unfollow (stop seeing their posts)
- Never remove a connection without explicit approval

```
1. Navigate to https://www.linkedin.com/mynetwork/network-manager/people-i-follow/
2. Find the account in the following list
3. Click the "Following" toggle to unfollow
4. Confirm if prompted
5. Wait: random 3–10 seconds
6. Continue to next
```

### Twitter/X Unfollow Flow

```
1. Open: browser action=open, url=https://x.com/[username], profile=user
2. Verify profile loaded
3. Find the "Following" button
4. Click it
5. Confirm "Unfollow" in the popup
6. Verify button now shows "Follow"
7. Wait: random 5–15 seconds
8. Continue to next
```

---

## Cron Setup (Optional)

For ongoing automated cleanup, once queue is approved:

```json
{
  "name": "🧹 Instagram Cleanup",
  "schedule": {
    "kind": "cron",
    "expr": "0 10,15,20 * * *",
    "tz": "America/New_York"
  },
  "payload": {
    "kind": "agentTurn",
    "model": "google/gemini-2.0-flash-lite",
    "message": "Run social cleanup for Instagram: unfollow next batch from the queue. Use the social-cleanup skill."
  },
  "sessionTarget": "isolated"
}
```

Adjust schedule per network (LinkedIn: weekdays only; Instagram: any time).

---

## Commands Reference

Run these via exec or have Debra invoke them:

```bash
# Check current queue status
cat /Users/debra/.openclaw/workspace/memory/social-cleanup-state.json | python3 -m json.tool

# Pause all networks
# (update state file manually: set paused=true for target network)

# Resume after error
# (update state file: set paused=false, clear lastError)
```

---

## Safety Checklist (Before Each Run)

- [ ] Queue was approved by Alex
- [ ] State file `paused` is false for target network
- [ ] Today's limit not exceeded
- [ ] No recent errors in `lastError`
- [ ] Browser is logged into the target network
- [ ] Not during any major platform outage

---

## Notes & Gotchas

**Instagram:**
- Never unfollow from the followers list page — always visit the profile and click the button there
- Instagram sometimes shows "Requested" instead of "Following" for private accounts — skip these
- If Alex previously muted someone, they still appear in following — treat the same way

**LinkedIn:**
- "Following" a non-connection is different from being connected — handle separately
- Some LinkedIn profiles don't have a visible "Following" toggle in the profile view — use the Settings → Following page instead

**Twitter/X:**
- X's UI changes frequently — take a snapshot before each session to verify the current UI
- Verified accounts (blue/gold checkmarks) are not automatically "keep" — evaluate on relationship merit

**General:**
- If a profile is suspended, deleted, or unavailable: mark as `skipped` with reason `account_unavailable`
- Private accounts that didn't approve Alex's follow request: mark as `review` — don't unfollow without checking
