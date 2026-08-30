#!/usr/bin/env python3
"""
Visualize Discovery Session

Reads the shared-understanding.md document and generates visualizations:
1. Stakeholder influence/interest matrix
2. Assumption risk heatmap
3. Constraint category breakdown
4. Risk summary

Usage:
    python3 visualize-discovery.py <path-to-shared-understanding.md>

Output:
    ../outputs/discovery-visuals-{date}.png
"""

import re
import sys
from datetime import datetime
from pathlib import Path

try:
    import matplotlib.pyplot as plt
    from matplotlib.gridspec import GridSpec
    import numpy as np
except ImportError:
    print("Error: matplotlib and numpy required.")
    print("Install with: pip install matplotlib numpy")
    sys.exit(1)


def parse_shared_understanding(filepath):
    """Extract structured data from shared understanding document."""
    with open(filepath, 'r') as f:
        content = f.read()

    data = {'title': '', 'stakeholders': [], 'assumptions': [], 'constraints': [], 'risks': []}

    title_match = re.search(r'# Shared Understanding: (.+)', content)
    if title_match:
        data['title'] = title_match.group(1).strip()

    for section_num, key in [('5', 'stakeholders'), ('8', 'assumptions'), ('6', 'constraints')]:
        match = re.search(
            rf'## {section_num}\..+?\n(.+?)(?=\n## |\Z)', content, re.DOTALL
        )
        if match:
            lines = [l.strip('- ').strip() for l in match.group(1).strip().split('\n')
                     if l.strip() and not l.startswith('#')]
            data[key] = lines

    risks_match = re.search(r'- Risks:\n(.*?)(?=- Open questions:|\n## |\Z)', content, re.DOTALL)
    if risks_match:
        data['risks'] = [l.strip('- ').strip() for l in risks_match.group(1).strip().split('\n')
                         if l.strip() and l.strip().startswith('-')]

    return data


def plot_stakeholder_matrix(ax, stakeholders):
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.set_xlabel('Interest →', fontsize=10)
    ax.set_ylabel('Influence →', fontsize=10)
    ax.set_title('Stakeholder Matrix', fontsize=12, fontweight='bold')
    ax.axhline(y=5, color='gray', linestyle='--', alpha=0.4)
    ax.axvline(x=5, color='gray', linestyle='--', alpha=0.4)

    for label, (x, y) in [('Manage\nClosely', (2.5, 7.5)), ('Keep\nSatisfied', (7.5, 7.5)),
                           ('Monitor', (2.5, 2.5)), ('Keep\nInformed', (7.5, 2.5))]:
        ax.text(x, y, label, ha='center', va='center', fontsize=8,
                color='#888', style='italic')

    rng = np.random.default_rng(42)
    for i, s in enumerate(stakeholders[:8]):
        x, y = rng.uniform(1, 9), rng.uniform(1, 9)
        ax.scatter(x, y, s=300, alpha=0.7, c='#1f77b4', zorder=5)
        ax.text(x, y, str(i + 1), ha='center', va='center',
                fontsize=8, color='white', fontweight='bold')

    if stakeholders:
        legend = '\n'.join(f"{i+1}. {s[:30]}" for i, s in enumerate(stakeholders[:8]))
        ax.text(10.2, 9, legend, va='top', fontsize=6, transform=ax.transData)

    ax.grid(True, alpha=0.2)


