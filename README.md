# MedLabs Standard

Machine-readable стандарт для лабораторных данных + SDK, который превращает PDF/сканы анализов в структурированные данные для AI и сервисов здоровья.

## Что внутри
- `standard/` — JSON Schema v0.1 и golden examples.
- `sdk/python/medlabs_sdk/` — Python SDK с пайплайном ingest → extract → normalize → map → validate.

## Цели v0.1
- единая каноническая форма лабораторных панелей и наблюдений;
- трассируемость к первоисточнику;
- нормализация единиц измерения.

## Статус
Каркас готов; часть модулей пока заглушки (ingest/pdf, extract, validate/jsonschema).

## License
MIT
