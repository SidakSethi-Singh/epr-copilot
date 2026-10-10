from typing import List, Dict, Any, Optional

KNOWLEDGE_BASE: List[Dict[str, Any]] = [
    {
        "id": "kb001",
        "title": "EPR Statutory Framework Origin & PIBO Scope",
        "citation": "Plastic Waste Management Rules, 2016; MoEFCC Notification G.S.R. 133(E) (Schedule II)",
        "confidence": "needs_verify",
        "source_id": "gsr133e-2022",
        "clause": "Schedule II, Clause 1-3",
        "effective_from": "2022-02-16",
        "superseded_by": None,
        "retrieved_on": "2026-10-10",
        "verified_by": None,
        "verified_on": None,
        "source_url": "TODO_SOURCE",
        "text": (
            "India's Extended Producer Responsibility (EPR) for plastic packaging is governed "
            "under Schedule II of the Plastic Waste Management Rules, 2016 (as amended in 2022, 2024, "
            "and 2026). EPR shifts lifecycle responsibility for post-consumer plastic packaging "
            "waste onto four categories of entities: Producers (P), Importers (I), Brand Owners (BO), "
            "collectively known as PIBOs, and Plastic Waste Processors (PWPs). Entities must obtain "
            "registration on the centralized CPCB portal before selling or importing any packaged product."
        ),
    },
    {
        "id": "kb002",
        "title": "Obliged Entities: Producer, Importer, Brand Owner, and Sellers",
        "citation": "PWM Amendment Rules 2022 (Clause 4) & PWM Amendment Rules 2026",
        "confidence": "needs_verify",
        "source_id": "gsr133e-2022",
        "clause": "Schedule II, Clause 4",
        "effective_from": "2022-02-16",
        "superseded_by": None,
        "retrieved_on": "2026-10-10",
        "verified_by": None,
        "verified_on": None,
        "source_url": "TODO_SOURCE",
        "text": (
            "Under the CPCB EPR framework: (1) 'Producer' means a person engaged in the manufacture "
            "or import of carry bags or multi-layered packaging or plastic sheets or like, and "
            "includes persons using plastic packaging for packaging goods. (2) 'Importer' means a person "
            "who imports plastic packaging products or products with plastic packaging. (3) 'Brand Owner' "
            "means a person or company who sells any commodity under a registered brand label or trade mark, "
            "including e-commerce marketplaces and modern trade retailers. (4) Under the 2026 amendment, "
            "'Sellers' of raw virgin plastic materials (granules, resins, pellets) must also register on the "
            "portal to track virgin resin flow from the source."
        ),
    },
    {
        "id": "kb003",
        "title": "The Packaging Categories: Categories I, II, III, IV and V",
        "citation": "Schedule II, Clause 5.1 of PWM Rules (MoEFCC Notification Feb 16, 2022)",
        "confidence": "needs_verify",
        "source_id": "gsr133e-2022",
        "clause": "Schedule II, Clause 5.1",
        "effective_from": "2022-02-16",
        "superseded_by": None,
        "retrieved_on": "2026-10-10",
        "verified_by": None,
        "verified_on": None,
        "source_url": "TODO_SOURCE",
        "text": (
            "Schedule II formally establishes plastic packaging categories: "
            "Category I: Rigid plastic packaging (containers, bottles, jars, crates, buckets, caps). "
            "Category II: Flexible plastic packaging of single layer or multilayer (more than one layer with "
            "different types of plastic), plastic sheets or covers, carry bags, sachets or pouches where "
            "all layers are made of plastic. "
            "Category III: Multilayered plastic packaging (MLP) having at least one layer of plastic and at "
            "least one layer of material other than plastic (such as paper, aluminium foil, cardboard, etc.). "
            "Category IV: Plastic sheets or carry bags made of compostable plastics conforming to IS/ISO 17088. "
            "Category V: Biodegradable plastic packaging certified as biodegradable."
        ),
    },
    {
        "id": "kb004",
        "title": "Category II (Flexible) vs Category III (Multi-layered MLP) Boundary",
        "citation": "Schedule II, Clause 5.1 (Category II & III Definitions)",
        "confidence": "needs_verify",
        "source_id": "gsr133e-2022",
        "clause": "Schedule II, Clause 5.1",
        "effective_from": "2022-02-16",
        "superseded_by": None,
        "retrieved_on": "2026-10-10",
        "verified_by": None,
        "verified_on": None,
        "source_url": "TODO_SOURCE",
        "text": (
            "The statutory legal boundary between Category II and Category III is strictly determined by "
            "layer composition: If a multilayer packaging consists EXCLUSIVELY of plastic polymers "
            "(e.g., LDPE laminated with HDPE or BOPP), it falls under Category II (Flexible). If the packaging "
            "contains at least ONE NON-PLASTIC layer (e.g., aluminium foil in chip pouches, paperboard in "
            "beverage cartons, metallized paper), it is classified as Category III (Multilayered Plastic Packaging). "
            "Recycling targets and credit trading prices differ significantly between these two categories."
        ),
    },
    {
        "id": "kb005",
        "title": "Category IV Compostable Plastic Requirements",
        "citation": "Schedule II, Clause 5.1 (Category IV) & PWM Rule 4(h)",
        "confidence": "needs_verify",
        "source_id": "gsr133e-2022",
        "clause": "Schedule II, Clause 5.1",
        "effective_from": "2022-02-16",
        "superseded_by": None,
        "retrieved_on": "2026-10-10",
        "verified_by": None,
        "verified_on": None,
        "source_url": "TODO_SOURCE",
        "text": (
            "Category IV covers packaging and carry bags made exclusively from compostable plastics. "
            "To qualify, manufacturers and brand owners must obtain a certificate from the Central "
            "Pollution Control Board (CPCB) certifying compliance with Indian Standard IS/ISO 17088 "
            "('Specifications for Compostable Plastics'). Compostable packaging has a 100% end-of-life "
            "disposal mandate via industrial composting facilities rather than standard mechanical recycling."
        ),
    },
    {
        "id": "kb006",
        "title": "Annual EPR Collection Obligation Formula",
        "citation": "Schedule II, Clause 7 (EPR Target Calculation)",
        "confidence": "needs_verify",
        "source_id": "gsr133e-2022",
        "clause": "Schedule II, Clause 7",
        "effective_from": "2022-02-16",
        "superseded_by": None,
        "retrieved_on": "2026-10-10",
        "verified_by": None,
        "verified_on": None,
        "source_url": "TODO_SOURCE",
        "text": (
            "The EPR collection obligation target Q for a PIBO is calculated based on the average weight of plastic "
            "packaging introduced into the market in the preceding two financial years (plus imported plastic). "
            "The graduated national collection targets are: 35% for FY 2021-22, 70% for FY 2022-23, and "
            "100% for FY 2023-24 and all subsequent financial years (including FY 2024-25, 2025-26, 2026-27 onwards). "
            "PIBOs must fulfill 100% of their introduced plastic packaging target Q through recycling or credits."
        ),
    },
    {
        "id": "kb007",
        "title": "Mandatory Recycling Target Schedule (% of EPR Obligation)",
        "citation": "Schedule II, Clause 7.2 (Recycling Targets by Category)",
        "confidence": "needs_verify",
        "source_id": "gsr133e-2022",
        "clause": "Schedule II, Clause 7.2",
        "effective_from": "2022-02-16",
        "superseded_by": None,
        "retrieved_on": "2026-10-10",
        "verified_by": None,
        "verified_on": None,
        "source_url": "TODO_SOURCE",
        "text": (
            "Out of the total EPR target Q, PIBOs must ensure minimum recycling percentages by category: "
            "Category I (Rigid): 50% in 2024-25, 60% in 2025-26, 70% in 2026-27, 80% in 2027-28, 80% in 2028-29. "
            "Category II (Flexible): 30% in 2024-25, 40% in 2025-26, 50% in 2026-27, 60% in 2027-28, 60% in 2028-29. "
            "Category III (MLP): 30% in 2024-25, 40% in 2025-26, 50% in 2026-27, 60% in 2027-28, 60% in 2028-29. "
            "Category IV (Compostable): 50% in 2024-25, 60% in 2025-26, 70% in 2026-27, 80% in 2027-28, 80% in 2028-29. "
            "Category V (Biodegradable): statutory recycling target pending separate notification."
        ),
    },
    {
        "id": "kb008",
        "title": "Mandatory Use of Recycled Plastic Content (Schedule II, Clause 7.3)",
        "citation": "Schedule II, Clause 7.3 & PWM Amendment 2022",
        "confidence": "needs_verify",
        "source_id": "gsr133e-2022",
        "clause": "Schedule II, Clause 7.3",
        "effective_from": "2022-02-16",
        "superseded_by": None,
        "retrieved_on": "2026-10-10",
        "verified_by": None,
        "verified_on": None,
        "source_url": "TODO_SOURCE",
        "text": (
            "Brand Owners and Producers must incorporate statutory minimum recycled plastic content: "
            "Category I (Rigid): 30% in 2025-26, 40% in 2026-27, 50% in 2027-28, 60% in 2028-29. "
            "Category II (Flexible): 10% in 2025-26, 10% in 2026-27, 20% in 2027-28, 20% in 2028-29. "
            "Category III (MLP): 5% in 2025-26, 5% in 2026-27, 10% in 2027-28, 10% in 2028-29 (calculated on weight of plastic layers only). "
            "Category IV (Compostable): 0% across all years. "
            "Category V (Biodegradable): mandate pending separate notification."
        ),
    },
    {
        "id": "kb009",
        "title": "EPR Certificates, Trading Portal & Market Pricing",
        "citation": "CPCB EPR Portal Guidelines & Trading Mechanism",
        "confidence": "needs_verify",
        "source_id": "gsr133e-2022",
        "clause": "Schedule II, Clause 9",
        "effective_from": "2022-02-16",
        "superseded_by": None,
        "retrieved_on": "2026-10-10",
        "verified_by": None,
        "verified_on": None,
        "source_url": "TODO_SOURCE",
        "text": (
            "PIBOs satisfy obligations by acquiring digital EPR certificates issued online by CPCB-registered PWPs. "
            "Certificates are category-specific: Category I certificates cannot offset Category II or III deficits. "
            "Current estimated certificate price ranges per MT are: "
            "Category I: Rs 3,500 to Rs 8,000 per MT. "
            "Category II: Rs 6,000 to Rs 14,000 per MT. "
            "Category III: Rs 8,000 to Rs 20,000 per MT. "
            "Category IV: Rs 4,000 to Rs 10,000 per MT."
        ),
    },
    {
        "id": "kb010",
        "title": "Producer Responsibility Organisation (PRO) Role & Limits",
        "citation": "Schedule II, Clause 12 (Role of PRO)",
        "confidence": "needs_verify",
        "source_id": "gsr133e-2022",
        "clause": "Schedule II, Clause 12",
        "effective_from": "2022-02-16",
        "superseded_by": None,
        "retrieved_on": "2026-10-10",
        "verified_by": None,
        "verified_on": None,
        "source_url": "TODO_SOURCE",
        "text": (
            "A Producer Responsibility Organisation (PRO) may be engaged by PIBOs to assist with collection, "
            "logistics, and recycler coordination. However, under statutory rules, the legal liability for "
            "compliance and filing remains solely with the PIBO. A PRO cannot register on behalf of a PIBO as the "
            "obligated entity, nor can contractual indemnity protect a PIBO from CPCB prosecution or fines."
        ),
    },
    {
        "id": "kb011",
        "title": "Annual EPR Return Filing Deadlines & Extension Circulars",
        "citation": "Schedule II, Clause 11.3 & MoEFCC Notice 2026-08-28",
        "confidence": "needs_verify",
        "source_id": "moefcc-ext-2026-08-28",
        "clause": "Schedule II, Clause 11.3",
        "effective_from": "2022-02-16",
        "superseded_by": None,
        "retrieved_on": "2026-10-10",
        "verified_by": None,
        "verified_on": None,
        "source_url": "TODO_SOURCE",
        "text": (
            "Under statutory Rule 11.3, the statutory annual return date for filing on the CPCB portal is June 30 (06-30). "
            "Under the MoEFCC annual return extension notice dated 2026-08-28 for FY 2025-26: "
            "the deadline for Plastic Waste Processors (PWP) is 2026-10-31, and "
            "the deadline for PIBOs (Producers, Importers, Brand Owners) is 2026-12-31."
        ),
    },
    {
        "id": "kb012",
        "title": "Mandatory QR Code and Barcode Labeling Mandate (Rule 11)",
        "citation": "PWM (Amendment) Rules, 2025, Rule 11 & March 2026 Notification",
        "confidence": "needs_verify",
        "source_id": "gsr133e-2022",
        "clause": "Rule 11",
        "effective_from": "2025-07-01",
        "superseded_by": None,
        "retrieved_on": "2026-10-10",
        "verified_by": None,
        "verified_on": None,
        "source_url": "TODO_SOURCE",
        "text": (
            "Under Rule 11 of the Plastic Waste Management Rules, all PIBOs must print a scannable on-pack "
            "QR code, barcode, or unique digital identifier on each packaging unit. The code must encode: "
            "(1) CPCB EPR Registration number, (2) Plastic packaging category (Cat I/II/III/IV), (3) Virgin vs recycled "
            "plastic percentage, and (4) Recycler/Manufacturer credentials. Enforcement commenced July 1, 2025."
        ),
    },
    {
        "id": "kb013",
        "title": "Environmental Compensation (EC) Regime & Refund Formula",
        "citation": "Schedule II, Clause 10 & CPCB EC Guidelines 2024-04-04",
        "confidence": "needs_verify",
        "source_id": "cpcb-ec-2024-04-04",
        "clause": "Schedule II, Clause 10",
        "effective_from": "2024-04-04",
        "superseded_by": None,
        "retrieved_on": "2026-10-10",
        "verified_by": None,
        "verified_on": None,
        "source_url": "TODO_SOURCE",
        "text": (
            "Under Section 15 of the EPA 1986 and Schedule II Clause 10, CPCB levies Environmental Compensation (EC). "
            "The statutory EC rates per MT by consecutive year of shortfall are: "
            "Rs 5,000 per MT for year 1, Rs 10,000 per MT for year 2, and Rs 20,000 per MT for year 3 onwards. "
            "Unfulfilled targets carry forward. If the deficit target is fulfilled within the window, the refund percentages are: "
            "75% refund within 1 year of fulfilment, 60% refund within 2 years, and 40% refund within 3 years. "
            "After 3 years, 0% refund is returned and the amount is forfeited."
        ),
    },
    {
        "id": "kb014",
        "title": "Penalties, Plant Closures and Registered Environmental Auditors",
        "citation": "PWM Amendment 2026 & EPA 1986 Section 15",
        "confidence": "needs_verify",
        "source_id": "gsr133e-2022",
        "clause": "Schedule II, Clause 13",
        "effective_from": "2026-03-01",
        "superseded_by": None,
        "retrieved_on": "2026-10-10",
        "verified_by": None,
        "verified_on": None,
        "source_url": "TODO_SOURCE",
        "text": (
            "Penalties for willful evasion, fraudulent EPR certificates, or operating without CPCB registration include: "
            "(1) Monetary EC fines assessed per MT of unfulfilled obligation plus daily delay fines; "
            "(2) Revocation of Consent to Operate (CTO) and customs clearance seizure for importers; (3) Mandatory audit "
            "inspections by CPCB-empanelled Registered Environment Auditors (introduced in March 2026 amendment); and "
            "(4) Criminal prosecution under Section 15 of EPA 1986 with imprisonment up to 5 years for repeated defiance."
        ),
    },
    {
        "id": "kb015",
        "title": "EPR for Packaging Rules, 2024: Non-Plastic Expansion (Effective April 2026)",
        "citation": "Environment Protection (EPR for Packaging) Rules, 2024",
        "confidence": "needs_verify",
        "source_id": "gsr133e-2022",
        "clause": "EPR Packaging Rules 2024",
        "effective_from": "2026-04-01",
        "superseded_by": None,
        "retrieved_on": "2026-10-10",
        "verified_by": None,
        "verified_on": None,
        "source_url": "TODO_SOURCE",
        "text": (
            "The Environment Protection (EPR for Packaging) Rules, 2024 expand EPR obligations beyond plastics. "
            "Effective April 1, 2026, brand owners and manufacturers packaging goods in paper, glass, and metal "
            "must register and report on a unified portal. Separate EPR frameworks also apply to scrap non-ferrous "
            "metals (copper, aluminium, zinc) and construction/demolition waste, creating a unified industrial packaging regime."
        ),
    },
    {
        "id": "kb016",
        "title": "CPCB EPR Portal Step-by-Step Registration Checklist",
        "citation": "CPCB SOP for PIBO Registration (Form I)",
        "confidence": "needs_verify",
        "source_id": "gsr133e-2022",
        "clause": "Schedule II, Clause 6",
        "effective_from": "2022-02-16",
        "superseded_by": None,
        "retrieved_on": "2026-10-10",
        "verified_by": None,
        "verified_on": None,
        "source_url": "TODO_SOURCE",
        "text": (
            "PIBO registration on the centralized CPCB portal requires: (1) Company PAN, GST, and CIN; "
            "(2) Valid Consent to Establish (CTE) and Consent to Operate (CTO) issued by State Pollution Control Board "
            "(SPCB/PCC) for production facilities; (3) IEC (Import Export Code) for Importers; (4) Process flow diagrams "
            "and declared packaging specifications; (5) District Industries Centre (DIC) / MSME registration if claiming "
            "small-scale status. Operating without registration attracts immediate customs holds and portal blacklisting."
        ),
    },
    {
        "id": "kb017",
        "title": "Single-Use Plastics (SUP) Ban & 120-Micron Carry Bag Threshold",
        "citation": "PWM (Amendment) Rules, 2021 (G.S.R. 571(E)) & Notification dated Aug 12, 2021",
        "confidence": "needs_verify",
        "source_id": "gsr133e-2022",
        "clause": "Rule 4",
        "effective_from": "2022-07-01",
        "superseded_by": None,
        "retrieved_on": "2026-10-10",
        "verified_by": None,
        "verified_on": None,
        "source_url": "TODO_SOURCE",
        "text": (
            "Effective July 1, 2022, India banned 19 identified Single-Use Plastic (SUP) items with low utility and "
            "high littering potential, including: plastic ear buds, balloon sticks, candy/ice-cream sticks, thermocol "
            "(polystyrene) for decoration, plates, cups, glasses, cutlery (forks, spoons, knives, straws, trays), "
            "wrapping films around sweet boxes, invitation cards, cigarette packets, and plastic PVC banners less than "
            "100 microns. Furthermore, virgin or recycled plastic carry bags must have a minimum thickness of 120 microns. "
            "Non-woven plastic carry bags must not be less than 60 grams per square meter (GSM)."
        ),
    },
    {
        "id": "kb018",
        "title": "Plastic Waste Processors (PWP) Protocols & Digital Credit Generation",
        "citation": "Schedule II, Clause 11 (Plastic Waste Processors) & CPCB Circulars on PWP Registration",
        "confidence": "needs_verify",
        "source_id": "gsr133e-2022",
        "clause": "Schedule II, Clause 11",
        "effective_from": "2022-02-16",
        "superseded_by": None,
        "retrieved_on": "2026-10-10",
        "verified_by": None,
        "verified_on": None,
        "source_url": "TODO_SOURCE",
        "text": (
            "Plastic Waste Processors (PWPs) — including recyclers, waste-to-energy operators, co-processors in cement kilns, "
            "and plastic-to-oil facilities — must register independently on the CPCB portal. PWPs generate digital EPR "
            "certificates proportional to the physical quantity of plastic packaging waste processed. These certificates "
            "are traded or transferred to PIBOs to fulfill annual recycling obligations. Portal rules strictly prohibit "
            "double-counting: certificates must reference actual electricity consumption, GST sales invoices, and weighbridge "
            "records. Unregistered recyclers cannot issue statutory EPR credits."
        ),
    },
    {
        "id": "kb019",
        "title": "Brand Owner MSME Exemptions & Small Entity Thresholds",
        "citation": "Schedule II, Clause 5.2 (Exemptions) of PWM Rules 2016",
        "confidence": "needs_verify",
        "source_id": "gsr133e-2022",
        "clause": "Schedule II, Clause 5.2",
        "effective_from": "2022-02-16",
        "superseded_by": None,
        "retrieved_on": "2026-10-10",
        "verified_by": None,
        "verified_on": None,
        "source_url": "TODO_SOURCE",
        "text": (
            "Under Schedule II, Micro and Small Enterprises (as defined under the MSMED Act, 2006: investment in plant & machinery "
            "up to Rs 1 crore and turnover up to Rs 5 crore for Micro; investment up to Rs 10 crore and turnover up to Rs 50 crore for Small) "
            "who are Brand Owners are exempt from mandatory recycling obligations and recycled content targets. However, Medium and "
            "Large brand owners have zero exemption. Crucially, even exempt micro/small brand owners must not use banned SUP items or "
            "carry bags thinner than 120 microns."
        ),
    },
    {
        "id": "kb020",
        "title": "Central CPCB vs State SPCB / PCC Jurisdictional Boundaries",
        "citation": "Schedule II, Clause 6 (Registration Process) & Rule 13 of PWM Rules",
        "confidence": "needs_verify",
        "source_id": "gsr133e-2022",
        "clause": "Schedule II, Clause 6",
        "effective_from": "2022-02-16",
        "superseded_by": None,
        "retrieved_on": "2026-10-10",
        "verified_by": None,
        "verified_on": None,
        "source_url": "TODO_SOURCE",
        "text": (
            "Jurisdiction for EPR registration is determined by the geographic footprint of operations: (1) Any Producer, "
            "Importer, or Brand Owner operating in more than two States or Union Territories must register with the Central "
            "Pollution Control Board (CPCB) on the national portal. (2) Entities operating in only one or two States/UTs must "
            "register with the respective State Pollution Control Board (SPCB) or Pollution Control Committee (PCC). (3) Once "
            "registered with CPCB, separate state-level registrations are not required, establishing a single-window compliance mechanism."
        ),
    },
    {
        "id": "kb021",
        "title": "End-of-Life Disposal Mandates for Non-Recyclable Category II & III Plastics",
        "citation": "Schedule II, Clause 8 & IRC SP:98 Guidelines",
        "confidence": "needs_verify",
        "source_id": "gsr133e-2022",
        "clause": "Schedule II, Clause 8",
        "effective_from": "2022-02-16",
        "superseded_by": None,
        "retrieved_on": "2026-10-10",
        "verified_by": None,
        "verified_on": None,
        "source_url": "TODO_SOURCE",
        "text": (
            "Plastic packaging waste that cannot be mechanically recycled — especially contaminated flexible plastics (Category II) "
            "and multilayered packaging (Category III) — must be diverted to authorized end-of-life disposal channels: (1) Co-processing "
            "in cement kilns as alternative fuel and raw material (AFR); (2) Waste-to-Energy (WtE) combustion plants complying with "
            "emission standards; (3) Plastic-to-fuel (pyrolysis) plants; or (4) Polymer-modified bituminous road construction under "
            "Indian Roads Congress guideline IRC SP:98. Disposal in landfills attracts maximum Environmental Compensation penalties."
        ),
    },
    {
        "id": "kb022",
        "title": "Cross-Compliance Boundaries: Battery (BWMR) and E-Waste EPR Rules",
        "citation": "Battery Waste Management Rules, 2022 & E-Waste (Management) Rules, 2022",
        "confidence": "needs_verify",
        "source_id": "gsr133e-2022",
        "clause": "Cross-Regime Framework",
        "effective_from": "2022-08-24",
        "superseded_by": None,
        "retrieved_on": "2026-10-10",
        "verified_by": None,
        "verified_on": None,
        "source_url": "TODO_SOURCE",
        "text": (
            "India enforces distinct, non-fungible EPR regimes for different waste streams. Packaging of electronic products or "
            "batteries is governed under Plastic Waste Management Rules (Schedule II). However, the internal electronic device or "
            "battery itself is governed under separate statutory notifications: (1) Battery Waste Management Rules, 2022 for all "
            "portable, automotive, and industrial batteries; (2) E-Waste (Management) Rules, 2022 for electronic equipment. Compliance "
            "credits from plastic EPR cannot offset battery or e-waste recycling deficits, and distinct portal filings are required."
        ),
    },
    {
        "id": "kb023",
        "title": "Category V: Biodegradable Plastic Packaging Specifications",
        "citation": "PWM Amendment Rules & Schedule II Category V Scope Note",
        "confidence": "needs_verify",
        "source_id": "gsr133e-2022",
        "clause": "Schedule II, Clause 5.1(e)",
        "effective_from": "2022-02-16",
        "superseded_by": None,
        "retrieved_on": "2026-10-10",
        "verified_by": None,
        "verified_on": None,
        "source_url": "TODO_SOURCE",
        "text": (
            "Category V plastic packaging covers biodegradable plastics other than compostable plastics. "
            "Statutory recycling minimum percentages and recycled content mandates for Category V remain null and "
            "subject to separate notification by CPCB and MoEFCC. Entities manufacturing or utilizing Category V materials "
            "must register on the portal and maintain certified laboratory test documentation confirming biodegradation criteria."
        ),
    },
    {
        "id": "kb024",
        "title": "Mandatory Reuse Obligations for Category I Rigid Plastics",
        "citation": "Schedule II, Clause 7.1 (Obligation for Reuse)",
        "confidence": "needs_verify",
        "source_id": "gsr133e-2022",
        "clause": "Schedule II, Clause 7.1",
        "effective_from": "2022-02-16",
        "superseded_by": None,
        "retrieved_on": "2026-10-10",
        "verified_by": None,
        "verified_on": None,
        "source_url": "TODO_SOURCE",
        "text": (
            "Under Schedule II Clause 7.1, Brand Owners utilizing Category I rigid plastic packaging have mandatory reuse obligations. "
            "Brand owners must ensure minimum reuse percentages for rigid packaging products introduced into the market across successive "
            "financial years, establishing refillable systems, reverse logistics deposit-return mechanisms, and audited reuse declarations."
        ),
    },
    {
        "id": "kb025",
        "title": "Carry-Forward of Unfulfilled EPR Obligations Across Three Years",
        "citation": "Schedule II, Clause 10.3 & CPCB EC Guidelines",
        "confidence": "needs_verify",
        "source_id": "cpcb-ec-2024-04-04",
        "clause": "Schedule II, Clause 10.3",
        "effective_from": "2024-04-04",
        "superseded_by": None,
        "retrieved_on": "2026-10-10",
        "verified_by": None,
        "verified_on": None,
        "source_url": "TODO_SOURCE",
        "text": (
            "Unfulfilled EPR recycling obligations are carried forward for up to 3 consecutive years. "
            "To qualify for carry-forward without forfeiture, an obligated entity must cure at least one third of the accumulated "
            "deficit per year. Failure to cure at least one third per year or lingering deficits beyond 3 consecutive years result in "
            "permanent forfeiture of Environmental Compensation and escalation to year-3 penalty rates."
        ),
    },
    {
        "id": "kb026",
        "title": "End-of-Life Disposal Share and Non-Recycled Remainder Obligation",
        "citation": "Schedule II, Clause 7.4 & Clause 8 (End-of-Life Disposal)",
        "confidence": "needs_verify",
        "source_id": "gsr133e-2022",
        "clause": "Schedule II, Clause 7.4",
        "effective_from": "2022-02-16",
        "superseded_by": None,
        "retrieved_on": "2026-10-10",
        "verified_by": None,
        "verified_on": None,
        "source_url": "TODO_SOURCE",
        "text": (
            "Any portion of the total EPR target Q remaining after fulfilling the mandatory recycling obligation is not exempt. "
            "The remaining non-recycled tonnage must be completely addressed through authorized end-of-life disposal routes: "
            "waste-to-energy incineration, cement co-processing, or road construction. Landfill dumping remains illegal and strictly penalized."
        ),
    },
    {
        "id": "kb027",
        "title": "Common EPR Portal Migration and Unified Reporting",
        "citation": "CPCB Circular on Common EPR Portal Integration",
        "confidence": "needs_verify",
        "source_id": "gsr133e-2022",
        "clause": "Portal Migration Circular",
        "effective_from": "2026-01-01",
        "superseded_by": None,
        "retrieved_on": "2026-10-10",
        "verified_by": None,
        "verified_on": None,
        "source_url": "TODO_SOURCE",
        "text": (
            "The CPCB centralized portal is undergoing migration to the Common EPR Portal, bringing together plastic packaging, "
            "e-waste, battery waste, and non-plastic packaging under a single sign-on architecture. Registered entities must verify "
            "their unified portal credentials, map existing GST numbers, and ensure all PWP certificates are registered in the migrated system."
        ),
    },
]
