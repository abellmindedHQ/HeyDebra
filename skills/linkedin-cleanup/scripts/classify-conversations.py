#!/usr/bin/env python3
"""
LinkedIn Conversation Classifier
=================================
Scrolls through LinkedIn messaging inbox via browser automation,
classifies each conversation as ARCHIVE or KEEP, and writes a state file.

Usage:
    python3 scripts/classify-conversations.py [--limit N] [--resume] [--dry-run]

Options:
    --limit N       Stop after scanning N conversations (default: unlimited)
    --resume        Resume from last saved intermediate state
    --dry-run       Classify but don't write state file
    --batch-size N  Conversations per batch before scrolling (default: 20)
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

# ── Paths ────────────────────────────────────────────────────────────────────
WORKSPACE = Path("/Users/debra/.openclaw/workspace")
STATE_FILE = WORKSPACE / "memory" / "linkedin-cleanup-state.json"
INTERMEDIATE_FILE = WORKSPACE / "memory" / "linkedin-classify-intermediate.json"

# ── Known people (always KEEP) ────────────────────────────────────────────────
KNOWN_PEOPLE_SUBSTRINGS = [
    "jay", "hannah", "annika", "brodsky", "brandon bruce", "brandon brown",
    "mike shell", "merle", "chelsea", "pooja", "marshall", "everett",
    "angelo", "sallijo", "jim biggs", "anthony caccese", "brooks herring",
    "herb himes", "nick hollensbe", "jason patrick", "jason shoemaker",
    "tom harper", "milan jain", "roger cass", "david hobbs",
    "jame houghton", "joshua wilson",
]

# ── Recruiter/spam keywords ───────────────────────────────────────────────────
ARCHIVE_KEYWORDS = [
    "i came across your profile",
    "i'd love to connect",
    "i would love to connect",
    "opportunity",
    "role",
    "position",
    "platform",
    "demo",
    "schedule a call",
    "let me know if you're interested",
    "open to exploring",
    "open to new opportunities",
    "exciting opportunity",
    "perfect fit",
    "reach out",
    "recruiting",
    "recruiter",
    "talent acquisition",
    "hiring manager",
    "job opening",
    "we're hiring",
    "congratulations on your",
    "happy work anniversary",
    "work anniversary",
    "happy birthday",
    "congratulations on",
    "new role",
    "new position",
    "hope you're doing well",
    "quick question",
    "i noticed your profile",
    "your background caught",
    "your experience caught",
    "i think you'd be a great",
    "would you be open",
    "are you open to",
]

# ── Location/org keywords (KEEP) ─────────────────────────────────────────────
KEEP_KEYWORDS = [
    "ornl", "kec", "techstars", "ut knoxville", "knoxville",
    "oak ridge", "haslam", "utk", " ut ", "lunchpool",
]


# ── Classification logic ──────────────────────────────────────────────────────

def classify_conversation(conv: dict, in_contacts: bool) -> tuple[str, list[str]]:
    """
    Returns ('KEEP' | 'ARCHIVE', [reason, ...])
    KEEP reasons always override ARCHIVE reasons.
    """
    name = (conv.get("name") or "").strip()
    preview = (conv.get("preview") or "").strip()
    date_str = (conv.get("date") or "").strip()
    msg_count = conv.get("msg_count")  # int or None
    is_inmail = conv.get("is_inmail", False)

    preview_lower = preview.lower()
    name_lower = name.lower()

    keep_reasons = []
    archive_reasons = []

    # ── KEEP checks ──────────────────────────────────────────────────────────
    if in_contacts:
        keep_reasons.append("in_google_contacts")

    if preview_lower.startswith("you:"):
        keep_reasons.append("alex_responded")

    if msg_count is not None and msg_count > 2:
        keep_reasons.append(f"multiple_messages({msg_count})")

    for person in KNOWN_PEOPLE_SUBSTRINGS:
        if person in name_lower:
            keep_reasons.append(f"known_person({person})")
            break

    # Last message within 6 months
    last_msg_date = parse_date(date_str)
    if last_msg_date:
        six_months_ago = datetime.now() - timedelta(days=183)
        if last_msg_date > six_months_ago:
            keep_reasons.append("recent_message(<6mo)")

    for kw in KEEP_KEYWORDS:
        if kw in preview_lower or kw in name_lower:
            keep_reasons.append(f"org_keyword({kw.strip()})")
            break

    # ── ARCHIVE checks ────────────────────────────────────────────────────────
    if is_inmail:
        archive_reasons.append("inmail")

    if name_lower == "linkedin member":
        archive_reasons.append("deactivated_account")

    if msg_count == 1:
        archive_reasons.append("single_message")

    # No response from Alex (preview doesn't start with "You:")
    if preview and not preview_lower.startswith("you:"):
        archive_reasons.append("no_alex_response")

    # Old AND sparse
    if last_msg_date:
        twelve_months_ago = datetime.now() - timedelta(days=365)
        if last_msg_date < twelve_months_ago and (msg_count is None or msg_count <= 2):
            archive_reasons.append("old_sparse(>12mo,<=2msgs)")

    for kw in ARCHIVE_KEYWORDS:
        if kw in preview_lower:
            archive_reasons.append(f"spam_keyword({kw[:30]})")
            break  # one reason is enough

    # ── Decision ──────────────────────────────────────────────────────────────
    if keep_reasons:
        return "KEEP", keep_reasons
    if archive_reasons:
        return "ARCHIVE", archive_reasons

    # Default: no signal → KEEP (conservative)
    return "KEEP", ["no_archive_signal"]


def parse_date(date_str: str) -> datetime | None:
    """Parse LinkedIn's relative/absolute date strings into a datetime."""
    if not date_str:
        return None
    now = datetime.now()
    s = date_str.strip().lower()

    # "just now", "moments ago"
    if "just now" in s or "moment" in s:
        return now

    # "X minutes ago"
    m = re.match(r"(\d+)\s*min", s)
    if m:
        return now - timedelta(minutes=int(m.group(1)))

    # "X hours ago"
    m = re.match(r"(\d+)\s*h", s)
    if m:
        return now - timedelta(hours=int(m.group(1)))

    # "X days ago"
    m = re.match(r"(\d+)\s*d", s)
    if m:
        return now - timedelta(days=int(m.group(1)))

    # "X weeks ago"
    m = re.match(r"(\d+)\s*w", s)
    if m:
        return now - timedelta(weeks=int(m.group(1)))

    # "X months ago"
    m = re.match(r"(\d+)\s*mo", s)
    if m:
        return now - timedelta(days=30 * int(m.group(1)))

    # "X years ago" or just "Xyr"
    m = re.match(r"(\d+)\s*y", s)
    if m:
        return now - timedelta(days=365 * int(m.group(1)))

    # Try absolute: "Mar 15", "Mar 2024", "2024-03-15"
    for fmt in ("%b %d", "%b %Y", "%Y-%m-%d", "%m/%d/%Y", "%b %d, %Y"):
        try:
            dt = datetime.strptime(date_str.strip(), fmt)
            # If no year in format, assume current year (or last year if in future)
            if dt.year == 1900:
                dt = dt.replace(year=now.year)
                if dt > now:
                    dt = dt.replace(year=now.year - 1)
            return dt
        except ValueError:
            continue
    return None


