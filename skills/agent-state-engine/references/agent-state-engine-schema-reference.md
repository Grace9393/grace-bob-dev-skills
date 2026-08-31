# Agent State Engine Schema Reference

## Identity

Use UUID text primary keys for database identity. Use separate generated human
labels for users and agents:

- `PRJ-0001`
- `WI-0042`
- `SRC-0004`
- `SRCV-0012`
- `ART-0101`
- `ARTV-0021`
- `IMP-0017`

All mutable tables use `row_version INTEGER NOT NULL DEFAULT 1` for optimistic
concurrency.

## V1 Tables

The generic engine schema uses these 12 table names:

- `project`
- `work_item`
- `work_dependency`
- `source_asset`
- `source_asset_version`
- `artifact`
- `artifact_version`
- `artifact_source`
- `impact`
- `work_item_claim`
- `event_log`
- `render_state`

## Required Rules

- `project` has `row_version`.
- `work_item.parent_work_item_id` represents multi-step operations.
- `work_item.tag` is optional and stores one specialist routing tag for
  `claim-next --tag`.
- `source_asset.asset_key` is required and unique per project.
- `source_asset_version.version_number` and `version_label` are required.
- `artifact.owner_work_item_id` identifies the work item allowed to write it.
- Artifact writes are allowed only by the active claimant of
  `artifact.owner_work_item_id`.
- `impact` must target at least one work item or artifact.
- `impact.confidence` is one of `low`, `medium`, `high`.
- One active work item claim is allowed per work item and old claim rows are
  retained.
- Expired claims must be reaped by `expire-claims`; watchdog agents should run
  it periodically.
- `render_state` is keyed by `(project_id, output_path)`.
- Dependency propagation uses severity order:
  `none < mark_needs_review < mark_outdated < block_until_refreshed`.

## Context Packs

Context packs are generated markdown files, not database rows. Each pack must
include a metadata header containing:

- work item label or ID
- generated event cursor
- generation timestamp
- policy path
- policy schema version

## SQLite Settings

```sql
PRAGMA foreign_keys=ON;
PRAGMA journal_mode=WAL;
```

Every mutating command runs in a transaction, appends to `event_log`, and uses
`row_version` where stale-agent updates are possible.

## Profile Mapping

Profiles may present aliases for generic tables. For example, the IBM bid
profile calls `source_asset` a source document, but the underlying table remains
generic.
