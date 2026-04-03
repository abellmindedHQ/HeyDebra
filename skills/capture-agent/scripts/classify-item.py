#!/usr/bin/env python3
"""
Action Item Classifier v2
Context-aware classification with hash-based dedup.

Changes from v1:
- Context-aware: voice notes / meeting transcripts get STRICT filtering
- Requires concrete deliverable (noun) not just action verb for conversational sources
- Hash-based dedup via state file
- Better skip patterns for conversational speech
"""

import hashlib
import json
import os
import re
import sys
from typing import Optional, Dict, Any

# --- STATE FILE FOR DEDUP ---
DEDUP_STATE_FILE = os.path.expanduser("~/.openclaw/workspace/memory/capture-dedup-state.json")

def load_dedup_state() -> set:
    """Load existing item fingerprints."""
    try:
        with open(DEDUP_STATE_FILE, "r") as f:
            data = json.load(f)
            return set(data.get("fingerprints", []))
    except (FileNotFoundError, json.JSONDecodeError):
        return set()

def save_dedup_state(fingerprints: set):
    """Save fingerprints. Keep last 2000 to prevent unbounded growth."""
    trimmed = list(fingerprints)[-2000:]
    os.makedirs(os.path.dirname(DEDUP_STATE_FILE), exist_ok=True)
    with open(DEDUP_STATE_FILE, "w") as f:
        json.dump({"fingerprints": trimmed}, f)

def fingerprint(text: str) -> str:
    """Create a normalized fingerprint for dedup."""
    normalized = re.sub(r'\s+', ' ', text.lower().strip())
    # Remove timestamps, dates, source tags for matching
    normalized = re.sub(r'\d{4}-\d{2}-\d{2}', '', normalized)
    normalized = re.sub(r'\d{1,2}:\d{2}\s*(am|pm|et|ct|pt)?', '', normalized, flags=re.IGNORECASE)
    normalized = re.sub(r'//.*$', '', normalized)  # Remove source tags
    normalized = normalized.strip()
    return hashlib.md5(normalized.encode()).hexdigest()[:12]


# --- SOURCE CONTEXT ---
# Voice notes and meeting transcripts need STRICT filtering
CONVERSATIONAL_SOURCES = [
    r"voice-note",
    r"voice_note",
    r"recording",
    r"meeting.*recording",
    r"transcript",
    r"otter\.ai",
    r"fireflies",
]

# LLM export sources should be BLOCKED from inbox entirely
BLOCKED_SOURCES = [
    r"chatgpt",
    r"chatgpt-ornl",
    r"claude-export",
    r"gemini-export",
    r"llm-export",
]

def is_conversational_source(source: str) -> bool:
    """Check if source is a voice note / meeting transcript."""
    for pattern in CONVERSATIONAL_SOURCES:
        if re.search(pattern, source, re.IGNORECASE):
            return True
    return False

def is_blocked_source(source: str) -> bool:
    """Check if source should be completely blocked from inbox."""
    for pattern in BLOCKED_SOURCES:
        if re.search(pattern, source, re.IGNORECASE):
            return True
    return False


# --- SKIP PATTERNS (universal) ---
SKIP_PATTERNS = [
    r"^(yeah|yep|ok|okay|sure|right|no|nah|hmm|huh|wow|lol|ha|hey|hi|hello|bye|goodbye|thanks|thank you|cool|nice|great|good|awesome|perfect|sweet|dope|bet|word|facts|true|real|same|mood|vibes)\b",
    r"^(I mean|I think|I guess|I don't know|I was like|I'm not|I'm just|I'm going to be)",
    r"(I'll talk to you|I'll see you|I'll be back|I'll catch you|talk to you later|see you later|catch you later)",
    r"(I'll be honest|I'll just say|I'll tell you what|I'll put it that way|I'll say this)",
    r"(I'm all right|I'm okay|I'm good|I'm fine|that's fair|that's true|that's good)",
    r"(sorry|no worries|no problem|you're good|you're fine|my bad|all good)",
    r"(I don't think|I don't know|I'm not sure|I'm not saying)",
    r"(let me see|let me think|well|so|anyway|but|also|and then)",
    r"(have a good|happy|merry|enjoy|take care|god bless|bless you)",
    r"(you know what I mean|if that makes sense|does that make sense|right\?$)",
    r"(I hate this|I love this|this is cool|this is interesting|that's wild|that's crazy)",
    r"(I remember|I forgot|I was thinking|I was wondering)",
    r"(we don't need to|we're not going to|that's not what|this is not)",
    r"(I'll give you a hint|let me go|hang on|hold on|one sec|be right back|brb)",
    r"(it's so funny|it's like|it's just|it's not|it's the)",
    r"(blah|blah blah|yada|whatever|etc)",
]

