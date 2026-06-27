from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from altintel.analytics.prospects import (
    compare_opportunities,
    rank_opportunities_for_portfolio,
    recommend_commitment,
    search_opportunities,
)
from altintel.core import (
    CommitmentRecommendationResult,
    OpportunityComparisonResult,
    OpportunityRankingResult,
    OpportunitySearchResult,
    PortfolioSnapshot,
)
from altintel.data.sample_data import load_opportunity_registry, load_portfolio_snapshot
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
) -> CommitmentRecommendationResult:
    portfolio = load_portfolio_snapshot(case_name=portfolio_case)
    opportunities = load_opportunity_registry()
    return recommend_commitment(
        portfolio_case=portfolio_case,
        portfolio=portfolio,
        opportunities=opportunities,
        opportunity_id=opportunity_id,
    )


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
) -> AIOpportunityPipelineArtifacts:
    result = run_ai_commitment_recommendation_pipeline(
        portfolio_case=portfolio_case,
        opportunity_id=opportunity_id,
    )
    output_root = Path(output_dir)
    json_path = export_commitment_recommendation_json(
        result,
        output_root / f"ai_commitment_recommendation_{portfolio_case}_{opportunity_id}.json",
    )
    markdown_path = export_commitment_recommendation_markdown(
        result,
        output_root / f"ai_commitment_recommendation_{portfolio_case}_{opportunity_id}.md",
    )
    return AIOpportunityPipelineArtifacts(json_path=json_path, markdown_path=markdown_path)
