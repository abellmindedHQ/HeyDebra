#!/usr/bin/env python3
"""
Process ChatGPT ORNL markdown exports into SecondBrain Obsidian vault.
These are markdown-format exports (not JSON), so we parse the .md files directly.
"""

import os
import re
import json
import hashlib
from datetime import datetime
from pathlib import Path

# Config
EXPORT_DIRS = [
    "/Users/debra/Downloads/ornl-chatgpt/export1",
    "/Users/debra/Downloads/ornl-chatgpt/export2",
    "/Users/debra/Downloads/ornl-chatgpt/export3",
]
OBSIDIAN_DIR = "/Users/debra/SecondBrain/Conversations/chatgpt-ornl"
REPORT_DIR = "/Users/debra/SecondBrain/Reflections/Daily"
STATE_FILE = "/Users/debra/.openclaw/workspace/memory/llm-export-state.json"
PROVIDER = "chatgpt-ornl"
TODAY = datetime.now().strftime("%Y-%m-%d")

# Ensure directories exist
os.makedirs(OBSIDIAN_DIR, exist_ok=True)
os.makedirs(REPORT_DIR, exist_ok=True)

# Load state
if os.path.exists(STATE_FILE):
    with open(STATE_FILE, 'r') as f:
        state = json.load(f)
else:
    state = {"imported": {}, "last_run": {}, "stats": {"total_imported": 0}}

if PROVIDER not in state["imported"]:
    state["imported"][PROVIDER] = []

imported_ids = set(state["imported"].get(PROVIDER, []))

# Also check the chatgpt-ornl-reimport-state for any already processed
reimport_state_file = "/Users/debra/.openclaw/workspace/memory/chatgpt-ornl-reimport-state.json"
if os.path.exists(reimport_state_file):
    with open(reimport_state_file, 'r') as f:
        reimport_state = json.load(f)
    reimport_ids = set(reimport_state.get("imported", {}).get("chatgpt", []))
else:
    reimport_ids = set()

def slugify(text, max_len=60):
    """Create a filesystem-safe slug from text."""
    slug = re.sub(r'[^\w\s-]', '', text.lower().strip())
    slug = re.sub(r'[\s_]+', '-', slug)
    return slug[:max_len].rstrip('-')

def generate_id(filepath):
    """Generate a stable ID from file path."""
    return hashlib.md5(filepath.encode()).hexdigest()

def extract_title_from_filename(filename):
    """Extract a readable title from ChatGPT export filename."""
    # Format: ChatGPT-Title_With_Underscores.md or ChatGPT-Title_With_Underscores (1).md
    name = filename.replace('.md', '')
    name = re.sub(r'\s*\(\d+\)\s*$', '', name)  # Remove (1) suffix
    if name.startswith('ChatGPT-'):
        name = name[8:]
    name = name.replace('_', ' ')
    return name

def parse_chatgpt_markdown(filepath):
    """Parse a ChatGPT markdown export file."""
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()
    
    # Fix encoding issues
    content = fix_encoding(content)
    
    lines = content.split('\n')
    
    # Extract title from first heading
    title = None
    for line in lines:
        if line.startswith('# '):
            title = line[2:].strip()
            break
    
    if not title:
        title = extract_title_from_filename(os.path.basename(filepath))
    
    # Parse messages
    messages = []
    current_role = None
    current_text = []
    
    for line in lines:
        if line.startswith('#### You:'):
            if current_role:
                messages.append({"role": current_role, "text": '\n'.join(current_text).strip()})
            current_role = "user"
            current_text = []
        elif line.startswith('#### ChatGPT:'):
            if current_role:
                messages.append({"role": current_role, "text": '\n'.join(current_text).strip()})
            current_role = "assistant"
            current_text = []
        else:
            if current_role:
                current_text.append(line)
    
    # Don't forget the last message
    if current_role and current_text:
        messages.append({"role": current_role, "text": '\n'.join(current_text).strip()})
    
    # Build full text for analysis
    full_text = '\n'.join(m['text'] for m in messages)
    word_count = len(full_text.split())
    
    return {
        "title": title,
        "messages": messages,
        "message_count": len(messages),
        "word_count": word_count,
        "full_text": full_text,
    }

