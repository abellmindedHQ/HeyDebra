---
name: social-data-processor
description: Process social media data exports (Instagram, Facebook, Twitter/X) into SecondBrain Obsidian vault and Neo4j graph. Extracts relationship signals from DMs, builds social graph, cross-references with Google Contacts, and archives content. Use when asked to "process my Instagram export", "import social data", "process Facebook takeout", or given a path to a social media export directory.
---

# social-data-processor

Parse social media data exports, extract relationship signals and social graph data, archive to SecondBrain, cross-reference with Google Contacts, and write to Neo4j.

**Currently supported:** Instagram (full)  
**Planned:** Facebook, Twitter/X (structure defined, parsers stubbed)

---

## Inputs

- **Export path** (required): Path to the extracted export directory
  - Instagram: root of extracted ZIP (contains `messages/`, `followers_and_following/`, `media/`, etc.)
  - Facebook: root of extracted ZIP (contains `messages/`, `friends/`, etc.)
  - Twitter/X: root of extracted ZIP (contains `data/`, `tweets.js`, `direct-messages.js`, etc.)
- **Provider** (required): `instagram` | `facebook` | `twitter`
- **Mode**: `full` (process everything) | `dms-only` | `graph-only` | `content-only`
- **Date range** (optional): `--after YYYY-MM-DD` to limit DM processing

---

## Config

```
Neo4j:        bolt://localhost:7687 / neo4j / secondbrain2026
Obsidian:     /Users/debra/SecondBrain/
Social archive: /Users/debra/SecondBrain/Social/[provider]/
Google acct:  alexander.o.abell@gmail.com (for contacts cross-ref via gog)
State file:   /Users/debra/.openclaw/workspace/memory/social-export-state.json
```

---

## ⚠️ Critical: Instagram Encoding Fix

Instagram exports have **broken text encoding** — they use latin-1 but write bytes as if they're UTF-8. The result is mojibake like `â€™` instead of `'` and `Ã©` instead of `é`.

**Apply this fix to ALL string fields from Instagram JSON:**

```python
def fix_instagram_encoding(text):
    """Fix Instagram's broken UTF-8 → latin-1 double encoding."""
    if not isinstance(text, str):
        return text
    try:
        return text.encode('latin-1').decode('utf-8')
    except (UnicodeDecodeError, UnicodeEncodeError):
        return text  # Already correct
```

Apply recursively to all string values when loading any Instagram JSON file.

---

## Instagram Export Structure

```
instagram-export/
├── messages/
│   ├── inbox/
│   │   └── [username_hash]/
│   │       └── message_1.json
│   └── archived_threads/
│       └── [username_hash]/
│           └── message_1.json
├── followers_and_following/
│   ├── followers_1.json
│   └── following.json
├── likes/
│   └── liked_posts.json
├── media/
│   └── posts/
└── personal_information/
    └── personal_information.json
```

### Instagram DM Format

```json
{
  "participants": [
    {"name": "Alex Abell"},
    {"name": "Other Person"}
  ],
  "messages": [
    {
      "sender_name": "Alex Abell",
      "timestamp_ms": 1234567890000,
      "content": "message text",
      "type": "Generic" | "Share" | "Call"
    }
  ],
  "title": "Other Person",
  "thread_type": "Regular" | "RegularGroup"
}
```

### Instagram Followers Format

```json
{
  "relationships_followers": [
    {
      "string_list_data": [
        {
          "href": "https://www.instagram.com/[username]/",
          "value": "[username]",
          "timestamp": 1234567890
        }
      ]
    }
  ]
}
```

---

## Workflow

### Step 1 — Load and Validate Export

```python
import os, json, glob

# Verify expected structure exists
required_paths = {
    'instagram': ['messages/inbox', 'followers_and_following'],
    'facebook': ['messages/inbox', 'friends'],
    'twitter': ['data']
}

