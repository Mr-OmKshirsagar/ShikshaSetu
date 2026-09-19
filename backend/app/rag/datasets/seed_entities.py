"""Dataset 19 — Entity / Organization Registry."""
from datetime import UTC, datetime
from pymongo.database import Database

ENTITIES = [
    {"entity_name": "MoSPI", "entity_type": "ministry",
     "full_name": "Ministry of Statistics and Programme Implementation",
     "parent_organization": "Government of India",
     "description": "Apex government body responsible for official statistics in India. Compiles national accounts, price indices (CPI), PLFS, IIP, and coordinates statistical activities across ministries.",
     "official_url": "https://mospi.gov.in",
     "official_status": "VERIFIED_OFFICIAL"},
    {"entity_name": "NSO", "entity_type": "office",
     "full_name": "National Statistical Office",
     "parent_organization": "MoSPI",
     "description": "Formed in 2019 by merging CSO and NSSO. Responsible for national accounts, PLFS, NSS surveys, and statistical standards.",
     "official_url": "https://mospi.gov.in",
     "official_status": "VERIFIED_OFFICIAL"},
    {"entity_name": "NSSO", "entity_type": "office",
     "full_name": "National Sample Survey Office",
     "parent_organization": "MoSPI (now NSO)",
     "description": "Former field data collection arm of MoSPI, merged into NSO in 2019. Conducted large-scale household surveys (EUS, NSS, PLFS).",
     "official_url": "https://mospi.gov.in",
     "official_status": "VERIFIED_OFFICIAL"},
    {"entity_name": "NSC", "entity_type": "commission",
     "full_name": "National Statistical Commission",
     "parent_organization": "MoSPI",
     "description": "Autonomous advisory body overseeing statistical standards, quality and methodology. Established 2005 following Rangarajan Commission.",
     "official_url": "https://mospi.gov.in/national-statistical-commission",
     "official_status": "VERIFIED_OFFICIAL"},
    {"entity_name": "NSSTA", "entity_type": "institute",
     "full_name": "National School of Statistical Training",
     "parent_organization": "MoSPI",
     "description": "In-service training institute for statistical cadre officers and government functionaries. Located in Greater Noida, UP.",
     "official_url": "https://nssta.gov.in",
     "official_status": "VERIFIED_OFFICIAL"},
    {"entity_name": "CBC", "entity_type": "commission",
     "full_name": "Capacity Building Commission",
     "parent_organization": "Government of India",
     "description": "Apex body under Mission Karmayogi for civil service HR reform. Develops and owns the National Competency Framework used in ShikshaSetu.",
     "official_url": "https://capabilitybuilding.gov.in",
     "official_status": "VERIFIED_OFFICIAL"},
    {"entity_name": "Karmayogi Bharat", "entity_type": "spv",
     "full_name": "Karmayogi Bharat (Special Purpose Vehicle)",
     "parent_organization": "Government of India",
     "description": "SPV under Mission Karmayogi that develops and manages the iGOT Karmayogi platform. Coordinates with ministries on competency-based learning.",
     "official_url": "https://karmayogibharat.gov.in",
     "official_status": "VERIFIED_OFFICIAL"},
    {"entity_name": "iGOT Karmayogi", "entity_type": "platform",
     "full_name": "Integrated Government Online Training - Karmayogi",
     "parent_organization": "Karmayogi Bharat",
     "description": "Online competency-based learning platform for Indian civil servants. Hosts courses mapped to the National Competency Framework.",
     "official_url": "https://igotkarmayogi.gov.in",
     "official_status": "VERIFIED_OFFICIAL"},
    {"entity_name": "DoPT", "entity_type": "ministry",
     "full_name": "Department of Personnel and Training",
     "parent_organization": "Ministry of Personnel, Public Grievances and Pensions",
     "description": "Responsible for civil service rules, conduct, discipline and training policy including CCS Conduct Rules 1964 applicable to all central government employees.",
     "official_url": "https://dopt.gov.in",
     "official_status": "VERIFIED_OFFICIAL"},
    {"entity_name": "CVC", "entity_type": "statutory_body",
     "full_name": "Central Vigilance Commission",
     "parent_organization": "Government of India",
     "description": "Apex vigilance institution for central government. Receives complaints of corruption, misconduct under Prevention of Corruption Act. Key channel for whistleblower complaints.",
     "official_url": "https://cvc.gov.in",
     "official_status": "VERIFIED_OFFICIAL"},
    {"entity_name": "ShikshaSetu", "entity_type": "platform",
     "full_name": "ShikshaSetu — Competency Intelligence Platform",
     "parent_organization": "SIH 2026 Team",
     "description": "AI-powered competency development platform for Indian civil servants built for Smart India Hackathon 2026 PS 26101. Integrates with iGOT Karmayogi and NSSTA.",
     "official_url": "",
     "official_status": "INTERNAL_PROTOTYPE"},
    {"entity_name": "DPIIT", "entity_type": "ministry",
     "full_name": "Department for Promotion of Industry and Internal Trade",
     "parent_organization": "Ministry of Commerce and Industry",
     "description": "Compiles the Wholesale Price Index (WPI) for India. Distinct from MoSPI which compiles CPI.",
     "official_url": "https://dpiit.gov.in",
     "official_status": "VERIFIED_OFFICIAL"},
    {"entity_name": "RBI", "entity_type": "central_bank",
     "full_name": "Reserve Bank of India",
     "parent_organization": "Government of India",
     "description": "India's central bank. Uses MoSPI's CPI data for monetary policy. Publishes inflation reports and monitors core inflation.",
     "official_url": "https://rbi.org.in",
     "official_status": "VERIFIED_OFFICIAL"},
]


def seed_entities(database: Database, overwrite: bool = False) -> dict:
    inserted = 0; updated = 0; skipped = 0
    for entry in ENTITIES:
        doc = {**entry, "last_verified_at": datetime.now(UTC).isoformat(), "created_at": datetime.now(UTC)}
        existing = database.rag_entity_registry.find_one({"entity_name": entry["entity_name"]})
        if existing:
            if overwrite:
                database.rag_entity_registry.update_one({"entity_name": entry["entity_name"]},
                    {"$set": {k: v for k, v in doc.items() if k != "created_at"}}); updated += 1
            else:
                skipped += 1
        else:
            database.rag_entity_registry.insert_one(doc); inserted += 1
    return {"inserted": inserted, "updated": updated, "skipped": skipped}
