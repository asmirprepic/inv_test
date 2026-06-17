from __future__ import annotations

import json
from pathlib import Path

from altintel.core.models import AIWatchlistResult


def _watchlist_payload(result: AIWatchlistResult) -> dict[str, object]:
    return {
        "portfolio_case": result.portfolio_case,
        "generated_as_of": result.generated_as_of.isoformat(),
        "portfolio_cash_burn_ratio": result.portfolio_cash_burn_ratio,
        "entries": [
            {
                "holding_name": entry.holding_name,
                "strategy": entry.strategy,
                "as_of": entry.as_of.isoformat(),
                "priority_score": entry.priority_score,
                "priority_label": entry.priority_label,
                "recommended_action": entry.recommended_action,
                "reasons": [
                    {
                        "category": reason.category,
                        "signal_strength": reason.signal_strength,
                        "message": reason.message,
                    }
                    for reason in entry.reasons
                ],
            }
            for entry in result.entries
        ],
    }


def export_watchlist_json(result: AIWatchlistResult, path: str | Path) -> Path:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(_watchlist_payload(result), indent=2), encoding="utf-8")
    return output_path


def render_watchlist_markdown(result: AIWatchlistResult, top_n: int | None = None) -> str:
    entries = result.entries[:top_n] if top_n is not None else result.entries
    lines = [
        f"# AI Watchlist: {result.portfolio_case}",
        "",
        f"- Generated as of: `{result.generated_as_of.isoformat()}`",
        f"- Portfolio cash burn ratio: `{result.portfolio_cash_burn_ratio}`",
        f"- Holdings on watchlist: `{len(entries)}`",
        "",
        "## Prioritized Entries",
        "",
    ]
    for entry in entries:
        lines.append(
            f"### {entry.holding_name} ({entry.strategy})"
        )
        lines.append(f"- Priority score: `{entry.priority_score}`")
        lines.append(f"- Priority label: `{entry.priority_label}`")
        lines.append(f"- Recommended action: {entry.recommended_action}")
        lines.append("- Key reasons:")
        for reason in entry.reasons[:4]:
            lines.append(
                f"  - `{reason.category}` | strength `{reason.signal_strength}` | {reason.message}"
            )
        lines.append("")
    return "\n".join(lines)


def export_watchlist_markdown(result: AIWatchlistResult, path: str | Path, top_n: int | None = None) -> Path:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_watchlist_markdown(result, top_n=top_n), encoding="utf-8")
    return output_path
