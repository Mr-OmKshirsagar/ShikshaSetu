# PHASE 5F — ASSESSMENT ARCHITECTURE CONSOLIDATION REPORT

**Timestamp:** 2026-09-06  
**Status:** Completed  
**Repository:** ShikshaSetu (Advanced Competency-Based Learning Platform)

---

## 1. Assessment Architecture Before

Prior to consolidation, ShikshaSetu contained multiple assessment paths with overlapping scoring terminology and asynchronous authority boundaries:
- `quizzes/`: Self-service quiz creation and submission.
- `capability_assessments/`: Fixed-form knowledge tests evaluating specific competencies.
- `adaptive_assessments/`: Item Response Theory (IRT) dynamic theta estimation assessments.
- `assessments/`: Diagnostic onboarding multi-component prototype assessments.
- `trainer/`: Trainer Assessment Studio managing learning materials, RAG question generation, review studio, and published quiz assignments.

Risks audited:
- Potential confusion between percentage scores (0–100%) and continuous IRT proficiency theta levels (1.0–5.0).
- Ensuring non-authoritative practice checks never mutate official competency profiles.
- Guarding session finalization against duplicate execution and duplicate evidence insertion.

---

## 2. Assessment Architecture After

The consolidated assessment architecture establishes strict domain partitioning and an unambiguous evidence authority contract:

```
                    ASSESSMENT DOMAIN
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
     PRACTICE          FORMAL             ADAPTIVE
       QUIZ           CAPABILITY          ASSESSMENT
    (quizzes/)      (capability_/)       (adaptive_/)
        │                  │                  │
        ▼                  ▼                  ▼
   SUPPORTING        AUTHORITATIVE      AUTHORITATIVE
    EVIDENCE           EVIDENCE           EVIDENCE
 (Weight: 0.30)     (Weight: 0.85)     (Weight: 0.85)
        │                  │                  │
        │                  └────────┬─────────┘
        │                           ▼
        │                   COMPETENCY UPDATE
        │                  (competency_profiles)
        │                           │
        │                           ▼
        │                       SKILL GAP
        ▼
   LEARNING/KNOWLEDGE
      EVIDENCE
 (competency_evidence)
```

---

## 3. Responsibility of Each Subsystem