assert os.path.exists(os.path.join(export_path, required_paths[provider][0])), \
    f"Export directory doesn't look like a {provider} export"
```

### Step 2 — Parse DM Conversations

**Instagram:**
```python
dm_files = glob.glob(f"{export_path}/messages/inbox/*/message_1.json")
# Also check archived:
dm_files += glob.glob(f"{export_path}/messages/archived_threads/*/message_1.json")

conversations = []
for path in dm_files:
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Fix encoding
    data = fix_instagram_encoding_recursive(data)
    
    # Extract participants (exclude self)
    other_participants = [p['name'] for p in data['participants'] 
                         if p['name'] != 'Alex Abell']
    
    conversations.append({
        'participants': other_participants,
        'title': data.get('title', ''),
        'is_group': data.get('thread_type') == 'RegularGroup',
        'message_count': len(data['messages']),
        'first_message': min(m['timestamp_ms'] for m in data['messages']),
        'last_message': max(m['timestamp_ms'] for m in data['messages']),
        'messages': data['messages']
    })
```

**Relationship signal scoring** (for non-group DMs):
- 1-5 messages: `ACQUAINTANCE`
- 6-20 messages: `LIGHT_CONTACT`
- 21-100 messages: `REGULAR_CONTACT`
- 100+ messages: `CLOSE_CONTACT`
- Any exchange within last 6 months: add `recent` flag

### Step 3 — Parse Social Graph

**Instagram followers/following:**
```python
# Following (people Alex follows)
with open(f"{export_path}/followers_and_following/following.json") as f:
    following_data = json.load(f)

following = []
for entry in following_data.get('relationships_following', []):
    for item in entry.get('string_list_data', []):
        following.append({
            'username': item['value'],
            'url': item['href'],
            'followed_since': item['timestamp']
        })

# Followers (people who follow Alex)
followers = []  # Similar structure from followers_1.json, followers_2.json, etc.
```

Compute:
- **Mutual follows**: in both following and followers
- **Alex follows but they don't follow back**: one-way
- **They follow Alex but he doesn't follow back**: fan/stranger

### Step 4 — Cross-Reference Google Contacts

```bash
gog contacts list --account alexander.o.abell@gmail.com --format json --limit 2000
```

Build lookup: `{name_lower: contact_data, email_lower: contact_data}`.

For each DM person, try to match:
1. Exact name match (after encoding fix)
2. Fuzzy name match (last name + partial first name)
3. Instagram username vs contact notes

Flag matches for Neo4j relationship strengthening.

### Step 5 — Write to Neo4j

```bash
cypher-shell -a bolt://localhost:7687 -u neo4j -p secondbrain2026 << 'EOF'
// Create SocialProfile node
MERGE (sp:SocialProfile {platform: "instagram", username: "[username]"})
SET sp.display_name = "[display name]",
    sp.url = "https://www.instagram.com/[username]/",
    sp.follower_relationship = "[mutual|following|follower]",
    sp.updated = datetime()

// Try to link to existing Person node
MATCH (p:Person)
WHERE toLower(p.name) = toLower("[display name]")
   OR p.instagram = "[username]"
MERGE (p)-[:HAS_PROFILE]->(sp)

// DM relationship
MERGE (alex:Person {name: "Alex Abell"})
MERGE (alex)-[:DM_CONVERSATION {
  platform: "instagram",
  message_count: N,
  strength: "[ACQUAINTANCE|LIGHT_CONTACT|REGULAR_CONTACT|CLOSE_CONTACT]",
  last_message_date: date("[YYYY-MM-DD]"),
  is_group: false
}]->(sp)
EOF
```

### Step 6 — Archive to Obsidian

**DM summaries** (for REGULAR_CONTACT and above):

Path: `/Users/debra/SecondBrain/Social/instagram/dms/[display-name-slug].md`

```markdown
---
platform: instagram
contact: [Display Name]
username: [username]
relationship_strength: [REGULAR_CONTACT|CLOSE_CONTACT]
message_count: N
first_message: YYYY-MM-DD
last_message: YYYY-MM-DD
mutual_follow: true|false
google_contact_match: true|false
tags: [social, instagram, dm]
---

