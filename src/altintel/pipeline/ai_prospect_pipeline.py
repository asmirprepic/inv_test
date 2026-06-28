from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from altintel.analytics.prospects import (
    compare_opportunities,
    rank_opportunities_for_portfolio,
    recommend_commitment,
    search_opportunities,
)
from altintel.core.config import AppConfig
from altintel.core import (
    CommitmentRecommendationResult,
    DenominatorEffectResult,
    OpportunityComparisonResult,
    OpportunityRankingResult,
    OpportunitySearchResult,
    PortfolioSnapshot,
)
from altintel.data.sample_data import load_opportunity_registry, load_portfolio_snapshot
from altintel.pipeline.denominator_effect_pipeline import run_denominator_effect_pipeline
from altintel.reporting import (
    export_commitment_recommendation_json,
    export_commitment_recommendation_markdown,
    export_opportunity_comparison_json,
    export_opportunity_comparison_markdown,
    export_opportunity_ranking_json,
    export_opportunity_ranking_markdown,
)


@dataclass(slots=True)
class AIOpportunityUniverse:
    portfolio_case: str
    portfolio: PortfolioSnapshot
    opportunity_count: int


@dataclass(slots=True)
class AIOpportunityPipelineArtifacts:
    json_path: Path
    markdown_path: Path


def _stressed_conviction(recommendation: str) -> str:
    if recommendation == "advance":
        return "medium"
    if recommendation == "advance_with_conditions":
        return "medium"
    if recommendation == "hold":
        return "low"
    return "low"


def _apply_denominator_effect_to_recommendation(
    result: CommitmentRecommendationResult,
    denominator_effect: DenominatorEffectResult,
) -> CommitmentRecommendationResult:
    impact = next(
        item for item in denominator_effect.opportunity_impacts if item.opportunity_id == result.opportunity_id
    )
    stressed_reasons = list(result.reasons)
    stressed_reasons.append(
        result.reasons[0].__class__(
            category="denominator_effect",
            impact="negative" if denominator_effect.overweight_gap_pct > 0 else "neutral",
            message=(
                f"Private-markets allocation rises to "
                f"{round(denominator_effect.stressed_private_markets_pct * 100, 2)}% after public-market drawdown."
            ),
        )
    )
    stressed_conditions = list(result.conditions)
    if denominator_effect.overweight_gap_pct > 0:
        stressed_conditions.append(
            "Reconfirm commitment pacing under denominator-effect stress before advancing to final approval."
        )
    stressed_conditions.append(f"Primary stressed constraint identified: {impact.key_constraint}.")

    return CommitmentRecommendationResult(
        portfolio_case=result.portfolio_case,
        opportunity_id=result.opportunity_id,
        manager_name=result.manager_name,
        fund_name=result.fund_name,
        recommendation=impact.stressed_recommendation,
        conviction=_stressed_conviction(impact.stressed_recommendation),
        composite_score=impact.stressed_composite_score,
        reasons=stressed_reasons,
        conditions=stressed_conditions,
        summary=(
            f"{impact.stressed_recommendation.replace('_', ' ').title()} {result.fund_name} for "
            f"{result.portfolio_case} after denominator-effect stress."
        ),
        denominator_effect_applied=True,
        baseline_recommendation=result.recommendation,
        baseline_conviction=result.conviction,
        baseline_composite_score=result.composite_score,
        public_market_drawdown_pct=denominator_effect.public_market_drawdown_pct,
        stressed_private_markets_pct=denominator_effect.stressed_private_markets_pct,
        overweight_gap_pct=denominator_effect.overweight_gap_pct,
        stressed_key_constraint=impact.key_constraint,
    )


def build_ai_opportunity_universe(portfolio_case: str = "balanced_institution") -> AIOpportunityUniverse:
    portfolio = load_portfolio_snapshot(case_name=portfolio_case)
    opportunities = load_opportunity_registry()
    return AIOpportunityUniverse(
        portfolio_case=portfolio_case,
        portfolio=portfolio,
        opportunity_count=len(opportunities),
    )


def run_ai_opportunity_ranking_pipeline(portfolio_case: str = "balanced_institution") -> OpportunityRankingResult:
    portfolio = load_portfolio_snapshot(case_name=portfolio_case)
    opportunities = load_opportunity_registry()
    return rank_opportunities_for_portfolio(
        portfolio_case=portfolio_case,
        portfolio=portfolio,
        opportunities=opportunities,
    )


