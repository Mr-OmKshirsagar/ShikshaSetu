# ShikshaSetu Codebase Clutter & Redundancy Audit Report

> **Generated on:** September 8, 2026  
> **Repository:** `Mr-OmKshirsagar/ShikshaSetu`  
> **Branch Audited:** `clutter`  
> **Scope:** Full repository audit (Backend, Frontend, Documentation, Git Tracking, Configuration)

---

## Executive Summary

A comprehensive forensic audit of the **ShikshaSetu** repository was performed across all **2,333 tracked Git files** and local directories. The audit identified significant code clutter, dead code, development residue, duplicate datasets, and severe Git tracking anomalies.

### Key Metrics & Breakdown

| Category | Item Count | Estimated Size / Impact | Primary Concern |
| :--- | :---: | :---: | :--- |
| **Committed Python Runtime / Venv** | **1,688 files** | **~100+ MB** | Complete Python 3.14 virtualenv (`backend/.python`) tracked in Git |
| **Backend Scratch / Debug Scripts** | **87 files** | **~480 KB** | One-off diagnostic, test, and verification scripts in `backend/` root |
| **Terminal Dumps & Output Logs** | **15 files** | **~220 KB** | Ad-hoc text dumps (`test_results.txt`, `e2e_*.txt`) in `backend/` root |
| **Test Result JSON Dumps** | **4 files** | **~20 KB** | Postman and E2E verification test result dumps in `backend/` root |
| **Tracked Uploads / Binary Clutter** | **14 files** | **~23 KB** | 13 upload PDFs & `test_sample.pdf` tracked in Git despite `.gitignore` |
| **OS Metadata in Git** | **1 file** | **12.3 KB** | `.DS_Store` tracked in Git root |
| **Unused / Duplicate Datasets** | **7 files** | **~340 KB** | Exact duplicates (`igot_courses_seed_56.csv`), unread `.json` dumps |
| **Dead Frontend Prototype Pages** | **4 files** | **~152 KB** | `Home.tsx`, `LiveHome.tsx`, `LearningPage.tsx`, `NotFound.tsx` |
| **Manus AI Template Residue** | **7 items** | **~50 KB** | `template.json`, `debug-collector.js`, `ManusDialog.tsx`, `Map.tsx`, Vite plugins |
| **Unused UI Components (Shadcn)** | **38 files** | **~125 KB** | Bulk-generated UI components never imported in application pages |
| **Exact Duplicate Docs (SHA-256)** | **8 pairs (16 files)**| **~85 KB** | 8 exact bit-for-bit duplicate markdown files in `docs/` |
| **Misplaced Root Audit Reports** | **6 files** | **~75 KB** | Phase 6 audit reports placed in repo root & `backend/` root |

**Core Conclusion:** Over **75% of the files tracked in this Git repository (1,800+ of 2,333 files)** are clutter, virtual environment binaries, temporary scratchpads, or dead code that should be purged or ignored.

---

## 1. Files That Must Be Ignored in Git (Git Tracking Anomalies)

These files are currently tracked by Git but should never be in version control. They bloat repository clone times, pollute git diffs, and create platform conflicts.

### 1.1 `backend/.python/` (1,688 files — CRITICAL SEVERITY)
* **Path:** `backend/.python/`
* **Description:** An entire Python 3.14 virtual environment / runtime distribution containing binaries (`bin/python`, `bin/pip`), C headers (`include/python3.14/*.h`), and standard library packages was accidentally committed into Git.
* **Why it was committed:** The root `.gitignore` only specified `.venv/` and omitted `.python/`, `env/`, or `venv/`.
* **Action Required:**
  ```bash
  git rm -r --cached backend/.python
  ```
  Add `.python/` and `backend/.python/` to `.gitignore`.

### 1.2 `.DS_Store` (1 file — macOS System File)
* **Path:** `.DS_Store` (in repo root, 12,292 bytes)
* **Description:** macOS Finder desktop services store metadata file.
* **Why it was committed:** Missing from root `.gitignore`.
* **Action Required:**
  ```bash
  git rm --cached .DS_Store
  ```

### 1.3 `backend/uploads/materials/*.pdf` (13 files — Uploaded User Content)
* **Path:** `backend/uploads/materials/*.pdf`
  * `6a91102a585424c9c7ef7b99.pdf`
  * `6a91122e3368d8cd9ba07b31.pdf`
  * `6a9112a7b7b677d6d764f466.pdf`
  * `6a911530eedeefc7a6c66a40.pdf`
  * `6a9115804d63de45a857fba1.pdf`
  * `6a911c544d63de45a857fba4.pdf`
  * `6a9139d5de633054d9238336.pdf`
  * `6a913e4ade633054d9238338.pdf`
  * `6a913e743a9e0dc033c542a2.pdf`
  * `6a913e833a9e0dc033c542a5.pdf`
  * `6a913ecf053ca72dfb28dda9.pdf`
  * `6a913efe33e998f7640d79e1.pdf`
  * `6a913f0c33e998f7640d79e3.pdf`
* **Description:** User-uploaded trainer learning materials generated during runtime testing.
* **Why it was committed:** Although `.gitignore` lines 15–18 list `backend/uploads/materials/*.pdf`, these files were staged before the rule was added or force-committed (`git add -f`). Once tracked, `.gitignore` does not stop Git from tracking modifications.
* **Action Required:**
  ```bash
  git rm --cached backend/uploads/materials/*.pdf
  ```

