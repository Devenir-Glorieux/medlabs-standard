from medlabs_sdk.core.map import to_standard_panel
from medlabs_sdk.core.models import NormalizedObservation, NormalizedReport, RawDocument


def test_map_creates_canonical_panel_payload() -> None:
    report = NormalizedReport(
        document=RawDocument(
            text="dummy",
            meta={
                "document_id": "doc-1",
                "lab_name": "Unit Test Lab",
                "report_date": "2026-02-07",
                "collected_at": "2026-02-07T08:00:00Z",
                "reported_at": "2026-02-07T10:00:00Z",
            },
        ),
        observations=[
            NormalizedObservation(
                code="wbc",
                value=5.4,
                unit="10*9/L",
                ref_low=4.0,
                ref_high=10.0,
                source_name="WBC",
            )
        ],
    )

    panel = to_standard_panel(report, panel="CBC")

    assert panel.data["resource_type"] == "panel"
    assert panel.data["standard_version"] == "0.1"
    assert panel.data["panel_code"]["code"] == "CBC"
    assert panel.data["panel_name"] == "Complete Blood Count"
    assert len(panel.data["observations"]) == 1

    observation = panel.data["observations"][0]
    assert observation["resource_type"] == "observation"
    assert observation["code"]["code"] == "6690-2"
    assert observation["value"]["unit_code"] == "10*9/L"
    assert observation["source"]["document_id"] == "doc-1"
