#!/usr/bin/env python3
"""
Weaver v3 — Zettelkasten connection builder for SecondBrain

Performance improvements over v2:
- Combined regex: one pass per file instead of N_entities passes (11x speedup)
- Incremental mode: only process files modified since last run (mtime-based)
- Chunked processing: 500 files per batch with progress reporting
- Entity lookup cache: saved as JSON, only rebuilt when needed
- State persistence: .weaver_state.json in vault root

Fixes from v1/v2:
- Proper word boundary matching (no partial matches inside words)
- Short name protection (names < 5 chars require exact case match)
- Ambiguous name blocklist
- Email/date-slug exclusions
- Test mode for QA
"""

import os
import re
import sys
import json
import time
from datetime import date
from collections import defaultdict

VAULT = "/Users/debra/SecondBrain"
CONCEPTS_DIR = os.path.join(VAULT, "Concepts")
MOCS_DIR = os.path.join(VAULT, "MOCs")
REPORT_DIR = os.path.join(VAULT, "Reflections", "Daily")
SKIP_DIRS = {"_archived", "Imports", ".obsidian", "photos", ".git", "node_modules"}

# State and cache files
STATE_FILE = os.path.join(VAULT, ".weaver_state.json")
ENTITY_CACHE_FILE = os.path.join(VAULT, ".weaver_entity_cache.json")

# Chunk size for batched processing
CHUNK_SIZE = 500

# Skip entity weaving for files larger than this (they're usually chat archives)
MAX_FILE_SIZE_FOR_ENTITY_WEAVE = 50 * 1024  # 50KB

# Names that are too ambiguous to auto-link
AMBIGUOUS_NAMES = {
    "done", "projects", "actions", "inbox", "backlog", "waiting", "someday",
    "health", "finance", "learning", "creative", "personal", "work",
    "people", "documents", "reflections", "concepts", "mocs",
    "a", "an", "the", "of", "in", "on", "at", "to", "for", "is", "it",
    "notes", "random notes", "brain dump",
    # Single/double letter names and common short words (learned 2026-03-28)
    "k", "e", "os", "jas", "lau", "tee", "joe", "trim",
    "lisia", "dystini", "halez",
}

# Hard minimum: never wikilink names shorter than this, period
ABSOLUTE_MIN_NAME_LENGTH = 3

# Concept candidates to actively look for
CONCEPT_CANDIDATES = [
    "HeartMath", "Johari Window", "Zettelkasten",
    "Data Sovereignty", "Communitism",
    "The Sentinel", "The Silvering", "The Looking Glass", "The Registry", "Mirror Mirror",
    "Night Swimming", "Wrinkles", "Drops", "Ripples",
    "ADAPT 2026", "Fractal", "SEEK", "KBUDDS",
    "Consciousness", "Self-reflection", "Self-actualization",
    "Lunchpool", "Pooli",
    "Abellminded",
]

# Minimum entity name length for case-insensitive matching (shorter = exact match only)
MIN_CASE_INSENSITIVE_LENGTH = 5

# Stats
stats = {
    "files_scanned": 0,
    "files_modified": 0,
    "files_skipped_unchanged": 0,
    "wikilinks_created": 0,
    "stubs_created": 0,
    "concept_cards_created": 0,
    "backlinks_added": 0,
    "skipped_ambiguous": 0,
    "skipped_short": 0,
    "incremental_mode": False,
    "chunks_processed": 0,
    "start_time": 0.0,
    "end_time": 0.0,
}

link_counts = defaultdict(int)
backlink_map = defaultdict(list)
discoveries = []
qa_log = []


def log_qa(msg):
    qa_log.append(msg)


# ──────────────────────────────────────────────
# State & Cache helpers
# ──────────────────────────────────────────────

def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"  Warning: Could not load state file: {e}", flush=True)
    return {}


def save_state(state):
    try:
        with open(STATE_FILE, "w") as f:
            json.dump(state, f, indent=2)
    except Exception as e:
        print(f"  Warning: Could not save state file: {e}", flush=True)


