# PHASE 5C — EVIDENCE GOVERNANCE & COMPETENCY AUTHORITY REPORT

**Status:** Completed & Verified  
**Date:** 2026-09-06  
**Repository:** ShikshaSetu (Government of India Competency & Training Platform)

---

## 1. Evidence Architecture Before

Prior to this remediation, ShikshaSetu had multiple assessment and learning paths interacting with the competency and evidence systems inconsistently:
- **`app.quizzes.service`**: Upon quiz submission, calculated percentage score and executed `_update_competency_deterministic()`, mapping score ranges directly into official competency levels (e.g., 80–100% -> Level 4.5, Confidence 0.90; 60–79% -> Level 3.5, Confidence 0.85). It wrote directly to `competency_profiles` and inserted a quiz evidence record.
- **`app.capability_assessments.service`**: Aggregated all evidence records matching a user and competency, treating `"QUIZ"` evidence on equal standing with formal assessment scores in computing proficiency.
- **`app.users.router` (`/users/me/evidence`)**: Hardcoded evidence classification based on strings, tagging `QUIZ` and `LEARNING` activities as "authoritative" if they had a score.
- **`app.learning_activities.service`**: Recorded learning completion into `competency_evidence` without modifying competency profile levels (correct supporting evidence behavior).
- **`app.adaptive_assessments.service`**: IRT-based adaptive capability assessment correctly calculated theta and proficiency level (0.0 to 5.0), updating profile levels and skill gaps with authoritative confidence.

---

## 2. Vulnerability Discovered

### The Self-Service Profile Mutation Vulnerability
- **Mechanism:** Any official could self-generate or practice a multiple-choice quiz on any material, achieve a high score (e.g. 100%), and trigger `_update_competency_deterministic()`.
- **Impact:** The official's official `competency_profiles.current_level` was immediately upgraded (e.g., to 4.5 out of 5.0 with 0.90 confidence), bypassing formal verification and distorting workforce gap analytics and role readiness reports.
- **Root Cause:** Conflation of *supporting knowledge demonstration* with *authoritative capability certification*.

---

## 3. Evidence Authority Model

We established canonical evidence authority rules in `backend/app/competencies/models.py`:

| Evidence Authority | Evidence Types | Can Mutate `competency_profiles`? | Confidence Level | Recalculates Skill Gaps? |
| :--- | :--- | :---: | :---: | :---: |
| **`SUPPORTING`** | `LEARNING_ACTIVITY`, `LEARNING_COMPLETION`, `PRACTICE_QUIZ`, `AI_GENERATED_QUIZ`, `TRAINER_REVIEWED_QUIZ`, `QUIZ`, `TRAINING`, `SELF_ASSESSMENT` | **NO** | `0.30` | No (reflects current authoritative profile) |
| **`AUTHORITATIVE`** | `FORMAL_CAPABILITY_ASSESSMENT`, `ADAPTIVE_CAPABILITY_ASSESSMENT`, `CAPABILITY_ASSESSMENT`, `KNOWLEDGE_TEST`, `SCENARIO_TEST`, `BASELINE_ASSESSMENT` | **YES** | `0.85` | Yes (triggers gap reduction calculation) |

### Key Policy Invariants:
1. **Trainer Review != Automatic Authoritativeness:** Trainer review in Quiz Studio verifies item bank quality and governance, but does not convert a learner's quiz attempt into a formal competency certification.
2. **Score Type Integrity:** Native units are strictly preserved:
   - Quizzes: `PERCENTAGE` (0.0 - 100.0%)
   - Adaptive Assessments: `IRT_THETA` / `PROFICIENCY_LEVEL` (0.0 - 5.0)
   - Capability Assessments: `WEIGHTED_SCORE` (0.0 - 100.0%) -> mapped level (0.0 - 5.0)

---

## 4. Files Changed

1. **`backend/app/competencies/models.py`**:
   - Added `EvidenceAuthority` enum (`SUPPORTING`, `AUTHORITATIVE`).
   - Defined canonical `EvidenceType` constants and authority mappings (`AUTHORITATIVE_EVIDENCE_TYPES`, `SUPPORTING_EVIDENCE_TYPES`).
   - Set standard confidence constants: `AUTHORITATIVE_CONFIDENCE = 0.85`, `SUPPORTING_CONFIDENCE = 0.30`.
