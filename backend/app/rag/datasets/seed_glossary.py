"""
Dataset 16 — Official Statistical Glossary (seed data).

Atomic, one-concept-per-chunk definitional content for high-precision
"What is X?" queries. Stored in MongoDB collection `rag_glossary`.

Sources:
  - MoSPI Statistical Glossary (mospi.gov.in)
  - NSC / NSSO Survey Concepts & Definitions
  - NAS Glossary (SNA 2008 India adaptation)
  - ILO Labour Statistics definitions
  - DoPT / CBC Mission Karmayogi framework

official_status values:
  VERIFIED_OFFICIAL        — directly from official MoSPI/govt publication
  DERIVED_FROM_OFFICIAL    — paraphrased/summarised from official sources
  INTERNAL_PROTOTYPE       — working definitions for internal use
"""

from datetime import UTC, datetime
from pymongo.database import Database


def _entry(
    term: str,
    definition: str,
    domain: str,
    source_document: str = "",
    source_url: str = "",
    source_page: str = "",
    official_status: str = "DERIVED_FROM_OFFICIAL",
    aliases: list[str] | None = None,
) -> dict:
    return {
        "term": term,
        "definition": definition,
        "domain": domain,
        "source_document": source_document,
        "source_url": source_url,
        "source_page": source_page,
        "official_status": official_status,
        "aliases": aliases or [],
        "publication_date": None,
        "retrieval_date": datetime.now(UTC).isoformat(),
        "created_at": datetime.now(UTC),
    }