# [Display Name] (@[username])

**Platform:** Instagram | **Messages:** N | **Last contact:** YYYY-MM-DD
**Mutual follow:** Yes/No | **Google Contact:** Yes/No

## Relationship Summary

[Brief description of the DM relationship — how many messages, rough topic, when active]

## Recent Context

[2-3 notable things from recent messages — topics, plans mentioned, etc.]
```

**Social graph summary:**

Path: `/Users/debra/SecondBrain/Social/instagram/social-graph-[YYYY-MM-DD].md`

```markdown
---
date: YYYY-MM-DD
type: social-graph
platform: instagram
---

# Instagram Social Graph — YYYY-MM-DD

**Following:** N | **Followers:** N | **Mutual:** N

## Key Stats

- Mutual follows with Google Contacts: N
- People I DM regularly (100+ messages): N  
- People I follow but don't know IRL: N

## DM Relationship Map

| Name | Username | Messages | Strength | In Contacts | Neo4j |
|------|----------|----------|----------|-------------|-------|
| [Name] | @[user] | N | [level] | ✅/❌ | ✅/❌ |

## Enrichment Candidates

People worth adding to Google Contacts / Neo4j:
- @[username] ([display name]) — N messages, mutual follow
```

### Step 7 — Generate Processing Report

Save to `/Users/debra/SecondBrain/Reflections/Daily/YYYY-MM-DD-social-[provider].md`:

```markdown
---
date: YYYY-MM-DD
type: social-export-processing
provider: [provider]
---

# 📱 Social Export Processing — [Provider] — YYYY-MM-DD

**DM conversations:** N | **Unique people:** N | **Following:** N | **Followers:** N
**Google Contact matches:** N | **Neo4j nodes created:** N | **Neo4j edges created:** N

---

## 🔍 Key Findings

- [Relationship patterns noticed]
- [People frequently communicated with]
- [Social graph observations]

---

## 👥 People Found (by relationship strength)

### Close Contacts (100+ messages)
- [Name] (@username) — N messages, last: YYYY-MM-DD

### Regular Contacts (21-100 messages)
- [Name] (@username) — N messages

---

## 🌐 Social Graph Highlights

- Following: N | Followers: N | Mutual: N
- Following but not mutual: N
- In Google Contacts AND following: N

---

## 🌱 Enrichment Recommendations

People worth adding or enriching in contacts/graph:
- @[username] ([name if known]) — [why worth adding]

---

## ⚠️ Encoding Issues

- N messages had encoding errors (fixed automatically)
- N messages still had unresolvable characters (logged)

---

*Generated by social-data-processor skill*
```

---

## Facebook (Stub — Future)

Export structure: `messages/inbox/[name_hash]/message_1.json`  
Format similar to Instagram but without encoding issues.  
Status: **Not yet implemented.** When adding Facebook support, check `references/facebook-format.md` and follow the same workflow pattern as Instagram.

## Twitter/X (Stub — Future)

Export files: `data/direct-messages.js`, `data/following.js`, `data/follower.js`, `data/tweets.js`  
Note: Twitter exports use `.js` files that are JavaScript module assignments — strip the `window.YTD.direct_messages.part0 = ` prefix before JSON parsing.  
Status: **Not yet implemented.**

---

## Edge Cases

- **Group DMs with strangers**: Process for message count only, don't create individual Person nodes from group participants you don't recognize
- **Deleted/unknown senders**: Some messages have `[Unknown]` or numeric sender IDs — skip person extraction, keep message count
- **Very large exports (10k+ messages per person)**: Don't include full transcripts in Obsidian — summary only
- **Name collisions**: Same display name for different people — use username as primary key, flag for manual review
- **No state file**: Create on first run with empty structure
