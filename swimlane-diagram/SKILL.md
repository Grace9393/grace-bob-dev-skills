---
name: swimlane-diagram
description: Create, parse, and convert swimlane diagrams (also called cross-functional flowcharts, Rummler-Brache diagrams, BPMN pools/lanes, or process flow diagrams with actors). Use whenever the user wants to visualize a process with multiple participants — including phrases like "draw a swimlane," "cross-functional flowchart," "who does what in this process," "show handoffs between teams," "BPMN with pools," "process flow by department," or any multi-actor workflow request. Also trigger when the user uploads a swimlane diagram (image, PDF, Mermaid, JSON) for parsing or re-rendering, or when they describe a written workflow to turn into a diagram. Supports four outputs — inline SVG (default), Mermaid, PowerPoint (.pptx), and downloadable .svg/.png files. Prefer this skill over generic flowchart approaches for any multi-actor process visualization, even if the user does not say "swimlane."
---

# Swimlane Diagram

A swimlane diagram is a flowchart partitioned into **lanes** — one per actor (person, role, team, department, or system). Process steps live in their actor's lane, and arrows between lanes make **handoffs** visible. This makes the diagram excellent for spotting redundancy, bottlenecks, and unclear ownership.

This skill handles three workflows (generate, parse, convert) and four output formats (inline SVG, Mermaid, PowerPoint, downloadable file).

---

## Canonical JSON representation

Everything routes through this intermediate structure. Build it first, then render to whichever format(s) the user wants:

```json
{
  "title": "Customer Onboarding",
  "orientation": "horizontal",
  "lanes": [
    {"id": "customer", "name": "Customer"},
    {"id": "sales",    "name": "Sales"},
    {"id": "ops",      "name": "Operations"}
  ],
  "nodes": [
    {"id": "n1", "lane": "customer", "type": "start",    "label": "Sign up"},
    {"id": "n2", "lane": "sales",    "type": "process",  "label": "Send welcome email"},
    {"id": "n3", "lane": "ops",      "type": "decision", "label": "Enterprise tier?"},
    {"id": "n4", "lane": "ops",      "type": "process",  "label": "Assign CSM"},
    {"id": "n5", "lane": "ops",      "type": "process",  "label": "Auto-provision"},
    {"id": "n6", "lane": "customer", "type": "end",      "label": "Account ready"}
  ],
  "edges": [
    {"from": "n1", "to": "n2"},
    {"from": "n2", "to": "n3"},
    {"from": "n3", "to": "n4", "label": "yes"},
    {"from": "n3", "to": "n5", "label": "no"},
    {"from": "n4", "to": "n6"},
    {"from": "n5", "to": "n6"}
  ]
}
```

**Node types** (see `references/symbols.md` for shape details):
- `start`, `end` — terminal events (rounded oval / stadium)
- `process` — an action or task (rectangle)
- `decision` — a branch (diamond)
- `subprocess` — nested process (rectangle with double vertical bars)
- `data` — input/output (parallelogram)
- `document` — produces a document (rectangle with wavy bottom)
- `delay` — waiting period (D-shape)
- `annotation` — note attached by dotted line (no enclosing shape)

**Orientation**:
- `"horizontal"` (default) — lanes stack as rows, flow runs left-to-right. Better for typical screens.
- `"vertical"` — lanes are columns, flow runs top-to-bottom. Better for tall mobile screens or long sequential processes.

**Edge labels** are optional but should be present on decision branches (e.g., "yes" / "no", "approved" / "rejected").

---

## Workflow A — Generate from description

When the user describes a process they want diagrammed:

1. **Extract actors** → lanes. Listen for "the X team," "the customer," "John," "the system." If there are obvious roles, use them. If actors are unclear, ask one short clarifying question rather than guessing.
2. **Extract steps** → nodes. Each verb-phrase action is usually a `process` node. "Either A or B" implies a `decision`. Start and end states get `start` / `end` nodes.
3. **Assign steps to lanes** based on who performs them. A handoff is implied whenever consecutive steps live in different lanes.
4. **Build the JSON** (above).
5. **Render** in the requested format(s). If the user didn't specify, default to inline SVG and offer the other three.

If the description is vague ("draw our deployment process"), make assumptions explicit before drafting — list the lanes and steps you inferred so the user can correct them.

---

## Workflow B — Parse existing diagram

The input determines the approach:

### Image (PNG/JPG) or PDF
Use Claude's vision to read the file directly. For PDFs with multiple pages, view each page that contains diagrams. Extraction order:
1. **Identify orientation** — are lane labels along the top edge (vertical lanes) or the left edge (horizontal lanes)?
2. **List lanes** in order from the labels.
3. **Inventory shapes** in each lane and assign node types from their geometry (oval → start/end, rectangle → process, diamond → decision, etc.).
4. **Trace arrows** from each shape to determine edges. Note any text on arrows as edge `label`.
5. **Output the JSON.** Then ask the user what they want done with it (re-render, edit, convert format, analyze).

For low-quality images, extract what's legible and flag uncertainty rather than fabricating nodes.

### Text / Mermaid / JSON
If the user pastes Mermaid `flowchart` with `subgraph` blocks, treat each subgraph as a lane. If they paste an existing JSON in the canonical form above, use it directly. If they paste plain text describing a process, that's Workflow C.

See `references/parsing.md` for detailed shape recognition rules and Mermaid mapping.

---

## Workflow C — Convert written workflow

The user provides a numbered list, narrative paragraph, runbook, or SOP. Steps:

