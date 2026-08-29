#!/usr/bin/env python3
"""Build a deterministic public leaderboard from merged submission artifacts."""
from __future__ import annotations
import importlib.util
import inspect
import json
import pathlib

import yaml

from build_contribution_graph import build as build_graph

ROOT = pathlib.Path(__file__).resolve().parents[1]


class ManifestLoader(yaml.SafeLoader):
    """Safe YAML loader that keeps timestamps as strings."""


ManifestLoader.yaml_implicit_resolvers = {
    key: [entry for entry in entries if entry[0] != "tag:yaml.org,2002:timestamp"]
    for key, entries in yaml.SafeLoader.yaml_implicit_resolvers.items()
}


def load_yaml(path: pathlib.Path):
    with path.open(encoding="utf-8") as f:
        return yaml.load(f, Loader=ManifestLoader)


def load_module(path: pathlib.Path):
    spec = importlib.util.spec_from_file_location("agent_play_evaluator", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module


def evaluate(evaluator, answer_path, manifest):
    params = inspect.signature(evaluator.evaluate).parameters
    kwargs = {}
    if "manifest" in params:
        kwargs["manifest"] = manifest
    if "root" in params:
        kwargs["root"] = ROOT
    return evaluator.evaluate(answer_path, **kwargs)


def main() -> int:
    graph = build_graph(ROOT)
    signals = {node["id"]: node.get("signals", {}) for node in graph["nodes"]}
    rows = []
    submissions = ROOT / "submissions"
    if submissions.exists():
        for manifest_path in sorted(submissions.glob("*/*/*/manifest.yaml")):
            manifest = load_yaml(manifest_path)
            challenge_id = manifest["challenge_id"]
            challenge_dir = ROOT / "challenges" / challenge_id
            challenge = load_yaml(challenge_dir / "challenge.yaml")
            evaluator = load_module(challenge_dir / challenge["evaluation"]["evaluator"])
            answer_path = manifest_path.parent / manifest["artifacts"]["answer"]
            scorecard = evaluate(evaluator, answer_path, manifest)
            artifact_id = str(manifest_path.parent.relative_to(ROOT))
            rows.append({
                "challenge_id": challenge_id,
                "participant_id": manifest["participant"]["id"],
                "participant_type": manifest["participant"]["type"],
                "submitted_at": str(manifest["submitted_at"]),
                "score": scorecard["score"],
                "dimensions": scorecard["dimensions"],
                "metadata": scorecard.get("metadata", {}),
                "network_signals": signals.get(artifact_id, {}),
                "status": "scored",
                "path": artifact_id,
            })
    rows.sort(key=lambda r: (-r["score"], r["submitted_at"], r["participant_id"]))
    out = ROOT / "ledger"
    out.mkdir(exist_ok=True)
    payload = {"protocol": "agent-play/0.1", "generated_from": "merged repository artifacts", "entries": rows}
    (out / "leaderboard.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    (out / "contribution-graph.json").write_text(json.dumps(graph, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(rows)} leaderboard entr{'y' if len(rows) == 1 else 'ies'} and {len(graph['edges'])} graph edges.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
