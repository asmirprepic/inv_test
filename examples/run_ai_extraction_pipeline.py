from __future__ import annotations

from altintel.core import load_app_config
from altintel.pipeline import run_ai_extraction_pipeline


def main() -> None:
    result = run_ai_extraction_pipeline(load_app_config(), commitment_case="infrastructure")

    print(f"AI extraction pipeline for: {result.commitment_case}")
    print(f"Validation passed: {result.validation_passed}")
    print(f"Fact evidence coverage: {result.fact_evidence_coverage}")
    print(f"Risk evidence coverage: {result.risk_evidence_coverage}")
    print("Retrieved sections:")
    for section in result.retrieved_sections:
        print(f"- {section.section} | score={section.score}")
    print("Extracted risks:")
    for risk in result.due_diligence_report.risks:
        print(f"- {risk.category}: {risk.severity} | {risk.title}")


if __name__ == "__main__":
    main()
