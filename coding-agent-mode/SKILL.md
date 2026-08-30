---
name: coding-agent-mode
description: Author specialized agent modes - role-based contexts that change tone, tools, and constraints (Code Reviewer, Architect, Client Demo, Security Auditor, etc.).
---

# coding-agent-mode

Use when the user wants their coding agent to behave differently for different *roles* of work — e.g. strict reviewer for PR review, expansive architect for design, conservative demoer for client demos.

## What a "mode" is

A named persona + behavior preset the agent activates on demand. Examples Bob ships with:
- **Plan** — explores, plans, doesn't write code yet
- **Code** — implements
- **Architect** — high-level design, ADRs
- **Code review** — strict, finds issues, doesn't refactor

You can add your own. Where supported (Cline, Bob), modes have:
- A **system prompt** layered on top of the default
- Sometimes **tool restrictions** (e.g. read-only for review mode)
- Sometimes **model overrides** (cheaper model for routine edits, smarter for architecture)

## Where they live

```
.agent/modes/
  code-reviewer.md
  architect.md
  client-demo.md
```

(Specific path depends on the agent. Consult your agent's docs.)

## Anatomy

```markdown
---
name: code-reviewer
description: Strict, evidence-driven PR reviewer. Finds issues; does not refactor.
tools_allowed: [read_file, grep, run_tests]
tools_denied: [edit_file, write_file, terminal_exec]
model: claude-opus-4-7  # optional override
---

# Code Reviewer Mode

## Role
You are an experienced senior engineer reviewing a pull request. You optimize for catching issues that would otherwise hit production. You do NOT refactor or write code in this mode.

## Output format
For each issue found, produce:
- **Severity**: blocker | major | minor | nit
- **File:line**
- **Issue**
- **Why it matters** (bug, perf, sec, maintainability, style)
- **Suggested fix** (description, not code)

End with a **Verdict**: approve | request-changes | block.

## Constraints
- Reference AGENTS.md and the Code Rules MCP server before flagging style issues — don't invent rules.
- If a complaint depends on context you don't have, say "need more info: <what>" instead of guessing.
- Limit minor/nit findings to the top 5 — don't drown the author.
```

## Mode design principles

- **One job per mode.** Mixing review + architect dilutes both.
- **Explicit do-nots.** Modes work as much by what they refuse as what they do.
- **Restrict tools** when the role is read-only (review, audit).
- **Override model** judiciously — only when the role really needs it (architect benefits from a stronger model; routine code can use a faster one).
- **Compose with workflows.** A workflow can call mode-X for step 3 and mode-Y for step 5.

## Common modes worth authoring

| Mode | Focus | Tools |
|---|---|---|
| `architect` | Design, ADRs, trade-offs | read-only + diagram tools |
| `code-reviewer` | PR review | read + tests, no edits |
| `client-demo` | Demos to clients | conservative; no internal-only references |
| `security-auditor` | OWASP / dependency review | read + dep scan, no edits |
| `documentation-writer` | Docs, READMEs, comments | read + edit on docs only |
| `migration-planner` | Library / framework migrations | read + sandboxed branch tools |

See `consulting-skills-samples/modes/` for ready-to-use copies.

## Switching modes

In Cline / Bob: a mode picker in the side panel, or a slash command (`/mode code-reviewer`). In Claude Code: invoke the matching skill (`/code-reviewer`).

Always announce the mode change in your first message back to the user so the user knows what shoes you've put on.

## Related skills
- `agents-md` — project rules a mode should respect.
- `coding-agent-workflow` — sequenced processes that may invoke modes.
- `bob-onboarding` — Bob's specialized modes are the canonical example.
