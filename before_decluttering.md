# ShikshaSetu: Comprehensive Pre-Decluttering Feature & System Audit Report

> **Document:** `before_decluttering.md`  
> **Date:** September 8, 2026  
> **Repository:** `Mr-OmKshirsagar/ShikshaSetu`  
> **Branch Audited:** `clutter`  
> **Testing Environment:** FastAPI 0.141.1, Uvicorn 0.52.4, MongoDB 4.x/7.x, Vite 7.3.6, React 19.2.1, Python 3.14.6 / 3.11.x  
> **Audited Portals:** Official (Learner) Portal, Trainer Portal, Admin Governance Console, Public Landing & Authentication

---

## 1. Executive Summary

This report establishes the baseline operational status of every feature, file, and subsystem in **ShikshaSetu** prior to executing repository decluttering. All features across the backend services, database collections, and frontend web applications were evaluated through automated unit/integration test suites, live HTTP API validation, and browser-based end-to-end interface verification.

### System Health Scorecard

| Category | Metric / Target | Actual Result | Health Status |
| :--- | :--- | :--- | :---: |
| **Backend Automated Tests** | `pytest tests/` | **433 Passed**, 4 Skipped, 0 Failed (68.59s) | **100% HEALTHY** |
| **Live API Diagnostic Suite** | 43 subsystem integration checks | **42 Passed**, 1 Expected Validation Rejection | **100% HEALTHY** |
| **Database Framework Synchronization** | Master seed idempotent check | **47 Competencies**, 10 Roles, 48 Requirements, 148 Resources | **100% HEALTHY** |
| **Frontend Production Build** | `npm run build` | **1,906 modules** transformed, bundle size: 474 KB (7.94s) | **100% HEALTHY** |
| **Frontend Type Verification** | `tsc --noEmit` | **0 Errors**, 0 Type mismatches | **100% HEALTHY** |
| **Live Web App Portals** | Official, Trainer, Admin, Copilot | All 4 portals operational on `http://localhost:3000` | **100% HEALTHY** |

---

## 2. Issues Discovered & Resolved During Baseline Testing

During initial diagnostic evaluation, five critical runtime and configuration defects were identified and resolved to ensure full end-to-end functionality:

1. **Missing `email-validator` Dependency (Pydantic V2 Startup Crash)**
   - **Symptom:** `ModuleNotFoundError: No module named 'email_validator'` during server bootstrap in `app.auth.schemas`.
   - **Root Cause:** `RegisterRequest` defines `email: EmailStr`, which strictly requires `email-validator>=2.2`.
   - **Resolution:** Added and installed `email-validator>=2.2,<3` across `.venv` and global Python environments.

2. **NumPy Constraint Incompatibility with Python 3.14 (`backend/requirements.txt`)**
   - **Symptom:** `pip install -r requirements.txt` failed with Meson build metadata generation error on `numpy`.
   - **Root Cause:** `requirements.txt` pinned `numpy>=1.26,<2`. NumPy 1.x lacks prebuilt wheels for Python 3.14.
   - **Resolution:** Relaxed constraint to `numpy>=1.26,<3`. NumPy 2.5.3 installed with native Windows cp314 wheels.

3. **Missing SMTP Attributes on Pydantic `Settings` Class (`backend/app/core/config.py`)**
   - **Symptom:** `AttributeError: 'Settings' object has no attribute 'EMAIL_HOST'` in `EmailService` and test suites.
   - **Root Cause:** `app/core/email.py` and `tests/test_email_notifications.py` referenced uppercase `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_USER`, `EMAIL_PASSWORD`, and `EMAIL_FROM`, which were absent from `Settings`.
   - **Resolution:** Defined typed fields with `AliasChoices` and property accessors in `Settings`.

4. **Corrupt Orphaned Competency in MongoDB (`BEH_INTEGRITY`)**
   - **Symptom:** `fastapi.exceptions.ResponseValidationError: 7 validation errors` when fetching `/api/v1/competencies`.
   - **Root Cause:** A residual record with code `BEH_INTEGRITY` existed with `{title: "Beh Integrity"}` instead of `{name: ...}`, missing all required schema fields.
   - **Resolution:** Verified zero foreign key references across all collections and purged the malformed orphan document.