### 1.4 Test Logs & Output Dumps (15 files)
* **Paths:**
  * `backend/test_results.txt` (53.0 KB)
  * `backend/e2e_full_test.txt` (34.8 KB)
  * `backend/test_rec_error.txt` (33.3 KB)
  * `backend/e2e_debug.txt` (15.6 KB)
  * `backend/e2e_test_output.txt` (14.9 KB)
  * `backend/phase3_tests.txt` (10.6 KB)
  * `backend/recommendation_tests.txt` (10.6 KB)
  * `backend/RESEARCH_FINDINGS_SUMMARY.txt` (8.7 KB)
  * `backend/VALIDATION_STATUS.txt` (8.4 KB)
  * `backend/DECISION_POINT.txt` (7.8 KB)
  * `backend/PHASE_3_WEEK1_COMPLETE.txt` (7.7 KB)
  * `backend/route_output.txt` (6.3 KB)
  * `backend/route_inspection_output.txt` (5.9 KB)
  * `backend/test_output.txt` (3.9 KB)
  * `backend/postman_results.txt` (3.2 KB)
* **Description:** Terminal command stdout redirections (`> test_results.txt`) and error logs created during debugging.
* **Action Required:** Delete files and untrack via `git rm --cached backend/*.txt`.

### 1.5 Test Result JSON Files (4 files)
* **Paths:**
  * `backend/postman_22_test_results.json` (9.1 KB)
  * `backend/postman_22_test_results_defect1.json` (4.3 KB)
  * `backend/postman_verification_results.json` (4.1 KB)
  * `backend/e2e_postman_results.json` (2.4 KB)
* **Description:** Automated test run output summaries dumped into `backend/` root.
* **Action Required:** Delete files and add `backend/*_results.json` to `.gitignore`.

### 1.6 Scratch Binary File in Backend Root
* **Path:** `backend/test_sample.pdf` (1.5 KB)
* **Description:** A dummy PDF used for route testing dumped directly in `backend/` instead of `backend/tests/fixtures/`.
* **Action Required:** Remove or relocate to `backend/tests/fixtures/`.

### 1.7 Dual Package Manager Lockfiles (Frontend)
* **Paths:** `frontend/package-lock.json` (421 KB) vs `frontend/pnpm-lock.yaml` (266 KB)
* **Description:** `package.json` declares `"packageManager": "pnpm@10.4.1"`, yet `render.yaml` (production build) executes `npm install && npm run build`, and both `package-lock.json` and `pnpm-lock.yaml` are committed. Having two lockfiles leads to divergence in installed dependency versions between local development and CI/Render deployment.
* **Action Required:** Standardize on one package manager (npm or pnpm) and remove the obsolete lockfile.

---

## 2. Missing Rules in `.gitignore`

The project root `.gitignore` is missing several critical patterns. Below is the recommended updated `.gitignore`:

```gitignore
# ==============================================================================
# ShikshaSetu Unified .gitignore
# ==============================================================================

# Environment variables
.env
.env.*
!.env.example

# Python virtual environments & runtimes
.venv/
venv/
env/
ENV/
.python/
backend/.python/

# Python compiled bytecode & caches
__pycache__/
*.py[cod]
*$py.class
.pytest_cache/
.coverage
htmlcov/
.mypy_cache/
.ruff_cache/

# Node & Frontend dependencies
node_modules/
**/node_modules/
.pnpm-store/
.npm/

# Build outputs
dist/
build/
*.dist
frontend/dist/
frontend/.vite/
.vite/

# User-uploaded content (keep directory structure with .gitkeep)
backend/uploads/materials/*
!backend/uploads/materials/.gitkeep

# Temporary test logs, stdout dumps, and diagnostic outputs
*.log
backend/*.txt
backend/*_results.json
backend/*_output.json
backend/*.pdf

# OS metadata & temporary files
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# IDE & Editor files
.vscode/
.idea/
*.swp
*.swo
*~

# Archives
*.zip
*.tar.gz
frontend.zip

# AI Generator & Scaffolding residue
frontend/client/public/__manus__/
.webdev/
```

---

## 3. Files Written Without a Reason: Backend Root Scripts (87 Files)

In `backend/`, **87 Python scripts** sit in the root directory rather than in `backend/app/` or `backend/tests/`. Every single one was created as an ad-hoc scratch script during various development phases (Phase 3, Phase 5, Phase 6) for temporary debugging, manual verification, or one-off database checks. 

Pytest ignores these root files (it only runs `backend/tests/`), meaning these 87 scripts are **completely unmaintained dead code** that clutter the backend.

### 3.1 Step Migration & Counting Scripts (9 Files)
*Temporary scripts written to check database counts before/after manual migrations.*
1. `backend/step1_backup_current_state.py` (1.1 KB) — Dumps counts before seeding.
2. `backend/step1_before_counts.py` (1.6 KB) — Records pre-seeding record counts.
3. `backend/step3_after_counts.py` (1.6 KB) — Verifies record counts post-seeding.
4. `backend/step3_verify_production.py` (2.1 KB) — Checks production database after seeding.
5. `backend/step4_integrity_checks.py` (3.1 KB) — Asserts reference integrity across MongoDB collections.
6. `backend/step4_role_requirements.py` (1.9 KB) — Verifies role requirement references.
7. `backend/step5_mappings_integrity.py` (2.3 KB) — Checks learning resource mapping integrity.
8. `backend/step5_mappings_integrity_fixed.py` (2.5 KB) — Bugfix variation of `step5_mappings_integrity.py`.
9. `backend/step5_verify_http.py` (3.4 KB) — Makes HTTP requests to verify mapping endpoints.

