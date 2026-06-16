from __future__ import annotations

from altintel.core import load_app_config
from altintel.pipeline import run_ai_evaluation_pipeline


def main() -> None:
    result = run_ai_evaluation_pipeline(load_app_config())

    print("AI evaluation pipeline")
    print(f"Provider: {result.provider}")
    print(f"Model: {result.model}")
    print(f"Passed: {result.passed}")
    print(f"Failed checks: {result.failed_checks or ['none']}")
    print(f"Average field accuracy: {result.evaluation.average_field_accuracy}")
    print(f"Average risk recall: {result.evaluation.average_risk_recall}")
    print(f"Average fact evidence coverage: {result.evaluation.average_fact_evidence_coverage}")
    print(f"Average risk evidence coverage: {result.evaluation.average_risk_evidence_coverage}")


if __name__ == "__main__":
    main()
