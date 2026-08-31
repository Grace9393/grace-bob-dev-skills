# Agent State Engine Design

## What It Is

Agent State Engine is a local SQLite-backed state layer for multi-step,
multi-agent workflows. It tracks work, dependencies, versioned inputs and
outputs, provenance, concurrent agent claims, impact review, generated context,
and rendered dashboards.

Domain meaning lives in profiles, not in the engine.

```text
Agent State Engine
  work graph, source versions, artifact versions, provenance, claims, impacts,
  event log, rendered views

Domain Profile
  labels, vocabularies, workflow templates, context policies, impact rules
```

The engine must avoid hardcoding any domain vocabulary.

## Core Tables

The v1 engine uses 12 tables:

| Table | Purpose |
| --- | --- |
| `project` | workspace root |
| `work_item` | durable unit of work, with execution and validity state |
| `work_dependency` | directed graph edge with invalidation policy |
| `source_asset` | logical input, such as a document, dataset, or feed |
| `source_asset_version` | exact received source file/version plus hash |
| `artifact` | logical output |
| `artifact_version` | exact produced output file/version plus hash |
| `artifact_source` | provenance from artifact version to source version |
| `impact` | proposed/approved effect of source change on work or artifacts |
| `work_item_claim` | auditable claim/lease per work item |
| `event_log` | append-only audit trail |
| `render_state` | rendered dashboard/graph freshness cursor |

The following concepts are intentionally not v1 tables:

- artifact locks: artifact write permission derives from the active claim on
  `artifact.owner_work_item_id`.
- operations: multi-step workflows are parent work items with child work items.
- context packs: context packs are generated files with metadata headers.
- skill runs: skill execution is recorded in `event_log`.
- source change events: source revisions are recorded in `event_log` and
  associated `impact` rows.

## Design Principles

1. SQLite owns canonical state.
2. Scripts own mutations.
3. Generated files own presentation and context bundles.
4. Profiles own domain meaning.
5. Agents should not reconstruct workflow state from chat history.
6. Agents should read generated context packs, not whole project folders.
7. Completed work remains complete; changed upstream basis alters
   `validity_status` and creates follow-on work or artifact versions.
8. Source impact propagation is proposed first, then applied only after review.
9. Artifact writes are allowed only by the active claimant of the artifact's
   owning work item.

## Work Items As Operations

Operations are represented as parent work items:

```text
WI-0100 Process pricing schedule v2
  WI-0101 Register source version
  WI-0102 Generate proposed impacts
  WI-0103 Await human approval
  WI-0104 Apply approved impacts
  WI-0105 Create refresh work
```

`agent_state.py next WI-0100` returns the next valid child step. Resumability
comes from `work_item.status`, `work_item.validity_status`, dependencies, and
`event_log`.

For parallel fan-out, an orchestrator should use `claim-next` against the
parent operation:

```bash
agent_state.py claim-next WI-0100 --limit 10 --agent-id-prefix subagent
```

The command selects eligible child work items and creates active claims in one
transaction, so multiple dispatchers cannot assign the same child. Each
subagent then builds a context pack for its claimed work item, completes or
releases it, and the parent operation remains resumable from database state.

Specialist subagents should request work by a single task tag:

```bash
agent_state.py claim-next WI-0100 --limit 5 --agent-id-prefix writer --tag writer
agent_state.py claim-next WI-0100 --limit 5 --agent-id-prefix reviewer --tag reviewer
```

Tags are deliberately simple in the initial engine version: each work item has
zero or one tag. The tag should represent the specialist capability needed to
perform the work, such as `writer`, `reviewer`, `pricing`, `architect`, or
`salesforce`.

## Context Packs

Context packs are generated files, not database rows. A context build command
reads project state, dependencies, profile context policies, and event cursors,
then writes a markdown file such as:

```text
./tmp/context-packs/WI-0042.md
```

Each generated context pack must include a metadata header:

```yaml
context_pack:
  work_item: WI-0042
  generated_from_event_id: 1234
  generated_at: 2026-05-05T10:30:00Z
  policy: default-task-policy.yaml
  policy_schema_version: 1
```

`context show WI-0042` compares `generated_from_event_id` with the latest
`event_log.id` to determine whether the pack is current.

## Dependency Propagation

Dependency propagation follows directed `work_dependency` edges. When multiple
upstream paths reach the same downstream item, apply the most severe policy.

Severity order:

```text
none < mark_needs_review < mark_outdated < block_until_refreshed
```

Impact propagation is proposed first. Approved impacts can then update
`validity_status`, create follow-on work items, and produce events.

## Generic Naming

Use generic names in core schema and scripts:

| Generic | Example Domain Label |
| --- | --- |
| project | engagement / bid / programme |
| source_asset | source document / dataset / feed |
| source_asset_version | source version |
| artifact | output document / generated asset |
| impact | change impact |
| work_item | task / answer / review / action |

Domain-specific terms belong in profile vocabularies and templates.

## Storage

Default local workspace layout:

```text
./tmp/agent-state.sqlite
./tmp/agent-state.md
./tmp/context-packs/
./tmp/impact-reports/
./inputs/
./outputs/
```

Profiles may alias these paths.

The SQLite database may be committed to Git for small local workflows. For large
workspaces, use Git LFS or periodic JSON exports.

The supported operating pattern is one project per SQLite database. Although
the schema is project-partitioned, commands select the current project from the
database rather than accepting a `--project` flag. Use the global `--db` flag to
switch project databases explicitly. `list-projects` exists to diagnose the
current database, not to encourage shared multi-project databases.

## Profile Contract

A profile supplies:

```text
profile.yaml
workflow-templates/
context-policies/
impact-rules/
dashboard-template.md
vocabularies/
```

The engine loads profile configuration but does not embed profile vocabulary in
the schema.

## References

- `references/agent-state-engine-schema-reference.md`
- `references/agent-state-engine-cli-reference.md`
- `references/agent-state-engine-context-policies.md`
- `references/agent-state-engine-migration.md`
- `references/agent-state-engine-implementation-plan.md`
