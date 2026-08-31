---
name: ibm-question-decomposer-ica
description: Use this skill when the user wants to decompose a complex question into layered subquestions with configurable depth and breadth, using an OpenAI-compatible API endpoint.
---

# Layered Question Decomposer

Use this skill to generate a multi-level decomposition tree from one root question.

## What This Skill Provides

- A simple Python CLI at `scripts/structured_decomposer_openai.py`
- OpenAI-compatible client defaults:
  - model: `global/anthropic.claude-sonnet-4-5-20250929-v1:0`
  - base URL: `http://localhost:10276/v1`
  - API key env var: `ICA_API_KEY`
- Configurable decomposition shape:
  - `--depth`
  - `--min-breadth`
  - `--max-breadth`
- Framework selection:
  - `--framework` supports: `adaptive`, `components`, `5w1h`, `mece`, `pestle`, `systems`, `scientific`, `design`, `root-cause`, `issue-tree`, `academic`
- Maturity assessment mode:
  - `--maturity` to generate 5-level maturity criteria for leaf questions
  - `--maturity-output` for CSV destination

## Usage

Run from repository root:

```bash
uv run python $SKILL_DIR/scripts/structured_decomposer_openai.py \
  "How should we modernize our customer onboarding process?" \
  --framework systems \
  --depth 2 \
  --min-breadth 3 \
  --max-breadth 5 \
  --output outputs/layered_questions.md
```

Use `--file` to load the root question from a text file.
