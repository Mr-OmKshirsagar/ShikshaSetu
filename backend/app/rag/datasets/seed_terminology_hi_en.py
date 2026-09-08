"""Dataset 17 — Hindi/English Statistical Terminology Mapping."""
from datetime import UTC, datetime
from pymongo.database import Database

HI_EN_ENTRIES = [
    # Labour
    {"term_en": "Labour Force Participation Rate", "term_hi": "श्रम बल भागीदारी दर",
     "transliteration": "Shram Bal Bhagidari Dar", "domain": "LABOUR_STATISTICS"},
    {"term_en": "Worker Population Ratio", "term_hi": "श्रमिक जनसंख्या अनुपात",
     "transliteration": "Shramik Jansankhya Anupat", "domain": "LABOUR_STATISTICS"},
    {"term_en": "Unemployment Rate", "term_hi": "बेरोजगारी दर",
     "transliteration": "Berozgari Dar", "domain": "LABOUR_STATISTICS"},
    {"term_en": "Periodic Labour Force Survey", "term_hi": "आवधिक श्रम बल सर्वेक्षण",
     "transliteration": "Aavadhik Shram Bal Sarvekshan", "domain": "LABOUR_STATISTICS"},
    {"term_en": "Employment", "term_hi": "रोजगार",
     "transliteration": "Rojgar", "domain": "LABOUR_STATISTICS"},
    # Price Statistics
    {"term_en": "Consumer Price Index", "term_hi": "उपभोक्ता मूल्य सूचकांक",
     "transliteration": "Upabhokta Mulya Suchakank", "domain": "PRICE_STATISTICS"},
    {"term_en": "Wholesale Price Index", "term_hi": "थोक मूल्य सूचकांक",
     "transliteration": "Thok Mulya Suchakank", "domain": "PRICE_STATISTICS"},
    {"term_en": "Inflation", "term_hi": "मुद्रास्फीति",
     "transliteration": "Mudrasphiti", "domain": "PRICE_STATISTICS"},
    # National Accounts
    {"term_en": "Gross Domestic Product", "term_hi": "सकल घरेलू उत्पाद",
     "transliteration": "Sakal Gharelu Utpad", "domain": "NATIONAL_ACCOUNTS"},
    {"term_en": "National Income", "term_hi": "राष्ट्रीय आय",
     "transliteration": "Rashtriya Aay", "domain": "NATIONAL_ACCOUNTS"},
    # Sampling
    {"term_en": "Sampling", "term_hi": "प्रतिचयन",
     "transliteration": "Pratichayan", "domain": "SAMPLING"},
    {"term_en": "Sample Survey", "term_hi": "प्रतिदर्श सर्वेक्षण",
     "transliteration": "Pratidarsh Sarvekshan", "domain": "SAMPLING"},
    {"term_en": "Population", "term_hi": "जनसंख्या",
     "transliteration": "Jansankhya", "domain": "SAMPLING"},
    # Competency
    {"term_en": "Competency", "term_hi": "दक्षता",
     "transliteration": "Dakshata", "domain": "COMPETENCY"},
    {"term_en": "Skill Gap", "term_hi": "कौशल अंतर",
     "transliteration": "Kaushal Antar", "domain": "COMPETENCY"},
    {"term_en": "Assessment", "term_hi": "मूल्यांकन",
     "transliteration": "Mulyankan", "domain": "COMPETENCY"},
    {"term_en": "Training", "term_hi": "प्रशिक्षण",
     "transliteration": "Prashikshan", "domain": "COMPETENCY"},
    # Organisations
    {"term_en": "Ministry of Statistics", "term_hi": "सांख्यिकी मंत्रालय",
     "transliteration": "Sankhyiki Mantralaya", "domain": "ORGANISATION"},
    {"term_en": "Civil Services", "term_hi": "सिविल सेवाएं",
     "transliteration": "Civil Sevaen", "domain": "ORGANISATION"},
]


def seed_terminology_hi_en(database: Database, overwrite: bool = False) -> dict:
    inserted = 0; updated = 0; skipped = 0
    for entry in HI_EN_ENTRIES:
        doc = {**entry,
               "source": "MoSPI / DoPT Official Publications",
               "official_status": "DERIVED_FROM_OFFICIAL",
               "last_verified_at": datetime.now(UTC).isoformat(),
               "created_at": datetime.now(UTC)}
        existing = database.rag_terminology_hi_en.find_one({"term_en": entry["term_en"]})
        if existing:
            if overwrite:
                database.rag_terminology_hi_en.update_one({"term_en": entry["term_en"]},
                    {"$set": {k: v for k, v in doc.items() if k != "created_at"}}); updated += 1
            else:
                skipped += 1
        else:
            database.rag_terminology_hi_en.insert_one(doc); inserted += 1
    return {"inserted": inserted, "updated": updated, "skipped": skipped}