# ── Google Contacts lookup ────────────────────────────────────────────────────

_contacts_cache: dict[str, bool] = {}
_last_contacts_call = 0.0


def is_in_google_contacts(name: str) -> bool:
    """Check if a name exists in Google Contacts. Rate-limited to 1/sec."""
    global _last_contacts_call

    if not name or name.lower() == "linkedin member":
        return False

    # Cache check
    if name in _contacts_cache:
        return _contacts_cache[name]

    # Rate limit: 1 req/sec
    elapsed = time.time() - _last_contacts_call
    if elapsed < 1.0:
        time.sleep(1.0 - elapsed)

    try:
        result = subprocess.run(
            ["gog", "contacts", "search", name,
             "--account", "alexander.o.abell@gmail.com", "--json"],
            capture_output=True, text=True, timeout=15
        )
        _last_contacts_call = time.time()

        if result.returncode == 0 and result.stdout.strip():
            data = json.loads(result.stdout)
            found = bool(data) and (
                isinstance(data, list) and len(data) > 0 or
                isinstance(data, dict) and data.get("contacts")
            )
        else:
            found = False
    except (subprocess.TimeoutExpired, json.JSONDecodeError, Exception):
        found = False
        _last_contacts_call = time.time()

    _contacts_cache[name] = found
    return found


# ── Browser / snapshot parsing ────────────────────────────────────────────────