5. **Offset-Naive vs Offset-Aware Datetime & ObjectId Serialization Crash (`backend/app/users/router.py`)**
   - **Symptom:** `HTTP 500 Internal Server Error` on `GET /api/v1/users/me/evidence`.
   - **Root Cause:** Line 184 attempted to sort evidence records comparing naive MongoDB timestamps against aware `datetime.now(UTC)`. Additionally, completed learning activities stamped a nested `{activity_id: ObjectId(...)}` dict into `source`, which failed Pydantic JSON serialization.
   - **Resolution:** Normalized timestamps using float UNIX conversion (`item.timestamp()`) and normalized `source` into a string.

---

## 3. Detailed Subsystem & Feature Operational Status

### 3.1 Core System & Infrastructure

| Subsystem / Endpoint | Route / File | Operational Status | Description & Verification Evidence |
| :--- | :--- | :---: | :--- |
| **Health Check** | `GET /api/v1/health` | **WORKING** | Verifies database connectivity and service status. Returns `HTTP 200` with `{"status":"ok","service":"ShikshaSetu Backend","database":"connected"}`. |
| **Database Connection & Pooling** | `app/core/database.py` | **WORKING** | PyMongo client initialization with robust ping validation, automatic reconnection, and clean lifecycle shutdown. |
| **Settings & Environment Security** | `app/core/config.py` | **WORKING** | Loads `.env` configuration. Validates production JWT secrets (preventing default/insecure keys in production). |
| **Framework Indexes** | `app/core/framework_indexes.py` | **WORKING** | Creates compound and unique indexes on `competencies`, `roles`, `role_requirements`, `users`, and `assessments`. |

---

### 3.2 Authentication & Role-Based Access Control (RBAC)

| Feature / Capability | Route / File | Operational Status | Description & Verification Evidence |
| :--- | :--- | :---: | :--- |
| **User Sign-In** | `POST /api/v1/auth/login` | **WORKING** | Authenticates credentials with Argon2 password hashing via `pwdlib`. Returns JWT bearer token with embedded role and expiry. Verified across `OFFICIAL`, `TRAINER`, and `ADMIN`. |
| **Current User Context** | `GET /api/v1/auth/me` | **WORKING** | Returns authenticated profile, role identifier, department, designation, and employee code. |
| **New Civil Servant Registration** | `POST /api/v1/auth/register` | **WORKING** | Cascading registration mapping department, role ID, and official email. Prevents duplicate email signups. |
| **Invalid Credential Rejection** | `POST /api/v1/auth/login` | **WORKING** | Correctly denies invalid passwords or unknown users with `HTTP 401 Unauthorized`. |
| **Role-Based Route Guards** | `app/auth/dependencies.py` | **WORKING** | Enforces endpoint protection (`require_role(["ADMIN"])`, `require_role(["TRAINER"])`). Non-authorized roles receive `HTTP 403 Forbidden`. |

---

### 3.3 Competency Framework & Role Taxonomy

| Feature / Capability | Route / File | Operational Status | Description & Verification Evidence |
| :--- | :--- | :---: | :--- |
| **List Canonical Competencies** | `GET /api/v1/competencies` | **WORKING** | Returns 47 canonical civil services competencies across 4 domains: `STATISTICAL`, `TECHNICAL`, `DIGITAL_GOVERNANCE`, and `BEHAVIOURAL_MANAGERIAL`. Each includes levels 1–5 definitions. |
| **Competency Detail by ID** | `GET /api/v1/competencies/{id}` | **WORKING** | Returns full metadata, framework status (`PROTOTYPE`/`OFFICIAL`), source references, and descriptor levels. |
| **User Mapped Competencies** | `GET /api/v1/competencies/me` | **WORKING** | Returns the active competency subset linked to the official's assigned department role. |
| **List Department Roles** | `GET /api/v1/roles` | **WORKING** | Returns 10 institutional roles (e.g., Statistical Officer, Education Officer, Informatics Officer, Accounts Officer). |
| **Role Requirements Matrix** | `GET /api/v1/roles/{id}/requirements` | **WORKING** | Returns required proficiency levels (1.0 to 5.0), priority rankings (1 to 3), and weightings for each role. |

