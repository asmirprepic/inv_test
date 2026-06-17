from __future__ import annotations

from altintel.pipeline import export_ai_watchlist_pipeline, run_ai_watchlist_pipeline


def main() -> None:
    result = run_ai_watchlist_pipeline(portfolio_case="balanced_institution")
    artifacts = export_ai_watchlist_pipeline(portfolio_case="balanced_institution")

    print(f"AI watchlist for portfolio case: {result.portfolio_case}")
    print(f"Generated as of: {result.generated_as_of}")
    print(f"Portfolio cash burn ratio: {result.portfolio_cash_burn_ratio}")
    print(f"JSON artifact: {artifacts.json_path}")
    print(f"Markdown artifact: {artifacts.markdown_path}")
    for entry in result.entries[:5]:
        print(
            f"- {entry.holding_name} | score={entry.priority_score} | "
            f"label={entry.priority_label} | action={entry.recommended_action}"
        )
        for reason in entry.reasons[:3]:
            print(f"  reason: {reason.category} | strength={reason.signal_strength} | {reason.message}")


if __name__ == "__main__":
    main()
