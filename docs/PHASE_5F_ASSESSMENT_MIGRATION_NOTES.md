# PHASE 5F — ASSESSMENT DATA MIGRATION NOTES

**Timestamp:** 2026-09-06  
**Status:** Audit & Safe Governance  
**Repository:** ShikshaSetu

---

## 1. Assessment Collection Inventory

| Collection | Subsystem | Entity | Canonical Status | Notes |
|---|---|---|---|---|
| `quizzes` | `quizzes/` | Practice / Self-Service Quiz | Canonical | Contains self-service practice quizzes created by learners |
| `trainer_quizzes` | `trainer/` | Trainer-Reviewed Quiz | Canonical | Contains published & assigned quizzes curated by Trainers |
| `quiz_attempts` | `quizzes/`, `trainer/` | Learner Quiz Attempt | Canonical | Shared canonical attempt store for all quiz submissions |
| `capability_assessments` | `capability_assessments/` | Formal Capability Evaluation | Canonical | Contains multi-item fixed-form authoritative evaluations |
| `adaptive_assessment_sessions` | `adaptive_assessments/` | IRT Adaptive Session | Canonical | Contains session state, theta history, and adaptive test progression |
| `assessments` | `assessments/` | Diagnostic Onboarding Tests | Canonical | Diagnostic baseline multi-component tests |
| `assessment_attempts` | `assessments/` | Diagnostic Attempts | Canonical | Diagnostic attempt store |
| `competency_evidence` | All subsystems | Append-Only Evidence Log | Canonical | Central evidence ledger storing both Supporting & Authoritative records |
| `competency_profiles` | All subsystems | Official Competency Profile | Canonical | Mutated ONLY by Authoritative evidence |

---

## 2. Compatibility & Historical Records

1. **No Destructive Migration Required:**
   - Existing historical evidence records in `competency_evidence` remain fully intact.
   - Distinct score types (`PERCENTAGE`, `NORMALIZED_SCORE`, `IRT_THETA`) and authorities (`SUPPORTING`, `AUTHORITATIVE`) are partitioned cleanly.
2. **Schema Separation:**
   - `quizzes` vs `trainer_quizzes`: Kept separate to allow autonomous learner practice without polluting trainer curriculum governance.
   - `capability_assessments` vs `adaptive_assessment_sessions`: Kept separate to preserve both fixed-form standardized benchmarking and dynamic IRT adaptive testing.

---

## 3. Operational Guidelines

- Do not delete historical `quiz_attempts` or `assessment_attempts`.
- Do not retroactively upgrade historical practice quiz evidence (`confidence: 0.30`) to authoritative capability ratings.
- Retain all historical audit trails for DoPT / MoSPI civil service compliance.