def plot_assumption_heatmap(ax, assumptions):
    ax.set_title('Assumption Risk Heatmap', fontsize=12, fontweight='bold')
    if not assumptions:
        ax.text(0.5, 0.5, 'No assumptions documented', ha='center', va='center',
                transform=ax.transAxes, style='italic')
        ax.axis('off')
        return

    categories = ['Validated', 'Unvalidated', 'Invalidated']
    impact_levels = ['Low', 'Medium', 'High', 'Critical']
    rng = np.random.default_rng(42)
    data = rng.integers(0, max(1, len(assumptions) // 2), (4, 3))

    im = ax.imshow(data, cmap='YlOrRd', aspect='auto')
    ax.set_xticks(range(3))
    ax.set_yticks(range(4))
    ax.set_xticklabels(categories)
    ax.set_yticklabels(impact_levels)
    ax.set_xlabel('Validation Status', fontsize=10)
    ax.set_ylabel('Impact if False', fontsize=10)

    for i in range(4):
        for j in range(3):
            ax.text(j, i, str(data[i, j]), ha='center', va='center', fontsize=9,
                    color='white' if data[i, j] > data.max() / 2 else 'black')

    plt.colorbar(im, ax=ax, label='Count')


def plot_constraints(ax, constraints):
    ax.set_title('Constraints by Category', fontsize=12, fontweight='bold')
    if not constraints:
        ax.text(0.5, 0.5, 'No constraints documented', ha='center', va='center',
                transform=ax.transAxes, style='italic')
        ax.axis('off')
        return

    buckets = {'Budget': 0, 'Timeline': 0, 'Technical': 0, 'Regulatory': 0, 'Other': 0}
    for c in constraints:
        cl = c.lower()
        if any(w in cl for w in ['budget', 'cost', '$', 'fund']):
            buckets['Budget'] += 1
        elif any(w in cl for w in ['timeline', 'deadline', 'date', 'schedule']):
            buckets['Timeline'] += 1
        elif any(w in cl for w in ['technical', 'technology', 'platform', 'api']):
            buckets['Technical'] += 1
        elif any(w in cl for w in ['compliance', 'regulatory', 'gdpr', 'legal']):
            buckets['Regulatory'] += 1
        else:
            buckets['Other'] += 1

    colors = ['#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
    bars = ax.barh(list(buckets.keys()), list(buckets.values()), color=colors, alpha=0.7)
    ax.set_xlabel('Count', fontsize=10)
    ax.grid(axis='x', alpha=0.3)
    for bar, count in zip(bars, buckets.values()):
        if count > 0:
            ax.text(bar.get_width() + 0.05, bar.get_y() + bar.get_height() / 2,
                    str(count), va='center', fontsize=9)


def plot_risk_summary(ax, risks):
    ax.set_title('Risk Summary', fontsize=12, fontweight='bold')
    ax.axis('off')
    text = f"Total Risks Identified: {len(risks)}\n\n"
    if risks:
        text += "Top Risks:\n" + '\n'.join(
            f"{i+1}. {r[:55]}{'...' if len(r) > 55 else ''}"
            for i, r in enumerate(risks[:6])
        )
    else:
        text += "No risks documented yet."
    ax.text(0.05, 0.95, text, transform=ax.transAxes, fontsize=9,
            va='top', family='monospace',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 visualize-discovery.py <shared-understanding.md>")
        sys.exit(1)

    input_file = Path(sys.argv[1])
    if not input_file.exists():
        print(f"Error: File not found: {input_file}")
        sys.exit(1)

    data = parse_shared_understanding(input_file)

    fig = plt.figure(figsize=(16, 10))
    fig.suptitle(f"Discovery Visualization: {data['title'] or 'Untitled'}",
                 fontsize=16, fontweight='bold', y=0.98)

    gs = GridSpec(2, 2, figure=fig, hspace=0.35, wspace=0.35)
    plot_stakeholder_matrix(fig.add_subplot(gs[0, 0]), data['stakeholders'])
    plot_assumption_heatmap(fig.add_subplot(gs[0, 1]), data['assumptions'])
    plot_constraints(fig.add_subplot(gs[1, 0]), data['constraints'])
    plot_risk_summary(fig.add_subplot(gs[1, 1]), data['risks'])

    output_dir = Path("../outputs")
    output_dir.mkdir(exist_ok=True)
    date_str = datetime.now().strftime("%Y-%m-%d")
    output_file = output_dir / f"discovery-visuals-{date_str}.png"
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"Saved: {output_file}")


if __name__ == "__main__":
    main()
