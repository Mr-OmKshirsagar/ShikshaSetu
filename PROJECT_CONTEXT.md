# ShikshaSetu - Canonical Project Context

Project: ShikshaSetu  
Document: PROJECT_CONTEXT.md  
Version: 1.0  
Generated: 2026-09-07  
Purpose: Canonical project continuation context.  
Source of truth: Current repository + verified tests  

This is a condensed canonical context document. It is not a substitute for source code. Claims are labelled VERIFIED, HISTORICAL, PLANNED, DEPRECATED, or UNKNOWN where that distinction matters.

## 1. Project Identity

- Project: ShikshaSetu; working product concept: AI-Powered Competency & Learning Intelligence Platform.
- Team name in the requested SIH identity: StatForge. Older notes also use Team Kinetics; treat that as historical/inconsistent metadata.
- Smart India Hackathon 2026, Problem Statement 26101, MoSPI, Data Informatics & Innovation Division (DIID), Software, Smart Education.
- Problem: official learning catalogues do not by themselves establish what an employee needs for a role, what the employee currently knows, or whether learning improved capability. ShikshaSetu connects role requirements, evidence-based competency assessment, skill gaps, learning recommendations, learning activity, and reassessment.
- This is not a generic LMS. The core loop is: Employee -> Competency Assessment -> Competency Profile -> Skill Gap -> Personalized Learning Recommendation -> iGOT + NSSTA -> Learning -> Assessment/Quiz -> Competency Update -> Next Recommendation.

## 2. Product Vision

The platform exists to help public-sector employees and their organizations understand role capability, identify defensible gaps, and select explainable learning actions. Primary personas are employees/officials, trainers, and administrators. A professional role is distinct from an application access role.

Employee journey: maintain profile, take a capability or adaptive assessment, inspect current versus required competencies, review prioritized gaps, start an iGOT/NSSTA resource, complete learning or a quiz, inspect evidence and updated capability, and receive refreshed recommendations.

Trainer journey: upload learning material, generate grounded questions, review/edit/approve questions, create/publish/assign quizzes, and inspect learner results and feedback.

Administrator journey: inspect workforce, competency, skill-gap, training-effectiveness, emerging-skill, capacity, user, report, and RAG evaluation data; assign roles and promote trainers.

Agreed positioning: "We understand what an official's role requires, assess what they currently know, identify competency gaps, recommend appropriate iGOT/NSSTA learning resources, assess learning, and continuously update competency."

Core differentiator: role-aware, evidence-backed competency intelligence with deterministic scoring and explainable recommendations, rather than content listing alone.

## 3. SIH Requirement Mapping

| Requirement | Current implementation | Status | Missing/notes |
|---|---|---|---|
| AI competency assessment | Standard, capability, and adaptive assessment modules; AI is used for content generation where configured | PARTIALLY_IMPLEMENTED | Production validation and official calibration remain open |
| Automated skill-gap analysis | Deterministic gap and priority engine at `/skill-gaps/me` | IMPLEMENTED | Depends on seeded role/profile data |
| iGOT recommendations | Prototype catalog adapter and mapped resource recommender | PARTIALLY_IMPLEMENTED | No live enrollment/progress API |
| NSSTA/TPAC recommendations | Curated NSSTA programmes in learning resources and mappings | PARTIALLY_IMPLEMENTED | No live NSSTA API |
| Personalized learning | Role/gap/provider/difficulty/prerequisite-aware ranking | IMPLEMENTED | Data freshness is prototype-bound |
| MCQ generation | Material extraction, chunking, retrieval, provider generation, validation and traceability | IMPLEMENTED | Real provider depends on configuration |
| Quizzes | Learner and trainer quiz lifecycle, server-side scoring, evidence/update | IMPLEMENTED | Current frontend test script is missing |
| Learner dashboard | Official portal dashboard and learner pages | IMPLEMENTED | Navigation is local React state, not verified URL routing |
| Admin dashboard | Admin analytics routes and frontend portal | IMPLEMENTED | Current deployment health unknown |
| Secure architecture | JWT, Argon2, RBAC, ownership checks, hidden answer keys, server scoring | IMPLEMENTED | Production hardening and live secret configuration remain to verify |
| Scalable architecture | Modular monolith, provider abstractions, indexes, caching/persistence | PARTIALLY_IMPLEMENTED | Some document work is synchronous |
| API interoperability | REST FastAPI contracts and provider abstractions | IMPLEMENTED | Live government adapters are planned |
| Competency mapping | Taxonomy, role requirements, resource mappings | IMPLEMENTED | 33/basic seed versus 42/master seed conflict must be resolved |
| Progress monitoring | Learning activities, quiz attempts, evidence, admin analytics | IMPLEMENTED | Fresh production data unknown |

## 4. System Architecture

Desired product flow:

```text
Frontend
  |
  v
Backend FastAPI API
  |
  +--> JWT authentication and RBAC
  +--> Competency and role requirement services
  +--> Assessment/capability/adaptive assessment engines
  +--> Evidence and competency profile updates
  +--> Skill-gap engine
  +--> Recommendation engine
  |       +--> iGOT prototype provider
  |       +--> NSSTA curated provider
  +--> Learning activities and quizzes
  +--> AI document ingestion and MCQ generation
  +--> Assistant intent routing and hybrid RAG
  |       +--> grounded answer/citations
  |       +--> planned external MoSPI/MCP path
  v
MongoDB
```

Actual architecture is a synchronous Python FastAPI modular monolith using PyMongo and Pydantic settings. Routers are registered in `backend/app/main.py`; domain modules own schemas, repositories, services, and routers. MongoDB is the persistence boundary. The frontend is a React/TypeScript/Vite client with role-selected portal pages and API clients.

## 5. Technology Stack

- Frontend: React 19, TypeScript, Vite, Tailwind/CSS and component libraries present in `frontend`; local React state selects pages. Wouter is installed but central URL routing was not verified. Frontend API base is `VITE_API_BASE_URL`, then `VITE_API_URL`, then `/api/v1`.
- Backend: Python 3.12+ target, FastAPI, synchronous PyMongo, Pydantic Settings, pytest, Uvicorn.
- Database: MongoDB; collections are listed below. Index definitions are in `backend/app/core/framework_indexes.py`.
- AI providers: Gemini and OpenAI provider implementations plus mock providers. Defaults are mock unless provider settings explicitly select a real provider. Real credentials/use are UNKNOWN.
- Embeddings: mock, Gemini, and OpenAI implementations behind a factory. Persistent vectors are stored with document chunks when embedding is enabled.
- RAG: keyword retrieval, vector retrieval, reciprocal rank fusion, MMR, groundedness checks, source citations, intent routing, safety/refusal handling, feedback and evaluation datasets.
- Infrastructure: `render.yaml` defines Render backend/frontend services; `deploy.md` historically describes Render backend plus Vercel frontend. The Render configuration is the repository deployment source; actual deployment health is UNKNOWN. MongoDB Atlas is the documented hosted database option.
- Environment: backend `.env.example` contains database, JWT, AI/provider, upload, chunking and model settings; secrets must remain environment-managed.

