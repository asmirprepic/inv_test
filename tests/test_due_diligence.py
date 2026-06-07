from altintel.core import load_app_config
from altintel.data.sample_data import load_proposed_commitment
from altintel.due_diligence.service import run_due_diligence


def test_run_due_diligence_extracts_expected_facts() -> None:
    config = load_app_config()
    memo = load_proposed_commitment()

    report = run_due_diligence(memo, config)

    assert report.facts.target_size_mn == 1200.0
    assert report.facts.gp_commitment_pct == 2.5
    assert report.facts.management_fee_pct == 1.5
    assert report.facts.carry_pct == 20.0
    assert report.facts.term_years == 12
    assert report.overall_risk_rating == "medium"
    assert len(report.risks) == 4
