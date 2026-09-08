# PHASE 5F — ASSESSMENT ARCHITECTURE AUDIT

**Timestamp:** 2026-09-06  
**Auditor:** Antigravity AI Engineering Team  
**Scope:** `backend/app/assessments/`, `backend/app/capability_assessments/`, `backend/app/adaptive_assessments/`, `backend/app/quizzes/`, `backend/app/trainer/`

---

## 1. Executive Summary

ShikshaSetu maintains four distinct assessment modules plus the Trainer Assessment Studio. Each serves a distinct stage in the Karmayogi capability lifecycle:
1. **Self-Service / Practice Quizzes (`quizzes/`):** Practice knowledge checks generating **SUPPORTING** evidence with 0.30 weight and percentage scores without mutating the official competency profile.
2. **Formal Capability Assessments (`capability_assessments/`):** Fixed-form multidimensional knowledge evaluations mapped to curated question banks, generating **AUTHORITATIVE** evidence and updating official competency profiles.
3. **Adaptive Capability Assessments (`adaptive_assessments/`):** Real-time Item Response Theory (IRT) dynamic adaptive evaluations, generating **AUTHORITATIVE** evidence (0.85 weight) and updating official competency profiles.
4. **Initial Diagnostic Baseline (`assessments/`):** Multi-component diagnostic assessment (self-rating, MCQ, scenario, training evidence) used during onboarding calibration.
5. **Trainer Assessment Studio (`trainer/`):** Trainer-governed lifecycle (material upload -> AI question generation -> human review/editing/approval -> quiz drafting -> publishing & learner assignment -> trainer qualitative feedback).

---

## 2. Assessment Subsystem Audit Table

