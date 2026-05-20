#!/usr/bin/env python3
"""Static audit for exported React/Tailwind layout files."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


CLASSNAME_RE = re.compile(r'className\s*=\s*"([^"]+)"')
ABSOLUTE_RE = re.compile(r'(^|\s)absolute(\s|$)')
FIXED_WIDTH_RE = re.compile(r'(^|\s)w-\[[^\]]+\](\s|$)')
FIXED_HEIGHT_RE = re.compile(r'(^|\s)h-\[[^\]]+\](\s|$)')
ANCHOR_RE = re.compile(r'(^|\s)(left|right|top|bottom)-\[[^\]]+\](\s|$)')


@dataclass
class NodeAudit:
    line: int
    tag: str
    classes: str
    category: str
    fixed_width: bool
    fixed_height: bool
    anchors: list[str]


def classify(classes: str, line_text: str) -> str:
    if "home indicator" in line_text.lower() or "status bar" in line_text.lower():
        return "device-chrome"
    if "bg-[url(" in classes and "absolute" in classes:
        return "background"
    if "absolute" not in classes:
        return "normal-flow"
    if "gradient" in classes or "inset-x-0 bottom-0" in classes:
        return "overlay"
    if "flex" in classes or "inline-flex" in classes:
        return "floating-content"
    return "review"


def iter_node_audits(text: str) -> Iterable[NodeAudit]:
    for line_no, line in enumerate(text.splitlines(), start=1):
        match = CLASSNAME_RE.search(line)
        if not match:
            continue
        classes = match.group(1)
        tag_match = re.search(r"<([A-Za-z0-9]+)", line)
        tag = tag_match.group(1) if tag_match else "unknown"
        anchors = [m.group(2) for m in ANCHOR_RE.finditer(classes)]
        yield NodeAudit(
            line=line_no,
            tag=tag,
            classes=classes,
            category=classify(classes, line),
            fixed_width=bool(FIXED_WIDTH_RE.search(classes)),
            fixed_height=bool(FIXED_HEIGHT_RE.search(classes)),
            anchors=anchors,
        )


def build_report(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    nodes = list(iter_node_audits(text))
    absolute_nodes = [n for n in nodes if ABSOLUTE_RE.search(n.classes)]
    summary = {
        "file": str(path),
        "class_nodes": len(nodes),
        "absolute_nodes": len(absolute_nodes),
        "fixed_width_nodes": sum(1 for n in nodes if n.fixed_width),
        "fixed_height_nodes": sum(1 for n in nodes if n.fixed_height),
        "anchor_counts": {
            anchor: sum(n.anchors.count(anchor) for n in nodes)
            for anchor in ("left", "right", "top", "bottom")
        },
    }
    return {
        "summary": summary,
        "absolute_nodes": [asdict(node) for node in absolute_nodes],
    }


def print_markdown(report: dict) -> None:
    summary = report["summary"]
    print(f"# Layout Audit: {summary['file']}")
    print()
    print(f"- class nodes: {summary['class_nodes']}")
    print(f"- absolute nodes: {summary['absolute_nodes']}")
    print(f"- fixed width nodes: {summary['fixed_width_nodes']}")
    print(f"- fixed height nodes: {summary['fixed_height_nodes']}")
    print(
        "- anchor counts: "
        + ", ".join(f"{k}={v}" for k, v in summary["anchor_counts"].items())
    )
    print()
    print("| line | tag | category | anchors | fixed w | fixed h |")
    print("| --- | --- | --- | --- | --- | --- |")
    for node in report["absolute_nodes"]:
        anchors = ",".join(node["anchors"]) if node["anchors"] else "-"
        print(
            f"| {node['line']} | {node['tag']} | {node['category']} | {anchors} | "
            f"{'yes' if node['fixed_width'] else 'no'} | {'yes' if node['fixed_height'] else 'no'} |"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="Path to JSX/TSX file")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of Markdown")
    args = parser.parse_args()

    report = build_report(args.source)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print_markdown(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
