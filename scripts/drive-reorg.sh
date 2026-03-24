#!/bin/bash
# Google Drive Reorg - Batch Move Script
# Moves files from root into organized folders
# Account: alexander.o.abell@gmail.com
# Generated: 2026-03-23

ACCT="alexander.o.abell@gmail.com"
LOG="/Users/debra/SecondBrain/Documents/Google Drive Reorg Log.md"
MOVED=0
ERRORS=0

move_file() {
  local FILE_ID="$1"
  local FOLDER_ID="$2"
  local FILENAME="$3"
  local FOLDERNAME="$4"
  
  echo "Moving: $FILENAME → $FOLDERNAME"
  result=$(gog drive mv "$FILE_ID" --parent "$FOLDER_ID" --account "$ACCT" --force 2>&1)
  if [ $? -eq 0 ]; then
    echo "  ✅ Done"
    echo "Moved: $FILENAME → $FOLDERNAME ($FILE_ID → $FOLDER_ID)" >> "$LOG"
    MOVED=$((MOVED + 1))
  else
    echo "  ❌ Error: $result"
    echo "ERROR: $FILENAME → $FOLDERNAME ($FILE_ID → $FOLDER_ID) — $result" >> "$LOG"
    ERRORS=$((ERRORS + 1))
  fi
  sleep 1
}

echo "" >> "$LOG"
echo "## Phase 3: File Moves ($(date))" >> "$LOG"

# Get all root files as JSON and build move commands
echo "Fetching file list..."
FILES_JSON=$(gog drive ls --account "$ACCT" --json --max 500 --results-only 2>/dev/null)

# Parse and move using Python to match filenames to categories
python3 << 'PYEOF'
import json, subprocess, time, sys

acct = "alexander.o.abell@gmail.com"
log_path = "/Users/debra/SecondBrain/Documents/Google Drive Reorg Log.md"

