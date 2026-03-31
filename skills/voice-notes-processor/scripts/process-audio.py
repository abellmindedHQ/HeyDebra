#!/usr/bin/env python3
"""
process-audio.py — AssemblyAI voice note processor for SecondBrain

Usage:
    python3 process-audio.py <audio_file_path>

Environment:
    ASSEMBLYAI_API_KEY — required

Outputs:
    - Obsidian note in ~/SecondBrain/Meetings/
    - Action items appended to ~/SecondBrain/GTD/inbox.md
    - State updated in ~/.openclaw/workspace/memory/voice-notes-state.json
    - Audio moved to ~/SecondBrain/Imports/voice-notes/processed/
"""

import sys
import os
import json
import shutil
import subprocess
import time
from datetime import datetime
from pathlib import Path

# ── Auto-install requests if missing ─────────────────────────────────────────
try:
    import requests
except ImportError:
    print("[voice-notes] Installing requests...", flush=True)
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "-q"])
    import requests

# ── Paths ─────────────────────────────────────────────────────────────────────
MEETINGS_DIR   = Path.home() / "SecondBrain" / "Meetings"
INBOX_FILE     = Path.home() / "SecondBrain" / "GTD" / "inbox.md"
PROCESSED_DIR  = Path.home() / "SecondBrain" / "Imports" / "voice-notes" / "processed"
STATE_FILE            = Path("/Users/debra/.openclaw/workspace/memory/voice-notes-state.json")
VOICE_PROFILES_DIR    = Path("/Users/debra/.openclaw/workspace/memory/voice-profiles")
UNKNOWN_SPEAKERS_FILE = VOICE_PROFILES_DIR / "unknown-speakers.json"

