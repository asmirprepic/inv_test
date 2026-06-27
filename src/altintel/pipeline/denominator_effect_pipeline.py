from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from altintel.analytics.denominator import analyze_denominator_effect
from altintel.analytics.prospects import rank_opportunities_for_portfolio
from altintel.core import AppConfig, DenominatorEffectResult
from altintel.data.sample_data import load_opportunity_registry, load_portfolio_snapshot
from altintel.reporting import export_denominator_effect_json, export_denominator_effect_markdown


@dataclass(slots=True)
class DenominatorEffectArtifacts:
    json_path: Path
    markdown_path: Path


def run_denominator_effect_pipeline(
    config: AppConfig,
    portfolio_case: str = "balanced_institution",
    public_market_drawdown_pct: float = 0.25,
    reserve_haircut_pct: float = 0.1,
) -> DenominatorEffectResult:
    portfolio = load_portfolio_snapshot(case_name=portfolio_case)
    opportunities = load_opportunity_registry()
    ranking = rank_opportunities_for_portfolio(
        portfolio_case=portfolio_case,
        portfolio=portfolio,
        opportunities=opportunities,
    )
    base_scores = {entry.opportunity_id: entry.composite_score for entry in ranking.opportunities}
    policy = config.portfolio_policy["policy"]
    return analyze_denominator_effect(
        portfolio_case=portfolio_case,
        portfolio=portfolio,
        opportunities=opportunities,
        base_scores=base_scores,
        target_private_markets_pct=float(policy["target_private_markets_pct"]),
        public_market_drawdown_pct=public_market_drawdown_pct,
        reserve_haircut_pct=reserve_haircut_pct,
    )


def export_denominator_effect_pipeline(
    config: AppConfig,
    portfolio_case: str = "balanced_institution",
    public_market_drawdown_pct: float = 0.25,
    reserve_haircut_pct: float = 0.1,
    output_dir: str | Path = "outputs",
) -> DenominatorEffectArtifacts:
    result = run_denominator_effect_pipeline(
        config=config,
        portfolio_case=portfolio_case,
        public_market_drawdown_pct=public_market_drawdown_pct,
        reserve_haircut_pct=reserve_haircut_pct,
    )
    output_root = Path(output_dir)
    drawdown_label = str(int(public_market_drawdown_pct * 100))
    json_path = export_denominator_effect_json(
        result,
        output_root / f"denominator_effect_{portfolio_case}_{drawdown_label}pct.json",
    )
    markdown_path = export_denominator_effect_markdown(
        result,
        output_root / f"denominator_effect_{portfolio_case}_{drawdown_label}pct.md",
    )
    return DenominatorEffectArtifacts(json_path=json_path, markdown_path=markdown_path)
