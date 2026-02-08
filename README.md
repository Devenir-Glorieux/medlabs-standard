# MedLabs Standard

`MedLabs Standard` = JSON Schema (`standard/`) + Python SDK (`sdk/python/medlabs_sdk`) для пайплайна:

`ingest -> extract -> normalize -> map -> validate`

Философия: SDK берет на себя воспроизводимую часть (контракты, нормализация, маппинг, валидация и наблюдаемость), а LLM/prompt storage остаются подключаемыми провайдерами.

Минимальный код для приложения:

```python
from medlabs_sdk import MedLabsPipeline

pipeline = MedLabsPipeline.from_env()
result = pipeline.parse_pdf("/path/to/report.pdf", panel="CBC")
```

## Что внутри

- `standard/` — схемы стандарта и golden fixtures
- `sdk/python/medlabs_sdk/` — SDK (контракты, pipeline, normalize/map/validate)
- `examples/` — практичные примеры использования SDK и стандарта

## Quick Start

```bash
uv sync --extra providers --extra dev
cp .env.example .env
```

После заполнения `.env` запустите любой пример:

```bash
uv run --extra dev python examples/validate_standard_fixtures.py
uv run --extra dev python examples/pipeline_with_mock_llm.py
uv run --extra providers python examples/parse_text.py --panel CBC
uv run --extra providers python examples/parse_pdf.py --panel CBC --pdf /path/to/report.pdf
```

Подробные инструкции по всем сценариям: `examples/README.md`.
Документация по внутреннему flow: `docs/flow.md`.

Поддерживаются env-флаги:
- `MEDLABS_ENABLE_LANGFUSE_PROMPTS` — включить/выключить загрузку prompt из Langfuse
- `MEDLABS_ENABLE_TRACING` — включить/выключить tracing
- `MEDLABS_FAIL_ON_PROMPT_ERROR` — падать при ошибке prompt provider или использовать fallback prompt
- `OPENAI_BASE_URL` — OpenAI-compatible endpoint (например OpenRouter)

## Качество

```bash
uv run --extra dev ruff check .
uv run --extra dev pytest -q
```
