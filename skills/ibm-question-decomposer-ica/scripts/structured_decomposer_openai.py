#!/usr/bin/env python3
"""Layered question decomposer using an OpenAI-compatible API."""

import argparse
import csv
import os
import re
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List, Optional

from openai import OpenAI

DEFAULT_MODEL = "global/anthropic.claude-sonnet-4-5-20250929-v1:0"
DEFAULT_BASE_URL = "http://localhost:10276/v1"
DEFAULT_DEPTH = 2
DEFAULT_MIN_BREADTH = 3
DEFAULT_MAX_BREADTH = 5
DEFAULT_OUTPUT = "outputs/layered_question_decomposition.md"
DEFAULT_MATURITY_OUTPUT = "outputs/layered_question_maturity.csv"
DEFAULT_TEMPERATURE = 0.2


class Framework(Enum):
    ADAPTIVE = "adaptive"
    COMPONENTS = "components"
    FW1H = "5w1h"
    MECE = "mece"
    PESTLE = "pestle"
    SYSTEMS = "systems"
    SCIENTIFIC = "scientific"
    DESIGN = "design"
    ROOT_CAUSE = "root-cause"
    ISSUE_TREE = "issue-tree"
    ACADEMIC = "academic"


class DecompositionFramework(ABC):
    @abstractmethod
    def get_guidance(self) -> str:
        pass


class ComponentsFramework(DecompositionFramework):
    def get_guidance(self) -> str:
        return "Use core components analysis: elements, information needs, scope, dependencies, and perspectives."


class FW1HFramework(DecompositionFramework):
    def get_guidance(self) -> str:
        return "Use 5W1H: generate questions covering Who, What, When, Where, Why, and How."


class MECEFramework(DecompositionFramework):
    def get_guidance(self) -> str:
        return "Use MECE: create mutually exclusive, collectively exhaustive dimensions."


class PESTLEFramework(DecompositionFramework):
    def get_guidance(self) -> str:
        return "Use PESTLE: political, economic, social, technological, legal, and environmental angles."


class SystemsFramework(DecompositionFramework):
    def get_guidance(self) -> str:
        return "Use systems thinking: inputs, processes, outputs, feedback loops, environment, stakeholders."


class ScientificFramework(DecompositionFramework):
    def get_guidance(self) -> str:
        return "Use scientific inquiry: observation, hypothesis, method, data, analysis, validation."


class DesignFramework(DecompositionFramework):
    def get_guidance(self) -> str:
        return "Use design thinking: users, pain points, desirability, feasibility, viability, iteration."


class RootCauseFramework(DecompositionFramework):
    def get_guidance(self) -> str:
        return "Use root-cause analysis (5 Whys): progressively probe from symptoms to systemic causes."


class IssueTreeFramework(DecompositionFramework):
    def get_guidance(self) -> str:
        return "Use issue-tree decomposition: break into hierarchical branches that are non-overlapping and complete."


class AcademicFramework(DecompositionFramework):
    def get_guidance(self) -> str:
        return "Use academic structure: definitions, literature, assumptions, methodology, evidence, limitations."


FRAMEWORKS = {
    Framework.COMPONENTS: ComponentsFramework(),
    Framework.FW1H: FW1HFramework(),
    Framework.MECE: MECEFramework(),
    Framework.PESTLE: PESTLEFramework(),
    Framework.SYSTEMS: SystemsFramework(),
    Framework.SCIENTIFIC: ScientificFramework(),
    Framework.DESIGN: DesignFramework(),
    Framework.ROOT_CAUSE: RootCauseFramework(),
    Framework.ISSUE_TREE: IssueTreeFramework(),
    Framework.ACADEMIC: AcademicFramework(),
}


@dataclass
class QuestionNode:
    node_id: str
    question: str
    level: int
    framework: Framework
    children: List["QuestionNode"] = field(default_factory=list)


@dataclass
class LeafAssessment:
    node_id: str
    question: str
    framework: str
    path: str
    criteria: List[str]


