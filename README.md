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

### 1) Установка

Для разработки из репозитория:

```bash
uv sync --extra providers --extra dev
```

После публикации в PyPI:

```bash
pip install "medlabs-standard[providers]"
```

### 2) Настройка окружения

```bash
cp .env.example .env
```

Минимально нужны:
- `OPENAI_API_KEY`
- `OPENAI_MODEL` (или оставить дефолт)
- `MEDLABS_SAMPLE_PDF` (если хотите запускать `examples/parse_pdf.py` без `--pdf`)

### 3) Минимальный запуск SDK

```python
from medlabs_sdk import MedLabsPipeline

pipeline = MedLabsPipeline.from_env()
result = pipeline.parse_text(
    "WBC 5,4 x10^9/L (4.0-10.0)",
    panel="CBC",
    document_meta={"document_id": "quickstart-1", "lab_name": "Example Lab"},
)
print(result.validation.is_valid, len(result.validation.issues))
```

### 4) Запуск примеров

```bash
uv run --extra dev python examples/validate_standard_fixtures.py
uv run --extra dev python examples/pipeline_with_mock_llm.py
uv run --extra providers python examples/parse_text.py --panel CBC
uv run --extra providers python examples/parse_pdf.py --panel CBC
```

Подробные сценарии: `examples/README.md`.
Документация по flow: `docs/flow.md`.

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
