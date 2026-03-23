#!/usr/bin/env python3
"""
cleanup_state.py — State management helper for LinkedIn cleanup.

Usage:
    python3 cleanup_state.py status
    python3 cleanup_state.py mark-done "<conversation name>"
    python3 cleanup_state.py set-error "<error description>"
    python3 cleanup_state.py unpause
    python3 cleanup_state.py reset-today
    python3 cleanup_state.py next [N]        # show next N conversations to archive
    python3 cleanup_state.py check-limits    # exit 0 if OK to run, 1 if should stop
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
import zoneinfo

STATE_FILE = "/Users/debra/.openclaw/workspace/memory/linkedin-cleanup-state.json"

# Rate limits (hard limits — do not change without updating SKILL.md)
MAX_PER_SESSION = 50
MAX_PER_DAY = 150
MAX_SESSION_MINUTES = 15
BUSINESS_HOURS_START = 9   # 9 AM ET
BUSINESS_HOURS_END = 17    # 5 PM ET
COOLDOWN_EVERY_N_DAYS = 3  # skip every 3rd calendar day

ET = zoneinfo.ZoneInfo("America/New_York")


def load_state() -> dict:
    path = Path(STATE_FILE)
    if not path.exists():
        print(f"❌ State file not found: {STATE_FILE}")
        print("   Run generate_queue.py first.")
        sys.exit(1)
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError as e:
        print(f"❌ State file is corrupt: {e}")
        sys.exit(1)


def save_state(state: dict):
    path = Path(STATE_FILE)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2, ensure_ascii=False))


def today_str() -> str:
    return datetime.now(ET).strftime("%Y-%m-%d")


def reset_daily_counter_if_needed(state: dict) -> dict:
    """Reset todayArchived if it's a new day."""
    today = today_str()
    if state.get("todayDate") != today:
        state["todayDate"] = today
        state["todayArchived"] = 0
    return state


def is_business_hours() -> bool:
    now = datetime.now(ET)
    if now.weekday() >= 5:  # Saturday=5, Sunday=6
        return False
    return BUSINESS_HOURS_START <= now.hour < BUSINESS_HOURS_END


def is_cooldown_day() -> bool:
    """Returns True if today is a cooldown day (every 3rd day since epoch)."""
    today = datetime.now(ET)
    day_number = today.toordinal()
    return (day_number % COOLDOWN_EVERY_N_DAYS) == 0


def check_limits(state: dict, session_count: int = 0) -> tuple[bool, str]:
    """
    Returns (can_continue, reason).
    can_continue=True means safe to proceed.
    """
    state = reset_daily_counter_if_needed(state)
    
    if state.get("paused"):
        return False, f"Paused. Last error: {state.get('lastError', 'none')}. Run 'unpause' to resume."
    
    if not state.get("queue"):
        return False, "Queue is empty — all done! 🎉"
    
    if not is_business_hours():
        now = datetime.now(ET)
        return False, f"Outside business hours (9am–5pm ET weekdays). Current time: {now.strftime('%A %I:%M %p %Z')}"
    
    if is_cooldown_day():
        return False, f"Today is a cooldown day (skip every {COOLDOWN_EVERY_N_DAYS}rd day). Try tomorrow."
    
    today_count = state.get("todayArchived", 0)
    if today_count >= MAX_PER_DAY:
        return False, f"Daily limit reached: {today_count}/{MAX_PER_DAY} archives today. Try again tomorrow."
    
    if session_count >= MAX_PER_SESSION:
        return False, f"Session limit reached: {session_count}/{MAX_PER_SESSION} archives this session."
    
    remaining_today = MAX_PER_DAY - today_count
    remaining_session = MAX_PER_SESSION - session_count
    can_do = min(remaining_today, remaining_session)
    
    return True, f"OK to proceed. Can archive up to {can_do} more (session: {remaining_session}, today: {remaining_today})"


