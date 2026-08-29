#!/usr/bin/env python3
"""Validate Agent Play challenge and submission manifests without executing participant code."""
from __future__ import annotations
import json
import pathlib

import yaml
from jsonschema import Draft202012Validator, FormatChecker

ROOT = pathlib.Path(__file__).resolve().parents[1]


class ManifestLoader(yaml.SafeLoader):
    """Safe YAML loader that keeps timestamps as strings for JSON Schema."""


ManifestLoader.yaml_implicit_resolvers = {
    key: [entry for entry in entries if entry[0] != "tag:yaml.org,2002:timestamp"]
    for key, entries in yaml.SafeLoader.yaml_implicit_resolvers.items()
}


def load_json(path: pathlib.Path):
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def load_yaml(path: pathlib.Path):
    with path.open(encoding="utf-8") as f:
        return yaml.load(f, Loader=ManifestLoader)


def validate(instance, schema, label):
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(instance), key=lambda e: list(e.absolute_path))
    for error in errors:
        loc = ".".join(str(x) for x in error.absolute_path) or "<root>"
        print(f"ERROR {label}:{loc}: {error.message}")
    return len(errors)


def main() -> int:
    challenge_schema = load_json(ROOT / "schemas/challenge.schema.json")
    submission_schema = load_json(ROOT / "schemas/submission.schema.json")
    failures = 0

    for path in sorted((ROOT / "challenges").glob("*/challenge.yaml")):
        failures += validate(load_yaml(path), challenge_schema, str(path.relative_to(ROOT)))

    submissions = ROOT / "submissions"
    if submissions.exists():
        for path in sorted(submissions.glob("*/*/*/manifest.yaml")):
            manifest = load_yaml(path)
            failures += validate(manifest, submission_schema, str(path.relative_to(ROOT)))
            base = path.parent
            for key in ("answer", "method"):
                relative = manifest.get("artifacts", {}).get(key)
                if relative and not (base / relative).is_file():
                    print(f"ERROR {path.relative_to(ROOT)}: missing artifact {relative}")
                    failures += 1

    if failures:
        print(f"Validation failed with {failures} error(s).")
        return 1
    print("Agent Play manifests valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
