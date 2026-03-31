#!/usr/bin/env python3
"""Import Otter.ai transcript .txt files into SecondBrain Obsidian vault."""

import os
import re
import json
import hashlib
from pathlib import Path
from datetime import datetime

SOURCE_DIR = Path.home() / "SecondBrain/Imports/otter-export/extracted"
DEST_DIR = Path.home() / "SecondBrain/Meetings"
STATE_FILE = Path.home() / ".openclaw/workspace/memory/otter-import-state.json"

def load_state():
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {"imported": {}, "errors": [], "last_run": None}

def save_state(state):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    state["last_run"] = datetime.now().isoformat()
    STATE_FILE.write_text(json.dumps(state, indent=2))

def slugify(text):
    """Convert text to a filesystem-safe slug."""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    text = re.sub(r'-+', '-', text)
    return text[:80].strip('-')

def parse_transcript(content):
    """Parse Otter transcript format: 'Speaker  HH:MM\\nText'"""
    lines = content.strip().split('\n')
    segments = []
    speakers = set()
    current_speaker = None
    current_time = None
    current_text = []

    # Pattern: "Speaker Name  MM:SS" or "Speaker Name  HH:MM:SS"
    speaker_pattern = re.compile(r'^(.+?)\s{2,}(\d{1,2}:\d{2}(?::\d{2})?)\s*$')

    for line in lines:
        match = speaker_pattern.match(line)
        if match:
            # Save previous segment
            if current_speaker and current_text:
                text = ' '.join(current_text).strip()
                if text:
                    segments.append({
                        'speaker': current_speaker,
                        'time': current_time,
                        'text': text
                    })
                    speakers.add(current_speaker)
            current_speaker = match.group(1).strip()
            current_time = match.group(2).strip()
            current_text = []
        else:
            if line.strip():
                current_text.append(line.strip())

    # Don't forget last segment
    if current_speaker and current_text:
        text = ' '.join(current_text).strip()
        if text:
            segments.append({
                'speaker': current_speaker,
                'time': current_time,
                'text': text
            })
            speakers.add(current_speaker)

    return segments, sorted(speakers)

def extract_title(filename):
    """Clean up filename to use as title."""
    title = Path(filename).stem
    # Remove leading # symbols
    title = re.sub(r'^#+\s*', '', title)
    return title.strip()

def format_obsidian_note(title, segments, speakers, source_file):
    """Format as an Obsidian meeting note with YAML frontmatter."""
    # Build frontmatter
    frontmatter = {
        'title': title,
        'date': '2026-03-31',  # import date as fallback
        'source_file': source_file,
        'source': 'otter',
        'speakers': speakers,
        'speaker_count': len(speakers),
        'tags': ['otter', 'transcription', 'meeting'],
    }

    lines = ['---']
    lines.append(f'title: "{frontmatter["title"]}"')
    lines.append(f'date: {frontmatter["date"]}')
    lines.append(f'source_file: "{frontmatter["source_file"]}"')
    lines.append(f'source: otter')
    lines.append(f'speakers: {json.dumps(frontmatter["speakers"])}')
    lines.append(f'speaker_count: {frontmatter["speaker_count"]}')
    lines.append(f'tags: [otter, transcription, meeting]')
    lines.append('---')
    lines.append('')
    lines.append(f'# {title}')
    lines.append('')
    lines.append(f'> 📅 Imported {frontmatter["date"]}  |  🎙️ {", ".join(speakers)}')
    lines.append('')

    # Transcript section
    lines.append('## Transcript')
    lines.append('')

    for seg in segments:
        lines.append(f'**{seg["speaker"]}** *{seg["time"]}*')
        lines.append(f'{seg["text"]}')
        lines.append('')

    return '\n'.join(lines)

def get_existing_source_files():
    """Scan existing meeting notes for source_file references to avoid duplicates."""
    existing = set()
    for f in DEST_DIR.glob('*.md'):
        try:
            content = f.read_text(errors='replace')
            # Check frontmatter for source_file
            m = re.search(r'source_file:\s*["\']?(.+?)["\']?\s*$', content, re.MULTILINE)
            if m:
                existing.add(m.group(1).strip())
        except Exception:
            pass
    return existing

def main():
    state = load_state()
    DEST_DIR.mkdir(parents=True, exist_ok=True)

    # Get all txt files
    txt_files = sorted(SOURCE_DIR.glob('*.txt'))
    print(f"Found {len(txt_files)} transcript files")

    # Get existing source files for dedup
    existing_sources = get_existing_source_files()
    print(f"Found {len(existing_sources)} existing meeting notes with source refs")

    imported_count = 0
    skipped_dedup = 0
    skipped_already = 0
    errors = []

    for txt_file in txt_files:
        filename = txt_file.name
        file_hash = hashlib.md5(filename.encode()).hexdigest()[:12]

        # Skip if already imported in previous run
        if filename in state["imported"]:
            skipped_already += 1
            continue

        # Skip if source file already referenced in existing notes
        if filename in existing_sources:
            state["imported"][filename] = {"status": "dedup_existing", "date": datetime.now().isoformat()}
            skipped_dedup += 1
            continue

        try:
            content = txt_file.read_text(errors='replace')
            if not content.strip():
                state["imported"][filename] = {"status": "empty", "date": datetime.now().isoformat()}
                errors.append(f"Empty file: {filename}")
                continue

            segments, speakers = parse_transcript(content)
            title = extract_title(filename)

            if not segments:
                # File has content but no parseable speaker segments - treat as plain text
                slug = slugify(title)
                out_name = f"otter-{slug}.md"
                out_path = DEST_DIR / out_name

                # Avoid collision
                counter = 1
                while out_path.exists():
                    out_name = f"otter-{slug}-{counter}.md"
                    out_path = DEST_DIR / out_name
                    counter += 1

                # Build a simple note
                note_lines = [
                    '---',
                    f'title: "{title}"',
                    f'date: 2026-03-31',
                    f'source_file: "{filename}"',
                    'source: otter',
                    'tags: [otter, transcription]',
                    '---',
                    '',
                    f'# {title}',
                    '',
                    content.strip(),
                    ''
                ]
                out_path.write_text('\n'.join(note_lines))
                state["imported"][filename] = {
                    "status": "imported_plain",
                    "output": out_name,
                    "date": datetime.now().isoformat()
                }
                imported_count += 1
                continue

            note = format_obsidian_note(title, segments, speakers, filename)

            slug = slugify(title)
            out_name = f"otter-{slug}.md"
            out_path = DEST_DIR / out_name

            # Avoid filename collision
            counter = 1
            while out_path.exists():
                out_name = f"otter-{slug}-{counter}.md"
                out_path = DEST_DIR / out_name
                counter += 1

            out_path.write_text(note)
            state["imported"][filename] = {
                "status": "imported",
                "output": out_name,
                "speakers": speakers,
                "segments": len(segments),
                "date": datetime.now().isoformat()
            }
            imported_count += 1

        except Exception as e:
            error_msg = f"{filename}: {str(e)}"
            errors.append(error_msg)
            state["imported"][filename] = {"status": "error", "error": str(e), "date": datetime.now().isoformat()}

    state["errors"] = errors
    save_state(state)

    print(f"\n=== Import Complete ===")
    print(f"Imported: {imported_count}")
    print(f"Skipped (already imported): {skipped_already}")
    print(f"Skipped (dedup existing): {skipped_dedup}")
    print(f"Errors: {len(errors)}")
    if errors:
        print("\nErrors:")
        for e in errors:
            print(f"  - {e}")

if __name__ == "__main__":
    main()