def parse_conversations_from_snapshot(snapshot_text: str) -> list[dict]:
    """
    Parse conversation entries from a browser snapshot (aria/role tree text).
    LinkedIn's messaging sidebar renders conversations as list items with:
      - Contact name
      - Message preview
      - Timestamp
      - Possibly "InMail" label

    Returns list of dicts: {name, preview, date, msg_count, is_inmail}
    """
    conversations = []

    # Split snapshot into lines for pattern matching
    lines = snapshot_text.split("\n")

    # Strategy: look for conversation rows. LinkedIn renders each as a
    # listitem or link with the contact name followed by preview text.
    # We'll use a sliding-window heuristic.

    # Pattern: look for lines that look like a name (short, Title Case or ALL CAPS)
    # followed by a date-like token and a preview snippet.

    # More robust: find all <article> or <li> blocks with class patterns.
    # Since we get aria/role text, we look for structured patterns.

    # LinkedIn messaging snapshot typically has entries like:
    #   "link [name] [date]\n  [preview text]"
    # or role=listitem blocks

    # Regex for a conversation entry block
    # We'll scan for date patterns to anchor entries
    date_pattern = re.compile(
        r"\b(\d+\s*(?:min|h|d|w|mo|yr|year|week|day|hour|month)s?\s*(?:ago)?"
        r"|just now|today|yesterday|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec"
        r"|\d{1,2}/\d{1,2}(?:/\d{2,4})?)\b",
        re.IGNORECASE
    )

    # Try to find listitem blocks in the snapshot
    # LinkedIn's aria tree typically shows:
    #   listitem:
    #     link "Name · Date"
    #       "Preview text..."
    #     OR
    #     "Name"
    #     "Date"
    #     "Preview"

    # We'll use a more flexible approach: find all "link" lines that contain
    # a bullet (·) which LinkedIn uses to separate name from date
    link_pattern = re.compile(
        r'(?:link|button)\s+"([^"]+?\s*[·•]\s*[^"]+)"',
        re.IGNORECASE
    )

    for match in link_pattern.finditer(snapshot_text):
        full_text = match.group(1)
        # Split on · or •
        parts = re.split(r'\s*[·•]\s*', full_text, maxsplit=1)
        if len(parts) < 2:
            continue
        name = parts[0].strip()
        remainder = parts[1].strip()

        # remainder might be "Date preview" or just "Date"
        # Try to split date from preview
        date_match = date_pattern.search(remainder)
        date_str = date_match.group(0) if date_match else ""
        preview = remainder[date_match.end():].strip() if date_match else remainder

        if len(name) < 2 or len(name) > 80:
            continue

        # Detect InMail
        is_inmail = "inmail" in full_text.lower() or "inmail" in name.lower()

        conversations.append({
            "name": name,
            "preview": preview,
            "date": date_str,
            "msg_count": None,  # not reliably visible in list view
            "is_inmail": is_inmail,
        })

    # Fallback: look for standalone name + date + preview patterns in listitem blocks
    if len(conversations) < 3:
        conversations = _parse_fallback(snapshot_text)

    return conversations


def _parse_fallback(snapshot_text: str) -> list[dict]:
    """
    Fallback parser: look for patterns in the raw snapshot text.
    Handles cases where LinkedIn renders differently.
    """
    conversations = []
    lines = [l.strip() for l in snapshot_text.split("\n") if l.strip()]

    i = 0
    while i < len(lines):
        line = lines[i]

        # Skip UI chrome lines
        if any(skip in line.lower() for skip in [
            "compose", "search messages", "messaging", "filter",
            "focused inbox", "other", "archived", "spam",
            "settings", "close", "back", "send a message"
        ]):
            i += 1
            continue

        # A name line: 2-60 chars, not starting with common UI words
        # and the NEXT line has a date-like pattern
        if (2 <= len(line) <= 60 and
                not line.startswith(("http", "/", "[", "<", "•", "·")) and
                i + 1 < len(lines)):

            next_line = lines[i + 1]
            date_match = re.search(
                r'\b(\d+\s*(?:min|h|d|w|mo|yr)s?\s*(?:ago)?|just now|today|yesterday'
                r'|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)',
                next_line, re.IGNORECASE
            )
            if date_match:
                name = line
                date_str = date_match.group(0)
                # Preview might be on the same line after date, or next line
                rest = next_line[date_match.end():].strip()
                preview = rest if rest else (lines[i + 2] if i + 2 < len(lines) else "")
                is_inmail = "inmail" in name.lower() or "inmail" in preview.lower()

                conversations.append({
                    "name": name,
                    "preview": preview,
                    "date": date_str,
                    "msg_count": None,
                    "is_inmail": is_inmail,
                })
                i += 2
                continue
        i += 1

    return conversations


# ── State helpers ─────────────────────────────────────────────────────────────

