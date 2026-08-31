# Parsing Existing Swimlane Diagrams

This file covers how to extract the canonical JSON representation from each supported input type.

## From an image (PNG / JPG / WebP)

Use Claude's vision capability directly — view the image and reason about it. Order of operations:

### 1. Determine orientation
- **Horizontal lanes** (lanes as rows): labels along the **left** edge, flow runs **left-to-right**.
- **Vertical lanes** (lanes as columns): labels along the **top** edge, flow runs **top-to-bottom**.

If the diagram has both row and column labels (rare — a "matrix" diagram), treat the larger dimension as the lane axis and ask the user for confirmation.

### 2. Identify lanes
Read the labels in order. Use these as the `lanes` array. If lane names are abbreviated or unclear, expand based on context (e.g., "HR" → "Human Resources" only if elsewhere on the diagram supports it; otherwise keep the abbreviation).

### 3. Identify nodes
For each visible shape, infer the node type from its geometry:

| Visual cue                           | `type`        |
|--------------------------------------|---------------|
| Pill / stadium / rounded full oval   | `start` or `end` (use context: leftmost/topmost = start, rightmost/bottommost = end) |
| Plain rectangle                      | `process`     |
| Diamond / rhombus                    | `decision`    |
| Rectangle with double vertical bars  | `subprocess`  |
| Parallelogram (slanted rectangle)    | `data`        |
| Rectangle with wavy bottom edge      | `document`    |
| D-shape (rectangle, one curved side) | `delay`       |
| Open bracket on one side, text       | `annotation`  |
| Circle (small, unlabeled)            | start/end event in BPMN — treat as `start`/`end` |
| Diamond with `+` inside              | `decision` with `subtype: "parallel"` |
| Diamond with `o` inside              | `decision` with `subtype: "inclusive"` |

Assign each node to the lane it sits within based on its vertical (horizontal layout) or horizontal (vertical layout) position relative to the lane dividers.

### 4. Read the label inside each shape
Use the text exactly as written. Strip trailing punctuation. If the label is multi-line in the image, join with a space.

### 5. Trace edges
For every arrow:
- Identify the shape it originates from and the shape it points to.
- Note any text on or near the arrow — that's the edge `label`.
- If multiple arrows share a path before splitting, record each one separately.

### 6. Assign stable IDs
Use `n1, n2, n3...` in roughly the order nodes appear left-to-right then top-to-bottom (for horizontal) or top-to-bottom then left-to-right (for vertical). The IDs are arbitrary as long as they're unique.

### 7. Output the JSON
Present it to the user with a short summary: "I extracted N lanes, M nodes, and K edges. Here's the JSON — want me to re-render in another format, or make changes?"

### Flagging uncertainty

When something is illegible or ambiguous, do not invent it. Options:
- Add an `annotation` node with `label: "?"` and flag it in the conversation.
- Use an obvious placeholder like `"label": "[unreadable]"`.
- Ask the user to confirm.

A wrong extraction is worse than a partial one.

## From a PDF

If the PDF is text-extractable and someone has drawn the diagram with native PDF shapes (rare), the underlying drawing operators can sometimes be read directly. In practice, **always treat PDF diagrams as images**: rasterize the relevant pages and apply the image parsing flow above.

For PDFs with multiple pages, ask which page contains the diagram, or scan all pages and process every diagram-bearing page.

The `pdf-reading` skill can help with rasterization if needed: `/mnt/skills/public/pdf-reading/SKILL.md`.

## From Mermaid text

Map Mermaid syntax back to canonical JSON using the inverse of the table in `mermaid-syntax.md`.

### Subgraphs → lanes
```
subgraph customer [Customer]
  ...
end
```
becomes `{"id": "customer", "name": "Customer"}` in `lanes`.

### Node shapes → node types

| Mermaid             | `type`     |
|---------------------|------------|
| `id([...])`         | `start`/`end` (infer from position in the flow — leaf-with-no-outgoing-edge = end; root-with-no-incoming-edge = start) |
| `id[...]`           | `process`  |
| `id{...}`           | `decision` |
| `id{{...}}`         | `decision` with `subtype: "parallel"` |
| `id[[...]]`         | `subprocess` |
| `id[/.../]`         | `data`     |
| `id[(...)]`         | `document` |
| `id((...))`         | `delay`    |
| `id>...]`           | `annotation` |

### Edges
- `A --> B` → `{"from": "A", "to": "B"}`
- `A -->|label| B` → `{"from": "A", "to": "B", "label": "label"}`
- `A -.-> B` → annotation attachment (the `to` should be an `annotation` node)

## From canonical JSON

Validate the structure and use it directly. Minimum required fields:
- `title` (string)
- `orientation` (`"horizontal"` or `"vertical"` — default to `"horizontal"` if missing)
- `lanes`: array of `{id, name}` objects (at least 1)
- `nodes`: array of `{id, lane, type, label}` objects (at least 1)
- `edges`: array of `{from, to}` objects (may be empty for trivial diagrams)

If validation fails, fix what's obviously fixable (e.g., add missing `orientation`) and flag the rest to the user.

## From plain text description

This is Workflow C in SKILL.md, not strictly "parsing." Follow that section.
