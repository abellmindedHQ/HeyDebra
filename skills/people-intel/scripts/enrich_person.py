#!/usr/bin/env python3
"""
enrich_person.py — people-intel skill helper script

This script handles the mechanical parts of person enrichment:
- Generating the SecondBrain markdown file from collected data
- Running Neo4j Cypher writes via cypher-shell
- Downloading and saving profile photos
- Checking for existing Google Contacts

Usage:
    python3 enrich_person.py --data person.json [--dry-run]

The JSON input schema is defined below. The AI agent does the research
and passes structured data to this script for deterministic writes.

This script is optional — the agent can do all writes directly via
exec/shell tools. Use this for batch operations or when you want
clean separation between research and write phases.
"""

import argparse
import json
import os
import subprocess
import sys
import urllib.request
from datetime import date
from pathlib import Path
from textwrap import dedent

SECONDBRAIN_PEOPLE = Path("/Users/debra/SecondBrain/People")
PHOTOS_DIR = SECONDBRAIN_PEOPLE / "photos"
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASS = "secondbrain2026"
GOG_ACCOUNT = "alexander.o.abell@gmail.com"

PERSON_SCHEMA = {
    # Required
    "name": str,                    # "Jane Smith"
    # Optional — include whatever was found
    "phone": str,                   # "+16155551234"
    "email": str,                   # "jane@example.com"
    "org": str,                     # "ORNL"
    "title": str,                   # "Research Scientist"
    "location": str,                # "Oak Ridge, TN"
    "relationship": str,            # "Met at Techstars 2019"
    "relationship_type": str,       # "COLLEAGUE_OF"
    "relationship_target": str,     # "Alex Abell" (default)
    "twitter": str,                 # "@janesmith"
    "linkedin": str,                # "https://linkedin.com/in/janesmith"
    "instagram": str,               # "@janesmith"
    "photo_url": str,               # URL to download, or None
    "photo_confidence": str,        # "high" | "medium" | "low" | "none"
    "bio": str,                     # 2-3 sentence narrative
    "background": str,              # Career arc paragraph
    "notes": str,                   # Misc notes
    "tags": list,                   # ["person", "academic"]
    "articles": list,               # [{"title": ..., "url": ..., "summary": ..., "year": ...}]
    "publications": list,           # [{"title": ..., "url": ..., "journal": ..., "year": ..., "summary": ...}]
    "ventures": list,               # [{"company": ..., "year": ..., "description": ..., "raised": ..., "cofounders": [...]}]
    "collaborators": list,          # [{"name": ..., "org": ..., "papers": 3}]
    "extra_edges": list,            # [{"type": "WORKS_AT", "target": "ORNL", "target_type": "Organization"}]
}


def run(cmd: str, dry_run: bool = False) -> tuple[int, str, str]:
    """Run a shell command. Returns (returncode, stdout, stderr)."""
    if dry_run:
        print(f"[DRY RUN] {cmd}")
        return 0, "", ""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr


def safe_filename(name: str) -> str:
    """Convert 'Jane Smith' to 'JaneSmith'."""
    return name.replace(" ", "").replace("'", "").replace("-", "")


def download_photo(person: dict, dry_run: bool = False) -> str | None:
    """Download photo if confidence is high or medium. Returns local path or None."""
    url = person.get("photo_url")
    confidence = person.get("photo_confidence", "none")

    if not url or confidence in ("low", "none"):
        print(f"  Photo: skipped (confidence={confidence})")
        return None

    PHOTOS_DIR.mkdir(parents=True, exist_ok=True)
    filename = safe_filename(person["name"]) + ".jpg"
    dest = PHOTOS_DIR / filename

    if dry_run:
        print(f"  [DRY RUN] Would download photo → {dest}")
        return str(dest.relative_to(SECONDBRAIN_PEOPLE))

    try:
        rc, _, _ = run(f'curl -sL -o "{dest}" "{url}"')
        if rc == 0 and dest.exists() and dest.stat().st_size > 1000:
            print(f"  Photo: saved → {dest} (confidence={confidence})")
            return str(dest.relative_to(SECONDBRAIN_PEOPLE))
        else:
            print(f"  Photo: download failed or file too small")
            dest.unlink(missing_ok=True)
            return None
    except Exception as e:
        print(f"  Photo: error — {e}")
        return None


