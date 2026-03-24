# Escalation Patterns — "Promised to Someone" Detection

## What Triggers Escalation

An item escalates (⚠️ flag + loud alert) when:
1. It is **overdue** (past due date or urgent + >48h old with no completion signal), AND
2. It was **promised to a named person** (not Alex to himself, not vague)

Escalation means: louder flag in report + iMessage notification regardless of notify setting.

---

## Patterns That Signal "Promised to Someone"

### Source field contains a known person
- `source: imessage:Jay:...` → committed in a conversation with boss
- `source: imessage:Hannah:...` → committed to girlfriend
- `source: imessage:Annika:...` → committed to co-parent (high stakes — Avie-related)
- `source: email:[from Jay's domain]:...` → email commitment to boss

### Assigned_by field contains a real person's name
- `assigned by: Jay` → boss asked for it
- `assigned by: Annika` → co-parenting obligation
- `assigned by: Hannah` → relationship commitment

### Action text contains commitment language + a name
Patterns (regex-style):
- `I told [Name] I'd...`
- `promised [Name]...`
- `[Name] is waiting for...`
- `owe [Name]...`
- `for [Name]...` (when combined with deadline)
- `[Name] needs this by...`
- `send [Name]...` with a due date

---

## Priority Escalation Tiers

| Who it's promised to | Escalation level |
|---------------------|-----------------|
| Jay (boss) | 🚨 CRITICAL — mention explicitly, always iMessage |
| Annika (co-parent, Avie-related) | 🔴 HIGH — affects Avie's schedule |
| External stakeholder / client | 🔴 HIGH |
| Hannah, friends, family | 🟡 MEDIUM — flag but softer tone |
| Alex himself (self-commitments) | No escalation |

---

## Known People to Watch For (From USER.md / TOOLS.md)

| Name | Context | Why it matters |
|------|---------|---------------|
| Jay | Alex's boss at ORNL | Work commitments = high stakes |
| Annika | Ex-wife, co-parent | Avie's schedule = non-negotiable |
| Hannah | Girlfriend | Relationship health |
| Sallijo / Sally Jo | Alex's mom | Family |
| Brad Greenfield | Professional contact | Business relationship |
| Avie | Daughter | Parenting — anything promised to/for her |

---

## Escalation Message Format

When escalating in the GSD Report:

```
⚠️ ESCALATION — PROMISED TO SOMEONE
[action text]
→ Who's waiting: [person]
→ How overdue: [N days] past [due date]  (or: "no deadline set, [N] days since captured")
→ Source: [where this was captured]
→ Recommended action: Send [person] a quick update, even if it's not done yet.
```

In iMessage escalation (keep it short):
```
⚠️ HEADS UP: You owe [person] — "[action]" — this is [N] days overdue. You should say something even if it's not done.
```

---

## Anti-Escalation (Don't Over-Alert)

Do NOT escalate for:
- Items in `waiting.md` (ball is in someone else's court)
- Items marked `low` priority that are < 7 days old
- Self-commitments with no named recipient
- Hypotheticals / "someday" items that leaked into the backlog

Use judgment. One escalation in a report = action-prompting. Five escalations = noise. If there are truly many escalations, group them and note "you have [N] overdue commitments to real people — here are the top 3."