| Subsystem | Primary Responsibility | Score Type | Authority | Profile Mutation |
|---|---|---|---|---|
| **quizzes/** | Self-service learner practice & trainer quiz assignments | `PERCENTAGE` | `SUPPORTING` (0.30) | **NONE** (Immutable) |
| **capability_assessments/** | Standardized fixed-form capability evaluation | `NORMALIZED_SCORE` | `AUTHORITATIVE` (0.85) | **YES** (Profile updated) |
| **adaptive_assessments/** | Dynamic IRT real-time adaptive capability test | `IRT_THETA` | `AUTHORITATIVE` (0.85) | **YES** (Profile updated) |
| **assessments/** | Initial diagnostic baseline onboarding calibration | `WEIGHTED_SCORE` | `AUTHORITATIVE` (Diagnostic) | **YES** (Baseline initialization) |
| **trainer/** | Material upload, RAG question generation & Review Studio | N/A (Authoring) | `SUPPORTING` (Learner attempts) | **NONE** |

---

## 4. Score Semantics

- **Percentage Score (`PERCENTAGE`):** Calculated as `(correct_count / total_questions) * 100.0`. Kept strictly in `[0.0, 100.0]`. Used for practice quizzes and learning checks.
- **IRT Theta Score (`IRT_THETA`):** Real-time calibrated item-response ability level bounded in `[1.0, 5.0]`. Represents continuous civil service proficiency.
- **Normalized Competency Score (`NORMALIZED_SCORE`):** Scaled capability rating in `[1.0, 5.0]` mapped from multidimensional or standard question batteries.
- Distinct scoring modules do not cross-interpret or mix percentage and IRT theta semantics.

---

## 5. Evidence Authority

Centralized in `competency_evidence`:
1. **SUPPORTING Evidence:**
   - Sources: `AI_QUIZ`, `TRAINER_QUIZ`, `LEARNING_ACTIVITY`
   - Weight: `0.30`
   - Role: Recorded into historical evidence ledger; never directly modifies `competency_profiles.current_level`.
2. **AUTHORITATIVE Evidence:**
   - Sources: `capability_assessment`, `adaptive_capability_assessment`, `initial_assessment`
   - Weight: `0.85`
   - Role: Directly updates official competency levels in `competency_profiles` and triggers downstream skill gap recalculation.

---

## 6. Competency Mutation Boundary

A single strict invariant governs `competency_profiles`:
- **Supporting paths:** Callers in `quizzes/` and `learning_activities/` are strictly read-only relative to `competency_profiles.current_level`.
- **Authoritative paths:** Authorized writes occur exclusively within `capability_assessments/service.py`, `adaptive_assessments/service.py`, and initial onboarding `assessments/service.py`.

---

## 7. Ownership & RBAC

- **Trainers:**
  - Own uploaded materials, AI question drafts, review statuses, and authored quizzes.
  - Cross-trainer isolation: Trainer A cannot modify, approve, or publish Trainer B's questions or quizzes.
  - Cannot take quizzes or manipulate learner attempts.
- **Officials / Learners:**
  - Can take self-service practice quizzes, assigned trainer quizzes, capability assessments, and adaptive assessments.
  - User isolation: Officials cannot view, submit, or finalize another user's session or attempt (enforced with HTTP 404/403).
  - Cannot publish trainer quizzes or escalate access roles.
- **Admins:**
  - Govern organizational intelligence, capacity planning, and user role configuration.

---

## 8. Lifecycle

```
[TRAINER AUTHORING]
Material Uploaded (READY) -> AI Question Draft (GENERATED) -> Trainer Review (APPROVED/REJECTED) -> Quiz Draft (DRAFT) -> Published (PUBLISHED) -> Assigned (ASSIGNED)

[LEARNER PRACTICE]
Start Quiz -> Answer -> Submit -> Scored (PERCENTAGE) -> SUPPORTING Evidence Logged -> Profile Unchanged

[FORMAL / ADAPTIVE EVALUATION]
Start Session -> Dynamic/Curated Questions -> Answer Calibration -> Finalize -> AUTHORITATIVE Evidence Logged -> Profile Updated -> Skill Gap Recalculated -> Cache Invalidated
```

---

## 9. Idempotency

- Submitting an already submitted practice quiz (`POST /quizzes/{id}/submit`) -> **HTTP 409 Conflict**.
- Submitting an already submitted capability assessment (`POST /capability-assessments/{id}/submit`) -> **HTTP 409 Conflict**.
- Finalizing an already completed adaptive session (`POST /adaptive-assessments/{id}/finalize`) -> **HTTP 409 Conflict** (via `evidence_id` / `completed_at` guard).
- Double submissions never result in duplicate evidence records or double competency level increments.

---

## 10. Trainer Assessment Studio Behavior

- **Grounding & Review:** Uploaded materials are chunked and embedded. MCQs generated by AI are validated against source chunks via `GroundingValidator` and stored in `trainer_questions` in `GENERATED` status.
- **Human In the Loop:** Trainers edit and approve questions. Only `APPROVED` questions can form a quiz draft.
- **Evidence Designation:** Quizzes taken by learners produce `SUPPORTING` evidence, serving formative learning without prematurely altering authoritative competency ratings.

---

## 11. 10/5/3/2 Enforcement Status

- **Audit Finding:** Generic quiz generation and trainer review support variable question counts (1–10) with flexible difficulty distribution for modular learning units.
- **Contract:** Trainer quiz authoring validates that all included questions are in `APPROVED` status before drafting or publishing. Formal standardized benchmarks follow configured battery sizes in `assessment_configurations`.

---

## 12. Duplicate Models & Collections

- `quizzes` (self-service) vs `trainer_quizzes` (trainer-governed): Kept distinct to preserve learner autonomy without polluting trainer curriculum governance.
- `quiz_attempts`: Shared canonical store for learner quiz execution across both self-service and trainer-assigned flows.
- `competency_evidence`: Single canonical append-only evidence ledger for all assessments.

---

## 13. API Compatibility

All existing routes remain backward-compatible:
- `/api/v1/quizzes/*`
- `/api/v1/capability-assessments/*`
- `/api/v1/adaptive-assessments/*`
- `/api/v1/assessments/*`
- `/api/v1/trainer/*`

---

## 14. Frontend Semantics

- **Practice Quizzes (`OfficialQuizzes.tsx`):** Clearly presented as formative practice checks.
- **Formal Assessments (`OfficialAssessments.tsx`):** Formal capability and adaptive evaluations clearly communicating authoritative profile updates.
- **Trainer Studio (`TrainerQuizStudio.tsx`, `TrainerQuestionReview.tsx`):** Dedicated workflows for question curation, editing, and publishing.

---

## 15. Files Changed

1. `backend/app/adaptive_assessments/service.py`
   - Added duplicate finalization guard (`evidence_id` / `completed_at` check) returning HTTP 409 Conflict.
2. `backend/tests/test_assessment_architecture_consolidation.py`
   - New comprehensive 9-test consolidation suite covering all assessment invariants.

---

## 16. Tests Added

Created `backend/tests/test_assessment_architecture_consolidation.py`:
1. `test_01_practice_quiz_creates_supporting_evidence_and_no_profile_mutation`
2. `test_02_formal_capability_assessment_creates_authoritative_evidence_and_mutates_profile`
3. `test_03_adaptive_assessment_creates_authoritative_irt_evidence_and_updates_profile`
4. `test_04_duplicate_finalization_is_idempotent_and_rejects_duplicate_runs`
5. `test_05_trainer_ownership_and_official_access_controls`
6. `test_06_user_isolation_on_assessment_attempts`
7. `test_07_score_type_semantics_preserved`
8. `test_08_evidence_immutability_and_audit_trail`
9. `test_09_official_cannot_finalize_another_users_adaptive_session`

---

## 17. Test Results

```
================ 373 passed, 4 skipped, 96 warnings in 34.45s =================
```
- **Passed:** 373
- **Skipped:** 4 (Live LLM tests requiring external API keys)
- **Failed:** 0
- **Regressions:** 0

---

## 18. Frontend Check

```powershell
Push-Location frontend
npm run check
# Output: tsc --noEmit -> Exit Code 0 (Passed)
Pop-Location
```

---

## 19. Frontend Build

```powershell
Push-Location frontend
npm run build
# Output: vite build && esbuild -> built in 6.22s -> Exit Code 0 (Passed)
Pop-Location
```

---

## 20. Remaining Architectural Limitations

1. **Synchronous IRT Stepping:** Adaptive assessment updates theta synchronously per question response. High concurrency is supported via lightweight in-memory theta estimation with atomic MongoDB session writes.
2. **Standardized Calibration:** IRT difficulty calibration currently uses discrete 3-tier mapping (`EASY`, `MEDIUM`, `HARD`) mapped to continuous theta steps in `[1.0, 5.0]`. Future phases can introduce item discrimination and pseudo-guessing parameters ($a, c$ parameters in 3PL model) as empirical civil service attempt volume scales.