# --- STRICT skip patterns for conversational sources ---
CONVERSATIONAL_SKIP_PATTERNS = [
    # Hedging / thinking out loud
    r"(I would|I could|I might|I may|maybe I|perhaps|possibly|potentially)",
    r"(I'm thinking|I'm wondering|I'm curious|I'm not going to lie)",
    r"(it depends|it's complicated|it's a long story|it's hard to)",
    # Storytelling / anecdotes
    r"(imagine that|let's say|for example|hypothetically|picture this)",
    r"(when I was|back when|remember when|there was this)",
    # Conversational filler
    r"(you know|like I said|as I was saying|going back to|the point is)",
    r"(the thing is|here's the thing|the other thing|another thing)",
    r"(I was going to say|what I was going to say|what I mean is)",
    # Opinions / reactions (not tasks)
    r"(I really|I honestly|I genuinely|I truly|I personally)",
    r"(that's a good|that's a great|that's a bad|that's a fair|that's interesting)",
    r"(I appreciate|I respect|I admire|I value)",
    # Generic future tense without deliverable
    r"^I'll be\b(?! sending| creating| drafting| submitting| reviewing| scheduling)",
    r"^I'll just\b",
    r"^I'll try\b",
]


# --- ACTION PATTERNS ---
ACTION_VERBS = [
    r"(?:^|\b)(schedule|create|build|send|email|call|text|pay|review|submit|complete|finish|update|fix|deploy|set up|configure|install|check|verify|prepare|prep|draft|write|book|register|sign up|apply|cancel|renew|refund|return|order|purchase|buy|hire|assign|delegate|approve|file|request|follow up|follow-up|reach out|contact|meet with|pick up|clean up|loop in)\b",
]

COMMITMENT_PATTERNS = [
    r"\bI'll (send|get|check|write|draft|put together|set up|follow up|reach out|email|call|text|share|work on|finish|complete|submit|review|schedule|create|build|look into|circle back|forward|update|handle|take care of|make sure)\b",
    r"\bI will (send|get|check|write|draft|put together|set up|follow up|reach out|email|call|text|share|work on|finish|complete|submit|review|schedule|create|build)\b",
    r"\bI need to (send|get|check|write|draft|put together|set up|follow up|reach out|email|call|text|share|work on|finish|complete|submit|review|schedule|create|build|pay|file|cancel)\b",
    r"\bwe need to (figure out|schedule|set up|create|build|fix|address|discuss|define|establish|finalize|get|hire|plan|submit|review|send)\b",
]

# --- CONCRETE DELIVERABLE PATTERNS ---
# For conversational sources, we require BOTH an action verb AND a concrete deliverable
DELIVERABLE_NOUNS = [
    r"\b(report|email|document|file|spreadsheet|deck|presentation|proposal|brief|memo|agenda|list|plan|budget|invoice|form|application|request|ticket|PR|pull request|branch|commit|patch|fix|link|URL|screenshot|draft|summary|analysis|quote|estimate|contract|NDA|agreement|survey|feedback|data|export|import|script|template|design|mockup|wireframe|prototype|spec|requirements|test|review|audit|assessment|checklist|timeline|roadmap|schedule|calendar invite|meeting invite)\b",
    r"\b(prescription|appointment|reservation|booking|registration|enrollment|payment|refund|receipt|bill|statement|certificate|license|permit|visa|passport|insurance|claim|coverage)\b",
]

