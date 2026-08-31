#!/usr/bin/env python3
"""Render a swimlane diagram from canonical JSON to SVG.

Usage:
    python render_svg.py --input diagram.json --output diagram.svg
    cat diagram.json | python render_svg.py > diagram.svg
"""

import argparse
import json
import sys
from collections import defaultdict, deque

# ---- Layout constants ----
LANE_HEADER_W = 120  # width of left lane-label column (horizontal layout)
LANE_HEADER_H = 50   # height of top lane-label row (vertical layout)
NODE_W = 140
NODE_H = 60
COL_GAP = 60
ROW_GAP = 40
PADDING = 24
TITLE_H = 40

LANE_PALETTE = [
    ("#E8F0FE", "#4285F4"),
    ("#FCE8E6", "#EA4335"),
    ("#FEF7E0", "#FBBC04"),
    ("#E6F4EA", "#34A853"),
    ("#F3E8FD", "#A142F4"),
    ("#E0F2F1", "#00897B"),
    ("#FFF3E0", "#F57C00"),
    ("#ECEFF1", "#546E7A"),
]


def topo_rank(nodes, edges):
    """Longest-path rank via Kahn's algorithm. When stuck on cycles, break by promoting
    the lowest-remaining-indegree node to a synthetic source."""
    node_ids = {n["id"] for n in nodes}
    outgoing = defaultdict(list)
    incoming = defaultdict(list)
    for e in edges:
        if e["from"] in node_ids and e["to"] in node_ids:
            outgoing[e["from"]].append(e["to"])
            incoming[e["to"]].append(e["from"])
    rank = {}
    indeg = {n["id"]: len(incoming[n["id"]]) for n in nodes}
    queue = deque()
    for n in nodes:
        if indeg[n["id"]] == 0:
            rank[n["id"]] = 0
            queue.append(n["id"])
    while len(rank) < len(nodes):
        while queue:
            u = queue.popleft()
            for v in outgoing[u]:
                if v in rank:
                    continue
                indeg[v] -= 1
                if indeg[v] == 0:
                    rank[v] = max((rank[p] for p in incoming[v] if p in rank), default=-1) + 1
                    queue.append(v)
        if len(rank) < len(nodes):
            # Cycle. Break at the unranked node with smallest remaining indegree.
            candidates = [
                (indeg[n["id"]], i, n["id"])
                for i, n in enumerate(nodes)
                if n["id"] not in rank
            ]
            candidates.sort()
            _, _, victim = candidates[0]
            rank[victim] = max(
                (rank[p] for p in incoming[victim] if p in rank),
                default=max(rank.values(), default=-1),
            ) + 1
            queue.append(victim)
    return rank


def escape_xml(s):
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def shape_svg(node, x, y):
    """Return the SVG element for the node shape at top-left (x, y)."""
    t = node.get("type", "process")
    w, h = NODE_W, NODE_H
    if t in ("start", "end"):
        rx = h / 2
        fill = "#E8F5E9" if t == "start" else "#FFEBEE"
        stroke = "#43A047" if t == "start" else "#E53935"
        return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" ry="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>'
    if t == "decision":
        cx, cy = x + w / 2, y + h / 2
        points = f"{cx},{y} {x + w},{cy} {cx},{y + h} {x},{cy}"
        return f'<polygon points="{points}" fill="#FFF8E1" stroke="#F9A825" stroke-width="1.5"/>'
    if t == "subprocess":
        return (
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" ry="4" fill="white" stroke="#546E7A" stroke-width="1.5"/>'
            f'<line x1="{x + 8}" y1="{y}" x2="{x + 8}" y2="{y + h}" stroke="#546E7A" stroke-width="1.5"/>'
            f'<line x1="{x + w - 8}" y1="{y}" x2="{x + w - 8}" y2="{y + h}" stroke="#546E7A" stroke-width="1.5"/>'
        )
    if t == "data":
        skew = 15
        points = f"{x + skew},{y} {x + w},{y} {x + w - skew},{y + h} {x},{y + h}"
        return f'<polygon points="{points}" fill="white" stroke="#9E9E9E" stroke-width="1.5"/>'
    if t == "document":
        return (
            f'<path d="M {x} {y} L {x + w} {y} L {x + w} {y + h - 6} '
            f'Q {x + 3 * w / 4} {y + h + 6}, {x + w / 2} {y + h - 6} '
            f'T {x} {y + h - 6} Z" fill="white" stroke="#9E9E9E" stroke-width="1.5"/>'
        )
    if t == "delay":
        return (
            f'<path d="M {x} {y} L {x + w * 0.7} {y} '
            f'A {h / 2} {h / 2} 0 0 1 {x + w * 0.7} {y + h} '
            f'L {x} {y + h} Z" fill="white" stroke="#9E9E9E" stroke-width="1.5"/>'
        )
    if t == "annotation":
        return (
            f'<path d="M {x + 8} {y} L {x} {y} L {x} {y + h} L {x + 8} {y + h}" '
            f'fill="none" stroke="#9E9E9E" stroke-width="1" stroke-dasharray="3,2"/>'
        )
    # default: process
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" ry="4" fill="white" stroke="#546E7A" stroke-width="1.5"/>'


