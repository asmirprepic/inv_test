from altintel.core import load_app_config
from altintel.due_diligence.evaluation import run_extraction_evaluation


def test_run_extraction_evaluation_for_mock_provider() -> None:
    result = run_extraction_evaluation(load_app_config())

    assert result.average_field_accuracy == 1.0
    assert result.average_risk_recall == 1.0
    assert result.average_fact_evidence_coverage == 1.0
    assert result.average_risk_evidence_coverage == 1.0
    assert {case.commitment_case for case in result.cases} >= {"infrastructure", "timberland"}
