from __future__ import annotations

import argparse
import json
from pathlib import Path

from medlabs_sdk import MedLabsPipeline

DEFAULT_TEXT = """
WBC 5,4 x10^9/L (4.0-10.0)
RBC 4.65 x10^12/L (4.2-5.6)
HGB 14.1 g/dL (13.0-17.0)
PLT 250 x10^9/L (150-400)
""".strip()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Parse lab text into MedLabs standard")
    parser.add_argument("--panel", default="CBC", help="Panel code: CBC/BIOCHEM/URINALYSIS")
    parser.add_argument("--input-file", help="Optional text file path")
    return parser.parse_args()


def load_text(input_file: str | None) -> str:
    if input_file:
        return Path(input_file).read_text(encoding="utf-8")
    return DEFAULT_TEXT


def main() -> None:
    args = parse_args()

    pipeline = MedLabsPipeline.from_env()
    result = pipeline.parse_text(
        load_text(args.input_file),
        panel=args.panel,
        document_meta={
            "document_id": "example-text-001",
            "lab_name": "Example Lab",
            "report_date": "2026-02-07",
            "panel_raw_text": args.panel,
        },
    )

    print("=== pipeline_summary ===")
    print(
        json.dumps(
            {
                "source": result.document.source,
                "text_size": len(result.document.text),
                "extracted_fields": len(result.extracted.fields),
                "normalized_observations": len(result.normalized.observations),
                "is_valid": result.validation.is_valid,
                "issue_count": len(result.validation.issues),
            },
            indent=2,
            ensure_ascii=False,
        )
    )
    print("=== mapped_payload ===")
    print(json.dumps(result.mapped.data, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
