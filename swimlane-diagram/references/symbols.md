# Symbols and Style Reference

## Node shape table

| `type`        | Visual shape              | Meaning                              | BPMN equivalent          |
|---------------|---------------------------|--------------------------------------|--------------------------|
| `start`       | Rounded oval (stadium)    | Entry point of the process           | Start event (thin circle)|
| `end`         | Rounded oval (stadium)    | Exit point of the process            | End event (thick circle) |
| `process`     | Rectangle                 | An action or task                    | Task                     |
| `decision`    | Diamond                   | Branch in flow                       | Exclusive gateway (XOR)  |
| `subprocess`  | Rectangle, double bars    | Calls a nested process               | Sub-process              |
| `data`        | Parallelogram             | Data input or output                 | Data object              |
| `document`    | Rectangle, wavy bottom    | A document is produced/consumed      | Data object (doc icon)   |
| `delay`       | D-shape (half rectangle)  | A waiting period                     | Timer event              |
| `annotation`  | Bracket / no shape        | Explanatory note, dotted line attach | Text annotation          |

### Decision subtypes
- `subtype: "exclusive"` (default) — XOR, exactly one outgoing path taken. Diamond.
- `subtype: "parallel"` — AND, all outgoing paths taken simultaneously. Diamond with `+` inside.
- `subtype: "inclusive"` — OR, one or more outgoing paths taken. Diamond with `o` inside.

## SVG dimensions (defaults)

| Element          | Width | Height | Notes                                   |
|------------------|-------|--------|-----------------------------------------|
| Rectangle node   | 140   | 60     | rounded corners radius 4                |
| Stadium (start)  | 120   | 50     | full pill shape                         |
| Diamond          | 140   | 80     | width = height × 1.75 for label fit     |
| Parallelogram    | 140   | 60     | skew 15°                                |
| Lane header (h)  | 120   | —      | left column for horizontal layout       |
| Lane header (v)  | —     | 50     | top row for vertical layout             |
| Horizontal gap   | 60    |        | between nodes in the same lane          |
| Vertical gap     | 40    |        | between lanes                           |
| Edge stroke      | 1.5px |        | arrowhead 8×8                           |

## Color palette

Lane backgrounds use a soft, distinguishable palette. Cycle through these in order:

| Index | Lane background | Border  | Use case               |
|-------|-----------------|---------|------------------------|
| 0     | `#E8F0FE`       | `#4285F4` | Customer / external   |
| 1     | `#FCE8E6`       | `#EA4335` | Sales / outbound      |
| 2     | `#FEF7E0`       | `#FBBC04` | Operations            |
| 3     | `#E6F4EA`       | `#34A853` | Engineering / build   |
| 4     | `#F3E8FD`       | `#A142F4` | Finance / approvals   |
| 5     | `#E0F2F1`       | `#00897B` | Support / service     |
| 6     | `#FFF3E0`       | `#F57C00` | Legal / compliance    |
| 7     | `#ECEFF1`       | `#546E7A` | System / automation   |

Node fills:
- `process`, `subprocess`: white (`#FFFFFF`) with the lane border color as outline.
- `decision`: pale yellow (`#FFF8E1`) with `#F9A825` outline.
- `start`, `end`: pale green (`#E8F5E9`) for start, pale red (`#FFEBEE`) for end.
- `data`, `document`: white with `#9E9E9E` outline.
- `annotation`: no fill, gray text, dotted attachment line.

## Typography

- Font family: system sans-serif (`-apple-system, "Segoe UI", Roboto, sans-serif`).
- Title: 18px, weight 600.
- Lane label: 14px, weight 600, color matching lane border.
- Node label: 12px, weight 400.
- Edge label: 11px, weight 400, with semi-transparent white background rectangle for legibility over crossing lines.

## Layout rules

1. **Lane order matters.** Order lanes in the JSON the way they should appear on screen — typically top-to-bottom by frequency of involvement, or in the order they first participate. The renderer does not reorder them.
2. **Nodes are placed in topological order within each lane.** If A → B and both are in lane L, A is to the left of B.
3. **Cross-lane edges have a clean entry and exit point** on the shape's edge nearest the other lane.
4. **No diagonal lines.** All edges are orthogonal polylines (right angles only).
5. **Avoid overlaps.** If two edges would cross, route one around. If a node would overlap another, push later nodes further along the flow axis.
