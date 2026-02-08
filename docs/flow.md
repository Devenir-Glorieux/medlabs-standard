# Pipeline Flow

## Что значат поля в выводе

- `is_valid`: итог валидации `mapped` payload против JSON Schema + rule checks.
  - `true` = нет `severity=error`
  - `false` = есть хотя бы одна ошибка
- `issue_count`: количество всех `issues` (ошибки и предупреждения).

## Что делает `_run_processing_workflow`

`_run_processing_workflow` в `/Users/stanley/Desktop/Active/medlabs-standard/sdk/python/medlabs_sdk/pipeline.py` выполняет workflow-граф после ingest.

Сейчас граф задан как `nodes + edges`:
- nodes: `extract`, `normalize`, `map`, `validate`
- edges: `extract -> normalize -> map -> validate`

Сейчас шаги выполняются через явный `PipelineState`:
- `state.document`
- `state.extracted`
- `state.normalized`
- `state.mapped`
- `state.validation`

И в конце строится `PipelineResult` c артефактами каждого шага:
- `document`
- `extracted`
- `normalized`
- `mapped`
- `validation`

## Текущий flow (sequence)

Диаграмма хранится в формате PlantUML:

- `/Users/stanley/Desktop/Active/medlabs-standard/docs/flow.puml`

## Важный момент про "extract as-is"

Да, сейчас extract intentionally черновой:
- LLM возвращает сырой промежуточный слой (`name_raw`, `value_raw`, `unit_raw`, `ref_raw`)
- канонизация происходит дальше в `normalize + map`

Это сделано, чтобы:
- держать SDK детерминированным на этапе стандартизации
- не завязывать финальный формат стандарта на поведение конкретной модели

## Что это дает разработчику

- Переиспользуемый core-пайплайн (ingest/normalize/map/validate)
- Прозрачную диагностику по шагам (`structlog`)
- Плаггабельные провайдеры (LLM / prompt storage / tracing)
- Единый контракт результата (`PipelineResult`) для приложения
