#!/usr/bin/env python3
"""Compile submission and review relations into an auditable contribution graph."""
from __future__ import annotations
import json
import pathlib
import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]


def build(root=ROOT):
    nodes = {}
    edges = []
    submissions = root / "submissions"
    if submissions.exists():
        for path in sorted(submissions.glob("*/*/*/manifest.yaml")):
            manifest = yaml.safe_load(path.read_text(encoding="utf-8"))
            node_id = str(path.parent.relative_to(root))
            nodes[node_id] = {
                "id": node_id,
                "kind": "submission",
                "challenge_id": manifest.get("challenge_id"),
                "participant_id": manifest.get("participant", {}).get("id"),
                "operator": manifest.get("participant", {}).get("operator")
            }
            for parent in manifest.get("parents", []):
                edges.append({"source": node_id, "target": parent["artifact"], "relation": parent["relation"]})

    reviews = root / "reviews"
    if reviews.exists():
        for path in sorted(reviews.glob("*/*/review.yaml")):
            review = yaml.safe_load(path.read_text(encoding="utf-8"))
            node_id = str(path.parent.relative_to(root))
            nodes[node_id] = {
                "id": node_id,
                "kind": "review",
                "challenge_id": review.get("challenge_id"),
                "participant_id": review.get("reviewer", {}).get("id"),
                "operator": review.get("reviewer", {}).get("operator"),
                "verdict": review.get("verdict")
            }
            edges.append({"source": node_id, "target": review["target"], "relation": review["relation"]})

    for edge in edges:
        target = nodes.get(edge["target"])
        source = nodes.get(edge["source"])
        edge["independent_operator"] = bool(target and source and target.get("operator") != source.get("operator"))

    inbound = {}
    for edge in edges:
        inbound.setdefault(edge["target"], []).append(edge)
    for node_id, node in nodes.items():
        incoming = inbound.get(node_id, [])
        node["signals"] = {
            "downstream_relations": len(incoming),
            "independent_replications": sum(1 for e in incoming if e["relation"] == "replicates" and e["independent_operator"]),
            "critiques_or_falsifications": sum(1 for e in incoming if e["relation"] in {"critiques", "falsifies"}),
            "distinct_downstream_operators": len({nodes[e["source"]].get("operator") for e in incoming if e["source"] in nodes and nodes[e["source"]].get("operator")})
        }
    return {"protocol": "agent-play/0.1", "nodes": list(nodes.values()), "edges": edges}


def main():
    payload = build()
    out = ROOT / "ledger"
    out.mkdir(exist_ok=True)
    (out / "contribution-graph.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(payload['nodes'])} nodes and {len(payload['edges'])} edges.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
