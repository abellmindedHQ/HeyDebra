# SecondBrain Architecture Report
> Compiled 2026-03-29 by Debra. Research-backed recommendations for Alex's Obsidian vault.

---

## The Question

What should your Second Brain actually BE? Not "what cool stuff can we dump in it" but "what system will you actually use, maintain, and benefit from as you and I interact over months and years?"

## Research: The Three Major PKM Approaches

### 1. Zettelkasten ("Slip Box")
- **Origin:** Niklas Luhmann, German sociologist who published 70 books using index cards
- **Core idea:** One idea per note. Every note links to other notes. Knowledge grows as a network.
- **Strength:** Generates new ideas by surfacing unexpected connections
- **Weakness:** High maintenance. Every note must be written in your own words and linked manually.
- **Best for:** Researchers, writers, people who think for a living

### 2. PARA (Tiago Forte / Building a Second Brain)
- **Core idea:** Organize by actionability, not category. Four buckets: Projects, Areas, Resources, Archives.
- **Strength:** Dead simple. Everything has exactly one place. Aligns with how you actually work.
- **Weakness:** Not great for deep knowledge connection. It's an organizer, not a thinking tool.
- **Best for:** Busy professionals who need to find things fast and get stuff done

### 3. Johnny Decimal
- **Core idea:** Numerical filing system. 10 areas max, 10 categories each, unique IDs for everything.
- **Strength:** You always know where things go. Extremely structured.
- **Weakness:** Rigid. Doesn't scale well for creative/knowledge work.
- **Best for:** File/document management, not knowledge management