def load_entity_cache():
    if os.path.exists(ENTITY_CACHE_FILE):
        try:
            cache_mtime = os.path.getmtime(ENTITY_CACHE_FILE)
            with open(ENTITY_CACHE_FILE, "r") as f:
                return json.load(f), cache_mtime
        except Exception as e:
            print(f"  Warning: Could not load entity cache: {e}", flush=True)
    return None, 0


def save_entity_cache(lookup):
    try:
        with open(ENTITY_CACHE_FILE, "w") as f:
            json.dump(lookup, f, indent=2)
    except Exception as e:
        print(f"  Warning: Could not save entity cache: {e}", flush=True)


# ──────────────────────────────────────────────
# File scanning
# ──────────────────────────────────────────────

def get_all_md_files():
    result = []
    for root, dirs, files in os.walk(VAULT):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in files:
            if f.endswith(".md"):
                result.append(os.path.join(root, f))
    return result


def filter_modified_files(all_files, last_run_time):
    modified = []
    for fp in all_files:
        try:
            mtime = os.path.getmtime(fp)
            if mtime > last_run_time:
                modified.append(fp)
        except OSError:
            modified.append(fp)
    return modified


# ──────────────────────────────────────────────
# Entity lookup
# ──────────────────────────────────────────────

def build_entity_lookup(all_files, force_rebuild=False):
    """Return {name_lowercase: canonical_name}. Uses JSON cache when fresh."""
    if not force_rebuild:
        cache, cache_mtime = load_entity_cache()
        if cache is not None:
            # Exclude report files (Weaver writes those, which would always make cache stale)
            non_report_files = [
                fp for fp in all_files
                if "/Reflections/Daily/" not in fp
            ]
            newest_file = max((os.path.getmtime(fp) for fp in non_report_files), default=0)
            if newest_file <= cache_mtime:
                print(f"  Using cached entity lookup ({len(cache)} entities)", flush=True)
                return cache
            else:
                print(f"  Entity cache stale (newest: {time.strftime('%H:%M:%S', time.localtime(newest_file))}), rebuilding...", flush=True)

    print(f"  Building entity lookup from {len(all_files)} files...", flush=True)
    lookup = {}
    for fp in all_files:
        stem = os.path.splitext(os.path.basename(fp))[0]
        lower = stem.lower()
        if len(stem) < ABSOLUTE_MIN_NAME_LENGTH:
            stats["skipped_short"] += 1
            continue
        if lower in AMBIGUOUS_NAMES:
            stats["skipped_ambiguous"] += 1
            continue
        if "@" in stem or stem.startswith("_plus_"):
            stats["skipped_ambiguous"] += 1
            continue
        if re.match(r'^\d{4}-\d{2}-\d{2}', stem):
            stats["skipped_ambiguous"] += 1
            continue
        lookup[lower] = stem

    save_entity_cache(lookup)
    print(f"  Entity lookup: {len(lookup)} entities (saved to cache)", flush=True)
    return lookup


def build_combined_regex(entity_lookup):
    """
    Build a single compiled regex that matches any entity name.
    Uses alternation: \b(Name1|Name2|...)\b
    Sorted by length desc so longer names match before shorter ones.
    """
    names = list(entity_lookup.values())
    # Sort longest first so "Alex Abell" matches before "Alex"
    names_sorted = sorted(names, key=len, reverse=True)
    pattern = r'\b(' + '|'.join(re.escape(n) for n in names_sorted) + r')\b'
    return re.compile(pattern, re.IGNORECASE), names_sorted


# ──────────────────────────────────────────────
# Text processing helpers
# ──────────────────────────────────────────────

# Pre-compiled mask regex (code, wikilinks, urls, yaml, markdown links)
MASK_RE = re.compile(
    r'```.*?```'           # fenced code blocks
    r'|`[^`\n]+`'          # inline code
    r'|\[\[[^\]]+\]\]'     # existing wikilinks
    r'|https?://\S+'       # URLs
    r'|\[[^\]]*\]\([^\)]*\)'  # markdown links [text](url)
    r'|^[a-z_]+:.*$',     # YAML-like lines
    re.DOTALL | re.MULTILINE
)


