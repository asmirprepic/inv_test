from __future__ import annotations

from altintel.core import load_app_config
from altintel.due_diligence.evaluation import run_extraction_evaluation


def main() -> None:
    result = run_extraction_evaluation(load_app_config())

    print("Due diligence extraction evaluation")
    print(f"Average field accuracy: {result.average_field_accuracy}")
    print(f"Average risk recall: {result.average_risk_recall}")
    for case in result.cases:
        print(
            f"- {case.commitment_case}: field_accuracy={case.field_accuracy} "
            f"risk_recall={case.risk_recall} "
            f"({case.matched_fields}/{case.total_fields} fields, {case.matched_risks}/{case.total_risks} risks)"
        )


if __name__ == "__main__":
    main()
