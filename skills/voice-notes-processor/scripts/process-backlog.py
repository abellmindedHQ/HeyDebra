#!/usr/bin/env python3
"""
process-backlog.py — Process all unprocessed audio files in the voice-notes drop folder.

Usage:
    python3 process-backlog.py [--dry-run]

Environment:
    ASSEMBLYAI_API_KEY — required

Scans ~/SecondBrain/Imports/voice-notes/ for audio files and processes each one
that hasn't already been processed (per state file). Skips files already in /processed/.
"""

import sys
import os
import json
import subprocess
from pathlib import Path
from datetime import datetime

# ── Config ────────────────────────────────────────────────────────────────────
DROP_FOLDER  = Path.home() / "SecondBrain" / "Imports" / "voice-notes"
STATE_FILE   = Path("/Users/debra/.openclaw/workspace/memory/voice-notes-state.json")
SUPPORTED_EXTENSIONS = {".m4a", ".mp3", ".wav", ".ogg", ".webm", ".mp4"}

SCRIPT_DIR     = Path(__file__).parent
PROCESS_SCRIPT = SCRIPT_DIR / "process-audio.py"


def load_state() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except Exception:
            pass
    return {"processed": [], "last_run": None}


def save_state(state: dict):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2, default=str))


def main():
    dry_run = "--dry-run" in sys.argv

    if not os.environ.get("ASSEMBLYAI_API_KEY"):
        print("[voice-notes] ERROR: ASSEMBLYAI_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    if not DROP_FOLDER.exists():
        print(f"[voice-notes] Drop folder does not exist: {DROP_FOLDER}", file=sys.stderr)
        sys.exit(1)

    state = load_state()
    already_processed = set(state.get("processed", []))
    errors_log = state.setdefault("errors", [])

    # Find all audio files (not in /processed/ subdir)
    candidates = []
    seen_keys = set()
    for ext in SUPPORTED_EXTENSIONS:
        for pattern in (f"*{ext}", f"*{ext.upper()}"):
            for f in DROP_FOLDER.glob(pattern):
                # Skip files inside the processed/ subdirectory
                if "processed" in f.parts:
                    continue
                key = str(f.resolve())
                if key in seen_keys:
                    continue
                seen_keys.add(key)
                if key not in already_processed:
                    candidates.append(f)

    # Sort by modification time (oldest first)
    candidates = sorted(candidates, key=lambda f: f.stat().st_mtime)

    if not candidates:
        print(f"[voice-notes] No new audio files found in {DROP_FOLDER}", flush=True)
        state["last_run"] = datetime.now().isoformat()
        if not dry_run:
            save_state(state)
        return

    print(f"[voice-notes] Found {len(candidates)} file(s) to process:", flush=True)
    for f in candidates:
        print(f"  - {f.name}", flush=True)

    if dry_run:
        print("[voice-notes] Dry run — no files will be processed.", flush=True)
        return

    succeeded = []
    failed    = []

    for audio_file in candidates:
        print(f"\n[voice-notes] ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", flush=True)
        print(f"[voice-notes] Processing: {audio_file.name}", flush=True)
        try:
            result = subprocess.run(
                [sys.executable, str(PROCESS_SCRIPT), str(audio_file)],
                env=os.environ.copy(),
                capture_output=False,  # Stream output to terminal
                check=True,
            )
            succeeded.append(audio_file.name)
            # State is already updated by process-audio.py; reload to stay in sync
            state = load_state()
            errors_log = state.setdefault("errors", [])
        except subprocess.CalledProcessError as e:
            err_msg = f"{audio_file.name}: exit code {e.returncode}"
            print(f"[voice-notes] ❌ Error processing {err_msg}", file=sys.stderr, flush=True)
            failed.append(audio_file.name)
            # Log the error in state but continue
            errors_log.append({
                "file": audio_file.name,
                "error": err_msg,
                "timestamp": datetime.now().isoformat(),
            })
            state["errors"] = errors_log
            save_state(state)
            # Continue to next file
            continue
        except Exception as e:
            err_msg = f"{audio_file.name}: {str(e)}"
            print(f"[voice-notes] ❌ Unexpected error: {err_msg}", file=sys.stderr, flush=True)
            failed.append(audio_file.name)
            errors_log.append({
                "file": audio_file.name,
                "error": err_msg,
                "timestamp": datetime.now().isoformat(),
            })
            state["errors"] = errors_log
            save_state(state)
            continue

    # Final summary
    print(f"\n[voice-notes] ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", flush=True)
    print(f"[voice-notes] Backlog complete.", flush=True)
    print(f"  ✅ Processed: {len(succeeded)}", flush=True)
    if failed:
        print(f"  ❌ Errors:    {len(failed)}", flush=True)
        for name in failed:
            print(f"     - {name}", flush=True)

    # Update last_run in final state
    state = load_state()
    state["last_run"] = datetime.now().isoformat()
    save_state(state)


if __name__ == "__main__":
    main()
