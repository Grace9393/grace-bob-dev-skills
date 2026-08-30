---
name: grace-skills
description: >
  Gateway to the 216-skill library built from seven Grace9393 repositories —
  dbskill (商业诊断 / 内容), khazix-skills (横纵分析, 写作, 任务书), openakita,
  superset (multi-agent CLI orchestration), notebooklm-skill, crawl4ai, and
  finger-frame-effect-lucy. Use this skill to find which of those skills fits a
  request, to install or uninstall a subset, or to decide which Claude model a
  skill's work should run on. Trigger on: "有沒有現成的 skill", "dbs", "横纵分析",
  "notebooklm", "crawl4ai", "openakita", "superset orchestration", "帮我写任务书",
  "which skill should I use", "install these skills", "run this on the right
  model", "auto switch model", or any mention of the seven repos by name.
metadata:
  sources: 7 Grace9393 repositories
  skills: 214 discovered + 2 authored
  built: 2026-08-07
  related: model-router, skill-catalogue
---

# Grace skills — one door, 216 skills, model-aware

Seven repositories were scanned; every `SKILL.md` in them is catalogued in
`references/catalogue.md` with **two labels attached to each row**: whether it
can actually run here, and which model tier its work belongs on.

## Do not install all of them

214 discovered skills is not a library, it is a routing hazard. 386 plugin
skill descriptions already load at the start of every session; another 214
degrades the match quality for all of them. Install a profile, not the world.

## Step 1 — find the skill

Never `Glob`/`Grep` the AA root for this. Query the generated index:

```bash
python "H:/My Drive/AA/grace-skill-pack/grace-skills/scripts/install_skills.py" --list
```

or read `references/catalogue.md`, which is grouped by source and shows every
skill's model tier and portability inline. `index.json` at the pack root is the
machine-readable version of the same data.

## Step 2 — check portability before promising anything

Only 59 of the 216 are usable here. The catalogue labels each one:

| Label | Count | Meaning |
|---|---:|---|
| `portable` | 57 + 2 authored | Self-contained. Install and use. |
| `needs-host` | 56 | The prose transfers; the tool calls do not. Needs an OpenAkita account, a China-platform API key (Baidu / Tencent / 阿里 / 抖音 / 小红书), or an MCP server that is not connected. Read it for method, do not expect it to run. |
| `host-builtin` | 77 | `openakita/skills/system/*` — wrappers around OpenAkita's own tool surface (`read-file`, `glob`, `grep`, `browser-click`, `run-shell`). Claude Code has these natively. Installing them creates collisions and buys nothing. **Never install.** |
| `duplicate` | 20 | Already available via `anthropic-skills` (docx, pdf, pptx, xlsx, canvas-design, skill-creator, mcp-builder, theme-factory, …). Installing shadows the maintained copy. |
| `repo-local` | 4 | `superset/.agents/*` — conventions that only mean something inside that repository. |

State the label when you recommend a skill. "Use `baidu-deep-research`" is
wrong if the user has no Baidu key; "`baidu-deep-research` describes a good
method but needs an OpenAkita account — here is the method" is right.

## Step 2b — check the licence separately

`portable` answers "will it run", **not** "may I use the output". Those come
apart badly here. Across the 57 portable skills:

| Licence class | Count | Billed client work |
|---|---:|---|
| `permissive` (MIT, Apache-2.0) | 8 (+`crawl4ai`) | Yes — attribution only |
| `noncommercial` (CC BY-NC 4.0 — all of dbskill) | 30 | **No.** Personal and learning only |
| `copyleft` (AGPL-3.0 — openakita) | 17 | Legal review before any client-facing use |
| `proprietary` (Elastic-2.0 — superset) | 2 | Read the restrictions |

The strongest content in the pack — the 30 dbskill 商业诊断 / 内容 skills — is
the part that is **not licensed for billed work**. Say so when recommending one
for an engagement; do not discover it at delivery.

Licence is detected **per skill**, not per repo: 14 openakita skills ship their
own Apache-2.0 LICENSE and are marked `*` in the catalogue. The
`finger-frame-effect-lucy` upstream ships no licence at all, so its authored
skill is `unlicensed` — reference only.

Full table and the reasoning: `references/sources.md`.

## Step 3 — route the model

Full rules and the honest limits: `references/model-routing.md`.
The catalogue's `Model` column already carries the verdict for every skill.

The one-line summary — route on **cost of being wrong**, not on how important
the project feels:

