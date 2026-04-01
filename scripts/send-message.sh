#!/bin/bash
# send-message.sh — Safe message sender with pre-send verification
# Usage:
#   send-message.sh --to "+1XXXXXXXXXX" --message "text" [--channel bluebubbles] [--guid "chat_guid"]
#   send-message.sh --to "name" --message "text"  (looks up GUID from TOOLS.md)
#   send-message.sh --check "name"  (just look up the GUID, don't send)
#
# Pre-send checks:
# 1. Resolves recipient to GUID via TOOLS.md
# 2. Shows you what will be sent and where
# 3. Blocks process narration (refuses messages matching debug patterns)
# 4. Logs all sends to memory

set -euo pipefail

TOOLS_FILE="/Users/debra/.openclaw/workspace/TOOLS.md"
SEND_LOG="/Users/debra/.openclaw/workspace/memory/send-log.json"

# Debug/narration patterns that should NEVER go to external chats
NARRATION_PATTERNS=(
    "let me try"
    "hmm"
    "that didn't work"
    "blank page"
    "error:"
    "trying again"
    "let me check"
    "wait, "
    "file sizes are suspicious"
    "not PDFs"
)

check_narration() {
    local msg_lower
    msg_lower=$(echo "$1" | tr '[:upper:]' '[:lower:]')
    for pattern in "${NARRATION_PATTERNS[@]}"; do
        if echo "$msg_lower" | grep -qi "$pattern"; then
            echo "🚫 BLOCKED: Message looks like process narration, not a result."
            echo "   Pattern matched: '$pattern'"
            echo "   Message: $1"
            echo ""
            echo "   If this IS a real message, remove the narration and try again."
            return 1
        fi
    done
    return 0
}

lookup_guid() {
    local search="$1"
    grep -i "$search" "$TOOLS_FILE" | grep "any;" | head -1 | sed 's/.*: //' | awk '{print $1}'
}

echo "=== send-message.sh pre-send check ==="
echo "This script validates before sending. Use the message tool directly after verification."
echo ""

# Parse args
TO=""
MESSAGE=""
GUID=""
CHECK_ONLY=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --to) TO="$2"; shift 2 ;;
        --message) MESSAGE="$2"; shift 2 ;;
        --guid) GUID="$2"; shift 2 ;;
        --check) TO="$2"; CHECK_ONLY=true; shift 2 ;;
        *) shift ;;
    esac
done

if [ -z "$TO" ]; then
    echo "❌ No recipient. Use --to 'name or number' or --check 'name'"
    exit 1
fi

# Look up GUID
if [ -z "$GUID" ]; then
    GUID=$(lookup_guid "$TO")
fi

if [ -n "$GUID" ]; then
    echo "✅ Recipient: $TO"
    echo "✅ GUID: $GUID"
    # Show participants from TOOLS.md
    grep "$GUID" "$TOOLS_FILE" 2>/dev/null || true
else
    echo "⚠️  No GUID found for '$TO' in TOOLS.md"
    echo "   If this is a new contact, send via phone number and add GUID after."
fi

if $CHECK_ONLY; then
    exit 0
fi

if [ -z "$MESSAGE" ]; then
    echo "❌ No message. Use --message 'text'"
    exit 1
fi

# Check for narration
if ! check_narration "$MESSAGE"; then
    exit 1
fi

echo ""
echo "📨 Ready to send:"
echo "   To: $TO"
echo "   GUID: ${GUID:-'(direct via number)'}"
echo "   Message: $MESSAGE"
echo ""
echo "Use the message tool with target=$GUID to send."
