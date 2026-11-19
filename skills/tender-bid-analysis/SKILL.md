---
name: tender-bid-analysis
description: Analyze Chinese tender/bidding documents, especially PDF tender files, and create or update a bid-ready Word brief. Use for requests to sort project background, scope, bidder instructions, qualification thresholds, evaluation method, mandatory submission materials, disqualification/invalid-bid risks, electronic-bidding controls, bid pricing rules, or bid preparation checklists.
---

# Tender Bid Analysis

Produce an operator-ready tender analysis, not a chapter-by-chapter paraphrase. The output must tell the bid team what to decide, prepare, submit, check, and avoid.

## Required workflow

1. Read the `pdf` skill for source PDFs and the `documents` skill for a Word deliverable. Use the bundled workspace runtime.
2. Extract all source text, inspect the table of contents and all pages carrying project data, bidder instructions, qualification appendices, evaluation rules, contract terms, employer requirements, and submission forms. Visually inspect source pages whenever extraction is ambiguous.
3. Maintain a fact ledger with source PDF page numbers. Reconcile conflicting dates, limits, or scope statements before drafting.
4. Create or update the Word document in the same folder as the tender source unless the user specifies another location. Preserve an existing document's style when updating it.
5. Render the finished DOCX and inspect every page. Do not ship a document with split/clipped tables, stranded table headers, unreadable Chinese text, or missing checklist rows.

## Required deliverable content

Use the schema in [references/tender-brief-schema.md](references/tender-brief-schema.md). Unless the tender lacks the relevant information, include:

- Project identity, construction scale, funding, schedule, contacts, and critical dates.
- Scope, lots/packages, service or work boundaries, interfaces, and on-site requirements.
- Applicable standards, contract obligations, payment, performance security, and delivery/acceptance requirements.
- Bidder qualifications: legal form, licences, enterprise and personnel experience, social-security/registration requirements, credit restrictions, and joint-bid rules.
- Evaluation method and a practical score-winning strategy.
- Bidder instructions: submission route, bid validity, pricing/ceiling price, bid security, opening, clarification, award, and contract signing.
- A materials checklist separated into first envelope/business-technical, second envelope/price, and post-award materials where applicable.
- A disqualification/invalid-bid checklist that separates (a) explicit tender consequences from (b) prudent operational controls.
- An electronic-bidding control checklist covering account, enterprise CA/e-seal, signing authority, tool version, file generation, encryption, upload receipt, decryption, opening attendance, and backups.

## High-risk analysis rules

### Evidence and wording

- State an exact tender consequence only where the tender says “reject”, “deny/negate”, “invalid”, “deemed withdrawn”, “not accepted”, or equivalent. Cite the source page in the Word text or its source-location section.
- Do not call a general best practice an automatic disqualification. Label it “operational control” or “anti-collusion precaution”.
- For IP address, device, network, software-lock/CA, remote desktop, and document-production controls: first search the tender for an explicit rule. If absent, say so. Then describe the anti-collusion risk only as a preventive measure, grounded in the tender's collusion provisions and applicable platform rules.
- Never advise concealment or evasion of platform, IP, device, CA, or anti-collusion checks. Require independent bid preparation, authorized company accounts and certificates, and traceable internal records.

### Mandatory response review

Treat the following as a final gate whenever applicable: correct envelope separation; required forms; valid signatory/e-seal; complete qualification evidence; truthful, internally consistent personnel/experience/credit evidence; compliant guarantee; deadline and encryption; full substantive response; bid price within ceiling; unique bid/price; required attendance and decryption; timely response to formal clarification.

### Electronic-bidding control review

- Use the platform-designated current bid-production tool and the bidding entity's own valid CA/e-seal. Confirm the encryption and opening/decryption certificates match the platform requirements.
- Do not share certificates, seals, accounts, bid-production operators, remote-control sessions, templates containing another bidder's data, bid-security payment accounts, or bid files with another bidder.
- Use a dedicated, stable computer and network for the bid. If a shared office network/IP is unavoidable, obtain written platform/agency guidance before submission and retain the record; do not assume the tender permits it.
- Perform an end-to-end sign/encrypt/upload/decrypt rehearsal, retain the upload receipt, and prepare a permitted backup file/device/network plan. Never replace a required file format with an improvised one.

## Deliverable standard

Lead with the decision and deadline risks. Use tables only for comparison grids and checklists. Make every checklist item actionable and, where useful, add owner/status/remark columns. In the final response, link only the requested DOCX and state that it was visually checked.
