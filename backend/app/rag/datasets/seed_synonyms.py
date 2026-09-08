"""
Dataset 15 — Synonym / Acronym / Alias Dictionary.

Used for query expansion in the keyword/BM25 leg of hybrid retrieval.
Stored in MongoDB collection `rag_synonyms`.

When a user types "PLFS" or "employment survey" or "जनशक्ति सर्वेक्षण",
the hybrid retriever should expand the query to include all known aliases
before hitting the BM25/text-search index.

Rules:
- canonical_term is the preferred, stable identifier
- aliases are alternative forms, abbreviations, or colloquial names
- Do NOT expand when aliases change meaning (e.g. CPI can mean Corruption
  Perception Index outside this domain — only expand within the statistics domain)
"""

from datetime import UTC, datetime
from pymongo.database import Database


def _syn(
    canonical: str,
    aliases: list[str],
    acronym_of: str = "",
    domain: str = "GENERAL",
    definition: str = "",
    source: str = "MoSPI / CBC / iGOT",
    official_status: str = "VERIFIED_OFFICIAL",
) -> dict:
    return {
        "canonical_term": canonical,
        "aliases": aliases,
        "acronym_of": acronym_of,
        "domain": domain,
        "definition": definition,
        "source": source,
        "official_status": official_status,
        "last_verified_at": datetime.now(UTC).isoformat(),
        "created_at": datetime.now(UTC),
    }


SYNONYM_ENTRIES: list[dict] = [

    # ── Labour / Employment ───────────────────────────────────────────────────
    _syn("PLFS",
         ["Periodic Labour Force Survey", "labour force survey", "employment survey",
          "job survey", "employment and unemployment survey", "EUS", "workforce survey",
          "periodic labour force", "labour survey"],
         acronym_of="Periodic Labour Force Survey",
         domain="LABOUR_STATISTICS"),

    _syn("LFPR",
         ["Labour Force Participation Rate", "labor force participation rate",
          "economic activity rate", "workforce participation",
          "labour market participation"],
         acronym_of="Labour Force Participation Rate",
         domain="LABOUR_STATISTICS"),

    _syn("WPR",
         ["Worker Population Ratio", "worker-population ratio",
          "employment-population ratio", "employment rate"],
         acronym_of="Worker Population Ratio",
         domain="LABOUR_STATISTICS"),

    _syn("UPS",
         ["Usual Principal Activity Status", "UPSS", "usual status",
          "annual employment status", "long-term activity status"],
         acronym_of="Usual Principal Activity Status",
         domain="LABOUR_STATISTICS"),

    _syn("CWS",
         ["Current Weekly Status", "weekly activity status",
          "weekly employment status", "current employment status"],
         acronym_of="Current Weekly Status",
         domain="LABOUR_STATISTICS"),

    # ── Price Statistics ──────────────────────────────────────────────────────
    _syn("CPI",
         ["Consumer Price Index", "retail price index", "cost of living index",
          "consumer inflation", "headline inflation", "retail inflation",
          "price index", "inflation index"],
         acronym_of="Consumer Price Index",
         domain="PRICE_STATISTICS"),

    _syn("WPI",
         ["Wholesale Price Index", "producer price index", "factory gate prices",
          "wholesale inflation", "producer inflation"],
         acronym_of="Wholesale Price Index",
         domain="PRICE_STATISTICS"),

    _syn("IIP",
         ["Index of Industrial Production", "industrial production index",
          "manufacturing output index", "factory output", "industrial output"],
         acronym_of="Index of Industrial Production",
         domain="PRICE_STATISTICS"),

    _syn("PPI",
         ["Producer Price Index", "production price index"],
         acronym_of="Producer Price Index",
         domain="PRICE_STATISTICS"),

    # ── National Accounts ─────────────────────────────────────────────────────
    _syn("GDP",
         ["Gross Domestic Product", "national output", "economic output",
          "total economic production", "national income", "economic size"],
         acronym_of="Gross Domestic Product",
         domain="NATIONAL_ACCOUNTS"),

    _syn("GVA",
         ["Gross Value Added", "value added", "sectoral output"],
         acronym_of="Gross Value Added",
         domain="NATIONAL_ACCOUNTS"),

    _syn("GNP",
         ["Gross National Product", "national income", "national gross product"],
         acronym_of="Gross National Product",
         domain="NATIONAL_ACCOUNTS"),

    _syn("NAS",
         ["National Accounts Statistics", "national accounts", "CSO national accounts",
          "national income statistics"],
         acronym_of="National Accounts Statistics",
         domain="NATIONAL_ACCOUNTS"),

    _syn("CFC",
         ["Consumption of Fixed Capital", "depreciation", "capital consumption",
          "capital consumption allowance", "fixed capital consumption"],
         acronym_of="Consumption of Fixed Capital",
         domain="NATIONAL_ACCOUNTS"),

    # ── Agricultural / Industrial Statistics ─────────────────────────────────
    _syn("ASI",
         ["Annual Survey of Industries", "industrial survey", "manufacturing survey",
          "factory survey", "annual industrial survey"],
         acronym_of="Annual Survey of Industries",
         domain="INDUSTRIAL_STATISTICS"),

    _syn("NSSO",
         ["National Sample Survey Office", "National Sample Survey Organisation",
          "NSS", "National Sample Survey", "NSO field wing"],
         acronym_of="National Sample Survey Office",
         domain="ORGANISATION"),

    # ── SDG / Quality ─────────────────────────────────────────────────────────
    _syn("SDG",
         ["Sustainable Development Goal", "SDGs", "2030 goals", "global goals",
          "United Nations SDG", "sustainable development goals"],
         acronym_of="Sustainable Development Goals",
         domain="SDG"),

    _syn("DQAF",
         ["Data Quality Assessment Framework", "data quality framework",
          "IMF data quality", "quality assessment framework"],
         acronym_of="Data Quality Assessment Framework",
         domain="DATA_QUALITY"),

    _syn("SDMX",
         ["Statistical Data and Metadata Exchange",
          "statistical data exchange", "metadata exchange standard"],
         acronym_of="Statistical Data and Metadata eXchange",
         domain="METADATA"),

    # ── Organisations ─────────────────────────────────────────────────────────
    _syn("MoSPI",
         ["Ministry of Statistics and Programme Implementation",
          "Ministry of Statistics", "statistics ministry",
          "Ministry of Statistics & PI", "MOSPI"],
         acronym_of="Ministry of Statistics and Programme Implementation",
         domain="ORGANISATION"),

    _syn("NSC",
         ["National Statistical Commission", "statistics commission",
          "statistical standards body"],
         acronym_of="National Statistical Commission",
         domain="ORGANISATION"),

    _syn("NSO",
         ["National Statistical Office", "Central Statistical Office",
          "CSO", "national statistics office"],
         acronym_of="National Statistical Office",
         domain="ORGANISATION"),

    _syn("NSSTA",
         ["National School of Statistical Training",
          "statistical training school", "MoSPI training institute",
          "national statistical training"],
         acronym_of="National School of Statistical Training",
         domain="ORGANISATION"),

    _syn("TPAC",
         ["Training Programme for Administrative Capacity",
          "administrative capacity training"],
         acronym_of="Training Programme for Administrative Capacity",
         domain="ORGANISATION"),

    _syn("CBC",
         ["Capacity Building Commission", "capacity commission",
          "Mission Karmayogi commission"],
         acronym_of="Capacity Building Commission",
         domain="ORGANISATION"),

    _syn("iGOT",
         ["iGOT Karmayogi", "karmayogi platform", "civil services learning platform",
          "government learning platform", "iGOT portal",
          "integrated government online training"],
         domain="ORGANISATION"),

    # ── Competency / ShikshaSetu ──────────────────────────────────────────────
    _syn("ShikshaSetu",
         ["shikshasetu", "capability platform", "competency intelligence platform",
          "SIH 2026 PS 26101", "civil services capability platform"],
         domain="SYSTEM"),

    _syn("PLFS Round",
         ["PLFS annual report", "PLFS quarterly bulletin", "labour force round",
          "PLFS 2022-23", "PLFS 2023-24"],
         domain="LABOUR_STATISTICS"),

    _syn("DoPT",
         ["Department of Personnel and Training",
          "personnel and training department",
          "central government HR ministry"],
         acronym_of="Department of Personnel and Training",
         domain="ORGANISATION"),

    # ── Sampling ──────────────────────────────────────────────────────────────
    _syn("PPS",
         ["Probability Proportional to Size", "PPS sampling",
          "size-based sampling", "proportional sampling"],
         acronym_of="Probability Proportional to Size",
         domain="SAMPLING"),

]


