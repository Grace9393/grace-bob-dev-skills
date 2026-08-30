# Agent State Engine Migration Guidance

## Principle

Migration from a legacy dashboard or checklist is a draft import, not a trusted
canonical conversion.

The migration command should produce:

- draft database rows
- a migration review report
- warnings for ambiguous fields
- explicit human approval before imported rows become canonical

## Generic Command

```bash
agent_state.py migrate-dashboard \
  --input ./tmp/legacy-project.md \
  --profile example_profile \
  --status draft
```

## Review

The review report should list parsed project metadata, inferred sources,
artifacts, work items, dependencies, unparsed fields, and records requiring human
confirmation.

Only after review should the user approve:

```bash
agent_state.py migration approve MIG-0001
```
