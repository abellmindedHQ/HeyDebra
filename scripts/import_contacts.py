#!/usr/bin/env python3
"""Import Google Contacts into Neo4j + Obsidian Second Brain."""

import json
import os
import subprocess
import sys
import time
from pathlib import Path

ACCOUNT = "alexander.o.abell@gmail.com"
PEOPLE_DIR = Path("/Users/debra/SecondBrain/People")
NEO4J_USER = "neo4j"
NEO4J_PASS = "secondbrain2026"
SKIP_NAMES = {"Sallijo Archer", "Dr. Chelsea Rothschild", "Chelsea Rothschild",
              "Hannah", "Avie", "Alex Brodsky", "Alex Abell"}
# Also skip if the file already exists (by filename)
SKIP_FILES = {f.stem for f in PEOPLE_DIR.glob("*.md")}

PAGE_SIZE = 500


def run_gog(args):
    """Run a gog command and return parsed JSON."""
    cmd = ["gog"] + args + ["--account", ACCOUNT, "--json", "--no-input"]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if result.returncode != 0:
        print(f"  ERROR: {' '.join(cmd)}: {result.stderr[:200]}", file=sys.stderr)
        return None
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        print(f"  JSON parse error for: {' '.join(cmd)}", file=sys.stderr)
        return None


def get_all_contacts():
    """Paginate through all contacts, returning list of resource names."""
    contacts = []
    page_token = None
    while True:
        args = ["contacts", "list", "--max", str(PAGE_SIZE)]
        if page_token:
            args += ["--page", page_token]
        data = run_gog(args)
        if not data:
            break
        batch = data.get("contacts", [])
        contacts.extend(batch)
        print(f"  Fetched {len(batch)} contacts (total: {len(contacts)})")
        page_token = data.get("nextPageToken")
        if not page_token or len(batch) == 0:
            break
        time.sleep(0.2)
    return contacts


def get_contact_details(resource_name):
    """Get full details for a single contact."""
    data = run_gog(["contacts", "get", resource_name])
    if data:
        return data.get("contact", data)
    return None


def extract_fields(contact):
    """Extract useful fields from a contact detail response."""
    info = {}

    # Name
    names = contact.get("names", [])
    if names:
        info["name"] = names[0].get("displayName", "")
        info["givenName"] = names[0].get("givenName", "")
        info["familyName"] = names[0].get("familyName", "")
    else:
        info["name"] = ""

    # Emails
    emails = contact.get("emailAddresses", [])
    info["emails"] = [e.get("value", "") for e in emails if e.get("value")]

    # Phones
    phones = contact.get("phoneNumbers", [])
    info["phones"] = [p.get("value", "") for p in phones if p.get("value")]

    # Organizations
    orgs = contact.get("organizations", [])
    if orgs:
        info["organization"] = orgs[0].get("name", "")
        info["title"] = orgs[0].get("title", "")
    else:
        info["organization"] = ""
        info["title"] = ""

    # URLs
    urls = contact.get("urls", [])
    info["urls"] = []
    for u in urls:
        url_type = u.get("type", u.get("formattedType", ""))
        url_val = u.get("value", "")
        if url_val:
            info["urls"].append({"type": url_type, "url": url_val})

    # Addresses
    addresses = contact.get("addresses", [])
    info["addresses"] = []
    for a in addresses:
        formatted = a.get("formattedValue", "")
        if formatted:
            info["addresses"].append(formatted)

    # Birthdays
    bdays = contact.get("birthdays", [])
    if bdays:
        date = bdays[0].get("date", {})
        if date:
            parts = []
            if date.get("year"):
                parts.append(str(date["year"]))
            if date.get("month"):
                parts.append(f"{date['month']:02d}")
            if date.get("day"):
                parts.append(f"{date['day']:02d}")
            info["birthday"] = "-".join(parts)

    # Notes/bio
    bios = contact.get("biographies", [])
    if bios:
        info["notes"] = bios[0].get("value", "")

    info["resourceName"] = contact.get("resourceName", "")

    return info


def create_obsidian_note(info):
    """Create an Obsidian markdown note for a person."""
    name = info["name"].strip()
    if not name:
        return False

    # Skip protected names
    if name in SKIP_NAMES:
        return False

    # Skip if file exists
    if name in SKIP_FILES:
        return False

    filepath = PEOPLE_DIR / f"{name}.md"
    if filepath.exists():
        return False

    lines = [f"# {name}", ""]

    # Frontmatter-style properties
    lines.append("## Contact Info")
    if info.get("emails"):
        for e in info["emails"]:
            lines.append(f"- **Email:** {e}")
    if info.get("phones"):
        for p in info["phones"]:
            lines.append(f"- **Phone:** {p}")
    if info.get("organization"):
        lines.append(f"- **Organization:** {info['organization']}")
    if info.get("title"):
        lines.append(f"- **Title:** {info['title']}")
    if info.get("birthday"):
        lines.append(f"- **Birthday:** {info['birthday']}")
    if info.get("addresses"):
        for a in info["addresses"]:
            lines.append(f"- **Address:** {a}")
    if info.get("urls"):
        for u in info["urls"]:
            lines.append(f"- **{u['type']}:** {u['url']}")

    lines.append("")
    lines.append("## Notes")
    if info.get("notes"):
        lines.append(info["notes"])
    else:
        lines.append("_Imported from Google Contacts_")
    lines.append("")

    filepath.write_text("\n".join(lines), encoding="utf-8")
    return True


