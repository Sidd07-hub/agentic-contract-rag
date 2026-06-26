"""
Field-specific retrieval queries.

Maps JSON schema fields to semantic search queries.
"""

FIELD_QUERIES = {

    "effective_date":
        "Find the effective date of the agreement.",

    "provider":
        "Find the provider company legal name, address, and organization details.",

    "client":
        "Find the client company legal name, address, and organization details.",

    "services":
        "Find the scope of services and deliverables provided under this agreement.",

    "fees":
        "Find payment terms, fees, invoices, taxes, milestone payments, and pricing.",

    "term":
        "Find the contract duration, renewal terms, and agreement period.",

    "termination":
        "Find termination clauses including termination for convenience, termination for cause, notice period, and obligations after termination.",

    "confidentiality":
        "Find confidentiality obligations and confidential information clauses.",

    "intellectual_property":
        "Find ownership of intellectual property, deliverables, licensing, and pre-existing IP.",

    "liability":
        "Find limitation of liability, indemnification, exclusions, and liability caps.",

    "governing_law":
        "Find governing law, jurisdiction, arbitration, and dispute resolution.",

    "sla":
        "Find service levels, response times, resolution targets, and service credits."
}