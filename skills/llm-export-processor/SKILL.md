---
name: llm-export-processor
description: Process exported conversation archives from ChatGPT, Claude, and Gemini into SecondBrain Obsidian vault and Neo4j graph. Extracts topics, people mentions, action items, and project references. Use when asked to "process my ChatGPT export", "import Claude conversations", "process LLM export", or when given a path to a conversations.json or takeout archive.
---

# llm-export-processor

Parse exported LLM conversations, extract knowledge and relationships, archive to SecondBrain, and build Neo4j graph nodes.

---

## Inputs

- **Export path** (required): Path to the export file or directory
  - ChatGPT: `conversations.json` (from takeout zip)
  - Claude: `conversations.json` (from Settings → Export)
  - Gemini: directory from Google Takeout → `Gemini Apps Activity/`
- **Provider** (required): `chatgpt` | `claude` | `gemini`
- **Date range** (optional): `--after YYYY-MM-DD --before YYYY-MM-DD` to limit processing
- **Mode**: `full` (import all) | `new-only` (skip already-imported based on state file)

---

## Config

```
Neo4j:        bolt://localhost:7687 / neo4j / secondbrain2026
Obsidian:     /Users/debra/SecondBrain/
Conversations: /Users/debra/SecondBrain/Conversations/[provider]/
State file:   /Users/debra/.openclaw/workspace/memory/llm-export-state.json
```

---

## Export Format Reference

### ChatGPT (`conversations.json`)

```json
[
  {
    "id": "uuid",
    "title": "Conversation Title",
    "create_time": 1234567890.0,
    "update_time": 1234567890.0,
    "mapping": {
      "node-uuid": {
        "message": {
          "author": { "role": "user" | "assistant" | "system" },
          "content": { "parts": ["text content"] },
          "create_time": 1234567890.0
        }
      }
    }
  }
]
```

Extract: title, created date, all user+assistant message text in order.

### Claude (`conversations.json`)

```json
[
  {
    "uuid": "uuid",
    "name": "Conversation Title",
    "created_at": "ISO-8601",
    "updated_at": "ISO-8601",
    "chat_messages": [
      {
        "uuid": "msg-uuid",
        "sender": "human" | "assistant",
        "text": "content",
        "created_at": "ISO-8601",
        "attachments": []
      }
    ]
  }
]
```

### Gemini (Google Takeout)

Takeout produces HTML or JSON files in `Gemini Apps Activity/`. Parse the JSON activity records. Format varies — check file structure on first run and adapt.

---

## Encoding Fix (Critical)

Instagram and some other exports have broken latin-1 → UTF-8 double-encoding. Apply this fix when reading any file that looks garbled:

```python
def fix_encoding(text):
    """Fix latin-1 encoded text that was read as UTF-8."""
    try:
        return text.encode('latin-1').decode('utf-8')
    except (UnicodeDecodeError, UnicodeEncodeError):
        return text  # Already correct, leave it
```

Apply `fix_encoding()` to all string fields when parsing exports that show `â€™` instead of `'` or `Ã©` instead of `é`.

---

## Workflow

### Step 1 — Parse Export

```python
import json, os
from datetime import datetime

with open(export_path, 'r', encoding='utf-8', errors='replace') as f:
    data = json.load(f)

conversations = []
for raw in data:
    conv = parse_conversation(raw, provider=provider)
    conversations.append(conv)
```

Each parsed conversation should have:
- `id`: unique ID from source
- `title`: conversation title
- `date`: ISO-8601 date
- `provider`: chatgpt | claude | gemini
- `messages`: list of `{role, text, timestamp}`
- `full_text`: concatenated message text for analysis

### Step 2 — Extract Intelligence

For each conversation, analyze `full_text` to extract:

**Topics & Projects:**
- Named projects: look for "project [name]", "working on [name]", "the [name] app/system/feature"
- Domains: tech/code, personal, business, creative, research
- Keywords: top 10 noun phrases (rough NLP, not perfect)

**People Mentioned:**
- Names that appear as "Alex", "[First Last]", "my [wife/boss/friend] [name]"
- Cross-reference against Neo4j `Person` nodes for fuzzy matching
- Note: "mentioned in conversation" is a weak signal — don't create new Person nodes from this alone

**Action Items:**
- Patterns: "I need to", "TODO:", "follow up on", "remind me to", "next step"
- Extract the sentence/phrase as the action item text

**Sentiment / Category:**
- Is this a coding session? Creative writing? Personal reflection? Technical research? Planning?
- Single label for the vault filing system

### Step 3 — Check for Existing Import

```bash
# Read state file
cat /Users/debra/.openclaw/workspace/memory/llm-export-state.json
```

State file structure:
```json
{
  "imported": {
    "chatgpt": ["conv-id-1", "conv-id-2"],
    "claude": ["conv-id-1"],
    "gemini": []
  },
  "last_run": {
    "chatgpt": "YYYY-MM-DD",
    "claude": null,
    "gemini": null
  },
  "stats": {
    "total_imported": 0,
    "total_people_found": 0
  }
}
```

