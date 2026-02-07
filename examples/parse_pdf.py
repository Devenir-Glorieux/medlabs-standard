from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Parse PDF lab report into MedLabs standard")
    parser.add_argument("--pdf", help="PDF path")
    parser.add_argument("--panel", default="CBC", help="Panel code: CBC/BIOCHEM/URINALYSIS")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    project_root = Path(__file__).resolve().parents[1]
    sdk_root = project_root / "sdk" / "python"
    if str(sdk_root) not in sys.path:
        sys.path.insert(0, str(sdk_root))

    from medlabs_sdk.config import MedLabsSettings
    from medlabs_sdk.pipeline import MedLabsPipeline
    from medlabs_sdk.providers import (
        LangfusePromptProvider,
        LangfuseTracer,
        NoopTracer,
        OpenAIClient,
    )

    settings = MedLabsSettings()

    pdf_path_value = args.pdf or settings.sample_pdf
    if not pdf_path_value:
        raise RuntimeError("Pass --pdf path or set MEDLABS_SAMPLE_PDF")

    pdf_path = Path(pdf_path_value)
    if not pdf_path.exists():
        raise RuntimeError(f"PDF file not found: {pdf_path}")

    prompt_provider = LangfusePromptProvider(
        public_key=settings.langfuse_public_key,
        secret_key=settings.langfuse_secret_key,
        host=settings.langfuse_host,
    )
    llm_client = OpenAIClient(
        model=settings.openai_model,
        api_key=settings.openai_api_key,
        prompt_provider=prompt_provider,
    )

    tracer = (
        LangfuseTracer(
            public_key=settings.langfuse_public_key,
            secret_key=settings.langfuse_secret_key,
            host=settings.langfuse_host,
        )
        if settings.enable_tracing
        else NoopTracer()
    )

    pipeline = MedLabsPipeline(
        llm_client=llm_client,
        prompt_name=settings.prompt_name,
        prompt_version=settings.prompt_version,
        tracer=tracer,
        schema_dir=settings.schema_dir_path(),
        log_level=settings.log_level,
    )

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

    print(json.dumps(result.mapped.data, indent=2, ensure_ascii=False))
    print(
        json.dumps(
            {
                "is_valid": result.validation.is_valid,
                "issue_count": len(result.validation.issues),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
