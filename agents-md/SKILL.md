---
name: agents-md
description: Author an AGENTS.md file - the standard for giving coding agents (Cline, Bob, Claude Code, Roo) the project-specific instructions, conventions, and context they need.
---

# agents-md

Use when the user wants to standardize how coding agents behave on a specific repo, or asks "why did the agent ignore our coding style".

## Why AGENTS.md exists

`README.md` is for humans. `AGENTS.md` is for coding agents:
- A predictable place agents look for project-specific guidance.
- Keeps the README clean and human-focused.
- Encodes detailed technical context that doesn't belong in the README.

The `agents.md` standard is documented at <https://agents.md/>.

## Where to put it

- Repo root: `AGENTS.md`
- Optional sub-scopes: `services/payments/AGENTS.md` for service-specific overrides
- Agents merge them: closest-AGENTS.md to the file being edited wins

## What goes in it

A well-structured AGENTS.md has these sections (omit any that don't apply — but be honest about what you have):

```markdown
# <Project name> Agent Guide

## Role
What kind of work the agent will primarily do here.

## Stack
- Language(s) and versions
- Major frameworks
- Build tool, package manager
- Database, message broker, cache
- Cloud / runtime target

## Coding Standards
- Style guide reference (PEP 8, Google Java, etc.)
- Naming conventions
- Line length, formatter (black, prettier, gofmt)
- Type-hint / type-safety expectations
- Linting rules

## Architecture
- Layering (controller / service / repo, hex, clean, etc.)
- Where domain models live
- How to add a new feature (folder layout)
- Patterns to use (repository, factory, DI, etc.)
- Patterns to avoid

## Testing
- Test framework
- Coverage minimum
- Where unit vs integration tests live
- How to run them locally and in CI

## Build / Run
- Commands to install, build, test, run
- Required env vars (point to .env.example, never check in real values)

## Domain knowledge
- Vocabulary (acronyms, terms specific to the business)
- Hard-won constraints ("don't ever cache the order endpoint — see incident #482")

## Out of scope
- Files / paths the agent must not modify
- External services that should never be called from this repo

## When in doubt
- Who to ask (Slack channel, code-owner)
- Where the architecture decision records live
```

## Authoring tips

- **Be specific.** "Use clean code" is useless. "Functions over 30 lines must be broken up" is testable.
- **Cite incidents.** "Don't add a synchronous DB call in the request path — see incident 2025-Q3-082." Agents and humans both benefit from the *why*.
- **Update on PRs.** Treat AGENTS.md as code: review changes, version-control, blame-trace.
- **Keep it tight.** Agents have context budgets. <2000 tokens is comfortable; >5000 starts to compete with the user's actual request.
- **Test it.** Before merging, ask the agent to do a representative task and see whether it follows the file.

## Asset hierarchy (where AGENTS.md fits)

| Asset | Scope | Updates | Best for |
|---|---|---|---|
| **AGENTS.md** | Project / repo | Low–Medium | Coding standards, conventions, domain knowledge |
| Workflows | Task / process | Medium | Repeatable processes, feature dev, deploy |
| Modes | Agent behavior | Low | Role-specific contexts (reviewer, architect, demoer) |
| Skills | Domain / tech | Low–Medium | Tech-stack expertise, design patterns |
| MCP Servers | Integration | Low | API access, external tools, data sources |
| Guidance docs | Org | Low | Architecture decisions, security policy, processes |

(Source: the Cline Guild's "Agentic Assets" overview.)

## Related skills
- `coding-agent-workflow` — multi-step processes that complement standing rules.
- `coding-agent-mode` — role-specialized agent contexts.
- `mcp-rules-server` — org-wide rules as an MCP source, complementary to AGENTS.md.
