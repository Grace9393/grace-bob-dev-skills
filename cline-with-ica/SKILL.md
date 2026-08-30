---
name: cline-with-ica
description: Configure the open-source Cline VS Code extension to use IBM Consulting Advantage as its model backend - install, paste API key, choose model, verify.
---

# cline-with-ica

Use when an IBM consultant wants to use Cline (open-source AI coding agent) backed by ICA's models, instead of (or while waiting for) Bob.

## Why this combination
- **Cline** is open-source, transparent, runs entirely client-side, and supports any model provider via direct API.
- **ICA** provides the LLMs, governance, and asset catalog IBM Consulting requires.
- The pairing gives you a Bob-equivalent experience (and an easy migration path *to* Bob later).

> Note: Roo Code is a similar option but **sunsets 2026-05-15** — recommend Cline for any new setup.

## Prerequisites
- VS Code (latest stable).
- An ICA account with API access enabled.
- Network access to the ICA tenant; if behind a corporate proxy, configure VS Code's proxy settings first.

## Install Cline

1. VS Code → Extensions → search **"Cline"** → Install.
2. Open the Cline side panel (icon in the activity bar).
3. Click ⚙️ Settings.

## Generate the ICA API key

Follow `ica-api`:
- Settings → My Settings → API Keys → **Generate API Key** → copy and store.

## Configure Cline against ICA

In Cline settings:
1. **API Provider**: choose IBM Consulting Advantage (or "OpenAI Compatible" if no native option, with the ICA base URL).
2. **API Key**: paste the key from above.
3. **Base URL** (if asked): your ICA tenant base URL. Global: `https://servicesessentials.ibm.com/apis/v1`. Regional: `https://<region>.ica.ibm.com/ica/apis/v1` where `<region>` ∈ `{uki, us, remea, au, canada, japan, india, sg}`. The OpenAI-compatible endpoint is `<base>/chat/completions`; the ICA-native endpoint is `/apis/v3/executePrompt` (see `ica-api` skill). Confirm against your tenant's Swagger UI at `https://servicesessentials.ibm.com/apis/docs/swagger-ui/index.html`.
4. **Model**: pick from your team catalog. Common choices:
   - A larger model for `Plan` mode and architecture work.
   - A faster/cheaper model for routine edits.

You can override the model per-task in Cline's UI.

## Verify

Open a small repo and ask Cline:
> "Read package.json and tell me what frameworks this uses."

Expected: Cline reads the file, lists frameworks, no auth errors. If you get a 401, the API key wasn't saved or has rotated.

## Recommended ergonomics

- **Plan mode for any task > 30 min of work** — let Cline plan, review the plan, then approve.
- **AGENTS.md in the repo root** — standard place for project conventions; Cline reads it automatically. See `agents-md`.
- **MCP Rules Server** for cross-repo coding standards. See `mcp-rules-server`.
- **Workflow files** for repeatable multi-step tasks. See `coding-agent-workflow`.
- **Modes** for role-specialized prompting (reviewer, architect, etc.). See `coding-agent-mode`.

## Cost & quota
- ICA usage is metered per your team's subscription.
- The Cline UI shows token counts in real time — use it.
- For long-running agentic loops, set a token budget cap in Cline preferences.

## Migrating to Bob later
If/when you get Bob access:
- Bob's IDE is a VS Code derivative; settings carry over conceptually.
- Your AGENTS.md, workflows, modes, and MCP server configs all transfer with no changes.
- The only swap is the model provider/API key.

## Related skills
- `ica-api` — generate and rotate the key.
- `agents-md`, `coding-agent-workflow`, `coding-agent-mode`, `mcp-rules-server` — assets that make Cline+ICA dramatically more effective.
- `bob-onboarding` — the IBM-internal alternative.
