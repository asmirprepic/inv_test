from __future__ import annotations

from altintel.core.models import InvestmentMemoInput


def build_due_diligence_extraction_prompt(memo: InvestmentMemoInput) -> str:
    return f"""You are extracting structured due diligence data from a synthetic alternative-investment memo.

Return strict JSON with this schema:
{{
  "fund_name": string,
  "strategy": string,
  "geography": string,
  "target_size_mn": number,
  "gp_commitment_pct": number,
  "management_fee_pct": number,
  "carry_pct": number,
  "term_years": integer,
  "risks": [
    {{
      "category": string,
      "severity": string,
      "title": string,
      "rationale": string
    }}
  ],
  "validation_notes": [string]
}}

Rules:
- Use only information supported by the memo text.
- Do not wrap the JSON in markdown fences.
- Use concise but specific titles and rationales.
- Prefer the strategy and geography from the memo content when clearly stated.

Document ID: {memo.document_id}
Fund name in input metadata: {memo.fund_name}
Document text:
{memo.source_text}
"""