| Subsystem | Purpose | Score Type | Evidence Authority | Profile Mutation | Owner | Overlap | Action |
|---|---|---|---|---|---|---|---|
| **quizzes/** | Self-service practice & learner quiz attempts | `PERCENTAGE` (0–100%) | `SUPPORTING` (0.30 weight) | **NO** (Immutable profile) | Official / Learner | Consumes trainer-assigned quizzes; distinct from formal tests | Preserve as practice/supporting check |
| **capability_assessments/** | Formal multi-item capability evaluation | `NORMALIZED_SCORE` (1.0–5.0) | `AUTHORITATIVE` (0.85 weight) | **YES** (Recalculates profile) | Official / System | Question bank scoring overlap with adaptive assessments | Retain as standard fixed-form authoritative evaluation |
| **adaptive_assessments/** | Real-time IRT theta adaptive assessment | `IRT_THETA` (1.0–5.0 level) | `AUTHORITATIVE` (0.85 weight) | **YES** (Direct level update) | Official / System | Uses same `question_bank` items dynamically | Retain as dynamic adaptive authoritative evaluation |
| **assessments/** | Diagnostic multi-component baseline assessment | `WEIGHTED_SCORE` (1.0–5.0) | `AUTHORITATIVE` (Baseline calibration) | **YES** (Baseline initialization) | Official / System | Pre-dates modular capability assessments | Retain for diagnostic baseline calibration |
| **trainer/** | Trainer Question Review Studio & Quiz Publishing | N/A (Review & Governance) | `SUPPORTING` (when attempted by learners) | **NO** | Trainer | Bridges trainer materials to learner quizzes | Retain full trainer authoring & review workflow |

---

## 3. Detailed Subsystem Audit

### A. Quizzes Subsystem (`backend/app/quizzes/`)
1. **Purpose:** Self-service practice knowledge checks and trainer-assigned quiz attempts.
2. **API Endpoints:**
   - `GET /api/v1/quizzes/assigned`
   - `POST /api/v1/quizzes`
   - `GET /api/v1/quizzes/{quiz_id}`
   - `POST /api/v1/quizzes/{quiz_id}/submit`
3. **Data Collections:** `quizzes`, `quiz_attempts`, `competency_evidence`
4. **Models & Schemas:** `Quiz`, `QuizAttempt`, `QuizCreateRequest`, `QuizSubmitRequest`, `QuizResultResponse`
5. **Scoring Mechanism:** Server-side percentage score: `(correct_count / total_questions) * 100`.
6. **Question Source:** Document chunks from uploaded materials or user-defined questions.
7. **Owner:** Learner (self-created) or Trainer (assigned).
8. **Who Can Take:** Officials (`OFFICIAL`, `EMPLOYEE`).
9. **Trainer Review Required:** Only for Trainer Studio quizzes; not for self-service practice.
10. **Evidence Created:** `competency_evidence` (`evidence_type="QUIZ"`, `authority="SUPPORTING"`, `confidence=0.30`, `score_type="PERCENTAGE"`).
11. **Evidence Authority:** `SUPPORTING`.
12. **Competency Profile Modification:** **NONE.** Explicitly guarded in `QuizService.submit_quiz`.
13. **Skill-Gap Recalculation:** Returns current gap without mutation.
14. **Finalization / Idempotency:** Submitting an already submitted quiz returns HTTP 409 Conflict.
15. **Duplicate Functionality:** Distinct from capability assessments (only practice/supporting evidence).

---

### B. Capability Assessments Subsystem (`backend/app/capability_assessments/`)
1. **Purpose:** Formal multi-item capability assessment against curated competency question banks.
2. **API Endpoints:**
   - `POST /api/v1/capability-assessments/create`
   - `GET /api/v1/capability-assessments/{assessment_id}`
   - `POST /api/v1/capability-assessments/{assessment_id}/submit`
   - `GET /api/v1/capability-assessments/history/me`
   - `GET /api/v1/capability-assessments/competencies/available`
3. **Data Collections:** `capability_assessments`, `question_bank`, `competency_evidence`, `competency_profiles`
4. **Models & Schemas:** `CapabilityAssessment`, `CapabilityAssessmentCreateRequest`, `CapabilityAssessmentSubmitRequest`
5. **Scoring Mechanism:** Percentage mapped to 1.0–5.0 normalized score scale.
6. **Question Source:** `question_bank` items filtered by competency code.
7. **Owner:** Learner attempt on system-configured assessments.
8. **Who Can Take:** Officials.
9. **Trainer Review Required:** No (curated standard bank).
10. **Evidence Created:** `competency_evidence` (`evidence_type="KNOWLEDGE_TEST"`, `authority="AUTHORITATIVE"`, `confidence=0.85`, `score_type="NORMALIZED_SCORE"`).
11. **Evidence Authority:** `AUTHORITATIVE`.
12. **Competency Profile Modification:** **YES.** Updates `current_level` and `confidence` in `competency_profiles`.
13. **Skill-Gap Recalculation:** Triggered dynamically through updated competency profile.
14. **Finalization / Idempotency:** Submitting an already submitted assessment returns HTTP 409 Conflict.
15. **Duplicate Functionality:** Complementary to adaptive assessments for standard fixed-form testing.

---

### C. Adaptive Assessments Subsystem (`backend/app/adaptive_assessments/`)
1. **Purpose:** Real-time Item Response Theory (IRT) adaptive capability testing with dynamic theta step-calibration.
2. **API Endpoints:**
   - `POST /api/v1/adaptive-assessments/start`
   - `POST /api/v1/adaptive-assessments/{session_id}/answer`
   - `POST /api/v1/adaptive-assessments/{session_id}/finalize`
   - `GET /api/v1/adaptive-assessments/{session_id}`
3. **Data Collections:** `adaptive_assessment_sessions`, `question_bank`, `competency_evidence`, `competency_profiles`
4. **Models & Schemas:** `AdaptiveStartRequest`, `AdaptiveAnswerRequest`, `AdaptiveFinalizeResponse`
5. **Scoring Mechanism:** Calibrated IRT theta step-up/down logic bounded in `[1.0, 5.0]`.
6. **Question Source:** Dynamic selection from `question_bank` by difficulty tier (`EASY`, `MEDIUM`, `HARD`).
7. **Owner:** Learner session on system test.
8. **Who Can Take:** Officials.
9. **Trainer Review Required:** No.
10. **Evidence Created:** `competency_evidence` (`evidence_type="CAPABILITY_ASSESSMENT"`, `authority="AUTHORITATIVE"`, `confidence=0.85`, `score_type="IRT_THETA"`).
11. **Evidence Authority:** `AUTHORITATIVE`.
12. **Competency Profile Modification:** **YES.** Sets `current_level` to final calibrated theta and `confidence=0.85`.
13. **Skill-Gap Recalculation:** Explicitly recalculates skill gaps and invalidates recommendation cache upon finalization.
14. **Finalization / Idempotency:** Guarded against duplicate finalization via HTTP 409 Conflict check.
15. **Duplicate Functionality:** Unique adaptive IRT engine.

---

### D. Initial Diagnostic Assessments (`backend/app/assessments/`)
1. **Purpose:** Diagnostic multi-source onboarding assessment (self-rating, knowledge test, scenario test, training records).
2. **API Endpoints:**
   - `POST /api/v1/assessments`
   - `GET /api/v1/assessments/{attempt_id}`
   - `POST /api/v1/assessments/{attempt_id}/submit`
   - `GET /api/v1/assessments/configurations`
3. **Data Collections:** `assessments`, `assessment_attempts`, `competency_evidence`, `competency_profiles`
4. **Models & Schemas:** `StartAssessmentRequest`, `SubmitAssessmentRequest`, `AssessmentAttemptResponse`
5. **Scoring Mechanism:** Weighted composite (0.10 self + 0.40 knowledge + 0.30 scenario + 0.20 training).
6. **Question Source:** Hardcoded/seeded multidimensional question sets in `assessments`.
7. **Owner:** System diagnostic.
8. **Who Can Take:** Officials.
9. **Trainer Review Required:** No.
10. **Evidence Created:** `competency_evidence` (`source="initial_assessment"`, `authority="AUTHORITATIVE"`).
11. **Evidence Authority:** `AUTHORITATIVE`.
12. **Competency Profile Modification:** **YES.** Initializes baseline profile.
13. **Skill-Gap Recalculation:** Implicit on subsequent gap calculation.
14. **Finalization / Idempotency:** Submitting non-in-progress attempt returns HTTP 409 Conflict.
15. **Duplicate Functionality:** Historical prototype assessment retained for initial onboarding diagnostics.

---

### E. Trainer Assessment Studio (`backend/app/trainer/`)
1. **Purpose:** Full trainer authoring lifecycle: upload materials, trigger AI RAG question generation, review/edit/approve questions in Review Studio, draft quizzes, publish and assign to officials, review official attempts and issue qualitative feedback.
2. **API Endpoints:**
   - `POST /api/v1/trainer/materials/{material_id}/generate-questions`
   - `GET /api/v1/trainer/questions`
   - `PUT /api/v1/trainer/questions/{question_id}`
   - `POST /api/v1/trainer/questions/{question_id}/review`
   - `POST /api/v1/trainer/quizzes`
   - `POST /api/v1/trainer/quizzes/{quiz_id}/publish`
   - `POST /api/v1/trainer/quizzes/{quiz_id}/assign`
   - `GET /api/v1/trainer/quizzes/{quiz_id}/attempts`
   - `POST /api/v1/trainer/attempts/{attempt_id}/feedback`
3. **Data Collections:** `learning_materials`, `document_chunks`, `trainer_questions`, `trainer_quizzes`, `quiz_attempts`
4. **Evidence Authority:** Quizzes created in Trainer Studio generate **SUPPORTING** evidence when taken by officials.
5. **Profile Mutation:** **NO.** Trainer quizzes do not directly overwrite civil servant competency ratings.

---

## 4. Key Boundaries & Architectural Invariants

1. **Scoring Separation:**
   - `PERCENTAGE` scores (0–100%) remain strictly percentage in practice quizzes.
   - `IRT_THETA` levels (1.0–5.0) remain strictly continuous proficiency metrics.
   - `NORMALIZED_SCORE` levels (1.0–5.0) represent bounded competency scores.
2. **Authority Contract:**
   - `SUPPORTING` evidence: Practice quizzes and learning activity completions (Confidence: 0.30). NEVER mutates `competency_profiles`.
   - `AUTHORITATIVE` evidence: Formal Capability Assessments and Adaptive IRT Assessments (Confidence: 0.85). Mutates `competency_profiles`.
3. **Idempotency Invariant:**
   - Submitting/finalizing any assessment twice returns HTTP 409 Conflict across all four subsystems without creating duplicate evidence records or double-updating profiles.
4. **RBAC Isolation:**
   - Trainers cannot take quizzes or modify other trainers' quizzes.
   - Officials cannot publish trainer quizzes or finalize another user's attempt.
   - Unauthenticated callers cannot access any assessment endpoint.
