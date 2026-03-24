# GTD Triage Guide — Inbox → Backlog/Waiting/Someday

## The Triage Decision Tree

For each `- [ ]` item in `inbox.md`, ask these questions in order:

```
1. Is this actionable?
   NO  → Is it reference? → Archive/delete. Is it "someday"? → someday.md
   YES → continue

2. Can it be done in < 2 minutes?
   YES → Do it now (don't even add to backlog, just DO it and log to done.md)
   NO  → continue

3. Am I the one who needs to do it?
   NO  → waiting.md ("waiting on: [person]")
   YES → continue

4. Does it belong to a project?
   YES → Tag it with the project name in backlog.md
   NO  → Treat as standalone task

5. What's the priority?
   URGENT  → 🔴 section of backlog.md
   NORMAL  → 🟡 section of backlog.md
   LOW     → 🔵 section of backlog.md
```

---

## Priority Definitions

### 🔴 URGENT
- Has a real deadline within 7 days
- Was promised to a named person and is past due
- Blocks Alex from something else that's urgent
- Tagged with: ASAP, EOD, EOW, "needs to happen today/this week"

### 🟡 NORMAL
- Should get done but won't cause a crisis if delayed a few days
- No explicit deadline but clearly expected "soon"
- Related to an ongoing project that's active

### 🔵 LOW
- Nice to have
- Background improvements
- No commitment to anyone else
- Vague "someday" phrasing but specific enough to be actionable

---

## Someday vs. Low Priority

**Someday (someday.md):** Not actively working on this. No one's waiting. Would be great to do eventually. Park it and review monthly.
- "Learn Rust some day"
- "Set up a home NAS eventually"
- "Would be cool to build a [thing]"

**Low priority (backlog.md 🔵):** Still real. Still on the hook. Just not urgent. Will do when higher-priority work clears.
- "Refactor that gnarly CSS file"
- "Update the onboarding doc"
- "Check in with Brad about the intro he offered"

---

## Waiting Items Format

When something goes to `waiting.md`:

```markdown
- [ ] [what you're waiting for] — waiting on: [person], since: [date], context: [why/what you asked for], follow up by: [date if applicable], source: [original source]
```

**Follow-up rule:** If something has been in `waiting.md` for > 5 days and has a `follow up by` date that's passed → gsd-agent should flag it as stale.

---

## Backlog Item Format

Standard format for backlog items (expanded from inbox capture):

```markdown
- [ ] [ACTION] — project: [project or "standalone"], due: [date or "none"], priority: [urgent/normal/low], assigned to: [Alex or other], assigned by: [who or "self"], source: [original source], captured: [date], updated: [date if edited]
```

---

## Common Triage Mistakes to Avoid

❌ **Over-capturing:** Not every "we should" is a task. If there's no person committed to it, it may not be an action item.

❌ **Under-dating:** Always try to infer a soft deadline even when not explicit. "Before the sprint ends" = [sprint end date]. "When you get a chance" = +7 days.

❌ **Skipping someday:** Don't delete "nice to have" items — they represent real intentions. Park them in someday.md so they're not lost.

❌ **Leaving inbox stale:** Inbox is a catch-all, not a parking lot. If something sits in inbox > 48h untriaged, gsd-agent will flag it.
