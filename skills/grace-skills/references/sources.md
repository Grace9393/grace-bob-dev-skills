# The seven sources

All seven are forks under `github.com/Grace9393`. Cached locally at
`%LOCALAPPDATA%\grace-skill-pack\sources` — never on the H: Drive mount.

## Licence — read this before any client use

Licences differ sharply, and three of the seven restrict exactly the use Grace's
work implies. This is not a formality.

| Repo | Licence | What it means for consulting work |
|---|---|---|
| `dbskill` | **CC BY-NC 4.0** | **Non-commercial.** Using these 30 skills to produce a billed client deliverable is outside the licence. Fine for personal use and learning. Get written permission before it touches an engagement. |
| `openakita` | **AGPL-3.0** | Strong copyleft, and the network clause triggers on *hosted* use, not just distribution. Do not vendor its code into anything client-facing without legal review. Reading a skill for its method carries no obligation; copying its code does. |
| `superset` | **Elastic License 2.0** | Not open source. Bars providing the software to third parties as a managed service, and bars removing licence key functionality. |
| `khazix-skills` | MIT | Unrestricted, attribution only. |
| `notebooklm-skill` | MIT | Unrestricted, attribution only. |
| `crawl4ai` | Apache-2.0 | Unrestricted, attribution + patent grant. |
| `finger-frame-effect-lucy` | **No LICENSE file** | Default is all rights reserved. It is a fork of `sophiamyang/finger-frame-effect-lucy`; upstream has not granted rights. Treat as read-only reference until a licence appears. |

The `portable` label in `catalogue.md` is a **technical** judgement — will it run
here. It says nothing about whether you are allowed to use the output. Check
this table separately.

---

## dbskill — 30 skills · CC BY-NC 4.0

`dontbesilent` 的商业工具箱. Simplified Chinese throughout. A router skill
(`dbs`) plus 29 specialists across four clusters:

- **诊断** — `dbs-diagnosis`, `dbs-deconstruct` (Wittgenstein + Austrian
  economics on fuzzy business concepts), `dbs-action` (Adlerian read on why
  someone knows what to do and isn't doing it), `dbs-benchmark`, `dbs-decision`
- **内容** — `dbs-content`, `dbs-hook`, `dbs-resonate`, `dbs-script-flow`,
  `dbs-spread`, `dbs-xhs-title`, `dbs-wechat-html`, `dbs-ai-check`
- **知识/状态** — `dbs-knowledge`, `dbs-content-system`, `dbs-save` /
  `dbs-restore` / `dbs-report` (cross-session state on disk)
- **Agent 工程** — `dbs-goal`, `dbs-good-question`, `dbs-bridge`,
  `dbs-agent-migration`, `dbs-skill-cleaner`

All 30 are technically portable. The whole set is the strongest material in the
pack **and** the one with the licence problem — that combination is the reason
this file exists.

## openakita — 171 skills · AGPL-3.0

A full agent platform, not a skill library. Its `SKILL.md` files split three ways
and only the first is worth installing:

| Subtree | Count | Verdict |
|---|---:|---|
| `skills/` | 77 | 16 portable. The rest are China-platform connectors (Baidu, Tencent, 阿里, 抖音, 小红书, 网易, 哔哩哔哩) needing platform keys, or duplicates of Anthropic's bundled skills. |
| `skills/system/` | 77 | **Never install.** Wrappers around OpenAkita's own tool surface — `read-file`, `glob`, `grep`, `run-shell`, `browser-click`, `desktop-*`. Claude Code has all of these natively; installing them collides. |
| `plugins/` | 15 | Media production (`ppt-maker`, `word-maker`, `excel-maker`, `subtitle-craft`, `avatar-studio`, `seedance-video`). All bound to the host runtime. |

Also vendors six `obra/superpowers@*` skills — `brainstorming`,
`writing-plans`, `systematic-debugging`, `test-driven-development`,
`verification-before-completion`, `receiving-code-review`. Those are portable
and good; they originate elsewhere.

## khazix-skills — 6 skills · MIT

数字生命卡兹克. Small and unusually high quality:

- `hv-analysis` — 横纵分析法. Vertical axis is the subject's full history as
  narrative; horizontal axis is a systematic comparison against peers at the
  present cross-section; the insight comes from crossing them. Outputs a
  typeset PDF. **The best single skill in the pack.**
- `leader` — turns a one-sentence idea into a brief an agent can execute blind.
  Measures the codebase first, asks ≤5 questions in one round, and produces
  ≤4000 characters with anti-cheat acceptance criteria and resume points.
- `khazix-writer` (公众号 long-form), `aihot` (AI news via an anonymous
  read-only API — no key, no MCP), `neat-freak`, `storage-analyzer`

## notebooklm-skill — 1 skill · MIT

`notebooklm-research`. Drives Google NotebookLM through `notebooklm-py` — an
**unofficial** web API over a browser session, not a supported Google API.
Notebooks from URLs/text/files, cited Q&A, and artifact generation (audio,
video, slides, study guides, quizzes, mind maps, infographics).

Ships `mcp_server/` (13 MCP tools) plus CLI scripts that emit JSON on stdout and
diagnostics on stderr. Needs setup per `docs/SETUP.md`. Google-side quotas and
availability are not guaranteed — the skill says so itself, so do not promise a
client a NotebookLM artifact on a deadline.

## crawl4ai — 0 skills shipped · Apache-2.0

A Python library (0.9.2), no `SKILL.md` upstream. **A skill was authored for it**
in `../new-skills/crawl4ai/`, verified against the 0.9.2 source.

Async Playwright crawler producing LLM-ready Markdown or schema-extracted JSON,
with deep crawling, content filters and batch dispatch. The cleanest licence in
the pack and the most directly useful for engagement work.

## superset — 6 skills · Elastic License 2.0

A large Bun/TypeScript monorepo for orchestrating terminal coding agents across
devices. Only two of its six skills mean anything outside the repo:

- `superset-orchestration` — spawn isolated workspaces, launch workers, send
  follow-ups, read terminal output, track dependencies, collect results
- `superset` — the CLI wrapper

The other four (`db-migrations`, `decide`, `redesign`, `ticket-format`) are that
repo's internal conventions.

**Windows note:** a full clone fails with `Filename too long`. `sync_sources.py`
uses `core.longpaths=true` plus a sparse checkout of `.agents` and
`plugins/superset/skills`, so only the skill directories land.

## finger-frame-effect-lucy — 0 skills shipped · no licence

A single-page web demo (`index.html` + 576-line `main.js`), no `SKILL.md`.
**A skill was authored for it** in `../new-skills/finger-frame-lucy/`, verified
against the source.

Two genuinely reusable halves: realtime video-to-video through Decart Lucy 2.5
over WebRTC (with live prompt swap, no reconnect), and a MediaPipe two-hand
tracking pipeline with anatomical corner ordering, gesture hysteresis, teleport
rejection, velocity-adaptive smoothing and dropout hold.

Needs a `platform.decart.ai` key. Degrades to a local canvas filter without one.