def seed_synonyms(database: Database, overwrite: bool = False) -> dict:
    """
    Idempotent seed of the synonym / acronym dictionary.

    Returns:
        {"inserted": n, "updated": n, "skipped": n}
    """
    inserted = 0
    updated = 0
    skipped = 0

    for entry in SYNONYM_ENTRIES:
        canonical = entry["canonical_term"]
        existing = database.rag_synonyms.find_one({"canonical_term": canonical})

        if existing:
            if overwrite:
                database.rag_synonyms.update_one(
                    {"canonical_term": canonical},
                    {"$set": {k: v for k, v in entry.items() if k != "created_at"}},
                )
                updated += 1
            else:
                skipped += 1
        else:
            database.rag_synonyms.insert_one(entry)
            inserted += 1

    return {"inserted": inserted, "updated": updated, "skipped": skipped}


def expand_query(database: Database, query: str, max_expansions: int = 3) -> str:
    """
    Expand a user query with canonical synonyms and aliases from the dictionary.

    Example:
        "What is the PLFS?" → "What is the PLFS Periodic Labour Force Survey labour force survey?"

    Only adds expansions that are not already in the query. Caps expansion to
    avoid bloating the query string.

    Returns the expanded query string.
    """
    query_lower = query.lower()
    expansions: list[str] = []
    added = 0

    # Search for any alias or canonical term that appears in the query
    all_entries = list(database.rag_synonyms.find({}))
    for entry in all_entries:
        if added >= max_expansions:
            break
        canonical = entry.get("canonical_term", "")
        aliases: list[str] = entry.get("aliases", [])

        # Check if query contains canonical or any alias
        all_forms = [canonical] + aliases
        matched = any(form.lower() in query_lower for form in all_forms if form)
        if not matched:
            continue

        # Add forms that are NOT already in the query
        for form in all_forms[:4]:  # limit forms per entry
            if form and form.lower() not in query_lower and form not in expansions:
                expansions.append(form)
                added += 1
                if added >= max_expansions:
                    break

    if expansions:
        return f"{query} {' '.join(expansions)}"
    return query