| Tier | When | Skills in this pack |
|---|---|---|
| **haiku** | One right answer, checkable in seconds, high volume | 13 — `dbs-ai-check`, `dbs-xhs-title`, `dbs-save`, `neat-freak`, `storage-analyzer`, `translate`, `aihot`, … |
| **sonnet** | Default. Real work with a human in the loop | 34 — the dbs diagnostic cluster, `khazix-writer`, `notebooklm-research`, `ppt-creator`, … |
| **opus** | Runs unattended many steps, or a wrong answer is expensive to undo | 10 — `leader`, `hv-analysis`, `dbs-agent-migration`, `dbs-knowledge`, `crawl4ai`, `superset-orchestration`, … |
| **fable** | Opus 5 already failed twice with a complete prompt | 0 by default — escalation only |

### What "auto switch" can and cannot mean

**No skill can change the model of the conversation it is already running in.**
Anyone who tells you otherwise is describing a feature that does not exist.
What this pack does instead:

| Surface | How the tier is applied |
|---|---|
| A subagent | **Automatic.** Four model-pinned agents ship in `agents/` — `gsp-haiku-bulk`, `gsp-sonnet-standard`, `gsp-opus-deep`, `gsp-fable-escalation`. Install them with `--agents` and the Agent tool honours their `model:` frontmatter with no further instruction. |
| A workflow stage | **Automatic.** `agent(prompt, {model, effort})` per stage, read from the catalogue. |
| Generated API code | **Automatic.** The model ID and effort go into the request. |
| The current chat session | **Manual.** State the verdict in one line — `→ Opus 5, effort high — leader writes a brief another agent runs blind` — and the user runs `/model`. Do not switch mid-conversation to save money: caches are model-scoped, so the switch throws away the cached prefix and you pay to rebuild it. |

So the working pattern is: **keep the session where it is and delegate the skill
to the right-tier subagent.** That is the switch that actually happens.

Each installed `SKILL.md` also carries `metadata.model` / `metadata.effort` and
a one-line banner, so the tier travels with the skill rather than living only
in this catalogue.

## Step 4 — install

```bash
python "H:/My Drive/AA/grace-skill-pack/grace-skills/scripts/install_skills.py" --profile core --target claude --agents
```

Profiles live in `profiles.json` (edit that, not the script):
**`client-safe` (9 — the only set cleared for billed work)** · `core` (12) ·
`business-diagnosis` (12) · `content` (12) · `research` (7) ·
`agent-building` (12) · `media` (3) · `all-portable`.

For an engagement, use both the profile and the gate — the gate is what
actually enforces it:

```bash
python … install_skills.py --profile client-safe --target both --commercial-only
```

`--commercial-only` refuses anything not MIT / Apache-2.0 / BSD and prints why.
Without it, non-permissive installs still go through but are flagged `⚠` with
their licence on every line.

`--target claude|bob|both`, `--dry-run`, `--uninstall`, `--audit`,
`--skill <id>…`, `--force` (to install a non-portable one anyway).
Bob's skill directories are `~/.bob/skills` and `<project>/.bob/skills`.

The installer will **not overwrite a skill it did not install** — it reports
`skip … exists and is not ours` and leaves it alone. If that fires, decide
deliberately; do not reach for `--force` reflexively.

The installer is not a copy — it rewrites frontmatter. 85 openakita skills carry
namespaced names like `openakita/skills@brainstorming`, which Claude Code cannot
load; the installer flattens them to the short id, makes the directory match,
and stamps the model tier.

## Refreshing

Sources are cached **off** the Google Drive mount, at
`%LOCALAPPDATA%\grace-skill-pack\sources` — ~250k files at ~10 ms per stat is
not something to put on H:.

```bash
python "H:/My Drive/AA/grace-skill-pack/grace-skills/scripts/sync_sources.py"
python "H:/My Drive/AA/grace-skill-pack/grace-skills/scripts/build_catalogue.py"
```

`catalogue.md` and `index.json` are generated. Do not hand-edit them; change the
classification rules in `build_catalogue.py` and rebuild.

## Reference

- `references/catalogue.md` — all 214 discovered skills, by source, with tier and portability.
- `references/sources.md` — what each of the seven repos actually is, licence, and what it costs to use.
- `references/model-routing.md` — the tier rules, effort dial, mixed-tier pipelines, and anti-patterns.
- `../new-skills/` — the two repos that shipped no `SKILL.md`; skills authored here.
