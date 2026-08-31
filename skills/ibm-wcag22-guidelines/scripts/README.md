# Scripts

Self-contained entrypoints for the `ibm-wcag22-guidelines` skill.

## Files

- `search.py` - run `sqlite-skill search ...` via inline PEP 723 metadata
- `get.py` - run `sqlite-skill get ...` via inline PEP 723 metadata
- `info.py` - run `sqlite-skill info ...` via inline PEP 723 metadata

## Usage

From the skill directory:

```bash
uv run scripts/search.py <db_path> "<query>"
uv run scripts/get.py <db_path> <doc_id>
uv run scripts/info.py <db_path>
```

The scripts pin `sqlite-skill==0.2.2` and resolve it from `../assets/wheels/`
using `tool.uv.sources`.
