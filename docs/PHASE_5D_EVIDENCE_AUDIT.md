# PHASE 5D — EVIDENCE GOVERNANCE & COMPETENCY AUTHORITY AUDIT

**Date:** 2026-09-06  
**Auditor:** Antigravity (Google DeepMind)  
**System:** ShikshaSetu Core Backend

---

## 1. Executive Summary

This audit evaluates all backend ingestion, calculation, and persistence pathways that interact with `competency_evidence` and `competency_profiles`.

The primary data-integrity objective is ensuring that:
- **Supporting Evidence** (learning completions, course completions, self-service AI quizzes, practice quizzes, trainer-reviewed quizzes) records learner engagement and demonstration of knowledge without directly mutating official competency profiles.
- **Authoritative Evidence** (formal capability assessments, adaptive IRT assessments, baseline department declarations) formally updates `competency_profiles.current_level` and `confidence` (0.85) and recalculates workforce skill gaps.

---

## 2. Comprehensive Evidence Audit Matrix

| Source / Subsystem | Evidence Type | Authority | Direct Profile Mutation? | Evidence Confidence | Correct Behavior? | Current State / Required Invariant |
| :--- | :--- | :--- | :---: | :---: | :---: | :--- |
| **`app/quizzes/service.py`** (Self-Service / AI Quiz) | `QUIZ` / `AI_GENERATED_QUIZ` | `SUPPORTING` | **NO** | `0.30` | **CORRECT** | `_update_competency_deterministic` removed; raw `PERCENTAGE` score preserved; profile level unchanged; supporting evidence logged. |
| **`app/learning_activities/service.py`** (Material Reading / Video) | `LEARNING_ACTIVITY` | `SUPPORTING` | **NO** | `0.30` | **CORRECT** | Creates supporting evidence on 100% progress completion; does not write to `competency_profiles`. |
| **`app/capability_assessments/service.py`** (Formal Assessment) | `CAPABILITY_ASSESSMENT` / `KNOWLEDGE_TEST` | `AUTHORITATIVE` | **YES** | `0.85` | **CORRECT** | Calculates weighted score and mapped proficiency level; updates profile and skill gaps; excludes supporting quizzes from formal capability aggregation. |
| **`app/adaptive_assessments/service.py`** (IRT Adaptive Engine) | `ADAPTIVE_CAPABILITY_ASSESSMENT` | `AUTHORITATIVE` | **YES** | `0.85` | **CORRECT** | Uses 2PL/3PL IRT engine to estimate theta ($0.0 - 5.0$); updates `competency_profiles` with confidence `0.85`; recalculates skill gaps. |
| **`app/assessments/service.py`** (Assessment Engine Prototype) | `FORMAL_CAPABILITY_ASSESSMENT` | `AUTHORITATIVE` | **YES** | `0.85` | **CORRECT** | Standard prototype assessment service updates profile upon passing submission. |
| **`app/users/router.py`** (`/users/me/evidence`) | `BASELINE_ASSESSMENT` (Onboarding seed) | `AUTHORITATIVE` | **YES** (via initial seed) | `0.85` | **CORRECT** | Seeds initial departmental role baseline; returns evidence tagged with correct authority classification. |
| **`app/trainer/router.py`** (Trainer Quiz Review / Studio) | `TRAINER_REVIEWED_QUIZ` | `SUPPORTING` | **NO** | `0.30` | **CORRECT** | Trainer review establishes content governance and item-bank validation; learner attempts remain supporting evidence unless configured into a formal capability assessment. |

---

## 3. Subsystem Authority Semantics

### 1. Quizzes Subsystem (`backend/app/quizzes/`)
- **Purpose:** Self-service learning verification and practice on uploaded learning materials.
- **Input:** Learner answers to multiple-choice questions.
- **Output:** Raw score percentage, answer explanations, supporting evidence log.
- **Authority:** `SUPPORTING`
- **Profile Mutation:** Forbidden.

### 2. Learning Activities Subsystem (`backend/app/learning_activities/`)
- **Purpose:** Tracking course progress and learning material engagement.
- **Input:** Reading/video time and completion status.
- **Output:** Activity log, supporting evidence record.
- **Authority:** `SUPPORTING`
- **Profile Mutation:** Forbidden.

### 3. Capability Assessments Subsystem (`backend/app/capability_assessments/`)
- **Purpose:** Multi-component formal competency evaluation (knowledge test, scenario test).
- **Input:** Formal assessment attempt scores.
- **Output:** Capability assessment certificate/record, profile level update, skill gap update.
- **Authority:** `AUTHORITATIVE`
- **Profile Mutation:** Allowed.

### 4. Adaptive Assessments Subsystem (`backend/app/adaptive_assessments/`)
- **Purpose:** Item Response Theory (IRT) adaptive capability testing.
- **Input:** Adaptive question responses (dichotomous / polytomous).
- **Output:** Latent trait theta estimation, demonstrated proficiency level ($0.0 - 5.0$), profile level update.
- **Authority:** `AUTHORITATIVE`
- **Profile Mutation:** Allowed.

---

## 4. Write Classification on `competency_profiles`

| Write Location | Call Site | Classification | Status |
| :--- | :--- | :--- | :--- |
| `app.adaptive_assessments.service:finalize_session` | `self.db.competency_profiles.update_one` | A. Authoritative & Valid | Active & Enforced |
| `app.capability_assessments.service:evaluate_capability` | `database.competency_profiles.update_one` | A. Authoritative & Valid | Active & Enforced |
| `app.assessments.service:submit_assessment` | `database.competency_profiles.update_one` | A. Authoritative & Valid | Active & Enforced |
| `app.roles.resolver:assign_role` | `database.competency_profiles.update_one` | C. Admin/Baseline Operation | Active & Enforced |
| `app.scripts.seed_master:seed_competency_profiles` | `database.competency_profiles.insert_many` | D. Seed Data | Active & Enforced |
| `app.quizzes.service:_update_competency_deterministic` | (Previous implementation) | B. Incorrect Supporting Update | **REMOVED** |

---

## 5. Security & Ownership Invariants

1. **Client Authority Tampering Prevention:** Clients cannot pass `"authority": "AUTHORITATIVE"` to promote their own evidence; the authority is strictly derived on the backend based on the endpoint and internal assessment configuration.
2. **User Isolation:** All evidence and profile mutations strictly scope by `user_id` authenticated via JWT claims. User A cannot submit quizzes or assessments for User B.
3. **Traceability:** Every ledger record maintains `evidence_type`, `authority`, `score_type`, `confidence`, and `recorded_at` for full historical audits.