## 6. Backend Modules

| Module | Purpose | Important files | Status/constraints |
|---|---|---|---|
| auth/users | Registration, login, JWT, profile | `app/auth`, `app/users` | Implemented; access role and professional role are separate |
| roles/competencies | Taxonomy, roles, requirements, profiles | `app/roles`, `app/competencies` | Prototype framework; seed-count conflict |
| assessments | Standard configured assessments and scoring | `app/assessments` | Implemented, deterministic scoring |
| capability_assessments | Question-bank capability assessments | `app/capability_assessments` | Implemented; answer keys hidden |
| adaptive_assessments | Session-based adaptive flow | `app/adaptive_assessments` | Implemented in source; calibration is prototype |
| questions | Question models/repository/seeds | `app/questions` | Supports curated and generated questions |
| evidence | Append-only competency evidence and confidence | competency services/repositories | Must not be replaced by transient UI state |
| skill_gaps | Required-current comparison and priority | `app/skill_gaps` | Deterministic, user-scoped |
| learning_resources | Catalog, mapping, candidate selection, scoring/cache | `app/learning_resources` | iGOT/NSSTA provider abstraction |
| learning_activities | Start/progress/complete learning | `app/learning_activities` | Completion creates supporting evidence |
| quizzes | Learner quiz retrieval/submission | `app/quizzes` | Server-side scoring and duplicate protection |
| ai | Extraction, cleaning, chunking, generation, validation | `app/ai` | PDF/DOCX/PPTX/TXT; synchronous processing can block workers |
| assistant | Context, routing, grounded answer, feedback | `app/assistant` | MCP branch is not live |
| rag | Retrieval, embeddings, reranking, datasets/evaluation | `app/rag` | Hybrid retrieval is current architecture |
| igot | Prototype course adapter and API | `app/igot` | No official live gateway |
| NSSTA | Curated resources via learning-resource provider | `app/learning_resources` | No live API verified |
| MCP | Intent category and planned external path | assistant/rag routing | Planned/not integrated as a client/server |
| trainer | Material/question/quiz authoring workflows | `app/trainer` | Trainer/admin authorization required |
| admin | Analytics, user role actions, RAG operations | `app/admin` | ADMIN required |

## 7. Database / Data Model

MongoDB collections currently referenced by source include:

| Collection/model | Purpose and key fields | Relationships/constraints |
|---|---|---|
| `users` | Credentials, email, name, department, designation, professional role, access role, status | Email uniqueness; users are isolated by authenticated ID |
| `roles` | Professional role definitions and codes | Linked to role requirements and profiles |
| `competencies` | Prototype taxonomy, domain, code, level metadata | Current taxonomy is internal prototype |
| `role_requirements` | Required competency level/importance/priority by role | Drives gap calculation |
| `competency_profiles` | Per-user current levels/confidence and update metadata | Owned by user and professional role |
| `competency_evidence` | Append-only evidence, type, score, confidence, source | Feeds profile updates; history must be preserved |
| `assessments` / `assessment_attempts` | Standard assessment configuration and attempts | User-owned attempts and submit lifecycle |
| `assessment_configurations` | Competency-specific assessment components/weights | Missing components are renormalized |
| `question_bank` | Curated/generated questions and answer metadata | Answer keys must never reach learner GET responses |
| `capability_assessments` | Capability attempts, responses, results, status | User ownership; server-side score |
| `adaptive_assessment_sessions` | Adaptive question/session state | User ownership and finalized result |
| `quizzes` / `quiz_attempts` | Published/assigned quiz and learner attempt state | Duplicate submission prevention and hidden keys |
| `learning_resources` | iGOT/NSSTA catalog records, provenance, provider, links | Official metadata separated from derived fields |
| `learning_resource_mappings` | Resource-to-competency links | Used by recommender |
| `learning_activities` | User start/progress/completion | Completion produces supporting evidence |
| `learning_materials` | Uploaded document metadata/status | User/trainer ownership; FAILED/READY states |
| `document_chunks` | Cleaned chunks, source metadata, embeddings | Used by vector/keyword retrieval; embedding reuse expected |
| RAG collections | `rag_glossary`, `rag_synonyms`, `rag_eval_set`, `rag_refusal_set`, `rag_feedback`, `rag_entity_registry`, `rag_terminology_hi_en` | Evaluation/metadata datasets, not all runtime answer corpus |

Indexes are created/managed through `backend/app/core/framework_indexes.py`; exact index names and fields must be read from that file before migration changes. No production database contents are verified in this context.

## 8. API Contracts

All routes use `/api/v1` unless noted. Authentication is JWT bearer where marked.

### Authentication/profile
- `POST /auth/register` (public): register employee/official; input includes email/password/name/profile and role selector; public registration cannot grant ADMIN/TRAINER.
- `POST /auth/login` (public): credentials -> bearer token.
- `GET /auth/me` (JWT): current authenticated user.
- `GET /users/me` (JWT): profile.
- `PUT /users/me` (JWT): editable profile fields; cannot self-change authorization/access role.
- `GET /users/me/evidence` (JWT): current user's evidence.

### Competency/roles
- `GET /competencies`, `GET /competencies/{competency_id}`, `GET /competencies/me`.
- `GET /roles`, `GET /roles/{role_id}`, `GET /roles/{role_id}/requirements`.

### Assessments
- `POST /assessments`, `GET /assessments/{attempt_id}`, `POST /assessments/{attempt_id}/submit`.
- `GET /assessments/configs`, `GET /assessments/configs/{competency_code}`.
- `POST /assessments/capability`, `GET /assessments/capability`, `GET /assessments/capability/{assessment_id}`, `POST /assessments/capability/{assessment_id}/submit`, `GET /assessments/capability/{assessment_id}/results`.
- `POST /adaptive-assessments/start`, `POST /adaptive-assessments/{session_id}/answer`, `GET /adaptive-assessments/history`, `GET /adaptive-assessments/{session_id}/status`, `POST /adaptive-assessments/{session_id}/finalize`.

### Gaps/recommendations/learning
- `GET /skill-gaps/me` (JWT): deterministic user skill gaps.
- `GET /recommendations/me`, `GET /recommendations/resources/{resource_id}`, `GET /recommendations/competencies/{competency_code}/resources`, `GET /recommendations/resources/unmapped` (JWT).
- `POST /learning-activities`, `GET /learning-activities`, `GET /learning-activities/{activity_id}`, `PUT /learning-activities/{activity_id}`, `POST /learning-activities/{activity_id}/complete` (JWT).

