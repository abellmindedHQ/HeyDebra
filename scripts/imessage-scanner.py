#!/usr/bin/env python3
"""
iMessage Scanner — READ-ONLY BlueBubbles API poller
Scans Alex's iMessages for action items, calendar events, people info, and financials.
NEVER sends messages. Ever.

Usage:
    python3 scripts/imessage-scanner.py [--password <pw>] [--since <timestamp_ms>] [--dry-run] [--verbose]

Environment:
    BB_ALEX_PASSWORD  BlueBubbles server password

BB API: http://localhost:1235 (v1.9.9+)
  POST /api/v1/message/query  — fetch messages with filters
  POST /api/v1/chat/query     — fetch chats
  GET  /api/v1/server/info    — health check
"""

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

# ─── Config ───────────────────────────────────────────────────────────────────

BB_BASE_URL = "http://localhost:1235"
WORKSPACE   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCAN_DIR    = os.path.join(WORKSPACE, "memory", "imessage-scan")
STATE_FILE  = os.path.join(SCAN_DIR, "scan-state.json")

# Known contacts (normalized phone → name)
KNOWN_CONTACTS = {
    "+16158101319": "Hannah",
    "+16159745363": "Chelsea",
    "+12292247731": "Sallijo",
    "+18135343383": "Alex",
    "+13213562000": "Pooja",
    "+19735107652": "Merle",
    "+18137600833": "Marco",
    "+18133682433": "Omar",
    "drdebrapepper@gmail.com": "Debra",
    "alexander.o.abell@gmail.com": "Alex",
}

# ─── Regex classifiers ────────────────────────────────────────────────────────

ACTION_PATTERNS = [
    r"\bI'?ll\b",
    r"\bI will\b",
    r"\bgonna\b",
    r"\bgoing to\b",
    r"\bneed to\b",
    r"\bhave to\b",
    r"\bshould\b",
    r"\bremind me\b",
    r"\bcan you\b",
    r"\bcould you\b",
    r"\bwould you\b",
    r"\bplease\b",
    r"\bby (monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b",
    r"\bby tomorrow\b",
    r"\bby end of\b",
    r"\bby (jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\b",
    r"\bby \d+[\/\-]\d+\b",
    r"\bpick up\b",
    r"\bdrop off\b",
    r"\bcall\b",
    r"\bemail\b",
    r"\btext\b",
    r"\bsend\b",
    r"\bdon'?t forget\b",
    r"\bmake sure\b",
]

CALENDAR_PATTERNS = [
    r"\bat \d{1,2}(:\d{2})?\s*(am|pm)?\b",
    r"\bat noon\b",
    r"\bat midnight\b",
    r"\bby \d{1,2}(:\d{2})?\s*(am|pm)\b",
    r"\btomorrow\b",
    r"\bthis (morning|afternoon|evening|weekend|week|month)\b",
    r"\bnext (monday|tuesday|wednesday|thursday|friday|saturday|sunday|week|month)\b",
    r"\b(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b",
    r"\bmeeting\b",
    r"\bappointment\b",
    r"\bdinner\b",
    r"\blunch\b",
    r"\bbreakfast\b",
    r"\brehearsal\b",
    r"\bpractice\b",
    r"\bevent\b",
    r"\bschool\b",
    r"\bpickup\b",
    r"\bpick up\b",
    r"\bdrop off\b",
    r"\b\d{1,2}:\d{2}\s*(am|pm)\b",
]

FINANCIAL_PATTERNS = [
    r"\$\d+(\.\d{2})?",
    r"\b\d+\s*dollars?\b",
    r"\bpay\b",
    r"\bowed?\b",
    r"\bbill\b",
    r"\bcharged?\b",
    r"\brefund\b",
    r"\bvenmo\b",
    r"\bzelle\b",
    r"\bpaypal\b",
    r"\bcash\b",
    r"\bfee\b",
    r"\bcost\b",
    r"\bprice\b",
    r"\bexpense\b",
    r"\brent\b",
    r"\bmortgage\b",
]

PEOPLE_PATTERNS = [
    r"\bmy (mom|dad|sister|brother|boss|wife|husband|girlfriend|boyfriend|daughter|son|aunt|uncle|friend)\b",
    r"\bher (mom|dad|sister|brother|daughter|son)\b",
    r"\bhis (mom|dad|sister|brother|daughter|son)\b",
    r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b",  # proper names
    r"\+1\d{10}",                              # phone numbers
    r"\b\(\d{3}\)\s*\d{3}[-.]?\d{4}\b",       # formatted phone numbers
]