# --- AREA MAPPING ---
AREA_MAP = {
    "🏢 ORNL": [
        r"\b(ORNL|ornl|lab|ServiceNow|SharePoint|Drupal|SEEK|AppDev|directorate|ITSD|CMS|BRM|UX|demand|budget|FY\d{2}|charge code|Power Apps|Power Platform|Coefficient|Elastic|Swish|Lone Rock|David Bond|Jay|Brooks|Brad Greenfield|Angie|Anthony|Jason Shoemaker|Brandon Brown|Mike Shell|SQA|CSDM|PIT|Transformation Group)\b",
    ],
    "💊 Health & Money": [
        r"\b(pay|bill|payment|invoice|subscription|insurance|medical|doctor|appointment|pharmacy|Walgreens|prescription|Rx|Costco|Citi|YNAB|Monarch|bank|credit card|dental|lipoma|psychiatry|therapy|therapist|health|OBGYN|surgery|consult)\b",
    ],
    "🚀 Build": [
        r"\b(build|code|deploy|app|website|repo|git|GitHub|Linear|API|SDK|v0|Vercel|OpenClaw|SecondBrain|Mirror|Pools|Pooli|HoldPlease|VisionClaw|script|pipeline|cron|Neo4j|Obsidian|Twilio|Supabase|Replit)\b",
    ],
    "👨👧 People": [
        r"\b(Hannah|Annika|Avie|Sallijo|Roxanne|Chelsea|Marshall|Everett|Merle|Brandon Bruce|Jim Biggs|Pooja|Lee Baird|Marco|Nick|Teresa|Allison)\b",
    ],
}

DEFAULT_AREA = "🏠 Life Ops"


def has_action_pattern(text: str) -> bool:
    """Check if text has action verbs or commitment patterns."""
    for pattern in ACTION_VERBS:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    for pattern in COMMITMENT_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False

def has_deliverable(text: str) -> bool:
    """Check if text mentions a concrete deliverable noun."""
    for pattern in DELIVERABLE_NOUNS:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False

def has_named_person(text: str) -> bool:
    """Check if text mentions a specific named person."""
    # Check area map people
    for pattern in AREA_MAP.get("👨👧 People", []):
        if re.search(pattern, text, re.IGNORECASE):
            return True
    for pattern in AREA_MAP.get("🏢 ORNL", []):
        if re.search(pattern, text, re.IGNORECASE):
            return True
    # Generic proper noun detection (capitalized words that aren't sentence starts)
    words = text.split()
    for i, word in enumerate(words):
        if i > 0 and word[0].isupper() and len(word) > 2 and not word.isupper():
            return True
    return False

def has_deadline(text: str) -> bool:
    """Check if text mentions a deadline or timeframe."""
    deadline_patterns = [
        r"\bby (Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\b",
        r"\bby (tomorrow|end of day|EOD|end of week|EOW|next week|tonight|morning)\b",
        r"\bby (\d{1,2}/\d{1,2})\b",
        r"\b(ASAP|urgent|immediately|right away|today|tonight)\b",
        r"\bby (January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}\b",
        r"\b(before|prior to|no later than|deadline)\b",
        r"\b(this week|next week|this month|next month)\b",
    ]
    for pattern in deadline_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False


def should_skip(text: str, source: str = "") -> bool:
    """Check if text should be skipped."""
    text = text.strip()
    
    # Too short
    if len(text) < 25:
        return True
    
    # Pure questions without action verbs
    if text.endswith("?") and not has_action_pattern(text):
        return True
    
    # Universal skip patterns
    for pattern in SKIP_PATTERNS:
        if re.search(pattern, text.strip(), re.IGNORECASE):
            # But don't skip if it ALSO has strong action signals
            if has_action_pattern(text) and (has_deliverable(text) or has_deadline(text)):
                return False
            return True
    
    # Extra strict filtering for conversational sources
    if is_conversational_source(source):
        for pattern in CONVERSATIONAL_SKIP_PATTERNS:
            if re.search(pattern, text.strip(), re.IGNORECASE):
                return True
    
    return False