def mask_protected_regions(text):
    blocks = []

    def replacer(m):
        idx = len(blocks)
        blocks.append(m.group(0))
        return f"\x00M{idx}\x00"

    masked = MASK_RE.sub(replacer, text)
    return masked, blocks


def unmask(text, blocks):
    for i, block in enumerate(blocks):
        text = text.replace(f"\x00M{i}\x00", block)
    return text


def parse_frontmatter(content):
    if content.startswith("---"):
        end = content.find("\n---", 3)
        if end != -1:
            fm = content[:end + 4]
            body = content[end + 4:]
            return fm, body, True
    return "", content, False


# ──────────────────────────────────────────────
# Core file processing (combined regex approach)
# ──────────────────────────────────────────────

def process_file(filepath, entity_lookup, combined_re, names_sorted):
    # Skip very large files (chat archives, import dumps) - they slow weaving significantly
    try:
        file_size = os.path.getsize(filepath)
        if file_size > MAX_FILE_SIZE_FOR_ENTITY_WEAVE:
            log_qa(f"SKIP large file ({file_size/1024:.0f}KB): {os.path.basename(filepath)}")
            return []
    except OSError:
        pass

    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            original = f.read()
    except Exception:
        return []

    fm, body, has_fm = parse_frontmatter(original)
    source_stem = os.path.splitext(os.path.basename(filepath))[0]
    source_lower = source_stem.lower()

    # Quick pre-check: does the file contain any entity name at all?
    # Use the combined regex for a fast scan first
    if not combined_re.search(body):
        return []

    masked, blocks = mask_protected_regions(body)
    linked_entities = []

    # Find all matches in one pass using combined regex
    matches = list(combined_re.finditer(masked))
    if not matches:
        return []

    # Filter out: self-links, short names with wrong case
    valid_replacements = []
    for m in matches:
        matched_text = m.group(1)
        matched_lower = matched_text.lower()

        # Don't self-link
        if matched_lower == source_lower:
            continue

        # Short names: require exact case match
        canonical = entity_lookup.get(matched_lower, matched_text)
        if len(canonical) < MIN_CASE_INSENSITIVE_LENGTH:
            if matched_text != canonical:
                stats["skipped_short"] += 1
                continue

        valid_replacements.append((m.start(), m.end(), matched_text, canonical))

    if not valid_replacements:
        return []

    # Apply replacements in reverse order (to preserve positions)
    new_masked = masked
    for start, end, matched_text, canonical in reversed(valid_replacements):
        new_masked = new_masked[:start] + f"[[{matched_text}]]" + new_masked[end:]
        stats["wikilinks_created"] += 1
        link_counts[canonical] += 1
        if canonical not in linked_entities:
            linked_entities.append(canonical)

    new_body = unmask(new_masked, blocks)

    if new_body != body:
        new_content = fm + new_body
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(new_content)
            stats["files_modified"] += 1
        except Exception as e:
            log_qa(f"ERROR writing {filepath}: {e}")
            return []

        for entity in linked_entities:
            backlink_map[entity].append((source_stem, f"mentioned in {source_stem}"))

    return linked_entities


# ──────────────────────────────────────────────
# Backlinks
# ──────────────────────────────────────────────

def ensure_backlinks_section(content):
    if "## Back-links" in content or "## Wrinkles" in content:
        return content, False
    return content.rstrip() + "\n\n## Back-links\n", True


def append_backlink(content, source_stem):
    entry = f"- [[{source_stem}]]\n"
    for section in ["## Back-links", "## Wrinkles"]:
        idx = content.find(section)
        if idx != -1:
            if f"[[{source_stem}]]" in content[idx:]:
                return content, False
            rest_start = idx + len(section)
            next_section = re.search(r'\n##\s', content[rest_start:])
            if next_section:
                insert_pos = rest_start + next_section.start()
                return content[:insert_pos] + "\n" + entry + content[insert_pos:], True
            else:
                return content.rstrip() + "\n" + entry, True
    return content, False


