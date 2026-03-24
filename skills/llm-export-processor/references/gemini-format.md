# Gemini Export Format Notes

This file documents the Gemini Takeout export format as discovered on first run.
Update this file when you process a Gemini export for the first time.

## Status
**Not yet processed.** No format documentation available yet.

## Where to Find Gemini Data in Takeout

When downloading Google Takeout:
1. Go to https://takeout.google.com
2. Deselect all → Select only "Gemini Apps Activity"
3. Download ZIP
4. Extract → look for `Takeout/Gemini Apps Activity/`

## Expected Structure (Unverified)

Likely formats (check on first run):
- `My Activity/Gemini/MyActivity.json` — activity log entries
- HTML files in `My Activity/Gemini/` — may need parsing

## Parsing Notes

When you first process a Gemini export:
1. List files in the Gemini directory
2. Inspect first few files to understand structure
3. Document the actual structure here for future runs
4. Update the parser in SKILL.md accordingly

## Known Limitations

- Gemini Takeout may only export activity metadata, not full conversation transcripts
- If full transcripts are unavailable, extract at minimum: date, topic (from title), and any activity signals
