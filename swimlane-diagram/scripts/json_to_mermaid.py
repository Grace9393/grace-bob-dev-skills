#!/usr/bin/env python3
"""Convert canonical swimlane JSON to Mermaid flowchart syntax.

Usage:
    python json_to_mermaid.py --input diagram.json
    cat diagram.json | python json_to_mermaid.py
"""

import argparse
import json
import re
import sys
from collections import defaultdict

LANE_COLORS = [
    ("#E8F0FE", "#4285F4"),
    ("#FCE8E6", "#EA4335"),
    ("#FEF7E0", "#FBBC04"),
    ("#E6F4EA", "#34A853"),
    ("#F3E8FD", "#A142F4"),
    ("#E0F2F1", "#00897B"),
    ("#FFF3E0", "#F57C00"),
    ("#ECEFF1", "#546E7A"),
]


def mermaid_id(raw):
    """Mermaid IDs must be alphanumeric / underscore — sanitize."""
    cleaned = re.sub(r"[^A-Za-z0-9_]", "_", str(raw))
    if not cleaned or not cleaned[0].isalpha():
        cleaned = "n_" + cleaned
    return cleaned


def shape_for(node):
    t = node.get("type", "process")
    raw = node.get("label", "")
    # Escape characters that break Mermaid label parsing
    label = raw.replace('"', "&quot;").replace("\n", " ")
    nid = mermaid_id(node["id"])
    if t in ("start", "end"):
        return f'{nid}(["{label}"])'
    if t == "decision":
        if node.get("subtype") == "parallel":
            return f'{nid}{{{{"{label}"}}}}'
        return f'{nid}{{"{label}"}}'
    if t == "subprocess":
        return f'{nid}[["{label}"]]'
    if t == "data":
        return f'{nid}[/"{label}"/]'
    if t == "document":
        return f'{nid}[("{label}")]'
    if t == "delay":
        return f'{nid}(("{label}"))'
    if t == "annotation":
        return f'{nid}>"{label}"]'
    return f'{nid}["{label}"]'


def convert(data):
    orientation = data.get("orientation", "horizontal")
    direction = "LR" if orientation == "horizontal" else "TD"
    lanes = data["lanes"]
    nodes = data["nodes"]
    edges = data.get("edges", [])

    by_lane = defaultdict(list)
    for n in nodes:
        by_lane[n["lane"]].append(n)

    lines = []
    title = data.get("title")
    if title:
        # Mermaid title goes via a front-matter or title directive
        lines.append("---")
        lines.append(f"title: {title}")
        lines.append("---")
    lines.append(f"flowchart {direction}")

    for lane in lanes:
        lid = mermaid_id(lane["id"])
        name = lane["name"].replace('"', "")
        lines.append(f"  subgraph {lid} [\"{name}\"]")
        for node in by_lane.get(lane["id"], []):
            lines.append(f"    {shape_for(node)}")
        lines.append("  end")

    if edges:
        lines.append("")
        for e in edges:
            f = mermaid_id(e["from"])
            t = mermaid_id(e["to"])
            label = e.get("label")
            if label:
                escaped = str(label).replace("|", "\\|")
                lines.append(f"  {f} -->|{escaped}| {t}")
            else:
                lines.append(f"  {f} --> {t}")

    # Lane coloring
    lines.append("")
    for i, lane in enumerate(lanes):
        fill, stroke = LANE_COLORS[i % len(LANE_COLORS)]
        lid = mermaid_id(lane["id"])
        cls = f"{lid}Cls"
        lines.append(f"  classDef {cls} fill:{fill},stroke:{stroke},stroke-width:1px")
        lines.append(f"  class {lid} {cls}")

    return "\n".join(lines)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input", "-i", default="-")
    p.add_argument("--output", "-o", default="-")
    args = p.parse_args()
    if args.input == "-":
        data = json.load(sys.stdin)
    else:
        with open(args.input) as f:
            data = json.load(f)
    out = convert(data)
    if args.output == "-":
        sys.stdout.write(out + "\n")
    else:
        with open(args.output, "w") as f:
            f.write(out + "\n")


if __name__ == "__main__":
    main()
