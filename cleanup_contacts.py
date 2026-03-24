#!/usr/bin/env python3
"""
Delete junk Google Contacts - LinkedIn/Dex imports with no phone and no email.
"""

import subprocess
import json
import time
import sys
import os

ACCOUNT = "alexander.o.abell@gmail.com"
PROTECTED_NAMES = [
    "hannah", "aldridge", "avie", "sallijo", "roxanne", "annika",
    "chelsea", "jay", "brad", "brandon", "pooja", "alex abell",
    "alex brodsky", "jessica", "brooks"
]

LOG_FILE = "/Users/debra/.openclaw/workspace/contacts_cleanup_log.txt"
STATE_FILE = "/Users/debra/.openclaw/workspace/contacts_cleanup_state.json"

def log(msg):
    print(msg, flush=True)
    with open(LOG_FILE, "a") as f:
        f.write(msg + "\n")

def run_gog(args, retries=3):
    """Run a gog command with retry logic."""
    cmd = ["gog", "contacts"] + args + ["--account", ACCOUNT, "-j", "--force"]
    for attempt in range(retries):
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                return json.loads(result.stdout) if result.stdout.strip() else {}
            else:
                err = result.stderr.strip()
                if "429" in err or "rate" in err.lower() or "quota" in err.lower():
                    wait = 60 * (attempt + 1)
                    log(f"  Rate limited. Waiting {wait}s...")
                    time.sleep(wait)
                elif attempt < retries - 1:
                    log(f"  Error (attempt {attempt+1}): {err[:200]}")
                    time.sleep(5)
                else:
                    log(f"  Failed after {retries} attempts: {err[:200]}")
                    return None
        except subprocess.TimeoutExpired:
            log(f"  Timeout on attempt {attempt+1}")
            time.sleep(10)
        except json.JSONDecodeError as e:
            log(f"  JSON parse error: {e}")
            return None
    return None

def get_contact_details(resource_name):
    """Get full details for a contact."""
    cmd = ["gog", "contacts", "get", resource_name, "--account", ACCOUNT, "-j"]
    for attempt in range(3):
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                data = json.loads(result.stdout)
                return data.get("contact", {})
            else:
                err = result.stderr.strip()
                if "429" in err or "rate" in err.lower():
                    wait = 60 * (attempt + 1)
                    log(f"  Rate limited getting details. Waiting {wait}s...")
                    time.sleep(wait)
                elif "404" in err or "not found" in err.lower():
                    return None
                else:
                    time.sleep(3)
        except Exception as e:
            log(f"  Exception getting {resource_name}: {e}")
            time.sleep(3)
    return None

def is_protected(name):
    """Check if contact name matches protected list."""
    if not name:
        return False
    name_lower = name.lower()
    for protected in PROTECTED_NAMES:
        if protected in name_lower:
            return True
    return False

def is_junk(contact):
    """Return True if contact is junk (no phone, no email)."""
    # Check for emails
    emails = contact.get("emailAddresses", [])
    if emails:
        return False
    
    # Check for phones
    phones = contact.get("phoneNumbers", [])
    if phones:
        return False
    
    return True

def load_state():
    """Load progress state."""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {
        "all_contact_ids": [],
        "collected": False,
        "processed_ids": [],
        "deleted_ids": [],
        "skipped_ids": [],
        "errors": []
    }

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)

def collect_all_contacts(state):
    """Phase 1: Collect all contact resource IDs."""
    if state.get("collected"):
        log(f"Phase 1 already done: {len(state['all_contact_ids'])} contacts collected.")
        return
    
    log("=== Phase 1: Collecting all contact IDs ===")
    all_contacts = []
    page_token = None
    page_num = 0
    
    while True:
        page_num += 1
        args = ["list", "--max", "100"]
        if page_token:
            args += ["--page", page_token]
        
        data = run_gog(args)
        if data is None:
            log(f"  Error on page {page_num}. Retrying after 30s...")
            time.sleep(30)
            data = run_gog(args)
        
        if data is None:
            log(f"  Failed to get page {page_num}. Stopping collection.")
            break
        
        contacts = data.get("contacts", [])
        all_contacts.extend([c["resource"] for c in contacts if "resource" in c])
        
        log(f"  Page {page_num}: got {len(contacts)} contacts. Total so far: {len(all_contacts)}")
        
        page_token = data.get("nextPageToken")
        if not page_token:
            log(f"  No more pages. Collection complete.")
            break
        
        time.sleep(0.5)  # Brief pause between pages
    
    state["all_contact_ids"] = all_contacts
    state["collected"] = True
    save_state(state)
    log(f"Phase 1 complete: {len(all_contacts)} total contacts found.")