def parse_numbered_questions(text: str, max_items: int) -> List[str]:
    matches = re.findall(r"^\s*\d+\.\s+(.+?)\s*$", text, flags=re.MULTILINE)
    cleaned = [m.strip() for m in matches if m.strip()]
    return cleaned[:max_items]


def parse_maturity_levels(text: str) -> List[str]:
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    parsed: List[str] = []
    for line in lines:
        m = re.match(r"^(?:\d+[\).\s-]*|Level\s*\d+[\s:\-]*)\s*(.+)$", line, flags=re.IGNORECASE)
        if m:
            parsed.append(m.group(1).strip())
        elif ":" in line:
            parsed.append(line.strip())
        if len(parsed) == 5:
            break
    return parsed


def normalize_framework(value: str) -> Framework:
    return Framework(value.lower().strip())


def choose_framework_adaptive(
    client: OpenAI,
    model: str,
    question: str,
    temperature: float,
) -> Framework:
    choices = [f.value for f in Framework if f != Framework.ADAPTIVE]
    prompt = f"""
Choose the single best framework for decomposing the question.

Question:
{question}

Allowed frameworks: {", ".join(choices)}

Return only the framework value.
""".strip()
    response = client.chat.completions.create(
        model=model,
        temperature=0.0 if temperature > 0.0 else temperature,
        messages=[
            {"role": "system", "content": "Return only one framework token from the allowed list."},
            {"role": "user", "content": prompt},
        ],
    )
    content = (response.choices[0].message.content or "").strip().lower()
    for framework in choices:
        if framework in content:
            return Framework(framework)
    return Framework.COMPONENTS


def build_decomposition_prompt(
    question: str,
    framework: Framework,
    depth_remaining: int,
    min_breadth: int,
    max_breadth: int,
    context_chain: List[str],
) -> str:
    context_text = " -> ".join(context_chain) if context_chain else "(root)"
    guidance = FRAMEWORKS.get(framework, FRAMEWORKS[Framework.COMPONENTS]).get_guidance()
    return f"""
You decompose questions into a layered set of focused subquestions.

Framework: {framework.value}
Guidance: {guidance}

Context chain:
{context_text}

Current question:
{question}

Depth remaining after this layer: {depth_remaining}

Requirements:
1. Return {min_breadth} to {max_breadth} subquestions.
2. Keep each subquestion specific and actionable.
3. Avoid duplicate or overlapping subquestions.
4. Output ONLY a numbered list.
""".strip()


def generate_subquestions(
    client: OpenAI,
    model: str,
    question: str,
    framework: Framework,
    depth_remaining: int,
    min_breadth: int,
    max_breadth: int,
    temperature: float,
    context_chain: List[str],
) -> List[str]:
    prompt = build_decomposition_prompt(
        question=question,
        framework=framework,
        depth_remaining=depth_remaining,
        min_breadth=min_breadth,
        max_breadth=max_breadth,
        context_chain=context_chain,
    )
    response = client.chat.completions.create(
        model=model,
        temperature=temperature,
        messages=[
            {"role": "system", "content": "You create clean, layered question decompositions."},
            {"role": "user", "content": prompt},
        ],
    )
    content = response.choices[0].message.content or ""
    return parse_numbered_questions(content, max_items=max_breadth)


def generate_maturity_criteria(
    client: OpenAI,
    model: str,
    question: str,
    context_chain: List[str],
    temperature: float,
) -> List[str]:
    context_text = " -> ".join(context_chain) if context_chain else "(root)"
    prompt = f"""
Create a 5-level maturity assessment for this question.

Context:
{context_text}

Question:
{question}

Output exactly five lines in this format:
1. Initial: ...
2. Developing: ...
3. Defined: ...
4. Managed: ...
5. Optimizing: ...
""".strip()
    response = client.chat.completions.create(
        model=model,
        temperature=temperature,
        messages=[
            {"role": "system", "content": "You produce concise maturity criteria."},
            {"role": "user", "content": prompt},
        ],
    )
    content = response.choices[0].message.content or ""
    criteria = parse_maturity_levels(content)
    if len(criteria) < 5:
        while len(criteria) < 5:
            criteria.append("")
    return criteria[:5]