### Quizzes/materials
- `GET /quizzes/assigned`, `POST /quizzes`, `GET /quizzes/{quiz_id}`, `POST /quizzes/{quiz_id}/submit` (JWT). Keys are hidden; score is server-side.
- `POST /learning-materials/upload`, `GET /learning-materials/{material_id}`, `POST /learning-materials/{material_id}/generate-questions` (JWT). Accepted source formats include PDF, DOCX, PPTX, TXT; upload size is configuration-controlled.

### iGOT/assistant
- `GET /igot/status`, `GET /igot/courses` (JWT or route policy as implemented).
- `POST /assistant/chat`, `POST /assistant/feedback` (JWT). Chat returns grounded/cited output or a refusal/fallback according to intent and retrieval/provider state.

### Trainer/admin
- Trainer: `GET /trainer/dashboard`, `GET /trainer/materials`, `POST /trainer/materials/{material_id}/generate`, `GET /trainer/questions`, `PUT /trainer/questions/{question_id}`, `POST /trainer/questions/{question_id}/approve`, `POST /trainer/questions/{question_id}/reject`, `POST /trainer/quizzes`, `POST /trainer/quizzes/{quiz_id}/publish`, `POST /trainer/quizzes/{quiz_id}/assign`, `GET /trainer/quizzes/{quiz_id}/attempts` plus learner/result/feedback routes in the trainer router.
- Admin: `/admin/dashboard`, `/admin/workforce`, `/admin/competencies`, `/admin/skill-gaps`, `/admin/training-effectiveness`, `/admin/emerging-skills`, `/admin/capacity-planning`, `/admin/users`, `/admin/reports`, `/admin/users/{user_id}/promote-to-trainer`, `/admin/users/{user_id}/assign-role`; RAG actions include `POST /admin/rag/seed-datasets`, `POST /admin/rag/run-evaluation`, `POST /admin/rag/reembed-materials`.

Typical errors are 400 validation/business errors, 401 missing/invalid JWT, 403 insufficient role/ownership, 404 missing resource, 409 duplicate/submitted resource, 413 oversized upload, and 503 unavailable database/provider. Exact schema fields and status codes are defined by the route schemas, not this summary.

## 9. Authentication and Authorization

JWT bearer tokens use configurable algorithm, secret, and expiry. Passwords use Argon2. Protected routes resolve an active user on every request. Access roles are `OFFICIAL`, legacy `EMPLOYEE`, `TRAINER`, and `ADMIN`; public registration creates the employee/official access role. Trainer routes allow TRAINER/ADMIN; admin routes require ADMIN. Professional `role_id` is separate from access role.

Ownership checks prevent users from reading/updating another user's assessments, quizzes, activities, evidence, and materials. Profile edits cannot elevate authorization or arbitrarily change professional role. Answer keys are withheld until server-side submission. Secrets/API keys come from environment configuration, never source or user payloads. Sensitive database/provider errors must not be exposed in health responses. Uploads require validation and bounded size. RAG answers must respect retrieval scope, prompt-injection handling, out-of-scope refusal, and citations.

## 10. Competency Framework

The intended prototype domains and competencies are:

- Statistical: Survey Design, Sampling, National Accounts, Price Statistics, Labour Statistics, Agricultural Statistics, Industrial Statistics, SDG Indicators, Metadata Standards, Data Quality Frameworks.
- Technical: Python, R, SQL, Stata, SPSS, SAS, GIS, Data Visualization, AI/ML, Cloud Computing, APIs, Open Data.
- Digital Governance: Cybersecurity, Data Privacy, Digital Signatures, Government Cloud, Digital Public Infrastructure.
- Behavioural/Managerial: Leadership, Communication, Project Management, Ethics, Decision Making, Change Management.

Subskills exist in source data and mapping files, but the canonical current count is unresolved: the basic framework seed describes 33 competencies while the master seed synchronizes 42 canonical taxonomy entries. Do not state one count as final until the seed path and database are reconciled.

## 11. Competency Level Model

Prototype levels: 1 Awareness, 2 Basic, 3 Intermediate, 4 Advanced, 5 Expert. This is not an official MoSPI/iGOT scale unless independently verified. Current scoring maps percentage to levels: 0-19%=1, 20-39%=2, 40-59%=3, 60-79%=4, 80-100%=5. Standard assessment weights are self assessment 20%, knowledge 40%, scenario 30%, training evidence 10%; absent components are excluded and remaining weights renormalized. Prototype confidence equals available evidence-weight coverage in the standard flow. Capability/adaptive flows normalize server-side results to the same prototype 1-5 scale.

## 12. Competency Assessment

Assessment configurations are competency-dependent. Curated question-bank flows support knowledge/MCQ and scenario questions; self-rating and training evidence are supported in the standard assessment. Capability assessment loads questions from configuration and does not expose answer keys. Adaptive assessment has start/answer/status/finalize lifecycle. Python, SQL, sampling, leadership, and other specialized examples must not be described as coding/debugging/situational formats unless the active configuration/question bank verifies them; those are supported only where configured. Submission creates evidence and updates the user competency profile, then skill gaps are recalculated.

## 13. Quiz Engine

Capability assessment asks what the employee currently knows and contributes authoritative assessment evidence. A learning quiz asks what the employee learned; it is not a substitute for a capability assessment.

Learner flow: assigned quiz -> load quiz -> answer -> submit once -> backend validates/scorers -> result -> evidence -> competency update where the quiz type permits -> refreshed gap/recommendation. Quiz GET responses hide correct answers. Server-side scoring is authoritative; duplicate submissions return conflict behavior. Trainer flow covers generated question review, approval/rejection, quiz creation, publishing, assignment, and attempt inspection. Generated questions retain source traceability to chunks/materials. Frontend integration should preserve loading, submission protection, 401, error, and result states.

## 14. RAG Architecture

Current components are under `backend/app/rag` and `backend/app/ai`.

