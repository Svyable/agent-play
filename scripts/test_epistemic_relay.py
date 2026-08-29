#!/usr/bin/env python3
from __future__ import annotations
import importlib.util
import pathlib
import tempfile

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
CHALLENGE = ROOT / "challenges/epistemic-relay-001"
EXAMPLES = ROOT / "examples/epistemic-relay-001"


def load_evaluator():
    spec = importlib.util.spec_from_file_location("epistemic_relay", CHALLENGE / "evaluator.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module


def write_manifest(root, artifact, operator):
    path = root / artifact
    path.mkdir(parents=True, exist_ok=True)
    manifest = {
        "participant": {"type": "agent", "id": operator.lower(), "operator": operator}
    }
    (path / "manifest.yaml").write_text(yaml.safe_dump(manifest), encoding="utf-8")


def main():
    evaluator = load_evaluator()
    assert evaluator.evaluate(EXAMPLES / "explorer/answer.json")["score"] == 100.0
    assert evaluator.evaluate(EXAMPLES / "skeptic/answer.json")["score"] == 100.0

    with tempfile.TemporaryDirectory() as tmp:
        root = pathlib.Path(tmp)
        parent_a = "submissions/epistemic-relay-001/agent-a/run-001"
        parent_b = "submissions/epistemic-relay-001/agent-b/run-001"
        write_manifest(root, parent_a, "operator-a")
        write_manifest(root, parent_b, "operator-b")

        replicator_manifest = {
            "participant": {"type": "agent", "id": "rep", "operator": "operator-c"},
            "parents": [{"artifact": parent_a, "relation": "replicates"}],
        }
        result = evaluator.evaluate(EXAMPLES / "replicator/answer.json", manifest=replicator_manifest, root=root)
        assert result["score"] == 100.0, result

        self_replication = {
            "participant": {"type": "agent", "id": "rep", "operator": "operator-a"},
            "parents": [{"artifact": parent_a, "relation": "replicates"}],
        }
        result = evaluator.evaluate(EXAMPLES / "replicator/answer.json", manifest=self_replication, root=root)
        assert result["score"] == 80.0, result

        synthesis_manifest = {
            "participant": {"type": "human-agent", "id": "synth", "operator": "operator-c"},
            "parents": [
                {"artifact": parent_a, "relation": "builds-on"},
                {"artifact": parent_b, "relation": "builds-on"},
            ],
        }
        result = evaluator.evaluate(EXAMPLES / "synthesizer/answer.json", manifest=synthesis_manifest, root=root)
        assert result["score"] == 100.0, result

    print("Epistemic Relay role and independence tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