# Folder IDs from the reorg
folders = {
    "ORNL-Work": "1VwudvkZLC3YPze5-6bJrZWFSS0N4yeq8",
    "ORNL-Work/ServiceNow Demands": "1KQEtrHupZ9modQ7ndJZs8gI9oKH2BAh7",
    "ORNL-Work/Incidents": "1W2TYfRT_INASezEDWUDbQdVCiKRk3Sjf",
    "ORNL-Work/AppDev Reorg": "1YroZSZkDTigLYV0YJ4LbynETiZGV5wng",
    "ORNL-Work/Presentations": "1ty4mR0dPvFdTSUchQjKjRL4KtD2_Wpo6",
    "ORNL-Work/Strategic Planning": "1gq7JemoApE2YX81Q-yWRFPfMhIcj1FLa",
    "ORNL-Work/Employee Photos": "1RU7BFC3nss2CJRElzPPtYSHIDOWTDCqv",
    "Hannah-Music-Business": "1ZvwUEh0nitV1td94AF_hkhgBu-XFqS2K",
    "Hannah/Resumes & Career": "1fOdmyeumbcHGUHTGR9e5OLuFcL9uX8ZU",
    "Hannah/Merchandise": "1_wpKQSzjY9MIaCHOXxnXLOLh-12mcASR",
    "Hannah/Tour Materials": "1x2n1NBj83CHc8w5UxQSyfEynQXDzjsa_",
    "Hannah/Music Files": "1GVOtIp2HOq50jdsKZqCuWqp-iQHsX-nD",
    "Hannah/Music Videos": "1wsvPdJ8YA67pLdN5urZhu_H48hnltkzr",
    "Hannah/Schedules": "1qiI42pEhPjoO52IgnZKFRFuHbw7E3a3o",
    "Hannah/Legal & Finance": "1mpp6WAxdVvrRHcsAc_u_xguCr59F1h7f",
    "Finance": "1Cvws3DGHEZf2qsZi61HlrdI6WSFIl4Vv",
    "Finance/Finance OS": "1-LibYg1cL1uvR2wu90J-6ne-rXMGDZWT",
    "Finance/Expenses & Transactions": "1sWRz5N7G5aAsL_NcrSgiNURusL4hQFLu",
    "Finance/Banking & Investments": "1rwkqO8YLy6MVV3p9yGWhsdxa3kYErfBj",
    "Finance/Financial Analysis": "1-jQZLRH2xdrW82_2T2lcpgNTDW727ZHk",
    "Legal": "1p7dF682Vu_5_bDx8VBlZACA1zUQ3CPsI",
    "Legal/Aldridge Estate": "1-sQJEYjeaJkVbi2i6hXWfybn6eTzf6cx",
    "Legal/Abell vs Aldridge": "18BdcD1FC6hM7mzBZJ1ges-xo1ozEoT_y",
    "Legal/Loan Documentation": "1Kg6VPmLmilnK0s8qRhBSPad6X3F-iGt5",
    "Legal/Housing Applications": "1BHTDMV8R91RvtW5zMA5IOk9vb-dMhA2G",
    "Legal/Agreements": "17_IBSD7lztec-S0LFV5IWktcXIo8ZxwH",
    "Avie": "1ETLvkSD78DQWnwr4JA4SG5XNf73MXPef",
    "Avie/School": "1wQoTRkGdZoBBTr21sai29i10d6ljI_za",
    "Avie/Songs": "1DArnYFX3Dy7w1VAbPuYHqHY8qZW9DoKL",
    "Writing": "1WyBpBCblCQtHNBwC13lC1ABq4XEzY4BW",
    "Writing/Novels & Fiction": "1rcE9aapfupJms2AiC9nHjEfYOUn8VvMZ",
    "Writing/Songs & Lyrics": "1YI56mTgrv3XpYanE0MAyr6u7bXJ4gjkz",
    "Writing/Personal Essays": "1S6yrx2imzzbyYp3nBRsxsxh8EQSmlsNg",
    "Personal": "1Onc5rAjF-RdEN5HcrGVi1iC8eVD-jT5P",
    "Personal/Health & Therapy": "12kkaF2QblBWdVyCCaJXGIwZhwj38Bc1c",
    "Personal/Family": "1OsBcQUYZhl5aofjTvX5kpvX3TD0RYJO1",
    "Personal/Housing": "1e41Maqy9XoRQKBW7XtKFy0t47ZGXqVCH",
    "Personal/Life Planning": "1q92MReGoJU3vMgGE6M8t5PjDwvyedIP2",
    "Projects": "1MOk5OwpHEawBLx0oBrWydYNYsv30WO3p",
    "Projects/Lunchpool Archive": "16f7Sj-i6V36p_X3-7xHJRnEU8rVa8uPR",
    "Media": "1am2RoX9Xfjonch1zzj76UETAV_xdrZ51",
    "Media/Videos - Personal": "1t9jH8gQm7nENlvWBGeQXYVCbV04NqC-R",
    "Media/Videos - Work": "1DDxYY63-wOn9-MFYqwUWKQMlvg2LU2Fs",
    "Media/Photos": "1PkcU6IbKezhCfeyegXxeUzi0i7VBGCNY",
    "Media/Audio": "1uyWXkpIPyu2H_BUDxWaxxlb3bvn8yEdf",
    "Archive": "1gU2hdShVgUYZxng-8N9vKbUm5AzyPo3s",
    "Archive/ChatGPT Artifacts": "1wfMAtRO5w9399xw2C2YpGx6-5wMnEqmI",
}

