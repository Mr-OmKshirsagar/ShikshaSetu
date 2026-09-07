"""Master RAG dataset seeder — seeds Datasets 14–21."""
import logging
import sys

logger = logging.getLogger("rag_seed")


def seed_all(db, overwrite: bool = False) -> dict:
    """Run all RAG dataset seeds. Returns summary dict."""
    from .seed_glossary import seed_glossary
    from .seed_synonyms import seed_synonyms
    from .seed_eval_set import seed_eval_set
    from .seed_refusal_set import seed_refusal_set
    from .seed_entities import seed_entities
    from .seed_terminology_hi_en import seed_terminology_hi_en

    results = {}
    for name, fn in [
        ("glossary (DS16)",         lambda: seed_glossary(db, overwrite)),
        ("synonyms (DS15)",         lambda: seed_synonyms(db, overwrite)),
        ("eval_set (DS14)",         lambda: seed_eval_set(db, overwrite)),
        ("refusal_set (DS21)",      lambda: seed_refusal_set(db, overwrite)),
        ("entity_registry (DS19)",  lambda: seed_entities(db, overwrite)),
        ("terminology_hi_en (DS17)",lambda: seed_terminology_hi_en(db, overwrite)),
    ]:
        try:
            r = fn()
            results[name] = r
            logger.info("%s: %s", name, r)
        except Exception as exc:
            results[name] = {"error": str(exc)}
            logger.error("%s FAILED: %s", name, exc)
    return results


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    overwrite = "--overwrite" in sys.argv

    from app.core.config import get_settings
    from app.core.database import initialize_database, close_database
    s = get_settings()
    client, db = initialize_database(s.mongodb_uri, s.mongodb_database)
    try:
        results = seed_all(db, overwrite=overwrite)
        print("\nSeed results:")
        for k, v in results.items():
            print(f"  {k}: {v}")
    finally:
        close_database(client)