### 3.2 Postman & HTTP Verification Runners (5 Files)
*Hardcoded HTTP client scripts simulating Postman runner suites.*
10. `backend/postman_22_tests.py` (19.7 KB) — 22 hardcoded HTTP tests for Postman spec.
11. `backend/postman_22_final_verification.py` (13.4 KB) — Second iteration of the 22 tests.
12. `backend/postman_verification.py` (17.0 KB) — Another variant of the 22 HTTP tests.
13. `backend/postman_verification_full.py` (11.3 KB) — Automated runner variant.
14. `backend/e2e_postman_real.py` (13.5 KB) — HTTP end-to-end integration test runner.

### 3.3 Batch Test Runners & Diagnosers (3 Files)
15. `backend/run_22_tests.py` (21.3 KB) — Duplicate runner script for the 22 endpoint checks.
16. `backend/run_full_22_tests.py` (4.2 KB) — Lightweight wrapper for `run_22_tests.py`.
17. `backend/run_audit_diagnostics.py` (6.9 KB) — Audit diagnostic runner.

### 3.4 Phase-Specific Verification Scripts (5 Files)
*Scripts hardcoded for specific historical audit milestones.*
18. `backend/PHASE_3_DEFECT_DIAGNOSIS.py` (9.9 KB) — Audit of failed Phase 3 tests.
19. `backend/phase6_e2e_verification.py` (11.4 KB) — AI pipeline verification for Phase 6.
20. `backend/phase6_e2e_verification_fixed.py` (11.4 KB) — Exact duplicate/patch of `phase6_e2e_verification.py`.
21. `backend/phase6_gemini_live_test.py` (12.8 KB) — One-off live test against Google Gemini API.
22. `backend/manual_verification_phase6.py` (12.7 KB) — Manual verification CLI for Phase 6.

### 3.5 Ad-Hoc Test Scripts (11 Files)
*Scratch tests written outside the standard `pytest` suite in `backend/tests/`.*
23. `backend/test_configs.py` (0.8 KB) — Direct HTTP GET to config endpoints.
24. `backend/test_defect1.py` (1.0 KB) — Scratch test for defect #1.
25. `backend/test_defect2.py` (1.0 KB) — Scratch test for defect #2.
26. `backend/test_get_endpoint.py` (1.2 KB) — Tests GET material endpoint.
27. `backend/test_http_queries.py` (3.1 KB) — Ad-hoc HTTP query checks.
28. `backend/test_mapping_query.py` (2.2 KB) — Queries mapping MongoDB collection.
29. `backend/test_rag_full.py` (5.8 KB) — Ad-hoc full RAG pipeline test.
30. `backend/test_rag_upload.py` (4.7 KB) — Ad-hoc upload endpoint test.
31. `backend/test_registration_debug.py` (1.5 KB) — Debugs user registration endpoint.
32. `backend/test_scope_dict.py` (2.5 KB) — Tests dictionary scoping logic.
33. `backend/test_upload_schema.py` (3.3 KB) — Validates upload payload Pydantic schema.

### 3.6 Diagnostic & Route Inspection Scripts (16 Files)
*Scripts created solely to inspect FastAPI route tables or print MongoDB records to stdout.*
34. `backend/audit_database.py` (10.0 KB) — Directly connects to Mongo and audits data.
35. `backend/audit_endpoints.py` (4.7 KB) — Iterates over `app.routes` and prints endpoints.
36. `backend/check_routes.py` (0.3 KB) — 10-line script printing route paths.
37. `backend/inspect_route.py` (1.0 KB) — Inspects specific `/config` route handler.
38. `backend/debug_defect1.py` (0.9 KB) — In-memory test client debugging defect #1.
39. `backend/debug_routing.py` (1.4 KB) — Fastapi routing debug.
40. `backend/deep_route_inspection.py` (3.8 KB) — Inspects material upload routes.
41. `backend/deep_route_inspection_v2.py` (3.8 KB) — Revision 2 of material upload route inspection.
42. `backend/diagnose_db.py` (5.4 KB) — Direct MongoDB diagnosis.
43. `backend/diagnose_db_deep.py` (3.9 KB) — Inspects orphan records in MongoDB.
44. `backend/diagnose_rag_error.py` (3.3 KB) — Diagnoses RAG/LLM processing errors.
45. `backend/diagnose_user_id.py` (2.7 KB) — Checks user ID mismatches.
46. `backend/inspect_null_records.py` (3.7 KB) — Inspects courses with `null` IDs.
47. `backend/investigate_failures.py` (3.7 KB) — Investigates specific test failures.
48. `backend/investigate_resource_ids.py` (2.1 KB) — Investigates resource ID formats.
49. `backend/detailed_validation.py` (8.6 KB) — Validation diagnostic print script.

### 3.7 Database / Route / Configuration Checks (10 Files)
50. `backend/check_beh_competency.py` (0.9 KB) — Checks behavioral competency records.
51. `backend/check_data.py` (1.2 KB) — Quick print of MongoDB collections.
52. `backend/check_gemini_models.py` (0.3 KB) — Checks available Google Gemini models via SDK.
53. `backend/check_latest_material.py` (0.7 KB) — Fetches latest material document from MongoDB.
54. `backend/check_mongo_state.py` (0.7 KB) — Checks Mongo connection during test runs.
55. `backend/check_null_course_id.py` (1.3 KB) — Analyzes courses with null IDs.
56. `backend/check_roles.py` (0.4 KB) — Prints user roles in database.
57. `backend/check_seed_state.py` (0.6 KB) — Verifies seed state.
58. `backend/check_test4.py` (1.2 KB) — Checks Test #4 endpoint.
59. `backend/list_all_configs.py` (0.4 KB) — Prints assessment configs.

