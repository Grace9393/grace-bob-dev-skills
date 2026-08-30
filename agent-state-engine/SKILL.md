---
name: agent-state-engine
description: Reusable local state-management substrate for agent workflows. Use when a skill or workflow needs durable task graphs, dependency tracking, versioned source assets and artifacts, provenance, resumable parent/child work items, context packs for progressive disclosure, claim/lease concurrency, append-only audit events, or generated markdown/Mermaid views. Domain skills should use this as a generic engine and supply profile-specific vocabularies, workflow templates, impact rules, and context policies.
---

# Agent State Engine

Use this skill as the generic state layer for multi-step, multi-agent workflows.
It owns workflow mechanics; domain profiles own meaning.

## References

- `$SKILL_DIR/references/agent-state-engine-design.md`
- `$SKILL_DIR/references/agent-state-engine-schema-reference.md`
- `$SKILL_DIR/references/agent-state-engine-cli-reference.md`
- `$SKILL_DIR/references/agent-state-engine-context-policies.md`
- `$SKILL_DIR/references/agent-state-engine-migration.md`
- `$SKILL_DIR/references/agent-state-engine-implementation-plan.md`

## Script Usage Examples

```bash
uv run $SKILL_DIR/scripts/agent_state.py --profile example_profile init
uv run $SKILL_DIR/scripts/agent_state.py list-projects
uv run $SKILL_DIR/scripts/agent_state.py show PRJ-0001
uv run $SKILL_DIR/scripts/agent_state.py add-child WI-0001 "Review requirement A" --type review --tag reviewer
uv run $SKILL_DIR/scripts/agent_state.py claim WI-0002 --agent-id agent-1 --expected-row-version 1
uv run $SKILL_DIR/scripts/agent_state.py claim-next WI-0001 --limit 10 --agent-id-prefix reviewer --tag reviewer
uv run $SKILL_DIR/scripts/agent_state.py expire-claims
uv run $SKILL_DIR/scripts/agent_state.py complete WI-0002 --agent-id agent-1 --expected-row-version 2 --summary "Done"
uv run $SKILL_DIR/scripts/agent_state.py context build --work-item WI-0003
uv run $SKILL_DIR/scripts/agent_state.py render
uv run $SKILL_DIR/scripts/agent_state.py validate --strict
```

## Multiple Projects

Each bid workspace should have its own `./tmp/ibm-bid-project.sqlite`. Use `--db` only when deliberately pointing at a specific project database.

## Profile Pattern

A domain profile supplies:

```text
profile.yaml
workflow-templates/
context-policies/
impact-rules/
vocabularies/
```

## Operating Rule

Agents should not reconstruct workflow state from chat history. They should read
the generated dashboard, inspect active parent and child work items, build the
relevant context pack, perform only the next valid step, then update the state
engine before stopping.

Orchestrator or watchdog agents should run `expire-claims` periodically so work
held by crashed or killed agents returns to `ready`.