- Ingestion: upload -> format extraction (PDF/DOCX/PPTX/TXT) -> cleaning -> chunking -> optional embedding -> `learning_materials`/`document_chunks` -> READY or FAILED.
- Retrieval: deterministic intent router classifies user-data, RAG, glossary, hybrid, MCP, and out-of-scope intents. Keyword and vector retrieval are combined by reciprocal rank fusion; MMR/reranking reduces redundancy. Metadata filters and source metadata are retained.
- Embeddings: factory supports mock/Gemini/OpenAI providers. Persistent embeddings are reused from document chunks; backfill/migration tooling exists. Fake/hash embeddings must not be represented as production semantic embeddings.
- Generation: assistant/MCQ generation uses provider abstraction, structured schemas, validation, grounded context and citations. Groundedness checks and fallback/refusal behavior prevent unsupported answers. Query rewriting is represented by synonym/acronym assets and routing where implemented; do not claim an independent rewrite pipeline without source verification.
- Safety: prompt injection and out-of-scope inputs are detected/refused or routed; structured user data is read from MongoDB, not hallucinated from RAG. Evaluation and refusal sets are available through admin actions.
- Feedback: assistant feedback is stored; RAG feedback/evaluation collections support future quality measurement. Caching and lazy/provider initialization are used where implemented; exact startup timings are UNKNOWN.
- Startup: embedding/RAG data should not require expensive eager re-embedding on every startup. Seeding and re-embedding are explicit admin/script operations.
- MCP: routing category exists, but no project MCP server/client/dependency or live MoSPI adapter is present. It is PLANNED/NOT INTEGRATED, with safe fallback rather than a live source claim.

## 15. RAG Datasets

The repository has or declares these datasets with the following status:

| Dataset | Storage/use | Provenance/status |
|---|---|---|
| iGOT course data/content | CSV/JSON seeds and MongoDB learning resources | Curated/derived prototype; official metadata must remain distinct |
| NSSTA/TPAC data | CSV/JSON seeds and MongoDB resources | Curated prototype, not a live feed |
| Competency taxonomy | CSV/JSON and competencies collection | Internal prototype taxonomy |
| Course -> competency mapping | CSV and mapping collection | Derived prototype |
| NSSTA -> competency mapping | CSV and mapping collection | Derived prototype |
| Role -> competency requirements | seed definitions and role_requirements | Prototype role model |
| Learning resource master | MongoDB `learning_resources` | Derived catalog/provider abstraction |
| MoSPI knowledge sources | RAG documents where ingested | Source status must be recorded per document; no universal official claim |
| Chatbot FAQ | RAG/assistant content if seeded | UNKNOWN as a standalone current dataset |
| RAG document registry | document/material/chunk metadata | Implemented through material/chunk records |
| Retrieval Evaluation/Golden Q&A | `rag_eval_set` and evaluation code | Internal evaluation asset |
| Synonym/acronym dictionary | `rag_synonyms` | Internal/derived terminology asset |
| Statistical glossary | `rag_glossary` | Curated grounding asset; source status per entry |
| Hindi-English mapping | `rag_terminology_hi_en` | Prototype terminology asset |
| Retrieval feedback log | `rag_feedback` | Append-only quality feedback asset |
| Entity registry | `rag_entity_registry` | Prototype disambiguation asset |
| Reranker calibration | Proposed/evaluation data | PLANNED/partial; no verified fine-tuned model |
| Out-of-scope/refusal set | `rag_refusal_set` | Internal safety evaluation asset |

Counts must be taken from current seed scripts/database, not historical reports. The additional dataset proposal is useful design context but does not prove every dataset is populated.

## 16. iGOT Data

The repository contains the existing 56-course seed dataset plus enriched CSV/JSON variants and a larger master resource seed. Official fields and provenance are imported separately from derived competency, difficulty, and recommendation metadata. Historical verification reports describe 63 iGOT resources in the master catalog and 42/68 mapping variants; other reports describe 56 courses. Treat exact current records as UNKNOWN until a fresh seed/database count is run. Five NSSTA/MoSPI course records with null course IDs were historically identified; they require stable internal resource IDs and must not be silently treated as live enrollment IDs.

The iGOT adapter currently lists/searches prototype catalog records, exposes status/deep-link metadata, and supports provider filtering. Live enrollment/progress synchronization is not implemented without official gateway access.

## 17. NSSTA / TPAC Data

NSSTA programmes are represented as curated learning-resource records and competency mappings. The JSON/CSV source files and seed scripts are prototype/derived representations; they are not proof of an official live catalogue or current availability. Historical data-quality work identified null course IDs and freshness concerns. Keep `provider=NSSTA`, source/provenance, last-verified metadata, and internal resource IDs explicit. A future adapter should poll/consume an official API, preserve snapshots, record last-verified time, reconcile removals, and keep the current provider abstraction.

## 18. MoSPI MCP

Current status: PLANNED / NOT INTEGRATED. The assistant intent router recognizes MCP/live-statistics intent and the service has a safe unconfigured/stub path, but no project MCP server, client, adapter, dependency, or authenticated MoSPI connection is verified. Do not call this live. Questions requiring real-time official statistics must be refused, clarified, or routed only when an approved integration is actually installed.

## 19. AI / LLM Architecture

Providers include mock, Gemini, and OpenAI implementations. LLM use includes grounded MCQ generation, assistant answer generation, and structured content transformations. Provider factories, prompt modules, schema validation, retries/fallbacks, and source/chunk traceability are present in the AI/assistant modules. Deterministic code owns authentication, authorization, competency scores, gaps, resource ranking, evidence, duplicate submission, and database state. An LLM must never be the source of truth for those items.

Mock providers are the safe local/test default. Production use of Gemini/OpenAI requires explicit provider configuration, valid environment secrets, and a live verification; `GEMINI_API_KEY` alone does not prove Gemini is selected. Generated output must be validated and rejected when malformed, ungrounded, or missing source traceability.

## 20. Frontend Architecture

The frontend lives under `frontend/client/src`. The app uses React/TypeScript with role-based portal selection in `App.tsx`. Official pages include Dashboard, My Competencies, Assessments, Skill Gaps, Recommendations, My Learning, Quizzes, Evidence, Progress, Profile, and Capability Assistant. Trainer pages cover dashboard, materials, AI question generation, review, quiz studio, published quizzes, learner results, and profile. Admin pages cover dashboard, workforce, competency, skill-gap, training effectiveness, emerging skills, capacity planning, users, reports, and profile.

The current navigation is predominantly local React state. A Wouter dependency/NotFound surface exists, but a central browser route contract is not verified. The API client uses JWT and environment base URL. Frontend design notes describe the Civic Clarity visual direction, but design notes are not behavioral contracts. Do not invent backend behavior for unfinished screens.

## 21. Profile Implementation

Editable user-owned profile data includes basic information, employment/department/designation, education, experience, training and related profile fields accepted by the current schema. System-generated/read-only data includes competency profile, evidence-derived results, confidence, skill gaps, and recommendations. Email, access role, authorization status, and protected professional role fields cannot be changed by ordinary profile updates. Department/designation changes may reconcile professional role/profile according to current service logic.

## 22. Refresh / Data Refetch

Backend GET routes are the authoritative refetch mechanism. Frontend learning activity hooks expose refresh/list/get operations and auto-load options. Any page refresh control must call the relevant API client rather than only rerender local state. Exact coverage of refresh controls on every page is UNKNOWN and should be verified before claiming complete refetch behavior.

