#!/usr/bin/env python3
"""
Action Item Classifier
Reads candidate items from stdin (one per line) and classifies them
as actionable or not, with area mapping for Things 3 routing.
"""

import json
import re
import sys
from typing import Optional, List, Dict, Any

# Patterns that indicate NOT an action item
SKIP_PATTERNS = [
    r"^(yeah|yep|ok|okay|sure|right|no|nah|hmm|huh|wow|lol|ha|hey|hi|hello|bye|goodbye|thanks|thank you)",
    r"^(I mean|I think|I guess|I don't know|I was like|I'm not|I'm just|I'm going to be)",
    r"(I'll talk to you|I'll see you|I'll be back|I'll catch you|talk to you later|see you later)",
    r"(I'll be honest|I'll just say|I'll tell you what|I'll put it that way)",
    r"(I'm all right|I'm okay|I'm good|I'm fine|that's fair|that's true|that's good)",
    r"(sorry|no worries|no problem|you're good|you're fine)",
    r"(I don't think|I don't know|I'm not sure|I'm not saying)",
    r"(let me see|let me think|well|so|anyway|but)",
    r"(have a good|happy|merry|enjoy|take care)",
    r"(I'll be in intensive therapy|I need to pee|I was hot|that's a joke)",
    r"(you know what I mean|if that makes sense|does that make sense)",
    r"(I hate this|I love this|this is cool|this is interesting)",
    r"(I remember|I forgot|I was thinking|I was wondering)",
    r"(we don't need to|we're not going to|that's not what|this is not)",
]

# Patterns that indicate IS an action item
ACTION_VERBS = [
    r"(?:^|\b)(schedule|create|build|send|email|call|text|pay|review|submit|complete|finish|update|fix|deploy|set up|configure|install|check|verify|prepare|prep|draft|write|book|register|sign up|apply|cancel|renew|refund|return|order|purchase|buy|hire|assign|delegate|approve|file|request|follow up|follow-up|reach out|contact|meet with|set a meeting|put together|get back to|circle back|look into|pick up|top up|clean up|set up|sign up|loop in)\b",
]

# Commitment patterns (first person future)
COMMITMENT_PATTERNS = [
    r"\bI'll (send|get|check|write|draft|put|set|follow|reach|email|call|text|share|work on|finish|complete|submit|review|schedule|create|build|look into|circle back|forward|update)\b",
    r"\bI will (send|get|check|write|draft|put|set|follow|reach|email|call|text|share|work on|finish|complete|submit|review|schedule|create|build)\b",
    r"\bI'm going to (send|get|check|write|draft|put|set|follow|reach|email|call|text|share|work on|finish|complete|submit|review|schedule|create|build|start)\b",
    r"\bI need to (send|get|check|write|draft|put|set|follow|reach|email|call|text|share|work on|finish|complete|submit|review|schedule|create|build|talk to|make)\b",
    r"\bwe need to (figure out|schedule|set up|create|build|fix|address|discuss|define|establish|finalize|get|hire|plan)\b",
]

# Area mapping keywords
AREA_MAP = {
    "🏢 ORNL": [
        r"\b(ORNL|ornl|lab|ServiceNow|SharePoint|Drupal|SEEK|AppDev|directorate|ITSD|CMS|BRM|UX|demand|budget|FY\d{2}|charge code|Power Apps|Power Platform|Coefficient|Elastic|Swish|Lone Rock|David Bond|Jay|Brooks|Brad|Angie|Herb|Anthony|Jason Shoemaker|Brandon Brown|Mike Shell)\b",
    ],
    "💊 Health & Money": [
        r"\b(pay|bill|payment|invoice|subscription|insurance|medical|doctor|appointment|pharmacy|Walgreens|prescription|Rx|Costco|Citi|Netflix|VirtualDJ|Recraft|YNAB|Monarch|bank|credit card|dental|lipoma|psychiatry|therapy|therapist|health)\b",
    ],
    "🚀 Build": [
        r"\b(build|code|deploy|app|website|repo|git|GitHub|Linear|API|SDK|v0|Vercel|OpenClaw|SecondBrain|Mirror|Pools|Pooli|BOBoBS|Batman|HoldPlease|VisionClaw|script|pipeline|cron|Neo4j|Obsidian)\b",
    ],
    "👨👧 People": [
        r"\b(Hannah|Annika|Avie|Sallijo|Roxanne|Chelsea|Marshall|Everett|Merle|Brandon Bruce|Jim Biggs|Pooja|Lee Baird|Marco|Nick|Alex Brodsky)\b",
    ],
}

DEFAULT_AREA = "🏠 Life Ops"


def should_skip(text: str) -> bool:
    """Check if text matches skip patterns, but NOT if it also has action verbs."""
    if len(text.strip()) < 20:
        return True
    if text.strip().endswith("?") and not any(re.search(p, text, re.IGNORECASE) for p in ACTION_VERBS):
        return True
    # Check if text has action verbs or commitment patterns FIRST
    # If it does, don't skip even if it matches a skip pattern
    if is_actionable(text):
        return False
    for pattern in SKIP_PATTERNS:
        if re.search(pattern, text.strip(), re.IGNORECASE):
            return True
    return False


def is_actionable(text: str) -> bool:
    """Check if text contains actionable patterns."""
    for pattern in ACTION_VERBS:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    for pattern in COMMITMENT_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False


def detect_area(text: str) -> str:
    """Map text to a Things 3 area."""
    for area, patterns in AREA_MAP.items():
        for pattern in patterns:
            if re.search(pattern, text):
                return area
    return DEFAULT_AREA


def extract_due(text: str) -> Optional[str]:
    """Try to extract a due date from text."""
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


def classify(text: str) -> Dict[str, Any]:
    """Classify a single candidate action item."""
    text = text.strip()

    if should_skip(text):
        return {
            "action": text,
            "is_actionable": False,
            "reason": "skipped by pre-filter"
        }

    actionable = is_actionable(text)
    if not actionable:
        return {
            "action": text,
            "is_actionable": False,
            "reason": "no action pattern detected"
        }

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


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Classify candidate action items")
    parser.add_argument("--file", help="Read from file instead of stdin")
    parser.add_argument("--json-input", action="store_true", help="Input is JSON array")
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

    results = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        result = classify(line)
        results.append(result)

    actionable = [r for r in results if r.get("is_actionable")]
    skipped = [r for r in results if not r.get("is_actionable")]

    output = {
        "total": len(results),
        "actionable": len(actionable),
        "skipped": len(skipped),
        "items": results
    }

    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
