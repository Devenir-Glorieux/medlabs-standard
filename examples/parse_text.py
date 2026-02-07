from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

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
    if not input_file:
        return DEFAULT_TEXT
    return Path(input_file).read_text(encoding="utf-8")


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