# Keyword-based routing rules
rules = [
    # ORNL / Work
    (["ORNL", "ornl", "AppDev", "appdev", "Reorg", "Gate 1", "PIT ", "Digital Transformation"], "ORNL-Work"),
    (["ServiceNow", "servicenow", "SNOW", "Demand"], "ORNL-Work/ServiceNow Demands"),
    (["Incident", "incident"], "ORNL-Work/Incidents"),
    (["EmployeePhoto", "Employee Photo", "staff photo"], "ORNL-Work/Employee Photos"),
    
    # Hannah
    (["Hannah", "hannah", "Aldridge"], "Hannah-Music-Business"),
    (["resume", "Resume", "CV ", "cv "], "Hannah/Resumes & Career"),
    (["merch", "Merch", "inventory", "Inventory", "merchandise"], "Hannah/Merchandise"),
    (["tour", "Tour", "booking", "Booking"], "Hannah/Tour Materials"),
    (["schedule", "Schedule", "calendar"], "Hannah/Schedules"),
    
    # Finance
    (["Finance OS", "finance os", "Financial"], "Finance/Finance OS"),
    (["expense", "Expense", "transaction", "Transaction", "receipt"], "Finance/Expenses & Transactions"),
    (["bank", "Bank", "investment", "Investment", "Citi", "Wells"], "Finance/Banking & Investments"),
    
    # Legal
    (["Aldridge Estate", "estate", "Estate", "probate"], "Legal/Aldridge Estate"),
    (["Abell vs", "custody", "Custody", "dissolution"], "Legal/Abell vs Aldridge"),
    (["loan", "Loan", "mortgage", "Mortgage"], "Legal/Loan Documentation"),
    (["rental", "Rental", "application", "lease", "Lease", "apartment"], "Legal/Housing Applications"),
    
    # Avie
    (["Avie", "avie", "Rocky Hill"], "Avie"),
    
    # Writing
    (["novel", "Novel", "chapter", "Chapter", "manuscript", "Camino"], "Writing/Novels & Fiction"),
    (["song", "Song", "lyric", "Lyric", "chord"], "Writing/Songs & Lyrics"),
    (["Built to Last", "Fear Map", "journal"], "Writing/Personal Essays"),
    
    # Personal
    (["therapy", "Therapy", "Chelsea", "psychiatr", "mental health"], "Personal/Health & Therapy"),
    
    # Media
    (["RPReplay", "IMG_", "MOV", ".mov", ".mp4", "video", "Video"], "Media/Videos - Personal"),
    (["photo", "Photo", ".jpg", ".png", ".heic", "HEIC", "screenshot"], "Media/Photos"),
    
    # Projects
    (["Lunchpool", "lunchpool"], "Projects/Lunchpool Archive"),
    (["Pooli", "pooli", "pool"], "Projects"),
    
    # Archive
    (["ChatGPT", "chatgpt", "Untitled spreadsheet", "Untitled document"], "Archive/ChatGPT Artifacts"),
]

# Get files
pages = []
for i in range(1, 6):
    try:
        with open(f"/tmp/drive-page{i}.json") as f:
            data = json.load(f)
            files = data.get("files", data.get("data", []))
            if isinstance(files, list):
                pages.extend(files)
    except:
        break

print(f"Found {len(pages)} files to process")

moved = 0
skipped = 0
errors = 0
log_lines = []

for item in pages:
    name = item.get("name", "")
    file_id = item.get("id", "")
    mime = item.get("mimeType", "")
    
    # Skip folders (they're already organized)
    if mime == "application/vnd.google-apps.folder":
        continue
    
    # Find matching rule
    target = None
    for keywords, folder in rules:
        for kw in keywords:
            if kw in name:
                target = folder
                break
        if target:
            break
    
    if not target:
        skipped += 1
        continue
    
    folder_id = folders.get(target)
    if not folder_id:
        print(f"  ⚠️  No folder ID for {target}")
        skipped += 1
        continue
    
    print(f"Moving: {name} → {target}")
    try:
        result = subprocess.run(
            ["gog", "drive", "move", file_id, "--parent", folder_id, "--account", acct, "--force"],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            print(f"  ✅")
            log_lines.append(f"Moved: {name} → {target} ({file_id} → {folder_id})")
            moved += 1
        else:
            print(f"  ❌ {result.stderr[:100]}")
            log_lines.append(f"ERROR: {name} → {target} — {result.stderr[:100]}")
            errors += 1
    except Exception as e:
        print(f"  ❌ {e}")
        errors += 1
    
    time.sleep(1)  # Rate limit

print(f"\n=== DONE ===")
print(f"Moved: {moved}")
print(f"Skipped (no match): {skipped}")
print(f"Errors: {errors}")

# Append to log
with open(log_path, "a") as f:
    f.write(f"\n## Phase 3: File Moves ({time.strftime('%Y-%m-%d %H:%M')})\n")
    for line in log_lines:
        f.write(f"  {line}\n")
    f.write(f"\nSummary: {moved} moved, {skipped} skipped, {errors} errors\n")

PYEOF

echo "Script complete. Moved: $MOVED, Errors: $ERRORS"
