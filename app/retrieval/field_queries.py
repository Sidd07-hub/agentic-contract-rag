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
        "contract number agreement number master services agreement identifier document reference MSA reference number",

    "effective_date":
        "effective date date entered into agreement commencement date execution date this agreement is entered into",

    "term_months":
        "initial term contract duration agreement period number of months renewal term term of this agreement",


    # ------------------------------------------------------------------
    # Provider Party
    # ------------------------------------------------------------------

    "parties.provider.legal_name":
        "provider company name service provider entity legal name party hereinafter referred to as provider",

    "parties.provider.address":
        "provider address registered office principal place of business provider located at",

    "parties.provider.signatory_name":
        "provider signatory authorised representative signed by on behalf of provider name signature block",

    "parties.provider.signatory_title":
        "provider signatory title designation chief officer director on behalf of provider title role",


    # ------------------------------------------------------------------
    # Client Party
    # ------------------------------------------------------------------

    "parties.client.legal_name":
        "client company name customer entity legal name party hereinafter referred to as client",

    "parties.client.address":
        "client address registered office principal place of business client located at",

    "parties.client.signatory_name":
        "client signatory authorised representative signed by on behalf of client name signature block",

    "parties.client.signatory_title":
        "client signatory title designation chief officer director on behalf of client title role",


    # ------------------------------------------------------------------
    # Parent-level fallbacks (used if a sub-field query is missing)
    # ------------------------------------------------------------------

    "parties":
        "parties provider client legal name registered office principal place of business address signatory authorised representative",


    # ------------------------------------------------------------------
    # Fees
    # ------------------------------------------------------------------

    "fees.headline_fee":
        "headline fee sticker price base fee professional services fee total fee amount",

    "fees.total_payable":
        "total payable amount total fees inclusive surcharges one-time fees actual total amount client will pay initial term",

    "fees.currency":
        "currency USD INR EUR GBP payment denomination",

    "fees.reimbursement_cap.amount":
        "reimbursement cap amount expense cap maximum reimbursable out-of-pocket expenses",

    "fees.reimbursement_cap.currency":
        "reimbursement cap currency expense denomination",

    "fees.reimbursement_cap.period":
        "reimbursement cap period per annum per year calendar year expense period",

    "fees":
        "payment fees pricing headline fee total payable reimbursement expenses taxes currency invoice payment schedule",


    # ------------------------------------------------------------------
    # Deliverables / Milestones
    # ------------------------------------------------------------------

    "milestones":
        "deliverables milestones milestone table target date payment schedule implementation phases statement of work milestone deliverable fee percentage payment released",


    # ------------------------------------------------------------------
    # Termination
    # ------------------------------------------------------------------

    "termination.notice_days_general":
        "general termination notice period days written notice termination for convenience termination of agreement",

    "termination.notice_days_managed_services":
        "managed services termination notice period days managed services termination clause specific notice",

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
    # Validation (uses broad query to get diverse context)
    # ------------------------------------------------------------------

    "validation_notes":
        "entire contract agreement terms conditions parties fees milestones termination",
}