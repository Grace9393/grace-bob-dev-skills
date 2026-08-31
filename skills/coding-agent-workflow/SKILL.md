---
name: coding-agent-workflow
description: Author multi-step workflow files for coding agents - codify repeatable processes (feature development, bug triage, release prep) so the agent runs them consistently.
---

# coding-agent-workflow

Use when the user wants to make a multi-step process repeatable: feature dev, bug triage, deploy checklist, client deliverable prep, etc.

## What a workflow is

A markdown file (or set of files) that describes a **named, multi-step process** the agent should follow when invoked. Distinct from:
- **AGENTS.md** — *standing* rules (how we code here).
- **Modes** — *role* contexts (act as reviewer / architect).
- **Workflows** — *processes* (do steps 1..N for goal G).

## Where they live

Conventionally:
```
.agent/workflows/
  feature-development.md
  bug-triage.md
  client-deliverable-prep.md
```

Or wherever your agent looks (Cline supports a `.cline/workflows/` folder; Claude Code looks under `~/.claude/skills/` which can wrap workflows).

## Anatomy

```markdown
---
name: feature-development
description: Plan, implement, test, and document a new feature end-to-end.
trigger_examples:
  - "implement <feature>"
  - "add a new <type> for <thing>"
---

# Feature Development Workflow

## Inputs
- Feature description (1-3 sentences from user)
- (Optional) Linked ticket / spec

## Steps

### 1. Plan
- Read AGENTS.md and any sub-scope AGENTS.md.
- Identify affected modules; sketch the change.
- Output: bullet plan with files to touch and risks. Pause for user approval.

### 2. Implement
- Make changes module by module.
- Keep diffs surgical — don't refactor unrelated code.
- After each module: run unit tests for the touched files only.

### 3. Test
- Add or update tests to cover the new behavior.
- Run full test suite; fix regressions.
- If integration tests exist, run them locally if cheap; flag if not.

### 4. Document
- Update README / API docs if public surface changed.
- Add entry to CHANGELOG (if the project has one).
- Update AGENTS.md if a new convention emerged.

### 5. Wrap up
- Summarize what changed, files touched, tests run, residual TODOs.
- Suggest a commit message and (if asked) open a PR with that body.

## Constraints
- Never push to main / master.
- Never run destructive git commands without explicit user OK.
- Stop and ask if the plan in step 1 reveals scope > 4 hours.
```

## Design principles

- **Idempotent** — re-running shouldn't corrupt state. Use guards ("if AGENTS.md already lists this convention, skip").
- **Has explicit pause points** — for high-blast-radius steps (file deletion, migration, push), pause for human OK.
- **Small Inputs section, big Steps section.** Don't ask for inputs you don't need.
- **Names trigger phrases** — list a few example user phrases the workflow handles, so agents can match correctly.

## Common workflows worth authoring

| Workflow | Inputs | Output |
|---|---|---|
| `feature-development` | feature description | working branch with tests + docs |
| `bug-triage` | bug report / failing test | reproduction + diagnosis + fix plan |
| `release-prep` | version bump | changelog, version files, PR |
| `client-deliverable-prep` | deliverable type | sanitized doc draft + checklist |
| `dependency-upgrade` | package + target version | upgrade PR with smoke tests |

See `consulting-skills-samples/workflows/` for ready-to-use copies.

## Related skills
- `agents-md` — standing rules the workflow references.
- `coding-agent-mode` — role contexts that may be invoked inside a workflow.
- `mcp-rules-server` — pull authoritative rules during the workflow's plan step.
