# run-classifier-agent.md
## Agent Workflow: LinkedIn Conversation Classifier

This document describes the **step-by-step agent procedure** for running the
classify-conversations.py classifier end-to-end. Follow this exactly.

---

## Prerequisites
- `browser profile=openclaw` must be running and logged in to LinkedIn
- `gog` CLI must be available (`gog contacts search ...`)
- State dir: `/Users/debra/.openclaw/workspace/memory/`

---

## Step 1 — Open LinkedIn Messaging

```
browser action=open url=https://www.linkedin.com/messaging/ profile=openclaw
```

Wait for page load, then:
```
browser action=snapshot compact=true profile=openclaw
```

Verify: the snapshot contains a conversation list (not a login wall).
Save the `targetId` from the response for all subsequent calls.

---

## Step 2 — Initialize Classification State

```python
import sys
sys.path.insert(0, '/Users/debra/.openclaw/workspace/skills/linkedin-cleanup/scripts')
import classify_conversations as cc

state = cc.load_intermediate()  # empty on first run
```

---

## Step 3 — Batch Classification Loop

Repeat until all conversations are scanned OR limit reached:

### 3a. Take snapshot
```
browser action=snapshot compact=true targetId=<saved_targetId> profile=openclaw
```

### 3b. Parse + classify
```python
snapshot_text = "<snapshot output from above>"
state = cc.agent_classify_from_snapshot(snapshot_text, resume=True)
```

### 3c. Print progress
```
Scanned {state['stats']['total_scanned']}/~4960: {archived} archive, {kept} keep
```

### 3d. Scroll down to load more conversations
```
browser action=act kind=evaluate
  fn="document.querySelector('.msg-conversations-container__conversations-list').scrollBy(0, 2000)"
  targetId=<targetId>
```
Wait 1.5 seconds for conversations to load.

### 3e. Click "Load more conversations" if visible
Look for a button with text "Load more conversations" or similar in the snapshot.
If found:
```
browser action=act kind=click ref=<button_ref> targetId=<targetId>
```
Wait 2 seconds.

### 3f. Check for new conversations
If snapshot shows no new names not already in `state['seen_names']`, we've hit the bottom.
Stop the loop.

---

## Step 4 — Finalize

```python
cc.finalize(state, dry_run=False)
```

This writes `/Users/debra/.openclaw/workspace/memory/linkedin-cleanup-state.json`
with:
- `queue`: ARCHIVE names (ready for cleanup_state.py)
- `kept`: KEEP entries with reasons
- `totalQueued`: archive count
- `classification_stats`: full breakdown

---

## Step 5 — Review & Approve

Show Alex a summary:
```
📊 Classification complete:
   Total scanned:  4,960
   To archive:     3,847 (77%)
   To keep:          1,113 (22%)

   Top archive reasons:
     spam_keyword           2,341
     single_message           892
     no_alex_response         614
     inmail                   433
     old_sparse(>12mo)        289
```

Ask: "Ready to start archiving? The cleanup skill will process ~150/day."

---

## Scroll Helper (JavaScript)

To scroll the conversations sidebar (not the page):
```javascript
const list = document.querySelector('[data-view-name="message-list-item-preview"]')
  ?.closest('ul') ||
  document.querySelector('.msg-conversations-container__conversations-list') ||
  document.querySelector('.scaffold-layout__list');
if (list) list.scrollTop += 3000;
```

---

## Rate Limiting Notes

- Google Contacts lookups: max 1/sec (built into cc.is_in_google_contacts)
- LinkedIn scrolling: wait 1.5–2s between scrolls
- No rate limit on classification itself (pure local logic)
