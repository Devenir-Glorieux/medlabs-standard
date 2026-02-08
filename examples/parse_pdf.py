import argparse
import json
from pathlib import Path

from medlabs_sdk import MedLabsPipeline, get_logger
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = get_logger()

class ExampleCliSettings(BaseSettings):
    sample_pdf: str | None = Field(default=None, alias="MEDLABS_SAMPLE_PDF")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )


def default_pdf_path() -> str | None:
    try:
        return ExampleCliSettings().sample_pdf
    except Exception:
        return None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Parse PDF lab report into MedLabs standard")
    parser.add_argument(
        "--pdf",
        default=default_pdf_path(),
        help="PDF path (or set MEDLABS_SAMPLE_PDF)",
    )
    parser.add_argument("--panel", default="CBC", help="Panel code: CBC/BIOCHEM/URINALYSIS")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if not args.pdf:
        raise RuntimeError("Pass --pdf path or set MEDLABS_SAMPLE_PDF")

    pdf_path = Path(args.pdf)
    if not pdf_path.is_absolute() and args.pdf.startswith("Users/"):
        pdf_path = Path("/") / pdf_path
    if not pdf_path.exists():
        raise RuntimeError(f"PDF file not found: {pdf_path}")

    pipeline = MedLabsPipeline.from_env()
    result = pipeline.parse_pdf(
        str(pdf_path),
        panel=args.panel,
        document_meta={
            "document_id": f"example-pdf-{pdf_path.stem}",
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
                "pages": len(result.document.pages),
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
