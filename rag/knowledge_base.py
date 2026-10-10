"""
Statutory Knowledge Base for EPR Compliance Copilot.

Derived from:
  - Plastic Waste Management Rules, 2016 (and amendments 2018, 2021, 2022, 2023, 2024, 2026)
  - Schedule II: Guidelines on Extended Producer Responsibility for Plastic Packaging (G.S.R. 133(E))
  - CPCB Guidelines on Assessment and Collection of Environmental Compensation (4 Apr 2024)
  - MoEFCC Annual Return Extension Notification (28 Aug 2026)
  - CPCB Technical Guidelines for Co-processing Plastic Waste in Cement Kilns (2021)
  - MNRE / CPCB Waste-to-Energy (WtE) Benchmark Specifications (2022)

Each chunk is tagged with confidence:
  - 'verified': Checked against official Gazette notification or CPCB order
  - 'reported': Sourced from secondary reporting or regulatory advisories
  - 'needs_verify': Proposed/draft rules or unresolved variations
"""

KNOWLEDGE_BASE = [
    {
        "id": "kb001",
        "title": "EPR Statutory Framework Origin & PIBO Scope",
        "citation": "Plastic Waste Management Rules, 2016, Rule 3 & Schedule II Clause 1-3",
        "confidence": "verified",
        "effective_from": "2022-02-16",
        "source_url": "https://cpcb.nic.in/plastic-waste-rules/",
        "superseded_by": None,
        "retrieved_on": "2026-10-10",
        "verified_by": "Statutory Review Team",
        "text": (
            "Extended Producer Responsibility (EPR) for plastic packaging in India is legally mandated under the "
            "Plastic Waste Management Rules, 2016, through Schedule II inserted via G.S.R. 133(E) dated 16 February 2022. "
            "The regime applies mandatorily to four classes of entities operating across the value chain: "
            "(1) Producers (P) of plastic packaging, (2) Importers (I) of plastic packaging or products with plastic packaging, "
            "(3) Brand Owners (BO) including online platforms and retailers, and (4) Plastic Waste Processors (PWPs) including "
            "recyclers and waste-to-energy operators. All must register on the CPCB centralized portal."
        ),
    },
    {
        "id": "kb002",
        "title": "Obliged Entities: Producer, Importer, Brand Owner, and Sellers",
        "citation": "Schedule II, Clause 3 & PWM (Amendment) Rules, 2024",
        "confidence": "verified",
        "effective_from": "2024-03-15",
        "source_url": "https://cpcb.nic.in/pibo-registration/",
        "superseded_by": None,
        "retrieved_on": "2026-10-10",
        "verified_by": "Statutory Review Team",
        "text": (
            "Entity classifications under Schedule II: A Producer is any person manufacturing virgin or recycled plastic packaging. "
            "An Importer is any person importing plastic packaging products or products packed in plastic. A Brand Owner is a person "
            "selling goods under a registered brand label. In 2024, the definition was expanded to include raw material suppliers ('Sellers') "
            "who supply polymer resin or granules to unregistered converters. Sellers are barred from supplying plastic raw materials "
            "to any producer or brand owner who lacks a valid CPCB registration certificate."
        ),
    },
    {
        "id": "kb003",
        "title": "The Four Official Packaging Categories (Categories I, II, III, IV)",
        "citation": "Schedule II, Clause 5 (Packaging Categories)",
        "confidence": "verified",
        "effective_from": "2022-02-16",
        "source_url": "https://cpcb.nic.in/plastic-waste-rules/",
        "superseded_by": None,
        "retrieved_on": "2026-10-10",
        "verified_by": "Statutory Review Team",
        "text": (
            "Plastic packaging is classified into four statutory categories under Schedule II: "
            "Category I: Rigid plastic packaging (e.g. HDPE, PET bottles, containers, crates). "
            "Category II: Flexible plastic packaging of single or multilayered polymer sheets without non-plastic layers (e.g. LDPE, PP pouches). "
            "Category III: Multilayered plastic packaging (MLP) containing at least one layer of a material other than plastic, such as aluminium foil or paper. "
            "Category IV: Plastic sheet or like used for packaging as well as carry bags made of compostable plastics conforming to IS/ISO 17088."
        ),
    },
    {
        "id": "kb004",
        "title": "Category II (Flexible) vs Category III (Multi-layered MLP) Boundary",
        "citation": "Schedule II, Clause 5.1(b) and Clause 5.1(c)",
        "confidence": "verified",
        "effective_from": "2022-02-16",
        "source_url": "https://cpcb.nic.in/plastic-waste-rules/",
        "superseded_by": None,
        "retrieved_on": "2026-10-10",
        "verified_by": "Statutory Review Team",
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
        "confidence": "verified",
        "effective_from": "2022-02-16",
        "source_url": "https://cpcb.nic.in/plastic-waste-rules/",
        "superseded_by": None,
        "retrieved_on": "2026-10-10",
        "verified_by": "Statutory Review Team",
        "text": (
            "Category IV covers packaging and carry bags made exclusively from compostable plastics. "
            "To qualify, manufacturers and brand owners must obtain a certificate from the Central "
            "Pollution Control Board (CPCB) certifying compliance with Indian Standard IS/ISO 17088 "
            "('Specifications for Compostable Plastics'). Under statutory guidelines, Category IV packaging "
            "follows graduated recycling/processing targets (50% in FY 2024-25, 60% in FY 2025-26, 70% in FY 2026-27, "
            "and 80% in FY 2027-28 onwards) with a 100% processing mandate via certified industrial composting facilities."
        ),
    },
    {
        "id": "kb006",
        "title": "Annual EPR Collection Obligation Formula",
        "citation": "Schedule II, Clause 7 (EPR Target Calculation)",
        "confidence": "verified",
        "effective_from": "2022-02-16",
        "source_url": "https://cpcb.nic.in/plastic-waste-rules/",
        "superseded_by": None,
        "retrieved_on": "2026-10-10",
        "verified_by": "Statutory Review Team",
        "text": (
            "The statutory EPR target obligation Q for a PIBO is determined under Schedule II Clause 7: "
            "Q = (A + B) - C, where A is the average weight of plastic packaging introduced into the market in the "
            "preceding two financial years, B is the average quantity of pre-consumer plastic packaging waste, and "
            "C is the quantity of plastic packaging supplied to brand owners or exported. "
            "The national collection targets are: 35% for FY 2021-22, 70% for FY 2022-23, and 100% for FY 2023-24 "
            "and all subsequent financial years (including FY 2024-25, 2025-26, 2026-27 onwards). "
            "PIBOs must fulfill 100% of their introduced plastic packaging weight through recycling or credits."
        ),
    },
    {
        "id": "kb007",
        "title": "Mandatory Recycling Target Schedule (% of EPR Obligation)",
        "citation": "Schedule II, Clause 7.2 (Recycling Targets by Category)",
        "confidence": "verified",
        "effective_from": "2022-02-16",
        "source_url": "https://cpcb.nic.in/plastic-waste-rules/",
        "superseded_by": None,
        "retrieved_on": "2026-10-10",
        "verified_by": "Statutory Review Team",
        "text": (
            "Out of the total EPR obligation, PIBOs must ensure minimum mechanical recycling by category: "
            "For Category I (Rigid): 50% in FY 2024-25, 60% in FY 2025-26, 70% in FY 2026-27, and 80% in FY 2027-28 onwards. "
            "For Category II (Flexible): 30% in FY 2024-25, 40% in FY 2025-26, 50% in FY 2026-27, and 60% in FY 2027-28 onwards. "
            "For Category III (MLP): 30% in FY 2024-25, 40% in FY 2025-26, 50% in FY 2026-27, and 60% in FY 2027-28 onwards. "
            "For Category IV (Compostable): 50% in FY 2024-25, 60% in FY 2025-26, 70% in FY 2026-27, and 80% in FY 2027-28 onwards. "
            "Any leftover obligation not capable of mechanical recycling must go to authorized End-of-Life disposal "
            "(Waste-to-Energy, cement co-processing, or road construction)."
        ),
    },
    {
        "id": "kb008",
        "title": "Mandatory Use of Recycled Plastic Content (Schedule II, Clause 7.3)",
        "citation": "Schedule II, Clause 7.3 & PWM Amendment Rules",
        "confidence": "verified",
        "effective_from": "2022-02-16",
        "source_url": "https://cpcb.nic.in/plastic-waste-rules/",
        "superseded_by": None,
        "retrieved_on": "2026-10-10",
        "verified_by": "Statutory Review Team",
        "text": (
            "Brand Owners and Producers must incorporate a statutory minimum percentage of recycled plastic "
            "content in their packaging: "
            "Category I (Rigid): 30% in FY 2025-26, 40% in FY 2026-27, 50% in FY 2027-28, and 60% in FY 2028-29 onwards. "
            "Category II (Flexible): 10% in FY 2025-26, 10% in FY 2026-27, 20% in FY 2027-28, and 20% in FY 2028-29 onwards. "
            "Category III (MLP): 5% in FY 2025-26, 5% in FY 2026-27, 10% in FY 2027-28, and 10% in FY 2028-29 onwards (calculated "
            "specifically on the weight of the plastic polymer layers only). Category IV compostables carry 0% recycled content mandate. "
            "Failure to meet recycled content thresholds is independently penalized under Environmental Compensation."
        ),
    },
    {
        "id": "kb009",
        "title": "EPR Certificates, Trading Portal & Market Pricing",
        "citation": "CPCB EPR Portal Guidelines & Trading Mechanism",
        "confidence": "reported",
        "effective_from": "2023-01-01",
        "source_url": "https://cpcb.nic.in/epr-portal/",
        "superseded_by": None,
        "retrieved_on": "2026-10-10",
        "verified_by": "Statutory Review Team",
        "text": (
            "PIBOs satisfy their obligation by generating recycling credits or buying digital EPR Certificates "
            "issued online by CPCB-registered Plastic Waste Processors (PWPs) via the centralized portal marketplace. "
            "Certificates are category-specific: Category I certificates cannot be used to offset Category II or III "
            "obligations. Market prices fluctuate based on category complexity: Category I typically trades at "
            "Rs 3,500 - Rs 8,000 per MT; Category II trades at Rs 6,000 - Rs 14,000 per MT; Category III trades at "
            "Rs 8,000 - Rs 20,000 per MT; Category IV trades at Rs 4,000 - Rs 10,000 per MT. Non-registered recycler "
            "certificates are void and subject to audit cancellation."
        ),
    },
    {
        "id": "kb010",
        "title": "Producer Responsibility Organisation (PRO) Role & Limits",
        "citation": "Schedule II, Clause 12 (Role of PRO)",
        "confidence": "verified",
        "effective_from": "2022-02-16",
        "source_url": "https://cpcb.nic.in/plastic-waste-rules/",
        "superseded_by": None,
        "retrieved_on": "2026-10-10",
        "verified_by": "Statutory Review Team",
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
        "citation": "Schedule II, Clause 11.3 & MoEFCC Extension Notice dated 28 August 2026",
        "confidence": "verified",
        "effective_from": "2026-08-28",
        "source_url": "https://moef.gov.in/notifications/",
        "superseded_by": None,
        "retrieved_on": "2026-10-10",
        "verified_by": "Statutory Review Team",
        "text": (
            "Under statutory Rule 11.3 and Schedule II Clause 13.1, PIBOs must file an Annual EPR Return for the preceding "
            "financial year on the CPCB portal by June 30. For FY 2025-26, MoEFCC issued an official extension notice dated "
            "28 August 2026: Plastic Waste Processors (PWPs) must file by 31 October 2026, and PIBOs must file by 31 December 2026. "
            "Filing requires audited procurement invoices, category-wise production/import figures, and matched EPR certificate numbers. "
            "Late filing attracts automatic Environmental Compensation penalties under Section 15 of EPA 1986."
        ),
    },
    {
        "id": "kb012",
        "title": "Mandatory QR Code and Barcode Labeling Mandate (Rule 11)",
        "citation": "PWM (Amendment) Rules, 2025, Rule 11 & March 2026 Notification",
        "confidence": "verified",
        "effective_from": "2025-07-01",
        "source_url": "https://cpcb.nic.in/plastic-waste-rules/",
        "superseded_by": None,
        "retrieved_on": "2026-10-10",
        "verified_by": "Statutory Review Team",
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
        "citation": "Schedule II, Clause 10, CPCB EC Guidelines (4 Apr 2024) & EPA 1986 Section 15",
        "confidence": "verified",
        "effective_from": "2024-04-04",
        "source_url": "https://cpcb.nic.in/environmental-compensation/",
        "superseded_by": None,
        "retrieved_on": "2026-10-10",
        "verified_by": "Statutory Review Team",
        "text": (
            "Under Section 15 of the EPA 1986 and Schedule II Clause 10, CPCB levies Environmental Compensation (EC) on non-compliant "
            "entities. The baseline EC rate escalates by consecutive year of default: Rs 5,000 per MT in Year 1, Rs 10,000 per MT in "
            "Year 2, and Rs 20,000 per MT in Year 3. Crucially, payment of EC does NOT waive the EPR target: unfulfilled targets "
            "carry forward for up to three consecutive years. If the deficit target is subsequently fulfilled: within 1 year, "
            "75% of the levied EC is refunded; within 2 years, 60% is refunded; within 3 years, 40% is refunded. "
            "After 3 years, the entire compensation is permanently forfeited to the National Environmental Relief Fund."
        ),
    },
    {
        "id": "kb014",
        "title": "Penalties, Plant Closures and Registered Environmental Auditors",
        "citation": "PWM Amendment 2026 & EPA 1986 Section 15",
        "confidence": "verified",
        "effective_from": "2026-03-01",
        "source_url": "https://cpcb.nic.in/plastic-waste-rules/",
        "superseded_by": None,
        "retrieved_on": "2026-10-10",
        "verified_by": "Statutory Review Team",
        "text": (
            "Penalties for willful evasion, fraudulent EPR certificates, or operating without CPCB registration include: "
            "(1) Monetary EC fines assessed at escalating rates (Rs 5,000 / Rs 10,000 / Rs 20,000 per MT) plus daily delay fines; "
            "(2) Revocation of Consent to Operate (CTO) and customs clearance seizure for importers; (3) Mandatory audit "
            "inspections by CPCB-empanelled Registered Environment Auditors; and "
            "(4) Criminal prosecution under Section 15 of EPA 1986 with imprisonment up to 5 years for repeated defiance."
        ),
    },
    {
        "id": "kb015",
        "title": "EPR for Packaging Rules, 2024: Non-Plastic Expansion (Effective April 2026)",
        "citation": "Environment Protection (EPR for Packaging) Rules, 2024",
        "confidence": "verified",
        "effective_from": "2026-04-01",
        "source_url": "https://cpcb.nic.in/non-plastic-epr/",
        "superseded_by": None,
        "retrieved_on": "2026-10-10",
        "verified_by": "Statutory Review Team",
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
        "confidence": "verified",
        "effective_from": "2022-04-05",
        "source_url": "https://cpcb.nic.in/pibo-registration/",
        "superseded_by": None,
        "retrieved_on": "2026-10-10",
        "verified_by": "Statutory Review Team",
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
        "confidence": "verified",
        "effective_from": "2022-07-01",
        "source_url": "https://cpcb.nic.in/sup-ban/",
        "superseded_by": None,
        "retrieved_on": "2026-10-10",
        "verified_by": "Statutory Review Team",
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
        "confidence": "verified",
        "effective_from": "2022-02-16",
        "source_url": "https://cpcb.nic.in/pwp-guidelines/",
        "superseded_by": None,
        "retrieved_on": "2026-10-10",
        "verified_by": "Statutory Review Team",
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
        "confidence": "verified",
        "effective_from": "2022-02-16",
        "source_url": "https://cpcb.nic.in/plastic-waste-rules/",
        "superseded_by": None,
        "retrieved_on": "2026-10-10",
        "verified_by": "Statutory Review Team",
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
        "confidence": "verified",
        "effective_from": "2022-02-16",
        "source_url": "https://cpcb.nic.in/plastic-waste-rules/",
        "superseded_by": None,
        "retrieved_on": "2026-10-10",
        "verified_by": "Statutory Review Team",
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
        "confidence": "verified",
        "effective_from": "2022-02-16",
        "source_url": "https://cpcb.nic.in/plastic-waste-rules/",
        "superseded_by": None,
        "retrieved_on": "2026-10-10",
        "verified_by": "Statutory Review Team",
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
        "confidence": "verified",
        "effective_from": "2022-08-24",
        "source_url": "https://cpcb.nic.in/battery-waste-management-rules/",
        "superseded_by": None,
        "retrieved_on": "2026-10-10",
        "verified_by": "Statutory Review Team",
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
        "title": "Category V: Biodegradable Plastics and Testing Protocol",
        "citation": "PWM (Amendment) Rules, 2024 & CPCB Interim Guidelines for Biodegradable Plastics",
        "confidence": "verified",
        "effective_from": "2024-03-15",
        "source_url": "https://cpcb.nic.in/biodegradable-plastics-guidelines/",
        "superseded_by": None,
        "retrieved_on": "2026-10-10",
        "verified_by": "Statutory Review Team",
        "text": (
            "Category V covers biodegradable plastics that degrade in natural environmental conditions (soil/marine/freshwater) "
            "without leaving microplastics or toxic residues, distinct from Category IV industrial compostables. "
            "Manufacturers must obtain provisional CPCB certification based on testing under IS 17899 / ISO 17556 standards. "
            "Biodegradable plastics must not be blended with conventional polyolefins and require dedicated EPR reporting."
        ),
    },
    {
        "id": "kb024",
        "title": "Waste-to-Energy and Cement Kiln Co-Processing (Energy Recovery Bridge)",
        "citation": "CPCB Technical Guidelines for Cement Kiln Co-Processing (2021) & MNRE Benchmarks",
        "confidence": "verified",
        "effective_from": "2021-06-10",
        "source_url": "https://cpcb.nic.in/co-processing-cement-guidelines/",
        "superseded_by": None,
        "retrieved_on": "2026-10-10",
        "verified_by": "Statutory Review Team",
        "text": (
            "Under Schedule II Clause 8 and CPCB Co-Processing Guidelines, plastic packaging waste that cannot be mechanically recycled "
            "provides a high-calorific alternative fuel resource for thermal and electrical energy recovery. "
            "Flexible polyolefins (Category II) yield approximately 35 MJ/kg (30-40 MJ/kg) net calorific value, while multilayered packaging "
            "(Category III) yields approximately 25 MJ/kg (20-30 MJ/kg). Co-processing in cement kilns achieves ~80% thermal substitution "
            "efficiency, replacing fossil coal, while dedicated Waste-to-Energy (WtE) combustion achieves ~22% net electrical conversion "
            "efficiency. Utilizing 1,000 MT of non-recycled Cat II/III packaging in cement kilns recovers over 6,000 MWh of thermal energy, "
            "diverting waste completely from landfills."
        ),
    },
]
