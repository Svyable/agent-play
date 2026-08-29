#!/usr/bin/env python3
"""Regression tests for contribution-graph mechanism audit heuristics."""
from audit_mechanisms import audit


def graph(nodes, edges):
    return {"protocol": "agent-play/0.1", "nodes": nodes, "edges": edges}


def main():
    nodes = [
        {"id": "a", "operator": "operator-a"},
        {"id": "b", "operator": "operator-b"},
    ]
    reciprocal = graph(nodes, [
        {"source": "a", "target": "b", "relation": "builds-on"},
        {"source": "b", "target": "a", "relation": "extends"},
    ])
    result = audit(reciprocal)
    assert any(f["type"] == "reciprocal-credit-risk" for f in result["findings"]), result

    one_way = graph(nodes, [
        {"source": "a", "target": "b", "relation": "builds-on"},
    ])
    result = audit(one_way)
    assert not any(f["type"] == "reciprocal-credit-risk" for f in result["findings"]), result

    malformed = graph(nodes, [
        {"source": "a", "target": "a", "relation": "extends"},
        {"source": "a", "target": "missing", "relation": "builds-on"},
        {"source": "a", "target": "b", "relation": "uses-tool"},
        {"source": "a", "target": "b", "relation": "uses-tool"},
    ])
    types = {f["type"] for f in audit(malformed)["findings"]}
    assert {"self-reference", "orphan-target", "duplicate-edge"}.issubset(types), types

    print("Mechanism-audit regression tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