_action_re    = re.compile("|".join(ACTION_PATTERNS),   re.IGNORECASE)
_calendar_re  = re.compile("|".join(CALENDAR_PATTERNS), re.IGNORECASE)
_financial_re = re.compile("|".join(FINANCIAL_PATTERNS),re.IGNORECASE)
_people_re    = re.compile("|".join(PEOPLE_PATTERNS))

# ─── HTTP helpers ─────────────────────────────────────────────────────────────

def log(msg, verbose=False, force=False):
    if force or verbose:
        ts = datetime.now().strftime("%H:%M:%S")
        print(f"[{ts}] [imessage-scanner] {msg}", file=sys.stderr)


def bb_get(path, password, verbose=False):
    """GET request to BB API. Returns parsed JSON or None."""
    url = f"{BB_BASE_URL}{path}?password={urllib.parse.quote(password)}"
    safe_url = url.replace(urllib.parse.quote(password), "***")
    log(f"GET {safe_url}", verbose=verbose)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "imessage-scanner/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        if e.code == 401:
            log("AUTH FAILURE — check BB_ALEX_PASSWORD", force=True)
        else:
            log(f"HTTP {e.code} for GET {safe_url}", force=True)
        return None
    except urllib.error.URLError as e:
        log(f"Cannot reach BB at {BB_BASE_URL}: {e.reason}", force=True)
        return None
    except Exception as e:
        log(f"GET error: {e}", force=True)
        return None


