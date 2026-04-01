#!/usr/bin/env python3
"""
ChatGPT ORNL Re-Import: Wikipedia of Alex approach
Processes ChatGPT markdown-format exports into rich SecondBrain content.
Handles the markdown export format (not JSON).
"""

import json
import os
import sys
import time
import re
from datetime import datetime
from pathlib import Path
import urllib.request
import urllib.error

# Paths
EXPORT_DIRS = [
    Path.home() / "Downloads/ornl-chatgpt/export1",
    Path.home() / "Downloads/ornl-chatgpt/export2",
    Path.home() / "Downloads/ornl-chatgpt/export3",
]
SECONDBRAIN = Path.home() / "SecondBrain"
PEOPLE_DIR = SECONDBRAIN / "People"
LLM_NOTES_DIR = SECONDBRAIN / "Reflections/LLM-Processing/ChatGPT-ORNL"
GTD_INBOX = SECONDBRAIN / "GTD/inbox.md"
STATE_FILE = Path.home() / ".openclaw/workspace/memory/chatgpt-ornl-reimport-state.json"
LOG_FILE = Path("/tmp/chatgpt-ornl-reimport.log")

# Ensure dirs
for d in [PEOPLE_DIR, LLM_NOTES_DIR, GTD_INBOX.parent]:
    d.mkdir(parents=True, exist_ok=True)

def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

def load_state():
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {"processed": [], "people_updated": [], "stats": {"conversations": 0, "people_enriched": 0, "notes_created": 0, "action_items": 0}}

def save_state(state):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2))

def get_existing_people():
    people = []
    for f in PEOPLE_DIR.glob("*.md"):
        people.append(f.stem)
    return people

def call_llm(prompt, max_retries=3):
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        log("  ERROR: No OPENAI_API_KEY set")
        return None
    
    for attempt in range(max_retries):
        try:
            payload = json.dumps({
                "model": "gpt-4o",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3,
                "max_tokens": 2000
            })
            
            req = urllib.request.Request(
                "https://api.openai.com/v1/chat/completions",
                data=payload.encode("utf-8"),
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}"
                }
            )
            
            with urllib.request.urlopen(req, timeout=90) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                content = result["choices"][0]["message"]["content"]
                if content.strip():
                    return content.strip()
                else:
                    log(f"  LLM attempt {attempt+1}: empty content")
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")[:200]
            log(f"  LLM HTTP {e.code} attempt {attempt+1}: {body}")
            if e.code == 429:
                time.sleep(10 * (attempt + 1))
            else:
                time.sleep(2 ** attempt)
        except Exception as e:
            log(f"  LLM error attempt {attempt+1}: {e}")
            time.sleep(2 ** attempt)
    return None

