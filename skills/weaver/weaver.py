#!/usr/bin/env python3
"""
Weaver v2 — Zettelkasten connection builder for SecondBrain
Creates wikilinks, concept cards, stubs, and back-links.

Fixes from v1:
- Proper word boundary matching (no partial matches inside words)
- Short name protection (names < 4 chars require exact case match)
- Ambiguous name blocklist
- Test mode for QA
"""

import os
import re
import sys
import json
from datetime import date
from collections import defaultdict

VAULT = "/Users/debra/SecondBrain"
CONCEPTS_DIR = os.path.join(VAULT, "Concepts")
MOCS_DIR = os.path.join(VAULT, "MOCs")
REPORT_DIR = os.path.join(VAULT, "Reflections", "Daily")
SKIP_DIRS = {"_archived", "Imports", ".obsidian", "photos", ".git", "node_modules"}

# Names that are too ambiguous to auto-link (common English words or fragments)
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

# Minimum entity name length to auto-link (shorter names need exact case match)
MIN_CASE_INSENSITIVE_LENGTH = 5

# Stats
stats = {
    "files_scanned": 0,
    "wikilinks_created": 0,
    "stubs_created": 0,
    "concept_cards_created": 0,
    "backlinks_added": 0,
    "skipped_ambiguous": 0,
    "skipped_short": 0,
}

link_counts = defaultdict(int)
backlink_map = defaultdict(list)
discoveries = []
qa_log = []  # For test/debug output


def log_qa(msg):
    qa_log.append(msg)


def get_all_md_files():
    result = []
    for root, dirs, files in os.walk(VAULT):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in files:
            if f.endswith(".md"):
                full = os.path.join(root, f)
                result.append(full)
    return result


def build_entity_lookup(all_files):
    """Return dict: {name_lowercase: canonical_name} for all file stems."""
    lookup = {}
    for fp in all_files:
        stem = os.path.splitext(os.path.basename(fp))[0]
        lower = stem.lower()
        # Skip names below absolute minimum length
        if len(stem) < ABSOLUTE_MIN_NAME_LENGTH:
            stats["skipped_short"] += 1
            log_qa(f"SKIP too short: '{stem}'")
            continue
        # Skip ambiguous names
        if lower in AMBIGUOUS_NAMES:
            stats["skipped_ambiguous"] += 1
            log_qa(f"SKIP ambiguous: '{stem}'")
            continue
        # Skip email addresses
        if "@" in stem or stem.startswith("_plus_"):
            stats["skipped_ambiguous"] += 1
            log_qa(f"SKIP email/phone: '{stem}'")
            continue
        # Skip date-pattern file slugs (YYYY-MM-DD-*)
        if re.match(r'^\d{4}-\d{2}-\d{2}', stem):
            stats["skipped_ambiguous"] += 1
            log_qa(f"SKIP date-slug: '{stem}'")
            continue
        lookup[lower] = stem
    return lookup


def parse_frontmatter(content):
    if content.startswith("---"):
        end = content.find("\n---", 3)
        if end != -1:
            fm = content[:end + 4]
            body = content[end + 4:]
            return fm, body, True
    return "", content, False


def mask_protected_regions(text):
    """Mask code blocks, existing wikilinks, URLs, and frontmatter references."""
    blocks = []
    def replacer(m):
        idx = len(blocks)
        blocks.append(m.group(0))
        return f"\x00MASKED{idx}\x00"
    
    # Mask code blocks (``` ... ```)
    masked = re.sub(r"```.*?```", replacer, text, flags=re.DOTALL)
    # Mask inline code (`...`)
    masked = re.sub(r"`[^`\n]+`", replacer, masked)
    # Mask existing wikilinks ([[...]])
    masked = re.sub(r"\[\[[^\]]+\]\]", replacer, masked)
    # Mask URLs
    masked = re.sub(r"https?://[^\s\)]+", replacer, masked)
    # Mask markdown links [text](url)
    masked = re.sub(r"\[[^\]]*\]\([^\)]*\)", replacer, masked)
    # Mask YAML-like lines (key: value) to avoid linking inside metadata
    masked = re.sub(r"^[a-z_]+:.*$", replacer, masked, flags=re.MULTILINE)
    
    return masked, blocks


def unmask(text, blocks):
    for i, block in enumerate(blocks):
        text = text.replace(f"\x00MASKED{i}\x00", block)
    return text


def should_link(name, match_text):
    """
    Determine if a match should actually be linked.
    Handles short names, case sensitivity, and context.
    """
    # Short names (< MIN_CASE_INSENSITIVE_LENGTH chars) must be exact case match
    if len(name) < MIN_CASE_INSENSITIVE_LENGTH:
        if match_text != name:
            return False
    return True


def make_wikilink_pattern(name):
    """
    Build a regex that matches the name as a complete word/phrase.
    Uses \\b word boundaries for proper matching.
    """
    escaped = re.escape(name)
    # Use word boundaries to prevent partial matches
    # \b matches at word boundary (between \w and \W)
    return r'\b(' + escaped + r')\b'