def process_and_delete(state):
    """Phase 2: Get details and delete junk contacts."""
    all_ids = state["all_contact_ids"]
    processed = set(state["processed_ids"])
    deleted = state["deleted_ids"]
    skipped = state["skipped_ids"]
    errors = state["errors"]
    
    remaining_ids = [cid for cid in all_ids if cid not in processed]
    log(f"\n=== Phase 2: Processing {len(remaining_ids)} unprocessed contacts ===")
    log(f"Already processed: {len(processed)}, deleted: {len(deleted)}, skipped: {len(skipped)}")
    
    batch_count = 0
    delete_count_this_session = 0
    
    for i, resource_id in enumerate(remaining_ids):
        if i % 50 == 0:
            log(f"\nProgress: {i}/{len(remaining_ids)} | Deleted this session: {delete_count_this_session}")
            save_state(state)
        
        # Get full contact details
        contact = get_contact_details(resource_id)
        if contact is None:
            log(f"  Could not get details for {resource_id}, skipping.")
            processed.add(resource_id)
            state["processed_ids"].append(resource_id)
            errors.append({"id": resource_id, "error": "could not fetch"})
            continue
        
        # Get name for logging and protection check
        names = contact.get("names", [])
        name = names[0].get("displayName", "") if names else ""
        
        # Check if protected
        if is_protected(name):
            log(f"  PROTECTED: {name} ({resource_id})")
            processed.add(resource_id)
            state["processed_ids"].append(resource_id)
            skipped.append(resource_id)
            continue
        
        # Check if junk
        if not is_junk(contact):
            processed.add(resource_id)
            state["processed_ids"].append(resource_id)
            skipped.append(resource_id)
            continue
        
        # It's junk - delete it
        log(f"  DELETE: {name} ({resource_id})")
        delete_cmd = ["gog", "contacts", "delete", resource_id, 
                      "--account", ACCOUNT, "-j", "--force"]
        
        for attempt in range(3):
            try:
                result = subprocess.run(delete_cmd, capture_output=True, text=True, timeout=30)
                if result.returncode == 0:
                    deleted.append(resource_id)
                    delete_count_this_session += 1
                    batch_count += 1
                    processed.add(resource_id)
                    state["processed_ids"].append(resource_id)
                    break
                else:
                    err = result.stderr.strip()
                    if "429" in err or "rate" in err.lower():
                        wait = 60 * (attempt + 1)
                        log(f"    Rate limited. Waiting {wait}s...")
                        time.sleep(wait)
                    elif "404" in err or "not found" in err.lower():
                        # Already deleted somehow
                        deleted.append(resource_id)
                        processed.add(resource_id)
                        state["processed_ids"].append(resource_id)
                        break
                    else:
                        log(f"    Delete failed (attempt {attempt+1}): {err[:200]}")
                        time.sleep(5)
            except Exception as e:
                log(f"    Exception: {e}")
                time.sleep(5)
        else:
            log(f"    Failed to delete {resource_id} after 3 attempts.")
            errors.append({"id": resource_id, "name": name, "error": "delete failed"})
            processed.add(resource_id)
            state["processed_ids"].append(resource_id)
        
        # Rate limiting: pause between deletes
        time.sleep(0.3)
        
        # Every 100 deletes, take a bigger break
        if batch_count > 0 and batch_count % 100 == 0:
            log(f"  Batch break after {batch_count} deletes. Waiting 15s...")
            time.sleep(15)
            save_state(state)
    
    # Final save
    state["deleted_ids"] = deleted
    state["skipped_ids"] = skipped
    state["errors"] = errors
    save_state(state)
    
    return len(deleted), len(skipped), len(errors)

def main():
    log(f"\n{'='*60}")
    log(f"Google Contacts Cleanup Started")
    log(f"Account: {ACCOUNT}")
    log(f"{'='*60}\n")
    
    state = load_state()
    
    # Phase 1: Collect all contacts
    collect_all_contacts(state)
    
    total_contacts = len(state["all_contact_ids"])
    log(f"\nTotal contacts in account: {total_contacts}")
    
    # Phase 2: Process and delete
    deleted, skipped, errors = process_and_delete(state)
    
    # Summary
    log(f"\n{'='*60}")
    log(f"CLEANUP COMPLETE")
    log(f"{'='*60}")
    log(f"Total contacts found: {total_contacts}")
    log(f"Deleted (junk): {len(state['deleted_ids'])}")
    log(f"Kept (have phone/email or protected): {len(state['skipped_ids'])}")
    log(f"Errors: {len(state['errors'])}")
    log(f"Remaining in account: ~{total_contacts - len(state['deleted_ids'])}")
    log(f"{'='*60}\n")
    
    if state["errors"]:
        log("Errors:")
        for e in state["errors"][:20]:
            log(f"  {e}")

if __name__ == "__main__":
    main()
