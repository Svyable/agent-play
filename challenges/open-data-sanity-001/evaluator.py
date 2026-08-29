"""Trusted deterministic evaluator for open-data-sanity-001.

This evaluator reads static submission artifacts only. It never executes participant code.
"""
from __future__ import annotations
import csv
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent


def ground_truth():
    rows = []
    with (HERE / "data.csv").open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            rows.append((row["reading_id"], float(row["pm25_ug_m3"])))
    values = sorted(v for _, v in rows)
    median = (values[5] + values[6]) / 2
    suspicious = max(rows, key=lambda item: abs(item[1] - median))[0]
    kept = [v for rid, v in rows if rid != suspicious]
    return suspicious, sum(kept) / len(kept)


def evaluate(answer_path):
    with pathlib.Path(answer_path).open(encoding="utf-8") as f:
        answer = json.load(f)
    suspicious, corrected_mean = ground_truth()
    anomaly_ok = answer.get("suspicious_reading_id") == suspicious
    reported = answer.get("corrected_mean_pm25")
    mean_ok = isinstance(reported, (int, float)) and abs(reported - corrected_mean) <= 0.01
    evidence_ok = isinstance(answer.get("evidence"), list) and len(answer["evidence"]) >= 1
    confidence = answer.get("confidence")
    calibration_ok = isinstance(confidence, (int, float)) and 0 <= confidence <= 1
    dimensions = {
        "correctness": 70 if anomaly_ok and mean_ok else 35 if anomaly_ok or mean_ok else 0,
        "evidence": 10 if evidence_ok else 0,
        "reproducibility": 10 if answer.get("method_reproducible") is True else 0,
        "calibration": 10 if calibration_ok else 0,
    }
    return {"score": sum(dimensions.values()), "dimensions": dimensions, "expected": {"suspicious_reading_id": suspicious, "corrected_mean_pm25": round(corrected_mean, 4)}}
