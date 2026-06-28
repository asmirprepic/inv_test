from __future__ import annotations

import _bootstrap

from altintel.core import load_app_config
from altintel.due_diligence.evaluation import run_extraction_evaluation


def main() -> None:
    result = run_extraction_evaluation(load_app_config())

    print("Due diligence extraction evaluation")
    print(f"Average field accuracy: {result.average_field_accuracy}")
    print(f"Average risk recall: {result.average_risk_recall}")
    print(f"Average fact evidence coverage: {result.average_fact_evidence_coverage}")
    print(f"Average risk evidence coverage: {result.average_risk_evidence_coverage}")
    for case in result.cases:
        print(
            f"- {case.commitment_case}: field_accuracy={case.field_accuracy} "
            f"risk_recall={case.risk_recall} "
            f"fact_evidence={case.fact_evidence_coverage} risk_evidence={case.risk_evidence_coverage} "
            f"({case.matched_fields}/{case.total_fields} fields, {case.matched_risks}/{case.total_risks} risks)"
        )



if __name__ == "__main__":
    main()