def bb_post(path, body, password, verbose=False):
    """POST request to BB API. Returns parsed JSON or None."""
    url = f"{BB_BASE_URL}{path}?password={urllib.parse.quote(password)}"
    safe_url = url.replace(urllib.parse.quote(password), "***")
    log(f"POST {safe_url} body={json.dumps(body)[:200]}", verbose=verbose)
    try:
        data = json.dumps(body).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={
                "User-Agent":   "imessage-scanner/1.0",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body_preview = e.read(200).decode("utf-8", errors="replace")
        if e.code == 401:
            log("AUTH FAILURE — check BB_ALEX_PASSWORD", force=True)
        else:
            log(f"HTTP {e.code} for POST {safe_url}: {body_preview}", force=True)
        return None
    except urllib.error.URLError as e:
        log(f"Cannot reach BB at {BB_BASE_URL}: {e.reason}", force=True)
        return None
    except Exception as e:
        log(f"POST error: {e}", force=True)
        return None


# ─── State ────────────────────────────────────────────────────────────────────

def load_state():
    if not os.path.exists(STATE_FILE):
        return {
            "lastScanTimestamp": 0,
            "lastScanAt": None,
            "totalScanned": 0,
            "totalActionItems": 0,
        }
    try:
        with open(STATE_FILE) as f:
            return json.load(f)
    except Exception:
        return {
            "lastScanTimestamp": 0,
            "lastScanAt": None,
            "totalScanned": 0,
            "totalActionItems": 0,
        }


def save_state(state, dry_run=False):
    if dry_run:
        print(f"[DRY RUN] Would save state:\n{json.dumps(state, indent=2)}")
        return
    os.makedirs(SCAN_DIR, exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


# ─── Message processing ───────────────────────────────────────────────────────

def normalize_address(address):
    """Normalize a phone number/email to a consistent form."""
    if not address:
        return ""
    if "@" in address:
        return address.lower()
    digits = re.sub(r"\D", "", address)
    if len(digits) == 10:
        return f"+1{digits}"
    if len(digits) == 11 and digits.startswith("1"):
        return f"+{digits}"
    return address


def sender_label(msg, chats_by_guid=None):
    """Return a human-readable sender label."""
    handle = msg.get("handle") or {}
    address = handle.get("address", "")
    normalized = normalize_address(address)

    if normalized and normalized in KNOWN_CONTACTS:
        return KNOWN_CONTACTS[normalized]
    if address:
        return address

    # Fallback to chat display name
    if chats_by_guid:
        for chat_ref in (msg.get("chats") or []):
            guid = chat_ref.get("guid", "")
            chat = chats_by_guid.get(guid, {})
            display = chat.get("displayName") or ""
            if display:
                return display
            # Try participants
            for p in (chat.get("participants") or []):
                paddr = normalize_address(p.get("address", ""))
                if paddr in KNOWN_CONTACTS:
                    return KNOWN_CONTACTS[paddr]

    return "Unknown"


def format_time_ms(timestamp_ms):
    """Format millisecond timestamp to human time string."""
    try:
        dt = datetime.fromtimestamp(timestamp_ms / 1000)
        return dt.strftime("%-I:%M %p")
    except Exception:
        return "?"


def classify_message(text):
    """Return classification flags for a message body."""
    if not text or not text.strip():
        return {}
    return {
        "action":    bool(_action_re.search(text)),
        "calendar":  bool(_calendar_re.search(text)),
        "financial": bool(_financial_re.search(text)),
        "people":    bool(_people_re.search(text)),
    }


def build_report(messages, chats_by_guid, scan_time_str, verbose=False):
    """Build the markdown report section from a batch of messages."""
    action_items    = []
    calendar_items  = []
    financial_items = []
    people_items    = []
    notable_msgs    = []

    seen = set()

    for msg in messages:
        text = (msg.get("text") or "").strip()
        if not text:
            continue

        # Skip system messages
        if msg.get("isSystemMessage") or msg.get("itemType", 0) != 0:
            continue

        dedup_key = text[:120]
        if dedup_key in seen:
            continue
        seen.add(dedup_key)

        flags    = classify_message(text)
        sender   = sender_label(msg, chats_by_guid)
        time_str = format_time_ms(msg.get("dateCreated", 0))
        snippet  = text[:160].replace("\n", " ")
        from_me  = bool(msg.get("isFromMe", False))
        direction = "→" if from_me else "←"

        if flags.get("action"):
            action_items.append(f"- [ ] {snippet} ({direction}{sender}, {time_str})")

        if flags.get("calendar"):
            calendar_items.append(f"- {snippet} — source: {sender}")

        if flags.get("financial"):
            financial_items.append(f"- {snippet} ({direction}{sender}, {time_str})")

        if flags.get("people") and not from_me:
            people_items.append(f"- {sender}: \"{snippet}\"")

        if any(flags.values()):
            notable_msgs.append(f"- {sender}: \"{snippet}\"")

        if verbose and any(flags.values()):
            log(f"  [{','.join(k for k,v in flags.items() if v)}] {sender}: {snippet[:80]}", force=True)

    # Deduplicate (preserve order)
    def dedup(lst):
        seen_items = set()
        out = []
        for item in lst:
            if item not in seen_items:
                seen_items.add(item)
                out.append(item)
        return out

    action_items    = dedup(action_items)
    calendar_items  = dedup(calendar_items)
    financial_items = dedup(financial_items)
    people_items    = dedup(people_items)
    notable_msgs    = dedup(notable_msgs)

    # Count unique chats represented
    chat_count = len(set(
        c.get("guid", "")
        for msg in messages
        for c in (msg.get("chats") or [])
        if c.get("guid")
    ))

    lines = [
        f"## Scan: {scan_time_str}",
        f"**Messages scanned:** {len(messages)} (from ~{chat_count} chats)",
        "",
    ]

    if action_items:
        lines.append("### Action Items")
        lines.extend(action_items[:30])
        lines.append("")

    if calendar_items:
        lines.append("### Calendar")
        lines.extend(calendar_items[:20])
        lines.append("")

    if financial_items:
        lines.append("### Financial")
        lines.extend(financial_items[:20])
        lines.append("")

    if people_items:
        lines.append("### People")
        lines.extend(people_items[:20])
        lines.append("")

    if notable_msgs:
        lines.append("### Notable Messages")
        lines.extend(notable_msgs[:25])
        lines.append("")

    if not any([action_items, calendar_items, financial_items, people_items, notable_msgs]):
        lines.append("_No notable items found in this scan._")
        lines.append("")

    lines.append("---")
    lines.append("")

    return "\n".join(lines), len(action_items)


def write_report(content, dry_run=False):
    date_str = datetime.now().strftime("%Y-%m-%d")
    path = os.path.join(SCAN_DIR, f"{date_str}.md")
    if dry_run:
        print("\n" + "=" * 60)
        print(f"[DRY RUN] Would append to: {path}")
        print("=" * 60)
        print(content)
        return
    os.makedirs(SCAN_DIR, exist_ok=True)
    with open(path, "a") as f:
        f.write(content)
    log(f"Wrote to {path}", force=True)


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="READ-ONLY iMessage scanner via BlueBubbles API. NEVER sends messages."
    )
    parser.add_argument("--password",  help="BB server password (overrides BB_ALEX_PASSWORD env var)")
    parser.add_argument("--since",     type=int, help="Scan messages after this Unix timestamp (ms)")
    parser.add_argument("--dry-run",   action="store_true", help="Print report without writing files")
    parser.add_argument("--verbose",   action="store_true", help="Verbose debug output")
    parser.add_argument("--limit",     type=int, default=200, help="Max messages per fetch (default 200)")
    args = parser.parse_args()

    # ── Password resolution ───────────────────────────────────────────────────
    password = args.password or os.environ.get("BB_ALEX_PASSWORD", "")
    if not password:
        env_file = os.path.join(WORKSPACE, ".env")
        if os.path.exists(env_file):
            with open(env_file) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("BB_ALEX_PASSWORD="):
                        password = line.split("=", 1)[1].strip().strip('"').strip("'")
                        break
    if not password:
        print("ERROR: No BB password. Set BB_ALEX_PASSWORD env var or use --password.", file=sys.stderr)
        sys.exit(1)

    # ── Load scan state ───────────────────────────────────────────────────────
    state = load_state()
    since_ts = args.since if args.since is not None else state.get("lastScanTimestamp", 0)
    log(f"Scanning messages after timestamp: {since_ts}", verbose=args.verbose, force=True)

    # ── Health check ──────────────────────────────────────────────────────────
    ping = bb_get("/api/v1/server/info", password, verbose=args.verbose)
    if ping is None:
        log("Cannot connect to BlueBubbles. Exiting gracefully.", force=True)
        sys.exit(0)
    if ping.get("status") == 401:
        log("AUTH FAILURE. Check BB_ALEX_PASSWORD.", force=True)
        sys.exit(0)
    log(f"BB server OK (v{ping.get('data', {}).get('server_version', '?')})", verbose=args.verbose, force=True)

    # ── Fetch chats for display name lookup ───────────────────────────────────
    chats_by_guid = {}
    chats_resp = bb_post(
        "/api/v1/chat/query",
        {"limit": 200, "offset": 0},
        password,
        verbose=args.verbose,
    )
    if chats_resp and isinstance(chats_resp.get("data"), list):
        for chat in chats_resp["data"]:
            guid = chat.get("guid", "")
            if guid:
                chats_by_guid[guid] = chat
        log(f"Loaded {len(chats_by_guid)} chats", verbose=args.verbose)

    # ── Fetch messages since watermark ────────────────────────────────────────
    query_body = {
        "limit":  args.limit,
        "offset": 0,
        "with":   ["chats", "handles"],
        "sort":   "ASC",
    }
    if since_ts > 0:
        query_body["after"] = since_ts

    msgs_resp = bb_post(
        "/api/v1/message/query",
        query_body,
        password,
        verbose=args.verbose,
    )
    if msgs_resp is None:
        log("Failed to fetch messages. Exiting gracefully.", force=True)
        sys.exit(0)

    messages = msgs_resp.get("data", [])
    if not isinstance(messages, list):
        log(f"Unexpected messages format: {type(messages)}", force=True)
        sys.exit(0)

    log(f"Fetched {len(messages)} messages", force=True)

    # ── Build and write report ────────────────────────────────────────────────
    now_et = datetime.now().strftime("%-I:%M %p ET")
    report, action_count = build_report(messages, chats_by_guid, now_et, verbose=args.verbose)

    if messages or args.dry_run:
        write_report(report, dry_run=args.dry_run)

    # ── Update watermark ──────────────────────────────────────────────────────
    max_ts = max(
        (msg.get("dateCreated", 0) for msg in messages if msg.get("dateCreated")),
        default=since_ts,
    )
    new_ts = max(max_ts, since_ts)

    new_state = {
        "lastScanTimestamp": new_ts,
        "lastScanAt": datetime.now(timezone.utc).isoformat(),
        "totalScanned": state.get("totalScanned", 0) + len(messages),
        "totalActionItems": state.get("totalActionItems", 0) + action_count,
    }
    save_state(new_state, dry_run=args.dry_run)

    log(
        f"Done. Scanned: {len(messages)} messages, {action_count} action items. "
        f"New watermark: {new_ts}",
        force=True,
    )


if __name__ == "__main__":
    main()