def generate_markdown(person: dict, photo_rel_path: str | None) -> str:
    """Generate the SecondBrain People markdown content."""
    today = date.today().isoformat()
    name = person["name"]
    tags = person.get("tags", ["person"])
    if "person" not in tags:
        tags = ["person"] + tags

    frontmatter_lines = [
        "---",
        f"name: {name}",
        "aliases: []",
        f"photo: {photo_rel_path or 'none'}",
        f"phone: \"{person.get('phone', '')}\"",
        f"email: \"{person.get('email', '')}\"",
        f"org: \"{person.get('org', '')}\"",
        f"title: \"{person.get('title', '')}\"",
        f"location: \"{person.get('location', '')}\"",
        f"relationship: \"{person.get('relationship', '')}\"",
        f"relationship_type: {person.get('relationship_type', 'FRIEND_OF')}",
        f"twitter: \"{person.get('twitter', '')}\"",
        f"linkedin: \"{person.get('linkedin', '')}\"",
        f"instagram: \"{person.get('instagram', '')}\"",
        f"tags: [{', '.join(tags)}]",
        f"created: {today}",
        f"updated: {today}",
        "---",
    ]
    frontmatter = "\n".join(frontmatter_lines)

    sections = [f"# {name}\n"]

    # Bio
    if person.get("bio"):
        sections.append(f"## Who They Are\n\n{person['bio']}\n")

    # Connection to Alex
    if person.get("relationship"):
        sections.append(f"## Connection to Alex\n\n{person['relationship']}\n")

    # Background
    if person.get("background"):
        sections.append(f"## Professional Background\n\n{person['background']}\n")

    # Online presence
    links = []
    if person.get("linkedin"):
        links.append(f"- LinkedIn: {person['linkedin']}")
    if person.get("twitter"):
        links.append(f"- Twitter: {person['twitter']}")
    if person.get("instagram"):
        links.append(f"- Instagram: {person['instagram']}")
    if links:
        sections.append("## Online Presence\n\n" + "\n".join(links) + "\n")

    # Articles
    articles = person.get("articles", [])
    if articles:
        lines = ["## Articles & Interviews\n"]
        for a in articles:
            title = a.get("title", "Untitled")
            url = a.get("url", "")
            summary = a.get("summary", "")
            year = a.get("year", "")
            prefix = "Podcast: " if a.get("type") == "podcast" else ""
            lines.append(f"- {prefix}[{title}]({url}) — {summary} ({year})")
        sections.append("\n".join(lines) + "\n")

    # Publications (academic)
    pubs = person.get("publications", [])
    if pubs:
        lines = ["## Research Publications\n"]
        for p in pubs:
            title = p.get("title", "Untitled")
            url = p.get("url", "")
            journal = p.get("journal", "")
            year = p.get("year", "")
            summary = p.get("summary", "")
            lines.append(f"- [{title}]({url}) — *{journal}*, {year}. {summary}")
        h_index = person.get("h_index")
        citations = person.get("citations")
        if h_index or citations:
            lines.append(f"\nh-index: {h_index or 'N/A'} | Citations: {citations or 'N/A'}")
        sections.append("\n".join(lines) + "\n")

    # Ventures (entrepreneur)
    ventures = person.get("ventures", [])
    if ventures:
        lines = ["## Ventures\n"]
        for v in ventures:
            company = v.get("company", "")
            year = v.get("year", "")
            description = v.get("description", "")
            raised = v.get("raised", "")
            cofounders = v.get("cofounders", [])
            lines.append(f"- **{company}** ({year}–present) — {description}")
            if raised:
                lines.append(f"  - Raised: {raised}")
            if cofounders:
                lines.append(f"  - Co-founders: {', '.join(cofounders)}")
        sections.append("\n".join(lines) + "\n")

    # Collaborators (academic)
    collabs = person.get("collaborators", [])
    if collabs:
        lines = ["## Collaborators\n"]
        for c in collabs:
            cname = c.get("name", "")
            org = c.get("org", "")
            papers = c.get("papers", "")
            paper_str = f" — {papers} co-authored paper(s)" if papers else ""
            lines.append(f"- {cname} ({org}){paper_str}")
        sections.append("\n".join(lines) + "\n")

    # Wrinkles placeholder
    sections.append("## Wrinkles\n\n*(Graph relationships — auto-populated from Neo4j)*\n\n")

    # Notes
    if person.get("notes"):
        sections.append(f"## Notes\n\n{person['notes']}\n")

    body = "\n".join(sections)
    return f"{frontmatter}\n\n{body}"