## 23. Quiz Frontend Flow

```text
Assigned Quiz -> Attempt Quiz -> Load quiz -> Answer questions -> Submit
-> Backend scoring -> Result -> Evidence -> Competency update
-> Updated skill gap/status -> Updated recommendation
```

The backend routes are `GET /quizzes/assigned`, `POST /quizzes`, `GET /quizzes/{quiz_id}`, and `POST /quizzes/{quiz_id}/submit`; trainer assignment/publish routes are separate. The frontend must never score authoritatively in the browser or display answer keys before submission.

## 24. Performance Optimization

Implemented or documented optimizations include MongoDB indexes, recommendation candidate/scoring separation, caching where present, persisted/reused embeddings, explicit RAG seed/re-embed operations, and frontend code/page organization. Some AI/document extraction is synchronous and may block a worker for large uploads.

Historical measurements are not current baselines: an older frontend note reports roughly 339.49 kB frontend bundle and 111.35 kB CSS; another historical prompt cites different sizes. Older backend reports cite 164/164 or 171 collected tests. These are HISTORICAL, not current verified measurements. Current startup, memory, API latency, bundle, and database measurements are UNKNOWN because the local validation commands were unavailable in this environment.

## 25. Testing Status

- Backend command: from `backend`, `pytest` (configured by `backend/pytest.ini`). Tests mock database reachability where appropriate and do not universally require local MongoDB.
- Frontend commands are defined by `frontend/package.json`; source tests exist under `frontend/client/src/**/__tests__`, but the repository currently lacks a verified `test` script. `npm run check` and `npm run build` are the documented typecheck/build checks.
- Historical artifacts record 171 collected backend tests and older runs of 164 passed/4 skipped, plus phase-specific and HTTP E2E checks. These are historical evidence only. A fresh backend suite could not run here because `pytest` is not installed on the active shell PATH; a fresh frontend command was not completed due to the initial shell path/session mismatch. Current baseline: UNKNOWN.
- Recorded historical failures include recommendation/skill-gap E2E failures, a MongoDB truth-value bug (compare database objects with `None`, never `bool(db)`), and validation blockers. Do not assume they remain or are fixed without a fresh run.

## 26. Security / Hardening

IMPLEMENTED: JWT bearer auth, Argon2 password hashing, active-user checks, access-role enforcement, ownership isolation, protected admin/trainer routes, server-side quiz/capability scoring, hidden answer keys, duplicate submission handling, request/schema validation, bounded upload types/size, environment-managed secrets, safe health errors, RAG prompt-injection/out-of-scope handling, source citations, and separation of official/derived data.

RECOMMENDED/NOT VERIFIED: production secret rotation, secure MongoDB network policy, rate limiting, audit-log retention policy, malware scanning for uploads, full CSP/security headers, live dependency scanning, SSO, and production penetration testing. Do not describe the prototype as production-ready.

## 27. Data Integrity / Migrations

Seed scripts are repeatable and use stable competency/role/resource codes where implemented. Framework, master data, role-resolution, competency-profile, resource-mapping, quiz, RAG, embedding backfill, and index scripts exist under `backend/app/scripts` and module seed files. Historical work includes role migration, evidence fixes, null-course-ID investigation, reseeding, and reconciliation. Never reseed production blindly; inspect current database, run validation, preserve user evidence, use stable upserts, and verify mappings/indexes. The 33-versus-42 framework discrepancy is an active integrity issue, not a reason to silently delete data.

## 28. Known Bugs / Limitations

| Issue | Severity | Current status | Workaround/next action | Module |
|---|---|---|---|---|
| Basic seed says 33 competencies; master seed says 42 | High | Unresolved | Select one canonical taxonomy and migrate mappings/profiles | Framework |
| Current exact test baseline unavailable | High | Unknown | Install project dependencies and run backend/frontend checks | Testing |
| Live iGOT enrollment/progress unavailable | High for production | Planned | Obtain official API access and implement adapter | iGOT |
| Live NSSTA API unavailable | High for freshness | Planned | Obtain official source/API and snapshot/reconcile | NSSTA |
| MoSPI MCP client/server unavailable | High for live-statistics claims | Planned | Integrate approved authenticated MCP path | Assistant |
| AI provider selection may remain mock despite Gemini key | Medium | Configuration risk | Set provider explicitly and run live verification | AI |
| `api_endpoints.json` says 0.3.0 while `main.py` says 0.3.1 | Medium | Documentation drift | Regenerate endpoint artifact | API docs |
| Root/backend README says scoring is not implemented | Medium | Stale documentation | Treat source as truth; update README when safe | Docs |
| Frontend has no verified test script | Medium | Current repo gap | Add/restore test command and run tests | Frontend |
| Some document processing is synchronous | Medium | Implemented limitation | Queue/background processing for production scale | AI |
| Render config and deploy guide disagree on frontend host | Low/medium | Documentation drift | Adopt one deployment source and verify deploy | Deployment |
| Current database contents and deployment health unknown | High | Unknown | Run environment-specific audit | Operations |
| Historical null resource/course IDs | Medium | Partially handled | Preserve internal IDs and provenance; repair source links | Data |

## 29. Important Architectural Decisions

- MongoDB fits flexible prototype competency/evidence/resource documents and supports provider/RAG metadata; preserve indexes and user ownership.
- A modular monolith keeps the SIH MVP operable while separating domains; extend existing modules instead of duplicating auth, users, scoring, RAG, or providers.
- Hybrid RAG is used because keyword matching handles acronyms/exact official terms while vectors handle semantic phrasing; fusion/MMR reduces single-retriever failure.
- Intent routing prevents structured user facts, grounded documents, external live statistics, and out-of-scope questions from being treated as the same corpus.
- Structured user data is not RAG: competency, role, evidence, and authorization must come from MongoDB/services.
- iGOT/NSSTA use a provider abstraction so curated prototype data can later be replaced by official adapters without changing recommendation APIs.
- LLM output is assistive and validated; deterministic services own scores, gaps, authorization, evidence, and persistence.
- Official metadata and derived/prototype metadata are separate to prevent prototype labels or links being presented as Government facts.
- Persistent embeddings and explicit re-embedding are required for predictable startup/performance; fake/hash embeddings are not acceptable as production semantics.
- Evidence is history, not a replaceable current score; preserve append-only records and explain confidence.

## 30. Protected Architecture / Do Not Break

Do not break JWT authentication, user isolation, access-role/professional-role separation, append-only evidence history, deterministic competency and skill-gap scoring, server-side quiz scoring, hidden answer keys, source traceability, grounded/refusal routing, official-versus-derived provenance, RAG routing and persistence, API response contracts, index/seed idempotency, and regression tests. Do not add a duplicate auth/user/dashboard/RAG/recommendation system. Do not call prototype scales, curated catalogs, mock providers, or planned integrations official/production without verification.

