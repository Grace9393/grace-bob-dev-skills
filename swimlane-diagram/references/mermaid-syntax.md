# Mermaid Syntax for Swimlane Diagrams

Mermaid doesn't have first-class swimlane support, but `flowchart` with `subgraph` blocks works well and is the de facto convention.

## Direction

- `flowchart LR` — Left to Right. Use for **horizontal** swimlanes (lanes stacked as rows).
- `flowchart TD` — Top Down. Use for **vertical** swimlanes (lanes side by side as columns).

> Note: Mermaid subgraphs default to the same direction as the parent. For horizontal swimlanes, each lane's internal flow should also be LR — this happens automatically with `flowchart LR`.

## Node shape mapping

| Canonical `type`        | Mermaid syntax                | Example                  |
|-------------------------|-------------------------------|--------------------------|
| `start`, `end`          | `id([label])`                 | `n1([Sign up])`          |
| `process`               | `id[label]`                   | `n2[Send email]`         |
| `decision` (exclusive)  | `id{label}`                   | `n3{Approved?}`          |
| `decision` (parallel)   | `id{{label}}` (hexagon-ish)   | `n3{{Fan out}}`          |
| `subprocess`            | `id[[label]]`                 | `n4[[Run pipeline]]`     |
| `data`                  | `id[/label/]`                 | `n5[/Customer record/]`  |
| `document`              | `id[(label)]` (cylinder-ish)¹ | `n5[(Invoice PDF)]`      |
| `delay`                 | `id((label))` (circle)²       | `n6((Wait 24h))`         |
| `annotation`            | `id>label]`                   | `n7>SLA: 4h]`            |

¹ Mermaid has no native "document" shape; cylinder is the closest visually distinct option.
² Mermaid has no native "delay" shape; a circle is a reasonable substitute.

## Edges

- Plain: `n1 --> n2`
- Labeled: `n2 -->|yes| n3`
- Dotted (for annotations): `n2 -.-> n7`
- Thick (for emphasis, optional): `n1 ==> n2`

## Subgraph per lane

```
flowchart LR
  subgraph customer [Customer]
    n1([Sign up])
    n6([Account ready])
  end
  subgraph sales [Sales]
    n2[Send welcome email]
  end
  subgraph ops [Operations]
    n3{Enterprise tier?}
    n4[Assign CSM]
    n5[Auto-provision]
  end

  n1 --> n2 --> n3
  n3 -->|yes| n4
  n3 -->|no|  n5
  n4 --> n6
  n5 --> n6
```

The bracketed display name (e.g., `subgraph customer [Customer]`) is optional but recommended — it lets the JSON `name` field differ from the `id` field (which must be alphanumeric).

## Coloring lanes

Append `classDef` and `class` statements:

```
classDef customerLane fill:#E8F0FE,stroke:#4285F4
classDef salesLane    fill:#FCE8E6,stroke:#EA4335
classDef opsLane      fill:#FEF7E0,stroke:#FBBC04

class customer customerLane
class sales salesLane
class ops opsLane
```

## Conversion algorithm (JSON → Mermaid)

```
1. Write the header: "flowchart LR" if horizontal, "flowchart TD" if vertical.
2. For each lane in lanes[]:
     - Write `subgraph <id> [<name>]`
     - For each node where node.lane == lane.id, write the node line in Mermaid shape syntax.
     - Write `end`
3. Write a blank line.
4. For each edge in edges[]:
     - If edge.label: write `<from> -->|<label>| <to>`
     - Else:         write `<from> --> <to>`
5. Append classDef + class statements for lane colors.
```

The `scripts/json_to_mermaid.py` script implements this.

## Limitations to flag to the user

Mermaid swimlanes look noticeably less polished than rendered SVG/PPTX because:
- Mermaid's subgraph borders aren't customizable per-subgraph beyond fill/stroke.
- Lane labels appear at the top of each subgraph rather than as a separate header column.
- Node placement within lanes is automatic — Mermaid may reorder nodes in ways that look odd.

If the user wants a polished diagram, recommend SVG or PPTX. Mermaid is best when they want something portable, version-controllable, and editable as text.
