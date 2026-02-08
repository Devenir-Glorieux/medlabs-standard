from __future__ import annotations

import json
from pathlib import Path

from medlabs_sdk.core.validate import validate_jsonschema


def iter_fixture_paths() -> list[Path]:
    root = Path(__file__).resolve().parents[1] / "standard" / "examples" / "v0.1"
    return sorted(root.glob("**/*.json"))


def main() -> None:
    fixture_paths = iter_fixture_paths()
    if not fixture_paths:
        raise RuntimeError("No standard fixtures found")

    failures = 0
    for path in fixture_paths:
        payload = json.loads(path.read_text(encoding="utf-8"))
        panel_code = payload.get("panel_code", {}).get("code")
        result = validate_jsonschema(payload, panel_code=panel_code)

        status = "OK" if result.is_valid else "FAIL"
        print(f"[{status}] {path}")

        if not result.is_valid:
            failures += 1
            for issue in result.issues:
                print(f"  - {issue.severity} {issue.path}: {issue.description}")

    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
