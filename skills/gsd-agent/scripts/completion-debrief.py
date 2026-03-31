#!/usr/bin/env python3
"""
Completion Debrief System
Checks Things 3 for newly completed tasks, logs them to done.md,
and returns a summary for the GSD agent to send to Alex.
"""

import json
import subprocess
import sys
import os
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

STATE_FILE = os.path.expanduser("~/.openclaw/workspace/memory/debrief-state.json")
DONE_FILE = os.path.expanduser("~/SecondBrain/GTD/done.md")


def load_state() -> Dict[str, Any]:
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {"debriefed_uuids": [], "last_check": None}


def save_state(state: Dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def get_completed_tasks(scope: str = "all") -> List[Dict[str, Any]]:
    """Get completed tasks from Things 3."""
    cmd = "logtoday" if scope == "today" else "completed"
    try:
        result = subprocess.run(
            ["things", cmd, "--json"],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0:
            print(f"Error running things {cmd}: {result.stderr}", file=sys.stderr)
            return []
        return json.loads(result.stdout)
    except Exception as e:
        print(f"Exception getting completed tasks: {e}", file=sys.stderr)
        return []


def calc_velocity_days(created: Optional[str], stopped: Optional[str]) -> Optional[int]:
    """Calculate days from creation to completion."""
    if not created or not stopped:
        return None
    try:
        # Handle both "YYYY-MM-DD" and "YYYY-MM-DD HH:MM:SS" formats
        created_date = datetime.strptime(created[:10], "%Y-%m-%d")
        stopped_date = datetime.strptime(stopped[:10], "%Y-%m-%d")
        return max(0, (stopped_date - created_date).days)
    except (ValueError, TypeError):
        return None


def append_to_done(tasks: List[Dict[str, Any]]) -> None:
    """Append completed tasks to done.md."""
    if not tasks:
        return
    os.makedirs(os.path.dirname(DONE_FILE), exist_ok=True)
    with open(DONE_FILE, "a") as f:
        for task in tasks:
            title = task.get("title", "Untitled")
            stop_date = task.get("stop_date", "unknown")
            area = task.get("area_title", "No Area")
            created = task.get("created", "unknown")
            velocity = calc_velocity_days(created, stop_date)
            velocity_str = f", velocity: {velocity}d" if velocity is not None else ""
            project = task.get("project_title")
            project_str = f", project: {project}" if project else ""
            f.write(
                f"- [x] {title} — completed: {stop_date}, "
                f"area: {area}{project_str}, "
                f"created: {created}{velocity_str}\n"
            )


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Completion debrief for Things 3")
    parser.add_argument("--scope", choices=["today", "all"], default="all",
                        help="Scope: 'today' for logtoday, 'all' for all completed")
    parser.add_argument("--days", type=int, default=7,
                        help="Only consider tasks completed in last N days (for 'all' scope)")
    args = parser.parse_args()

    state = load_state()
    debriefed = set(state.get("debriefed_uuids", []))

    completed = get_completed_tasks(args.scope)

    # Filter to recent if using 'all' scope
    if args.scope == "all" and args.days:
        cutoff = (datetime.now() - timedelta(days=args.days)).strftime("%Y-%m-%d")
        completed = [
            t for t in completed
            if t.get("stop_date", "") >= cutoff
        ]

    # Find newly completed (not yet debriefed)
    newly_completed = [t for t in completed if t.get("uuid") not in debriefed]

    if newly_completed:
        # Log to done.md
        append_to_done(newly_completed)

        # Update state
        for t in newly_completed:
            debriefed.add(t["uuid"])

    # Calculate velocity stats
    velocities = []
    for t in completed:
        v = calc_velocity_days(t.get("created"), t.get("stop_date"))
        if v is not None:
            velocities.append(v)

    avg_velocity = round(sum(velocities) / len(velocities), 1) if velocities else None

    # Save state
    state["debriefed_uuids"] = list(debriefed)
    state["last_check"] = datetime.now().isoformat()
    save_state(state)

    # Output summary
    summary = {
        "newly_completed": [
            {
                "title": t.get("title"),
                "area": t.get("area_title"),
                "project": t.get("project_title"),
                "completed": t.get("stop_date"),
                "velocity_days": calc_velocity_days(t.get("created"), t.get("stop_date"))
            }
            for t in newly_completed
        ],
        "total_completed_in_scope": len(completed),
        "total_debriefed": len(debriefed),
        "avg_velocity_days": avg_velocity,
        "newly_logged": len(newly_completed)
    }

    print(json.dumps(summary, indent=2))
    return 0 if not newly_completed else len(newly_completed)


if __name__ == "__main__":
    sys.exit(main())
