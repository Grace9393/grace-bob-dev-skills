---
name: mcp-rules-server
description: Install and use the Code Rules MCP Server - centralized, GitHub-backed coding rules served over MCP to Cline, Bob, Claude Code, and other MCP-capable agents.
---

# mcp-rules-server

Use when the user wants consistent coding rules enforced across teams, asks "where should our coding standards live", or wants their AI agent to follow framework-specific rules.

## What it is

The **Code Rules MCP Server** is an internally-developed MCP server that exposes a curated GitHub repository of coding rules to any MCP-capable agent. It's part of the IBM Consulting Guild of Coding Agents.

- **Repo**: <https://github.ibm.com/guild-of-coding-agents-at-consulting/mcp-rules-server> (IBM internal)
- **Lightweight**, modular, cloud-friendly.

## Why use it (vs an AGENTS.md file)
- AGENTS.md scopes per-project. Rules MCP scopes **organization-wide**.
- Pulls only rules relevant to the current project (categories: web/backend/mobile; frameworks: React/Angular/Vue/etc.).
- Centralized: update once, propagate everywhere.
- Versioned: tag stable rule sets per language/framework.
- Use both — AGENTS.md for project-specific overrides, MCP Rules for shared baseline.

## Install (high level)
1. Clone or pull the server image per the server repo's README.
2. Configure the GitHub backing repo URL (the rules source).
3. Run the server (stdio or SSE transport, per agent compatibility).
4. Add an entry to your agent's MCP config:
   - **Cline**: `cline_mcp_settings.json`
   - **Claude Code**: `~/.claude/mcp.json` (or project `.mcp.json`)
   - **Bob**: per Bob's MCP config UI
5. Restart the agent; verify the server appears in the agent's MCP tool list.

(Always check the server README for the current invocation — args evolve.)

## Tools the server exposes (typical)

| Tool | What it does |
|---|---|
| `list_categories` | Top-level rule buckets (web, backend, mobile, …) |
| `list_frameworks` | Frameworks under a category |
| `get_rules` | Pull rules for a specific framework/category |
| `search_rules` | Keyword search across the rule corpus |
| `save_rules_to_project` | Write retrieved rules into the current workspace |

## Authoring rules

Rules are markdown files in the backing GitHub repo. Best practices from the Cline Guild docs:
- **Focused** — one rule per file, one concern per rule.
- **Versioned** — tag releases (`v1.0`, `v1.1`) so teams can pin to stable versions.
- **Reviewed** — PR-based; require sign-off from the rule's owning framework lead.
- **Updated** — retire stale rules; track currency in repo README.
- **Searchable** — front-matter with tags so `search_rules` returns useful matches.

## Use patterns

- **Onboarding** — new dev's agent calls `list_frameworks`, `get_rules` for their stack on day one.
- **Pre-commit** — workflow file (see `coding-agent-workflow`) pulls relevant rules before generating code, enforces them in review.
- **Cross-stack consistency** — same security/logging/error-handling rules surface across React, Spring, FastAPI, etc.

## Fit with ICA

- Use **MCP Rules Server** for cross-team coding rules.
- Use **ICA Context Studio** (see `ica-context-studio`) for project-specific knowledge graphs.
- They're complementary — an agent should have both wired up on a typical engagement.

## Related skills
- `agents-md` — per-project complement to org-wide rules.
- `cline-with-ica`, `bob-onboarding` — agents that consume this server.
- `ica-context-studio` — sibling MCP source for project context.