### 3.8 Verification & Utility Scripts (18 Files)
60. `backend/verify_apis.py` (7.8 KB) — Endpoint verification utility.
61. `backend/verify_data.py` (2.4 KB) — Data integrity checks.
62. `backend/verify_db_isolation.py` (2.4 KB) — Verifies DB isolation in test environment.
63. `backend/verify_defects_cycle_1.py` (13.3 KB) — Cycle 1 defect verification.
64. `backend/verify_fixes.py` (2.9 KB) — Checks applied bugfixes.
65. `backend/verify_fixes_v2.py` (3.8 KB) — Version 2 of `verify_fixes.py`.
66. `backend/verify_quiz_security.py` (6.0 KB) — Checks quiz security rules.
67. `backend/verify_seed.py` (6.7 KB) — Verifies master seed state.
68. `backend/verify_sync.py` (8.0 KB) — Verifies synchronization between resources and competencies.
69. `backend/final_fix_verification.py` (2.6 KB) — Final fix verification script.
70. `backend/final_integrity_check.py` (4.2 KB) — Final MongoDB integrity checks.
71. `backend/manual_verification.py` (6.4 KB) — CLI manual verification helper.
72. `backend/original_e2e.py` (0.8 KB) — Deprecated original E2E test script.
73. `backend/preview_nssta_classification.py` (5.5 KB) — NSSTA course classifier preview.
74. `backend/register_test_user.py` (1.4 KB) — Registers a single test user.
75. `backend/research_null_courses.py` (4.0 KB) — Queries courses with null IDs.
76. `backend/document_active_data.py` (2.1 KB) — Generates active data summary.
77. `backend/find_empty_ids.py` (0.7 KB) — Searches for empty ObjectId strings.

### 3.9 One-Off Database State Manipulation Scripts (10 Files)
*Scripts that write or alter MongoDB data outside of the canonical `seed_master.py`.*
78. `backend/cleanup_failed_materials.py` (2.9 KB) — Deletes failed materials from MongoDB.
79. `backend/clear_mappings.py` (0.4 KB) — Truncates resource mappings collection.
80. `backend/create_demo_accounts.py` (2.0 KB) — Creates demo accounts (already handled in seed).
81. `backend/create_test_fixtures.py` (6.2 KB) — Creates test fixtures in database.
82. `backend/execute_seeding.py` (5.6 KB) — One-off seeding executor.
83. `backend/fix_test_user_role.py` (1.6 KB) — One-off update of a test user's role.
84. `backend/generate_email_preview.py` (12.4 KB) — Generates sample HTML email previews.
85. `backend/get_test_user.py` (0.6 KB) — Prints test user credentials.
86. `backend/validation_script.py` (6.1 KB) — One-off validation script.
87. `backend/e2e_verify.py` (31.6 KB) — Massive 31 KB script containing duplicated verification routines.

> **Recommendation for Backend Root Scripts:**  
> None of these 87 scripts are imported by `app/` or run by `pytest`. Legitimate automated tests already exist in `backend/tests/` (43 test files). These 87 scripts should either be deleted or archived into a non-tracked `backend/archive_scripts/` directory if needed for historical reference.

---

## 4. Redundant Datasets & Unused JSON Conversions in Backend Root

The root of `backend/` contains several large CSV and JSON files that are either exact duplicates, obsolete, or never read by any part of the application or seeding scripts.

| File | Size | Status / Description |
| :--- | :---: | :--- |
| `backend/igot_courses_seed_56.csv` | 39.9 KB | **Exact Duplicate** of `igot_courses_dataset.csv` (SHA-256: `FECD48B96A54...`). Superseded by `igot_courses_enriched.csv`. Completely redundant. |
| `backend/igot_courses_dataset.csv` | 39.9 KB | **Obsolete**. The master seed (`seed_master.py` & `seed_learning_resources.py`) uses `igot_courses_enriched.csv`. |
| `backend/competency_taxonomy.json` | 46.2 KB | **Unused**. `seed_master.py` and `seed_competencies.py` parse `competency_taxonomy.csv`. This JSON file is never imported or read. |
| `backend/igot_courses_enriched.json` | 119.8 KB | **Unused**. `seed_learning_resources.py` reads `igot_courses_enriched.csv`. This JSON file is an unreferenced export. |
| `backend/nssta_training_programmes.json` | 78.9 KB | **Unused**. `seed_learning_resources.py` reads `nssta_training_programmes.csv`. This JSON is unreferenced. |
| `backend/source_registry.csv` | 3.3 KB | **Unused**. Documentation (`docs/backend_PHASE_3_INDEX.md`) explicitly notes this is a reference table "not loaded in Phase 3". Never loaded anywhere. |
| `backend/api_endpoints.json` | 14.6 KB | **Unused Dump**. A static JSON export of API route schemas, completely unreferenced by any backend or frontend code. |

