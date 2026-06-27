"""
Prompt builder for schema-driven contract extraction.
"""

import json

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

- Dates
Return ISO-8601 format:
YYYY-MM-DD

Examples:
15 May 2026 -> 2026-05-15
June 5, 2026 -> 2026-06-05
15-Oct-2026 -> 2026-10-15

- Currency
Return numeric values only.

Example:
USD 75,000 -> 75000
INR 5,00,000 -> 500000

- Percentages
20% -> 20

- If a value truly does not exist,
return null.
"""


def build_extraction_prompt(
    field_name: str,
    field_description: str,
    context: str,
    field_schema: dict | None = None,
) -> str:
    """
    Build a prompt for extracting a single schema field.

    Args:
        field_name: The dotted path of the field (e.g. "parties.provider.legal_name").
        field_description: Human-readable description from the schema.
        context: Retrieved contract text chunks.
        field_schema: The full JSON schema definition for this field (used for arrays).
    """

    # For array fields, include the item schema so the LLM uses exact key names
    array_instructions = ""
    if field_schema and field_schema.get("type") == "array" and "items" in field_schema:
        items = field_schema["items"]
        required_keys = items.get("required", [])
        properties = items.get("properties", {})

        key_descriptions = []
        for key, prop in properties.items():
            desc = prop.get("description", "")
            ptype = prop.get("type", "string")
            req = " (REQUIRED)" if key in required_keys else ""
            key_descriptions.append(f'  - "{key}" ({ptype}){req}: {desc}')

        keys_block = "\n".join(key_descriptions)

        array_instructions = f"""
IMPORTANT: This field is an ARRAY of objects.
Each object in the array MUST use these EXACT key names:

{keys_block}

Return ALL items found in the document.
If a value within an item cannot be determined, use null for that value.
Do NOT rename or abbreviate any keys.
"""

    return f"""
Extract ONLY ONE field from the contract.

FIELD
-----
{field_name}

DESCRIPTION
-----------
{field_description}
{array_instructions}
CONTRACT CONTEXT
----------------
{context}

Return ONLY valid JSON.

The JSON must contain EXACTLY one key: "{field_name}".

Example for a simple field:

{{
    "{field_name}": value
}}

Example for an array field:

{{
    "{field_name}": [
        {{ ... }},
        {{ ... }}
    ]
}}

Do not add any explanation.
Do not invent values.
If the value is not explicitly present, return:

{{
    "{field_name}": null
}}
"""