# MedLabs Standard

`MedLabs Standard` объединяет:
- `standard/` — открытый JSON-стандарт лабораторных панелей
- `sdk/python/medlabs_sdk/` — Python SDK для детерминированного пайплайна

Пайплайн SDK: `ingest -> extract -> normalize -> map -> validate`.

## Миссия

- Стандарт: привести результаты лабораторных отчетов к единому, машинно-читабельному JSON-контракту.
- Библиотека: дать простой и воспроизводимый способ получить этот контракт из текста/PDF, независимо от конкретного LLM-провайдера.

## Quick Start

### 1) Установка

Для работы из репозитория:

```bash
uv sync --extra providers --extra dev
```

После публикации в PyPI:

```bash
pip install "medlabs-standard[providers]"
```

### 2) Настройка переменных окружения

```bash
cp .env.example .env
```

Минимально нужны:
- `OPENAI_API_KEY`
- `OPENAI_MODEL` (можно оставить дефолт)

Опционально:
- `MEDLABS_SAMPLE_PDF` для `examples/parse_pdf.py`

`MedLabsPipeline()` автоматически читает переменные из окружения процесса и `.env/.env.local` по всей иерархии директорий (ближайший к текущей директории файл имеет приоритет).

### 3) Запуск examples

```bash
uv run --extra dev python examples/validate_standard_fixtures.py
uv run --extra dev python examples/pipeline_with_mock_llm.py
uv run --extra providers python examples/parse_text.py --panel CBC
uv run --extra providers python examples/parse_pdf.py --panel CBC
```

### 4) Минимальный код

```python
from medlabs_sdk import MedLabsPipeline

pipeline = MedLabsPipeline()
result = pipeline.parse_text("WBC 5,4 x10^9/L (4.0-10.0)", panel="CBC")
print(result.validation.is_valid, len(result.validation.issues))
```

Детали примеров: `examples/README.md`.
Flow пайплайна: `docs/flow.md`.

## Проверка качества

```bash
uv run --extra dev ruff check .
uv run --extra dev pytest -q
```