GLOSSARY_ENTRIES: list[dict] = [

    # ── GDP / National Accounts ───────────────────────────────────────────────
    _entry("Gross Domestic Product (GDP)",
           "The total monetary value of all final goods and services produced within a country's "
           "borders during a specific period, regardless of the nationality of producers. Measured "
           "using three equivalent approaches: Production (Value Added), Income, and Expenditure.",
           "NATIONAL_ACCOUNTS",
           "MoSPI National Accounts Statistics", "https://mospi.gov.in",
           official_status="VERIFIED_OFFICIAL",
           aliases=["GDP", "gross domestic product", "national output"]),

    _entry("Gross Value Added (GVA)",
           "The value of output less the value of intermediate consumption. GVA at basic prices = "
           "GDP at market prices – taxes on products + subsidies on products. India reports GVA by "
           "sector (agriculture, industry, services) as the primary production measure.",
           "NATIONAL_ACCOUNTS",
           "MoSPI National Accounts Statistics",
           official_status="VERIFIED_OFFICIAL",
           aliases=["GVA", "value added", "gross value added"]),

    _entry("Net Domestic Product (NDP)",
           "GDP minus consumption of fixed capital (depreciation). NDP = GDP – CFC. "
           "Represents the net addition to the capital stock of the economy.",
           "NATIONAL_ACCOUNTS",
           "MoSPI NAS Concepts & Definitions",
           official_status="DERIVED_FROM_OFFICIAL",
           aliases=["NDP", "net domestic product"]),

    _entry("GDP Deflator",
           "A price index that measures the average price level of all goods and services "
           "included in GDP. GDP Deflator = (Nominal GDP / Real GDP) × 100. Unlike CPI, covers "
           "the entire economy's output, not just a consumer basket.",
           "NATIONAL_ACCOUNTS",
           "MoSPI National Accounts Manual",
           official_status="DERIVED_FROM_OFFICIAL",
           aliases=["GDP deflator", "implicit price deflator", "national accounts deflator"]),

    _entry("Chain Linking",
           "A method of constructing volume measures of GDP by chaining together growth rates "
           "calculated using weights from adjacent years. India uses a fixed-base (2011-12) "
           "approach, while chain-linking is the international best practice per SNA 2008.",
           "NATIONAL_ACCOUNTS",
           "SNA 2008 / MoSPI NAS Manual",
           official_status="DERIVED_FROM_OFFICIAL",
           aliases=["chain linking", "chain index", "chained volume measure"]),

    _entry("Base Year",
           "The reference year against which price and volume changes are measured in index "
           "numbers. India's current NAS base year is 2011-12. The choice of base year affects "
           "the level and growth rates reported in national accounts.",
           "NATIONAL_ACCOUNTS",
           "MoSPI National Accounts Statistics",
           official_status="VERIFIED_OFFICIAL",
           aliases=["base year", "reference year", "base period"]),

    _entry("Consumption of Fixed Capital (CFC)",
           "The decline in the value of fixed assets used in production as a result of physical "
           "deterioration, normal obsolescence, or accidental damage. Equivalent to economic "
           "depreciation. CFC is deducted from gross to obtain net measures.",
           "NATIONAL_ACCOUNTS",
           "SNA 2008",
           official_status="DERIVED_FROM_OFFICIAL",
           aliases=["CFC", "consumption of fixed capital", "depreciation", "capital consumption allowance"]),

    # ── Price Statistics ──────────────────────────────────────────────────────
    _entry("Consumer Price Index (CPI)",
           "A measure of the average change over time in prices paid by households for a basket "
           "of goods and services. India's CPI (base 2012=100) covers CPI-Rural, CPI-Urban, and "
           "CPI-Combined, compiled by MoSPI. Food and Beverages carry ~45.86% weight.",
           "PRICE_STATISTICS",
           "MoSPI CPI Technical Manual",
           "https://mospi.gov.in/consumer-price-indices",
           official_status="VERIFIED_OFFICIAL",
           aliases=["CPI", "consumer price index", "retail inflation", "headline inflation"]),

    _entry("Wholesale Price Index (WPI)",
           "A price index measuring average changes in prices of goods at the wholesale/producer "
           "level. Compiled by DPIIT (Ministry of Commerce), base year 2011-12. Distinct from "
           "CPI which measures retail/consumer prices.",
           "PRICE_STATISTICS",
           "DPIIT WPI Technical Note",
           official_status="VERIFIED_OFFICIAL",
           aliases=["WPI", "wholesale price index", "producer prices"]),

    _entry("Core Inflation",
           "CPI inflation excluding volatile food and fuel/energy prices. Reveals underlying "
           "demand-driven inflation trends. Monitored by RBI for monetary policy alongside "
           "headline CPI. Not an official MoSPI concept but widely used in policy analysis.",
           "PRICE_STATISTICS",
           "RBI Monetary Policy Reports",
           official_status="DERIVED_FROM_OFFICIAL",
           aliases=["core inflation", "underlying inflation", "ex-food ex-fuel inflation"]),

    _entry("Laspeyres Price Index",
           "A fixed-weight price index using base-period quantities as weights. India's CPI "
           "uses a modified Laspeyres formula. Formula: Σ(P_t × Q_0) / Σ(P_0 × Q_0) × 100. "
           "Tends to overstate inflation due to substitution bias.",
           "PRICE_STATISTICS",
           "MoSPI CPI Methodology Paper",
           official_status="DERIVED_FROM_OFFICIAL",
           aliases=["Laspeyres index", "fixed weight index", "base weighted index"]),

    _entry("Index of Industrial Production (IIP)",
           "A composite indicator measuring the short-term changes in the volume of production "
           "of industrial products during a given period compared to a reference period. "
           "Compiled by MoSPI, base year 2011-12. Covers Mining, Manufacturing, and Electricity.",
           "PRICE_STATISTICS",
           "MoSPI IIP Technical Document",
           "https://mospi.gov.in/index-industrial-production",
           official_status="VERIFIED_OFFICIAL",
           aliases=["IIP", "index of industrial production", "industrial output index"]),

    # ── Labour Statistics ─────────────────────────────────────────────────────
    _entry("Periodic Labour Force Survey (PLFS)",
           "A continuous household survey conducted by MoSPI (from 2017-18) providing quarterly "
           "urban and annual rural/urban estimates of employment and unemployment. Replaced the "
           "earlier Employment and Unemployment Survey (EUS). Collects UPS, CWS, and weekly "
           "activity status data.",
           "LABOUR_STATISTICS",
           "MoSPI PLFS Annual Report",
           "https://mospi.gov.in/plfs-report",
           official_status="VERIFIED_OFFICIAL",
           aliases=["PLFS", "Periodic Labour Force Survey", "labour force survey", "employment survey", "job survey"]),

    _entry("Labour Force Participation Rate (LFPR)",
           "The proportion of the working-age population (15+ years) that is part of the labour "
           "force (employed + unemployed). LFPR = Labour Force / Working-Age Population × 100. "
           "Reported by PLFS separately for rural/urban and male/female.",
           "LABOUR_STATISTICS",
           "MoSPI PLFS Concepts & Definitions",
           official_status="VERIFIED_OFFICIAL",
           aliases=["LFPR", "labour force participation rate", "labor force participation", "economic activity rate"]),

    _entry("Worker Population Ratio (WPR)",
           "The proportion of the total population that is employed. WPR = Employed persons / "
           "Total population × 100. A broader measure than employment rate as denominator is "
           "total population, not just labour force.",
           "LABOUR_STATISTICS",
           "MoSPI PLFS Concepts & Definitions",
           official_status="VERIFIED_OFFICIAL",
           aliases=["WPR", "worker population ratio", "employment-population ratio"]),

    _entry("Usual Principal Activity Status (UPS/UPSS)",
           "The activity status of a person based on the major time spent (reference period of "
           "365 days). Categories: employed (self-employed, regular wage/salary, casual labour), "
           "unemployed, and not in labour force. Used in annual PLFS reports.",
           "LABOUR_STATISTICS",
           "MoSPI PLFS Technical Notes",
           official_status="VERIFIED_OFFICIAL",
           aliases=["UPS", "UPSS", "usual principal status", "usual status", "annual activity status"]),

    _entry("Current Weekly Status (CWS)",
           "The activity status of a person based on a reference period of 7 days preceding the "
           "date of survey. A person is considered employed if they worked for at least one hour "
           "on any day during the reference week.",
           "LABOUR_STATISTICS",
           "MoSPI PLFS Concepts & Definitions",
           official_status="VERIFIED_OFFICIAL",
           aliases=["CWS", "current weekly status", "weekly activity status"]),

    _entry("Unemployment Rate",
           "The proportion of persons in the labour force who are not employed but are seeking "
           "and available for work. Unemployment Rate = Unemployed / Labour Force × 100. "
           "Reported by PLFS under UPS, CWS, and CWSS separately.",
           "LABOUR_STATISTICS",
           "MoSPI PLFS Annual Report",
           official_status="VERIFIED_OFFICIAL",
           aliases=["unemployment rate", "jobless rate", "unemployment", "unemployed"]),

    # ── Sampling / Survey Methodology ─────────────────────────────────────────
    _entry("Probability Proportional to Size (PPS) Sampling",
           "A sampling procedure in which each unit's probability of selection is proportional "
           "to its size (e.g. number of workers, cultivated area). Used extensively in MoSPI "
           "household surveys (NSS, PLFS) for selecting first-stage units.",
           "SAMPLING",
           "MoSPI NSS Survey Methodology",
           official_status="DERIVED_FROM_OFFICIAL",
           aliases=["PPS", "PPS sampling", "probability proportional to size", "size-based sampling"]),

    _entry("Stratified Random Sampling",
           "A probability sampling method where the population is divided into non-overlapping "
           "groups (strata) and a random sample is drawn from each stratum. Improves precision "
           "when the population has distinct subgroups with different characteristics.",
           "SAMPLING",
           "MoSPI Statistical Training Manual",
           official_status="DERIVED_FROM_OFFICIAL",
           aliases=["stratified sampling", "stratified random sampling"]),

    _entry("Sampling Frame",
           "The list or representation of all units from which a sample may be drawn. In India's "
           "NSS and PLFS, the sampling frame is the Population Census list of villages/urban "
           "blocks (first stage) and households (second stage).",
           "SAMPLING",
           "MoSPI NSS Sampling Manual",
           official_status="DERIVED_FROM_OFFICIAL",
           aliases=["sampling frame", "survey frame", "population list"]),

    _entry("Confidence Interval",
           "A range of values, calculated from sample data, that is likely to contain the true "
           "population parameter at a specified confidence level (e.g. 95%). Width depends on "
           "sample size, variability, and the confidence level chosen.",
           "SAMPLING",
           "MoSPI Statistical Concepts",
           official_status="DERIVED_FROM_OFFICIAL",
           aliases=["confidence interval", "CI", "margin of error", "interval estimate"]),

    _entry("Standard Error",
           "A measure of the statistical accuracy of an estimate, equal to the standard deviation "
           "of the sampling distribution. Smaller standard errors indicate more precise estimates. "
           "Used to construct confidence intervals and test hypotheses.",
           "SAMPLING",
           "MoSPI Statistical Concepts",
           official_status="DERIVED_FROM_OFFICIAL",
           aliases=["standard error", "SE", "sampling error", "standard error of estimate"]),

    _entry("Non-Sampling Error",
           "Errors in survey data that are not due to sampling variability. Includes coverage "
           "error (missed units), measurement error (incorrect responses), non-response error, "
           "and processing error. Can affect both census and sample surveys.",
           "SAMPLING",
           "MoSPI Data Quality Framework",
           official_status="DERIVED_FROM_OFFICIAL",
           aliases=["non-sampling error", "non-sampling errors", "systematic error", "survey error"]),

    # ── Data Quality ──────────────────────────────────────────────────────────
    _entry("Data Quality Assessment Framework (DQAF)",
           "A structured framework developed by IMF for assessing quality of statistical systems "
           "across six dimensions: prerequisites of quality, integrity, methodological soundness, "
           "accuracy and reliability, serviceability, and accessibility. Used by MoSPI.",
           "DATA_QUALITY",
           "IMF DQAF / MoSPI Quality Assurance",
           "https://www.imf.org/en/Data/Statistics/DQRS",
           official_status="VERIFIED_OFFICIAL",
           aliases=["DQAF", "data quality assessment", "data quality framework"]),

    _entry("Administrative Data",
           "Data collected for non-statistical purposes by government departments and agencies "
           "in the course of their administrative functions (e.g. tax records, birth/death "
           "registrations). Increasingly used to supplement survey data.",
           "DATA_QUALITY",
           "MoSPI Administrative Data Guidelines",
           official_status="DERIVED_FROM_OFFICIAL",
           aliases=["administrative data", "admin data", "by-product data", "register data"]),

    # ── SDGs / Metadata ───────────────────────────────────────────────────────
    _entry("Sustainable Development Goals (SDGs)",
           "A set of 17 global goals adopted by the UN in 2015 as part of the 2030 Agenda for "
           "Sustainable Development. India's progress is monitored by MoSPI through the SDG "
           "National Indicator Framework (NIF) covering 306 national indicators.",
           "SDG",
           "MoSPI SDG National Indicator Framework",
           "https://mospi.gov.in/sdg",
           official_status="VERIFIED_OFFICIAL",
           aliases=["SDG", "SDGs", "sustainable development goals", "2030 agenda"]),

    _entry("SDMX (Statistical Data and Metadata eXchange)",
           "An international standard (ISO 17369) for the exchange and sharing of statistical "
           "data and metadata. Used by MoSPI and international statistical organizations (IMF, "
           "World Bank, UN) for interoperable data dissemination.",
           "METADATA",
           "SDMX Technical Standards",
           "https://sdmx.org",
           official_status="DERIVED_FROM_OFFICIAL",
           aliases=["SDMX", "statistical data exchange", "metadata exchange"]),

    # ── Organisations ─────────────────────────────────────────────────────────
    _entry("National Statistical Commission (NSC)",
           "An autonomous advisory body under MoSPI that oversees statistical standards, quality, "
           "and coordination in India. Established in 2005 following the Rangarajan Commission "
           "report. Reviews methodology of major surveys.",
           "ORGANISATION",
           "MoSPI — NSC",
           "https://mospi.gov.in/national-statistical-commission",
           official_status="VERIFIED_OFFICIAL",
           aliases=["NSC", "National Statistical Commission"]),

    _entry("National Sample Survey Office (NSSO)",
           "The field organisation of MoSPI responsible for collecting socioeconomic data through "
           "large-scale household surveys. Merged with the Central Statistical Office (CSO) to "
           "form the National Statistical Office (NSO) in 2019.",
           "ORGANISATION",
           "MoSPI",
           official_status="VERIFIED_OFFICIAL",
           aliases=["NSSO", "National Sample Survey Office", "NSS", "National Sample Survey"]),

    _entry("National Statistical Office (NSO)",
           "The apex body for official statistics in India formed in 2019 by merging the Central "
           "Statistical Office (CSO) and National Sample Survey Office (NSSO) under MoSPI. "
           "Responsible for national accounts, price indices, and major surveys.",
           "ORGANISATION",
           "MoSPI — NSO",
           official_status="VERIFIED_OFFICIAL",
           aliases=["NSO", "National Statistical Office", "CSO"]),

    _entry("Capacity Building Commission (CBC)",
           "An apex body under the Government of India's Mission Karmayogi initiative to "
           "reform the human resource development of civil servants. CBC develops and maintains "
           "the competency framework used in iGOT Karmayogi and ShikshaSetu.",
           "ORGANISATION",
           "Mission Karmayogi / CBC",
           "https://capabilitybuilding.gov.in",
           official_status="VERIFIED_OFFICIAL",
           aliases=["CBC", "Capacity Building Commission", "Mission Karmayogi"]),

    _entry("iGOT Karmayogi",
           "An online learning platform under Mission Karmayogi providing competency-based "
           "courses for Indian civil servants. Developed and managed by Karmayogi Bharat. "
           "Integrated with ShikshaSetu for personalized learning pathway recommendations.",
           "ORGANISATION",
           "Mission Karmayogi",
           "https://igotkarmayogi.gov.in",
           official_status="VERIFIED_OFFICIAL",
           aliases=["iGOT", "iGOT Karmayogi", "Karmayogi platform", "civil services learning platform"]),

    _entry("National School of Statistical Training (NSSTA)",
           "An institute under MoSPI providing in-service training to statistical cadre officers "
           "and other government functionaries in statistical methods, data analysis, and survey "
           "design. Located in Greater Noida, Uttar Pradesh.",
           "ORGANISATION",
           "MoSPI — NSSTA",
           "https://nssta.gov.in",
           official_status="VERIFIED_OFFICIAL",
           aliases=["NSSTA", "National School of Statistical Training", "statistical training"]),

    # ── Competency Framework ──────────────────────────────────────────────────
    _entry("Competency Level",
           "In ShikshaSetu, competency proficiency is rated on a 5-point scale: "
           "Level 1 (Awareness/Foundation), Level 2 (Working Knowledge), "
           "Level 3 (Operational Practitioner), Level 4 (Advanced Specialist), "
           "Level 5 (Expert/Policy Authority). Levels are updated by authoritative "
           "assessments (confidence 0.85) or supporting evidence (confidence 0.30).",
           "COMPETENCY_FRAMEWORK",
           "ShikshaSetu CBC Competency Framework",
           official_status="INTERNAL_PROTOTYPE",
           aliases=["competency level", "proficiency level", "skill level", "capability level"]),

    _entry("Authoritative Evidence",
           "In ShikshaSetu, evidence generated by completing an adaptive capability assessment "
           "or standardised capability assessment. Carries a confidence weight of 0.85 and "
           "directly updates the official competency rating in the ledger.",
           "COMPETENCY_FRAMEWORK",
           "ShikshaSetu Evidence System",
           official_status="INTERNAL_PROTOTYPE",
           aliases=["authoritative evidence", "0.85 evidence", "assessment evidence"]),

    _entry("Supporting Evidence",
           "In ShikshaSetu, evidence generated by completing a learning activity, iGOT course, "
           "or quiz. Carries a confidence weight of 0.30. Does NOT automatically update the "
           "competency rating — formal assessment is required to close a skill gap.",
           "COMPETENCY_FRAMEWORK",
           "ShikshaSetu Evidence System",
           official_status="INTERNAL_PROTOTYPE",
           aliases=["supporting evidence", "0.30 evidence", "learning evidence"]),

    _entry("Skill Gap",
           "The difference between the required competency level for a role and the official's "
           "current assessed competency level. skill_gap = required_level – current_level. "
           "Negative or zero = met. Positive = gap requiring learning intervention.",
           "COMPETENCY_FRAMEWORK",
           "ShikshaSetu Skill Gap Engine",
           official_status="INTERNAL_PROTOTYPE",
           aliases=["skill gap", "competency gap", "proficiency gap", "capability deficit"]),

]


def seed_glossary(database: Database, overwrite: bool = False) -> dict:
    """
    Idempotent seed of the official statistical glossary.

    Args:
        database:  MongoDB database instance.
        overwrite: If True, update existing entries. Default False (skip existing).

    Returns:
        {"inserted": n, "updated": n, "skipped": n}
    """
    inserted = 0
    updated = 0
    skipped = 0

    for entry in GLOSSARY_ENTRIES:
        term = entry["term"]
        existing = database.rag_glossary.find_one({"term": term})

        if existing:
            if overwrite:
                database.rag_glossary.update_one(
                    {"term": term},
                    {"$set": {k: v for k, v in entry.items() if k != "created_at"}},
                )
                updated += 1
            else:
                skipped += 1
        else:
            database.rag_glossary.insert_one(entry)
            inserted += 1

    return {"inserted": inserted, "updated": updated, "skipped": skipped}
