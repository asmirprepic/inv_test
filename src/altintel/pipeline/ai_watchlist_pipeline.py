from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from altintel.analytics.monitoring import build_data_driven_insights
from altintel.analytics.watchlist import build_ai_watchlist
from altintel.core import AIWatchlistResult
from altintel.data.sample_data import load_portfolio_snapshot
from altintel.data.simulation import generate_portfolio_monitoring_data
from altintel.reporting import export_watchlist_json, export_watchlist_markdown


@dataclass(slots=True)
class AIWatchlistPipelineArtifacts:
    json_path: Path
    markdown_path: Path


def run_ai_watchlist_pipeline(
    portfolio_case: str = "balanced_institution",
    quarters: int = 12,
    seed: int = 7,
) -> AIWatchlistResult:
    portfolio = load_portfolio_snapshot(case_name=portfolio_case)
    observations = generate_portfolio_monitoring_data(portfolio, quarters=quarters, seed=seed)
    insights = build_data_driven_insights(observations, portfolio.liquid_reserves_mn)
    return build_ai_watchlist(portfolio_case=portfolio_case, insights=insights)


def export_ai_watchlist_pipeline(
    portfolio_case: str = "balanced_institution",
    quarters: int = 12,
    seed: int = 7,
    output_dir: str | Path = "outputs",
) -> AIWatchlistPipelineArtifacts:
    result = run_ai_watchlist_pipeline(portfolio_case=portfolio_case, quarters=quarters, seed=seed)
    output_root = Path(output_dir)
    json_path = export_watchlist_json(
        result,
        output_root / f"ai_watchlist_{portfolio_case}.json",
    )
    markdown_path = export_watchlist_markdown(
        result,
        output_root / f"ai_watchlist_{portfolio_case}.md",
    )
    return AIWatchlistPipelineArtifacts(json_path=json_path, markdown_path=markdown_path)
