# Examples

Цель примеров: показать максимально простой usage SDK.

Базовый сценарий в коде:

```python
from medlabs_sdk import MedLabsPipeline

pipeline = MedLabsPipeline.from_env()
result = pipeline.parse_text(...)
```

## Подготовка

```bash
uv sync --extra providers --extra dev
cp .env.example .env
```

## 1) Валидация golden fixtures стандарта

Без LLM, только standard + JSON Schema:

```bash
uv run --extra dev python examples/validate_standard_fixtures.py
```

## 2) Pipeline с mock LLM

Без внешних API:

```bash
uv run --extra dev python examples/pipeline_with_mock_llm.py
```

## 3) Parse text (реальные провайдеры)

```bash
uv run --extra providers python examples/parse_text.py --panel CBC
```

С input-файлом:

```bash
uv run --extra providers python examples/parse_text.py --panel CBC --input-file /path/to/input.txt
```

## 4) Parse PDF (реальные провайдеры)

```bash
uv run --extra providers python examples/parse_pdf.py --panel CBC --pdf /path/to/report.pdf
```

## Что выводится в консоль

Каждый пример печатает два блока:

1. `pipeline_summary` — краткая сводка шагов:
- размер текста
- сколько полей извлечено
- сколько наблюдений нормализовано
- `is_valid` и `issue_count`

2. `mapped_payload` — итоговый JSON после `normalize + map`.

Важно: `PipelineResult` содержит больше данных (`document`, `extracted`, `normalized`, `mapped`, `validation`),
но в examples мы печатаем только полезный минимум по умолчанию.

## Смена LLM-провайдера

Используется OpenAI-compatible transport + `OPENAI_BASE_URL`:
- OpenAI: не указывать `OPENAI_BASE_URL`
- OpenRouter: `OPENAI_BASE_URL=https://openrouter.ai/api/v1`
- другой совместимый endpoint: укажите свой `OPENAI_BASE_URL`

## Флаги prompt/tracing через env

- `MEDLABS_ENABLE_LANGFUSE_PROMPTS=true|false`
- `MEDLABS_ENABLE_TRACING=true|false`
- `MEDLABS_FAIL_ON_PROMPT_ERROR=true|false`
- `MEDLABS_PROMPT_FALLBACK=...`