def create_neo4j_node(info):
    """Create a Person node in Neo4j via cypher-shell."""
    name = info["name"].strip()
    if not name:
        return False

    # Build properties
    props = {"name": name}
    if info.get("givenName"):
        props["givenName"] = info["givenName"]
    if info.get("familyName"):
        props["familyName"] = info["familyName"]
    if info.get("emails"):
        props["email"] = info["emails"][0]
        if len(info["emails"]) > 1:
            props["emails"] = info["emails"]
    if info.get("phones"):
        props["phone"] = info["phones"][0]
        if len(info["phones"]) > 1:
            props["phones"] = info["phones"]
    if info.get("organization"):
        props["organization"] = info["organization"]
    if info.get("title"):
        props["title"] = info["title"]
    if info.get("birthday"):
        props["birthday"] = info["birthday"]
    if info.get("resourceName"):
        props["googleContactId"] = info["resourceName"]

    props["source"] = "google_contacts"

    # Build Cypher MERGE statement
    # Use name as the merge key, set other properties
    set_clauses = []
    for k, v in props.items():
        if k == "name":
            continue
        if isinstance(v, list):
            escaped = json.dumps(v)
            set_clauses.append(f"p.{k} = {escaped}")
        else:
            escaped = v.replace("\\", "\\\\").replace("'", "\\'")
            set_clauses.append(f"p.{k} = '{escaped}'")

    name_escaped = name.replace("\\", "\\\\").replace("'", "\\'")
    cypher = f"MERGE (p:Person {{name: '{name_escaped}'}}) ON CREATE SET {', '.join(set_clauses)}"

    try:
        result = subprocess.run(
            ["cypher-shell", "-u", NEO4J_USER, "-p", NEO4J_PASS, cypher],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode != 0:
            print(f"  Neo4j error for {name}: {result.stderr[:200]}", file=sys.stderr)
            return False
        return True
    except Exception as e:
        print(f"  Neo4j exception for {name}: {e}", file=sys.stderr)
        return False


def main():
    print("=== Google Contacts → Second Brain Import ===")
    print()

    # Step 1: Get all contacts (basic list)
    print("Step 1: Fetching all contacts...")
    contacts = get_all_contacts()
    print(f"  Total contacts found: {len(contacts)}")
    print()

    # Step 2: Get details and import each
    print("Step 2: Fetching details and importing...")
    imported_notes = 0
    imported_neo4j = 0
    skipped = 0
    errors = 0

    for i, c in enumerate(contacts):
        resource = c.get("resource", "")
        basic_name = c.get("name", "unknown")

        if not resource:
            errors += 1
            continue

        # Quick skip check on basic name
        if basic_name in SKIP_NAMES or basic_name in SKIP_FILES:
            skipped += 1
            continue

        # Get full details
        detail = get_contact_details(resource)
        if not detail:
            errors += 1
            continue

        info = extract_fields(detail)
        if not info["name"]:
            skipped += 1
            continue

        # Re-check after getting full name
        if info["name"] in SKIP_NAMES or info["name"] in SKIP_FILES:
            skipped += 1
            continue

        # Create Obsidian note
        note_created = create_obsidian_note(info)
        if note_created:
            imported_notes += 1

        # Create Neo4j node
        neo_created = create_neo4j_node(info)
        if neo_created:
            imported_neo4j += 1

        if (i + 1) % 50 == 0:
            print(f"  Processed {i + 1}/{len(contacts)}...")

        # Small delay to not hammer the API
        time.sleep(0.1)

    print()
    print("=== Import Complete ===")
    print(f"  Total contacts: {len(contacts)}")
    print(f"  Obsidian notes created: {imported_notes}")
    print(f"  Neo4j nodes created/merged: {imported_neo4j}")
    print(f"  Skipped (existing/protected): {skipped}")
    print(f"  Errors: {errors}")

    # Write summary for parent process
    summary = {
        "total": len(contacts),
        "notes_created": imported_notes,
        "neo4j_created": imported_neo4j,
        "skipped": skipped,
        "errors": errors
    }
    print()
    print(f"SUMMARY_JSON:{json.dumps(summary)}")


if __name__ == "__main__":
    main()