def add_wikilinks(body, entity_names, source_file_stem):
    masked, blocks = mask_protected_regions(body)
    linked_entities = []

    # Sort by length descending to match longer names first
    sorted_names = sorted(entity_names, key=lambda x: len(x), reverse=True)

    for name in sorted_names:
        # Don't self-link
        if name.lower() == source_file_stem.lower():
            continue

        pattern = make_wikilink_pattern(name)
        
        # For short names, use case-sensitive matching
        if len(name) < MIN_CASE_INSENSITIVE_LENGTH:
            flags = 0  # case sensitive
        else:
            flags = re.IGNORECASE

        # Find all matches first, filter, then replace
        matches = list(re.finditer(pattern, masked, flags=flags))
        if not matches:
            continue

        # Verify each match passes the should_link check
        valid_matches = [m for m in matches if should_link(name, m.group(1))]
        if not valid_matches:
            stats["skipped_short"] += 1
            continue

        # Replace (do it in reverse order to preserve positions)
        new_masked = masked
        for m in reversed(valid_matches):
            original_text = m.group(1)
            new_masked = new_masked[:m.start()] + f"[[{original_text}]]" + new_masked[m.end():]
            stats["wikilinks_created"] += 1
            link_counts[name] += 1

        masked = new_masked
        linked_entities.append(name)

    result = unmask(masked, blocks)
    return result, linked_entities


def ensure_backlinks_section(content):
    if "## Back-links" in content or "## Wrinkles" in content:
        return content, False
    return content.rstrip() + "\n\n## Back-links\n", True


def append_backlink(content, source_stem, context):
    entry = f"- [[{source_stem}]]\n"
    for section in ["## Back-links", "## Wrinkles"]:
        idx = content.find(section)
        if idx != -1:
            # Check if already listed
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


def create_concept_card(concept, referencing_files):
    os.makedirs(CONCEPTS_DIR, exist_ok=True)
    filepath = os.path.join(CONCEPTS_DIR, f"{concept}.md")
    if os.path.exists(filepath):
        return False

    refs_list = "\n".join([f"- [[{os.path.splitext(os.path.basename(f))[0]}]]" for f in referencing_files[:20]])

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
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    stats["concept_cards_created"] += 1
    return True


def process_file(filepath, entity_lookup):
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            original = f.read()
    except Exception:
        return []

    fm, body, has_fm = parse_frontmatter(original)
    source_stem = os.path.splitext(os.path.basename(filepath))[0]

    entity_names = list(entity_lookup.values())
    new_body, linked = add_wikilinks(body, entity_names, source_stem)

    if linked:
        new_content = fm + new_body
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(new_content)
        except Exception as e:
            log_qa(f"ERROR writing {filepath}: {e}")
            return []

        for entity in linked:
            backlink_map[entity].append((source_stem, f"mentioned in {source_stem}"))

    return linked


