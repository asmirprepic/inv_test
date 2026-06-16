from __future__ import annotations

from altintel.data.sample_data import load_named_proposed_commitment
from altintel.llm.retrieval import build_retrieval_packet


def main() -> None:
    memo = load_named_proposed_commitment(case_name="infrastructure")
    print(build_retrieval_packet(memo))


if __name__ == "__main__":
    main()
