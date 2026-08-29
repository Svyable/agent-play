#!/usr/bin/env python3
"""Deterministic evaluator for Epistemic Relay 001."""
from __future__ import annotations
import csv
import json
import math
import pathlib

HERE = pathlib.Path(__file__).resolve().parent


def _packet_means():
    values = {}
    with (HERE / "data.csv").open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            values.setdefault(row["packet"], []).append(float(row["value"]))
    return {k: sum(v) / len(v) for k, v in values.items()}, values


def _close(a, b):
    return math.isclose(float(a), float(b), rel_tol=1e-9, abs_tol=1e-9)


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
        if f"data.csv:{packet}" in answer.get("evidence", []):
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
        parents = (manifest or {}).get("parents", [])
        if any(p.get("relation") == "replicates" for p in parents):
            linkage = 1.0
    elif role == "synthesizer":
        if _close(answer.get("value"), grand_mean):
            correctness = 1.0
        parents = (manifest or {}).get("parents", [])
        distinct = {p.get("artifact") for p in parents if p.get("relation") in {"builds-on", "extends", "replicates"}}
        if len(distinct) >= 2:
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
        }
    }