def load_intermediate() -> dict:
    if INTERMEDIATE_FILE.exists():
        with open(INTERMEDIATE_FILE) as f:
            return json.load(f)
    return {
        "scanned": [],
        "seen_names": [],
        "stats": {
            "total_scanned": 0,
            "archived": 0,
            "kept": 0,
            "reasons": {}
        }
    }


def save_intermediate(state: dict):
    INTERMEDIATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(INTERMEDIATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def save_final_state(state: dict):
    """Write the final linkedin-cleanup-state.json."""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)

    # Load existing state to preserve cleanup progress fields
    existing = {}
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            existing = json.load(f)

    archive_items = [c for c in state["scanned"] if c["decision"] == "ARCHIVE"]
    keep_items = [c for c in state["scanned"] if c["decision"] == "KEEP"]

    # Build queue: just names (for compatibility with cleanup_state.py)
    queue_names = [c["name"] for c in archive_items]

    # Merge: prepend new archive names, preserving any existing queue entries
    existing_queue = existing.get("queue", [])
    existing_set = set(existing_queue)
    new_names = [n for n in queue_names if n not in existing_set]
    merged_queue = new_names + existing_queue

    output = {
        **existing,
        "queue": merged_queue,
        "kept": [{"name": c["name"], "reasons": c["keep_reasons"]} for c in keep_items],
        "totalQueued": len(merged_queue),
        "classification_stats": state["stats"],
        "last_classified_at": datetime.now().isoformat(),
    }

    with open(STATE_FILE, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\n✅ State saved → {STATE_FILE}")
    print(f"   Queue: {len(merged_queue)} to archive | Kept: {len(keep_items)}")


# ── Main classifier ───────────────────────────────────────────────────────────

def run_classifier(limit: int = 0, resume: bool = False, dry_run: bool = False,
                   batch_size: int = 20):
    """Main entry point — uses subprocess to call openclaw browser tool."""

    print("🔍 LinkedIn Conversation Classifier")
    print("=" * 50)

    # Load intermediate state if resuming
    state = load_intermediate() if resume else {
        "scanned": [],
        "seen_names": set(),
        "stats": {
            "total_scanned": 0,
            "archived": 0,
            "kept": 0,
            "reasons": {}
        }
    }

    if resume and state["scanned"]:
        seen = set(state["seen_names"])
        print(f"▶️  Resuming from {state['stats']['total_scanned']} conversations scanned")
    else:
        seen = set()

    # We'll use openclaw's built-in Python browser API via subprocess calls
    # to avoid needing to import openclaw modules directly.
    # The script drives the browser via the `openclaw browser` CLI or
    # by calling the agent tool indirectly.
    #
    # For standalone operation, we use a helper that calls the browser
    # through openclaw's REST API or via the agent's browser tool.
    #
    # Since this script is CALLED by the agent (not standalone), the agent
    # will handle browser interactions. This script provides the classification
    # logic and state management.
    #
    # AGENT-DRIVEN MODE: The agent reads this script's classify() function
    # and calls it directly with data extracted from browser snapshots.

    print("\n📋 This script is designed to be driven by the OpenClaw agent.")
    print("   The agent handles browser snapshots and passes conversation data here.")
    print("   For direct invocation, use: --agent-mode\n")

    # Provide the classification engine as a library
    return state


def classify_batch(conversations: list[dict], state: dict,
                   dry_run: bool = False) -> dict:
    """
    Classify a batch of conversations and update state.
    Called by the agent after each browser snapshot.

    Args:
        conversations: List of conv dicts from parse_conversations_from_snapshot()
        state: Current classification state
        dry_run: If True, don't save intermediate state

    Returns:
        Updated state dict
    """
    seen = set(state.get("seen_names", []))

    for conv in conversations:
        name = conv.get("name", "").strip()
        if not name or name in seen:
            continue

        seen.add(name)

        # Google Contacts lookup
        in_contacts = is_in_google_contacts(name)

        # Classify
        decision, reasons = classify_conversation(conv, in_contacts)

        # Update stats
        state["stats"]["total_scanned"] += 1
        if decision == "ARCHIVE":
            state["stats"]["archived"] += 1
        else:
            state["stats"]["kept"] += 1

        # Track reasons
        for r in reasons:
            # Normalize reason key (strip dynamic parts for aggregation)
            key = re.sub(r'\([^)]+\)', '', r).rstrip('_')
            state["stats"]["reasons"][key] = state["stats"]["reasons"].get(key, 0) + 1

        # Record
        entry = {
            **conv,
            "decision": decision,
            "keep_reasons": reasons if decision == "KEEP" else [],
            "archive_reasons": reasons if decision == "ARCHIVE" else [],
            "in_contacts": in_contacts,
        }
        state["scanned"].append(entry)

        total = state["stats"]["total_scanned"]
        archived = state["stats"]["archived"]
        kept = state["stats"]["kept"]

        # Progress print every 10
        if total % 10 == 0:
            print(f"  Scanned {total}: {archived} archive, {kept} keep  |  latest: {name} → {decision}")

        # Save intermediate every 50
        if not dry_run and total % 50 == 0:
            state["seen_names"] = list(seen)
            save_intermediate(state)
            print(f"  💾 Intermediate save at {total} conversations")

    state["seen_names"] = list(seen)
    return state


# ── Agent-facing entrypoint ───────────────────────────────────────────────────

def agent_classify_from_snapshot(snapshot_text: str, state_path: str = None,
                                  resume: bool = False) -> dict:
    """
    High-level function called by the OpenClaw agent.

    1. Parses conversations from snapshot
    2. Classifies them
    3. Updates and saves state
    4. Returns updated state

    Args:
        snapshot_text: Raw text from browser snapshot
        state_path: Override for intermediate state file path
        resume: Load existing intermediate state first

    Returns:
        Updated state dict with classification results
    """
    global INTERMEDIATE_FILE
    if state_path:
        INTERMEDIATE_FILE = Path(state_path)

    state = load_intermediate() if resume else {
        "scanned": [],
        "seen_names": [],
        "stats": {
            "total_scanned": 0,
            "archived": 0,
            "kept": 0,
            "reasons": {}
        }
    }

    conversations = parse_conversations_from_snapshot(snapshot_text)
    if not conversations:
        print("⚠️  No conversations parsed from snapshot")
        return state

    print(f"  Parsed {len(conversations)} conversations from snapshot")
    state = classify_batch(conversations, state)

    return state


def finalize(state: dict, dry_run: bool = False):
    """Save final state and print summary."""
    total = state["stats"]["total_scanned"]
    archived = state["stats"]["archived"]
    kept = state["stats"]["kept"]

    print("\n" + "=" * 50)
    print(f"📊 Classification Complete")
    print(f"   Total scanned:  {total}")
    print(f"   To archive:     {archived} ({100*archived//max(total,1)}%)")
    print(f"   To keep:        {kept} ({100*kept//max(total,1)}%)")
    print("\n  Top archive reasons:")
    sorted_reasons = sorted(state["stats"]["reasons"].items(), key=lambda x: -x[1])
    for reason, count in sorted_reasons[:10]:
        print(f"    {reason:<35} {count:>5}")

    if not dry_run:
        save_final_state(state)
        # Clean up intermediate
        if INTERMEDIATE_FILE.exists():
            INTERMEDIATE_FILE.unlink()
            print(f"  🗑  Removed intermediate file")
    else:
        print("\n  [DRY RUN] — state file not written")


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LinkedIn Conversation Classifier")
    parser.add_argument("--limit", type=int, default=0,
                        help="Stop after N conversations (0=unlimited)")
    parser.add_argument("--resume", action="store_true",
                        help="Resume from last intermediate save")
    parser.add_argument("--dry-run", action="store_true",
                        help="Classify but don't write state file")
    parser.add_argument("--batch-size", type=int, default=20,
                        help="Conversations per batch")
    parser.add_argument("--test-parse", metavar="FILE",
                        help="Test snapshot parsing on a file (print results, exit)")
    parser.add_argument("--finalize", action="store_true",
                        help="Finalize intermediate state into main state file")

    args = parser.parse_args()

    if args.test_parse:
        with open(args.test_parse) as f:
            text = f.read()
        convs = parse_conversations_from_snapshot(text)
        print(f"Parsed {len(convs)} conversations:")
        for c in convs[:20]:
            print(f"  {c['name']!r:40} | {c['date']!r:15} | {c['preview'][:50]!r}")
        sys.exit(0)

    if args.finalize:
        state = load_intermediate()
        if not state["scanned"]:
            print("No intermediate state to finalize.")
            sys.exit(1)
        finalize(state, dry_run=args.dry_run)
        sys.exit(0)

    # Normal run: print instructions for agent-driven mode
    print(__doc__)
    print("\nTo classify conversations, the OpenClaw agent will:")
    print("1. Navigate to https://www.linkedin.com/messaging/")
    print("2. Take browser snapshots")
    print("3. Call agent_classify_from_snapshot(snapshot_text, resume=True)")
    print("4. Scroll and repeat until all conversations scanned")
    print("5. Call finalize(state) to write the final state file")
    print("\nOr run with --test-parse <snapshot.txt> to test parsing.")