def parse_markdown_conversation(filepath):
    """Parse a ChatGPT markdown export file into a conversation dict"""
    content = filepath.read_text(errors="replace")
    
    # Extract title from first heading
    title_match = re.match(r'^#\s+(.+)$', content, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else filepath.stem
    
    # Clean up ChatGPT- prefix from filename
    if title.startswith("ChatGPT-"):
        title = title[8:]
    title = title.replace("_", " ")
    
    # Extract messages (#### You: and #### ChatGPT:)
    messages = []
    # Split by #### headers
    parts = re.split(r'^####\s+(You|ChatGPT):\s*$', content, flags=re.MULTILINE)
    
    for i in range(1, len(parts) - 1, 2):
        role = parts[i].strip()
        text = parts[i + 1].strip()
        # Strip base64 images to save tokens
        text = re.sub(r'!\[image\]\(data:image/[^)]+\)', '[image]', text)
        if text:
            messages.append({"role": role, "text": text[:3000]})
    
    return {
        "filename": filepath.name,
        "title": title,
        "messages": messages,
        "source": "ChatGPT-ORNL (abellao@ornl.gov)"
    }

def process_conversation(convo, existing_people):
    title = convo["title"]
    messages = convo["messages"]
    
    if not messages:
        return None
    
    convo_text = f"Title: {title}\nSource: ORNL work account (abellao@ornl.gov)\n\n"
    for msg in messages:
        role = "Alex" if msg["role"] == "You" else "ChatGPT"
        convo_text += f"**{role}:** {msg['text'][:3000]}\n\n"
    
    if len(convo_text) > 15000:
        convo_text = convo_text[:15000] + "\n\n[TRUNCATED]"
    
    existing_people_str = ", ".join(existing_people[:100])
    
    prompt = f"""You are processing a ChatGPT conversation from Alex Abell's WORK account (abellao@ornl.gov) at Oak Ridge National Laboratory. This is his ORNL/work ChatGPT, so most conversations will be work-related.

EXISTING PEOPLE IN VAULT: {existing_people_str}

CONVERSATION:
{convo_text}

Extract the following as JSON (and ONLY JSON, no markdown fencing):
{{
  "summary": "2-3 sentence summary of what this conversation is about and why it matters",
  "domain": "one of: Work/ORNL, Work/ServiceNow, Work/WordPress, Work/AppDev, Work/Transformation, Work/Leadership, Technology/AI, Technology/Web, Business/Consulting, Personal/Other, Reference, Other",
  "key_insights": ["insight 1", "insight 2"],
  "decisions_made": ["decision 1 with context"],
  "people_mentioned": [
    {{
      "name": "Full Name",
      "context": "what we learned about them",
      "is_existing": true/false,
      "relationship_to_alex": "brief description"
    }}
  ],
  "action_items": [
    {{
      "task": "what needs to be done",
      "status": "completed/pending/unknown",
      "assigned_to": "who"
    }}
  ],
  "projects_referenced": ["project name"],
  "wikilinks": ["[[Person Name]]", "[[Project Name]]", "[[Concept]]"],
  "importance": "high/medium/low",
  "tags": ["tag1", "tag2"]
}}

Be thorough but concise. This is Alex's WORK account so focus on ORNL-relevant insights. If trivial, set importance to "low"."""

    result = call_llm(prompt)
    if not result:
        return None
    
    try:
        json_match = re.search(r'\{[\s\S]*\}', result)
        if json_match:
            data = json.loads(json_match.group())
        else:
            log(f"  No JSON found in LLM response")
            return None
    except json.JSONDecodeError as e:
        log(f"  JSON parse error: {e}")
        return None
    
    return data

def write_obsidian_note(convo, extracted):
    title = convo["title"]
    source = convo["source"]
    
    safe_name = re.sub(r'[^\w\s-]', '', title)[:80].strip()
    if not safe_name:
        safe_name = convo["filename"][:40]
    
    filename = f"{safe_name}.md"
    filepath = LLM_NOTES_DIR / filename
    
    if filepath.exists():
        return filepath
    
    domain = extracted.get("domain", "Work/ORNL")
    summary = extracted.get("summary", "")
    insights = extracted.get("key_insights", [])
    decisions = extracted.get("decisions_made", [])
    people = extracted.get("people_mentioned", [])
    actions = extracted.get("action_items", [])
    wikilinks = extracted.get("wikilinks", [])
    tags = extracted.get("tags", [])
    importance = extracted.get("importance", "medium")
    
    note = f"""---
title: "{title}"
source: {source}
domain: {domain}
importance: {importance}
tags: [{', '.join(tags + ['chatgpt-ornl-import', 'llm-conversation', 'ornl'])}]
created: {datetime.now().strftime('%Y-%m-%d')}
---

# {title}

> 🏷️ {domain} | ⭐ {importance} | 🏢 ORNL

## Summary

{summary}

"""
    
    if insights:
        note += "## Key Insights\n\n"
        for i in insights:
            note += f"- {i}\n"
        note += "\n"
    
    if decisions:
        note += "## Decisions & Rationale\n\n"
        for d in decisions:
            note += f"- {d}\n"
        note += "\n"
    
    if people:
        note += "## People Referenced\n\n"
        for p in people:
            pname = p.get("name", "Unknown")
            ctx = p.get("context", "")
            note += f"- [[{pname}]]: {ctx}\n"
        note += "\n"
    
    if actions:
        note += "## Action Items\n\n"
        for a in actions:
            status = "x" if a.get("status") == "completed" else " "
            note += f"- [{status}] {a.get('task', '')} (assigned: {a.get('assigned_to', 'Alex')})\n"
        note += "\n"
    
    if wikilinks:
        note += f"## Related\n\n{' · '.join(wikilinks)}\n"
    
    filepath.write_text(note)
    return filepath

def enrich_people_card(person_info):
    name = person_info.get("name", "")
    context = person_info.get("context", "")
    
    if not name or not context:
        return False
    
    card_path = PEOPLE_DIR / f"{name}.md"
    if not card_path.exists():
        return False
    
    existing = card_path.read_text()
    
    if context[:50] in existing:
        return False
    
    section_header = "## ChatGPT ORNL Import Context"
    today = datetime.now().strftime("%Y-%m-%d")
    new_entry = f"- ({today}) {context}"
    
    if section_header in existing:
        existing = existing.replace(section_header, f"{section_header}\n{new_entry}")
    else:
        existing += f"\n\n{section_header}\n{new_entry}\n"
    
    card_path.write_text(existing)
    return True

def append_action_items(actions, convo_title):
    if not actions:
        return 0
    
    pending = [a for a in actions if a.get("status") != "completed"]
    if not pending:
        return 0
    
    today = datetime.now().strftime("%Y-%m-%d %H:%M")
    with open(GTD_INBOX, "a") as f:
        for a in pending:
            task = a.get("task", "")
            assigned = a.get("assigned_to", "Alex")
            f.write(f"- [ ] {task} — assigned to: {assigned}, source: chatgpt-ornl:{convo_title}, captured: {today}\n")
    
    return len(pending)

def main():
    log("=" * 60)
    log("ChatGPT ORNL Re-Import: Wikipedia of Alex Approach")
    log("=" * 60)
    
    state = load_state()
    processed_files = set(state["processed"])
    
    # Collect all markdown files
    all_files = []
    for d in EXPORT_DIRS:
        if d.exists():
            for f in sorted(d.glob("*.md")):
                if f.name not in processed_files:
                    all_files.append(f)
    
    log(f"Total files found: {sum(len(list(d.glob('*.md'))) for d in EXPORT_DIRS if d.exists())}")
    log(f"Already processed: {len(processed_files)}")
    log(f"To process: {len(all_files)}")
    log("")
    
    existing_people = get_existing_people()
    log(f"Existing people cards: {len(existing_people)}")
    
    notes_created = state["stats"].get("notes_created", 0)
    people_enriched = state["stats"].get("people_enriched", 0)
    action_items_total = state["stats"].get("action_items", 0)
    
    for i, filepath in enumerate(all_files):
        convo = parse_markdown_conversation(filepath)
        msg_count = len(convo["messages"])
        log(f"[{i+1}/{len(all_files)}] {convo['title'][:60]} ({msg_count} msgs)")
        
        if msg_count == 0:
            log(f"  ⚠️ No messages, skipping")
            state["processed"].append(filepath.name)
            save_state(state)
            continue
        
        extracted = process_conversation(convo, existing_people)
        if not extracted:
            log(f"  ⚠️ Extraction failed, skipping")
            state["processed"].append(filepath.name)
            save_state(state)
            continue
        
        importance = extracted.get("importance", "medium")
        domain = extracted.get("domain", "Work/ORNL")
        log(f"  Domain: {domain} | Importance: {importance}")
        
        note_path = write_obsidian_note(convo, extracted)
        if note_path:
            notes_created += 1
            log(f"  📝 Note: {note_path.name}")
        
        for person in extracted.get("people_mentioned", []):
            if person.get("is_existing") and enrich_people_card(person):
                people_enriched += 1
                log(f"  👤 Enriched: {person.get('name')}")
        
        if importance in ("high", "medium"):
            n_actions = append_action_items(extracted.get("action_items", []), convo["title"])
            if n_actions:
                action_items_total += n_actions
                log(f"  ✅ {n_actions} action items")
        
        state["processed"].append(filepath.name)
        state["stats"]["conversations"] = len(state["processed"])
        state["stats"]["notes_created"] = notes_created
        state["stats"]["people_enriched"] = people_enriched
        state["stats"]["action_items"] = action_items_total
        save_state(state)
        
        time.sleep(1)
    
    log("")
    log("=" * 60)
    log("COMPLETE")
    log(f"  Conversations processed: {len(state['processed'])}")
    log(f"  Notes created: {notes_created}")
    log(f"  People enriched: {people_enriched}")
    log(f"  Action items captured: {action_items_total}")
    log("=" * 60)

if __name__ == "__main__":
    main()