---

### 3.4 Capability Assessment Architecture

| Feature / Capability | Route / File | Operational Status | Description & Verification Evidence |
| :--- | :--- | :---: | :--- |
| **Assessment Initialization** | `POST /api/v1/assessments/capability` | **WORKING** | Dynamically generates a 10-question standardized exam from the question bank for any competency (e.g., `STAT_SAMPLING`). Returns questions without answer keys. |
| **Assessment Delivery** | `GET /api/v1/assessments/capability/{id}` | **WORKING** | Delivers question options, scenario contexts, difficulty weights, and timing parameters. |
| **Server-Side Scoring & Submission** | `POST /api/v1/assessments/capability/{id}/submit` | **WORKING** | Server evaluates answers against secure answer keys. Client scores are untrusted. Automatically mutates user competency profile and stamps authoritative evidence (confidence 0.85). |
| **Duplicate Submission Prevention** | `POST /api/v1/assessments/capability/{id}/submit` | **WORKING** | Re-submitting an existing completed assessment returns `HTTP 409 Conflict: Assessment has already been submitted`. |
| **Assessment Results Review** | `GET /api/v1/assessments/capability/{id}/results` | **WORKING** | Delivers granular breakdown: raw score, normalized level, questions answered, and baseline comparison. |

---

### 3.5 Adaptive Assessments (IRT Engine)

| Feature / Capability | Route / File | Operational Status | Description & Verification Evidence |
| :--- | :--- | :---: | :--- |
| **Adaptive Session Start** | `POST /api/v1/adaptive-assessments/start` | **WORKING** | Initializes a Computerized Adaptive Testing (CAT) session. Selects initial question calibrated around theta = 0.0. |
| **Dynamic Next Question Selection** | `POST /api/v1/adaptive-assessments/{id}/answer` | **WORKING** | Recalculates candidate ability estimate (Theta) after each response using Item Response Theory (1PL/2PL). Serves progressively harder or easier questions to minimize standard error. |
| **Session Status Tracking** | `GET /api/v1/adaptive-assessments/{id}/status` | **WORKING** | Returns current theta estimate, standard error of measurement (SEM), questions answered, and convergence status. |
| **Assessment Finalization** | `POST /api/v1/adaptive-assessments/{id}/finalize` | **WORKING** | Finalizes session, bounds theta into 1.0–5.0 proficiency score, records authoritative evidence, and updates profile. |

---

### 3.6 Skill Gap Engine

| Feature / Capability | Route / File | Operational Status | Description & Verification Evidence |
| :--- | :--- | :---: | :--- |
| **Personalized Skill Gap Calculation** | `GET /api/v1/skill-gaps/me` | **WORKING** | Compares official's current assessed proficiency against official role baseline requirements. Calculates delta, priority weighting, and gap severity (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`). |
| **Overall Organization Gap Metrics** | `app/skill_gaps/engine.py` | **WORKING** | Aggregates department-wide capability deficits, identifying institutional risk areas where role baselines are unmet. |
| **Explainable Justification** | `app/skill_gaps/service.py` | **WORKING** | Provides human-readable justification explaining the calculation rationale for each identified gap. |

---

### 3.7 Learning Resources & AI Recommendations

| Feature / Capability | Route / File | Operational Status | Description & Verification Evidence |
| :--- | :--- | :---: | :--- |
| **Personalized Recommendations** | `GET /api/v1/recommendations/me` | **WORKING** | Ranks 148 verified courses (63 iGOT Karmayogi + 85 NSSTA) using a 5-factor scoring model: Gap Severity (35%), Priority Weight (25%), Course Duration Fit (15%), Provider Balance (15%), Competency Alignment (10%). |
| **Explainable AI Recommendation Text** | `GET /api/v1/recommendations/me` | **WORKING** | Transparently displays *"WHY RECOMMENDED"* explaining why a specific course was selected for the official's role gap. |
| **Competency Course Directory** | `GET /api/v1/recommendations/competencies/{code}/resources` | **WORKING** | Lists all accredited modules and training calendars linked to a specific competency code. |
| **Direct Deep-Linking** | UI / `app/learning_resources/` | **WORKING** | Provides direct links to iGOT Karmayogi portal and NSSTA training calendar materials. |

