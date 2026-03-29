#!/usr/bin/env python3
"""
Vault Indexer — Generate a fast-lookup index of the SecondBrain vault.
Creates:
  1. vault-index.json — machine-readable index with metadata
  2. VAULT-INDEX.md — human-readable Obsidian note

Usage:
    python3 vault_indexer.py
    python3 vault_indexer.py --output-json /path/to/index.json
"""

import os
import re
import sys
import json
import time
from datetime import datetime, date
from collections import defaultdict

VAULT = "/Users/debra/SecondBrain"
SKIP_DIRS = {"_archived", ".obsidian", "photos", ".git", "node_modules", "imazing-import"}

INDEX_JSON = os.path.join(VAULT, ".vault-index.json")
INDEX_MD = os.path.join(VAULT, "MOCs", "VAULT-INDEX.md")


def get_frontmatter(content):
    """Extract frontmatter dict from markdown content."""
    if content.startswith("---"):
        end = content.find("\n---", 3)
        if end != -1:
            fm_str = content[4:end]
            fm = {}
            for line in fm_str.split("\n"):
                if ":" in line:
                    k, _, v = line.partition(":")
                    fm[k.strip()] = v.strip().strip('"').strip("'")
            return fm
    return {}


def build_vault_index():
    """Scan vault and build comprehensive index."""
    index = {
        "generated": datetime.now().isoformat(),
        "vault": VAULT,
        "total_files": 0,
        "total_size_bytes": 0,
        "folders": {},
        "people": [],
        "projects": [],
        "concepts": [],
        "conversations": [],
        "recent_reflections": [],
        "all_files": [],
    }
    
    folder_stats = defaultdict(lambda: {"count": 0, "size": 0})
    
    for root, dirs, files in os.walk(VAULT):
        dirs[:] = sorted([d for d in dirs if d not in SKIP_DIRS])
        rel_root = root.replace(VAULT, "").lstrip("/")
        top_folder = rel_root.split("/")[0] if rel_root else "ROOT"
        
        for f in files:
            if not f.endswith(".md"):
                continue
            
            fp = os.path.join(root, f)
            size = os.path.getsize(fp)
            mtime = os.path.getmtime(fp)
            stem = os.path.splitext(f)[0]
            rel_path = fp.replace(VAULT + "/", "")
            
            index["total_files"] += 1
            index["total_size_bytes"] += size
            folder_stats[top_folder]["count"] += 1
            folder_stats[top_folder]["size"] += size
            
            # Basic file entry
            entry = {
                "name": stem,
                "path": rel_path,
                "folder": top_folder,
                "size": size,
                "mtime": mtime,
            }
            
            # Read frontmatter for key files
            if size < 10 * 1024:  # only read small files for FM
                try:
                    with open(fp, "r", encoding="utf-8", errors="ignore") as fh:
                        content = fh.read(2048)
                    fm = get_frontmatter(content)
                    if fm:
                        entry["frontmatter"] = fm
                except Exception:
                    pass
            
            index["all_files"].append(entry)
            
            # Categorize
            if top_folder == "People":
                fm = entry.get("frontmatter", {})
                index["people"].append({
                    "name": fm.get("name", stem),
                    "path": rel_path,
                    "job_title": fm.get("job_title", ""),
                    "size": size,
                })
            elif top_folder == "Projects":
                index["projects"].append({"name": stem, "path": rel_path, "size": size})
            elif top_folder == "Concepts":
                index["concepts"].append({"name": stem, "path": rel_path, "size": size})
            elif top_folder == "Conversations":
                index["conversations"].append({
                    "name": stem, "path": rel_path, "size": size, "mtime": mtime
                })
            elif top_folder == "Reflections":
                if "/Daily/" in fp:
                    index["recent_reflections"].append({
                        "name": stem, "path": rel_path, "mtime": mtime
                    })
    
    # Sort and limit
    index["people"].sort(key=lambda x: x["name"])
    index["recent_reflections"].sort(key=lambda x: -x["mtime"])
    index["recent_reflections"] = index["recent_reflections"][:30]
    index["conversations"].sort(key=lambda x: -x["mtime"])
    
    # Folder summary
    for folder, stats in sorted(folder_stats.items(), key=lambda x: -x[1]["count"]):
        index["folders"][folder] = {
            "count": stats["count"],
            "size_kb": round(stats["size"] / 1024, 1),
        }
    
    return index


