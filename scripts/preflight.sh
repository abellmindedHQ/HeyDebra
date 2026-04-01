#!/bin/bash
# preflight.sh — MANDATORY before any outbound message to non-Alex recipient
# This script gathers context so you don't send blind.
# Usage: preflight.sh "recipient name or number"
#
# Outputs: last 10 messages in the thread, participant list, any pending requests
# YOU MUST READ THIS OUTPUT before composing your message.

set -euo pipefail

TOOLS_FILE="/Users/debra/.openclaw/workspace/TOOLS.md"
BB_PASS="H!tchhiker42"
RECIPIENT="${1:-}"

if [ -z "$RECIPIENT" ]; then
    echo "❌ Usage: preflight.sh 'recipient name or number'"
    exit 1
fi

echo "========================================"
echo "📋 PREFLIGHT CHECK: $RECIPIENT"
echo "========================================"

# Step 1: Find GUID
GUID=$(grep -i "$RECIPIENT" "$TOOLS_FILE" | grep "any;" | head -1 | sed 's/.*: //' | awk '{print $1}')

if [ -z "$GUID" ]; then
    echo "⚠️  No GUID found in TOOLS.md for '$RECIPIENT'"
    echo "   Search BB API manually or use phone number."
    exit 1
fi

echo ""
echo "✅ GUID: $GUID"
echo ""

# Step 2: Show participants
echo "👥 PARTICIPANTS (from TOOLS.md):"
grep "$GUID" "$TOOLS_FILE" || echo "  (no entry found)"
echo ""

# Step 3: Pull last 10 messages
echo "💬 LAST 10 MESSAGES:"
echo "----------------------------------------"
curl -s "http://localhost:1234/api/v1/chat/$GUID/message?limit=10&password=$BB_PASS" | python3 -c "
import sys, json
d = json.load(sys.stdin)
for m in reversed(d.get('data', [])):
    sender = m.get('handle', {}).get('address', 'me') if m.get('handle') else 'DEBRA'
    is_from_me = m.get('is_from_me', False)
    if is_from_me:
        sender = 'DEBRA'
    text = (m.get('text', '') or '')[:200]
    attachments = m.get('attachments', [])
    att_str = f' [📎 {len(attachments)} attachment(s)]' if attachments else ''
    print(f'  {sender}: {text}{att_str}')
" 2>/dev/null || echo "  (failed to fetch messages)"

echo "----------------------------------------"
echo ""

# Step 4: Check for pending requests
echo "📌 PENDING REQUESTS (look for asks directed at Debra):"
curl -s "http://localhost:1234/api/v1/chat/$GUID/message?limit=10&password=$BB_PASS" | python3 -c "
import sys, json
d = json.load(sys.stdin)
keywords = ['debra', 'can you', 'could you', 'please', 'make', 'send', 'do this', 'help']
for m in d.get('data', []):
    text = (m.get('text', '') or '').lower()
    if any(k in text for k in keywords):
        sender = m.get('handle', {}).get('address', 'DEBRA') if m.get('handle') else 'DEBRA'
        print(f'  ⚡ {sender}: {(m.get(\"text\", \"\") or \"\")[:200]}')
" 2>/dev/null || echo "  (none found)"

echo ""
echo "========================================"
echo "✅ READ THE ABOVE before composing your message."
echo "   Do you know: who's in the chat, what they're talking about,"
echo "   and what (if anything) they asked you to do?"
echo "========================================"
