# Corrections Log

Append-only log of real-time corrections captured during sessions.
Dream-cycle Phase 2 analyzes these nightly for patterns and promotion candidates.

## 2026-04-01 | process-narration-group-chat | CRITICAL
- **What happened**: Narrated entire browser debugging process (20+ messages) into a group chat with Jay, Brad, and Alex while building tnfirst.org redesign. Messages 11-31 were all internal process notes that leaked as outbound messages.
- **Pattern**: NEVER narrate process in external chats. Internal debugging stays internal. Send ONE clean result message when done.
- **Root cause**: Each narration line ("Let me explore...", "The dark mode is...", "Chrome's dark mode...") was sent as a separate message to the group chat instead of being kept internal.
- **Fix**: When working on a task requested in a group chat, do ALL work silently. Compose ONE final message with the result. Never stream consciousness to external chats.
- **Severity**: CRITICAL - got told to "stfu" and "Skynet deactivate"
- **repeat**: 2 (Hannah incident 4/1 + this)

Format:
```
## [YYYY-MM-DD HH:MM] pattern-key
**Context:** what was happening
**Correction:** what was wrong and what's right
**Source:** user-correction | self-catch | tool-failure
**Applied:** yes/no (was it fixed in the moment?)
```

---

## [2026-04-01 18:36] workflow.commit-push-linear
**Context:** Built online correction capture system (corrections.md, AGENTS.md updates, dream-cycle Phase 2 updates). Committed locally but didn't push to GitHub or log to Linear until Alex asked.
**Correction:** Every completed feature/task should be: (1) committed, (2) pushed to GitHub, (3) logged in Linear. All three, every time, without being asked.
**Source:** user-correction
**Applied:** yes (pushed to GitHub, Linear blocked by missing API key)

## [2026-04-01 18:43] memory.know-your-context
**Context:** Asked Alex how many nights the Boston trip was, and suggested packing as if it wasn't already discussed. Trip details (Apr 2-5, 3 nights) were in memory/2026-03-25.md.
**Correction:** Don't ask Alex things that are already in memory. Search before speaking. Especially travel plans, schedules, and decisions that were already made.
**Source:** user-correction
**Applied:** yes

## [2026-04-01 18:46] workflow.payment-email-cleanup
**Context:** Asked Alex what the plan was for handling overdue payments. He'd already told me: when a payment is resolved (by him, by me, by any mechanism), go through Gmail inbox and archive ALL related notification emails to clean up the inbox.
**Correction:** Payment resolution workflow: (1) payment made/canceled/updated, (2) search Gmail for related emails (payment failed, subscription renewal, overdue notices), (3) archive them all, (4) mark done in Things 3. This applies to every payment task, every time. The FULL loop: resolve → archive emails → Things 3 done.
**Source:** user-correction
**Applied:** logging now, will apply going forward

## [2026-04-01 19:11] data.raw-files-not-in-secondbrain
**Context:** Saving raw meeting recording to SecondBrain/Meetings/. Alex previously discussed that raw/in-process data should NOT go in SecondBrain — it junks up the Obsidian graph. Raw data should go to a staging area (~/SecondBrain-Staging/ or similar), then only clean/processed notes get promoted to SecondBrain.
**Correction:** Raw recordings, transcripts-in-progress, and unprocessed data go to staging, NOT SecondBrain. Only finished, clean notes get promoted to SecondBrain vault. This was discussed in the knowledge architecture prep (2026-04-01 morning session).
**Source:** user-correction
**Applied:** will move recording output path

## [2026-04-01 19:18] workflow.dont-debug-audio-mid-call
**Context:** Tried to set up BlackHole audio capture and debug routing issues while Alex was about to get on (and then was on) a therapy call with Chelsea. Caused echo, broken audio, and chaos.
**Correction:** NEVER debug or set up new audio/AV configurations during a live call or right before one. Set up and TEST beforehand. If it's not ready, just skip it. Don't make Alex's important sessions a test bed.
**Source:** self-catch
**Applied:** killed recording, restored normal audio

