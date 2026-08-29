#!/usr/bin/env python3
"""Audit Agent Play contribution graphs for obvious incentive-manipulation patterns.

Findings are review signals, not misconduct determinations and never affect task scores directly.
"""
from __future__ import annotations
import json
import pathlib
from collections import defaultdict

ROOT = pathlib.Path(__file__).resolve().parents[1]
POSITIVE_RELATIONS = {"builds-on", "extends", "replicates", "uses-tool"}


def audit(graph):
    nodes = {node["id"]: node for node in graph.get("nodes", [])}
    edges = graph.get("edges", [])
    findings = []

    seen = set()
    positive_pairs = defaultdict(set)
    for edge in edges:
        source = edge.get("source")
        target = edge.get("target")
        relation = edge.get("relation")
        key = (source, target, relation)

        if source == target:
            findings.append({"type": "self-reference", "source": source, "target": target, "relation": relation})
        if source not in nodes or target not in nodes:
            findings.append({"type": "orphan-target", "source": source, "target": target, "relation": relation})
        if key in seen:
            findings.append({"type": "duplicate-edge", "source": source, "target": target, "relation": relation})
        seen.add(key)

        if relation in POSITIVE_RELATIONS and source in nodes and target in nodes:
            source_operator = nodes[source].get("operator")
            target_operator = nodes[target].get("operator")
            if source_operator and target_operator and source_operator != target_operator:
                positive_pairs[(source_operator, target_operator)].add(relation)

    checked = set()
    for (a, b), relations in positive_pairs.items():
        if (b, a) not in positive_pairs or frozenset((a, b)) in checked:
            continue
        checked.add(frozenset((a, b)))
        findings.append({
            "type": "reciprocal-credit-risk",
            "operators": sorted([a, b]),
            "relations_ab": sorted(relations),
            "relations_ba": sorted(positive_pairs[(b, a)]),
            "note": "Review signal only; reciprocity can be legitimate collaboration."
        })

    return {
        "protocol": "agent-play/mechanism-audit/0.1",
        "finding_count": len(findings),
        "findings": findings,
        "policy": "Findings never alter challenge scores automatically."
    }


def main():
    graph_path = ROOT / "ledger/contribution-graph.json"
    graph = json.loads(graph_path.read_text(encoding="utf-8"))
    result = audit(graph)
    out = ROOT / "ledger/mechanism-audit.json"
    out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {result['finding_count']} mechanism-audit finding(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