## 31. Current File Map

| Path | Purpose | Status |
|---|---|---|
| `backend/app/main.py` | FastAPI app/router registration | VERIFIED |
| `backend/app/core/` | Settings, DB lifecycle, indexes | VERIFIED |
| `backend/app/auth/` and `backend/app/users/` | Auth/profile/RBAC | VERIFIED |
| `backend/app/competencies/`, `roles/` | Framework and requirements | VERIFIED |
| `backend/app/assessments/`, `capability_assessments/`, `adaptive_assessments/` | Assessment flows/scoring | VERIFIED |
| `backend/app/questions/` | Question bank and seeds | VERIFIED |
| `backend/app/learning_resources/`, `igot/` | Resources, mapping, provider/recommendations | VERIFIED |
| `backend/app/learning_activities/`, `quizzes/` | Learning and quiz evidence flows | VERIFIED |
| `backend/app/ai/` | Extraction, chunking, generation, embeddings | VERIFIED |
| `backend/app/rag/`, `assistant/` | Routing, retrieval, grounding, assistant | VERIFIED |
| `backend/app/trainer/`, `admin/` | Authoring and administration | VERIFIED |
| `backend/app/scripts/` | Seeds, migrations, RAG/embedding operations | VERIFIED |
| `backend/tests/` | Backend tests | VERIFIED, current pass status UNKNOWN |
| `frontend/client/src/` | React application, pages, API client/hooks | VERIFIED |
| `backend/requirements.txt`, `frontend/package.json` | Dependencies/scripts | VERIFIED |
| `render.yaml`, `.env.example` files | Deployment/environment templates | VERIFIED |

## 32. Phase History

| Phase | Objective | Outcome |
|---|---|---|
| 1/2 | Backend foundation, auth, prototype framework | Implemented; old README claims scoring was not yet implemented |
| 1C | Frontend API/state integration and learning activity flow | Historical report says real activity/evidence flow and frontend tests/build were added |
| 1D/2 | Capability assessment and profile/role work | Implemented in current modules; exact historical phase boundaries vary |
| 3 | Competency mappings, skill gaps, provider recommendation engine | Implemented deterministic recommendation/gap loop; historical audits include defects and fixes |
| 3F-3G | Data integrity, mapping, role resolution, performance | Fixes/migrations exist; taxonomy count still needs reconciliation |
| 3H-3I | RAG/data relevance and frontend presentation | RAG datasets/routing and UI refinements added; exact completion claims are historical |
| 5A-5H | Security, analytics, evidence, roles, assessments, recommendations | Current routes/modules reflect much of this work; verify with fresh tests |
| 6 | SIH/demo readiness and Gemini verification | Prototype demo path documented; live provider/deployment status remains unknown |

## 33. Current State - Single Source of Truth

| Feature | Current status | Location | Tested? | Known issue/next action |
|---|---|---|---|---|
| Auth/RBAC | IMPLEMENTED | `backend/app/auth`, routers | Historical tests; fresh baseline UNKNOWN | Production hardening/SSO later |
| Profile | IMPLEMENTED | users/profile schemas/services | Historical frontend/backend evidence | Verify all editable fields |
| Competency taxonomy | IMPLEMENTED but inconsistent count | competencies, seed CSV/JSON | Historical tests | Reconcile 33 vs 42 |
| Capability assessment | IMPLEMENTED | capability_assessments | Historical tests | Fresh regression |
| Adaptive assessment | IMPLEMENTED in source | adaptive_assessments | UNKNOWN current pass | Validate calibration |
| Evidence/profile update | IMPLEMENTED | competency/evidence services | Historical tests | Preserve append-only history |
| Skill gaps | IMPLEMENTED | skill_gaps | Historical E2E mixed | Re-run with current DB |
| Recommendations | IMPLEMENTED | learning_resources | Historical deterministic checks | Verify current resource counts |
| iGOT | Prototype | igot | Historical checks | Official API required |
| NSSTA | Curated prototype | learning_resources/data | Historical checks | Official freshness required |
| Learning activities | IMPLEMENTED | learning_activities | Historical frontend/backend tests | Validate complete flow |
| Quizzes | IMPLEMENTED | quizzes/trainer | Historical tests | Ensure answer-key isolation |
| AI materials/MCQ | IMPLEMENTED | ai/router | Historical tests | Explicit provider/live test |
| Hybrid RAG | IMPLEMENTED | rag/assistant | New tests/source present | Fresh pytest and evaluation |
| MCP | PLANNED | intent branch only | Not live-tested | Do not claim integration |
| Frontend portals | IMPLEMENTED in source | frontend/client/src | Build/test status UNKNOWN | Add verified test script/routes |
| Admin analytics | IMPLEMENTED | admin router/service | Historical tests | Verify authorization/data |
| Deployment | CONFIGURED, not verified | render.yaml/deploy.md | Not verified | Run deployment health check |

## 34. Next Implementation Roadmap

NOW: install pinned backend/frontend dependencies; run fresh backend pytest and frontend typecheck/build; reconcile 33/42 taxonomy; synchronize endpoint/version documentation; verify seed counts and database indexes; keep official/derived provenance explicit.

NEXT: implement focused live-provider contract adapters behind existing iGOT/NSSTA abstractions; add current frontend test command and route/refetch coverage; add background processing for large document ingestion; run RAG golden/refusal evaluation and record measurable baselines.

LATER: approved MoSPI MCP/live statistics integration, production SSO, external enrollment/progress sync, stronger audit/rate-limit/upload controls, multilingual expansion, and production observability.

OPTIONAL: reranker calibration/fine-tuning, larger official glossary and Hindi terminology corpus, adaptive difficulty, and richer analytics after MVP reliability.

## 35. SIH Demo Flow

Employee -> Profile -> Capability Assessment -> Competency -> Skill Gap -> iGOT/NSSTA Recommendation -> Learning -> Quiz -> Result -> Competency Improvement -> Updated Recommendation.

Key screens: authenticated learner dashboard, assessment/question/result, competency and gap comparison, recommendation explanation/provider filter, learning activity progress/completion, quiz submission/result/evidence, assistant with citations, and admin/trainer views as optional supporting proof. Key backend interactions are the auth/profile, assessment submit, `/skill-gaps/me`, `/recommendations/me`, learning activity lifecycle, quiz submit, evidence/profile update, and subsequent gap/recommendation reads.

## 36. Data Source / Provenance Rules

Use exactly these conceptual labels:

- OFFICIAL: directly verified from an authorized Government/provider source, with source and verification time.
- DERIVED: computed/mapped/enriched from a source; never display as original official metadata.
- INTERNAL_PROTOTYPE: team-created taxonomy, scoring, curated catalogue record, mapping, prompt, or evaluation data.
- UNKNOWN: provenance or currentness is not verified.