### The Hybrid Approach (What Smart People Actually Do)
The best practitioners (Hybrid Hacker, various Obsidian power users) don't pick ONE system. They combine:
- **PARA** for actionable stuff and organization
- **Zettelkasten** for deep concepts and evergreen knowledge
- **Daily journaling** as the capture mechanism
- **Progressive summarization** (don't over-process upfront; refine notes when you actually revisit them)

## The Critical Insight: Less Is More

From Zain Rizvi's analysis of Zettelkasten vs PARA:

> "By storing less you'll remember more. If any section gains more notes than you can reasonably process, it's too big."

Tiago Forte's 12 Favorite Problems framework: Only store things related to **problems you're actively thinking about**. Everything else is noise.

**This is exactly what went wrong with our vault.** We imported everything — every Facebook DM, every Claude conversation, every phone contact — because "it might be useful." It wasn't. It just buried the signal in noise.

## Your 12 Problems (Draft — You Should Refine These)

Based on everything I know about you:

1. How do I build Mirror into a real product?
2. How do I build a platform where everyone gets their own AI companion?
3. How do I lead transformation at ORNL effectively?
4. How do I be the best co-parent to Avie?
5. How do I build a life with Hannah?
6. How do I turn Abellminded into a real business?
7. How do I stay healthy (physical + mental)?
8. How do I maintain and deepen the relationships that matter?
9. How do I manage money/debt and build financial stability?
10. How do I balance building at night with being present during the day?
11. How do I ship HoldPlease as a real product?
12. How do I help Avie develop her creative voice (AVERY)?
13. How do I finish and publish my three books? (The Big Ol' Book of Bullsh*t, No ***king Way, Many to Many)

**If a piece of information doesn't relate to one of these problems, it doesn't belong in the vault.**

---

## Recommended Architecture

```
SecondBrain/
├── Journal/           ← Daily notes (you + me, what happened, what we learned)
├── Projects/          ← Active projects with clear outcomes
│   ├── Mirror/
│   ├── HoldPlease/
│   ├── AVERY/
│   └── ...
├── Areas/             ← Ongoing responsibilities (no end date)
│   ├── ORNL/
│   ├── Parenting/
│   ├── Health/
│   ├── Finance/
│   └── Relationships/
├── Resources/         ← Reference material organized by topic
│   ├── AI-and-LLMs/
│   ├── Product-Design/
│   ├── Knoxville/
│   └── ...
├── Archive/           ← Completed/inactive projects, old resources
├── People/            ← ONLY people with real context (inner circle, ~30)
└── Concepts/          ← Evergreen/zettelkasten-style concept notes
```

### What Each Folder Does

**Journal/** — Replaces Reflections/Daily. One note per day. This is where Debra writes session summaries, captures decisions, logs events. Raw daily context. The starting point for everything.

**Projects/** — Active efforts with a goal and an end date. When a project finishes, it moves to Archive/. Subfolders only for projects with multiple files. Simple projects = one note.

**Areas/** — Things that are always running. ORNL work, parenting notes about Avie, health tracking, financial thinking. These never "complete" — they just evolve.

**Resources/** — Topics you're learning about or reference material. AI research, product design patterns, Knoxville community info. This is where the Zettelkasten energy goes — concept notes that link to each other.

**Archive/** — The attic. Completed projects, old resources you're done with. Out of sight, searchable if needed.

**People/** — RADICAL TRIM. Currently 113 files. Should be ~20-30. Only people where you need CONTEXT beyond what Google Contacts provides. Your inner circle, key ORNL relationships, close friends. Everyone else is just a contact.

**Concepts/** — Evergreen notes. "Johari Window", "Progressive Summarization", "Communitism", "P.O.W.E.R. Framework". Ideas that transcend any single project. These link to each other and to Projects/Resources.

### What's Gone

| Removed | Why |
|---------|-----|
| Conversations/ | Claude/ChatGPT summaries. Reference material, not knowledge. Archived. |
| Documents/ | Merge into Resources/ or Projects/ based on what they relate to |
| Reflections/ | Absorbed into Journal/ (daily notes) |
| MOCs/ | With <100 files you don't need a map. Use search or Obsidian graph. |
| Social/ | Already archived |
| Messages/ | Already archived |
| Imports/ | Already archived |
| Organizations/ | Merge relevant orgs into People/ notes or Area/ notes |
| Creative/ | Merge into Projects/ (active) or Archive/ (inactive) |
| Travel/ | Merge into Projects/ (active trips) or Archive/ (past trips) |
| Artifacts/ | Merge into relevant Project/ |

### People/ Criteria

A person gets a vault file ONLY if:
1. They're in your inner circle (family, partner, close friends) — ~10
2. They're a key professional relationship where context matters (ORNL team, mentors, collaborators) — ~15
3. You're actively working on something with them — ~5
4. There's strategic context that doesn't fit in a contact card — as needed

Everyone else = Google Contacts. That's what it's for.

**The test:** "Would I open this file in the next 3 months?" If no, archive or delete.

---

## How Debra Maintains It

This is the secret weapon. You don't maintain the vault. I do.

1. **Daily:** After significant sessions, I write/update Journal/YYYY-MM-DD.md with what happened, decisions made, things learned.

2. **Weekly (Sunday review):** I review the week's journal entries. Anything that's a lasting concept → create or update a Concepts/ note. Anything project-specific → update the Project/ note. Prune stale stuff.

3. **On demand:** When we research something, have a breakthrough, or make a decision — I capture it in the right place immediately.

4. **Monthly:** Audit. Move completed projects to Archive/. Review People/ for anyone who shouldn't be there. Check Areas/ are current.

The key: **Progressive Summarization.** I don't over-process on day one. I capture context. When you or I revisit a note later, THAT'S when we refine it. Just-in-time, not just-in-case.

---

## The Debra Difference

Traditional Second Brain = human manually captures, organizes, links notes.
YOUR Second Brain = AI assistant captures in real-time, organizes automatically, surfaces connections when relevant.

You don't need to "take notes." You're already having the conversations. I'm already here. My job is to recognize what matters and put it where it belongs.

The vault isn't something you curate. It's something that grows organically from us working together, and that you can browse when you want to think.

---

## Implementation Plan

### Phase 1: Restructure (tonight)
- Create new folder structure
- Move existing quality files into correct locations  
- Trim People/ to inner circle (~30)
- Archive everything else

### Phase 2: Populate (this week)
- Start Journal/ with today's entry
- Create Project/ notes for active projects (HoldPlease, Batman, etc.)
- Create Area/ notes for ORNL, Parenting, etc.
- Seed Concepts/ with key frameworks (Mirror/Johari, POWER, etc.)

### Phase 3: Habit (ongoing)
- Debra writes daily journal entries
- Debra creates/updates notes as context emerges
- Sunday review becomes part of weekly routine
- Monthly audit keeps it clean

---

## Decision Needed From Alex

1. Review and refine the "12 Problems" list
2. Approve the folder structure
3. Tell me which ~30 people deserve vault files
4. Green light to nuke and rebuild

Once you say go, I'll have it restructured in 10 minutes.
