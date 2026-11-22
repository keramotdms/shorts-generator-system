#!/usr/bin/env python3
"""Tiny stdlib JSON Schema validator for the six project schemas.

Supports: type, required, properties, items, enum, minLength, minimum,
maximum, minItems, maxItems and pattern. No external packages.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
SCHEMAS = ROOT / "config" / "schemas"

TYPE_CHECKS = {
    "object": lambda value: isinstance(value, dict),
    "array": lambda value: isinstance(value, list),
    "string": lambda value: isinstance(value, str),
    "number": lambda value: isinstance(value, (int, float)) and not isinstance(value, bool),
    "integer": lambda value: isinstance(value, int) and not isinstance(value, bool),
    "boolean": lambda value: isinstance(value, bool),
    "null": lambda value: value is None,
}


class ValidationError(ValueError):
    pass


def _type_ok(value: Any, expected: Any) -> bool:
    names = [expected] if isinstance(expected, str) else list(expected)
    return any(TYPE_CHECKS.get(name, lambda _v: True)(value) for name in names)


def validate(instance: Any, schema: dict[str, Any], path: str = "$") -> list[str]:
    errors: list[str] = []

    expected = schema.get("type")
    if expected is not None and not _type_ok(instance, expected):
        return [f"{path}: expected type {expected}, got {type(instance).__name__}"]

    if "enum" in schema and instance not in schema["enum"]:
        errors.append(f"{path}: value {instance!r} not in {schema['enum']}")

    if isinstance(instance, str):
        if "minLength" in schema and len(instance) < schema["minLength"]:
            errors.append(f"{path}: shorter than minLength {schema['minLength']}")
        if "pattern" in schema and not re.search(schema["pattern"], instance):
            errors.append(f"{path}: does not match pattern {schema['pattern']}")

    if isinstance(instance, (int, float)) and not isinstance(instance, bool):
        if "minimum" in schema and instance < schema["minimum"]:
            errors.append(f"{path}: below minimum {schema['minimum']}")
        if "maximum" in schema and instance > schema["maximum"]:
            errors.append(f"{path}: above maximum {schema['maximum']}")

    if isinstance(instance, list):
        if "minItems" in schema and len(instance) < schema["minItems"]:
            errors.append(f"{path}: fewer than minItems {schema['minItems']}")
        if "maxItems" in schema and len(instance) > schema["maxItems"]:
            errors.append(f"{path}: more than maxItems {schema['maxItems']}")
        if "items" in schema:
            for index, item in enumerate(instance):
                errors += validate(item, schema["items"], f"{path}[{index}]")

    if isinstance(instance, dict):
        for key in schema.get("required", []):
            if key not in instance:
                errors.append(f"{path}: missing required field '{key}'")
        for key, sub_schema in schema.get("properties", {}).items():
            if key in instance:
                errors += validate(instance[key], sub_schema, f"{path}.{key}")
    return errors


def load_schema(name: str) -> dict[str, Any]:
    path = SCHEMAS / f"{name}.json"
    if not path.is_file():
        raise ValidationError(f"Unknown schema: {name} ({path})")
    return json.loads(path.read_text(encoding="utf-8"))


def validate_file(schema_name: str, file_path: Path) -> list[str]:
    if not file_path.is_file():
        return [f"missing input file: {file_path}"]
    try:
        data = json.loads(file_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"invalid JSON in {file_path}: {exc}"]
    return validate(data, load_schema(schema_name))


def main() -> int:
    if len(sys.argv) != 3:
        print("Usage: python scripts/schema_validator.py <schema-name> <file.json>")
        return 2
    schema_name, target = sys.argv[1], sys.argv[2]
    errors = validate_file(schema_name, Path(target))
    if errors:
        print(f"FAIL {schema_name} <- {target}")
        for error in errors:
            print(" - " + error)
        return 1
    print(f"PASS {schema_name} <- {target}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
