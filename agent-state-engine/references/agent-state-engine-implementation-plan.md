# Agent State Engine Implementation Plan

## Goal

Build Agent State Engine as a reusable local SQLite state layer for skills and
multi-agent workflows. Domain profiles integrate with it without requiring
engine code changes.

## Engine Deliverables

- `scripts/agent_state.py`
- `scripts/agent_state/`
- `assets/schema.sql`
- focused tests for schema, mutations, dependency propagation, claims, impact
  review, rendering, context packs, and dynamic task creation

## Profile Integration Contract

A separate domain skill may provide:

- `assets/profile.yaml`
- `assets/workflow-templates/*.yaml`
- `assets/impact-rules/*.yaml`
- `assets/vocabularies/*.yaml`
- a thin wrapper script that supplies profile config and aliases

The wrapper must not duplicate engine state-transition, claim, dependency,
impact, context, or rendering logic.

## Build Phases

1. CLI skeleton and package structure.
2. SQLite schema and `init`.
3. identity, labels, create/show/list, and validation.
4. work graph, parent/child work items, `add-child`, and `add-children`.
5. claim, batch `claim-next`, heartbeat, release, complete, and expire stale claims.
6. source revision, proposed impacts, approval, rejection, and application.
7. artifact versioning and provenance.
8. dashboard rendering, graph rendering, and context packs.
9. profile loading and wrapper support.
10. migration helpers for legacy state files.
11. hardening: JSON output, strict validation, import/export, and agent-friendly
    error messages.

## Minimal Useful Release

The smallest useful release should include:

1. schema and init
2. work item create/show/list
3. dependency links
4. `add-child` and `add-children`
5. claim/complete with row-version checks
6. batch child claiming for parallel subagents
7. stale claim expiry
8. source revision with proposed impacts
9. approve/apply impacts
10. dashboard render
11. context build/show
12. profile wrapper support

## Acceptance Scenario

```bash
agent_state.py --profile example_profile init
agent_state.py show PRJ-0001
agent_state.py add-child WI-0001 "Review requirement A" --type review
agent_state.py add-children WI-0001 --file ./tmp/generated-work.yaml --source-work-item WI-0002
agent_state.py claim-next WI-0001 --limit 10 --agent-id-prefix subagent
agent_state.py claim WI-0002 --agent-id agent-1 --expected-row-version 1
agent_state.py expire-claims
agent_state.py complete WI-0002 --agent-id agent-1 --expected-row-version 2 --summary "Done"
agent_state.py revise-source SRC-0001 --path ./inputs/source-v2.md --version-label v2
agent_state.py review-impacts SRCV-0002
agent_state.py approve-impact IMP-0001 --reviewed-by human
agent_state.py apply-approved-impacts SRCV-0002
agent_state.py context build --work-item WI-0003
agent_state.py render
agent_state.py render-graph
agent_state.py validate --strict
```

## Definition Of Done

Agent State Engine is ready when:

1. engine commands work without domain-specific vocabulary
2. tests cover claim concurrency, dependency propagation, dynamic task creation,
   impact approval, context freshness, and atomic rendering
3. generated dashboard, graph, and context packs can be deleted and recreated
   from SQLite
4. a separate domain skill can load a profile and wrapper without modifying
   engine code
