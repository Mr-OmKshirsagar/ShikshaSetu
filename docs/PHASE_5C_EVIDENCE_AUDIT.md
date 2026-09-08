# Phase 5C — Evidence Governance & Competency Authority Audit

**Audit Date:** 2026-09-06  
**Auditor:** Antigravity Engineering & Security Remediation Agent  
**Scope:** ShikshaSetu Assessment Subsystems, Evidence Ledger, and Competency Profile Mutators  
**Status:** AUDIT COMPLETE — REMEDIATION MATRIX ESTABLISHED  

---

## 1. Executive Summary

An audit of all assessment, learning activity, and quiz pathways in ShikshaSetu was performed to address the data-integrity issue identified in the product audit:
> *"Evidence governance is not centralized. Some quiz/self-service flows directly modify the official competency profile."*

### Key Invariants
1. **Supporting Evidence (Confidence = 0.30):** Non-formal demonstrations of knowledge (learning activity completion, course completion, self-service practice quizzes, AI-generated quizzes, trainer-reviewed practice quizzes). Supporting evidence **MUST NOT** mutate `competency_profiles.current_level` or authoritative confidence.
2. **Authoritative Evidence (Confidence = 0.85):** Formal capability assessments, multi-component diagnostic assessments, and adaptive IRT assessments. Only authoritative assessments **MAY** update `competency_profiles.current_level`, set `confidence = 0.85`, and trigger skill-gap recalculation.

---

## 2. Assessment Pathways & Evidence Audit Matrix

| Evidence Source | Evidence Type | Authority Class | Can Change Profile? (Current) | Should Change Profile? | Confidence | Current Behavior | Required Change |
|---|---|---|---|---|---|---|---|
| **Self-Service Practice Quiz** (`/quizzes/{id}/submit`) | `QUIZ` / `PRACTICE_QUIZ` | **SUPPORTING** | **YES (VULNERABILITY)** | **NO** | 0.30 (current: 0.3-0.9) | `_update_competency_deterministic` mapped percentage (0-100%) to levels 1.5-4.5 and directly updated `competency_profiles` | Remove direct profile mutation; record as immutable supporting evidence (`confidence = 0.30`, `authority = SUPPORTING`); keep profile level unchanged |
| **AI-Generated Practice Quiz** (`/quizzes/{id}/submit`) | `AI_GENERATED_QUIZ` | **SUPPORTING** | **YES (VULNERABILITY)** | **NO** | 0.30 | Same as self-service quiz | Remove direct profile mutation; record as supporting evidence only |
| **Trainer-Reviewed Practice Quiz** (`/quizzes/{id}/submit`) | `TRAINER_REVIEWED_QUIZ` | **SUPPORTING** | **YES (VULNERABILITY)** | **NO** | 0.30 | Same as self-service quiz | Content quality review by trainer does not make learner quiz result authoritative; remove profile mutation |
| **Learning Activity Completion** (`/learning-activities/{id}/complete`) | `LEARNING_ACTIVITY` | **SUPPORTING** | **NO** | **NO** | 0.30 | Records `competency_evidence` document, leaves profile untouched | No change needed (already properly governed) |
| **Multi-Component Initial Assessment** (`/assessments/submit`) | `SELF_ASSESSMENT`, `KNOWLEDGE_TEST`, `SCENARIO_TEST`, `TRAINING` | **AUTHORITATIVE** | **YES** | **YES** | Weighted formula / 0.85 | Aggregates 4 components, writes evidence ledger, updates `competency_profiles` | Preserve formal multi-component scoring & profile update |
| **Formal Capability Assessment** (`/capability-assessments/{id}/submit`) | `KNOWLEDGE_TEST` / `CAPABILITY_ASSESSMENT` | **AUTHORITATIVE** | **YES** | **YES** | 0.85 | Aggregates past evidence, updates `competency_profiles` | Remove aggregation of past `QUIZ` evidence into formal capability score; preserve authoritative profile update |
| **Adaptive IRT Assessment** (`/adaptive-assessments/submit-response`) | `CAPABILITY_ASSESSMENT` / `IRT_THETA` | **AUTHORITATIVE** | **YES** | **YES** | 0.85 | Estimates latent ability theta via IRT MLE/EAP, records evidence, updates `competency_profiles.current_level = theta`, `confidence = 0.85`, recalculates skill gaps | Preserve authoritative IRT scoring & profile update |

---

## 3. Detailed Data Flow Analysis per Subsystem

### 3.1 Self-Service Quiz Pathway (`backend/app/quizzes/`)
- **User Action:** Official submits answers to a generated or assigned practice quiz.
- **Evidence Created:** `competency_evidence` record with score type `PERCENTAGE`.
- **Flawed Code:** `QuizService._update_competency_deterministic` in `backend/app/quizzes/service.py` directly called `upsert_profile(...)` with deterministic steps (e.g. >=80% $\to$ level 4.5, confidence 0.9).
- **Remediation:** Remove `_update_competency_deterministic` execution. Record supporting evidence with `confidence = 0.30` and `authority = SUPPORTING`. Profile level and confidence remain strictly unchanged.

### 3.2 Learning Activities Pathway (`backend/app/learning_activities/`)
- **User Action:** Official marks learning module or course as completed.
- **Evidence Created:** Record inserted into `competency_evidence` with `type = "LEARNING_ACTIVITY"`, `confidence = 0.30`.
- **Competency Profile:** Preserved without mutation (`current_level` unchanged).
- **Status:** Verified compliant.

### 3.3 Formal Initial Assessment Pathway (`backend/app/assessments/`)
- **User Action:** Official completes formal diagnostic baseline assessment.
- **Evidence Created:** Detailed component records (`SELF_ASSESSMENT`, `KNOWLEDGE_TEST`, `SCENARIO_TEST`, `TRAINING`).
- **Competency Profile:** Updates `competency_profiles.current_level` and `confidence` using weighted psychometric formula.
- **Status:** Verified compliant authoritative path.

### 3.4 Adaptive Assessment Pathway (`backend/app/adaptive_assessments/`)
- **User Action:** Official completes Item Response Theory (IRT) adaptive assessment session.
- **Evidence Created:** `competency_evidence` record with `score_type = "IRT_THETA"`, `confidence = 0.85`.
- **Competency Profile:** Updates `competency_profiles.current_level` to calibrated latent ability $\theta \in [1.0, 5.0]$ with `confidence = 0.85` and updates skill gaps.
- **Status:** Verified compliant authoritative path.

### 3.5 Evidence Retrieval Endpoint (`/users/me/evidence` in `backend/app/users/router.py`)
- **Finding:** Was categorizing `"QUIZ"` as `is_authoritative = True` and assigning default confidence `0.85`.
- **Remediation:** Explicitly classify `QUIZ`, `PRACTICE_QUIZ`, `AI_GENERATED_QUIZ`, `LEARNING_ACTIVITY` as `SUPPORTING` (`confidence = 0.30`).

---

## 4. Canonical Authority Enums & Constants

To be defined in `backend/app/competencies/models.py`:
- `EvidenceAuthority.SUPPORTING` (`"SUPPORTING"`)
- `EvidenceAuthority.AUTHORITATIVE` (`"AUTHORITATIVE"`)
- `AUTHORITATIVE_CONFIDENCE = 0.85`
- `SUPPORTING_CONFIDENCE = 0.30`
