from __future__ import annotations

import json
from pathlib import Path

from altintel.core.models import (
    CommitmentRecommendationResult,
    DenominatorEffectResult,
    OpportunityComparisonResult,
    OpportunityRankingResult,
)


def _write_json(payload: dict[str, object], path: str | Path) -> Path:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return output_path


def export_opportunity_ranking_json(result: OpportunityRankingResult, path: str | Path) -> Path:
    payload = {
        "portfolio_case": result.portfolio_case,
        "opportunities": [
            {
                "opportunity_id": opportunity.opportunity_id,
                "manager_name": opportunity.manager_name,
                "fund_name": opportunity.fund_name,
                "strategy": opportunity.strategy,
                "vehicle_type": opportunity.vehicle_type,
                "pipeline_stage": opportunity.pipeline_stage,
                "composite_score": opportunity.composite_score,
                "recommended_action": opportunity.recommended_action,
                "reasons": [
                    {
                        "category": reason.category,
                        "score_impact": reason.score_impact,
                        "message": reason.message,
                    }
                    for reason in opportunity.reasons
                ],
            }
            for opportunity in result.opportunities
        ],
    }
    return _write_json(payload, path)


def render_opportunity_ranking_markdown(result: OpportunityRankingResult, top_n: int | None = None) -> str:
    opportunities = result.opportunities[:top_n] if top_n is not None else result.opportunities
    lines = [
        f"# Opportunity Ranking: {result.portfolio_case}",
        "",
        f"- Opportunities ranked: `{len(opportunities)}`",
        "",
        "## Ranked Opportunities",
        "",
    ]
    for item in opportunities:
        lines.append(f"### {item.manager_name} | {item.fund_name}")
        lines.append(f"- Composite score: `{item.composite_score}`")
        lines.append(f"- Vehicle: `{item.vehicle_type}`")
        lines.append(f"- Pipeline stage: `{item.pipeline_stage}`")
        lines.append(f"- Recommended action: {item.recommended_action}")
        lines.append("")
    return "\n".join(lines)


def export_opportunity_ranking_markdown(
    result: OpportunityRankingResult,
    path: str | Path,
    top_n: int | None = None,
) -> Path:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_opportunity_ranking_markdown(result, top_n=top_n), encoding="utf-8")
    return output_path


def export_opportunity_comparison_json(result: OpportunityComparisonResult, path: str | Path) -> Path:
    payload = {
        "portfolio_case": result.portfolio_case,
        "compared_opportunity_ids": result.compared_opportunity_ids,
        "preferred_opportunity_id": result.preferred_opportunity_id,
        "summary": result.summary,
        "entries": [
            {
                "opportunity_id": entry.opportunity_id,
                "manager_name": entry.manager_name,
                "fund_name": entry.fund_name,
                "strategy": entry.strategy,
                "vehicle_type": entry.vehicle_type,
                "pipeline_stage": entry.pipeline_stage,
                "composite_score": entry.composite_score,
                "recommended_action": entry.recommended_action,
                "strengths": entry.strengths,
                "weaknesses": entry.weaknesses,
            }
            for entry in result.entries
        ],
        "dimensions": [
            {
                "category": dimension.category,
                "winner_opportunity_id": dimension.winner_opportunity_id,
                "score_difference": dimension.score_difference,
                "explanation": dimension.explanation,
            }
            for dimension in result.dimensions
        ],
    }
    return _write_json(payload, path)


def render_opportunity_comparison_markdown(result: OpportunityComparisonResult) -> str:
    lines = [
        f"# Opportunity Comparison: {result.portfolio_case}",
        "",
        f"- Preferred opportunity: `{result.preferred_opportunity_id}`",
        f"- Summary: {result.summary}",
        "",
        "## Compared Opportunities",
        "",
    ]
    for entry in result.entries:
        lines.append(f"### {entry.manager_name} | {entry.fund_name}")
        lines.append(f"- Composite score: `{entry.composite_score}`")
        lines.append(f"- Recommended action: {entry.recommended_action}")
        lines.append("- Strengths:")
        for strength in entry.strengths[:3]:
            lines.append(f"  - {strength}")
        lines.append("- Weaknesses:")
        for weakness in entry.weaknesses[:3]:
            lines.append(f"  - {weakness}")
        lines.append("")
    lines.append("## Dimension Winners")
    lines.append("")
    for dimension in result.dimensions:
        lines.append(
            f"- `{dimension.category}` | winner `{dimension.winner_opportunity_id}` | diff `{dimension.score_difference}`"
        )
    return "\n".join(lines)


def export_opportunity_comparison_markdown(result: OpportunityComparisonResult, path: str | Path) -> Path:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_opportunity_comparison_markdown(result), encoding="utf-8")
    return output_path


