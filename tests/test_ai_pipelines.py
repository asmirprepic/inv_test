from altintel.core import load_app_config
from altintel.pipeline import run_ai_evaluation_pipeline, run_ai_extraction_pipeline


def test_run_ai_extraction_pipeline_for_mock_provider() -> None:
    result = run_ai_extraction_pipeline(load_app_config(), commitment_case="infrastructure")

    assert result.validation_passed is True
    assert result.fact_evidence_coverage == 1.0
    assert result.risk_evidence_coverage == 1.0
    assert result.retrieved_sections


def test_run_ai_evaluation_pipeline_for_mock_provider() -> None:
    result = run_ai_evaluation_pipeline(load_app_config())

    assert result.passed is True
    assert result.failed_checks == []