def cmd_status(state: dict):
    state = reset_daily_counter_if_needed(state)
    
    total_queued = state.get("totalQueued", 0)
    total_archived = state.get("totalArchived", 0)
    today_archived = state.get("todayArchived", 0)
    queue_len = len(state.get("queue", []))
    last_run = state.get("lastRunAt", "never")
    last_error = state.get("lastError")
    paused = state.get("paused", False)
    
    pct = (total_archived / total_queued * 100) if total_queued > 0 else 0
    
    # Progress bar
    bar_width = 30
    filled = int(bar_width * pct / 100)
    bar = "█" * filled + "░" * (bar_width - filled)
    
    print("\n" + "="*55)
    print("🧹 LinkedIn Cleanup Status")
    print("="*55)
    print(f"  Progress: [{bar}] {pct:.1f}%")
    print(f"  Archived: {total_archived:,} / {total_queued:,} total")
    print(f"  Remaining: {queue_len:,} in queue")
    print(f"  Today: {today_archived} / {MAX_PER_DAY} (date: {state.get('todayDate')})")
    print(f"  Last run: {last_run}")
    
    if paused:
        print(f"\n  ⏸️  PAUSED — Error: {last_error}")
        print("  Run 'unpause' to resume after investigating")
    elif last_error:
        print(f"\n  ⚠️  Last error: {last_error}")
    
    can_run, reason = check_limits(state)
    status_icon = "✅" if can_run else "🚫"
    print(f"\n  {status_icon} Run status: {reason}")
    
    if queue_len > 0:
        per_day = MAX_PER_DAY
        active_ratio = (COOLDOWN_EVERY_N_DAYS - 1) / COOLDOWN_EVERY_N_DAYS
        active_days_per_week = 5 * active_ratio
        weeks = (queue_len / per_day) / active_days_per_week
        print(f"\n  ⏱️  Est. completion: ~{weeks:.1f} weeks at {per_day}/day")
    
    print("="*55 + "\n")


def cmd_mark_done(state: dict, name: str):
    state = reset_daily_counter_if_needed(state)
    queue = state.get("queue", [])
    
    # Find by exact name match first, then partial
    found = None
    for i, item in enumerate(queue):
        if item["name"] == name:
            found = i
            break
    
    if found is None:
        for i, item in enumerate(queue):
            if name.lower() in item["name"].lower():
                found = i
                print(f"⚠️  Exact match not found, using partial match: '{item['name']}'")
                break
    
    if found is None:
        print(f"❌ Conversation not found in queue: '{name}'")
        sys.exit(1)
    
    item = queue.pop(found)
    item["archivedAt"] = datetime.now(ET).isoformat()
    
    completed = state.get("completed", [])
    completed.append(item)
    
    state["queue"] = queue
    state["completed"] = completed
    state["totalArchived"] = len(completed)
    state["todayArchived"] = state.get("todayArchived", 0) + 1
    state["lastRunAt"] = datetime.now(ET).isoformat()
    state["lastError"] = None  # clear error on success
    
    save_state(state)
    
    cat_icon = "⚪" if item.get("category") == "spam" else "🟢"
    today = state["todayArchived"]
    total = state["totalArchived"]
    print(f"✅ Archived: {cat_icon} {item['name']} (today: {today}/{MAX_PER_DAY}, total: {total:,})")


def cmd_set_error(state: dict, error: str):
    state["lastError"] = error
    state["paused"] = True
    state["lastRunAt"] = datetime.now(ET).isoformat()
    save_state(state)
    print(f"⏸️  Paused with error: {error}")
    print("   Investigate, then run 'unpause' to resume.")


def cmd_unpause(state: dict):
    state["paused"] = False
    # Keep lastError for reference but allow running
    save_state(state)
    print("▶️  Unpaused. Ready to run.")
    if state.get("lastError"):
        print(f"   (Previous error was: {state['lastError']})")


def cmd_reset_today(state: dict):
    today = today_str()
    confirm = input(f"⚠️  Reset today's archive count to 0? (current: {state.get('todayArchived', 0)}) [yes/no]: ")
    if confirm.strip().lower() != "yes":
        print("Aborted.")
        return
    state["todayArchived"] = 0
    state["todayDate"] = today
    save_state(state)
    print("✅ Daily counter reset to 0.")


def cmd_next(state: dict, n: int = 10):
    queue = state.get("queue", [])
    if not queue:
        print("Queue is empty!")
        return
    print(f"\n📋 Next {min(n, len(queue))} conversations to archive:")
    for i, item in enumerate(queue[:n]):
        cat_icon = "⚪" if item.get("category") == "spam" else "🟢"
        print(f"  {i+1:3}. {cat_icon} {item['name']}")
    if len(queue) > n:
        print(f"  ... and {len(queue) - n:,} more")
    print()


def cmd_check_limits(state: dict):
    """Exit 0 if OK to run, exit 1 if should stop."""
    can_run, reason = check_limits(state)
    print(reason)
    sys.exit(0 if can_run else 1)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    command = sys.argv[1]
    state = load_state()
    
    if command == "status":
        cmd_status(state)
    
    elif command == "mark-done":
        if len(sys.argv) < 3:
            print("Usage: mark-done \"<conversation name>\"")
            sys.exit(1)
        cmd_mark_done(state, sys.argv[2])
    
    elif command == "set-error":
        if len(sys.argv) < 3:
            print("Usage: set-error \"<error description>\"")
            sys.exit(1)
        cmd_set_error(state, sys.argv[2])
    
    elif command == "unpause":
        cmd_unpause(state)
    
    elif command == "reset-today":
        cmd_reset_today(state)
    
    elif command == "next":
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        cmd_next(state, n)
    
    elif command == "check-limits":
        cmd_check_limits(state)
    
    else:
        print(f"Unknown command: {command}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
