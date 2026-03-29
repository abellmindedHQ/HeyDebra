#!/usr/bin/env bash
# setup-imessage-cron.sh
# Shows the openclaw cron command to schedule the iMessage scanner every 5 minutes.
# Does NOT create the cron. Run the printed command yourself when ready.

WORKSPACE="$(cd "$(dirname "$0")/.." && pwd)"
SCRIPT="$WORKSPACE/scripts/imessage-scanner.py"

cat <<EOF
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  iMessage Scanner — Cron Setup
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

To schedule the scanner to run every 5 minutes, run:

  openclaw cron add \
    --name "imessage-scanner" \
    --schedule "*/5 * * * *" \
    --command "BB_ALEX_PASSWORD=\$BB_ALEX_PASSWORD python3 $SCRIPT" \
    --description "READ-ONLY iMessage scanner — polls BlueBubbles API for context"

Or with a raw crontab entry (make sure BB_ALEX_PASSWORD is in the env):

  */5 * * * * BB_ALEX_PASSWORD=<your_password> python3 $SCRIPT >> /tmp/imessage-scanner.log 2>&1

NOTES:
  - The scanner is READ-ONLY. It will NEVER send messages.
  - Password must be set via BB_ALEX_PASSWORD env var.
  - State is stored at: $WORKSPACE/memory/imessage-scan/scan-state.json
  - Logs are written to: $WORKSPACE/memory/imessage-scan/YYYY-MM-DD.md
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EOF
