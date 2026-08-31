# Model routing

The rule this pack applies, the mechanism that makes it automatic, and the
limits of that mechanism. Facts cached 2026-07-26 from the bundled `claude-api`
skill; the companion `model-router` skill in `H:\My Drive\AA\model-router\` is
the general-purpose version of the same thing.

## The rule

Route on **cost of being wrong**, not on how important the project feels.
Ask in order; first match wins.

1. **Mechanically checkable in seconds, and a lot of it?** (classify, extract,
   tag, reformat, translate one field, triage a queue) → **Haiku 4.5**
2. **Runs unattended for many steps, or a wrong answer is expensive to undo?**
   (multi-file refactor, overnight run, a deliverable that ships, contract risk,
   a migration) → **Opus 5** at `high`, `xhigh` for coding/agentic
3. **Has Opus 5 already failed this twice with a complete prompt?** → **Fable 5**.
   Not before.
4. **Everything else** → **Sonnet 5** at `high`

If two tiers look equally plausible, take the cheaper one and escalate on
evidence. Escalation is cheap; a Fable run you did not need is 10× a Haiku run
you did.

| Model | ID | In / Out per MTok | Context | Relative input cost |
|---|---|---|---|---|
| Haiku 4.5 | `claude-haiku-4-5` | $1 / $5 | 200K | 0.33× |
| Sonnet 5 | `claude-sonnet-5` | $3 / $15 (intro $2/$10 to 2026-08-31) | 1M | 1× |
| Opus 5 | `claude-opus-5` | $5 / $25 | 1M | 1.67× |
| Fable 5 | `claude-fable-5` | $10 / $50 | 1M | 3.3× |

Re-verify pricing before quoting a client — the Sonnet 5 intro rate expires
2026-08-31.

## Effort is the second dial — try it before changing tier

`output_config: {effort: "low"|"medium"|"high"|"xhigh"|"max"}`, default `high`.

- **Sonnet 5 at `medium` ≈ Sonnet 4.6 at `high`.** One notch down often saves
  more than a tier drop, without losing the tier's judgement.
- **Opus 5 at `low`/`medium` is unusually strong.** Sweep down before assuming
  you need `xhigh`.
- `max` is correctness-over-cost only; it overthinks simple tasks.
- At `xhigh`/`max`, set `max_tokens` ≥ 64000 or output truncates mid-thought.
- Effort does **not** reliably shorten user-facing prose. Ask for shorter answers.
- **`effort` errors on Haiku 4.5.** Do not send it. The catalogue shows `—` for
  that tier's effort column for this reason.

## How this pack applies the routing automatically

| Surface | Applied |
|---|---|
| **A subagent** | **Automatically.** `agents/gsp-haiku-bulk`, `gsp-sonnet-standard`, `gsp-opus-deep`, `gsp-fable-escalation` carry `model:` in frontmatter. The Agent tool honours it with no further instruction. Install with `install_skills.py --agents`. |
| **A workflow stage** | **Automatically.** `agent(prompt, {model, effort})` per stage, values from the catalogue. |
| **Generated API code** | **Automatically.** The model ID and effort are written into the request. |
| **Each installed skill** | `metadata.model` / `metadata.effort` plus a one-line banner, stamped by the installer. The tier travels with the skill. |
| **The current chat session** | **Not automatic, and cannot be.** |

### The honest limit

**No skill can change the model of the conversation it is already running in.**
Not this one, not `model-router`, not any other. The mechanism does not exist.

What to do instead, in order of preference:

1. **Delegate to the right-tier subagent** and leave the session where it is.
   This is the switch that actually happens, and it is usually better anyway —
   the orchestrator keeps the plan on a capable model while the legs run cheap.
2. **State the verdict in one line** and let the user run `/model`:
   `→ Opus 5, effort high — leader writes a brief another agent runs blind.`
   No option survey, no table, unless they ask why.

**Never switch model mid-conversation to save money.** Caches are model-scoped,
so the switch discards the whole cached prefix and you pay to rebuild it. Spawn
a cheaper subagent instead.

## Mixed-tier pipelines

The highest-leverage move is not picking one model — it is splitting the job.

- **Fan out on Haiku, synthesize on Opus.** 30 documents → 30 Haiku extractions
  → 1 Opus synthesis. A fraction of 30 Opus reads, and usually better, because
  each extraction is small and checkable.
- **Draft on Sonnet, review on Opus.** Cheap first pass, expensive judgement
  only on the diff.
- **Route subagents down, keep the orchestrator up.** Search, file reads and
  mechanical edits run `haiku`/`sonnet` at `effort: low`; the coordinator
  holding the plan stays on `opus`.

In this pack that maps to: `gsp-haiku-bulk` for the legs, `gsp-opus-deep` for
the synthesis.

## Fable 5 — read before routing there

Fable is not "Opus but better", it is a different operating envelope.

- **$10 / $50** — 2× Opus 5, 3.3× Sonnet 5.
- **Thinking is always on.** `thinking: {type: "disabled"}` or `budget_tokens`
  returns 400. Omit the parameter entirely.
- **Requires 30-day data retention.** A zero-data-retention org gets
  `400 invalid_request_error` on *every* Fable request. Check this before
  proposing Fable for a client tenant.
- **Turns run for minutes.** Plan streaming, timeouts and progress UX.
- **Prompts tuned for smaller models make it worse.** Strip the step-by-step
  scaffolding; state the goal and the constraints.

Full detail: the `fable-model-capability` skill.

## Anti-patterns

| Don't | Because |
|---|---|
| Route to Fable because the client is important | Importance is not difficulty. Route on whether Opus 5 actually failed. |
| Switch model mid-conversation to save money | Model-scoped caches — you pay to rebuild the prefix. |
| Send `effort` to Haiku 4.5 | It errors. |
| Put >200K tokens at Haiku | 200K ceiling; every other tier is 1M. |
| Default to `xhigh` everywhere | On Opus 5 and Sonnet 5, `high` is the sweet spot and `medium` is often enough. |
| Assume cheaper = faster | Latency tracks effort and output length more than tier. Opus 5 at `low` can beat Sonnet 5 at `xhigh`. |

## How the catalogue's tiers were assigned

`build_catalogue.py` assigns in this order: an explicit override table (skills
judged individually), then keyword rules, then `sonnet` as the default. All 77
`host-builtin` skills are forced to `haiku` — they are tool wrappers.

The override table exists because keyword rules misfire in both directions:
`chinese-novelist` matched "plot **architecture**" and `dbs-slowisfast` matched
「长期」, both promoted to Opus wrongly and pinned back to Sonnet. If you disagree
with a tier, edit `MODEL_OVERRIDE` in the script and rebuild — do not edit
`catalogue.md`, which is generated.