> **Active Seed Files (Keep):**  
> Only the following 5 CSV files are actually read by `app/scripts/seed_master.py`:
> 1. `competency_taxonomy.csv`
> 2. `igot_courses_enriched.csv`
> 3. `course_competency_mapping.csv`
> 4. `nssta_training_programmes.csv`
> 5. `nssta_competency_mapping.csv`  
> *(Recommendation: Move these active CSVs into `backend/app/data/` so they don't clutter the root directory.)*

---

## 5. Frontend Clutter: Dead Pages, Boilerplate & Unused Code

### 5.1 Dead / Unrouted Prototype Pages (152.8 KB)
The frontend application uses a custom role-based portal router in `App.tsx` (`RoleRouter` switching between `TrainerApp`, `AdminApp`, and `OfficialApp`). Four complete page files in `frontend/client/src/pages/` are **completely unrouted and unrendered**:

| Dead Page File | Size | Lines | Rationale / Note |
| :--- | :---: | :---: | :--- |
| `frontend/client/src/pages/Home.tsx` | **83.4 KB** | 696 | Initial development prototype with mock UI, placeholder stats, and hardcoded flows. Never referenced in `App.tsx`. |
| `frontend/client/src/pages/LiveHome.tsx` | **56.9 KB** | 900 | Monolithic prototype containing duplicated official/trainer views and redundant API wrappers. Never imported in `App.tsx`. |
| `frontend/client/src/pages/LearningPage.tsx` | **10.8 KB** | 287 | Early prototype for the learning module. Superseded by `OfficialLearning.tsx`. Never imported. |
| `frontend/client/src/pages/NotFound.tsx` | **1.8 KB** | 42 | 404 page originally built for `wouter` router. The app now routes via `useAuth().user.access_role` and never shows this page. |

#### Related Dead Code in `api.ts`
Because `LiveHome.tsx` was abandoned, lines 1463–1490 in `frontend/client/src/lib/api.ts` contain 27 lines of legacy flat API aliases explicitly marked:
```typescript
// ── Legacy flat aliases kept for backwards-compat with LiveHome.tsx ──────
```
These aliases are dead code once `LiveHome.tsx` is removed.

### 5.2 Manus AI Generator Residue & Scaffolding Artifacts (~50 KB)
The frontend was originally initialized using the Manus AI platform generator. Several generator-specific files, plugins, and configurations were left in the codebase:

1. **`frontend/template.json` (14.4 KB)**  
   Contains a raw JSON dump of the template generator scaffolding, including stringified boilerplate code for an app named `"learnflow-education-frontend"`.
2. **`frontend/client/public/__manus__/debug-collector.js` (26.0 KB)**  
   A client-side telemetry/inspector script injected by the Manus development container.
3. **`frontend/client/src/components/ManusDialog.tsx` (2.5 KB)**  
   A modal dialog with hardcoded text: *"Please login with Manus to continue"*. Never imported anywhere in the project.
4. **`frontend/client/src/components/Map.tsx` (5.1 KB)**  
   A Google Maps component template defaulting to San Francisco coordinates (`lat: 37.7749, lng: -122.4194`) that attempts to connect to `forge.butterfly-effect.dev` (Manus backend forge API). Completely unused.
5. **`@types/google.maps` in `package.json`**  
   DevDependency installed solely for the dead `Map.tsx` component.
6. **`frontend/patches/wouter@3.7.1.patch` (1.0 KB)**  
   A patch that mutates `wouter` to register all route paths into `window.__WOUTER_ROUTES__` for the Manus preview environment. `wouter` is no longer used in `App.tsx`.
7. **Manus Plugins in `frontend/vite.config.ts`**  
   Lines 14–142 define `vitePluginManusRuntime()`, `vitePluginManusDebugCollector()`, and `vitePluginStorageProxy()`. Furthermore, `allowedHosts` lists `.manus.computer`, `.manuspre.computer`, `.manusvm.computer`, etc., and resolves an alias `@assets` to non-existent `attached_assets`.

### 5.3 Dead Utilities, Deprecated Wrappers & Standalone Servers
1. **`frontend/client/src/components/LearningActivityCard.tsx` (7.0 KB)**  
   A 193-line card component never imported anywhere (the actual activities in `OfficialLearning.tsx` are rendered inline).
2. **`frontend/client/src/services/api.ts` (0.2 KB) & `frontend/client/src/services/__tests__/api.test.ts`**  
   A deprecated 7-line file that re-exports `@/lib/api`. No file in the repository imports from `services/api`.
3. **`frontend/client/src/const.ts` (0.7 KB) & `frontend/shared/const.ts` (0.1 KB)**  
   Contains `COOKIE_NAME`, `ONE_YEAR_MS`, and `getLoginUrl()`. Neither `getLoginUrl` nor the constants are ever consumed by the application (auth uses localStorage `shikshasetu_token`).
4. **`frontend/client/src/types/index.ts` (0.1 KB)**  
   A 3-line re-export (`export * from "../lib/api"`) never imported by any file.
5. **`frontend/server/index.ts` (1.0 KB)**  
   A standalone Express HTTP server designed to serve `dist/public`. In production (Render), the frontend is configured as `runtime: static` (Render serves the static files directly without Node). In local development, `vite --host` is used. This Express server is redundant and incurs `express` and `esbuild` dependencies.
6. **Placeholder `.gitkeep` Files**  
   `frontend/.gitkeep` and `frontend/client/public/.gitkeep` are empty files in directories that already contain actual code/assets.

### 5.4 Unused Shadcn/UI Components (38 Files, ~125 KB)
The project contains 45+ components in `frontend/client/src/components/ui/`. An import analysis reveals that all pages (`AdminDashboard`, `TrainerDashboard`, `OfficialDashboard`, `SkillGapAnalytics`, etc.) use raw HTML elements with Tailwind utility classes rather than Shadcn component wrappers.

Only **`button.tsx`**, **`card.tsx`**, **`dialog.tsx`**, **`input.tsx`**, **`label.tsx`**, **`sonner.tsx`**, and **`tooltip.tsx`** have active consumers.

The following **38 UI components** are never imported outside `components/ui/`:
```
frontend/client/src/components/ui/accordion.tsx
frontend/client/src/components/ui/alert-dialog.tsx
frontend/client/src/components/ui/aspect-ratio.tsx
frontend/client/src/components/ui/avatar.tsx
frontend/client/src/components/ui/badge.tsx
frontend/client/src/components/ui/breadcrumb.tsx
frontend/client/src/components/ui/button-group.tsx
frontend/client/src/components/ui/calendar.tsx
frontend/client/src/components/ui/carousel.tsx
frontend/client/src/components/ui/chart.tsx
frontend/client/src/components/ui/checkbox.tsx
frontend/client/src/components/ui/collapsible.tsx
frontend/client/src/components/ui/command.tsx
frontend/client/src/components/ui/context-menu.tsx
frontend/client/src/components/ui/drawer.tsx
frontend/client/src/components/ui/dropdown-menu.tsx
frontend/client/src/components/ui/empty.tsx
frontend/client/src/components/ui/field.tsx
frontend/client/src/components/ui/form.tsx
frontend/client/src/components/ui/hover-card.tsx
frontend/client/src/components/ui/input-group.tsx
frontend/client/src/components/ui/input-otp.tsx
frontend/client/src/components/ui/item.tsx
frontend/client/src/components/ui/kbd.tsx
frontend/client/src/components/ui/menubar.tsx
frontend/client/src/components/ui/navigation-menu.tsx
frontend/client/src/components/ui/pagination.tsx
frontend/client/src/components/ui/popover.tsx
frontend/client/src/components/ui/progress.tsx
frontend/client/src/components/ui/radio-group.tsx
frontend/client/src/components/ui/resizable.tsx
frontend/client/src/components/ui/scroll-area.tsx
frontend/client/src/components/ui/select.tsx
frontend/client/src/components/ui/sidebar.tsx
frontend/client/src/components/ui/slider.tsx
frontend/client/src/components/ui/spinner.tsx
frontend/client/src/components/ui/switch.tsx
frontend/client/src/components/ui/table.tsx
frontend/client/src/components/ui/tabs.tsx
frontend/client/src/components/ui/toggle-group.tsx
```

---

## 6. Documentation Clutter & Redundancies

### 6.1 Identical 100% SHA-256 Duplicate Pairs in `docs/` (8 Pairs)
There are 8 pairs of markdown files in `docs/` where one file is prefixed with `backend_` and the other is not, yet both have **identical cryptographic SHA-256 hashes**:

| Duplicate Pair | File Size | SHA-256 Hash |
| :--- | :---: | :--- |
| `docs/backend_DATABASE_CONSISTENCY_AUDIT.md`<br>`docs/DATABASE_CONSISTENCY_AUDIT.md` | 7.9 KB | `331268A0D9B8C9D6EE6A121DEF763741...` |
| `docs/backend_BACKEND_CURRENT_STATE_AUDIT.md`<br>`docs/BACKEND_CURRENT_STATE_AUDIT.md` | 13.9 KB | `32AE3381B5E385AC77FE1E383925F4FB...` |
| `docs/backend_BACKEND_FEATURE_COMPLETION_AUDIT.md`<br>`docs/BACKEND_FEATURE_COMPLETION_AUDIT.md` | 11.8 KB | `8B3100BE7D844A8EBE0E341F2CDAFDE7...` |
| `docs/backend_BACKEND_PRODUCTION_READINESS_AUDIT.md`<br>`docs/BACKEND_PRODUCTION_READINESS_AUDIT.md` | 13.8 KB | `9A55FBC62B9C8E8B3D9D5E8C949D6A42...` |
| `docs/backend_BACKEND_QUALITY_HARDENING_CYCLE_A_B.md`<br>`docs/BACKEND_QUALITY_HARDENING_CYCLE_A_B.md` | 11.2 KB | `2EF736E999E6C38865D39962294AEF80...` |
| `docs/backend_LIVE_E2E_BACKEND_VERIFICATION.md`<br>`docs/LIVE_E2E_BACKEND_VERIFICATION.md` | 10.6 KB | `F1FD233EF88A6E3B95B11C1C52CE621B...` |
| `docs/backend_MASTER_DATA_SYNC_REPORT.md`<br>`docs/MASTER_DATA_SYNC_REPORT.md` | 10.1 KB | `5D0E3BF00300A523924B8B2E0B5B16F3...` |
| `docs/backend_TARGETED_DEFECT_CYCLE_1_REPORT.md`<br>`docs/TARGETED_DEFECT_CYCLE_1_REPORT.md` | 11.8 KB | `2FD37CAEEF581A43A3A95E7C82EE22D0...` |

*Action:* Delete one copy from each pair.

### 6.2 Misplaced Audit Reports in Root Directories
Six Phase 6 audit reports were saved directly in the project root and `backend/` root rather than inside `docs/`:
1. `PHASE_6B_COPILOT_LATENCY_AUDIT.md` (root, 8.8 KB)
2. `PHASE_6B_COPILOT_LATENCY_FIX_REPORT.md` (root, 10.4 KB)
3. `PHASE_6C_ADMIN_LEARNING_AUDIT.md` (root, 10.2 KB)
4. `PHASE_6C_ADMIN_LEARNING_FIX_REPORT.md` (root, 15.5 KB)
5. `PHASE_6D_EMAIL_AUDIT.md` (root, 14.1 KB)
6. `backend/PHASE_6D_EMAIL_IMPLEMENTATION_REPORT.md` (`backend/`, 16.3 KB)

*Action:* Move these 6 reports into `docs/` alongside the other phase reports.

### 6.3 Historical Phase Documentation Bloat (156 Files in `docs/`)
`docs/` contains 156 markdown files documenting every granular testing step, defect cycle, and checkpoint from Phases 1, 2, 3, 5, and 6 (e.g., `backend_PHASE_3_READY.md`, `backend_PHASE_3_WEEK1_STATUS.md`, `backend_SIH_SUBMISSION_NOTES.md`, `backend_RESEARCH_NULL_COURSE_IDS.md`). 
*Action:* Consolidate core architectural documentation and move historical phase notes into a `docs/archive/` subfolder.

---

## 7. Prioritized Remediation Roadmap

To clean up the repository safely without breaking any active features, follow this 4-stage action plan:

### Stage 1: Purge Git Tracking Bloat & Fix `.gitignore` (Immediate P0)
1. **Remove `.python` runtime from Git:**
   ```bash
   git rm -r --cached backend/.python
   ```
2. **Remove `.DS_Store`:**
   ```bash
   git rm --cached .DS_Store
   ```
3. **Remove tracked uploaded PDFs:**
   ```bash
   git rm --cached backend/uploads/materials/*.pdf
   ```
4. **Update `.gitignore`** with the comprehensive rules specified in Section 2.
5. **Commit the `.gitignore` update and index cleanup:**
   ```bash
   git commit -m "fix(git): untrack python virtualenv, .DS_Store, and uploaded PDFs"
   ```

### Stage 2: Clean Up Backend Root (P1)
1. **Delete 15 test dump text files:**
   ```bash
   rm backend/test_results.txt backend/e2e_full_test.txt backend/test_rec_error.txt backend/e2e_debug.txt backend/e2e_test_output.txt backend/phase3_tests.txt backend/recommendation_tests.txt backend/RESEARCH_FINDINGS_SUMMARY.txt backend/VALIDATION_STATUS.txt backend/DECISION_POINT.txt backend/PHASE_3_WEEK1_COMPLETE.txt backend/route_output.txt backend/route_inspection_output.txt backend/test_output.txt backend/postman_results.txt
   ```
2. **Delete 4 test result JSON files & test sample PDF:**
   ```bash
   rm backend/postman_22_test_results.json backend/postman_22_test_results_defect1.json backend/postman_verification_results.json backend/e2e_postman_results.json backend/test_sample.pdf
   ```
3. **Archive or delete the 87 scratch Python scripts in `backend/`** (all active tests remain safely in `backend/tests/`).
4. **Remove redundant dataset duplicates:**
   ```bash
   rm backend/igot_courses_seed_56.csv backend/igot_courses_dataset.csv backend/competency_taxonomy.json backend/igot_courses_enriched.json backend/nssta_training_programmes.json backend/source_registry.csv backend/api_endpoints.json
   ```
5. **Move active seed CSVs** (`competency_taxonomy.csv`, `igot_courses_enriched.csv`, `course_competency_mapping.csv`, `nssta_training_programmes.csv`, `nssta_competency_mapping.csv`) into `backend/app/data/` and update paths in `seed_master.py`.

### Stage 3: Clean Up Frontend Dead Code & Residue (P1)
1. **Delete dead prototype pages:**
   ```bash
   rm frontend/client/src/pages/Home.tsx frontend/client/src/pages/LiveHome.tsx frontend/client/src/pages/LearningPage.tsx frontend/client/src/pages/NotFound.tsx
   ```
2. **Delete Manus AI residue:**
   ```bash
   rm frontend/template.json
   rm -r frontend/client/public/__manus__
   rm frontend/client/src/components/ManusDialog.tsx
   rm frontend/client/src/components/Map.tsx
   rm frontend/patches/wouter@3.7.1.patch
   ```
3. **Clean `frontend/vite.config.ts`:**
   * Remove `vitePluginManusRuntime()`, `vitePluginManusDebugCollector()`, `vitePluginStorageProxy()`.
   * Remove `.manus.computer` allowed hosts and `@assets` alias.
4. **Delete dead component wrappers & server:**
   ```bash
   rm frontend/client/src/components/LearningActivityCard.tsx
   rm frontend/client/src/services/api.ts
   rm frontend/client/src/services/__tests__/api.test.ts
   rm frontend/client/src/const.ts frontend/shared/const.ts
   rm frontend/client/src/types/index.ts
   rm frontend/server/index.ts
   rm frontend/.gitkeep frontend/client/public/.gitkeep
   ```
5. **Clean unused Shadcn/UI components:** Delete the 38 unreferenced components from `frontend/client/src/components/ui/`.
6. **Standardize lockfiles:** Standardize on npm (`package-lock.json`), delete `pnpm-lock.yaml`, and update `package.json` `"packageManager"`.

### Stage 4: Documentation Consolidation (P2)
1. **Delete the 8 duplicate markdown files in `docs/`:**
   ```bash
   rm docs/DATABASE_CONSISTENCY_AUDIT.md docs/BACKEND_CURRENT_STATE_AUDIT.md docs/BACKEND_FEATURE_COMPLETION_AUDIT.md docs/BACKEND_PRODUCTION_READINESS_AUDIT.md docs/BACKEND_QUALITY_HARDENING_CYCLE_A_B.md docs/LIVE_E2E_BACKEND_VERIFICATION.md docs/MASTER_DATA_SYNC_REPORT.md docs/TARGETED_DEFECT_CYCLE_1_REPORT.md
   ```
2. **Move root Phase 6 audit reports into `docs/`:**
   ```bash
   mv PHASE_6B_COPILOT_LATENCY_AUDIT.md docs/
   mv PHASE_6B_COPILOT_LATENCY_FIX_REPORT.md docs/
   mv PHASE_6C_ADMIN_LEARNING_AUDIT.md docs/
   mv PHASE_6C_ADMIN_LEARNING_FIX_REPORT.md docs/
   mv PHASE_6D_EMAIL_AUDIT.md docs/
   mv backend/PHASE_6D_EMAIL_IMPLEMENTATION_REPORT.md docs/
   ```
3. **Archive historical phase notes** into `docs/archive/`.

---

## 8. Summary Table of Files Written Without a Reason / Clutter

| File / Folder Path | Category | Reason Written / Clutter Nature | Recommended Action |
| :--- | :--- | :--- | :--- |
| `backend/.python/` (1,688 files) | Git Tracking Bloat | Python 3.14 virtualenv accidentally committed to Git | Untrack & ignore in `.gitignore` |
| `.DS_Store` | Git Tracking Bloat | macOS folder metadata | Untrack & ignore in `.gitignore` |
| `backend/uploads/materials/*.pdf` (13 files) | Git Tracking Bloat | Runtime trainer upload files tracked in Git | Untrack via `git rm --cached` |
| `backend/step1_backup_current_state.py` through `step5_verify_http.py` (9 files) | Backend Scratch Script | One-off migration count checks | Delete / Archive |
| `backend/postman_22_tests.py` & 4 variants | Backend Scratch Script | Ad-hoc HTTP test scripts (duplicates) | Delete / Archive |
| `backend/run_22_tests.py` & variants (3 files) | Backend Scratch Script | Ad-hoc batch test runners | Delete / Archive |
| `backend/PHASE_3_DEFECT_DIAGNOSIS.py` & Phase 6 scripts (5 files) | Backend Scratch Script | Historical phase defect diagnosis | Delete / Archive |
| `backend/test_configs.py` through `test_upload_schema.py` (11 files) | Backend Scratch Script | One-off test scripts outside `pytest` | Delete / Archive |
| `backend/audit_database.py` through `detailed_validation.py` (16 files) | Backend Scratch Script | Diagnostics & route inspection scripts | Delete / Archive |
| `backend/check_beh_competency.py` through `list_all_configs.py` (10 files) | Backend Scratch Script | Ad-hoc collection & route check scripts | Delete / Archive |
| `backend/verify_apis.py` through `find_empty_ids.py` (18 files) | Backend Scratch Script | Temporary verification scripts | Delete / Archive |
| `backend/cleanup_failed_materials.py` through `validation_script.py` (10 files) | Backend Scratch Script | One-off DB state manipulation scripts | Delete / Archive |
| `backend/*.txt` (15 files) | Test Output / Log Dumps | Terminal output redirections & logs | Delete & add to `.gitignore` |
| `backend/*_results.json` (4 files) | Test Output / Log Dumps | Postman/E2E test result JSON dumps | Delete & add to `.gitignore` |
| `backend/test_sample.pdf` | Test Binary Dump | Scratch PDF in backend root | Delete / Move to fixtures |
| `backend/igot_courses_seed_56.csv` | Redundant Dataset | Exact byte-for-byte duplicate of `igot_courses_dataset.csv` | Delete |
| `backend/igot_courses_dataset.csv` | Redundant Dataset | Obsolete dataset superseded by `igot_courses_enriched.csv` | Delete |
| `backend/competency_taxonomy.json` | Redundant Dataset | Unread JSON copy of `competency_taxonomy.csv` | Delete |
| `backend/igot_courses_enriched.json` | Redundant Dataset | Unread JSON copy of `igot_courses_enriched.csv` | Delete |
| `backend/nssta_training_programmes.json` | Redundant Dataset | Unread JSON copy of `nssta_training_programmes.csv` | Delete |
| `backend/source_registry.csv` | Redundant Dataset | Reference table never loaded in code | Delete |
| `backend/api_endpoints.json` | Redundant Dataset | Static API route dump never loaded in code | Delete |
| `frontend/client/src/pages/Home.tsx` | Dead Page | Unrouted prototype home page (83 KB) | Delete |
| `frontend/client/src/pages/LiveHome.tsx` | Dead Page | Unrouted monolithic prototype (57 KB) | Delete |
| `frontend/client/src/pages/LearningPage.tsx` | Dead Page | Unrouted prototype learning page (11 KB) | Delete |
| `frontend/client/src/pages/NotFound.tsx` | Dead Page | Unrouted 404 page (replaced by role routing) | Delete |
| `frontend/template.json` | Manus Residue | Scaffolding dump from Manus generator | Delete |
| `frontend/client/public/__manus__/` | Manus Residue | Debug collector script from Manus | Delete |
| `frontend/client/src/components/ManusDialog.tsx` | Manus Residue | "Login with Manus" modal, never imported | Delete |
| `frontend/client/src/components/Map.tsx` | Manus Residue | Unused SF map connecting to Manus forge | Delete |
| `frontend/patches/wouter@3.7.1.patch` | Manus Residue | Patch collecting routes for Manus preview | Delete |
| `frontend/client/src/components/LearningActivityCard.tsx` | Unused Component | Activity card never imported | Delete |
| `frontend/client/src/services/api.ts` & test | Deprecated Wrapper | Unused 7-line re-export wrapper | Delete |
| `frontend/client/src/const.ts` & `frontend/shared/const.ts` | Dead Code | Unused cookie & OAuth constants | Delete |
| `frontend/server/index.ts` | Dead Code | Redundant Express static server | Delete |
| `frontend/client/src/components/ui/*` (38 files) | Unused UI Components | Shadcn components never imported | Delete |
| `frontend/pnpm-lock.yaml` | Lockfile Conflict | Conflicts with `package-lock.json` and `render.yaml` | Delete (if using npm) |
| `docs/backend_*` duplicates (8 files) | Documentation Clutter | Exact 100% duplicate markdown files in `docs/` | Delete 1 of each pair |
| `PHASE_6*` in root & backend (6 files) | Misplaced Reports | Phase reports saved in root directories | Move to `docs/` |

---
*End of Clutter & Redundancy Audit Report.*