def fix_encoding(text):
    """Fix latin-1 encoded text that was read as UTF-8."""
    try:
        return text.encode('latin-1').decode('utf-8')
    except (UnicodeDecodeError, UnicodeEncodeError):
        return text

def categorize(title, full_text):
    """Simple categorization based on keywords."""
    text_lower = (title + ' ' + full_text[:2000]).lower()
    
    if any(w in text_lower for w in ['servicenow', 'csdm', 'pdi', 'portfolio', 'cmdb']):
        return 'servicenow'
    elif any(w in text_lower for w in ['code', 'function', 'api', 'javascript', 'python', 'css', 'html', 'react', 'component']):
        return 'coding'
    elif any(w in text_lower for w in ['reorg', 'restructur', 'team', 'leadership', 'management', 'division']):
        return 'management'
    elif any(w in text_lower for w in ['resume', 'self-assessment', 'performance', 'review']):
        return 'career'
    elif any(w in text_lower for w in ['draft', 'email', 'message', 'write']):
        return 'writing'
    elif any(w in text_lower for w in ['budget', 'salary', 'compensation', 'finance', 'transfer']):
        return 'finance'
    else:
        return 'general'

def extract_topics(title, full_text):
    """Extract rough topics from content."""
    topics = []
    text_lower = (title + ' ' + full_text[:3000]).lower()
    
    topic_keywords = {
        'ServiceNow': ['servicenow', 'csdm', 'pdi'],
        'Application Portfolio': ['portfolio', 'application rationalization', 'app portfolio'],
        'Web Development': ['css', 'html', 'javascript', 'react', 'component', 'wordpress'],
        'Team Management': ['reorg', 'restructur', 'team', 'division'],
        'ORNL': ['ornl', 'oak ridge', 'lab'],
        'Data': ['csv', 'data', 'export', 'import'],
        'Career': ['self-assessment', 'performance', 'resume'],
    }
    
    for topic, keywords in topic_keywords.items():
        if any(k in text_lower for k in keywords):
            topics.append(topic)
    
    return topics[:5] if topics else ['Work']

def write_obsidian_note(conv_id, title, parsed, category, topics):
    """Write a conversation to an Obsidian note."""
    slug = slugify(title)
    filename = f"{slug}.md"
    filepath = os.path.join(OBSIDIAN_DIR, filename)
    
    # Handle duplicates
    if os.path.exists(filepath):
        filepath = os.path.join(OBSIDIAN_DIR, f"{slug}-{conv_id[:8]}.md")
    
    topics_str = ', '.join(topics)
    
    note = f"""---
id: {conv_id}
provider: chatgpt-ornl
title: "{title.replace('"', "'")}"
date: unknown
topics: [{topics_str}]
category: {category}
tags: [conversation, chatgpt-ornl, ornl]
---

# {title}

**Provider:** ChatGPT (ORNL) | **Messages:** {parsed['message_count']} | **Words:** {parsed['word_count']}

## Topics

{chr(10).join('- ' + t for t in topics)}

## Summary

ChatGPT conversation from ORNL account. Category: {category}.

---

"""
    
    # Add transcript for shorter conversations
    if parsed['word_count'] < 10000:
        note += "## Full Conversation\n\n"
        for msg in parsed['messages']:
            role_label = "**User:**" if msg['role'] == 'user' else "**ChatGPT:**"
            # Truncate very long individual messages
            text = msg['text'][:3000]
            if len(msg['text']) > 3000:
                text += "\n\n*(message truncated)*"
            note += f"{role_label} {text}\n\n"
    else:
        note += "*Transcript omitted (too long - {} words)*\n".format(parsed['word_count'])
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(note)
    
    return filepath

# Process all exports
new_conversations = []
skipped = 0
failed = 0
all_categories = {}
all_topics = {}