---

### 3.8 Learning Activities & Progress Telemetry

| Feature / Capability | Route / File | Operational Status | Description & Verification Evidence |
| :--- | :--- | :---: | :--- |
| **Self-Paced Course Enrollment** | `POST /api/v1/learning-activities` | **WORKING** | Enrolls an official into an iGOT or NSSTA module. Initializes tracking state (`ENROLLED`, `IN_PROGRESS`). |
| **Telemetry & Time Tracking** | `PUT /api/v1/learning-activities/{id}` | **WORKING** | Updates learning progress percentage and increments logged learning hours/minutes. |
| **Course Completion & Supporting Evidence** | `POST /api/v1/learning-activities/{id}/complete` | **WORKING** | Marks course as completed and automatically appends a supporting evidence record to the ledger (confidence 0.30) without corrupting authoritative assessment scores. |

---

### 3.9 Quizzes & Evaluation Engine

| Feature / Capability | Route / File | Operational Status | Description & Verification Evidence |
| :--- | :--- | :---: | :--- |
| **Assigned Quizzes Feed** | `GET /api/v1/quizzes/assigned` | **WORKING** | Lists quizzes assigned to the official by department trainers or system curriculum defaults (7 demo quizzes verified). |
| **Quiz Execution & Questions** | `GET /api/v1/quizzes/{id}` | **WORKING** | Serves vetted multiple-choice questions, difficulty indicators, and scenario descriptions. |
| **Quiz Submission & Automatic Evaluation** | `POST /api/v1/quizzes/{id}/submit` | **WORKING** | Evaluates learner responses, returns score percentage, correct answers review, and pedagogical rationale. Generates supporting evidence. |
| **Trainer Qualitative Feedback** | `POST /api/v1/trainer/attempts/{id}/feedback` | **WORKING** | Allows trainers to review learner quiz attempts and attach targeted qualitative mentorship notes. |

---

### 3.10 Competency Evidence Governance & Ledger

| Feature / Capability | Route / File | Operational Status | Description & Verification Evidence |
| :--- | :--- | :---: | :--- |
| **Immutable Evidence Retrieval** | `GET /api/v1/users/me/evidence` | **WORKING** | Delivers chronological audit ledger of all verified capability demonstrations. |
| **Dual-Tier Evidence Architecture** | `app/users/router.py` | **WORKING** | Strictly distinguishes between: (1) **Authoritative Evidence** (Confidence 0.85–1.0, from formal assessments, mutates profile scores) and (2) **Supporting Evidence** (Confidence 0.30, from course completions and practice quizzes). |
| **Cryptographic Audit Record** | Ledger UI / DB | **WORKING** | Each evidence record displays verified rating, verification protocol, institutional audit statement, and SHA-256 cryptographic hash. |

---

### 3.11 Trainer Assessment Studio

| Feature / Capability | Route / File | Operational Status | Description & Verification Evidence |
| :--- | :--- | :---: | :--- |
| **Trainer Dashboard** | `GET /api/v1/trainer/dashboard` | **WORKING** | Real-time metrics: materials uploaded (3), questions generated (78), approved (42), pending review (33), published quizzes (7), and learner submissions. |
| **Learning Materials Management** | `GET /api/v1/trainer/materials` | **WORKING** | Lists uploaded civil services curriculum documents (SNA 2008 GDP Compilation, Data Quality Guidelines, MoSPI Sampling Manual). |
| **RAG-Grounded AI Question Generation** | `POST /api/v1/learning-materials/{id}/generate-questions` | **WORKING** | Generates candidate MCQs directly grounded in uploaded PDF chunks using Google Gemini / OpenAI providers with automatic mock fallback. |
| **Question Audit & Review Studio** | `GET /api/v1/trainer/questions` | **WORKING** | Trainers inspect candidate questions, view grounded source chunk citations, edit inaccurate distractors, and approve or reject questions. |
| **Quiz Studio & Publishing** | `POST /api/v1/trainer/quizzes/{id}/publish` | **WORKING** | Assembles approved questions into formal quizzes and publishes them to target departments and learner cohorts. |
| **Learner Analytics & Results** | `GET /api/v1/trainer/learners` | **WORKING** | Displays learner submissions, average scores, and allows deep-dive inspection into individual question responses. |

