#!/usr/bin/env python3
"""
ChatGPT Re-Import: Wikipedia of Alex approach
Processes ChatGPT export conversations into rich SecondBrain content.
"""

import json
import os
import sys
import time
import re
from datetime import datetime
from pathlib import Path
import subprocess

# Paths
EXPORT_PATH = Path.home() / "Downloads/data-2026-03-24-12-55-28-batch-0000/conversations.json"
SECONDBRAIN = Path.home() / "SecondBrain"
PEOPLE_DIR = SECONDBRAIN / "People"
PROJECTS_DIR = SECONDBRAIN / "Projects"
LLM_NOTES_DIR = SECONDBRAIN / "Reflections/LLM-Processing/ChatGPT"
GTD_INBOX = SECONDBRAIN / "GTD/inbox.md"
STATE_FILE = Path.home() / ".openclaw/workspace/memory/chatgpt-reimport-state.json"
LOG_FILE = Path("/tmp/chatgpt-reimport.log")

# Ensure dirs
for d in [PEOPLE_DIR, PROJECTS_DIR, LLM_NOTES_DIR, GTD_INBOX.parent]:
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
    """Get list of existing people card names"""
    people = []
    for f in PEOPLE_DIR.glob("*.md"):
        people.append(f.stem)
    return people

def call_llm(prompt, max_retries=3):
    """Call OpenAI API directly via curl"""
    import urllib.request
    import urllib.error
    
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

def process_conversation(convo, existing_people):
    """Process a single conversation into SecondBrain content"""
    name = convo.get("name", "Untitled")
    uuid = convo["uuid"]
    created = convo.get("created_at", "")
    messages = convo.get("chat_messages", [])
    
    if not messages:
        return None
    
    # Build conversation text
    convo_text = f"Title: {name}\nDate: {created}\n\n"
    for msg in messages:
        sender = msg.get("sender", "unknown")
        text = msg.get("text", "")
        if text:
            role = "Alex" if sender == "human" else "ChatGPT"
            convo_text += f"**{role}:** {text[:3000]}\n\n"
    
    # Truncate if too long
    if len(convo_text) > 15000:
        convo_text = convo_text[:15000] + "\n\n[TRUNCATED - conversation continues...]"
    
    existing_people_str = ", ".join(existing_people[:100])
    
    prompt = f"""You are processing a ChatGPT conversation for Alex Abell's SecondBrain knowledge graph (Obsidian vault).

EXISTING PEOPLE IN VAULT: {existing_people_str}

CONVERSATION:
{convo_text}

Extract the following as JSON (and ONLY JSON, no markdown fencing):
{{
  "summary": "2-3 sentence summary of what this conversation is about and why it matters to Alex",
  "domain": "one of: Work/ORNL, Product/Mirror, Product/Pools, Product/SecondBrain, Product/HeyDebra, Business/Consulting, Business/Abellminded, Personal/Relationships, Personal/Health, Personal/Finance, Personal/Parenting, Creative/Writing, Creative/Music, Creative/Design, Technology/AI, Technology/Web, Community/Knoxville, Community/Entrepreneurship, Reference, Other",
  "key_insights": ["insight 1", "insight 2"],
  "decisions_made": ["decision 1 with context"],
  "people_mentioned": [
    {{
      "name": "Full Name",
      "context": "what we learned about them from this conversation",
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

Be thorough but concise. Focus on UNIQUE information that enriches understanding of Alex's world. If the conversation is trivial (test, joke, one-liner), set importance to "low" and keep everything minimal."""

    result = call_llm(prompt)
    if not result:
        return None
    
    # Parse JSON from response
    try:
        # Try to find JSON in the response
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

