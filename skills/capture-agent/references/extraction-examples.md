# Extraction Examples — Good vs. Bad Captures

## ✅ GOOD CAPTURES (extract these)

### Direct commitments
- "I'll send you the proposal by Friday" → `Send proposal — assigned to: Alex, due: Friday`
- "Can you follow up with Jay about the budget?" → `Follow up with Jay about budget — assigned to: Alex`
- "We need to schedule a 1:1 before the end of the month" → `Schedule 1:1 with [person] — due: end of month`
- "Don't forget to update the README before merging" → `Update README before merging PR — priority: urgent`
- "Remind me to call mom on Sunday" → `Call Sallijo — due: Sunday, priority: normal`
- "I owe Hannah a birthday plan" → `Plan Hannah's birthday — assigned to: Alex, priority: normal`
- "The deadline for the ORNL proposal is March 31" → `Submit ORNL proposal — due: 2026-03-31, priority: urgent`

### Implied commitments (extract with "normal" priority)
- "I've been meaning to clean up the repo" → `Clean up repo — assigned to: Alex, priority: low`
- "We should really look into that vendor" → `Evaluate [vendor] — priority: low`
- "I told Jay I'd have something to him by EOW" → `Deliver [item] to Jay — due: EOW, priority: urgent, assigned to: Alex`

### Calendar / meeting action items
- Meeting description: "Action items: 1. Alex to send slides to team by Thursday" → `Send slides to team — due: Thursday, assigned to: Alex, source: calendar:[meeting name]`
- "Prep agenda before standup tomorrow" → `Prep standup agenda — due: tomorrow, priority: urgent`

---

## ❌ BAD CAPTURES (skip these)

### Observations, not commitments
- "That was a great meeting" → SKIP
- "The deadline was last week" → SKIP (past deadline, no action)
- "Alex mentioned he's been busy" → SKIP

### Questions without commitment
- "Do you think we should refactor this?" → SKIP (no commitment)
- "Have you seen the new update?" → SKIP

### Vague non-actionable statements
- "We'll figure it out" → SKIP
- "Something to think about" → SKIP
- "That would be nice" → SKIP

### Already completed context
- "I sent the email yesterday" → SKIP (past tense, completed)
- "We shipped the feature last week" → SKIP

---

## 🔶 EDGE CASES

### Soft commitments (capture with low priority)
- "I should really..." → capture as low priority, assignee: Alex
- "One of these days I want to..." → capture as someday candidate with low priority
- "Thinking about maybe..." → skip (too vague)

### Third-party commitments (capture with "waiting on" flag)
- "Hannah said she'd send the invite" → `Waiting: Hannah to send invite — waiting on: Hannah, captured: [date]`
  - Write this to `waiting.md` instead of inbox.md

### Date parsing
- "by EOD" → interpret as today at 5pm
- "by EOW" → interpret as Friday
- "next week" → do not hardcode, write "next week" literally
- "ASAP" → priority: urgent, due: not specified
- "in two weeks" → calculate from capture date if possible

---

## Format Reminder

```
- [ ] [ACTION TEXT] — assigned to: [who], due: [when or "not specified"], assigned by: [who or "unknown"], priority: [urgent/normal/low], source: [tag], captured: [YYYY-MM-DD HH:MM]
```

Keep action text concise but complete. Verb first. "Send X to Y" not "There needs to be a sending of X".
