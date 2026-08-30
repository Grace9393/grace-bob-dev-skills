# Agent State Engine Context Policies

## Purpose

Context policies provide progressive disclosure. They decide which source
assets, artifacts, risks, decisions, and work items appear in a generated
context pack.

Policies are profile-owned YAML files loaded by the generic engine.

## Policy Format

```yaml
schema_version: 1
profile: example_profile
skill: example-analysis-skill
include:
  - source_asset_type: requirements_source
    disclosure: full
    required: true
  - artifact_type: analysis_output
    disclosure: full
  - artifact_type: supporting_output
    disclosure: excerpt
exclude:
  - source_asset_type: unrelated_reference
```

## Precedence

1. Work-item required context is included first.
2. Explicit human-added context items override policy excludes.
3. Policy excludes override generic policy includes.
4. Required policy includes are included unless explicitly rejected by a human.
5. Optional includes are included only when they match the current work item or
   dependency neighborhood.
6. Every generated context pack records the policy file path and
   `schema_version`.

## Disclosure Levels

- `metadata_only`
- `summary`
- `excerpt`
- `full`
- `reference`

Every context item must have a relevance reason.
