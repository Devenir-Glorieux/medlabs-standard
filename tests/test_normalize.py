from medlabs_sdk.core.models import ExtractedField, ExtractedReport, RawDocument
from medlabs_sdk.core.normalize import normalize


def test_normalize_parses_commas_and_ranges() -> None:
    report = ExtractedReport(
        document=RawDocument(text="dummy"),
        fields=[
            ExtractedField(
                name_raw="WBC",
                value_raw="5,4",
                unit_raw="x10^9/L",
                ref_raw="4,0-10,0",
                confidence=0.9,
            )
        ],
    )

    result = normalize(report)

    assert len(result.observations) == 1
    observation = result.observations[0]
    assert observation.code == "wbc"
    assert observation.value == 5.4
    assert observation.unit == "10*9/L"
    assert observation.ref_low == 4.0
    assert observation.ref_high == 10.0


def test_normalize_adds_warning_for_unparsed_reference() -> None:
    report = ExtractedReport(
        document=RawDocument(text="dummy"),
        fields=[
            ExtractedField(
                name_raw="Glucose",
                value_raw="4.9",
                unit_raw="mmol/L",
                ref_raw="> 3.9",
            )
        ],
    )

    result = normalize(report)

    assert result.observations[0].value == 4.9
    assert result.warnings
    assert "unparsed reference range" in result.warnings[0]