def write_markdown(person: dict, photo_rel_path: str | None, dry_run: bool = False) -> Path:
    """Write SecondBrain markdown file."""
    SECONDBRAIN_PEOPLE.mkdir(parents=True, exist_ok=True)
    filename = safe_filename(person["name"]) + ".md"
    dest = SECONDBRAIN_PEOPLE / filename
    content = generate_markdown(person, photo_rel_path)

    if dry_run:
        print(f"  [DRY RUN] Would write markdown → {dest}")
        print("  Preview (first 20 lines):")
        for line in content.split("\n")[:20]:
            print(f"    {line}")
        return dest

    dest.write_text(content, encoding="utf-8")
    print(f"  SecondBrain: wrote → {dest}")
    return dest


def write_neo4j(person: dict, dry_run: bool = False):
    """Write Person node and relationship edges to Neo4j."""
    name = person["name"]
    target = person.get("relationship_target", "Alex Abell")
    rel_type = person.get("relationship_type", "FRIEND_OF")
    relationship_context = person.get("relationship", "")
    today = date.today().isoformat()

    # Escape single quotes for Cypher
    def esc(s: str) -> str:
        return (s or "").replace("'", "\\'")

    cypher_parts = [
        f"MERGE (p:Person {{name: '{esc(name)}'}})",
        f"SET p.phone = '{esc(person.get('phone', ''))}',",
        f"    p.email = '{esc(person.get('email', ''))}',",
        f"    p.org = '{esc(person.get('org', ''))}',",
        f"    p.title = '{esc(person.get('title', ''))}',",
        f"    p.location = '{esc(person.get('location', ''))}',",
        f"    p.linkedin = '{esc(person.get('linkedin', ''))}',",
        f"    p.twitter = '{esc(person.get('twitter', ''))}',",
        f"    p.updated = date('{today}')",
        "",
        f"MERGE (target:Person {{name: '{esc(target)}'}})",
        f"MERGE (p)-[:{rel_type} {{context: '{esc(relationship_context)}'}}]->(target)",
    ]

    # Org node
    if person.get("org"):
        cypher_parts += [
            "",
            f"MERGE (org:Organization {{name: '{esc(person['org'])}'}})",
            f"MERGE (p)-[:WORKS_AT]->(org)",
        ]

    # Extra edges
    for edge in person.get("extra_edges", []):
        edge_type = edge.get("type", "RELATED_TO")
        tgt_name = esc(edge.get("target", ""))
        tgt_label = edge.get("target_type", "Person")
        cypher_parts += [
            "",
            f"MERGE (xtgt:{tgt_label} {{name: '{tgt_name}'}})",
            f"MERGE (p)-[:{edge_type}]->(xtgt)",
        ]

    # Collaborator edges
    for c in person.get("collaborators", []):
        cname = esc(c.get("name", ""))
        corg = esc(c.get("org", ""))
        papers_prop = c.get("papers", 1)
        cypher_parts += [
            "",
            f"MERGE (co:Person {{name: '{cname}'}})",
            f"SET co.org = '{corg}'",
            f"MERGE (p)-[:COLLABORATES_WITH {{papers: {papers_prop}}}]->(co)",
        ]

    # Co-founders
    for v in person.get("ventures", []):
        co_name = esc(v.get("company", ""))
        v_year = v.get("year", "")
        if co_name:
            cypher_parts += [
                "",
                f"MERGE (comp:Organization {{name: '{co_name}'}})",
                f"SET comp.type = 'startup', comp.founded = {v_year or 'null'}",
                f"MERGE (p)-[:FOUNDED {{year: {v_year or 'null'}}}]->(comp)",
            ]
        for cf in v.get("cofounders", []):
            cf_name = esc(cf)
            cypher_parts += [
                f"MERGE (cf:Person {{name: '{cf_name}'}})",
                f"MERGE (cf)-[:CO_FOUNDED]->(comp)",
                f"MERGE (p)-[:CO_FOUNDED_WITH]->(cf)",
            ]

    cypher = "\n".join(cypher_parts)

    cmd = f"""cypher-shell -a {NEO4J_URI} -u {NEO4J_USER} -p {NEO4J_PASS} "{cypher.replace('"', chr(39))}" """
    # Use heredoc for safety with complex cypher
    heredoc_cmd = f"""cypher-shell -a {NEO4J_URI} -u {NEO4J_USER} -p {NEO4J_PASS} << 'CYPHER'\n{cypher}\nCYPHER"""

    if dry_run:
        print("  [DRY RUN] Would run Cypher:")
        for line in cypher.split("\n")[:30]:
            print(f"    {line}")
        return

    rc, stdout, stderr = run(heredoc_cmd)
    if rc == 0:
        print(f"  Neo4j: Person node written + edges created")
    else:
        print(f"  Neo4j: ERROR (rc={rc})")
        if stderr:
            print(f"    {stderr[:500]}")


