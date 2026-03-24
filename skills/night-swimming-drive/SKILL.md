---
name: night-swimming-drive
description: Google Drive audit skill. Catalogs all files, identifies duplicates and near-duplicates, recommends folder organization, and generates an audit report. READ-ONLY — never moves or deletes anything without explicit user approval. Use when asked to "audit Drive", "find duplicates in Drive", "clean up Google Drive", "run night swimming drive", or as part of a nightly batch.
---

# night-swimming-drive

Audit Google Drive: catalog everything, find the mess, recommend fixes. **Does not touch files.** Alex decides what to move or delete.

---

## Inputs

- **Account** (default: `alexander.o.abell@gmail.com`): Google account
- **Report date** (default: today): YYYY-MM-DD for the output filename
- **Scope**: `all` (entire Drive) | `root` (root folder only) | folder ID/name

---

## Config

```
Tool:    gog CLI (Google Workspace CLI)
Access:  Google Drive read-only (metadata + list)
Output:  /Users/debra/SecondBrain/Documents/drive-audit-YYYY-MM-DD.md
```

**🚨 HARD RULE: NO WRITES TO DRIVE**
This skill ONLY reads. It does not move, rename, delete, share, or modify any Drive file.
If you find yourself about to call `gog drive move` or `gog drive delete` — STOP.
All recommendations go in the report for Alex to act on manually.

---

## Workflow

### Step 1 — Catalog All Files

```bash
# List all files with metadata
gog drive list --account alexander.o.abell@gmail.com \
  --fields "id,name,mimeType,size,createdTime,modifiedTime,parents,owners,trashed" \
  --limit 1000 \
  --format json

# Paginate with --page-token if > 1000 files
```

Collect into a working dataset:
- File ID, name, MIME type, size (bytes), created date, modified date, parent folder ID, in trash (yes/no)

### Step 2 — Build Folder Tree

```bash
# List all folders specifically
gog drive list --account alexander.o.abell@gmail.com \
  --mime application/vnd.google-apps.folder \
  --format json
```

Build a tree: folder ID → folder name → parent folder ID → depth level.
Resolve file parent IDs to folder names for readable paths.

### Step 3 — Identify Duplicates

**Exact duplicates** (same name + same size):
- Group files by `(name, size)` pairs
- Any group with 2+ members = duplicate set

**Near-duplicates** (same name, different size or different location):
- Group by normalized name (lowercase, strip version suffixes like " (1)", " copy", " - Copy")
- Flag groups where same base name appears in multiple folders

**Version clutter** (files with " (1)", " (2)", " - Copy", "final", "final2", "FINAL-v3" etc.):
- Regex match on names: `\s*\(\d+\)$`, `\s*-\s*copy`, `final\d*`, `v\d+`
- List all version clusters

**Large files** (worth knowing about):
- Files > 50MB: list with size and location
- Files > 500MB: highlight in report

**Orphaned files** (in root or unknown parent):
- Files whose parent resolves to root "My Drive" but feel misplaced
- Google Docs/Sheets/Slides outside any named folder

### Step 4 — Analyze Folder Structure

**Identify disorganization signals:**
- Files in root with no folder (should be organized)
- Folders with only 1 file (might belong elsewhere)
- Deeply nested folders (> 4 levels deep)
- Folders with 50+ files (might need sub-organization)
- "Untitled" folders or folders named with dates (ad hoc creation)
- Multiple folders that seem to overlap in purpose

**Recommend a folder structure** based on what you find:
```
Suggested top-level structure:
📁 Work/
   📁 ORNL/
   📁 Projects/
📁 Personal/
   📁 Finance/
   📁 Health/
📁 Archive/
📁 Media/
```
Tailor the recommendation to what actually exists in Alex's Drive.

### Step 5 — Analyze by Type

Count files by MIME type:
- Google Docs / Sheets / Slides / Forms
- PDFs
- Images (jpg, png, gif, webp, heic)
- Videos
- Archives (zip, tar, etc.)
- Unknown / misc

Flag: any media files that might be better stored locally or in Photos vs Drive.

### Step 6 — Generate Report

Save to `/Users/debra/SecondBrain/Documents/drive-audit-YYYY-MM-DD.md`:

```markdown
---
date: YYYY-MM-DD
type: drive-audit
account: alexander.o.abell@gmail.com
---

# 📁 Google Drive Audit — YYYY-MM-DD

**Total files:** N | **Total size:** X GB | **Folders:** N | **Trashed (not emptied):** N

---

## 🔢 Files by Type

| Type | Count | Total Size |
|------|-------|-----------|
| Google Docs | N | — |
| Google Sheets | N | — |
| PDFs | N | X MB |
| Images | N | X MB |
| Videos | N | X MB |
| Other | N | X MB |

---

## 🔴 Exact Duplicates (N sets)

These files appear to be identical (same name + same size in multiple locations):

| File Name | Size | Copies | Locations |
|-----------|------|--------|-----------|
| [filename] | [size] | N | [folder A], [folder B] |

**Suggested action:** Keep one, trash the others. Review locations first.

---

## 🟠 Near-Duplicates / Version Clutter (N sets)

| Base Name | Versions Found | Locations |
|-----------|---------------|-----------|
| [name] | "doc", "doc (1)", "doc - Copy" | [folders] |

---

## 🟡 Large Files (> 50MB)

| File | Size | Location | Last Modified |
|------|------|----------|--------------|
| [filename] | [size] | [folder] | [date] |

---

## 📂 Folder Structure Analysis

### Current Structure Issues

- [Describe what's messy: files in root, overlapping folders, etc.]
- [List folders with only 1 file]
- [List deeply nested folders]

### Suggested Reorganization

```
[Proposed folder tree]
```

**Files to move:**

| File | Current Location | Suggested Destination |
|------|-----------------|----------------------|
| [file] | Root | [suggested folder] |

*⚠️ These are suggestions only. Nothing has been moved.*

---

## 🗑️ Trash (Not Emptied)

N files in trash using [X MB]. Consider emptying if you're done with them.

---

## 📊 Summary Stats

- Duplicate sets: N (potential space savings: X MB)
- Files in root with no folder: N
- Version clutter sets: N
- Orphaned/misplaced files: N

---

*Generated by night-swimming-drive skill — read-only audit, no files modified*
```

### Step 7 — Summary to User

```
📁 Drive audit complete — YYYY-MM-DD
- Total: N files, X GB
- Exact duplicates: N sets (save ~X MB)
- Version clutter: N sets
- Large files: N files over 50MB
- Root-level mess: N files with no folder
- Report: SecondBrain/Documents/drive-audit-YYYY-MM-DD.md
⚠️ Nothing was moved or deleted. All suggestions are in the report.
```

---

## Edge Cases

- **Shared files (not owned by Alex)**: Include in catalog but mark as "shared", don't include in size totals
- **Google Workspace files (Docs/Sheets)**: These have no "size" in bytes from the API — note as "N/A"
- **Very large Drive (> 5000 files)**: Process in batches, note in report that full catalog may be incomplete
- **gog rate limiting**: If API calls fail with 429, back off 30s and retry; don't crash
- **Files in shared drives**: Note separately if gog returns shared drive contents
