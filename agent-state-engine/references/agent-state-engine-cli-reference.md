# Agent State Engine CLI Reference

## Command Style

Use one command convention: noun-oriented subcommands with positional IDs.

Generic executable name:

```bash
uv run $ENGINE_DIR/scripts/agent_state.py ...
```

Profiles may wrap or alias this command, but wrappers should call the generic engine commands internally.

## Core Commands

```bash
agent_state.py --profile example_profile init
agent_state.py list-projects
agent_state.py show WI-0042
agent_state.py show WI-0042 --children
agent_state.py next WI-0042
agent_state.py claim WI-0043 --agent-id agent-1 --expected-row-version 7
agent_state.py claim-next WI-0042 --limit 10 --agent-id-prefix subagent
agent_state.py claim-next WI-0042 --limit 10 --agent-id-prefix reviewer --tag reviewer
agent_state.py expire-claims
agent_state.py complete WI-0043 --agent-id agent-1 --expected-row-version 8 --summary "Done"
agent_state.py link WI-0010 WI-0042 --policy mark_outdated
agent_state.py add-child WI-0001 "Review requirement A" --type review --tag reviewer --source-work-item WI-0004
agent_state.py add-children WI-0001 --file ./tmp/generated-work-items.yaml --source-work-item WI-0004
```

`add-child` and `add-children` are intended for skills that discover additional
work while running. For example, an analysis step can create one child work item per discovered requirement, question, risk, or follow-on action. `--source-work-item` records which existing task caused the expansion.

`next` returns the first currently eligible child of a parent work item. It is
for single-step orchestration and inspection.

`claim-next` is the batch fan-out command for parallel subagents. It selects up
to `--limit` eligible children under the parent, skips blocked, invalid, active,
complete, cancelled, and already in-progress work, then claims the selected
items in one SQLite transaction. By default it assigns agent ids from
`--agent-id-prefix` and `--start-index`, for example `subagent-1`,
`subagent-2`, and `subagent-3`. Use `--agent-id` only with the default
single-item limit.

Use one optional `tag` per work item to route specialist work. A tagged
`claim-next` call only claims children with that tag, so a writer agent can ask
for `--tag writer` while a reviewer agent asks for `--tag reviewer`. Untagged
`claim-next` keeps the generalist behavior and can claim any otherwise eligible
child.

## Parallel Child Dispatch Example

Create or discover several children under an operation parent:

```yaml
# ./tmp/generated-work-items.yaml
children:
  - title: Draft answer for requirement A
    key: draft_requirement_a
    type: answer
    tag: writer
    phase: content_development
    priority: 1
  - title: Draft answer for requirement B
    key: draft_requirement_b
    type: answer
    tag: writer
    phase: content_development
    priority: 1
  - title: Fact check requirement A
    key: fact_check_requirement_a
    type: review
    tag: reviewer
    phase: assurance
    priority: 2
    dependencies:
      - upstream: WI-0043
        policy: mark_needs_review
```

Register the children and inspect the parent:

```bash
agent_state.py add-children WI-0042 --file ./tmp/generated-work-items.yaml --source-work-item WI-0041
agent_state.py show WI-0042 --children
agent_state.py next WI-0042
```

Claim up to 10 ready children for a specialist agent team:

```bash
agent_state.py claim-next WI-0042 --limit 10 --agent-id-prefix writer --tag writer
agent_state.py claim-next WI-0042 --limit 10 --agent-id-prefix reviewer --tag reviewer
```

Example output:

```json
[
  {
    "agent_id": "subagent-1",
    "claim_id": "6db0d6c8-8aa2-4aa2-a111-8d9f41eb0001",
    "expires_at": "2026-05-06T10:30:00Z",
    "tag": "writer",
    "work_item_label": "WI-0043",
    "work_item_row_version": 2,
    "work_item_title": "Draft answer for requirement A"
  },
  {
    "agent_id": "subagent-2",
    "claim_id": "9ac1a5a0-590e-4f4a-b222-9fd610740002",
    "expires_at": "2026-05-06T10:30:00Z",
    "tag": "writer",
    "work_item_label": "WI-0044",
    "work_item_row_version": 2,
    "work_item_title": "Draft answer for requirement B"
  }
]
```

Each subagent then works only its claimed item:

```bash
agent_state.py context build --work-item WI-0043
agent_state.py heartbeat WI-0043 --agent-id subagent-1 --lease-minutes 60
agent_state.py complete WI-0043 --agent-id subagent-1 --expected-row-version 2 --summary "Drafted requirement A"
```

If an agent is stopped or killed, release or expire the claim:

```bash
agent_state.py release WI-0044 --agent-id subagent-2 --reason "handing off"
agent_state.py expire-claims
```

`expire-claims` is a recovery command for agent failure. It transitions active
claims whose `expires_at` is in the past to `expired` and returns their
`in_progress` work items to `ready`.

`list-projects` is diagnostic only. The supported operating pattern is one
project per SQLite database, selected with the global `--db` flag.

## Source Change Impact

```bash
agent_state.py revise-source SRC-0004 --path ./inputs/source-v2.xlsx --version-label v2
agent_state.py review-impacts SRCV-0012
agent_state.py approve-impact IMP-0017 --reviewed-by "human"
agent_state.py reject-impact IMP-0018 --reviewed-by "human" --reason "No dependency"
agent_state.py apply-approved-impacts SRCV-0012
```

## Context

```bash
agent_state.py context build --work-item WI-0042
agent_state.py context show WI-0042
```

Context packs are generated files with metadata headers. They are not database
rows.

## Rendering

```bash
agent_state.py render
agent_state.py render-graph
agent_state.py render-graph --template government_salesforce_implementation
```

Rendering must write to a temporary file and atomically rename it into place.
