#!/usr/bin/env python3
"""
generate_queue.py — Parse LinkedIn Message Analysis report and generate cleanup queue.

Usage:
    python3 generate_queue.py --input <path_to_analysis.md> --output <state_file.json>
    python3 generate_queue.py --preview   # show summary without writing

Parses conversations classified as:
  ⚪ spam      → archived first (highest priority)
  🟢 one-touch → archived second (oldest first)
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

STATE_FILE_DEFAULT = "/Users/debra/.openclaw/workspace/memory/linkedin-cleanup-state.json"
ANALYSIS_FILE_DEFAULT = "/Users/debra/SecondBrain/Documents/LinkedIn Message Analysis.md"


def parse_analysis_report(filepath: str) -> tuple[list[dict], list[dict]]:
    """
    Parse the LinkedIn Message Analysis markdown file.
    Returns (spam_convos, one_touch_convos) as lists of dicts.
    
    Expected format: lines containing ⚪ or 🟢 with conversation name and date info.
    Tries multiple common markdown table/list formats.
    """
    path = Path(filepath)
    if not path.exists():
        print(f"❌ Analysis file not found: {filepath}")
        sys.exit(1)

    content = path.read_text(encoding="utf-8")
    
    spam = []
    one_touch = []

    # Pattern 1: Markdown table rows like | ⚪ | Name | Date | ...
    # Pattern 2: List items like - ⚪ **Name** (date)
    # Pattern 3: Lines containing emoji + name
    
    # Try to find table rows first
    table_row_pattern = re.compile(
        r'\|([^|]*(?:⚪|🟢)[^|]*)\|([^|]+)\|([^|]*)\|',
        re.UNICODE
    )
    
    # Generic line pattern: emoji followed by name
    line_pattern = re.compile(
        r'(⚪|🟢)\s+\**([^\*\n|]+?)\**\s*(?:\(([^)]+)\))?',
        re.UNICODE
    )

    lines = content.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Detect emoji category
        category = None
        if '⚪' in line:
            category = 'spam'
        elif '🟢' in line:
            category = 'one-touch'
        else:
            continue

        # Try to extract name from table row or list
        name = None
        date_str = None
        
        # Try table row format: | emoji | name | date |
        table_match = re.search(r'\|\s*([^\|]+?)\s*\|\s*([^\|]*?)\s*\|', line)
        if table_match:
            col1 = table_match.group(1).strip()
            col2 = table_match.group(2).strip()
            # Name is whichever column doesn't just have the emoji
            for col in [col1, col2]:
                cleaned = re.sub(r'[⚪🟢]', '', col).strip()
                cleaned = re.sub(r'\*+', '', cleaned).strip()
                if cleaned and len(cleaned) > 1:
                    name = cleaned
                    break
        
        # Try inline pattern
        if not name:
            match = line_pattern.search(line)
            if match:
                name = match.group(2).strip()
                date_str = match.group(3)
        
        # Last resort: grab text after the emoji
        if not name:
            cleaned = re.sub(r'[⚪🟢\|\-\*#]', '', line).strip()
            cleaned = re.sub(r'\s+', ' ', cleaned).strip()
            if cleaned and len(cleaned) > 2:
                name = cleaned[:80]  # cap length
        
        if not name:
            continue
        
        # Clean up the name
        name = re.sub(r'\s+', ' ', name).strip()
        name = name[:100]  # max 100 chars
        
        entry = {
            "name": name,
            "category": category,
            "dateDetected": date_str or "",
            "addedAt": datetime.now().isoformat(),
        }
        
        if category == 'spam':
            spam.append(entry)
        else:
            one_touch.append(entry)

    return spam, one_touch


def load_existing_state(state_path: str) -> dict:
    """Load existing state file or return empty state."""
    path = Path(state_path)
    if path.exists():
        try:
            return json.loads(path.read_text())
        except json.JSONDecodeError:
            print("⚠️  Existing state file is invalid JSON. Will create fresh.")
    return {}


def build_state(spam: list[dict], one_touch: list[dict], existing: dict) -> dict:
    """Build the full state file, preserving any existing progress."""
    # Spam first, then one-touch (one-touch by addedAt = oldest first)
    # one_touch is already in file order; sort by dateDetected if available
    one_touch_sorted = sorted(
        one_touch,
        key=lambda x: x.get("dateDetected", "") or ""
    )
    
    queue = spam + one_touch_sorted
    
    # If there's an existing state with progress, preserve completed list
    completed = existing.get("completed", [])
    completed_names = {c["name"] for c in completed}
    
    # Remove already-completed items from new queue
    queue = [item for item in queue if item["name"] not in completed_names]
    
    today = datetime.now().strftime("%Y-%m-%d")
    today_archived = existing.get("todayArchived", 0) if existing.get("todayDate") == today else 0
    
    return {
        "totalQueued": len(queue) + len(completed),
        "totalArchived": len(completed),
        "todayArchived": today_archived,
        "todayDate": today,
        "lastRunAt": existing.get("lastRunAt"),
        "lastError": existing.get("lastError"),
        "queue": queue,
        "completed": completed,
        "paused": existing.get("paused", False),
        "generatedAt": datetime.now().isoformat(),
        "breakdown": {
            "spam": len(spam),
            "oneTouch": len(one_touch),
            "alreadyCompleted": len(completed),
            "remainingInQueue": len(queue),
        }
    }


def print_summary(state: dict, spam_count: int, one_touch_count: int):
    """Print a human-readable summary of what will be queued."""
    b = state["breakdown"]
    queue_size = len(state["queue"])
    
    print("\n" + "="*55)
    print("📋 LinkedIn Cleanup Queue Summary")
    print("="*55)
    print(f"  ⚪ Spam conversations:      {spam_count:>6,}")
    print(f"  🟢 One-touch conversations: {one_touch_count:>6,}")
    print(f"  ✅ Already completed:        {b['alreadyCompleted']:>6,}")
    print(f"  📦 Remaining in queue:       {queue_size:>6,}")
    print(f"  📊 Total to process:         {state['totalQueued']:>6,}")
    print()
    
    if queue_size > 0:
        # Estimate completion
        per_day = 150  # max daily
        active_days_per_week = 10/3  # skip every 3rd day = ~3.3 days/week
        weeks = (queue_size / per_day) / active_days_per_week
        print(f"  ⏱️  Est. completion: ~{weeks:.1f} weeks at 150/day")
    
    print()
    if state["queue"]:
        print("  First 5 in queue:")
        for i, item in enumerate(state["queue"][:5]):
            cat_icon = "⚪" if item["category"] == "spam" else "🟢"
            print(f"    {i+1}. {cat_icon} {item['name']}")
        if queue_size > 5:
            print(f"    ... and {queue_size - 5:,} more")
    print("="*55)


def main():
    parser = argparse.ArgumentParser(description="Generate LinkedIn cleanup queue from analysis report")
    parser.add_argument("--input", default=ANALYSIS_FILE_DEFAULT,
                        help="Path to LinkedIn Message Analysis.md")
    parser.add_argument("--output", default=STATE_FILE_DEFAULT,
                        help="Path to state JSON file")
    parser.add_argument("--preview", action="store_true",
                        help="Show summary without writing to disk")
    parser.add_argument("--force", action="store_true",
                        help="Skip confirmation prompt")
    args = parser.parse_args()

    print(f"\n🔍 Reading analysis from:\n   {args.input}")
    spam, one_touch = parse_analysis_report(args.input)
    
    print(f"\n✅ Parsed: {len(spam):,} spam + {len(one_touch):,} one-touch = {len(spam)+len(one_touch):,} total")
    
    if not spam and not one_touch:
        print("\n⚠️  No conversations found! Check that the analysis file has ⚪ or 🟢 emoji markers.")
        print("    File path:", args.input)
        sys.exit(1)
    
    # Load any existing progress
    existing = load_existing_state(args.output) if not args.preview else {}
    state = build_state(spam, one_touch, existing)
    print_summary(state, len(spam), len(one_touch))

    if args.preview:
        print("👀 Preview mode — nothing written to disk.\n")
        return

    # Confirmation prompt
    if not args.force:
        print(f"\n📁 Will write state to:\n   {args.output}\n")
        confirm = input("Type 'yes' to generate the queue and write the state file: ").strip().lower()
        if confirm != "yes":
            print("\n❌ Aborted. Nothing written.\n")
            sys.exit(0)

    # Ensure output directory exists
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    output_path.write_text(json.dumps(state, indent=2, ensure_ascii=False))
    print(f"\n✅ State file written to:\n   {args.output}")
    print(f"   Queue size: {len(state['queue']):,} conversations ready to archive\n")


if __name__ == "__main__":
    main()
