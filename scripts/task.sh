#!/bin/bash
# task.sh — Single entry point for Things 3 task management
# Usage:
#   task.sh add "title" [--list "area"] [--when date] [--notes "notes"] [--tags "tag"]
#   task.sh done "title" [--list "area"] [--notes "notes"]
#   task.sh check "search term"
#
# Handles: dedup check, area/list enforcement, add, complete, search

set -euo pipefail

export THINGS_AUTH_TOKEN="${THINGS_AUTH_TOKEN:-H_VPe3JVQdKhVnQdWFiMIQ}"

ACTION="${1:-help}"
shift || true

# Default area mapping based on keywords in title
guess_area() {
    local title="$1"
    title_lower=$(echo "$title" | tr '[:upper:]' '[:lower:]')
    
    if echo "$title_lower" | grep -qiE "ornl|work|meeting|oak ridge|serviceNow|shield|patti|jay|angie|budget"; then
        echo "🏢 ORNL"
    elif echo "$title_lower" | grep -qiE "finance|money|insurance|health|doctor|budget|tax|ynab|monarch|payment|bill|prescription|lipoma|surgery|dentist|psychiatr"; then
        echo "💊 Health & Money"
    elif echo "$title_lower" | grep -qiE "hannah|annika|avie|sallijo|chelsea|merle|birthday|roxanne|marshall|brandon|teresa|family"; then
        echo "👨‍👧 People"
    elif echo "$title_lower" | grep -qiE "code|build|openclaw|deploy|github|linear|api|skill|agent|cron|dream|capture|gsd|neo4j|gemini|1password|things3|webhook|script"; then
        echo "🚀 Build"
    else
        echo "🏠 Life Ops"
    fi
}

# Check for duplicates
check_dupe() {
    local title="$1"
    # Search existing tasks (incomplete)
    local results
    results=$(things search "$title" --json 2>/dev/null || echo "[]")
    local count
    count=$(echo "$results" | python3 -c "import sys,json; items=json.load(sys.stdin); print(len([i for i in items if i.get('status',0)==0]))" 2>/dev/null || echo "0")
    
    if [ "$count" -gt "0" ]; then
        echo "⚠️  DUPLICATE FOUND ($count match): $title"
        echo "$results" | python3 -c "import sys,json; [print(f'  → {i[\"uuid\"]} | {i[\"title\"]} | {i.get(\"area_title\",\"no area\")}') for i in json.load(sys.stdin) if i.get('status',0)==0]" 2>/dev/null
        return 1
    fi
    return 0
}

case "$ACTION" in
    add)
        TITLE=""
        LIST=""
        WHEN=""
        NOTES=""
        TAGS=""
        
        # Parse args
        while [[ $# -gt 0 ]]; do
            case "$1" in
                --list) LIST="$2"; shift 2 ;;
                --when) WHEN="$2"; shift 2 ;;
                --notes) NOTES="$2"; shift 2 ;;
                --tags) TAGS="$2"; shift 2 ;;
                --) shift; TITLE="$*"; break ;;
                *) 
                    if [ -z "$TITLE" ]; then
                        TITLE="$1"
                    fi
                    shift ;;
            esac
        done
        
        if [ -z "$TITLE" ]; then
            echo "❌ No title provided"
            exit 1
        fi
        
        # Auto-detect area if not provided
        if [ -z "$LIST" ]; then
            LIST=$(guess_area "$TITLE")
            echo "📂 Auto-categorized: $LIST"
        fi
        
        # Dedup check
        if ! check_dupe "$TITLE"; then
            echo "Skipping add (duplicate exists). Use 'task.sh add --force' to override."
            exit 0
        fi
        
        # Build command
        CMD="things add --list \"$LIST\""
        [ -n "$WHEN" ] && CMD="$CMD --when \"$WHEN\""
        [ -n "$NOTES" ] && CMD="$CMD --notes \"$NOTES\""
        [ -n "$TAGS" ] && CMD="$CMD --tags \"$TAGS\""
        CMD="$CMD -- \"$TITLE\""
        
        eval "$CMD" 2>&1
        echo "✅ Added: $TITLE [$LIST]"
        ;;
        
    done)
        TITLE=""
        LIST=""
        NOTES=""
        
        # Parse args
        while [[ $# -gt 0 ]]; do
            case "$1" in
                --list) LIST="$2"; shift 2 ;;
                --notes) NOTES="$2"; shift 2 ;;
                --) shift; TITLE="$*"; break ;;
                *) 
                    if [ -z "$TITLE" ]; then
                        TITLE="$1"
                    fi
                    shift ;;
            esac
        done
        
        if [ -z "$TITLE" ]; then
            echo "❌ No title provided"
            exit 1
        fi
        
        # Auto-detect area if not provided
        if [ -z "$LIST" ]; then
            LIST=$(guess_area "$TITLE")
        fi
        
        # Build command
        CMD="things add --completed --list \"$LIST\""
        [ -n "$NOTES" ] && CMD="$CMD --notes \"$NOTES\""
        CMD="$CMD -- \"$TITLE\""
        
        eval "$CMD" 2>&1
        echo "✅ Done: $TITLE [$LIST]"
        ;;
        
    check)
        QUERY="${*:-}"
        if [ -z "$QUERY" ]; then
            echo "Usage: task.sh check <search term>"
            exit 1
        fi
        things search "$QUERY" --json 2>/dev/null | python3 -c "
import sys,json
items = json.load(sys.stdin)
active = [i for i in items if i.get('status',0) == 0]
done = [i for i in items if i.get('status',0) != 0]
print(f'Active: {len(active)}, Completed: {len(done)}')
for i in active:
    print(f'  📋 {i[\"title\"]} | {i.get(\"area_title\",\"no area\")}')
for i in done[:3]:
    print(f'  ✅ {i[\"title\"]}')
" 2>/dev/null
        ;;
        
    help|*)
        echo "task.sh — Things 3 task manager"
        echo ""
        echo "Commands:"
        echo "  add \"title\" [--list area] [--when date] [--notes text] [--tags tag]"
        echo "  done \"title\" [--list area] [--notes text]"
        echo "  check \"search term\""
        echo ""
        echo "Features:"
        echo "  - Auto-categorizes by keyword (ORNL, Build, People, Health, Life Ops)"
        echo "  - Dedup check before adding"
        echo "  - Always adds with area/list"
        ;;
esac
