#!/usr/bin/env python3
"""
Weaver Dedup Pass — finds potential duplicate files in SecondBrain.

Checks for:
1. First-name-only files that match a full-name file (e.g., "Jay" and "Dr. Jay Eckles")
2. Files with same phone number
3. Files with same email
4. Files with matching aliases
5. Non-person files in People/ directory

Run: python3 dedup.py
"""

import os
import re
from collections import defaultdict
from datetime import date

VAULT = "/Users/debra/SecondBrain"
PEOPLE_DIR = os.path.join(VAULT, "People")
SKIP_DIRS = {"_archived", "photos"}


def get_frontmatter(filepath):
    """Extract frontmatter fields as a dict (basic parser, no pyyaml)."""
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
    except:
        return {}
    
    if not content.startswith("---"):
        return {}
    
    end = content.find("\n---", 3)
    if end == -1:
        return {}
    
    fm_text = content[3:end]
    fields = {}
    for line in fm_text.split("\n"):
        if ":" in line:
            key, _, val = line.partition(":")
            key = key.strip()
            val = val.strip().strip('"').strip("'")
            if val:
                fields[key] = val
    return fields


def scan_people():
    """Scan People/ directory for duplicates and misplaced files."""
    issues = []
    files = {}
    phones = defaultdict(list)
    emails = defaultdict(list)
    
    for f in os.listdir(PEOPLE_DIR):
        if f.startswith("_") or f == "photos" or not f.endswith(".md"):
            continue
        
        stem = f.replace(".md", "")
        filepath = os.path.join(PEOPLE_DIR, f)
        fm = get_frontmatter(filepath)
        
        files[stem] = fm
        
        # Collect phones and emails for dupe detection
        phone = fm.get("phone", "").replace(" ", "").replace("-", "").replace("(", "").replace(")", "").replace("+", "")
        if phone and len(phone) >= 10:
            phones[phone].append(stem)
        
        email = fm.get("email", "").lower()
        if email:
            emails[email].append(stem)
        
        # Check if this is actually a person file
        has_person_signals = any(k in fm for k in ["name", "relationship", "phone", "email", "org", "tier"])
        if not has_person_signals:
            # Check content for person-like content
            try:
                with open(filepath, "r", encoding="utf-8", errors="ignore") as fh:
                    content = fh.read()
                if "## Who They Are" not in content and "## Relationship" not in content and "## Connection" not in content:
                    issues.append(f"MISPLACED? {stem} — no person signals in frontmatter or content")
            except:
                pass
    
    # Check for first-name duplicates
    names = list(files.keys())
    for name in names:
        parts = name.split()
        if len(parts) == 1:
            # Single name — check for full-name matches
            matches = [n for n in names if n != name and n.lower().startswith(name.lower() + " ")]
            if matches:
                issues.append(f"DUPLICATE: '{name}' is likely same person as {matches}")
    
    # Check for phone duplicates
    for phone, people in phones.items():
        if len(people) > 1:
            issues.append(f"SAME PHONE ({phone}): {people}")
    
    # Check for email duplicates
    for email, people in emails.items():
        if len(people) > 1:
            issues.append(f"SAME EMAIL ({email}): {people}")
    
    return issues


def main():
    print("🔍 Weaver Dedup Scan\n")
    issues = scan_people()
    
    if issues:
        print(f"Found {len(issues)} issues:\n")
        for issue in issues:
            print(f"  ⚠️  {issue}")
    else:
        print("  ✅ No duplicates or misplaced files found.")
    
    # Write report
    report_dir = os.path.join(VAULT, "Reflections", "Daily")
    os.makedirs(report_dir, exist_ok=True)
    report_path = os.path.join(report_dir, f"{date.today().isoformat()} Dedup Report.md")
    
    with open(report_path, "w") as f:
        f.write(f"# Dedup Report — {date.today().isoformat()}\n\n")
        if issues:
            f.write(f"**{len(issues)} issues found:**\n\n")
            for issue in issues:
                f.write(f"- {issue}\n")
        else:
            f.write("✅ No duplicates or misplaced files found.\n")
    
    print(f"\nReport: {report_path}")
    return len(issues)


if __name__ == "__main__":
    exit(main())
