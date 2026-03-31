#!/usr/bin/env python3
"""
watch-folder.py — Continuously watch the voice-notes drop folder and process new files.

Usage:
    python3 watch-folder.py [--poll-interval SECONDS]

Environment:
    ASSEMBLYAI_API_KEY — required

Watches ~/SecondBrain/Imports/voice-notes/ for new audio files.
Uses polling (no external dependencies). Processes files as they appear.
Designed to run as a background daemon or via launchd/cron.

Default poll interval: 30 seconds
"""

import sys
import os
import json
import time
import subprocess
from pathlib import Path
from datetime import datetime

# ── Config ────────────────────────────────────────────────────────────────────
DROP_FOLDER          = Path.home() / "SecondBrain" / "Imports" / "voice-notes"
STATE_FILE           = Path("/Users/debra/.openclaw/workspace/memory/voice-notes-state.json")
SUPPORTED_EXTENSIONS = {".m4a", ".mp3", ".wav", ".ogg", ".webm", ".mp4"}
DEFAULT_POLL_SECONDS = 30
STABILITY_WAIT       = 3  # Seconds to wait after detecting a file before processing (ensure write is complete)

SCRIPT_DIR     = Path(__file__).parent
PROCESS_SCRIPT = SCRIPT_DIR / "process-audio.py"


def load_state() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except Exception:
            pass
    return {"processed": [], "last_run": None, "watching_since": None}


def get_known_files() -> set[str]:
    """Return set of already-processed file paths."""
    state = load_state()
    return set(state.get("processed", []))


def scan_for_files() -> list[Path]:
    """Find unprocessed audio files in the drop folder (not in /processed/ subdir)."""
    if not DROP_FOLDER.exists():
        return []

    candidates = []
    for f in DROP_FOLDER.iterdir():
        if f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS:
            candidates.append(f)

    return sorted(candidates, key=lambda f: f.stat().st_mtime)


def is_file_stable(path: Path, wait: int = STABILITY_WAIT) -> bool:
    """Check if a file has stopped growing (i.e., fully written)."""
    try:
        size1 = path.stat().st_size
        time.sleep(wait)
        size2 = path.stat().st_size
        return size1 == size2 and size2 > 0
    except Exception:
        return False


def process_file(audio_file: Path) -> bool:
    """Run process-audio.py on a single file. Returns True on success."""
    print(f"\n[watcher] 🎙️  New file detected: {audio_file.name}", flush=True)

    if not is_file_stable(audio_file):
        print(f"[watcher] File not stable yet, skipping: {audio_file.name}", flush=True)
        return False

    try:
        result = subprocess.run(
            [sys.executable, str(PROCESS_SCRIPT), str(audio_file)],
            env=os.environ.copy(),
            check=True,
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"[watcher] ❌ Error processing {audio_file.name}: exit code {e.returncode}", file=sys.stderr)
        return False


def main():
    # Parse args
    poll_interval = DEFAULT_POLL_SECONDS
    args = sys.argv[1:]
    if "--poll-interval" in args:
        idx = args.index("--poll-interval")
        try:
            poll_interval = int(args[idx + 1])
        except (IndexError, ValueError):
            pass

    if not os.environ.get("ASSEMBLYAI_API_KEY"):
        print("[watcher] ERROR: ASSEMBLYAI_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    DROP_FOLDER.mkdir(parents=True, exist_ok=True)

    # Update state with watcher start time
    state = load_state()
    state["watching_since"] = datetime.now().isoformat()
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2, default=str))

    print(f"[watcher] 👁️  Watching: {DROP_FOLDER}", flush=True)
    print(f"[watcher] Poll interval: {poll_interval}s", flush=True)
    print(f"[watcher] Press Ctrl+C to stop.", flush=True)

    processed_this_session: set[str] = set()

    while True:
        try:
            known_files = get_known_files()
            candidates  = scan_for_files()

            for audio_file in candidates:
                fpath = str(audio_file.resolve())
                if fpath in known_files or fpath in processed_this_session:
                    continue

                success = process_file(audio_file)
                if success:
                    processed_this_session.add(fpath)

            time.sleep(poll_interval)

        except KeyboardInterrupt:
            print("\n[watcher] Stopped by user.", flush=True)
            break
        except Exception as e:
            print(f"[watcher] Unexpected error: {e}", file=sys.stderr)
            time.sleep(poll_interval)


if __name__ == "__main__":
    main()
