# PHASE 5D — EVIDENCE GOVERNANCE & COMPETENCY AUTHORITY REMEDIATION REPORT

**Status:** Successfully Remediated & Verified  
**Date:** 2026-09-06  
**Repository:** ShikshaSetu (Government of India Competency & Training Platform)

---

## 1. Current Evidence Architecture

The ShikshaSetu platform manages civil service capability development and gap analytics across several subsystems:
- **`app/quizzes/`**: Practice and self-service quizzes generated from uploaded learning materials or assigned by trainers.
- **`app/learning_activities/`**: Engagement tracking for courses, documents, and videos.
- **`app/capability_assessments/`**: Multi-dimensional formal capability assessments (knowledge tests, scenario tests).
- **`app/adaptive_assessments/`**: Computerized Adaptive Testing (CAT) based on Item Response Theory (IRT 2PL/3PL models).
- **`app/competencies/`**: Canonical competency taxonomy, competency profiles, and immutable evidence ledger.
- **`app/skill_gaps/`**: Real-time role gap calculation based on official required levels versus assessed profile levels.

---

## 2. Vulnerability Found

- **Profile Escalation via Practice Quizzes:** Any authenticated official taking a self-service or AI-generated quiz could achieve a high percentage score (e.g. 100%), which immediately triggered a deterministic update function (`_update_competency_deterministic`).
- **Arbitrary Level Jump:** This mapped percentage ranges directly to high competency levels (e.g., Level 4.5/5.0 with confidence 0.90), altering `competency_profiles.current_level` and artificially clearing official civil service skill gaps without formal evaluation.

---

## 3. Root Cause

- **Conflation of Engagement with Certification:** The codebase did not maintain a distinction between **Supporting Evidence** (demonstrations of knowledge/practice) and **Authoritative Evidence** (formal standardized assessments).
- **Decentralized Mutation Pathways:** Multiple modules had direct write access to `competency_profiles` without going through an authority validation gate.

---

## 4. Evidence Authority Model

Defined canonical evidence authority enums and mappings in `backend/app/competencies/models.py`:

| Authority Class | Evidence Types Included | Mutates `competency_profiles`? | Confidence Value | Recalculates Skill Gaps? |
| :--- | :--- | :---: | :---: | :---: |
| **`SUPPORTING`** | `LEARNING_ACTIVITY`, `LEARNING_COMPLETION`, `PRACTICE_QUIZ`, `AI_GENERATED_QUIZ`, `TRAINER_REVIEWED_QUIZ`, `QUIZ`, `TRAINING`, `SELF_ASSESSMENT` | **NO** | `0.30` | No (reflects unmutated profile) |
| **`AUTHORITATIVE`** | `FORMAL_CAPABILITY_ASSESSMENT`, `ADAPTIVE_CAPABILITY_ASSESSMENT`, `CAPABILITY_ASSESSMENT`, `KNOWLEDGE_TEST`, `SCENARIO_TEST`, `BASELINE_ASSESSMENT` | **YES** | `0.85` | Yes (gap = required - new level) |

---

## 5. Files Changed

1. **`backend/app/competencies/models.py`**:
   - Defined `EvidenceAuthority` (`SUPPORTING`, `AUTHORITATIVE`) and `EvidenceType` enums.
   - Defined `AUTHORITATIVE_EVIDENCE_TYPES` and standard confidence constants (`AUTHORITATIVE_CONFIDENCE = 0.85`, `SUPPORTING_CONFIDENCE = 0.30`).
2. **`backend/app/quizzes/service.py`**:
   - Removed `_update_competency_deterministic()`.
   - Quiz submission logs `SUPPORTING` evidence (`confidence = 0.30`, `score_type = "PERCENTAGE"`) and preserves profile level with `improvement = 0.0`.
3. **`backend/app/quizzes/repository.py`**:
   - Hardened `get_quiz_by_id` query logic for ObjectId and string IDs.
4. **`backend/app/capability_assessments/service.py`**:
   - Excluded `"QUIZ"` supporting evidence from formal capability score aggregation.
   - Tagged capability assessment evidence with `authority = "AUTHORITATIVE"` and `confidence = 0.85`.
5. **`backend/app/adaptive_assessments/service.py`**:
   - Added robust competency ID/code resolution fallback in `finalize_session()`.
6. **`backend/app/users/router.py`**:
   - Corrected `/users/me/evidence` endpoint to classify quiz and learning activities as `SUPPORTING` (`confidence = 0.30`).
7. **`backend/tests/test_evidence_governance.py`**:
   - Added exhaustive unit & integration tests covering all 21 Phase 5D requirements, including the mandatory Step 14 regression scenario.
8. **`backend/tests/test_quizzes.py`**:
   - Updated quiz test assertions to verify that quiz completion does not mutate competency profile level.
9. **`frontend/client/src/pages/LiveHome.tsx`**:
   - Updated quiz result card to display "Current Level" with clear governance notes.