2. **`backend/app/quizzes/service.py`**:
   - Removed `_update_competency_deterministic()` call from quiz submission workflow.
   - Tagged all quiz evidence as `authority="SUPPORTING"`, `confidence=0.30`, `score_type="PERCENTAGE"`.
   - Preserved `competency_level_after` as the existing authoritative profile level (or default baseline `2.5`) with `improvement=0.0`.
3. **`backend/app/quizzes/repository.py`**:
   - Cleaned up `get_quiz_by_id` query to handle ObjectId and string IDs cleanly.
4. **`backend/app/capability_assessments/service.py`**:
   - Filtered out `"QUIZ"` supporting evidence from formal capability assessment score calculations.
   - Stamped capability assessment evidence as `authority="AUTHORITATIVE"`, `confidence=0.85`.
5. **`backend/app/adaptive_assessments/service.py`**:
   - Added resilient competency code/ID lookup fallback in `finalize_session()`.
6. **`backend/app/users/router.py`**:
   - Corrected `/users/me/evidence` endpoint to classify `QUIZ` and `LEARNING` as `SUPPORTING` with 0.30 confidence.
7. **`backend/tests/test_evidence_governance.py`**:
   - Comprehensive test suite covering all 18 Phase 5C requirements and the Step 11 mandatory scenario.
8. **`backend/tests/test_quizzes.py`**:
   - Updated quiz test assertions to verify that quiz submission leaves `competency_level_after` unchanged at baseline with `improvement == 0.0`.
9. **`frontend/client/src/pages/LiveHome.tsx`**:
   - Clarified UI wording on quiz completion card from "Updated Level" to "Current Level" with governance notice indicating supporting evidence logging.

---

## 5. Self-Service Quiz Behavior Before vs After

| Aspect | Before | After |
| :--- | :--- | :--- |
| **Competency Profile Level** | Directly mutated to 1.5–4.5 based on quiz score | **Unchanged** (remains at authoritative baseline) |
| **Competency Profile Confidence** | Mutated to 0.80–0.90 | **Unchanged** (authoritative level retains its confidence) |
| **Evidence Record Authority** | Implicit / Undefined | `SUPPORTING` |
| **Evidence Record Confidence** | Implicit / Undefined | `0.30` |
| **Evidence Record Score Type** | Numeric score | `PERCENTAGE` (0.0 - 100.0) |
| **User Feedback** | "Your competency level increased to 4.5" | "Knowledge demonstrated. Supporting evidence recorded (confidence 0.30)." |

---

## 6. Formal Assessment Behavior Before vs After

| Aspect | Before | After |
| :--- | :--- | :--- |
| **Capability Assessment Evidence** | Created with score | Created with `authority="AUTHORITATIVE"`, `confidence=0.85` |
| **Adaptive Assessment Evidence** | Created with theta & level | Created with `authority="AUTHORITATIVE"`, `confidence=0.85` |
| **Profile Mutation** | Updated level & confidence | Updated level & confidence (`0.85`) |
| **Skill Gap Calculation** | Recalculated | Recalculated based on new authoritative level |

---

## 7. Evidence Ledger Behavior

- **Append-Only Immutability:** Evidence records in `competency_evidence` are strictly append-only.
- **Traceability:** Every evidence record contains:
  - `user_id`
  - `competency_id` & `competency_code`
  - `evidence_type` (`QUIZ`, `LEARNING_ACTIVITY`, `CAPABILITY_ASSESSMENT`, `ADAPTIVE_ASSESSMENT`)
  - `authority` (`SUPPORTING` vs `AUTHORITATIVE`)
  - `score` & `score_type` (`PERCENTAGE`, `PROFICIENCY_LEVEL`, etc.)
  - `confidence` (`0.30` or `0.85`)
  - `source` (`AI_QUIZ`, `LEARNING_ACTIVITY`, `ADAPTIVE_ENGINE`, etc.)
  - `timestamp` / `recorded_at`