def check_or_create_contact(person: dict, photo_local: str | None, dry_run: bool = False):
    """Create or update Google Contact via gog CLI."""
    name = person["name"]

    # Check if exists
    rc, stdout, _ = run(f'gog contacts list --account {GOG_ACCOUNT} --query "{name}" --format json 2>/dev/null')
    exists = rc == 0 and name.lower() in stdout.lower()

    verb = "update" if exists else "create"

    args = [f'gog contacts {verb}', f'--account {GOG_ACCOUNT}']
    if exists:
        # Try to extract contact ID from listing (gog-specific, may vary)
        args.append(f'--name "{name}"')  # used as lookup key for update

    args.append(f'--name "{name}"')

    if person.get("phone"):
        args.append(f'--phone "{person["phone"]}"')
    if person.get("email"):
        args.append(f'--email "{person["email"]}"')
    if person.get("org"):
        args.append(f'--org "{person["org"]}"')
    if person.get("title"):
        args.append(f'--title "{person["title"]}"')

    # Build notes
    notes_parts = []
    if person.get("relationship"):
        notes_parts.append(f"Relationship to Alex: {person['relationship']}")
    if person.get("linkedin"):
        notes_parts.append(f"LinkedIn: {person['linkedin']}")
    if person.get("twitter"):
        notes_parts.append(f"Twitter: {person['twitter']}")
    notes_parts.append(f"Enriched by people-intel on {date.today().isoformat()}")

    if notes_parts:
        notes = " | ".join(notes_parts)
        args.append(f'--notes "{notes}"')

    cmd = " ".join(args)

    if dry_run:
        print(f"  [DRY RUN] Would run: {cmd}")
        return

    rc, stdout, stderr = run(cmd)
    if rc == 0:
        print(f"  Google Contact: {verb}d ✓")
    else:
        print(f"  Google Contact: {verb} failed (rc={rc}): {stderr[:200]}")


def enrich(person_data: dict, dry_run: bool = False):
    """Main enrichment routine."""
    name = person_data["name"]
    print(f"\n{'='*60}")
    print(f"Enriching: {name}")
    print(f"{'='*60}")

    # 1. Photo
    print("\n[1/4] Photo")
    photo_path = download_photo(person_data, dry_run)

    # 2. SecondBrain markdown
    print("\n[2/4] SecondBrain Markdown")
    md_path = write_markdown(person_data, photo_path, dry_run)

    # 3. Neo4j
    print("\n[3/4] Neo4j")
    write_neo4j(person_data, dry_run)

    # 4. Google Contact
    print("\n[4/4] Google Contact")
    check_or_create_contact(person_data, photo_path, dry_run)

    print(f"\n✅ Done: {name}")
    print(f"   SecondBrain: {md_path}")
    print(f"   Photo: {photo_path or 'none'}")


def main():
    parser = argparse.ArgumentParser(description="Enrich a person's profile across all three stores.")
    parser.add_argument("--data", required=True, help="Path to JSON file with person data")
    parser.add_argument("--dry-run", action="store_true", help="Show what would happen without writing")
    args = parser.parse_args()

    data_path = Path(args.data)
    if not data_path.exists():
        print(f"ERROR: {data_path} not found", file=sys.stderr)
        sys.exit(1)

    with open(data_path) as f:
        person = json.load(f)

    if "name" not in person:
        print("ERROR: person data must include 'name'", file=sys.stderr)
        sys.exit(1)

    enrich(person, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