def wrap_text(label, max_chars=18, max_lines=3):
    words = label.split()
    lines, current = [], ""
    for word in words:
        if not current:
            current = word
        elif len(current) + 1 + len(word) <= max_chars:
            current += " " + word
        else:
            lines.append(current)
            current = word
        if len(lines) == max_lines - 1 and len(current) + 1 > max_chars:
            # truncate
            lines.append(current[: max_chars - 1] + "…")
            return lines
    if current:
        lines.append(current)
    return lines[:max_lines]


def render(data):
    title = data.get("title", "Swimlane Diagram")
    orientation = data.get("orientation", "horizontal")
    lanes = data["lanes"]
    nodes = data["nodes"]
    edges = data.get("edges", [])

    rank = topo_rank(nodes, edges)
    max_rank = max(rank.values(), default=0)
    lane_index = {lane["id"]: i for i, lane in enumerate(lanes)}

    # Detect node collisions in the same (lane, rank) cell and offset them
    # by inserting empty rank slots so all nodes in a lane have distinct ranks
    cell_nodes = defaultdict(list)
    for n in nodes:
        cell_nodes[(n["lane"], rank[n["id"]])].append(n["id"])
    # If two nodes share a cell, give the second one rank+1 and shift downstream
    rank_adjusted = dict(rank)
    for (lane_id, r), node_ids in cell_nodes.items():
        if len(node_ids) > 1:
            # Push duplicates to higher ranks
            for offset, nid in enumerate(node_ids[1:], start=1):
                rank_adjusted[nid] = r + offset
    rank = rank_adjusted
    max_rank = max(rank.values(), default=0)

    positions = {}
    if orientation == "horizontal":
        col_w = NODE_W + COL_GAP
        row_h = NODE_H + ROW_GAP * 2
        diagram_w = LANE_HEADER_W + (max_rank + 1) * col_w + COL_GAP
        diagram_h = TITLE_H + len(lanes) * row_h + PADDING
        for n in nodes:
            r = rank[n["id"]]
            li = lane_index[n["lane"]]
            x = LANE_HEADER_W + r * col_w + (col_w - NODE_W) / 2
            y = TITLE_H + li * row_h + (row_h - NODE_H) / 2
            positions[n["id"]] = (x, y)
    else:
        col_w = NODE_W + COL_GAP * 2
        row_h = NODE_H + ROW_GAP
        diagram_w = len(lanes) * col_w + PADDING
        diagram_h = TITLE_H + LANE_HEADER_H + (max_rank + 1) * row_h + ROW_GAP
        for n in nodes:
            r = rank[n["id"]]
            li = lane_index[n["lane"]]
            x = li * col_w + (col_w - NODE_W) / 2
            y = TITLE_H + LANE_HEADER_H + r * row_h + (row_h - NODE_H) / 2
            positions[n["id"]] = (x, y)

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {diagram_w} {diagram_h}" '
        f'font-family="-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif">',
        '<defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="5" '
        'orient="auto" markerUnits="strokeWidth">'
        '<path d="M 0 0 L 10 5 L 0 10 z" fill="#546E7A"/></marker></defs>',
        f'<text x="{diagram_w / 2}" y="26" text-anchor="middle" font-size="18" '
        f'font-weight="600" fill="#212121">{escape_xml(title)}</text>',
    ]

    # Lanes
    for i, lane in enumerate(lanes):
        fill, stroke = LANE_PALETTE[i % len(LANE_PALETTE)]
        if orientation == "horizontal":
            y = TITLE_H + i * row_h
            parts.append(
                f'<rect x="{LANE_HEADER_W}" y="{y}" width="{diagram_w - LANE_HEADER_W}" '
                f'height="{row_h}" fill="{fill}" stroke="{stroke}" stroke-width="1" opacity="0.55"/>'
            )
            parts.append(
                f'<rect x="0" y="{y}" width="{LANE_HEADER_W}" height="{row_h}" '
                f'fill="{fill}" stroke="{stroke}" stroke-width="1"/>'
            )
            parts.append(
                f'<text x="{LANE_HEADER_W / 2}" y="{y + row_h / 2 + 5}" '
                f'text-anchor="middle" font-size="14" font-weight="600" '
                f'fill="{stroke}">{escape_xml(lane["name"])}</text>'
            )
        else:
            x = i * col_w
            parts.append(
                f'<rect x="{x}" y="{TITLE_H + LANE_HEADER_H}" width="{col_w}" '
                f'height="{diagram_h - TITLE_H - LANE_HEADER_H}" fill="{fill}" '
                f'stroke="{stroke}" stroke-width="1" opacity="0.55"/>'
            )
            parts.append(
                f'<rect x="{x}" y="{TITLE_H}" width="{col_w}" height="{LANE_HEADER_H}" '
                f'fill="{fill}" stroke="{stroke}" stroke-width="1"/>'
            )
            parts.append(
                f'<text x="{x + col_w / 2}" y="{TITLE_H + LANE_HEADER_H / 2 + 5}" '
                f'text-anchor="middle" font-size="14" font-weight="600" '
                f'fill="{stroke}">{escape_xml(lane["name"])}</text>'
            )

    # Build a quick lookup: (lane_id, rank) -> node_id so we can detect intervening nodes
    occupied = {(n["lane"], rank[n["id"]]): n["id"] for n in nodes}
    rank_of = rank
    lane_of = {n["id"]: n["lane"] for n in nodes}

    def edge_skips_lane_nodes(src, dst):
        """True if src→dst stays in the same lane and skips one or more intervening node ranks."""
        if lane_of[src] != lane_of[dst]:
            return False
        r1, r2 = rank_of[src], rank_of[dst]
        lo, hi = (r1, r2) if r1 < r2 else (r2, r1)
        if hi - lo < 2:
            return False
        for r in range(lo + 1, hi):
            if (lane_of[src], r) in occupied:
                return True
        return False

    # Edges
    for e in edges:
        if e["from"] not in positions or e["to"] not in positions:
            continue
        x1, y1 = positions[e["from"]]
        x2, y2 = positions[e["to"]]
        src_id, dst_id = e["from"], e["to"]
        r1, r2 = rank_of[src_id], rank_of[dst_id]
        same_lane = lane_of[src_id] == lane_of[dst_id]
        is_back = r2 < r1
        same_rank = r1 == r2

        # Pick default faces for forward edges
        if orientation == "horizontal":
            if x2 > x1:
                sx, sy = x1 + NODE_W, y1 + NODE_H / 2
                tx, ty = x2, y2 + NODE_H / 2
            elif x2 < x1:
                sx, sy = x1, y1 + NODE_H / 2
                tx, ty = x2 + NODE_W, y2 + NODE_H / 2
            else:
                if y2 > y1:
                    sx, sy = x1 + NODE_W / 2, y1 + NODE_H
                    tx, ty = x2 + NODE_W / 2, y2
                else:
                    sx, sy = x1 + NODE_W / 2, y1
                    tx, ty = x2 + NODE_W / 2, y2 + NODE_H
        else:
            if y2 > y1:
                sx, sy = x1 + NODE_W / 2, y1 + NODE_H
                tx, ty = x2 + NODE_W / 2, y2
            elif y2 < y1:
                sx, sy = x1 + NODE_W / 2, y1
                tx, ty = x2 + NODE_W / 2, y2 + NODE_H
            else:
                if x2 > x1:
                    sx, sy = x1 + NODE_W, y1 + NODE_H / 2
                    tx, ty = x2, y2 + NODE_H / 2
                else:
                    sx, sy = x1, y1 + NODE_H / 2
                    tx, ty = x2 + NODE_W, y2 + NODE_H / 2

        same_lane_skip = same_lane and edge_skips_lane_nodes(src_id, dst_id)

        if orientation == "horizontal":
            if is_back and not same_rank:
                # Back-edge — route over the top of the upper lane (between src and dst)
                upper_li = min(lane_index[lane_of[src_id]], lane_index[lane_of[dst_id]])
                band_y = TITLE_H + upper_li * row_h + 12
                sx, sy = x1 + NODE_W / 2, y1
                tx, ty = x2 + NODE_W / 2, y2
                path = f"M {sx} {sy} L {sx} {band_y} L {tx} {band_y} L {tx} {ty}"
            elif same_lane_skip:
                # Forward skip within a lane — route along the bottom of the lane
                li = lane_index[lane_of[src_id]]
                by = TITLE_H + li * row_h + row_h - 12
                sx, sy = x1 + NODE_W / 2, y1 + NODE_H
                tx, ty = x2 + NODE_W / 2, y2 + NODE_H
                path = f"M {sx} {sy} L {sx} {by} L {tx} {by} L {tx} {ty}"
            elif sx == tx or sy == ty:
                path = f"M {sx} {sy} L {tx} {ty}"
            else:
                mx = (sx + tx) / 2
                path = f"M {sx} {sy} L {mx} {sy} L {mx} {ty} L {tx} {ty}"
        else:  # vertical
            if is_back and not same_rank:
                upper_li = min(lane_index[lane_of[src_id]], lane_index[lane_of[dst_id]])
                band_x = upper_li * col_w + 12
                sx, sy = x1, y1 + NODE_H / 2
                tx, ty = x2, y2 + NODE_H / 2
                path = f"M {sx} {sy} L {band_x} {sy} L {band_x} {ty} L {tx} {ty}"
            elif same_lane_skip:
                li = lane_index[lane_of[src_id]]
                bx = li * col_w + col_w - 12
                sx, sy = x1 + NODE_W, y1 + NODE_H / 2
                tx, ty = x2 + NODE_W, y2 + NODE_H / 2
                path = f"M {sx} {sy} L {bx} {sy} L {bx} {ty} L {tx} {ty}"
            elif sx == tx or sy == ty:
                path = f"M {sx} {sy} L {tx} {ty}"
            else:
                my = (sy + ty) / 2
                path = f"M {sx} {sy} L {sx} {my} L {tx} {my} L {tx} {ty}"

        parts.append(
            f'<path d="{path}" fill="none" stroke="#546E7A" stroke-width="1.5" marker-end="url(#arrow)"/>'
        )

        if e.get("label"):
            lx = (sx + tx) / 2
            ly = (sy + ty) / 2 - 8
            lbl = escape_xml(str(e["label"]))
            text_w = max(28, len(lbl) * 7 + 8)
            parts.append(
                f'<rect x="{lx - text_w / 2}" y="{ly - 11}" width="{text_w}" height="15" '
                f'fill="white" opacity="0.9" rx="2" ry="2"/>'
            )
            parts.append(
                f'<text x="{lx}" y="{ly}" text-anchor="middle" font-size="11" '
                f'fill="#424242">{lbl}</text>'
            )

    # Nodes
    for n in nodes:
        x, y = positions[n["id"]]
        parts.append(shape_svg(n, x, y))
        lines = wrap_text(n.get("label", ""))
        line_h = 14
        total_h = len(lines) * line_h
        start_y = y + NODE_H / 2 - total_h / 2 + 11
        for i, line in enumerate(lines):
            parts.append(
                f'<text x="{x + NODE_W / 2}" y="{start_y + i * line_h}" '
                f'text-anchor="middle" font-size="12" fill="#212121">{escape_xml(line)}</text>'
            )

    parts.append("</svg>")
    return "\n".join(parts)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input", "-i", default="-", help="JSON input file (- for stdin)")
    p.add_argument("--output", "-o", default="-", help="SVG output file (- for stdout)")
    args = p.parse_args()
    if args.input == "-":
        data = json.load(sys.stdin)
    else:
        with open(args.input) as f:
            data = json.load(f)
    svg = render(data)
    if args.output == "-":
        sys.stdout.write(svg)
    else:
        with open(args.output, "w") as f:
            f.write(svg)


if __name__ == "__main__":
    main()