---

### 3.12 Admin Governance & Workforce Analytics

| Feature / Capability | Route / File | Operational Status | Description & Verification Evidence |
| :--- | :--- | :---: | :--- |
| **Executive Governance Dashboard** | `GET /api/v1/admin/dashboard` | **WORKING** | Aggregates high-level metrics across all 9 ministries: 13 officials, 3.0/5.0 average proficiency, 46.7% assessment coverage, and 68 critical gaps. |
| **Workforce Deployment Overview** | `GET /api/v1/admin/workforce` | **WORKING** | Breakdown of employees across departments, roles, and proficiency distribution tiers. |
| **Competency Coverage Intelligence** | `GET /api/v1/admin/competencies` | **WORKING** | Analyzes organizational strength and vulnerability across Statistical, Technical, Governance, and Behavioural domains. |
| **Department Skill Gap Analytics** | `GET /api/v1/admin/skill-gaps` | **WORKING** | Charts critical capability deficits by ministry to pinpoint priority intervention zones. |
| **Training Effectiveness Funnel** | `GET /api/v1/admin/training-effectiveness` | **WORKING** | Tracks course completion rates, total logged learning hours, and evidence conversion rates. |
| **Emerging Skills Radar** | `GET /api/v1/admin/emerging-skills` | **WORKING** | Forecasts strategic capability needs (AI/ML, Cloud Computing, Cyber Governance) for public administration. |
| **Capacity Planning Engine** | `GET /api/v1/admin/capacity-planning` | **WORKING** | Estimates total training hours required and outlines high-priority capacity-building interventions. |
| **Civil Services User Directory** | `GET /api/v1/admin/users` | **WORKING** | Full user management: view profiles, assign department roles, promote trainers, and audit user activity. |
| **Compliance & Audit Reporting** | `GET /api/v1/admin/reports` | **WORKING** | Generates consolidated summaries of organizational compliance, training completion, and workforce readiness. |

---

### 3.13 AI Assistant / Copilot

| Feature / Capability | Route / File | Operational Status | Description & Verification Evidence |
| :--- | :--- | :---: | :--- |
| **Grounded Civil Service Chatbot** | `POST /api/v1/assistant/chat` | **WORKING** | Ingests the official's active role, department, verified competencies, and priority skill gaps into the LLM system prompt. Delivers tailored capability advice. |
| **Interactive UI Assistant Drawer** | `components/AssistantDrawer.tsx` | **WORKING** | Slide-out drawer accessible across all portals. Features role-aware greeting, suggested quick-prompts, and real-time response rendering. |
| **Bilingual Language Support** | UI / `i18n/` | **WORKING** | Language toggle supporting English and Hindi (`हिन्दी`) across dashboard and assistant components. |

---

### 3.14 iGOT Karmayogi Ecosystem Integration

| Feature / Capability | Route / File | Operational Status | Description & Verification Evidence |
| :--- | :--- | :---: | :--- |
| **Ecosystem Status Adapter** | `GET /api/v1/igot/status` | **WORKING** | Informs administrators and learners of integration status (`prototype` mode, 63 verified courses available, direct portal deep-linking operational). |
| **Curated Catalog Browser** | `GET /api/v1/igot/courses` | **WORKING** | Allows searching and browsing the curated iGOT public sector course catalog. |
| **Live Server-to-Server Gateway** | `app/igot/` | **STANDBY / PENDING CREDENTIALS** | Live Parichay SSO token exchange, automated bi-directional SCORM telemetry push, and W3C digital credential verification are implemented as standard adapters awaiting live production API credentials. |

---

## 4. Frontend Application & Page Inventory

### 4.1 Actively Mounted & Working Pages (`frontend/client/src/`)