Every iGOT/NSSTA/RAG resource should preserve source, source URL/document, retrieved/last-verified time where available, provider, and derived-field status. Never present prototype/derived metadata as official Government data.

## 37. Future Integration

Future/dependent on official access: iGOT API course/enrollment/progress adapter, NSSTA/TPAC API adapter, authenticated MoSPI MCP client/server, Government SSO, production MongoDB/network/secret management, and production deployment observability. Keep these behind current provider/router/service interfaces. Do not change current API contracts to imply an integration is live before credentials, schemas, data freshness, security, and an executable verification are present.

## 38. Instructions for the Next LLM / Coding Agent

1. Read `PROJECT_CONTEXT.md` first.
2. Inspect current source code before modifying anything.
3. Trust code/tests over historical reports.
4. Reuse existing modules and provider abstractions.
5. Do not create duplicate systems.
6. Do not break protected architecture.
7. Run regression tests after changes.
8. Do not invent Government data.
9. Keep official versus derived data separate.
10. Ask for an audit before large rewrites or destructive migrations.
11. Optimize before adding unnecessary features.
12. Preserve the SIH demo path.
13. Do not call anything production-ready without verification.
14. Treat UNKNOWN as an action item, not as permission to infer.
15. Read exact schemas/routes before documenting new API behavior.

## 39. Historical Documents Consolidated

The following 136 Markdown reports were scheduled/marked deleted in the worktree and are consolidated here. They are grouped by topic; individual reports were deduplicated against current source, tests, seeds, and each other. Unless noted otherwise, their useful implementation knowledge is FULLY CONSOLIDATED into sections 3-38; obsolete status claims are retained only as historical context.

### Root historical audits and plans

`AUDIT_SUMMARY_FOR_STAKEHOLDERS.md`, `BACKEND_CURRENT_STATE_AUDIT.md`, `BACKEND_FEATURE_COMPLETION_AUDIT.md`, `BACKEND_PACKAGE_MODERNIZATION_REPORT.md`, `BACKEND_PRODUCTION_READINESS_AUDIT.md`, `BACKEND_QUALITY_HARDENING_CYCLE_A_B.md`, `DATABASE_CONSISTENCY_AUDIT.md`, `DECISION_TREE.md`, `FINAL_BACKEND_HARDENING_AUDIT.md`, `FINAL_BACKEND_HARDENING_REPORT.md`, `FINAL_PROJECT_COMPLETION_AUDIT.md`, `FINAL_RELEASE_CHECKLIST.md`, `FRONTEND_INTEGRATION_AUDIT_REPORT.md`, `FRONTEND_PRODUCT_COMPLETION_AUDIT.md`, `IMPLEMENTATION_PLAN_FOR_PRODUCT_COMPLETION.md`, `IMPLEMENTATION_SUMMARY.md`, `LIVE_E2E_BACKEND_VERIFICATION.md`, `MASTER_DATA_SYNC_REPORT.md`, `NEXT_STEPS_ACTION_PLAN.md`, `ORIGINAL_AIM_GAP_ANALYSIS.md`, `PHASE_1C_CHECKLIST.md`, `PHASE_1D_ANSWER_TO_CONCERN.md`, `PHASE_1D_COMPLETION_REPORT.md`, `PHASE_1D_PLANNING.md`, `PHASE_1_COMPLETE_SUMMARY.md`, `PHASE_2A_COMPLETION_REPORT.md`, `PHASE_2B_COMPLETION_REPORT.md`, `PHASE_2_ROADMAP.md`, `PHASE_3A_COMPLETION_REPORT.md`, `PHASE_3A_IGOT_INTEGRATION_AUDIT.md`, `PHASE_3B_COMPLETION_REPORT.md`, `PHASE_3C_COMPLETION_REPORT.md`, `PHASE_3D_COMPLETION_REPORT.md`, `PHASE_3E_FINAL_VERIFICATION_AND_SIH_READINESS.md`, `PHASE_3H_DATA_RELEVANCE_FINDING.md`, `PHASE_3H_MOTION_ENHANCEMENT_AUDIT.md`, `PHASE_3I_TYPOGRAPHY_AUDIT.md`, `PHASE_3I_TYPOGRAPHY_REPORT.md`, `PHASE_5A_SECURITY_AUDIT.md`, `PHASE_5A_SECURITY_FIX_REPORT.md`, `PHASE_5B_SECRETS_AUDIT.md`, `PHASE_5B_SECRETS_FIX_REPORT.md`, `PHASE_5C_ANALYTICS_AUDIT.md`, `PHASE_5C_ANALYTICS_FIX_REPORT.md`, `PHASE_5C_EVIDENCE_AUDIT.md`, `PHASE_5C_EVIDENCE_FIX_REPORT.md`, `PHASE_5D_DATA_MIGRATION_NOTES.md`, `PHASE_5D_EVIDENCE_AUDIT.md`, `PHASE_5D_EVIDENCE_FIX_REPORT.md`, `PHASE_5E_ROLE_MIGRATION_NOTES.md`, `PHASE_5E_ROLE_RESOLUTION_AUDIT.md`, `PHASE_5E_ROLE_RESOLUTION_FIX_REPORT.md`, `PHASE_5F_ASSESSMENT_ARCHITECTURE_AUDIT.md`, `PHASE_5F_ASSESSMENT_ARCHITECTURE_FIX_REPORT.md`, `PHASE_5F_ASSESSMENT_MIGRATION_NOTES.md`, `PHASE_5G_RECOMMENDATION_AUDIT.md`, `PHASE_5H_FIX_REPORT.md`, `PHASE_5H_FULL_SYSTEM_AUDIT.md`, `PHASE_6_FIX_REPORT.md`, `PHASE_6_SIH_DEMO_SCRIPT.md`, `PHASE_6_SIH_JUDGE_CHECKLIST.md`, `PHASE_6_UI_DEMO_AUDIT.md`, `PHASE_ANIMATION_AUDIT.md`, `PRIORITIZED_BACKLOG.md`, `PRODUCT_VISION_AUDIT.md`, `RAG_LLM_DEBUGGING_GUIDE.md`, `RAG_LLM_FIX_SUMMARY.md`, `README_AUDIT_COMPLETION.md`, `SIH_DEMO_READINESS_AUDIT.md`, `SIH_FINAL_DEMO_READINESS_REPORT.md`, `SIH_LIVE_DEMO_SCRIPT.md`, `SIH_REQUIREMENT_COMPLETION_AUDIT.md`, `TARGETED_DEFECT_CYCLE_1_REPORT.md`.