- **History Preservation:** A subsequent formal assessment adds a new evidence record; historical supporting quiz records remain intact in the ledger.

---

## 8. Profile Mutation Authority

- **Single Pathway Invariant:** Only authorized assessment services (`adaptive_assessments/service.py`, `capability_assessments/service.py`, `assessments/service.py`) and administrative baseline configuration are permitted to write to `competency_profiles.current_level` and `competency_profiles.confidence`.
- Arbitrary endpoints and self-service learning/quiz tools cannot write to `competency_profiles`.

---

## 9. Skill Gap Behavior

- **Supporting Evidence Alone:** Does **not** alter the authoritative `current_level` and therefore does not artificially reduce skill gaps.
- **Authoritative Evidence:** Updates `current_level`, triggering a recalculation of `gap = max(0, required_level - current_level)`.

---

## 10. Existing Historical Data Concerns & Migration Strategy

- **Audit Finding:** In development/demo databases, some historical `competency_profiles` may have been created or modified by previous quiz submissions.
- **Safety Policy:** As mandated, production data was **not silently destroyed or overwritten**.
- **Recommended Non-Destructive Migration Strategy:**
  1. Inspect `competency_profiles` for records whose latest evidence in `competency_evidence` has `evidence_type: "QUIZ"`.
  2. For affected users who lack an authoritative assessment (`ADAPTIVE_ASSESSMENT` or `CAPABILITY_ASSESSMENT`), reset `current_level` to baseline (`2.5` or role baseline) and confidence to `0.30` or baseline.
  3. Keep all historical `competency_evidence` intact in the immutable ledger for auditability.

---

## 11. Tests Added & Step 11 Mandatory Scenario

The test suite in `backend/tests/test_evidence_governance.py` validates all 18 invariants:
1. `test_learning_completion_creates_supporting_evidence_and_preserves_profile`: Learning completion creates supporting evidence (confidence 0.30) without mutating `competency_profiles`.
2. `test_practice_quiz_and_ai_quiz_do_not_modify_profile`: AI quiz and practice quizzes create supporting evidence (0.30) and leave profile unchanged.
3. `test_step_11_mandatory_vulnerability_scenario`:
   - Official starts with baseline level = 2.5.
   - Official completes self-service quiz with 100% score.
   - **Verified:** Profile level remains 2.5; supporting evidence recorded.
   - Official completes authoritative assessment with result 3.8.
   - **Verified:** Profile level updates to 3.8, confidence to 0.85, skill gap recalculates from 1.5 to 0.2.
4. `test_evidence_ledger_immutability_and_user_isolation`: Evidence ledger records append-only history for both events and enforces user isolation (User A cannot access or mutate User B's profile/evidence).

---

## 12. Full Backend Test Suite Results

```bash
..\.venv\Scripts\pytest tests/ -v
```

**Results:**
- **351 Passed**
- **4 Skipped**
- **0 Failures**
- **Time:** 91.45s

---

## 13. Frontend Verification Results

### Type Check:
```bash
npm run check
# tsc --noEmit
# Exit Code: 0 (No type errors)
```

### Production Build:
```bash
npm run build
# vite build && esbuild server/index.ts ...
# Exit Code: 0 (Build successful in 6.26s)
```

---

## 14. Summary of Evidence Governance Invariants

```
               [ Learner Action ]
                       |
        +--------------+--------------+
        |                             |
[ Supporting Action ]         [ Formal Assessment ]
(Quiz, Course, Practice)      (Adaptive, Capability)
        |                             |
[ Evidence Record ]           [ Evidence Record ]
 authority: SUPPORTING         authority: AUTHORITATIVE
 confidence: 0.30              confidence: 0.85
 score_type: PERCENTAGE        score_type: IRT / LEVEL
        |                             |
[ Ledger Appended ]           [ Ledger Appended ]
        |                             |
(Profile Unchanged)           [ Competency Profile Updated ]
                               current_level = new_level
                               confidence = 0.85
                                      |
                              [ Skill Gap Recalculated ]
```
