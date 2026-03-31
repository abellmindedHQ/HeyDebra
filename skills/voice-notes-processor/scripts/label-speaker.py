#!/usr/bin/env python3
"""
label-speaker.py — Assign a real name to an unknown voice profile entry.

Usage:
    python3 label-speaker.py --profile unknown-speakers.json --index N --name "Jay Eckles"
    python3 label-speaker.py --profile unknown-speakers.json --index N --name "Jay Eckles" --contact "+19014884890"

Arguments:
    --profile   Path to unknown-speakers.json (default: voice-profiles/unknown-speakers.json)
    --index     0-based index of the entry to label
    --name      Full name to assign (e.g. "Jay Eckles")
    --contact   Optional phone number or email for the contact
    --list      List all pending unknown-speaker entries instead of labeling

The entry is moved from unknown-speakers.json into a named file like:
    voice-profiles/jay-eckles.json

If jay-eckles.json already exists, the new entry is appended to it (for
multi-recording averaging — the most recent entry is considered canonical).
"""

import argparse
import json
import re
import sys
from pathlib import Path

VOICE_PROFILES_DIR    = Path("/Users/debra/.openclaw/workspace/memory/voice-profiles")
UNKNOWN_SPEAKERS_FILE = VOICE_PROFILES_DIR / "unknown-speakers.json"


def slugify(name: str) -> str:
    """Convert 'Jay Eckles' → 'jay-eckles'."""
    s = name.lower().strip()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[\s_]+", "-", s)
    s = re.sub(r"-+", "-", s)
    return s.strip("-")


def load_json(path: Path) -> list:
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text())
        return data if isinstance(data, list) else []
    except Exception as e:
        print(f"[label-speaker] ERROR reading {path}: {e}", file=sys.stderr)
        return []


def save_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))


def list_unknowns(profile_path: Path):
    entries = load_json(profile_path)
    if not entries:
        print("[label-speaker] No unknown-speaker entries found.")
        return

    print(f"[label-speaker] {len(entries)} unknown-speaker entry/entries in {profile_path}:\n")
    for i, e in enumerate(entries):
        fp       = e.get("fingerprint", "?")
        src      = e.get("source_file", "?")
        sp_label = e.get("speaker_label", "?")
        dur      = e.get("duration_secs", 0)
        ts       = e.get("timestamp", "?")
        emb_dim  = len(e.get("embedding", []))
        print(
            f"  [{i}]  {sp_label}  |  fingerprint: {fp}  |  duration: {dur:.1f}s  |  "
            f"dim: {emb_dim}  |  file: {src}  |  ts: {ts}"
        )


def label_speaker(profile_path: Path, index: int, name: str, contact: str | None):
    entries = load_json(profile_path)

    if not entries:
        print(f"[label-speaker] ERROR: {profile_path} is empty or missing.", file=sys.stderr)
        sys.exit(1)

    if index < 0 or index >= len(entries):
        print(
            f"[label-speaker] ERROR: index {index} out of range (0–{len(entries) - 1}).",
            file=sys.stderr,
        )
        sys.exit(1)

    entry = entries.pop(index)

    # Annotate with name/contact
    entry["name"]    = name
    entry["labeled"] = True
    if contact:
        entry["contact"] = contact

    # Determine target file
    slug        = slugify(name)
    target_path = VOICE_PROFILES_DIR / f"{slug}.json"

    # Load existing profile if present and append
    existing = load_json(target_path)
    existing.append(entry)

    save_json(target_path, existing)
    print(f"[label-speaker] ✅ Entry moved → {target_path}  (profile now has {len(existing)} recording(s))")

    # Save back the pruned unknown-speakers list
    save_json(profile_path, entries)
    remaining = len(entries)
    print(
        f"[label-speaker] {remaining} unknown-speaker entry/entries remaining in "
        f"{profile_path}"
    )


def main():
    parser = argparse.ArgumentParser(
        description="Label an unknown speaker voice profile entry.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--profile",
        type=Path,
        default=UNKNOWN_SPEAKERS_FILE,
        help="Path to unknown-speakers.json (default: voice-profiles/unknown-speakers.json)",
    )
    parser.add_argument(
        "--index",
        type=int,
        help="0-based index of the entry to label",
    )
    parser.add_argument(
        "--name",
        type=str,
        help='Full name to assign (e.g. "Jay Eckles")',
    )
    parser.add_argument(
        "--contact",
        type=str,
        default=None,
        help="Optional phone number or email for the contact",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all pending unknown-speaker entries",
    )

    args = parser.parse_args()

    # Resolve relative paths against the default voice-profiles dir
    profile_path = Path(args.profile)
    if not profile_path.is_absolute():
        profile_path = VOICE_PROFILES_DIR / profile_path

    if args.list:
        list_unknowns(profile_path)
        return

    # Validate required args for labeling
    if args.index is None:
        parser.error("--index is required when labeling a speaker.")
    if not args.name:
        parser.error("--name is required when labeling a speaker.")

    label_speaker(profile_path, args.index, args.name, args.contact)


if __name__ == "__main__":
    main()
