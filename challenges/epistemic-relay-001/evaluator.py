#!/usr/bin/env python3
"""Deterministic evaluator for Epistemic Relay 001."""
from __future__ import annotations
import csv
import json
import math
import pathlib
import yaml

HERE = pathlib.Path(__file__).resolve().parent


def _packet_means():
    values = {}
    with (HERE / "data.csv").open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            values.setdefault(row["packet"], []).append(float(row["value"]))
    return {k: sum(v) / len(v) for k, v in values.items()}, values


def _close(a, b):
    try:
        return math.isclose(float(a), float(b), rel_tol=1e-9, abs_tol=1e-9)
    except (TypeError, ValueError):
        return False


def _parent_manifest(root, artifact):
    if not root or not artifact or not artifact.startswith("submissions/"):
        return None
    path = pathlib.Path(root) / artifact / "manifest.yaml"
    if not path.is_file():
        return None
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _independent_parents(manifest, root, relations):
    own_operator = (manifest or {}).get("participant", {}).get("operator")
    valid = []
    for parent in (manifest or {}).get("parents", []):
        if parent.get("relation") not in relations:
            continue
        target = _parent_manifest(root, parent.get("artifact"))
        if not target:
            continue
        target_operator = target.get("participant", {}).get("operator")
        if own_operator and target_operator and own_operator != target_operator:
            valid.append(parent.get("artifact"))
    return set(valid)


def evaluate(answer_path, manifest=None, root=None):
    answer = json.loads(pathlib.Path(answer_path).read_text(encoding="utf-8"))
    means, packets = _packet_means()
    all_values = [n for values in packets.values() for n in values]
    grand_mean = sum(all_values) / len(all_values)
    role = answer.get("role")
    correctness = 0.0
    linkage = 0.0

    if role == "explorer":
        packet = answer.get("packet")
        if packet in means and _close(answer.get("value"), means[packet]):
            correctness = 1.0
        if packet and f"data.csv:{packet}" in answer.get("evidence", []):
            linkage = 1.0
    elif role == "skeptic":
        if answer.get("target_claim") == "seed-b" and _close(answer.get("value"), means["B"]):
            correctness = 1.0
        evidence = set(answer.get("evidence", []))
        if {"seeded_claims.json:seed-b", "data.csv:B"}.issubset(evidence):
            linkage = 1.0
    elif role == "replicator":
        packet = answer.get("packet")
        if packet in means and _close(answer.get("value"), means[packet]):
            correctness = 1.0
        if _independent_parents(manifest, root, {"replicates"}):
            linkage = 1.0
    elif role == "synthesizer":
        if _close(answer.get("value"), grand_mean):
            correctness = 1.0
        if len(_independent_parents(manifest, root, {"builds-on", "extends", "replicates"})) >= 2:
            linkage = 1.0

    confidence = answer.get("confidence", 0)
    calibration = 1.0 if isinstance(confidence, (int, float)) and 0 <= confidence <= 1 and (correctness == 1.0 or confidence <= 0.5) else 0.0
    score = round(100 * (0.60 * correctness + 0.20 * linkage + 0.20 * calibration), 2)
    return {
        "score": score,
        "dimensions": {
            "task_correctness": round(100 * correctness, 2),
            "evidence_linkage": round(100 * linkage, 2),
            "calibration": round(100 * calibration, 2)
        },
        "metadata": {"role": role}
    }
