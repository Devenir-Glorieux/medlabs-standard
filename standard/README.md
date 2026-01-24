# MedLabs Standard v0.1

## Scope v0.1
- Laboratory panels and observations extracted from PDF/scan lab reports into a canonical, machine-readable JSON format.
- Coverage is limited to panel-level containers and their contained observations with normalized units and traceability.
- Examples in `standard/examples/v0.1/` act as golden fixtures for future testing.

## Principles
- Machine-readable: consistent JSON shapes with explicit typing and stable field names.
- Source traceability: every panel and observation carries a trace back to the originating document and raw text.
- Unit normalization: quantitative values use UCUM units for consistent downstream analytics.

## Out of scope (v0.1)
- Diagnoses or clinical interpretations beyond basic lab flags.
- Recommendations, care plans, or treatment guidance.
- Full EHR structures or longitudinal patient records.
- Medications, prescriptions, or dispensing data.