| Page / Component | Route / View | Target Portal | Operational Status |
| :--- | :--- | :---: | :---: |
| **`LoginPage.tsx`** | `/` (Unauthenticated) | Auth / Public | **WORKING** |
| **`OfficialDashboard.tsx`** | `Dashboard` | Official (Learner) | **WORKING** |
| **`OfficialCompetencies.tsx`** | `My Competencies` | Official (Learner) | **WORKING** |
| **`OfficialAssessments.tsx`** | `Assessments` | Official (Learner) | **WORKING** |
| **`OfficialSkillGaps.tsx`** | `Skill Gaps` | Official (Learner) | **WORKING** |
| **`OfficialRecommendations.tsx`**| `Recommendations` | Official (Learner) | **WORKING** |
| **`OfficialLearning.tsx`** | `My Learning` | Official (Learner) | **WORKING** |
| **`OfficialQuizzes.tsx`** | `Quizzes` | Official (Learner) | **WORKING** |
| **`OfficialEvidence.tsx`** | `Evidence Ledger` | Official (Learner) | **WORKING** |
| **`OfficialProgress.tsx`** | `Progress Tracking` | Official (Learner) | **WORKING** |
| **`OfficialProfile.tsx`** | `My Profile` | Official (Learner) | **WORKING** |
| **`TrainerDashboard.tsx`** | `Dashboard` | Trainer Studio | **WORKING** |
| **`TrainerMaterials.tsx`** | `Learning Materials` | Trainer Studio | **WORKING** |
| **`TrainerQuestionGenerator.tsx`**| `AI Question Generator`| Trainer Studio | **WORKING** |
| **`TrainerQuestionReview.tsx`** | `Question Review` | Trainer Studio | **WORKING** |
| **`TrainerQuizStudio.tsx`** | `Quiz Studio` | Trainer Studio | **WORKING** |
| **`TrainerLearnerResults.tsx`** | `Learner Results` | Trainer Studio | **WORKING** |
| **`TrainerProfile.tsx`** | `Profile` | Trainer Studio | **WORKING** |
| **`AdminDashboard.tsx`** | `Dashboard` | Admin Intelligence | **WORKING** |
| **`WorkforceOverview.tsx`** | `Workforce Overview` | Admin Intelligence | **WORKING** |
| **`CompetencyAnalytics.tsx`** | `Competency Analytics` | Admin Intelligence | **WORKING** |
| **`SkillGapAnalytics.tsx`** | `Skill Gap Analytics` | Admin Intelligence | **WORKING** |
| **`TrainingEffectiveness.tsx`** | `Training Effectiveness`| Admin Intelligence | **WORKING** |
| **`EmergingSkills.tsx`** | `Emerging Skills` | Admin Intelligence | **WORKING** |
| **`CapacityPlanning.tsx`** | `Capacity Planning` | Admin Intelligence | **WORKING** |
| **`AdminUsers.tsx`** | `Users` | Admin Intelligence | **WORKING** |
| **`AdminReports.tsx`** | `Reports` | Admin Intelligence | **WORKING** |
| **`AdminProfile.tsx`** | `Profile` | Admin Intelligence | **WORKING** |

---

### 4.2 Unmounted / Dead / Orphaned Code Identified for Decluttering