def update_backlinks(entity_files_map):
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

        if not entity_file or not os.path.exists(entity_file):
            continue

        try:
            with open(entity_file, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
        except Exception:
            continue

        content, added_section = ensure_backlinks_section(content)
        changed = added_section

        for source_stem, context in sources:
            if f"[[{source_stem}]]" not in content:
                content, ok = append_backlink(content, source_stem, context)
                if ok:
                    stats["backlinks_added"] += 1
                    changed = True

        if changed:
            try:
                with open(entity_file, "w", encoding="utf-8") as f:
                    f.write(content)
            except Exception as e:
                log_qa(f"ERROR writing backlinks to {entity_file}: {e}")


def pass1_entity_weave(all_files, entity_lookup):
    print(f"\n=== PASS 1: Entity Weave ({len(all_files)} files) ===")

    def priority(fp):
        rel = fp.replace(VAULT, "")
        if "/People/" in rel: return 0
        if "/Projects/" in rel: return 1
        if "/Work/" in rel: return 2
        return 3

    sorted_files = sorted(all_files, key=priority)

    for i, fp in enumerate(sorted_files):
        if i % 50 == 0:
            print(f"  Processing file {i+1}/{len(sorted_files)}...")
        stats["files_scanned"] += 1
        linked = process_file(fp, entity_lookup)


def pass2_concept_weave(all_files):
    print(f"\n=== PASS 2: Concept Weave ===")

    concept_file_map = defaultdict(list)

    for fp in all_files:
        try:
            with open(fp, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
        except Exception:
            continue

        for concept in CONCEPT_CANDIDATES:
            # Use word boundary matching for concepts too
            pattern = r'\b' + re.escape(concept) + r'\b'
            if len(concept) < MIN_CASE_INSENSITIVE_LENGTH:
                flags = 0
            else:
                flags = re.IGNORECASE
            if re.search(pattern, content, flags):
                concept_file_map[concept].append(fp)

    for concept, files in concept_file_map.items():
        if len(files) < 2:
            continue
        concept_path = os.path.join(CONCEPTS_DIR, f"{concept}.md")
        if os.path.exists(concept_path):
            continue

        print(f"  Creating concept card: {concept} (referenced in {len(files)} files)")
        created = create_concept_card(concept, files)
        if created:
            discoveries.append(f"Concept **{concept}** appears in {len(files)} files")


def write_report():
    os.makedirs(REPORT_DIR, exist_ok=True)
    today = date.today().isoformat()
    report_path = os.path.join(REPORT_DIR, f"{today} Weaver Report.md")

    top_entities = sorted(link_counts.items(), key=lambda x: x[1], reverse=True)[:20]

    top_table = "| Entity | Link Count |\n|--------|------------|\n"
    for name, count in top_entities:
        top_table += f"| [[{name}]] | {count} |\n"

    discovery_text = "\n".join([f"- {d}" for d in discoveries]) if discoveries else "- No unexpected connections found."

    qa_text = "\n".join([f"- {q}" for q in qa_log[:50]]) if qa_log else "- Clean run, no issues."

    report = f"""---
date: {today}
type: weaver-report
tags: [weaver, maintenance, zettelkasten]
---

# Weaver Report — {today}

*Auto-generated by Weaver v2.*

## Summary

| Metric | Count |
|--------|-------|
| Files Scanned | {stats["files_scanned"]} |
| New Wikilinks Created | {stats["wikilinks_created"]} |
| Stub Files Created | {stats["stubs_created"]} |
| Concept Cards Created | {stats["concept_cards_created"]} |
| Back-links Added | {stats["backlinks_added"]} |
| Skipped (ambiguous) | {stats["skipped_ambiguous"]} |
| Skipped (short name, wrong case) | {stats["skipped_short"]} |

## Top 20 Most Connected Entities

{top_table}

## Discoveries

{discovery_text}

## QA Log

{qa_text}

## Matching Rules (v2)
- Names < {MIN_CASE_INSENSITIVE_LENGTH} chars require **exact case match** (prevents "Jay" matching "jaywalking")
- Word boundary matching with \\b (prevents "PARA" matching "separate")
- Ambiguous names blocklisted: common words like "done", "projects", "health", etc.
- Protected regions masked: code blocks, existing wikilinks, URLs, YAML lines, markdown links
- Frontmatter never modified
"""

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"\nReport written to: {report_path}")
    return report_path


def write_qa_report():
    """Write detailed QA report for debugging."""
    qa_path = os.path.join(REPORT_DIR, f"{date.today().isoformat()} Weaver QA.md")
    with open(qa_path, "w", encoding="utf-8") as f:
        f.write(f"# Weaver QA Report — {date.today().isoformat()}\n\n")
        f.write(f"## Stats\n```json\n{json.dumps(stats, indent=2)}\n```\n\n")
        f.write(f"## All Entity Link Counts\n")
        for name, count in sorted(link_counts.items(), key=lambda x: x[1], reverse=True):
            f.write(f"- {name}: {count}\n")
        f.write(f"\n## QA Log ({len(qa_log)} entries)\n")
        for entry in qa_log:
            f.write(f"- {entry}\n")
    print(f"QA report written to: {qa_path}")


def main():
    test_mode = "--test" in sys.argv
    
    print("🕸️  Weaver v2 starting...")
    print(f"Vault: {VAULT}")
    if test_mode:
        print("*** TEST MODE — will process but write QA report ***")

    os.makedirs(CONCEPTS_DIR, exist_ok=True)
    os.makedirs(MOCS_DIR, exist_ok=True)

    all_files = get_all_md_files()
    print(f"Found {len(all_files)} markdown files")

    entity_lookup = build_entity_lookup(all_files)
    print(f"Entity lookup: {len(entity_lookup)} entities ({stats['skipped_ambiguous']} ambiguous skipped)")

    # Pass 1
    pass1_entity_weave(all_files, entity_lookup)
    print(f"\nPass 1 complete: {stats['wikilinks_created']} wikilinks added")

    # Back-links
    print("\n=== Updating Back-links ===")
    update_backlinks(backlink_map)
    print(f"Back-links updated: {stats['backlinks_added']}")

    # Pass 2
    all_files = get_all_md_files()
    pass2_concept_weave(all_files)
    print(f"\nPass 2 complete: {stats['concept_cards_created']} concept cards created")

    # Reports
    write_report()
    write_qa_report()

    print(f"\n🕸️  Weaver v2 complete!")
    print(f"   Files scanned:       {stats['files_scanned']}")
    print(f"   Wikilinks created:   {stats['wikilinks_created']}")
    print(f"   Stubs created:       {stats['stubs_created']}")
    print(f"   Concept cards:       {stats['concept_cards_created']}")
    print(f"   Back-links added:    {stats['backlinks_added']}")
    print(f"   Skipped ambiguous:   {stats['skipped_ambiguous']}")
    print(f"   Skipped short/case:  {stats['skipped_short']}")


if __name__ == "__main__":
    main()