def run_ai_opportunity_search_pipeline(query: str) -> OpportunitySearchResult:
    opportunities = load_opportunity_registry()
    return search_opportunities(query=query, opportunities=opportunities)


def run_ai_opportunity_comparison_pipeline(
    portfolio_case: str,
    compared_opportunity_ids: list[str],
) -> OpportunityComparisonResult:
    portfolio = load_portfolio_snapshot(case_name=portfolio_case)
    opportunities = load_opportunity_registry()
    return compare_opportunities(
        portfolio_case=portfolio_case,
        portfolio=portfolio,
        opportunities=opportunities,
        compared_opportunity_ids=compared_opportunity_ids,
    )


def run_ai_commitment_recommendation_pipeline(
    portfolio_case: str,
    opportunity_id: str,
    config: AppConfig | None = None,
    public_market_drawdown_pct: float | None = None,
    reserve_haircut_pct: float = 0.1,
) -> CommitmentRecommendationResult:
    portfolio = load_portfolio_snapshot(case_name=portfolio_case)
    opportunities = load_opportunity_registry()
    result = recommend_commitment(
        portfolio_case=portfolio_case,
        portfolio=portfolio,
        opportunities=opportunities,
        opportunity_id=opportunity_id,
    )
    if config is not None and public_market_drawdown_pct is not None:
        denominator_effect = run_denominator_effect_pipeline(
            config=config,
            portfolio_case=portfolio_case,
            public_market_drawdown_pct=public_market_drawdown_pct,
            reserve_haircut_pct=reserve_haircut_pct,
        )
        return _apply_denominator_effect_to_recommendation(result, denominator_effect)
    return result


def export_ai_opportunity_ranking_pipeline(
    portfolio_case: str = "balanced_institution",
    output_dir: str | Path = "outputs",
) -> AIOpportunityPipelineArtifacts:
    result = run_ai_opportunity_ranking_pipeline(portfolio_case=portfolio_case)
    output_root = Path(output_dir)
    json_path = export_opportunity_ranking_json(result, output_root / f"ai_opportunity_ranking_{portfolio_case}.json")
    markdown_path = export_opportunity_ranking_markdown(
        result,
        output_root / f"ai_opportunity_ranking_{portfolio_case}.md",
    )
    return AIOpportunityPipelineArtifacts(json_path=json_path, markdown_path=markdown_path)


def export_ai_opportunity_comparison_pipeline(
    portfolio_case: str,
    compared_opportunity_ids: list[str],
    output_dir: str | Path = "outputs",
) -> AIOpportunityPipelineArtifacts:
    result = run_ai_opportunity_comparison_pipeline(
        portfolio_case=portfolio_case,
        compared_opportunity_ids=compared_opportunity_ids,
    )
    output_root = Path(output_dir)
    comparison_key = "_vs_".join(compared_opportunity_ids)
    json_path = export_opportunity_comparison_json(
        result,
        output_root / f"ai_opportunity_comparison_{portfolio_case}_{comparison_key}.json",
    )
    markdown_path = export_opportunity_comparison_markdown(
        result,
        output_root / f"ai_opportunity_comparison_{portfolio_case}_{comparison_key}.md",
    )
    return AIOpportunityPipelineArtifacts(json_path=json_path, markdown_path=markdown_path)


def export_ai_commitment_recommendation_pipeline(
    portfolio_case: str,
    opportunity_id: str,
    output_dir: str | Path = "outputs",
    config: AppConfig | None = None,
    public_market_drawdown_pct: float | None = None,
    reserve_haircut_pct: float = 0.1,
) -> AIOpportunityPipelineArtifacts:
    result = run_ai_commitment_recommendation_pipeline(
        portfolio_case=portfolio_case,
        opportunity_id=opportunity_id,
        config=config,
        public_market_drawdown_pct=public_market_drawdown_pct,
        reserve_haircut_pct=reserve_haircut_pct,
    )
    output_root = Path(output_dir)
    suffix = f"_stress_{int(public_market_drawdown_pct * 100)}pct" if public_market_drawdown_pct is not None else ""
    json_path = export_commitment_recommendation_json(
        result,
        output_root / f"ai_commitment_recommendation_{portfolio_case}_{opportunity_id}{suffix}.json",
    )
    markdown_path = export_commitment_recommendation_markdown(
        result,
        output_root / f"ai_commitment_recommendation_{portfolio_case}_{opportunity_id}{suffix}.md",
    )
    return AIOpportunityPipelineArtifacts(json_path=json_path, markdown_path=markdown_path)