def write_json_index(index):
    """Write machine-readable JSON index."""
    # Write a compact version (without all_files details for size)
    compact = {k: v for k, v in index.items() if k != "all_files"}
    compact["file_count"] = len(index["all_files"])
    
    with open(INDEX_JSON, "w") as f:
        json.dump(compact, f, indent=2, default=str)
    print(f"JSON index written to: {INDEX_JSON}", flush=True)


def write_md_index(index):
    """Write human-readable Obsidian index note."""
    os.makedirs(os.path.dirname(INDEX_MD), exist_ok=True)
    
    today = date.today().isoformat()
    total_mb = index["total_size_bytes"] / 1024 / 1024
    
    # Folder table
    folder_rows = ""
    for folder, stats in index["folders"].items():
        folder_rows += f"| {folder} | {stats['count']} | {stats['size_kb']}KB |\n"
    
    # Recent reflections
    reflections_list = ""
    for r in index["recent_reflections"][:10]:
        reflections_list += f"- [[{r['name']}]]\n"
    
    # Projects
    projects_list = "\n".join([f"- [[{p['name']}]]" for p in index["projects"]]) or "- None"
    
    # Concepts  
    concepts_list = "\n".join([f"- [[{c['name']}]]" for c in index["concepts"]]) or "- None"
    
    content = f"""---
type: vault-index
generated: {today}
tags: [moc, index, meta]
---

# 🗂️ Vault Index

*Auto-generated by vault_indexer.py on {today}*

## Stats

| Metric | Value |
|--------|-------|
| Total Files | {index['total_files']} |
| Total Size | {total_mb:.1f} MB |
| Generated | {index['generated'][:19]} |

## Folder Breakdown

| Folder | Files | Size |
|--------|-------|------|
{folder_rows}

## Projects

{projects_list}

## Concepts

{concepts_list}

## Recent Reflections

{reflections_list}

## Navigation

- [[People/]] — {index['folders'].get('People', {}).get('count', 0)} people
- [[Messages/]] — {index['folders'].get('Messages', {}).get('count', 0)} message threads
- [[Social/]] — {index['folders'].get('Social', {}).get('count', 0)} social profiles
- [[Conversations/]] — {index['folders'].get('Conversations', {}).get('count', 0)} LLM conversation exports
- [[Documents/]] — {index['folders'].get('Documents', {}).get('count', 0)} documents
- [[Concepts/]] — {index['folders'].get('Concepts', {}).get('count', 0)} concept cards
- [[GTD/]] — GTD inbox and actions
- [[Reflections/]] — Daily notes and reports

---
*Index is rebuilt automatically. Edit the indexer to change what appears here.*
"""
    
    with open(INDEX_MD, "w") as f:
        f.write(content)
    print(f"Markdown index written to: {INDEX_MD}", flush=True)


def main():
    print("📚 Vault Indexer starting...", flush=True)
    t0 = time.time()
    
    index = build_vault_index()
    
    write_json_index(index)
    write_md_index(index)
    
    elapsed = time.time() - t0
    print(f"\n📚 Vault index complete in {elapsed:.1f}s", flush=True)
    print(f"   Total files: {index['total_files']}", flush=True)
    print(f"   Total size:  {index['total_size_bytes']/1024/1024:.1f} MB", flush=True)
    print(f"   People: {len(index['people'])}", flush=True)
    print(f"   Projects: {len(index['projects'])}", flush=True)
    print(f"   Concepts: {len(index['concepts'])}", flush=True)
    print(f"   Conversations: {len(index['conversations'])}", flush=True)
    
    # Print folder summary
    print("\n   Folder breakdown:", flush=True)
    for folder, stats in index["folders"].items():
        print(f"   {folder:<20} {stats['count']:>5} files  {stats['size_kb']:>8}KB", flush=True)


if __name__ == "__main__":
    main()
