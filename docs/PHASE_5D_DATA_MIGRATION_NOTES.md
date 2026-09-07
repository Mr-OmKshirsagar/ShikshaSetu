# PHASE 5D — DATA MIGRATION & HISTORICAL EVIDENCE AUDIT NOTES

**System:** ShikshaSetu Core Platform  
**Scope:** Competency Evidence Ledger & Competency Profiles  
**Date:** 2026-09-06

---

## 1. Audit of Historical Records

During the data integrity audit, we examined the historical relationship between `competency_evidence` and `competency_profiles`:

1. **Pre-Remediation Behavior:**
   - Previous self-service quiz submissions ran `_update_competency_deterministic()`, directly writing values to `competency_profiles.current_level` (ranging from 1.5 to 4.5) and `confidence` (0.80 to 0.90).
   - In environments where quizzes were run without subsequent formal assessments, the profile level reflected the quiz score rather than a formal assessment.

2. **Remediation Invariants:**
   - **DO NOT delete historical evidence.** All records in `competency_evidence` are immutable historical facts documenting learner practice.
   - **DO NOT silently mutate production data without a formal migration window.**

---

## 2. Non-Destructive Migration Strategy (When Executing Against Production)

If historical profile levels need alignment with the new authority rules in a deployed database:

### Migration Algorithm:
```python
# Pseudo-code for non-destructive historical reconciliation
for user in database.users.find():
    for comp in database.competencies.find():
        user_id = user["_id"]
        comp_id = comp["_id"]

        # Check if user has an authoritative assessment record
        authoritative_ev = database.competency_evidence.find_one(
            {
                "user_id": user_id,
                "competency_id": comp_id,
                "authority": "AUTHORITATIVE"
            },
            sort=[("created_at", -1)]
        )

        if authoritative_ev:
            # Profile correctly reflects the latest authoritative evaluation
            continue
        
        # If user ONLY has supporting quiz evidence:
        supporting_only = database.competency_evidence.find_one(
            {
                "user_id": user_id,
                "competency_id": comp_id,
                "authority": "SUPPORTING"
            }
        )
        
        if supporting_only:
            # Revert profile to baseline (role required or standard 2.5 baseline)
            # Retain supporting evidence in ledger
            database.competency_profiles.update_one(
                {"user_id": user_id, "competency_id": comp_id},
                {"$set": {"current_level": 2.5, "confidence": 0.50, "updated_at": datetime.now(UTC)}}
            )
```

### Impact on Seed / Demo Datasets:
- Seed master scripts (`seed_master.py`) establish authoritative baseline profiles (`BASELINE_ASSESSMENT`) during initial role assignment.
- Test suites have been updated to assert that quiz submissions do not mutate these baseline profiles.