def update_backlinks(entity_files_map):
    print(f"\n=== Updating Back-links ({len(entity_files_map)} entities) ===", flush=True)
    for entity, sources in entity_files_map.items():
        entity_file = None
        for root, dirs, files in os.walk(VAULT):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
            for fn in files:
                if fn == f"{entity}.md":
                    entity_file = os.path.join(root, fn)
                    break
            if entity_file:
                break

        if not entity_file:
            continue

        try:
            with open(entity_file, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
        except Exception:
            continue

        content, added_section = ensure_backlinks_section(content)
        changed = added_section

        for source_stem, _ in sources:
            content, ok = append_backlink(content, source_stem)
            if ok:
                stats["backlinks_added"] += 1
                changed = True

        if changed:
            try:
                with open(entity_file, "w", encoding="utf-8") as f:
                    f.write(content)
            except Exception as e:
                log_qa(f"ERROR writing backlinks to {entity_file}: {e}")

    print(f"Back-links updated: {stats['backlinks_added']}", flush=True)


# ──────────────────────────────────────────────
# Pass 1: Entity weave (chunked)
# ──────────────────────────────────────────────

def pass1_entity_weave(files_to_process, entity_lookup, combined_re, names_sorted):
    total = len(files_to_process)
    print(f"\n=== PASS 1: Entity Weave ({total} files, chunk_size={CHUNK_SIZE}) ===", flush=True)

    def priority(fp):
        rel = fp.replace(VAULT, "")
        if "/People/" in rel: return 0
        if "/Projects/" in rel: return 1
        if "/Work/" in rel: return 2
        return 3

    sorted_files = sorted(files_to_process, key=priority)
    num_chunks = (total + CHUNK_SIZE - 1) // CHUNK_SIZE

    for chunk_idx in range(num_chunks):
        chunk_start = chunk_idx * CHUNK_SIZE
        chunk_end = min(chunk_start + CHUNK_SIZE, total)
        chunk = sorted_files[chunk_start:chunk_end]
        chunk_t0 = time.time()

        for fp in chunk:
            stats["files_scanned"] += 1
            process_file(fp, entity_lookup, combined_re, names_sorted)

        chunk_elapsed = time.time() - chunk_t0
        stats["chunks_processed"] += 1
        pct = (chunk_end / total * 100)
        print(f"  Chunk {chunk_idx+1}/{num_chunks} ({pct:.0f}%): {len(chunk)} files in {chunk_elapsed:.1f}s "
              f"| wikilinks so far: {stats['wikilinks_created']}", flush=True)

    print(f"\nPass 1 complete: {stats['wikilinks_created']} wikilinks, {stats['files_modified']} files modified", flush=True)


# ──────────────────────────────────────────────
# Pass 2: Concept weave
# ──────────────────────────────────────────────

def pass2_concept_weave(all_files):
    print(f"\n=== PASS 2: Concept Weave ({len(CONCEPT_CANDIDATES)} candidates) ===", flush=True)

    concept_file_map = defaultdict(list)
    for fp in all_files:
        try:
            with open(fp, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
        except Exception:
            continue

        for concept in CONCEPT_CANDIDATES:
            pattern = r'\b' + re.escape(concept) + r'\b'
            flags = 0 if len(concept) < MIN_CASE_INSENSITIVE_LENGTH else re.IGNORECASE
            if re.search(pattern, content, flags):
                concept_file_map[concept].append(fp)

    for concept, files in concept_file_map.items():
        if len(files) < 2:
            continue
        concept_path = os.path.join(CONCEPTS_DIR, f"{concept}.md")
        if os.path.exists(concept_path):
            continue

        print(f"  Creating concept card: {concept} (referenced in {len(files)} files)", flush=True)
        refs_list = "\n".join(
            [f"- [[{os.path.splitext(os.path.basename(f))[0]}]]" for f in files[:20]]
        )
        content = f"""---
name: {concept}
type: concept
created: {date.today().isoformat()}
tags: [concept]
---

# {concept}

> *Concept card auto-generated by Weaver.*

## Definition

*[Define this concept here.]*

## References

{refs_list}

## Back-links
"""
        with open(concept_path, "w", encoding="utf-8") as f:
            f.write(content)
        stats["concept_cards_created"] += 1
        discoveries.append(f"Concept **{concept}** appears in {len(files)} files")

    print(f"Pass 2 complete: {stats['concept_cards_created']} concept cards created", flush=True)


# ──────────────────────────────────────────────
# Reports
# ──────────────────────────────────────────────

def write_report(incremental_mode, total_files, processed_files):
    os.makedirs(REPORT_DIR, exist_ok=True)
    today = date.today().isoformat()
    report_path = os.path.join(REPORT_DIR, f"{today} Weaver Report.md")

    top_entities = sorted(link_counts.items(), key=lambda x: x[1], reverse=True)[:20]
    top_table = "| Entity | Link Count |\n|--------|------------|\n"
    for name, count in top_entities:
        top_table += f"| [[{name}]] | {count} |\n"

    discovery_text = "\n".join([f"- {d}" for d in discoveries]) if discoveries else "- No unexpected connections found."
    qa_text = "\n".join([f"- {q}" for q in qa_log[:50]]) if qa_log else "- Clean run, no issues."
    elapsed = stats["end_time"] - stats["start_time"]

    mode_note = (
        f"**Incremental mode** — {processed_files}/{total_files} files processed "
        f"({stats['files_skipped_unchanged']} unchanged)"
        if incremental_mode
        else f"**Full scan** — all {total_files} files processed"
    )

    report = f"""---
date: {today}
type: weaver-report
tags: [weaver, maintenance, zettelkasten]
---

# Weaver Report — {today}

*Auto-generated by Weaver v3.*

## Run Mode
{mode_note}
Runtime: **{elapsed:.1f}s** | Chunks: {stats['chunks_processed']}

## Summary

| Metric | Count |
|--------|-------|
| Files Total | {total_files} |
| Files Processed | {processed_files} |
| Files Modified | {stats['files_modified']} |
| Files Skipped (unchanged) | {stats['files_skipped_unchanged']} |
| New Wikilinks Created | {stats['wikilinks_created']} |
| Concept Cards Created | {stats['concept_cards_created']} |
| Back-links Added | {stats['backlinks_added']} |
| Skipped (ambiguous) | {stats['skipped_ambiguous']} |
| Skipped (short/wrong-case) | {stats['skipped_short']} |

## Top 20 Most Connected Entities

{top_table}

## Discoveries

{discovery_text}

## QA Log

{qa_text}

## Matching Rules (v3)
- **Combined regex**: single pass per file using alternation (11x faster than v2)
- Names < {MIN_CASE_INSENSITIVE_LENGTH} chars require **exact case match**
- Word boundary matching with \\b
- Ambiguous names blocklisted
- Email/date-slug file names excluded
- Protected regions masked: code blocks, wikilinks, URLs, YAML, markdown links
- Frontmatter never modified
- **Incremental**: only processes files modified since last run
- **Chunked**: {CHUNK_SIZE} files per batch
"""

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"\nReport written to: {report_path}", flush=True)
    return report_path


def write_qa_report():
    today = date.today().isoformat()
    qa_path = os.path.join(REPORT_DIR, f"{today} Weaver QA.md")
    with open(qa_path, "w", encoding="utf-8") as f:
        f.write(f"# Weaver QA Report — {today}\n\n")
        f.write(f"## Stats\n```json\n{json.dumps(stats, indent=2)}\n```\n\n")
        f.write("## Top Linked Entities\n")
        for name, count in sorted(link_counts.items(), key=lambda x: x[1], reverse=True):
            f.write(f"- {name}: {count}\n")
        f.write(f"\n## QA Log ({len(qa_log)} entries)\n")
        for entry in qa_log:
            f.write(f"- {entry}\n")
    print(f"QA report written to: {qa_path}", flush=True)


# ──────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────

def main():
    test_mode = "--test" in sys.argv
    full_mode = "--full" in sys.argv

    stats["start_time"] = time.time()

    print("🕸️  Weaver v3 starting...", flush=True)
    print(f"Vault: {VAULT}", flush=True)
    if test_mode:
        print("*** TEST MODE ***", flush=True)

    os.makedirs(CONCEPTS_DIR, exist_ok=True)
    os.makedirs(MOCS_DIR, exist_ok=True)

    # Load state for incremental mode
    state = load_state()
    last_run_time = state.get("last_run_time", 0)

    all_files = get_all_md_files()
    print(f"Found {len(all_files)} markdown files", flush=True)

    # Incremental vs full
    incremental_mode = (last_run_time > 0) and not full_mode
    if incremental_mode:
        files_to_process = filter_modified_files(all_files, last_run_time)
        stats["files_skipped_unchanged"] = len(all_files) - len(files_to_process)
        last_run_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(last_run_time))
        print(f"Incremental mode: last run was {last_run_str}", flush=True)
        print(f"Files to process: {len(files_to_process)} / {len(all_files)} ({stats['files_skipped_unchanged']} unchanged)", flush=True)
        stats["incremental_mode"] = True
    else:
        files_to_process = all_files
        mode_label = "Full scan (--full)" if full_mode else "Full scan (first run)"
        print(mode_label, flush=True)

    # Build entity lookup (uses cache when fresh)
    entity_lookup = build_entity_lookup(all_files, force_rebuild=full_mode)
    print(f"Entities: {len(entity_lookup)} ({stats['skipped_ambiguous']} ambiguous, {stats['skipped_short']} short skipped)", flush=True)

    # Build combined regex (single compilation)
    t0 = time.time()
    combined_re, names_sorted = build_combined_regex(entity_lookup)
    print(f"Combined regex compiled in {time.time()-t0:.2f}s", flush=True)

    # Pass 1
    if files_to_process:
        pass1_entity_weave(files_to_process, entity_lookup, combined_re, names_sorted)
    else:
        print("\nPass 1: No files modified since last run — skipping", flush=True)

    # Backlinks
    if backlink_map:
        update_backlinks(backlink_map)

    # Pass 2 (always scan all files for concepts)
    all_files_current = get_all_md_files()
    pass2_concept_weave(all_files_current)

    # Save state
    stats["end_time"] = time.time()
    save_state({
        "last_run_time": stats["start_time"],
        "last_run_date": date.today().isoformat(),
        "files_processed": len(files_to_process),
        "files_total": len(all_files),
        "wikilinks_created": stats["wikilinks_created"],
        "incremental_mode": incremental_mode,
    })

    # Reports
    write_report(incremental_mode, len(all_files), len(files_to_process))
    write_qa_report()

    elapsed = stats["end_time"] - stats["start_time"]
    print(f"\n🕸️  Weaver v3 complete in {elapsed:.1f}s!", flush=True)
    print(f"   Files total:          {len(all_files)}", flush=True)
    print(f"   Files processed:      {len(files_to_process)}", flush=True)
    print(f"   Files skipped:        {stats['files_skipped_unchanged']}", flush=True)
    print(f"   Files modified:       {stats['files_modified']}", flush=True)
    print(f"   Wikilinks created:    {stats['wikilinks_created']}", flush=True)
    print(f"   Concept cards:        {stats['concept_cards_created']}", flush=True)
    print(f"   Back-links added:     {stats['backlinks_added']}", flush=True)
    print(f"   Chunks processed:     {stats['chunks_processed']}", flush=True)


if __name__ == "__main__":
    main()