1. **Identify actors.** Look for subject-verb constructions ("HR sends the offer," "the candidate accepts"). If actors aren't named at all (e.g., a passive-voice runbook), ask the user who's involved rather than inventing them.
2. **Identify the sequence and any branches.** Phrases like "if X, then Y, otherwise Z" become decisions.
3. Proceed as in Workflow A.

This often overlaps with A — the line is fuzzy. The main difference is that converting a written workflow may involve restructuring (the original text might not be in clean step order, or might mix concerns).

---

## Output formats

### 1. Inline SVG (default)

Use the `visualize:show_widget` tool. Before the first call in a session, also call `visualize:read_me` with `modules=["diagram"]` to load the design tokens.

The layout algorithm:
- Lane labels sit in a fixed-width column on the left (horizontal) or fixed-height row on top (vertical).
- Within each lane, nodes are placed left-to-right (or top-to-bottom) in topological order.
- Edges are drawn as orthogonal (right-angle) polylines with arrowheads. Cross-lane edges visibly enter/exit the lane region.
- Decision branches label their edges.

For non-trivial diagrams (more than ~8 nodes or more than 4 lanes), use `scripts/render_svg.py` to compute layout deterministically:

```bash
python /path/to/swimlane-diagram/scripts/render_svg.py --input diagram.json --output diagram.svg
```

The script accepts JSON on stdin too: `cat diagram.json | python render_svg.py > diagram.svg`.

For small diagrams (≤6 nodes, ≤3 lanes), hand-writing SVG inline in `show_widget` is fine and often produces cleaner results.

### 2. Mermaid code

Use `flowchart LR` for horizontal lanes (or `flowchart TD` for vertical), with one `subgraph` per lane. Node shape syntax:
- `n1([Sign up])` — start/end (stadium)
- `n2[Send welcome email]` — process (rectangle)
- `n3{Enterprise tier?}` — decision (diamond)
- `n4[[Assign CSM]]` — subprocess
- `n5[/Data input/]` — data
- `n6>Annotation]` — annotation

Edge labels: `n3 -->|yes| n4`.

Use `scripts/json_to_mermaid.py` for deterministic conversion, or write it inline for simple cases. See `references/mermaid-syntax.md` for the full mapping.

### 3. PowerPoint slide (.pptx)

Use `scripts/render_pptx.py`. This script uses `python-pptx` to produce a single-slide deck with editable shapes — lanes as outlined rectangles, nodes as standard PowerPoint autoshapes, edges as connectors. The user can open the result and edit any element.

```bash
python /path/to/swimlane-diagram/scripts/render_pptx.py --input diagram.json --output /mnt/user-data/outputs/diagram.pptx
```

For richer multi-slide decks (e.g., current-state and future-state on separate slides), also read `/mnt/skills/public/pptx/SKILL.md` and integrate.

### 4. Standalone .svg / .png file

For `.svg`: write the output of `render_svg.py` directly to `/mnt/user-data/outputs/<name>.svg`, then `present_files`.

For `.png`: render SVG first, then convert with `cairosvg`:

```python
import cairosvg
cairosvg.svg2png(url="diagram.svg", write_to="/mnt/user-data/outputs/diagram.png", output_width=1600)
```

If `cairosvg` isn't available, `pip install --break-system-packages cairosvg`.

---

## Style conventions

Follow Lucidchart / BPMN conventions:
- **Lane colors**: light, distinct, low-saturation. The skill's default palette is in `references/symbols.md`. Lane backgrounds should be subtle so node shapes pop.
- **Title** at the top of the diagram, in a slightly larger weight than node labels.
- **Standard symbols only** — do not invent new shapes. If something doesn't fit a node type, use `process` plus an `annotation`.
- **Arrows enter and exit shapes cleanly** — orthogonal routing, no diagonal lines through other shapes.
- **Label decision branches.** A diamond with unlabeled outgoing edges is a bug.
- **Handoffs are explicit.** When an arrow crosses lanes, it should be unambiguous which shapes it connects.

---

## Common edge cases

- **One actor only**: not really a swimlane — ask if they actually want a plain flowchart.
- **Loops / cycles**: supported. The layout algorithm in `render_svg.py` handles back-edges by routing them around the lane.
- **Parallel flows** (AND-splits): represent with an unlabeled diamond or a small filled circle (BPMN parallel gateway). Use `type: "decision"` with a `subtype: "parallel"` field.
- **Very wide diagrams** (>15 nodes in a single lane): suggest splitting into sub-processes or a multi-page deck.
- **Pools vs. lanes**: a BPMN "pool" is a higher-level container (e.g., a separate company) holding multiple lanes. The canonical JSON supports this via an optional `pool` field on each lane. If the user doesn't mention pools, omit them.

---

## When _not_ to use this skill

- The user wants a generic flowchart with no actors → use a regular flowchart approach, not swimlanes.
- The user wants an org chart, mind map, or entity-relationship diagram → those are different diagram types.
- The user wants real-time editable diagramming in a third-party tool (Lucidchart, Visio, Miro) → produce the canonical JSON or Mermaid and tell them how to import.

---

## Reference files

- `references/symbols.md` — Full table of node shapes, BPMN equivalents, and the default color palette.
- `references/mermaid-syntax.md` — Mermaid flowchart conventions and the JSON-to-Mermaid mapping.
- `references/parsing.md` — Detailed image and PDF parsing strategy, including shape recognition heuristics.
- `scripts/render_svg.py` — JSON → SVG renderer with layout algorithm.
- `scripts/render_pptx.py` — JSON → editable .pptx via python-pptx.
- `scripts/json_to_mermaid.py` — JSON → Mermaid flowchart syntax.