def decompose_question(
    client: OpenAI,
    model: str,
    question: str,
    depth: int,
    min_breadth: int,
    max_breadth: int,
    temperature: float,
    framework: Framework,
    level: int = 0,
    node_id: str = "1",
    context_chain: Optional[List[str]] = None,
) -> QuestionNode:
    active_context = context_chain[:] if context_chain else []
    node = QuestionNode(node_id=node_id, question=question, level=level, framework=framework)

    if level >= depth:
        return node

    effective_framework = framework
    if framework == Framework.ADAPTIVE:
        effective_framework = choose_framework_adaptive(
            client=client, model=model, question=question, temperature=temperature
        )
        node.framework = effective_framework

    subquestions = generate_subquestions(
        client=client,
        model=model,
        question=question,
        framework=effective_framework,
        depth_remaining=depth - level,
        min_breadth=min_breadth,
        max_breadth=max_breadth,
        temperature=temperature,
        context_chain=active_context,
    )

    for idx, subquestion in enumerate(subquestions, start=1):
        child = decompose_question(
            client=client,
            model=model,
            question=subquestion,
            depth=depth,
            min_breadth=min_breadth,
            max_breadth=max_breadth,
            temperature=temperature,
            framework=framework,
            level=level + 1,
            node_id=f"{node_id}.{idx}",
            context_chain=active_context + [question],
        )
        node.children.append(child)

    return node


def render_markdown(node: QuestionNode, lines: Optional[List[str]] = None) -> List[str]:
    if lines is None:
        lines = []
    indent = "  " * node.level
    lines.append(f"{indent}- **{node.node_id}** [{node.framework.value}]: {node.question}")
    for child in node.children:
        render_markdown(child, lines)
    return lines


def collect_leaves(node: QuestionNode, ancestry: Optional[List[str]] = None) -> List[tuple]:
    chain = (ancestry or []) + [node.question]
    if not node.children:
        return [(node, chain)]
    leaves: List[tuple] = []
    for child in node.children:
        leaves.extend(collect_leaves(child, chain))
    return leaves


def write_maturity_csv(path: Path, assessments: List[LeafAssessment]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "node_id",
                "framework",
                "path",
                "question",
                "level_1_initial",
                "level_2_developing",
                "level_3_defined",
                "level_4_managed",
                "level_5_optimizing",
            ],
        )
        writer.writeheader()
        for row in assessments:
            writer.writerow(
                {
                    "node_id": row.node_id,
                    "framework": row.framework,
                    "path": row.path,
                    "question": row.question,
                    "level_1_initial": row.criteria[0],
                    "level_2_developing": row.criteria[1],
                    "level_3_defined": row.criteria[2],
                    "level_4_managed": row.criteria[3],
                    "level_5_optimizing": row.criteria[4],
                }
            )


