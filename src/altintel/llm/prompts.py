from __future__ import annotations

from altintel.core.models import InvestmentMemoInput
from altintel.llm.retrieval import build_retrieval_packet


def build_due_diligence_extraction_prompt(memo: InvestmentMemoInput) -> str:
    retrieval_packet = build_retrieval_packet(memo)
    return f"""You are an analyst extracting structured due-diligence data from a synthetic alternative-investment memo.

Your job is to convert the memo into normalized JSON for downstream quantitative workflows.

Requirements:
- Return only valid JSON. Do not include markdown fences, commentary, or explanatory prose outside the JSON object.
- Use only facts supported by the memo text.
- Ground every output in the retrieved memo context provided below.
- If a field is not stated explicitly and cannot be inferred with high confidence, set its value to `null` and mention the gap in `validation_notes`.
- Normalize monetary fields to EUR millions as numbers.
- Normalize percentage fields as numeric percentages, e.g. `2.5` for 2.5%.
- Keep `strategy` and `geography` concise and normalized.
- Separate extracted facts from synthesized risk judgments.
- Every extracted fact must include evidence.
- Every risk must use one of the allowed categories for the detected strategy.

Allowed risk categories by strategy:
- infrastructure: ["deployment_pacing", "financing_risk", "sector_concentration", "key_person"]
- timberland: ["biological_weather", "exit_timing", "geographic_concentration", "operating_complexity"]

JSON schema:
{{
  "facts": {{
    "fund_name": {{
      "value": string|null,
      "confidence": "high"|"medium"|"low",
      "evidence_quote": string,
      "evidence_section": string
    }},
    "strategy": {{
      "value": string|null,
      "confidence": "high"|"medium"|"low",
      "evidence_quote": string,
      "evidence_section": string
    }},
    "geography": {{
      "value": string|null,
      "confidence": "high"|"medium"|"low",
      "evidence_quote": string,
      "evidence_section": string
    }},
    "target_size_mn": {{
      "value": number|null,
      "confidence": "high"|"medium"|"low",
      "evidence_quote": string,
      "evidence_section": string
    }},
    "gp_commitment_pct": {{
      "value": number|null,
      "confidence": "high"|"medium"|"low",
      "evidence_quote": string,
      "evidence_section": string
    }},
    "management_fee_pct": {{
      "value": number|null,
      "confidence": "high"|"medium"|"low",
      "evidence_quote": string,
      "evidence_section": string
    }},
    "carry_pct": {{
      "value": number|null,
      "confidence": "high"|"medium"|"low",
      "evidence_quote": string,
      "evidence_section": string
    }},
    "term_years": {{
      "value": integer|null,
      "confidence": "high"|"medium"|"low",
      "evidence_quote": string,
      "evidence_section": string
    }}
  }},
  "risks": [
    {{
      "category": string,
      "severity": "low"|"medium"|"high",
      "title": string,
      "rationale": string,
      "evidence_quote": string,
      "evidence_section": string
    }}
  ],
  "overall_risk_rating": "low"|"medium"|"high",
  "validation_notes": [string]
}}

Quality rules:
- Use exact supporting quote snippets from the memo for evidence fields.
- Do not invent sections. Use the nearest visible memo heading.
- If the memo uses a broader regional phrase, preserve that phrase rather than over-normalizing.
- Titles should read like investment-committee risk headers, not generic labels.
- Rationales should be concise and decision-useful.
- If retrieved context is insufficient for a field, prefer `null` over guessing.

Document ID: {memo.document_id}
Fund name in input metadata: {memo.fund_name}
{retrieval_packet}
"""