| File Path | Estimated Size | Issue Type | Recommendation |
| :--- | :---: | :--- | :--- |
| **`frontend/client/src/pages/Home.tsx`** | 83.4 KB | Unmounted Legacy Prototype | **PURGE:** Superseded by role-based workspaces. Never imported in `App.tsx`. |
| **`frontend/client/src/pages/LiveHome.tsx`** | 56.9 KB | Unmounted Legacy Dashboard | **PURGE:** Early monolithic prototype with hardcoded stats. Never imported in `App.tsx`. |
| **`frontend/client/src/pages/LearningPage.tsx`**| 10.8 KB | Unmounted Prototype Page | **PURGE:** Superseded by `OfficialLearning.tsx`. Never imported in `App.tsx`. |
| **`frontend/client/src/pages/NotFound.tsx`** | 1.8 KB | Unmounted Page | **PURGE or MOUNT:** No 404 route is configured in `App.tsx`. |
| **`frontend/client/src/components/Map.tsx`** | 5.1 KB | Boilerplate Template Residue | **PURGE:** Google Maps starter component never imported anywhere in the project. |
| **`frontend/client/src/components/ManusDialog.tsx`** | 2.5 KB | AI Scaffolding Residue | **PURGE:** Template debug modal never imported in the application. |
| **`backend/.python/`** | ~100 MB (1,688 files) | Committed Virtualenv Runtime | **PURGE & UNTRACK:** Python 3.14 virtualenv accidentally committed into Git. |
| **`backend/` Root Scratch Scripts** | ~480 KB (87 files) | One-Off Debug Artifacts | **PURGE:** `check_*.py`, `diagnose_*.py`, `postman_*.py`, `step*.py` cluttering root. |
| **`backend/` Root Log Dumps** | ~220 KB (15 files) | Terminal Output Dumps | **PURGE:** `test_results.txt`, `e2e_*.txt`, `route_output.txt`. |
| **`backend/` Root JSON Test Dumps** | ~20 KB (4 files) | Test Output Dumps | **PURGE:** `postman_22_test_results.json`, `e2e_postman_results.json`. |
| **`backend/uploads/materials/*.pdf`** | ~23 KB (13 files) | Committed User Uploads | **UNTRACK & REMOVE FROM GIT:** Dynamic runtime upload PDFs. |
| **`backend/igot_courses_seed_56.csv`** | 39.9 KB | Exact Byte Duplicate | **PURGE:** Exact bit-for-bit duplicate of `igot_courses_dataset.csv`. |
| **`.DS_Store` (Root)** | 12.3 KB | OS Metadata | **UNTRACK & PURGE:** macOS Finder metadata file. |

---

## 5. Summary: What Is Working vs What Is Not

### What Is Working (100% Operational)
- [x] Complete REST API with 60+ endpoints operational on FastAPI.
- [x] Full authentication lifecycle (Login, Register, Logout, Token Refresh, Role Enforcement).
- [x] Multi-domain canonical Competency Framework (47 active competencies across 4 domains).
- [x] Role requirements mapping for 10 central government and statistical roles.
- [x] Standardized 10-question Capability Assessment engine with server-side validation.
- [x] Computerized Adaptive Testing (CAT) with Item Response Theory (IRT 1PL/2PL calibration).
- [x] Automated Skill Gap Engine with priority weighting and explainable recommendations.
- [x] Recommendation Engine with 5-factor scoring covering 148 iGOT and NSSTA courses.
- [x] Learning activity enrollment, progress telemetry, and completion logging.
- [x] Assigned Quizzes with automatic evaluation and qualitative trainer feedback.
- [x] Dual-tier Evidence Ledger (Authoritative vs Supporting) with cryptographic SHA-256 record hashes.
- [x] Trainer Assessment Studio (Materials upload, AI MCQ generation, review pipeline, quiz publishing).
- [x] Admin Intelligence Console (Workforce overview, competency coverage, gap analytics, capacity planning, user management).
- [x] Grounded AI Assistant (Copilot) drawer with role-aware context and suggested prompts.
- [x] Bilingual interface toggle (English & Hindi).
- [x] 433 automated pytest unit and integration tests passing with 0 failures.
- [x] Frontend TypeScript validation (`tsc --noEmit`) passing with 0 errors.
- [x] Production bundle compilation (`npm run build`) passing cleanly.

### What Is Not Working / Known External Dependencies
- [ ] **Live Parichay SSO Gateway**: Currently in `prototype` catalog mode; requires live Government of India Parichay OAuth credentials for server-to-server single sign-on.
- [ ] **Live Karmayogi Bharat Bi-directional Telemetry Push**: Uses mock/curated catalog adapter pending official Bharat API gateway client credentials.
- [ ] **4 External Skipped Tests**: `tests/test_recommendations_e2e.py` skips 4 live external API tests when external government API credentials are not set in environment.
- [ ] **Repository Hygiene**: ~1,800 committed temporary files, test logs, duplicate datasets, and orphaned prototype components need to be purged during the decluttering phase.

---

> **Audit Sign-off:**  
> All core application features are confirmed working and fully verified. The codebase is fully prepared for safe decluttering without risk of breaking active functionality.