def export_commitment_recommendation_json(result: CommitmentRecommendationResult, path: str | Path) -> Path:
    payload = {
        "portfolio_case": result.portfolio_case,
        "opportunity_id": result.opportunity_id,
        "manager_name": result.manager_name,
        "fund_name": result.fund_name,
        "recommendation": result.recommendation,
        "conviction": result.conviction,
        "composite_score": result.composite_score,
        "summary": result.summary,
        "denominator_effect_applied": result.denominator_effect_applied,
        "baseline_recommendation": result.baseline_recommendation,
        "baseline_conviction": result.baseline_conviction,
        "baseline_composite_score": result.baseline_composite_score,
        "public_market_drawdown_pct": result.public_market_drawdown_pct,
        "stressed_private_markets_pct": result.stressed_private_markets_pct,
        "overweight_gap_pct": result.overweight_gap_pct,
        "stressed_key_constraint": result.stressed_key_constraint,
        "reasons": [
            {
                "category": reason.category,
                "impact": reason.impact,
                "message": reason.message,
            }
            for reason in result.reasons
        ],
        "conditions": result.conditions,
    }
    return _write_json(payload, path)


def render_commitment_recommendation_markdown(result: CommitmentRecommendationResult) -> str:
    lines = [
        f"# Commitment Recommendation: {result.fund_name}",
        "",
        f"- Portfolio case: `{result.portfolio_case}`",
        f"- Recommendation: `{result.recommendation}`",
        f"- Conviction: `{result.conviction}`",
        f"- Composite score: `{result.composite_score}`",
        f"- Summary: {result.summary}",
        "",
    ]
    if result.denominator_effect_applied:
        lines.extend(
            [
                "## Stress Context",
                "",
                f"- Baseline recommendation: `{result.baseline_recommendation}`",
                f"- Baseline score: `{result.baseline_composite_score}`",
                f"- Public-market drawdown: `{result.public_market_drawdown_pct}`",
                f"- Stressed private-markets pct: `{result.stressed_private_markets_pct}`",
                f"- Overweight gap pct: `{result.overweight_gap_pct}`",
                f"- Key stressed constraint: `{result.stressed_key_constraint}`",
                "",
            ]
        )
    lines.extend(["## Reasons", ""])
    for reason in result.reasons:
        lines.append(f"- `{reason.category}` | `{reason.impact}` | {reason.message}")
    lines.append("")
    lines.append("## Conditions")
    lines.append("")
    for condition in result.conditions:
        lines.append(f"- {condition}")
    return "\n".join(lines)


def export_commitment_recommendation_markdown(result: CommitmentRecommendationResult, path: str | Path) -> Path:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_commitment_recommendation_markdown(result), encoding="utf-8")
    return output_path


def export_denominator_effect_json(result: DenominatorEffectResult, path: str | Path) -> Path:
    payload = {
        "portfolio_case": result.portfolio_case,
        "public_market_drawdown_pct": result.public_market_drawdown_pct,
        "baseline_private_markets_pct": result.baseline_private_markets_pct,
        "stressed_private_markets_pct": result.stressed_private_markets_pct,
        "target_private_markets_pct": result.target_private_markets_pct,
        "overweight_gap_pct": result.overweight_gap_pct,
        "baseline_public_nav_mn": result.baseline_public_nav_mn,
        "stressed_public_nav_mn": result.stressed_public_nav_mn,
        "stressed_liquid_reserves_mn": result.stressed_liquid_reserves_mn,
        "summary": result.summary,
        "opportunity_impacts": [
            {
                "opportunity_id": impact.opportunity_id,
                "manager_name": impact.manager_name,
                "fund_name": impact.fund_name,
                "base_composite_score": impact.base_composite_score,
                "stressed_composite_score": impact.stressed_composite_score,
                "score_change": impact.score_change,
                "stressed_recommendation": impact.stressed_recommendation,
                "key_constraint": impact.key_constraint,
            }
            for impact in result.opportunity_impacts
        ],
    }
    return _write_json(payload, path)


def render_denominator_effect_markdown(result: DenominatorEffectResult, top_n: int | None = 8) -> str:
    impacts = result.opportunity_impacts[:top_n] if top_n is not None else result.opportunity_impacts
    lines = [
        f"# Denominator Effect: {result.portfolio_case}",
        "",
        f"- Public-market drawdown: `{result.public_market_drawdown_pct}`",
        f"- Baseline private-markets pct: `{result.baseline_private_markets_pct}`",
        f"- Stressed private-markets pct: `{result.stressed_private_markets_pct}`",
        f"- Target private-markets pct: `{result.target_private_markets_pct}`",
        f"- Overweight gap pct: `{result.overweight_gap_pct}`",
        f"- Stressed liquid reserves (EUR mn): `{result.stressed_liquid_reserves_mn}`",
        "",
        "## Opportunity Impacts",
        "",
    ]
    for impact in impacts:
        lines.append(f"### {impact.manager_name} | {impact.fund_name}")
        lines.append(f"- Base score: `{impact.base_composite_score}`")
        lines.append(f"- Stressed score: `{impact.stressed_composite_score}`")
        lines.append(f"- Stressed recommendation: `{impact.stressed_recommendation}`")
        lines.append(f"- Key constraint: `{impact.key_constraint}`")
        lines.append("")
    return "\n".join(lines)


def export_denominator_effect_markdown(
    result: DenominatorEffectResult,
    path: str | Path,
    top_n: int | None = 8,
) -> Path:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_denominator_effect_markdown(result, top_n=top_n), encoding="utf-8")
    return output_path
