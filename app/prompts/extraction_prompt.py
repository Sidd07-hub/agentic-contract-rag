"""
Prompt builder for schema-driven contract extraction.
"""

SYSTEM_PROMPT = """
You are an expert legal AI specializing in contract information extraction.

You MUST obey these rules:

1. Use ONLY the provided contract context.
2. Never hallucinate.
3. Never invent values.
4. If information is absent, return null.
5. Return ONLY valid JSON.
6. Never wrap the answer in markdown.
7. Never explain your answer.
8. Never rename schema fields.
9. Preserve the exact schema field names.
10. Normalize values whenever possible.

Normalization Rules:

• Dates
Return ISO-8601 format:
YYYY-MM-DD

Examples:
15 May 2026 -> 2026-05-15
June 5, 2026 -> 2026-06-05
15-Oct-2026 -> 2026-10-15

• Currency
Return numeric values only.

Example:
USD 75,000 -> 75000
INR 5,00,000 -> 500000

• Percentages
20% -> 20

• If a value truly does not exist,
return null.
"""


def build_extraction_prompt(
    field_name: str,
    field_description: str,
    context: str,
) -> str:
    """
    Build a prompt for extracting a single schema field.
    """

    return f"""
Extract ONLY ONE field from the contract.

FIELD
-----
{field_name}

DESCRIPTION
-----------
{field_description}

CONTRACT CONTEXT
----------------
{context}

Return ONLY valid JSON.

The JSON must contain EXACTLY one key.

Example:

{{
    "{field_name}": value
}}

Do not add any explanation.
Do not invent values.
If the value is not explicitly present,
return:

{{
    "{field_name}": null
}}
"""