---

## 6. Quiz Behavior: Before vs After

| Dimension | Before Remediation | After Remediation |
| :--- | :--- | :--- |
| **Profile Mutation** | Level jumped to 1.5–4.5 based on quiz score | **Unchanged** (profile remains at authoritative level) |
| **Profile Confidence** | Overwritten to 0.80–0.90 | **Unchanged** |
| **Evidence Authority** | Implicit / Untyped | `SUPPORTING` |
| **Evidence Confidence** | Variable / Untracked | `0.30` |
| **Score Type** | Untyped float | `PERCENTAGE` ($0.0 - 100.0\%$) |
| **User Feedback** | "Competency improved to 4.5" | "Knowledge demonstrated. Supporting evidence recorded (confidence 0.30)." |

---

## 7. Formal Assessment Behavior: Before vs After

| Dimension | Before Remediation | After Remediation |
| :--- | :--- | :--- |
| **Adaptive Assessment** | Updated profile level | Updates profile level + sets `confidence = 0.85` + recalculates skill gaps |
| **Capability Assessment** | Contaminated by quiz scores | Formal scoring isolated from supporting quizzes + updates profile + sets `confidence = 0.85` |
| **Evidence Authority** | Implicit | `AUTHORITATIVE` |
| **Score Type** | `IRT_THETA` / `PROFICIENCY_LEVEL` | `IRT_THETA` / `PROFICIENCY_LEVEL` ($0.0 - 5.0$) |

---

## 8. Profile Mutation Authority

Single Responsible Authority Boundary:
- `competency_profiles.current_level` and `competency_profiles.confidence` can **ONLY** be modified by:
  1. `app.adaptive_assessments.service:finalize_session`
  2. `app.capability_assessments.service:evaluate_capability`
  3. `app.assessments.service:submit_assessment`
  4. `app.roles.resolver:assign_role` (Baseline civil service onboarding)
- Self-service quizzes, material reviews, and client requests cannot mutate `competency_profiles`.

---

## 9. Evidence Traceability

Every record in `competency_evidence` provides end-to-end traceability:
```json
{
  "_id": "ObjectId(...)",
  "user_id": "ObjectId(...)",
  "competency_id": "ObjectId(...)",
  "competency_code": "TECH_PYTHON",
  "evidence_type": "QUIZ",
  "authority": "SUPPORTING",
  "score": 92.0,
  "score_type": "PERCENTAGE",
  "confidence": 0.30,
  "source": "AI_QUIZ",
  "quiz_id": "6a91102a...",
  "recorded_at": "2026-09-06T01:45:00Z"
}
```

---

## 10. Security & Ownership Verification

1. **Client Authority Tampering Prevention:** Clients cannot inject `"authority": "AUTHORITATIVE"` in payloads; authority is determined entirely by backend service trust boundaries.
2. **User Isolation:** All operations enforce `user_id` matching authenticated JWT claims. User A cannot view, submit, or mutate User B's evidence or profile.
3. **Immutability:** Historical evidence records are append-only; subsequent formal assessments append new records without deleting previous practice history.

---

## 11. Historical-Data Findings & Migration Notes

- Documented in `PHASE_5D_DATA_MIGRATION_NOTES.md`.
- No historical evidence records were deleted or corrupted.
- A non-destructive reconciliation strategy is documented for production deployment windows if historical profiles need recalibration.

---

## 12. Tests Added

Located in `backend/tests/test_evidence_governance.py`:
- `test_learning_completion_creates_supporting_evidence_and_preserves_profile`
- `test_practice_quiz_and_ai_quiz_do_not_modify_profile`
- `test_step_11_mandatory_vulnerability_scenario` (Step 14 Mandatory Scenario)
- `test_evidence_ledger_immutability_and_user_isolation`
- `test_client_cannot_self_declare_authoritative_authority`
- `test_trainer_reviewed_quiz_remains_supporting`

---

## 13. Test Results

### Backend Pytest Suite:
```bash
..\.venv\Scripts\pytest tests/ -v
```
- **353 Passed**
- **4 Skipped**
- **0 Failed**
- Execution Time: 81.60s

### Frontend Type Check:
```bash
npm run check
# Exit code: 0 (0 type errors)
```

### Frontend Production Build:
```bash
npm run build
# Exit code: 0 (Built successfully in 6.21s)
```

### Git Diff Whitespace / Format Check:
```bash
git diff --check
# Exit code: 0 (Clean)
```

---

## 14. Remaining Governance Limitations

1. **Third-Party External LMS Integration (e.g. iGOT):** External completions currently map into `SUPPORTING` evidence unless explicitly accompanied by a digitally signed government certificate.
2. **Trainer Assessment Studio Distinction:** Trainer-authored quizzes default to `SUPPORTING` evidence; in future phases, a formal "Proctored Examination Mode" flag can be introduced for designated proctored testing centers.