Classification: FULLY CONSOLIDATED for architectural/product/security/current-state knowledge; obsolete completion claims are HISTORICAL or DEPRECATED.

### Backend historical audits, phase reports, verification, data and migration notes

`backend/AUDIT_REPORT.md`, `backend/BACKEND_CURRENT_STATE_AUDIT.md`, `backend/BACKEND_FEATURE_COMPLETION_AUDIT.md`, `backend/BACKEND_PRODUCTION_READINESS_AUDIT.md`, `backend/BACKEND_QUALITY_HARDENING_CYCLE_A_B.md`, `backend/CLASSIFICATION_CONFIRMATION.md`, `backend/DATABASE_CONSISTENCY_AUDIT.md`, `backend/DATA_DISCREPANCIES.md`, `backend/DATA_INTEGRITY_FIX_REPORT.md`, `backend/DELETION_ROOT_CAUSE_ANALYSIS.md`, `backend/DIAGNOSIS_REPORT.md`, `backend/FINAL_BLOCKER_DIAGNOSIS.md`, `backend/FINAL_E2E_VERIFICATION_REPORT.md`, `backend/FINAL_PHASE_3F_DIFF_REVIEW.md`, `backend/INVESTIGATION_INDEX.md`, `backend/LIVE_E2E_BACKEND_VERIFICATION.md`, `backend/MASTER_DATA_SYNC_REPORT.md`, `backend/PHASE3_BUG_FIX_REPORT.md`, `backend/PHASE3_FINAL_VERIFICATION.md`, `backend/PHASE3_WEEK2_VERIFICATION.md`, `backend/PHASE_1C_PLAN.md`, `backend/PHASE_1D_PLAN.md`, `backend/PHASE_1_CAPABILITY_ASSESSMENT_REPORT.md`, `backend/PHASE_1_SUMMARY.md`, `backend/PHASE_2_ARCHITECTURE_AUDIT.md`, `backend/PHASE_2_CAPABILITY_ASSESSMENT_REPORT.md`, `backend/PHASE_3F_COMPETENCY_MAPPING_AUDIT.md`, `backend/PHASE_3F_FINAL_INTEGRITY_AUDIT.md`, `backend/PHASE_3F_ROLE_COMPETENCY_MAPPING.md`, `backend/PHASE_3G_CRITICAL_SKILL_GAP_FIX.md`, `backend/PHASE_3G_CROSS_PAGE_DATA_PERFORMANCE_AUDIT.md`, `backend/PHASE_3G_DATA_CONSISTENCY_PERFORMANCE_FIX.md`, `backend/PHASE_3G_FINAL_PRODUCTION_VERIFICATION.md`, `backend/PHASE_3G_POST_ASSESSMENT_SYNC_AUDIT.md`, `backend/PHASE_3G_PRODUCTION_VERIFICATION.md`, `backend/PHASE_3_CHECKPOINT.md`, `backend/PHASE_3_DATA_AUDIT.md`, `backend/PHASE_3_DEFECT_REPORT.md`, `backend/PHASE_3_EXECUTION_GUIDE.md`, `backend/PHASE_3_FINAL_ARCHITECTURE.md`, `backend/PHASE_3_IMPLEMENTATION_PLAN.md`, `backend/PHASE_3_IMPLEMENTATION_TASKS.md`, `backend/PHASE_3_INDEX.md`, `backend/PHASE_3_NEXT_STEPS.md`, `backend/PHASE_3_QUICK_SUMMARY.md`, `backend/PHASE_3_READY.md`, `backend/PHASE_3_RECOMMENDATION_ENGINE_AUDIT.md`, `backend/PHASE_3_SUMMARY.md`, `backend/PHASE_3_WEEK1_STATUS.md`, `backend/PHASE_5_REPORT.md`, `backend/PHASE_6_GEMINI_VERIFICATION_REPORT.md`, `backend/PHASE_6_REPORT.md`, `backend/PHASE_6_VERIFICATION_CHECKLIST.md`, `backend/PHASE_6_VERIFICATION_REPORT.md`, `backend/PHASE_CAPABILITY_ASSESSMENT_AUDIT.md`, `backend/PHASE_QUIZ_ENGINE_REPORT.md`, `backend/POSTMAN_22_TEST_SPEC.md`, `backend/POSTMAN_TEST_FAILURE_REPORT.md`, `backend/POSTMAN_VERIFICATION_PLAN.md`, `backend/PRE_SEED_VALIDATION_REPORT.md`, `backend/PYTEST_ISOLATION_FIX_REPORT.md`, `backend/README_PHASE3_COMPLETE.md`, `backend/README_VALIDATION.md`, `backend/RESEARCH_COMPLETE_REPORT.md`, `backend/RESEARCH_NULL_COURSE_IDS.md`, `backend/RESEED_FINAL_REPORT.md`, `backend/RESEED_FINDINGS.md`, `backend/SEEDING_VERIFICATION_REPORT.md`, `backend/TARGETED_DEFECT_CYCLE_1_REPORT.md`, `backend/TECHNICAL_DEBT_PHASE3.md`, `backend/VALIDATION_DECISION_POINT.md`, `backend/VERIFICATION_BLOCKERS_ANALYSIS.md`, `backend/VERIFICATION_BLOCKERS_READY_FOR_FIX.md`, `backend/VERIFICATION_FAILURE_REPORT.md`, `backend/data_quality_report.md`.

Classification: FULLY CONSOLIDATED for current module map, data decisions, security, migrations, API behavior, phase history, known defects, and verification context. Individual report conclusions remain HISTORICAL where current source/tests contradict them.

### Retained Markdown documents

The following were intentionally retained and are not part of the deleted manifest: `README.md`, `ARCHITECTURE.md`, `RAG.md`, `additional_rag_datasets.md`, `deploy.md`, `strict.md`, `backend/README.md`, `backend/API_ENDPOINTS.md`, `backend/SIH_SUBMISSION_NOTES.md`, `frontend/todo.md`, `frontend/ideas.md`, and `frontend/client/PHASE_1C_SUMMARY.md`. `ARCHITECTURE.md` and `RAG.md` are empty in the current worktree; `additional_rag_datasets.md` is a proposal; `README.md`/`backend/README.md` contain stale early-phase claims; the other retained notes remain useful as supporting references until a separate deletion decision.

No implementation code was removed by this consolidation. The deletion status of historical Markdown was already present in the worktree before this file was created; this document does not stage, commit, or alter those deletions.

## 40. Document Quality Review

A new developer can use this file to identify the product loop, current modules, routes, data model, security boundaries, RAG design, provenance rules, known conflicts, test limitations, roadmap, demo path, and exact source locations. Current claims are anchored to source inventory and recorded test artifacts. Fresh executable validation and live database/provider verification remain explicitly UNKNOWN and are the first follow-up actions.
