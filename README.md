# MedLabs Standard

MedLabs Standard = JSON Schema (`standard/`) + Python SDK (`sdk/python/medlabs_sdk`) для пайплайна:

`ingest -> extract -> normalize -> map -> validate`

SDK остается библиотекой: без agent runtime, planner-ов и orchestration графов.

## Архитектура

- `ingest`: источник (`text` или text-based `PDF`)
- `extract`: `LLMClient.extract_structured(...)`
- `normalize`: числа/диапазоны/units, без падения, с warning-ами
- `map`: канонический payload стандарта `v0.1`
- `validate`: JSON Schema + rule checks

Контракты:

- `LLMClient` — `/Users/stanley/Desktop/Active/medlabs-standard/sdk/python/medlabs_sdk/contracts.py`
- `Tracer` — `/Users/stanley/Desktop/Active/medlabs-standard/sdk/python/medlabs_sdk/contracts.py`

## Провайдеры (разделенные ответственности)

- `OpenAIClient`: только structured generation
- `LangfusePromptProvider`: только загрузка prompt по `name/version`
- `LangfuseTracer`: только tracing spans
- `NoopTracer`: fallback

Совместимость сохранена: `LangfuseOpenAIClient` оставлен как тонкий wrapper, но рекомендован явный composition через отдельные провайдеры.

## Конфиг и `.env`

Для examples используется `pydantic-settings`:

- класс: `/Users/stanley/Desktop/Active/medlabs-standard/sdk/python/medlabs_sdk/config.py`
- порядок источников: `init args -> .env -> process env -> file secrets`

Это означает: `.env` имеет приоритет над системными переменными окружения.

## Quick Start

### 1) Установить зависимости

```bash
uv sync --extra providers --extra dev
```

### 2) Создать `.env`

```bash
cp .env.example .env
```

```dotenv
OPENAI_API_KEY=...
OPENAI_MODEL=gpt-4o-mini

LANGFUSE_PUBLIC_KEY=...
LANGFUSE_SECRET_KEY=...
LANGFUSE_HOST=https://cloud.langfuse.com

MEDLABS_PROMPT_NAME=medlabs.extract
MEDLABS_PROMPT_VERSION=production

MEDLABS_ENABLE_TRACING=true
MEDLABS_LOG_LEVEL=INFO
# optional
# MEDLABS_SAMPLE_PDF=/absolute/path/to/report.pdf
# MEDLABS_SCHEMA_DIR=/absolute/path/to/standard/schema/v0.1
```

### 3) Запустить parse из текста

```bash
uv run --extra providers python examples/parse_text.py --panel CBC
```

### 4) Запустить parse из PDF

```bash
uv run --extra providers python examples/parse_pdf.py --pdf /path/to/report.pdf --panel CBC
```

Если `--pdf` не передан, берется `MEDLABS_SAMPLE_PDF`.

## Как подключить свой LLMClient

Реализуйте интерфейс:

```python
class LLMClient(Protocol):
    def extract_structured(
        self,
        *,
        prompt_name: str,
        prompt_version: str,
        input_text: str,
        output_schema: dict,
        temperature: float = 0.0,
    ) -> dict:
        ...
```

И передайте реализацию в `MedLabsPipeline`.

## Добавление нового анализа

1. Добавьте schema в `standard/schema/v0.1/`.
2. Добавьте mapping правила в `/Users/stanley/Desktop/Active/medlabs-standard/sdk/python/medlabs_sdk/core/map/to_standard.py`.
3. Добавьте unit/integration тесты.
4. Зарегистрируйте panel в валидаторе `/Users/stanley/Desktop/Active/medlabs-standard/sdk/python/medlabs_sdk/core/validate/jsonschema.py`.

## Проверки

```bash
uv run --extra dev ruff check .
uv run --extra dev pytest -q
```

`ruff` — единый стандарт style/lint.
