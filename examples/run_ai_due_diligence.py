from __future__ import annotations

from altintel.core import load_app_config
from altintel.data.sample_data import load_proposed_commitment
from altintel.due_diligence.service import run_due_diligence


def main() -> None:
    config = load_app_config()
    memo = load_proposed_commitment()
    report = run_due_diligence(memo, config)

    print(f"Fund: {report.facts.fund_name}")
    print(f"Strategy: {report.facts.strategy}")
    print(f"Target size (EUR mn): {report.facts.target_size_mn}")
    print(f"GP commitment (%): {report.facts.gp_commitment_pct}")
    print(f"Overall risk rating: {report.overall_risk_rating}")
    print("Risks:")
    for risk in report.risks:
        print(f"- {risk.category}: {risk.severity} | {risk.title}")


if __name__ == "__main__":
    main()