def classify(text: str, source: str = "") -> Dict[str, Any]:
    """Classify a single candidate action item with context awareness."""
    text = text.strip()

    # Block LLM export sources entirely
    if is_blocked_source(source):
        return {
            "action": text,
            "is_actionable": False,
            "reason": "blocked source (LLM export — archive only, no inbox routing)"
        }

    # Skip check
    if should_skip(text, source):
        return {
            "action": text,
            "is_actionable": False,
            "reason": "skipped by pre-filter"
        }

    has_action = has_action_pattern(text)
    
    if not has_action:
        return {
            "action": text,
            "is_actionable": False,
            "reason": "no action pattern detected"
        }

    # STRICT MODE for conversational sources:
    # Require action verb + (deliverable OR deadline OR named person)
    if is_conversational_source(source):
        has_noun = has_deliverable(text)
        has_person = has_named_person(text)
        has_due = has_deadline(text)
        
        if not (has_noun or has_due or has_person):
            return {
                "action": text,
                "is_actionable": False,
                "reason": "conversational source: action verb found but no concrete deliverable, deadline, or named person"
            }
        
        # Extra length check for conversational — very short items from transcripts are usually noise
        if len(text) < 60 and not has_due:
            return {
                "action": text,
                "is_actionable": False,
                "reason": "conversational source: too short without deadline"
            }

    # Extract metadata
    due = extract_due(text)
    priority = detect_priority(text, due)
    area = detect_area(text)

    return {
        "action": text,
        "is_actionable": True,
        "assignee": "Alex",
        "due": due,
        "priority": priority,
        "area": area
    }


def extract_due(text: str) -> Optional[str]:
    """Extract due date from text."""
    patterns = [
        (r"\bby (Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\b", None),
        (r"\bby (tomorrow|end of day|EOD|end of week|EOW|next week)\b", None),
        (r"\bby (\d{1,2}/\d{1,2})\b", None),
        (r"\b(ASAP|urgent|immediately)\b", "ASAP"),
        (r"\bby (January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}\b", None),
    ]
    for pattern, override in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return override if override else match.group(0)
    return None


def detect_priority(text: str, due: Optional[str] = None) -> str:
    """Detect priority level."""
    if due == "ASAP" or re.search(r"\b(urgent|ASAP|critical|immediately|right now)\b", text, re.IGNORECASE):
        return "urgent"
    if re.search(r"\b(when you get a chance|whenever|no rush|someday|eventually)\b", text, re.IGNORECASE):
        return "low"
    return "normal"


def detect_area(text: str) -> str:
    """Map text to a Things 3 area."""
    for area, patterns in AREA_MAP.items():
        for pattern in patterns:
            if re.search(pattern, text):
                return area
    return DEFAULT_AREA


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Classify candidate action items (v2)")
    parser.add_argument("--file", help="Read from file instead of stdin")
    parser.add_argument("--json-input", action="store_true", help="Input is JSON array")
    parser.add_argument("--source", default="", help="Source context (e.g., 'voice-note:meeting.m4a', 'email:subject:sender')")
    parser.add_argument("--no-dedup", action="store_true", help="Skip dedup check")
    args = parser.parse_args()

    if args.file:
        with open(args.file, "r") as f:
            lines = f.readlines()
    else:
        lines = sys.stdin.readlines()

    if args.json_input:
        try:
            items = json.loads("".join(lines))
            if isinstance(items, list):
                lines = [json.dumps(i) if isinstance(i, dict) else str(i) for i in items]
        except json.JSONDecodeError:
            pass

    # Load dedup state
    existing_fps = load_dedup_state() if not args.no_dedup else set()
    new_fps = set()

    results = []
    deduped = 0
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Check source from JSON if present
        source = args.source
        try:
            item = json.loads(line)
            if isinstance(item, dict):
                line = item.get("text", item.get("action", str(item)))
                source = item.get("source", source)
        except (json.JSONDecodeError, TypeError):
            pass
        
        # Dedup check
        fp = fingerprint(line)
        if fp in existing_fps or fp in new_fps:
            deduped += 1
            continue
        
        result = classify(line, source)
        results.append(result)
        
        if result.get("is_actionable"):
            new_fps.add(fp)

    # Save updated dedup state
    if not args.no_dedup and new_fps:
        save_dedup_state(existing_fps | new_fps)

    actionable = [r for r in results if r.get("is_actionable")]
    skipped = [r for r in results if not r.get("is_actionable")]

    output = {
        "total": len(results) + deduped,
        "actionable": len(actionable),
        "skipped": len(skipped),
        "deduped": deduped,
        "items": results
    }

    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
