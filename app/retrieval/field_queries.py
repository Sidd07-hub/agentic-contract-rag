"""
Semantic retrieval queries.

Each schema field is mapped to a natural-language search query that
helps retrieve the most relevant contract sections before sending
them to the LLM.
"""

FIELD_QUERIES = {

    # ------------------------------------------------------------------
    # Contract Information
    # ------------------------------------------------------------------

    "contract_id":
        "contract number agreement number master services agreement identifier document reference",

    "effective_date":
        "effective date date entered into agreement commencement date execution date",

    "term_months":
        "initial term contract duration agreement period number of months renewal term",


    # ------------------------------------------------------------------
    # Parties
    # ------------------------------------------------------------------

    "parties":
        "provider client parties legal name registered office principal place of business address signatory authorised representative",


    # ------------------------------------------------------------------
    # Fees
    # ------------------------------------------------------------------

    "fees":
        "payment fees pricing headline fee total payable reimbursement expenses taxes currency invoice payment schedule",


    # ------------------------------------------------------------------
    # Deliverables / Milestones
    # ------------------------------------------------------------------

    "milestones":
        "deliverables milestones target date payment schedule implementation phases statement of work milestone table",


    # ------------------------------------------------------------------
    # Termination
    # ------------------------------------------------------------------

    "termination":
        "termination notice termination for convenience termination for cause effect of termination notice period thirty sixty days",


    # ------------------------------------------------------------------
    # Confidentiality
    # ------------------------------------------------------------------

    "confidentiality":
        "confidential information confidentiality obligations non disclosure confidentiality period",


    # ------------------------------------------------------------------
    # Liability
    # ------------------------------------------------------------------

    "liability":
        "limitation of liability damages liability cap indirect damages consequential damages",


    # ------------------------------------------------------------------
    # Governing Law
    # ------------------------------------------------------------------

    "governing_law":
        "governing law jurisdiction arbitration dispute resolution applicable law",


    # ------------------------------------------------------------------
    # Intellectual Property
    # ------------------------------------------------------------------

    "intellectual_property":
        "intellectual property ownership deliverables client materials provider pre existing intellectual property",


    # ------------------------------------------------------------------
    # SLA
    # ------------------------------------------------------------------

    "sla":
        "service level agreement response time resolution time severity schedule b",


    # ------------------------------------------------------------------
    # Validation (placeholder)
    # ------------------------------------------------------------------

    "validation_notes":
        "entire contract"
}