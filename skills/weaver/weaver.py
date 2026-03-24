#!/usr/bin/env python3
"""
Weaver — Zettelkasten connection builder for SecondBrain
Creates wikilinks, concept cards, stubs, and back-links.
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
SKIP_DIRS = {"_archived", "Imports", ".obsidian", "photos"}

# Concept candidates to actively look for
CONCEPT_CANDIDATES = [
    "HeartMath", "Johari Window", "PARA", "Zettelkasten", "GTD",
    "Data Sovereignty", "Communitism", "P.O.W.E.R.",
    "The Sentinel", "The Silvering", "The Looking Glass", "The Registry", "Mirror Mirror",
    "Night Swimming", "Wrinkles", "Drops", "Ripples",
    "ADAPT 2026", "Fractal", "SEEK", "KBUDDS",
    "Consciousness", "Self-reflection", "Self-actualization",
    "Second Brain", "SecondBrain", "Lunchpool", "Pooli", "Mirror",
    "ORNL", "Abellminded",
]

# Stats
stats = {
    "files_scanned": 0,
    "wikilinks_created": 0,
    "stubs_created": 0,
    "concept_cards_created": 0,
    "backlinks_added": 0,
}

# Track link counts per entity
link_counts = defaultdict(int)
# Track which files link to which entities: {entity: [(source_file, context), ...]}
backlink_map = defaultdict(list)
# Track interesting discoveries
discoveries = []


def should_skip(path):
    parts = path.replace(VAULT, "").split(os.sep)
    for part in parts:
        if part in SKIP_DIRS:
            return True
    return False


def get_all_md_files():
    result = []
    for root, dirs, files in os.walk(VAULT):
        # Prune skip dirs in-place
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
        lookup[stem.lower()] = stem
    return lookup


def parse_frontmatter(content):
    """Return (frontmatter_text, body_text, has_frontmatter)."""
    if content.startswith("---"):
        end = content.find("\n---", 3)
        if end != -1:
            fm = content[:end + 4]
            body = content[end + 4:]
            return fm, body, True
    return "", content, False


def mask_code_blocks(text):
    """Replace content inside code blocks with placeholders. Returns (masked_text, blocks)."""
    blocks = []
    def replacer(m):
        idx = len(blocks)
        blocks.append(m.group(0))
        return f"\x00CODEBLOCK{idx}\x00"
    masked = re.sub(r"```.*?```", replacer, text, flags=re.DOTALL)
    # Also mask inline code
    masked = re.sub(r"`[^`\n]+`", replacer, masked)
    return masked, blocks


def unmask_code_blocks(text, blocks):
    for i, block in enumerate(blocks):
        text = text.replace(f"\x00CODEBLOCK{i}\x00", block)
    return text


def already_wikilinked(text, name):
    """Check if the name appears already inside [[ ]] in text."""
    pattern = r'\[\[' + re.escape(name) + r'(\|[^\]]+)?\]\]'
    return bool(re.search(pattern, text, re.IGNORECASE))


def make_wikilink_pattern(name):
    """
    Build a regex that matches the name as a whole word/phrase,
    but NOT already inside [[ ]] brackets.
    """
    escaped = re.escape(name)
    # Word boundary: match name not preceded by [[ or word char
    # and not followed by ]] or word char (for single words)
    # For multi-word names, just use word boundaries at start/end
    if " " in name:
        pattern = r'(?<!\[\[)(?<!\w)(' + escaped + r')(?!\]\])(?!\w)'
    else:
        pattern = r'(?<!\[\[)(?<!\w)(' + escaped + r')(?!\]\])(?!\w)'
    return pattern


def add_wikilinks(body, entity_names, source_file_stem):
    """
    Add [[wikilinks]] for all entity_names found in body.
    Returns (new_body, list_of_entities_linked).
    """
    masked, blocks = mask_code_blocks(body)
    linked_entities = []

    # Sort by length descending to match longer names first
    sorted_names = sorted(entity_names, key=lambda x: len(x), reverse=True)

    for name in sorted_names:
        # Don't self-link
        if name.lower() == source_file_stem.lower():
            continue
        # Don't link if already a wikilink in the original body
        if already_wikilinked(body, name):
            continue

        pattern = make_wikilink_pattern(name)
        new_masked, n = re.subn(pattern, r'[[\1]]', masked, flags=re.IGNORECASE)
        if n > 0:
            masked = new_masked
            linked_entities.append(name)
            stats["wikilinks_created"] += n
            link_counts[name] += n

    result = unmask_code_blocks(masked, blocks)
    return result, linked_entities


def ensure_backlinks_section(content):
    """Ensure file has a ## Back-links section. Return updated content."""
    if "## Back-links" in content or "## Wrinkles" in content:
        return content, False
    # Add section at end
    return content.rstrip() + "\n\n## Back-links\n", True