def write_obsidian_note(convo, extracted, existing_notes):
    """Write a rich Obsidian note for the conversation"""
    name = convo.get("name", "Untitled") or "Untitled"
    created = convo.get("created_at", "")
    date_str = created[:10] if created else "unknown-date"
    
    # Clean filename
    safe_name = re.sub(r'[^\w\s-]', '', name)[:80].strip()
    if not safe_name:
        safe_name = convo["uuid"][:8]
    
    filename = f"{date_str}-{safe_name}.md"
    filepath = LLM_NOTES_DIR / filename
    
    # Skip if already exists
    if filepath.exists():
        return filepath
    
    domain = extracted.get("domain", "Other")
    summary = extracted.get("summary", "")
    insights = extracted.get("key_insights", [])
    decisions = extracted.get("decisions_made", [])
    people = extracted.get("people_mentioned", [])
    actions = extracted.get("action_items", [])
    wikilinks = extracted.get("wikilinks", [])
    tags = extracted.get("tags", [])
    importance = extracted.get("importance", "medium")
    
    # Build note
    note = f"""---
title: "{name}"
date: {date_str}
source: ChatGPT (alexander.o.abell@gmail.com)
domain: {domain}
importance: {importance}
tags: [{', '.join(tags + ['chatgpt-import', 'llm-conversation'])}]
created: {datetime.now().strftime('%Y-%m-%d')}
---

# {name}

> 📅 {date_str} | 🏷️ {domain} | ⭐ {importance}

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
    """Append new context to an existing people card"""
    name = person_info.get("name", "")
    context = person_info.get("context", "")
    
    if not name or not context:
        return False
    
    card_path = PEOPLE_DIR / f"{name}.md"
    if not card_path.exists():
        return False
    
    # Read existing card
    existing = card_path.read_text()
    
    # Don't add duplicate context
    if context[:50] in existing:
        return False
    
    # Append to a "ChatGPT Import Context" section
    section_header = "## ChatGPT Import Context"
    today = datetime.now().strftime("%Y-%m-%d")
    new_entry = f"- ({today}) {context}"
    
    if section_header in existing:
        # Append to existing section
        existing = existing.replace(section_header, f"{section_header}\n{new_entry}")
    else:
        # Add new section before the end
        existing += f"\n\n{section_header}\n{new_entry}\n"
    
    card_path.write_text(existing)
    return True

def append_action_items(actions, convo_name):
    """Append action items to GTD inbox"""
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
            f.write(f"- [ ] {task} — assigned to: {assigned}, source: chatgpt:{convo_name}, captured: {today}\n")
    
    return len(pending)

def main():
    log("=" * 60)
    log("ChatGPT Re-Import: Wikipedia of Alex Approach")
    log("=" * 60)
    
    # Load state
    state = load_state()
    processed_uuids = set(state["processed"])
    
    # Load conversations
    with open(EXPORT_PATH) as f:
        conversations = json.load(f)
    
    # Filter to ones with messages, skip already processed
    to_process = [c for c in conversations 
                  if len(c.get("chat_messages", [])) > 0 
                  and c["uuid"] not in processed_uuids]
    
    log(f"Total conversations: {len(conversations)}")
    log(f"With messages: {len([c for c in conversations if c.get('chat_messages')])}")
    log(f"Already processed: {len(processed_uuids)}")
    log(f"To process: {len(to_process)}")
    log("")
    
    existing_people = get_existing_people()
    log(f"Existing people cards: {len(existing_people)}")
    
    # Sort by date (oldest first)
    to_process.sort(key=lambda c: c.get("created_at", ""))
    
    notes_created = state["stats"].get("notes_created", 0)
    people_enriched = state["stats"].get("people_enriched", 0)
    action_items_total = state["stats"].get("action_items", 0)
    
    for i, convo in enumerate(to_process):
        name = convo.get("name", "Untitled") or "Untitled"
        msg_count = len(convo.get("chat_messages", []))
        log(f"[{i+1}/{len(to_process)}] {name} ({msg_count} msgs)")
        
        # Process with LLM
        extracted = process_conversation(convo, existing_people)
        if not extracted:
            log(f"  ⚠️ Extraction failed, skipping")
            state["processed"].append(convo["uuid"])
            save_state(state)
            continue
        
        importance = extracted.get("importance", "medium")
        domain = extracted.get("domain", "Other")
        log(f"  Domain: {domain} | Importance: {importance}")
        
        # Write Obsidian note
        existing_notes = list(LLM_NOTES_DIR.glob("*.md"))
        note_path = write_obsidian_note(convo, extracted, existing_notes)
        if note_path:
            notes_created += 1
            log(f"  📝 Note: {note_path.name}")
        
        # Enrich people cards
        for person in extracted.get("people_mentioned", []):
            if person.get("is_existing") and enrich_people_card(person):
                people_enriched += 1
                log(f"  👤 Enriched: {person.get('name')}")
        
        # Action items (only from high/medium importance)
        if importance in ("high", "medium"):
            n_actions = append_action_items(extracted.get("action_items", []), name)
            if n_actions:
                action_items_total += n_actions
                log(f"  ✅ {n_actions} action items")
        
        # Update state
        state["processed"].append(convo["uuid"])
        state["stats"]["conversations"] = len(state["processed"])
        state["stats"]["notes_created"] = notes_created
        state["stats"]["people_enriched"] = people_enriched
        state["stats"]["action_items"] = action_items_total
        save_state(state)
        
        # Rate limit (be gentle with API)
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