Skip any conversation whose ID is already in `imported[provider]`.

### Step 4 — Write to Obsidian

For each conversation, create a markdown file:

Path: `/Users/debra/SecondBrain/Conversations/[provider]/YYYY-MM-[title-slug].md`

```markdown
---
id: [conv-id]
provider: [chatgpt|claude|gemini]
title: [Conversation Title]
date: YYYY-MM-DD
topics: [topic1, topic2]
people_mentioned: [Name1, Name2]
category: [coding|planning|personal|research|creative]
action_items: [item1, item2]
tags: [conversation, [provider]]
---

# [Conversation Title]

**Date:** YYYY-MM-DD | **Provider:** [Provider] | **Messages:** N

## Topics

- [extracted topic 1]
- [extracted topic 2]

## Action Items

- [ ] [action item 1]
- [ ] [action item 2]

## People Mentioned

- [[Person Name]] *(see People/PersonName.md)*

## Summary

[2-4 sentence summary of what this conversation was about and any notable outcomes]

---

## Full Conversation

<details>
<summary>Show full transcript</summary>

**[User/Human]:** [message text]

**[Assistant]:** [message text]

...

</details>
```

**Note on full transcripts:** Only include `<details>` block if conversation is < 10,000 words. For very long conversations, omit the full text and note "Transcript omitted (too long)".

### Step 5 — Write to Neo4j

```bash
cypher-shell -a bolt://localhost:7687 -u neo4j -p secondbrain2026 << 'EOF'
// Create Conversation node
MERGE (c:Conversation {id: "[conv-id]"})
SET c.title = "[title]",
    c.date = date("[YYYY-MM-DD]"),
    c.provider = "[provider]",
    c.category = "[category]",
    c.obsidian_path = "Conversations/[provider]/[filename]",
    c.message_count = N,
    c.updated = datetime()

// Link to Alex
MERGE (alex:Person {name: "Alex Abell"})
MERGE (alex)-[:HAD_CONVERSATION {provider: "[provider]", date: date("[YYYY-MM-DD]")}]->(c)

// Link topics (as Tag nodes)
MERGE (t:Tag {name: "[topic]"})
MERGE (c)-[:ABOUT]->(t)

// Link mentioned people (only if Person node already exists)
MATCH (p:Person {name: "[mentioned name]"})
MERGE (c)-[:MENTIONS]->(p)
EOF
```

Create one Cypher block per conversation. Batch in groups of 20 to avoid overwhelming the shell.

### Step 6 — Update State File

```python
import json

with open(state_path, 'r') as f:
    state = json.load(f)

state['imported'][provider].extend([c['id'] for c in new_conversations])
state['last_run'][provider] = today_iso
state['stats']['total_imported'] += len(new_conversations)

with open(state_path, 'w') as f:
    json.dump(state, f, indent=2)
```

### Step 7 — Generate Processing Report

Save to `/Users/debra/SecondBrain/Reflections/Daily/YYYY-MM-DD-llm-export-[provider].md`:

```markdown
---
date: YYYY-MM-DD
type: llm-export-processing
provider: [provider]
---

# 🤖 LLM Export Processing — [Provider] — YYYY-MM-DD

**Processed:** N conversations | **Skipped (already imported):** N | **Failed:** N

---

## 📊 Stats

| Metric | Count |
|--------|-------|
| Total conversations | N |
| Date range | YYYY-MM-DD to YYYY-MM-DD |
| Total messages | N |
| People mentioned | N unique names |
| Action items extracted | N |
| Neo4j nodes created | N |

---

## 🔍 Interesting Findings

- [Notable conversation themes]
- [Recurring topics]
- [People frequently mentioned]
- [Projects that came up repeatedly]

---

## 👥 People Mentioned

| Person | Mentions | Neo4j Match | Notes |
|--------|----------|-------------|-------|
| [Name] | N convs | ✅/❌ | [context] |

---

## ✅ Action Items Extracted

- [ ] [action item] *(from: [conversation title], [date])*
- [ ] ...

---

## ❌ Failed / Skipped

| Conversation | Reason |
|-------------|--------|
| [title] | [parse error / encoding issue / etc] |

---

*Generated by llm-export-processor skill*
```

---

## Edge Cases

- **Malformed JSON**: Try `json.loads(f.read(), strict=False)`. If still failing, log the error and skip that file.
- **Very large exports (> 1GB)**: Process in streaming chunks, don't load entire file into memory
- **Duplicate conversation IDs across exports**: Prefix ID with provider to avoid collisions (`chatgpt:uuid`, `claude:uuid`)
- **No state file yet**: Create it with empty structure on first run
- **Gemini format unknown**: On first Gemini run, inspect the file structure, log what you find, and adapt the parser. Note the format in `references/gemini-format.md` for future runs.
- **Encoding issues**: Apply `fix_encoding()` broadly when any non-ASCII looks garbled