def read_question(args: argparse.Namespace) -> str:
    if args.file and args.question:
        raise ValueError("Provide either a positional question or --file, not both.")
    if args.file:
        file_path = Path(args.file)
        if not file_path.exists():
            raise ValueError(f"Question file not found: {file_path}")
        text = file_path.read_text(encoding="utf-8").strip()
        if not text:
            raise ValueError(f"Question file is empty: {file_path}")
        return text
    if args.question:
        return args.question.strip()
    raise ValueError("A root question is required (positional question or --file).")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Layered question decomposition via OpenAI-compatible API"
    )
    parser.add_argument("question", nargs="?", help="Root question to decompose")
    parser.add_argument("--file", help="Read root question from file")
    parser.add_argument(
        "--framework",
        default=Framework.COMPONENTS.value,
        choices=[f.value for f in Framework],
        help=f"Framework (default: {Framework.COMPONENTS.value})",
    )
    parser.add_argument(
        "--depth",
        type=int,
        default=DEFAULT_DEPTH,
        help=f"Max decomposition depth (default: {DEFAULT_DEPTH})",
    )
    parser.add_argument(
        "--min-breadth",
        type=int,
        default=DEFAULT_MIN_BREADTH,
        help=f"Min subquestions per node (default: {DEFAULT_MIN_BREADTH})",
    )
    parser.add_argument(
        "--max-breadth",
        type=int,
        default=DEFAULT_MAX_BREADTH,
        help=f"Max subquestions per node (default: {DEFAULT_MAX_BREADTH})",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help=f"Model name (default: {DEFAULT_MODEL})",
    )
    parser.add_argument(
        "--base-url",
        default=DEFAULT_BASE_URL,
        help=f"OpenAI-compatible base URL (default: {DEFAULT_BASE_URL})",
    )
    parser.add_argument(
        "--api-key",
        default=os.getenv("ICA_API_KEY"),
        help="API key (default: ICA_API_KEY environment variable)",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=DEFAULT_TEMPERATURE,
        help=f"Sampling temperature (default: {DEFAULT_TEMPERATURE})",
    )
    parser.add_argument(
        "--output",
        default=DEFAULT_OUTPUT,
        help=f"Output markdown path (default: {DEFAULT_OUTPUT})",
    )
    parser.add_argument(
        "--maturity",
        action="store_true",
        help="Generate maturity criteria CSV for leaf questions",
    )
    parser.add_argument(
        "--maturity-output",
        default=DEFAULT_MATURITY_OUTPUT,
        help=f"Maturity CSV path (default: {DEFAULT_MATURITY_OUTPUT})",
    )

    args = parser.parse_args()

    try:
        question = read_question(args)
        framework = normalize_framework(args.framework)
        if args.depth < 0:
            raise ValueError("--depth must be >= 0")
        if args.min_breadth < 1 or args.max_breadth < 1:
            raise ValueError("Breadth values must be >= 1")
        if args.min_breadth > args.max_breadth:
            raise ValueError("--min-breadth cannot be greater than --max-breadth")
        if not args.api_key:
            raise ValueError("Missing API key. Set ICA_API_KEY or pass --api-key.")

        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        client = OpenAI(api_key=args.api_key, base_url=args.base_url)

        tree = decompose_question(
            client=client,
            model=args.model,
            question=question,
            depth=args.depth,
            min_breadth=args.min_breadth,
            max_breadth=args.max_breadth,
            temperature=args.temperature,
            framework=framework,
        )

        lines = [
            "# Layered Question Decomposition",
            "",
            f"- Generated: {datetime.now().isoformat(timespec='seconds')}",
            f"- Model: {args.model}",
            f"- Base URL: {args.base_url}",
            f"- Framework: {framework.value}",
            f"- Depth: {args.depth}",
            f"- Breadth: {args.min_breadth}-{args.max_breadth}",
            f"- Maturity Mode: {'on' if args.maturity else 'off'}",
            "",
            "## Tree",
            "",
        ]
        lines.extend(render_markdown(tree))
        output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

        if args.maturity:
            leaf_rows: List[LeafAssessment] = []
            for leaf_node, chain in collect_leaves(tree):
                criteria = generate_maturity_criteria(
                    client=client,
                    model=args.model,
                    question=leaf_node.question,
                    context_chain=chain[:-1],
                    temperature=args.temperature,
                )
                leaf_rows.append(
                    LeafAssessment(
                        node_id=leaf_node.node_id,
                        question=leaf_node.question,
                        framework=leaf_node.framework.value,
                        path=" -> ".join(chain),
                        criteria=criteria,
                    )
                )
            maturity_path = Path(args.maturity_output)
            write_maturity_csv(maturity_path, leaf_rows)
            print(f"Maturity CSV written: {maturity_path}")

        print(f"Decomposition complete: {output_path}")
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