def append_backlink(content, source_stem, context):
    """Append a backlink entry to existing section."""
    entry = f"- [[{source_stem}]] — {context}\n"
    # Find the section
    for section in ["## Back-links", "## Wrinkles"]:
        idx = content.find(section)
        if idx != -1:
            # Find end of section (next ## or EOF)
            rest_start = idx + len(section)
            next_section = re.search(r'\n##\s', content[rest_start:])
            if next_section:
                insert_pos = rest_start + next_section.start()
                return content[:insert_pos] + "\n" + entry + content[insert_pos:], True
            else:
                # Append at end
                return content.rstrip() + "\n" + entry, True
    return content, False


def create_stub(name, stub_dir=None):
    """Create a stub file for an entity that doesn't exist."""
    if stub_dir is None:
        stub_dir = VAULT
    filepath = os.path.join(stub_dir, f"{name}.md")
    if os.path.exists(filepath):
        return filepath

    content = f"""---
name: {name}
type: stub
created: {date.today().isoformat()}
tags: [stub]
---

# {name}

> *Stub — no detailed notes yet.*

## Wrinkles
"""
    os.makedirs(stub_dir, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    stats["stubs_created"] += 1
    discoveries.append(f"Created stub for **{name}**")
    return filepath


def create_concept_card(concept, referencing_files):
    """Create a concept card in Concepts/ directory."""
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


def process_file(filepath, entity_lookup, all_files_set):
    """Process a single file: add wikilinks, return list of entities linked."""
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            original = f.read()
    except Exception:
        return []

    fm, body, has_fm = parse_frontmatter(original)
    source_stem = os.path.splitext(os.path.basename(filepath))[0]

    # Build entity names to check (use canonical names)
    entity_names = list(entity_lookup.values())

    new_body, linked = add_wikilinks(body, entity_names, source_stem)

    if linked:
        new_content = fm + new_body
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(new_content)
        except Exception as e:
            print(f"  ERROR writing {filepath}: {e}")
            return []

        # Record backlink info
        for entity in linked:
            # Extract a brief context snippet
            # Find first mention location
            context = f"mentioned in {source_stem}"
            backlink_map[entity].append((source_stem, context))

    return linked


def update_backlinks(entity_files_map):
    """
    For each entity that was linked TO, update its file with back-link entries.
    entity_files_map: {entity_name: [(source_stem, context), ...]}
    """
    for entity, sources in entity_files_map.items():
        # Find the entity's file
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

        # Ensure backlinks section exists
        content, added_section = ensure_backlinks_section(content)

        # Check which sources are already listed
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
                print(f"  ERROR writing backlinks to {entity_file}: {e}")


def pass1_entity_weave(all_files, entity_lookup):
    """Pass 1: Add wikilinks for all entities in all files."""
    print(f"\n=== PASS 1: Entity Weave ({len(all_files)} files) ===")

    # Priority order: People, Projects, Work, then rest
    def priority(fp):
        rel = fp.replace(VAULT, "")
        if "/People/" in rel:
            return 0
        if "/Projects/" in rel:
            return 1
        if "/Work/" in rel:
            return 2
        return 3

    sorted_files = sorted(all_files, key=priority)
    all_files_set = set(all_files)

    for i, fp in enumerate(sorted_files):
        if i % 50 == 0:
            print(f"  Processing file {i+1}/{len(sorted_files)}...")
        stats["files_scanned"] += 1
        linked = process_file(fp, entity_lookup, all_files_set)
        if linked:
            stem = os.path.splitext(os.path.basename(fp))[0]
            print(f"  Linked in {stem}: {linked[:5]}{'...' if len(linked) > 5 else ''}")


def pass2_concept_weave(all_files):
    """Pass 2: Find recurring concepts and create concept cards."""
    print(f"\n=== PASS 2: Concept Weave ===")

    concept_file_map = defaultdict(list)

    for fp in all_files:
        try:
            with open(fp, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
        except Exception:
            continue

        for concept in CONCEPT_CANDIDATES:
            # Check if concept mentioned (as text or wikilink)
            if re.search(re.escape(concept), content, re.IGNORECASE):
                concept_file_map[concept].append(fp)

    # Create concept cards for those appearing in 3+ files without existing card
    for concept, files in concept_file_map.items():
        if len(files) < 2:
            continue
        # Check if concept card already exists
        concept_path = os.path.join(CONCEPTS_DIR, f"{concept}.md")
        if os.path.exists(concept_path):
            continue

        print(f"  Creating concept card: {concept} (referenced in {len(files)} files)")
        created = create_concept_card(concept, files)

        if created:
            discoveries.append(f"Concept **{concept}** appears in {len(files)} files — created card")
            # Now add wikilinks back to concept from source files
            for fp in files[:30]:  # Cap at 30 to avoid too many writes
                try:
                    with open(fp, "r", encoding="utf-8", errors="ignore") as f:
                        original = f.read()
                except Exception:
                    continue

                fm, body, has_fm = parse_frontmatter(original)
                source_stem = os.path.splitext(os.path.basename(fp))[0]

                if already_wikilinked(body, concept):
                    continue

                masked, blocks = mask_code_blocks(body)
                pattern = make_wikilink_pattern(concept)
                new_masked, n = re.subn(pattern, r'[[\1]]', masked, count=1, flags=re.IGNORECASE)
                if n > 0:
                    new_body = unmask_code_blocks(new_masked, blocks)
                    new_content = fm + new_body
                    try:
                        with open(fp, "w", encoding="utf-8") as f:
                            f.write(new_content)
                        stats["wikilinks_created"] += 1
                        link_counts[concept] += 1
                        backlink_map[concept].append((source_stem, f"mentioned in {source_stem}"))
                    except Exception as e:
                        print(f"  ERROR: {e}")


def write_report():
    """Write the Weaver report."""
    os.makedirs(REPORT_DIR, exist_ok=True)
    today = date.today().isoformat()
    report_path = os.path.join(REPORT_DIR, f"{today} Weaver Report.md")

    # Top 10 most connected
    top_entities = sorted(link_counts.items(), key=lambda x: x[1], reverse=True)[:10]

    top_table = "| Entity | Link Count |\n|--------|------------|\n"
    for name, count in top_entities:
        top_table += f"| [[{name}]] | {count} |\n"

    discovery_text = "\n".join([f"- {d}" for d in discoveries]) if discoveries else "- No unexpected connections found."

    report = f"""---
date: {today}
type: weaver-report
tags: [weaver, maintenance, zettelkasten]
---

# Weaver Report — {today}

*Auto-generated by the Weaver skill. Zettelkasten connection pass complete.*

## Summary

| Metric | Count |
|--------|-------|
| Files Scanned | {stats["files_scanned"]} |
| New Wikilinks Created | {stats["wikilinks_created"]} |
| Stub Files Created | {stats["stubs_created"]} |
| Concept Cards Created | {stats["concept_cards_created"]} |
| Back-links Added | {stats["backlinks_added"]} |

## Top 10 Most Connected Entities

{top_table}

## Discoveries

{discovery_text}

## Notes

- Entity Weave: People → Projects → Work → All other files
- Concept candidates scanned: {len(CONCEPT_CANDIDATES)}
- Skipped directories: `_archived/`, `Imports/`, `.obsidian/`
- Frontmatter and code blocks were not modified
"""

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"\nReport written to: {report_path}")
    return report_path


def main():
    print("🕸️  Weaver starting...")
    print(f"Vault: {VAULT}")

    # Ensure output dirs exist
    os.makedirs(CONCEPTS_DIR, exist_ok=True)
    os.makedirs(MOCS_DIR, exist_ok=True)

    # Gather all files
    all_files = get_all_md_files()
    print(f"Found {len(all_files)} markdown files (excluding _archived/ and Imports/)")

    # Build entity lookup
    entity_lookup = build_entity_lookup(all_files)
    print(f"Entity lookup: {len(entity_lookup)} entities")

    # Pass 1: Entity Weave
    pass1_entity_weave(all_files, entity_lookup)

    print(f"\nPass 1 complete: {stats['wikilinks_created']} wikilinks added")

    # Update back-links for all linked entities
    print("\n=== Updating Back-links ===")
    update_backlinks(backlink_map)
    print(f"Back-links updated: {stats['backlinks_added']}")

    # Pass 2: Concept Weave
    # Re-gather files to include any stubs created
    all_files = get_all_md_files()
    pass2_concept_weave(all_files)
    print(f"\nPass 2 complete: {stats['concept_cards_created']} concept cards created")

    # Write report
    report_path = write_report()

    print(f"\n🕸️  Weaver complete!")
    print(f"   Files scanned:       {stats['files_scanned']}")
    print(f"   Wikilinks created:   {stats['wikilinks_created']}")
    print(f"   Stubs created:       {stats['stubs_created']}")
    print(f"   Concept cards:       {stats['concept_cards_created']}")
    print(f"   Back-links added:    {stats['backlinks_added']}")
    print(f"   Report: {report_path}")


if __name__ == "__main__":
    main()
