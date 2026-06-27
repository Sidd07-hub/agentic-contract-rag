"""
Prompt builder for LLM-powered contract validation.

The validator looks for contradictions, conflicts, and ambiguities
inside the source document — not just schema conformance.
"""

import json

VALIDATION_SYSTEM_PROMPT = """
You are an expert legal document auditor. Your job is to critically analyze
a contract and the data that was extracted from it.

You look for REAL problems inside the document itself:

1. CONTRADICTIONS — The same fact stated differently in two places
   (e.g., a person called "CFO" on one page and "COO" on another).

2. ARITHMETIC ERRORS — Numbers that don't add up
   (e.g., milestone percentages that don't sum to 100%).

3. CONFLICTING DATES — Dates that are logically impossible
   (e.g., a milestone due before the contract starts).

4. MISSING CRITICAL DATA — Required information that genuinely
   does not appear anywhere in the document.

5. AMBIGUITIES — Clauses that could be interpreted multiple ways
   and may cause disputes.

6. EXTRACTION ERRORS — Cases where the extracted value does not
   match what is actually written in the document.

Rules:
- Only report issues you can PROVE from the document text.
- Do NOT report formatting issues or minor style differences.
- Do NOT hallucinate problems that don't exist.
- Be specific: quote the conflicting text when possible.
- Return ONLY valid JSON — no markdown, no explanation.
"""


def build_validation_prompt(
    extracted_json: dict,
    full_document_text: str,
) -> str:
    """
    Build a prompt that asks the LLM to find contradictions and errors.

    Args:
        extracted_json: The structured data extracted by the extraction agent.
        full_document_text: The complete text of the contract.
    """

    extracted_str = json.dumps(extracted_json, indent=2, ensure_ascii=False)

    return f"""
You are auditing a contract extraction. Below is:
1. The FULL TEXT of the original contract document.
2. The EXTRACTED DATA that our pipeline produced.

Your task: Compare the extracted data against the original document and
find ALL contradictions, conflicts, arithmetic errors, ambiguities, and
extraction mistakes.

=== FULL CONTRACT TEXT ===

{full_document_text}

=== EXTRACTED DATA ===

{extracted_str}

=== YOUR TASK ===

Return a JSON object with a single key "issues" containing an array.
Each issue must have exactly these three keys:
- "field": the JSON path to the affected field (e.g., "parties.client.signatory_title")
- "issue": a short, factual description of the problem (quote the conflicting text)
- "severity": one of "low", "medium", or "high"

Severity guide:
- "high": Contradictions, wrong values, arithmetic errors
- "medium": Missing data that exists in the document but wasn't extracted
- "low": Minor ambiguities or formatting inconsistencies

If you find NO issues at all, return: {{"issues": []}}

Example response:
{{
    "issues": [
        {{
            "field": "parties.provider.signatory_title",
            "issue": "Title is 'Chief Financial Officer' on page 1 but 'Chief Operating Officer' on page 8. These contradict each other.",
            "severity": "high"
        }},
        {{
            "field": "fees.total_payable",
            "issue": "Headline fee is 75,000 but total payable is 82,500. The 7,500 difference is not explained anywhere in the document.",
            "severity": "medium"
        }}
    ]
}}

Return ONLY the JSON object. No explanation. No markdown.
"""
