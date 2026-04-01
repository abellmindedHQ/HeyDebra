---
name: coding-agent
description: 'Delegate coding tasks to Codex, Claude Code, or Pi agents via background process. Use when: (1) building/creating new features or apps, (2) reviewing PRs (spawn in temp dir), (3) refactoring large codebases, (4) iterative coding that needs file exploration. NOT for: simple one-liner fixes (just edit), reading code (use read tool), thread-bound ACP harness requests in chat (for example spawn/run Codex or Claude Code in a Discord thread; use sessions_spawn with runtime:"acp"), or any work in ~/clawd workspace (never spawn agents here). Claude Code: use --print --permission-mode bypassPermissions (no PTY). Codex/Pi/OpenCode: pty:true required.'
---

# Coding Agent (bash-first) — Extended

This is a LOCAL OVERRIDE of the upstream coding-agent skill. It adds a two-stage review process.

For base usage (CLI flags, PTY modes, parallel patterns, etc.), see the upstream skill at:
`/opt/homebrew/lib/node_modules/openclaw/skills/coding-agent/SKILL.md`

Everything below is ADDITIONAL guidance layered on top of upstream.

---

## Two-Stage Review Process

For any coding task estimated at **30+ minutes** (or touching 5+ files), follow this process:

### Stage 1: Spec Validation (BEFORE coding starts)

Before spawning a coding agent, write a brief spec:

```markdown
## Task Spec: [title]
**Goal:** [what we're building/changing]
**Files affected:** [list known files]
**Acceptance criteria:**
- [ ] [criterion 1]
- [ ] [criterion 2]
- [ ] [criterion 3]
**Out of scope:** [what NOT to touch]
**Estimated effort:** [time/complexity]
```

Save to: `/tmp/task-spec-[short-name].md`

Include the spec in the agent prompt:
```
Read the spec at /tmp/task-spec-[name].md. Implement ONLY what's in scope.
When done, verify each acceptance criterion and report status.
```

### Stage 2: Post-Completion Review (AFTER coding finishes)

After the coding agent completes, run TWO review passes:

**Pass 1 — Spec Compliance:**
- Does the output match every acceptance criterion?
- Did the agent stay in scope? (check git diff for unexpected changes)
- Are there files modified that weren't in the spec?

```bash
# Quick diff check
cd [project] && git diff --stat
```

**Pass 2 — Code Quality:**
- Spawn a FRESH agent (not the same session) for review:
```bash
cd [project] && claude --permission-mode bypassPermissions --print \
  "Review the changes in this repo (git diff HEAD~1). Check for:
   1. Bugs or logic errors
   2. Security issues (hardcoded secrets, SQL injection, etc)
   3. Missing error handling
   4. Code style consistency
   Report issues as a numbered list. If clean, say 'LGTM'."
```

**If issues found:** Fix them before committing/pushing. Respawn coding agent with specific fix instructions.

**If clean:** Proceed with commit/PR.

---

## Fresh Agent Per Task

- **DO NOT reuse sessions** for independent coding tasks
- Each task gets its own agent spawn with its own context
- This prevents context pollution and "ghost memory" from prior tasks
- For parallel tasks, use git worktrees (one worktree per agent)

---

## CWD Scoping

- **ALWAYS set explicit `workdir`** to the project directory
- Never let a coding agent run from home (~) or workspace root
- Agent should see ONLY the project it's working on

---

## Quick Tasks (Under 30 min)

For quick tasks (< 30 min, < 5 files), skip the formal spec. Just:
1. Spawn agent with clear prompt
2. Check the diff when done
3. Commit if it looks good

The two-stage process is for SUBSTANTIAL work only. Don't over-process a one-liner.

---

## ⚠️ Claude Code git reset Bug (v2.1.87)

Claude Code v2.1.87 silently runs `git reset --hard origin/main` every ~10 min.
This DESTROYS uncommitted changes to tracked files.
- Untracked files and git worktrees are immune
- ALWAYS: commit frequently, verify CC version
- Use git worktrees for isolation on important repos
- Monitor: https://github.com/anthropics/claude-code/issues/40710