for d in [MEETINGS_DIR, INBOX_FILE.parent, PROCESSED_DIR, STATE_FILE.parent, VOICE_PROFILES_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ── Helpers ───────────────────────────────────────────────────────────────────

def load_state() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except Exception:
            pass
    return {"processed": [], "last_run": None}


def save_state(state: dict):
    STATE_FILE.write_text(json.dumps(state, indent=2, default=str))


def format_duration(seconds) -> str:
    if seconds is None:
        return "unknown"
    seconds = int(float(seconds))
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    if h:
        return f"{h}h {m}m {s}s"
    elif m:
        return f"{m}m {s}s"
    return f"{s}s"


def speaker_label(speaker) -> str:
    """Convert AssemblyAI speaker token (A, B, ...) to friendly label."""
    if not speaker:
        return "Unknown"
    return f"Speaker {speaker}"


def sentiment_emoji(label) -> str:
    mapping = {"POSITIVE": "😊", "NEGATIVE": "😟", "NEUTRAL": "😐"}
    return mapping.get(str(label).upper() if label else "", "")


def safe_text(val) -> str:
    return str(val) if val is not None else ""


# ── AssemblyAI REST API ───────────────────────────────────────────────────────

ASSEMBLYAI_BASE = "https://api.assemblyai.com/v2"


def transcribe(audio_path: Path) -> dict:
    api_key = os.environ.get("ASSEMBLYAI_API_KEY")
    if not api_key:
        print("[voice-notes] ERROR: ASSEMBLYAI_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    headers = {"authorization": api_key}

    # Step 1: Upload the audio file
    print(f"[voice-notes] Uploading: {audio_path.name}", flush=True)
    with open(audio_path, "rb") as f:
        upload_resp = requests.post(
            f"{ASSEMBLYAI_BASE}/upload",
            headers=headers,
            data=f,
        )
    upload_resp.raise_for_status()
    upload_url = upload_resp.json()["upload_url"]
    print(f"[voice-notes] Upload complete. Submitting transcription...", flush=True)

    # Step 2: Submit transcription request
    transcript_req = {
        "audio_url": upload_url,
        "speech_models": ["universal-3-pro"],
        "speaker_labels": True,
        "auto_chapters": True,
        "entity_detection": True,
        "sentiment_analysis": True,
        "auto_highlights": True,
        "punctuate": True,
        "format_text": True,
    }

    submit_resp = requests.post(
        f"{ASSEMBLYAI_BASE}/transcript",
        headers={**headers, "content-type": "application/json"},
        json=transcript_req,
    )
    submit_resp.raise_for_status()
    transcript_id = submit_resp.json()["id"]
    print(f"[voice-notes] Transcription queued: {transcript_id}", flush=True)

    # Step 3: Poll until complete
    poll_url = f"{ASSEMBLYAI_BASE}/transcript/{transcript_id}"
    while True:
        poll_resp = requests.get(poll_url, headers=headers)
        poll_resp.raise_for_status()
        data = poll_resp.json()
        status = data.get("status")

        if status == "completed":
            duration = format_duration(data.get("audio_duration"))
            print(f"[voice-notes] Transcription complete. Duration: {duration}", flush=True)
            return data
        elif status == "error":
            print(f"[voice-notes] Transcription failed: {data.get('error')}", file=sys.stderr)
            sys.exit(1)
        else:
            print(f"[voice-notes] Status: {status} — waiting...", flush=True)
            time.sleep(5)



# ── Voice Embedding Extraction ─────────────────────────────────────────────────

def _ms_to_sec(ms) -> float:
    return (ms or 0) / 1000.0


def extract_voice_embeddings(transcript: dict, audio_path: Path, now: datetime) -> dict:
    """
    Extract 256-dim voice embeddings per speaker using resemblyzer.

    Returns dict mapping speaker label -> 8-char fingerprint (sha256 of embedding),
    and appends full embedding entries to unknown-speakers.json.
    Returns {} if resemblyzer is not installed or no utterances present.
    """
    try:
        from resemblyzer import VoiceEncoder, preprocess_wav  # type: ignore
    except ImportError:
        print("[voice-notes] ⚠️  resemblyzer not installed — skipping voice embedding extraction.", flush=True)
        print("[voice-notes]    Install with: pip install resemblyzer", flush=True)
        return {}

    import hashlib
    import tempfile
    import numpy as np  # type: ignore

    utterances = transcript.get("utterances") or []
    if not utterances:
        print("[voice-notes] No utterances available for voice embedding.", flush=True)
        return {}

    # Group utterances by speaker code
    speaker_utterances: dict = {}
    for u in utterances:
        sp = u.get("speaker")
        if sp:
            speaker_utterances.setdefault(sp, []).append(u)

    if not speaker_utterances:
        return {}

    # Load existing unknown-speakers list
    unknown_speakers = []
    if UNKNOWN_SPEAKERS_FILE.exists():
        try:
            unknown_speakers = json.loads(UNKNOWN_SPEAKERS_FILE.read_text())
            if not isinstance(unknown_speakers, list):
                unknown_speakers = []
        except Exception:
            unknown_speakers = []

    try:
        encoder = VoiceEncoder()
    except Exception as e:
        print(f"[voice-notes] ⚠️  Failed to initialise VoiceEncoder: {e}", flush=True)
        return {}

    fingerprints: dict = {}
    timestamp_str = now.strftime("%Y-%m-%dT%H:%M:%S")
    MIN_DURATION_MS = 10_000  # target >= 10 s per speaker

    for speaker_code, utts in speaker_utterances.items():
        sp_label = speaker_label(speaker_code)
        print(f"[voice-notes] Extracting voice embedding for {sp_label}...", flush=True)

        # Sort by start time and accumulate until we have >= 10 s
        utts_sorted = sorted(utts, key=lambda u: u.get("start", 0))
        selected = []
        total_ms = 0
        for u in utts_sorted:
            dur = (u.get("end") or 0) - (u.get("start") or 0)
            if dur <= 0:
                continue
            selected.append(u)
            total_ms += dur
            if total_ms >= MIN_DURATION_MS:
                break

        if not selected:
            print(f"[voice-notes] No valid utterances for {sp_label}. Skipping.", flush=True)
            continue

        duration_secs = total_ms / 1000.0

        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                tmp_path = Path(tmpdir)

                # Extract each utterance segment to a separate WAV
                seg_files = []
                for i, u in enumerate(selected):
                    start_s = _ms_to_sec(u.get("start", 0))
                    dur_s   = _ms_to_sec((u.get("end") or 0) - (u.get("start") or 0))
                    if dur_s <= 0:
                        continue
                    seg_path = tmp_path / f"seg_{i}.wav"
                    result = subprocess.run(
                        [
                            "ffmpeg", "-y",
                            "-i",  str(audio_path),
                            "-ss", f"{start_s:.3f}",
                            "-t",  f"{dur_s:.3f}",
                            "-ar", "16000",
                            "-ac", "1",
                            str(seg_path),
                        ],
                        capture_output=True,
                    )
                    if result.returncode == 0 and seg_path.exists() and seg_path.stat().st_size > 0:
                        seg_files.append(seg_path)

                if not seg_files:
                    print(f"[voice-notes] ⚠️  No audio segments extracted for {sp_label}.", flush=True)
                    continue

                if len(seg_files) == 1:
                    final_wav_path = seg_files[0]
                else:
                    # Concatenate segments with ffmpeg concat demuxer
                    concat_list = tmp_path / "concat.txt"
                    concat_list.write_text(
                        "\n".join(f"file '{str(p)}'" for p in seg_files)
                    )
                    concat_out = tmp_path / "combined.wav"
                    r = subprocess.run(
                        [
                            "ffmpeg", "-y",
                            "-f",    "concat",
                            "-safe", "0",
                            "-i",    str(concat_list),
                            "-ar",   "16000",
                            "-ac",   "1",
                            str(concat_out),
                        ],
                        capture_output=True,
                    )
                    if r.returncode != 0 or not concat_out.exists():
                        print(f"[voice-notes] ⚠️  ffmpeg concat failed for {sp_label}.", flush=True)
                        continue
                    final_wav_path = concat_out

                # Generate embedding
                wav = preprocess_wav(str(final_wav_path))
                embedding = encoder.embed_utterance(wav)  # shape (256,)

                # Compute short fingerprint (first 8 hex chars of sha256)
                emb_bytes   = embedding.astype("float32").tobytes()
                fingerprint = hashlib.sha256(emb_bytes).hexdigest()[:8]
                fingerprints[sp_label] = fingerprint

                # Build entry for unknown-speakers.json
                entry = {
                    "embedding":     embedding.tolist(),
                    "source_file":   audio_path.name,
                    "speaker_label": sp_label,
                    "timestamp":     timestamp_str,
                    "duration_secs": round(duration_secs, 2),
                    "fingerprint":   fingerprint,
                }
                unknown_speakers.append(entry)
                print(
                    f"[voice-notes] ✅ {sp_label}: fingerprint={fingerprint}, "
                    f"duration={duration_secs:.1f}s ({len(selected)} segments)",
                    flush=True,
                )

        except Exception as e:
            print(f"[voice-notes] ⚠️  Embedding error for {sp_label}: {e}", flush=True)

    # Persist unknown-speakers.json
    if fingerprints:
        UNKNOWN_SPEAKERS_FILE.write_text(json.dumps(unknown_speakers, indent=2))
        print(f"[voice-notes] Saved {len(fingerprints)} embedding(s) → {UNKNOWN_SPEAKERS_FILE}", flush=True)

    return fingerprints

# ── Obsidian Note Builder ─────────────────────────────────────────────────────

def extract_real_date(audio_path: Path) -> tuple:
    """Extract real recording date from audio metadata via ffprobe."""
    import subprocess as _sp
    try:
        result = _sp.run(
            ["ffprobe", "-v", "quiet", "-show_entries", "format_tags=creation_time",
             "-of", "csv=p=0", str(audio_path)],
            capture_output=True, text=True, timeout=10
        )
        meta_date = result.stdout.strip()[:10]
        if meta_date and len(meta_date) == 10:
            return meta_date, meta_date.replace("-", "")
    except Exception:
        pass
    return None, None


def clean_title(audio_path: Path) -> str:
    """Extract a human-readable title from the filename."""
    stem = audio_path.stem
    # Remove leading number + unknown-date prefix
    import re
    stem = re.sub(r'^\d+_unknown-date_', '', stem)
    stem = re.sub(r'^\d+_\d{4}-\d{2}-\d{2}_', '', stem)
    # Remove trailing _N_recording or _N_New Recording etc
    stem = re.sub(r'_\d+_(recording|New Recording|New-Recording)$', '', stem, flags=re.IGNORECASE)
    # Clean up separators
    stem = stem.replace('_', ' ').replace('-', ' ').strip()
    if not stem or stem.lower() in ('new recording', 'recording', 'needs meeting name', 'meeting name'):
        return "Voice Note"
    return stem.title()


def build_obsidian_note(transcript: dict, audio_path: Path, now: datetime,
                        speaker_fingerprints: dict = None) -> str:
    # Try to get real date from audio metadata
    real_date, _ = extract_real_date(audio_path)
    date_str   = real_date if real_date else now.strftime("%Y-%m-%d")
    time_str   = now.strftime("%H:%M")
    title      = clean_title(audio_path)
    duration   = format_duration(transcript.get("audio_duration"))

    utterances  = transcript.get("utterances") or []
    chapters    = transcript.get("chapters") or []
    entities    = transcript.get("entities") or []
    sentiments  = transcript.get("sentiment_analysis_results") or []
    highlights_data = transcript.get("auto_highlights_result") or {}
    highlights  = highlights_data.get("results") or []

    # Gather unique speaker labels
    speakers_set = set()
    for u in utterances:
        sp = u.get("speaker")
        if sp:
            speakers_set.add(speaker_label(sp))
    speakers_list = sorted(speakers_set) if speakers_set else ["Unknown"]
    speakers_yaml = "[" + ", ".join(f'"{s}"' for s in speakers_list) + "]"

    # Overall sentiment tally
    sentiment_counts = {"POSITIVE": 0, "NEGATIVE": 0, "NEUTRAL": 0}
    for s in sentiments:
        label = safe_text(s.get("sentiment")).upper()
        if label in sentiment_counts:
            sentiment_counts[label] += 1
    total_sent = sum(sentiment_counts.values()) or 1
    dominant_sentiment = max(sentiment_counts, key=sentiment_counts.get)

    # ── YAML Frontmatter ──────────────────────────────────────────────────────
    lines = [
        "---",
        f'title: "{title}"',
        f"date: {date_str}",
        f"time: {time_str}",
        f"source_file: {audio_path.name}",
        f"duration: {duration}",
        f"speakers: {speakers_yaml}",
        f"speaker_count: {len(speakers_list)}",
        f"dominant_sentiment: {dominant_sentiment.lower()}",
        f"tags: [voice-note, meeting, transcription]",
    ]

    # Add speaker fingerprints if available
    if speaker_fingerprints:
        fp_entries = ", ".join(
            f'"{sp}": "{fp}"'
            for sp, fp in sorted(speaker_fingerprints.items())
        )
        lines.append(f"speaker_fingerprints: {{{fp_entries}}}")

    lines += [
        "---",
        "",
        f"# {title}",
        "",
        f"> 📅 {date_str} {time_str}  |  ⏱️ {duration}  |  🎙️ {', '.join(speakers_list)}",
        "",
    ]

    # ── Chapters / Sections ───────────────────────────────────────────────────
    if chapters:
        lines += ["## 📑 Chapters", ""]
        for i, ch in enumerate(chapters, 1):
            start_ms = ch.get("start") or 0
            start_min = int(start_ms / 1000 / 60)
            start_sec = int((start_ms / 1000) % 60)
            headline = ch.get("headline") or ""
            summary  = ch.get("summary") or ""
            lines.append(f"### {i}. {headline}")
            lines.append(f"*{start_min:02d}:{start_sec:02d}* — {summary}")
            lines.append("")

    # ── Full Transcript ───────────────────────────────────────────────────────
    lines += ["## 📝 Transcript", ""]

    if utterances:
        current_speaker = None
        for u in utterances:
            label = speaker_label(u.get("speaker"))
            start_ms = u.get("start") or 0
            start_min = int(start_ms / 1000 / 60)
            start_sec = int((start_ms / 1000) % 60)
            if label != current_speaker:
                if current_speaker is not None:
                    lines.append("")
                lines.append(f"**{label}** _{start_min:02d}:{start_sec:02d}_")
                current_speaker = label
            lines.append(f"> {u.get('text', '')}")
        lines.append("")
    else:
        # Fallback: no speaker diarization
        lines.append(transcript.get("text") or "*(no transcript)*")
        lines.append("")

    # ── Sentiment Analysis ────────────────────────────────────────────────────
    if sentiments:
        lines += ["## 😊 Sentiment", ""]
        pos_pct = round(sentiment_counts["POSITIVE"] / total_sent * 100)
        neu_pct = round(sentiment_counts["NEUTRAL"]  / total_sent * 100)
        neg_pct = round(sentiment_counts["NEGATIVE"] / total_sent * 100)
        lines.append(f"- 😊 Positive: {pos_pct}%")
        lines.append(f"- 😐 Neutral: {neu_pct}%")
        lines.append(f"- 😟 Negative: {neg_pct}%")
        lines.append("")

        # Notable negative/positive segments
        notable = [
            s for s in sentiments
            if safe_text(s.get("sentiment")).upper() in ("POSITIVE", "NEGATIVE")
        ][:10]
        if notable:
            lines.append("**Notable moments:**")
            lines.append("")
            for seg in notable:
                emoji = sentiment_emoji(seg.get("sentiment"))
                lines.append(f"- {emoji} *\"{seg.get('text', '')}\"*")
            lines.append("")

    # ── Key Highlights / Action Items from AssemblyAI ─────────────────────────
    if highlights:
        lines += ["## ✨ Key Highlights", ""]
        for h in highlights[:15]:
            text  = h.get("text", "")
            count = h.get("count", 0)
            rank  = h.get("rank", 0.0)
            lines.append(f"- **{text}** (mentioned {count}x, rank {rank:.2f})")
        lines.append("")

    # ── Entities ──────────────────────────────────────────────────────────────
    if entities:
        lines += ["## 🏷️ Entities", ""]

        entity_groups: dict = {}
        for e in entities:
            etype = e.get("entity_type") or "unknown"
            text  = e.get("text") or ""
            entity_groups.setdefault(etype, [])
            if text and text not in entity_groups[etype]:
                entity_groups[etype].append(text)

        type_icons = {
            "person_name":       "👤",
            "organization":      "🏢",
            "location":          "📍",
            "date":              "📅",
            "time":              "⏰",
            "money_amount":      "💰",
            "email_address":     "📧",
            "phone_number":      "📞",
            "url":               "🔗",
            "product_name":      "📦",
            "event":             "🎉",
            "medical_condition": "🏥",
        }

        for etype, items in sorted(entity_groups.items()):
            if not items:
                continue
            icon = type_icons.get(etype, "🔹")
            label_display = etype.replace("_", " ").title()
            lines.append(f"**{icon} {label_display}:** {', '.join(items)}")
        lines.append("")

    # ── People for SecondBrain Entity Cards ───────────────────────────────────
    people = []
    for e in entities:
        if e.get("entity_type") == "person_name":
            name = e.get("text") or ""
            if name and name not in people:
                people.append(name)

    if people:
        lines += ["## 👥 People Mentioned", ""]
        for p in people:
            lines.append(f"- [[{p}]]")
        lines.append("")

    lines.append("---")
    lines.append(f"*Processed by voice-notes-processor on {date_str} {time_str}*")
    lines.append(f"*Source: `{audio_path.name}`*")

    return "\n".join(lines)


# ── GTD Inbox Appender ────────────────────────────────────────────────────────

def extract_action_items(transcript: dict, audio_path: Path, now: datetime) -> list:
    """Pull action items from AssemblyAI auto_highlights + heuristics."""
    captured = now.strftime("%Y-%m-%d %H:%M")
    source_tag = f"voice-note:{audio_path.name}"
    items = []

    utterances = transcript.get("utterances") or []
    highlights_data = transcript.get("auto_highlights_result") or {}
    highlights = highlights_data.get("results") or []

    action_keywords = [
        "need to", "should", "will", "going to", "have to", "must",
        "action", "todo", "follow up", "follow-up", "remind", "schedule",
        "call", "email", "send", "review", "check", "make sure",
        "don't forget", "remember", "deadline", "by ", "asap",
    ]

    for h in highlights:
        text = h.get("text") or ""
        text_lower = text.lower()
        if any(kw in text_lower for kw in action_keywords):
            item = (
                f"- [ ] {text} — "
                f"assigned to: Alex, due: not specified, "
                f"assigned by: voice note, priority: normal, "
                f"source: {source_tag}, captured: {captured}"
            )
            items.append(item)

    # From transcript utterances — look for imperative sentences (fallback)
    if utterances and not items:
        for u in utterances:
            text = u.get("text") or ""
            text_lower = text.lower()
            if any(kw in text_lower for kw in [
                "action item", "todo", "follow up",
                "i'll ", "i will ", "we need to", "you need to"
            ]):
                clean = text.strip().rstrip(".")
                sp = u.get("speaker")
                item = (
                    f"- [ ] {clean} — "
                    f"assigned to: Alex, due: not specified, "
                    f"assigned by: voice note ({speaker_label(sp)}), priority: normal, "
                    f"source: {source_tag}, captured: {captured}"
                )
                items.append(item)

    return items


def append_to_inbox(items: list, audio_path: Path, now: datetime):
    if not items:
        print("[voice-notes] No action items detected.", flush=True)
        return

    if not INBOX_FILE.exists():
        INBOX_FILE.write_text("# GTD Inbox\n\nItems captured by Debra's Capture Agent. Triage via GSD Agent.\n\n---\n\n")

    existing = INBOX_FILE.read_text()

    new_items = []
    for item in items:
        # Dedup: check if core phrase already present
        core = item.split(" — ")[0].replace("- [ ] ", "").lower().strip()
        if core not in existing.lower():
            new_items.append(item)

    if not new_items:
        print("[voice-notes] All action items already in inbox (dedup).", flush=True)
        return

    with INBOX_FILE.open("a") as f:
        f.write(f"\n<!-- voice-note: {audio_path.name} @ {now.strftime('%Y-%m-%d %H:%M')} -->\n")
        for item in new_items:
            f.write(item + "\n")

    print(f"[voice-notes] Appended {len(new_items)} action item(s) to inbox.", flush=True)


# ── Main ──────────────────────────────────────────────────────────────────────

def process_file(audio_path: Path):
    audio_path = audio_path.resolve()
    now = datetime.now()

    print(f"[voice-notes] Processing: {audio_path}", flush=True)

    # Load state, check for duplicates
    state = load_state()
    if str(audio_path) in state.get("processed", []):
        print(f"[voice-notes] Already processed: {audio_path.name}. Skipping.", flush=True)
        return

    # Transcribe via REST API
    transcript = transcribe(audio_path)

    # Extract voice embeddings (optional — skipped if resemblyzer not installed)
    speaker_fingerprints = extract_voice_embeddings(transcript, audio_path, now)

    # Build Obsidian note
    note_content = build_obsidian_note(transcript, audio_path, now,
                                       speaker_fingerprints=speaker_fingerprints)
    real_date, _  = extract_real_date(audio_path)
    date_str      = real_date if real_date else now.strftime("%Y-%m-%d")
    clean_name    = clean_title(audio_path).lower().replace(" ", "-").replace("/", "-")
    if not clean_name or clean_name == "voice-note":
        clean_name = audio_path.stem.replace(" ", "-").lower()[:60]
    note_filename = f"{date_str}-{clean_name}.md"
    note_path     = MEETINGS_DIR / note_filename
    note_path.write_text(note_content, encoding="utf-8")
    print(f"[voice-notes] Saved note: {note_path}", flush=True)

    # Extract and append action items
    action_items = extract_action_items(transcript, audio_path, now)
    append_to_inbox(action_items, audio_path, now)

    # Move audio to processed/
    dest = PROCESSED_DIR / audio_path.name
    if dest.exists():
        stem   = audio_path.stem
        suffix = audio_path.suffix
        dest   = PROCESSED_DIR / f"{stem}_{now.strftime('%Y%m%d%H%M%S')}{suffix}"
    shutil.move(str(audio_path), str(dest))
    print(f"[voice-notes] Moved audio to: {dest}", flush=True)

    # Update state
    state.setdefault("processed", []).append(str(audio_path))
    state["last_run"] = now.isoformat()
    state.setdefault("notes_created", []).append(str(note_path))
    save_state(state)

    result = {
        "file": audio_path.name,
        "note": str(note_path),
        "action_items": len(action_items),
        "duration": format_duration(transcript.get("audio_duration")),
    }
    print(f"[voice-notes] ✅ Done: {audio_path.name}", flush=True)
    return result


def main():
    if len(sys.argv) < 2:
        print("Usage: process-audio.py <audio_file>", file=sys.stderr)
        sys.exit(1)

    audio_path = Path(sys.argv[1])
    if not audio_path.exists():
        print(f"[voice-notes] File not found: {audio_path}", file=sys.stderr)
        sys.exit(1)

    result = process_file(audio_path)
    if result:
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
