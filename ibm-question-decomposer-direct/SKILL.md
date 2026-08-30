---
name: ibm-question-decomposer-direct
description: Use this skill to decompose a complex question into layered subquestions directly in-chat (no script), with configurable framework, depth, breadth, and optional 5-level maturity criteria for leaf questions.
---

# IBM Question Decomposer (Direct)

Use this skill when the user wants a structured question decomposition without running Python.

## Workflow

1. Confirm decomposition controls from user input:
- `framework` (default `components`; allow `adaptive`)
- `depth` (default `2`)
- `min_breadth` (default `3`)
- `max_breadth` (default `5`)
- `maturity` (default `off`)
- `output_format` (default `markdown`; allow `csv`)
2. If framework is `adaptive`, choose one framework from `references/frameworks.md` and state the choice.
3. Build the decomposition tree breadth-first with strict per-level breadth:
- Treat `depth` as exact levels of question IDs in the output.
- Every node at levels `1..(depth-1)` must be expanded with between `min_breadth` and `max_breadth` children.
- Do not leave a parent node with fewer than `min_breadth` children unless the user explicitly asks for sparse expansion.
- Keep sibling questions non-overlapping where possible.
- Only stop early if the user explicitly allows early stopping.
4. Output a markdown tree with numeric IDs (`1`, `1.1`, `1.1.1`, ...).
5. If `maturity=on`, always output maturity assessments as CSV using `references/maturity_levels.md`:
- set `output_format=csv` even if the user does not request CSV
- include these per-leaf columns:
  - `node_id`
  - `leaf_question`
  - `level_1_initial_answer`
  - `level_2_developing_answer`
  - `level_3_defined_answer`
  - `level_4_managed_answer`
  - `level_5_optimizing_answer`
6. Enforce question-specific maturity criteria for every leaf:
- Each level answer must directly reference the leaf question subject (for example, naming the artifact, control, metric, owner, SLA, or process in that question).
- Do not reuse one generic 1-5 phrase set across multiple leaf questions.
- Make progression concrete across levels: ad hoc -> partial -> standardized -> measured/enforced -> optimized/predictive.
- Keep answers concise but specific enough to be auditable.
- Before finalizing, run a quality gate: if an answer can apply unchanged to many unrelated questions, rewrite it to be leaf-specific.

## Output Contract

- Include a short config header:
- `Framework`
- `Depth`
- `Breadth`
- `Maturity Mode`
- `Output Format`
- Include a short structure summary:
- `Top-level Questions`
- `Children Per Parent`
- `Leaf Count` (if fully expanded)
- Include `## Tree` with hierarchical bullets.
- If maturity enabled, include a `## Maturity Criteria (CSV)` section and provide a CSV table (inside a fenced code block) with these per-question columns:
- `node_id`
- `leaf_question`
- `level_1_initial_answer`
- `level_2_developing_answer`
- `level_3_defined_answer`
- `level_4_managed_answer`
- `level_5_optimizing_answer`
- Maturity rows must be uniquely tailored per leaf question; generic repeated wording across many rows is not allowed.

## Breadth Semantics (Required)

- Breadth constraints apply to every parent node, not just the root.
- Example with `depth=2`, `min_breadth=3`, `max_breadth=3`:
- `1`, `2`, `3`
- `1.1`, `1.2`, `1.3`
- `2.1`, `2.2`, `2.3`
- `3.1`, `3.2`, `3.3`
- Example with `depth=3`, `min_breadth=3`, `max_breadth=3`:
- Level 1: `1`, `2`, `3`
- Level 2: each of `1..3` has `.1..3`
- Level 3: each level-2 node has `.1..3` (for example `1.1.1`, `1.1.2`, `1.1.3`, ...).

## References

- Framework guidance: `references/frameworks.md`
- Maturity-level template: `references/maturity_levels.md`
