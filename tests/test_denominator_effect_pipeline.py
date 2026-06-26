from altintel.core import load_app_config
from altintel.pipeline import run_denominator_effect_pipeline


def test_run_denominator_effect_pipeline_returns_stressed_opportunity_view() -> None:
    result = run_denominator_effect_pipeline(load_app_config(), portfolio_case="balanced_institution")

    assert result.stressed_private_markets_pct > result.baseline_private_markets_pct
    assert result.opportunity_impacts
    assert result.opportunity_impacts[0].stressed_composite_score >= result.opportunity_impacts[-1].stressed_composite_score