for export_dir in EXPORT_DIRS:
    if not os.path.exists(export_dir):
        continue
    
    for filename in sorted(os.listdir(export_dir)):
        if not filename.endswith('.md'):
            continue
        
        filepath = os.path.join(export_dir, filename)
        conv_id = generate_id(filepath)
        
        if conv_id in imported_ids or conv_id in reimport_ids:
            skipped += 1
            continue
        
        try:
            parsed = parse_chatgpt_markdown(filepath)
            
            if parsed['message_count'] == 0:
                failed += 1
                continue
            
            title = parsed['title']
            category = categorize(title, parsed['full_text'])
            topics = extract_topics(title, parsed['full_text'])
            
            # Write Obsidian note
            note_path = write_obsidian_note(conv_id, title, parsed, category, topics)
            
            new_conversations.append({
                "id": conv_id,
                "title": title,
                "category": category,
                "topics": topics,
                "message_count": parsed['message_count'],
                "word_count": parsed['word_count'],
                "source_file": filename,
            })
            
            # Track stats
            all_categories[category] = all_categories.get(category, 0) + 1
            for t in topics:
                all_topics[t] = all_topics.get(t, 0) + 1
            
        except Exception as e:
            failed += 1
            print(f"FAILED: {filename}: {e}")

# Update state
state["imported"][PROVIDER].extend([c["id"] for c in new_conversations])
state["last_run"][PROVIDER] = TODAY
state["stats"]["total_imported"] = state["stats"].get("total_imported", 0) + len(new_conversations)
state["stats"]["chatgpt-ornl-md-count"] = len(new_conversations)

with open(STATE_FILE, 'w') as f:
    json.dump(state, f, indent=2)

# Generate report
report = f"""---
date: {TODAY}
type: llm-export-processing
provider: chatgpt-ornl
format: markdown
---

# 🤖 LLM Export Processing — ChatGPT ORNL (Markdown) — {TODAY}

**Processed:** {len(new_conversations)} conversations | **Skipped (already imported):** {skipped} | **Failed:** {failed}

---

## 📊 Stats

- Total conversations processed: {len(new_conversations)}
- Total messages across all: {sum(c['message_count'] for c in new_conversations)}
- Total words: {sum(c['word_count'] for c in new_conversations):,}
- Format: Markdown exports (not JSON)
- Source: /Users/debra/Downloads/ornl-chatgpt/ (3 export batches)

---

## 📁 Categories

{chr(10).join(f'- **{cat}**: {count} conversations' for cat, count in sorted(all_categories.items(), key=lambda x: -x[1]))}

---

## 🏷️ Top Topics

{chr(10).join(f'- **{topic}**: {count} mentions' for topic, count in sorted(all_topics.items(), key=lambda x: -x[1])[:15])}

---

## ⚠️ Notes

- Neo4j was **offline** during this run — no graph nodes were created
- These exports are in **markdown format** (not the standard conversations.json)
- Dates are unknown (markdown exports don't include timestamps)
- No new Claude personal or Claude ORNL (JSON) exports found
- No ChatGPT JSON exports found
- No Gemini exports found

---

## 📝 Sample Conversations

{chr(10).join(f'- [{c["title"]}] ({c["category"]}, {c["message_count"]} msgs)' for c in new_conversations[:20])}
{"- ... and {} more".format(len(new_conversations) - 20) if len(new_conversations) > 20 else ""}

---

*Generated by llm-export-processor skill — {TODAY} 10:00 PM ET*
"""

report_path = os.path.join(REPORT_DIR, f"{TODAY}-llm-export-chatgpt-ornl.md")
with open(report_path, 'w', encoding='utf-8') as f:
    f.write(report)

# Print summary
print(f"✅ Processed: {len(new_conversations)} new conversations")
print(f"⏭️  Skipped: {skipped} already imported")
print(f"❌ Failed: {failed}")
print(f"📄 Report: {report_path}")
print(f"📁 Notes saved to: {OBSIDIAN_DIR}")
