# PHASE 5E — ROLE RESOLUTION INTEGRITY REPORT

**Timestamp:** 2026-09-06  
**Status:** Completed  
**Repository:** ShikshaSetu (Advanced Competency-Based Learning Platform)

---

## 1. Role Resolution Architecture Before

Previously, user professional role resolution was intended to map a user's `(department, designation)` to a role document in the `roles` collection. The process was orchestrated during registration (`POST /api/v1/auth/register`) and profile updates (`PUT /api/v1/users/me`).

The legacy resolution flow in `backend/app/roles/resolver.py`:
1. Searched active roles for matching department and designation.
2. Searched active roles for designation match across all departments.
3. **Silent Fallback:** If no match was found, it queried `roles.find_one({"role_code": "STATISTICAL_OFFICER"})`.
4. **Secondary Fallback:** If Statistical Officer was not found, it picked `roles.find_one({"status": "active"})` or `roles.find_one({})`.
5. In `backend/app/learning_resources/service.py`, if a user had no role, recommendations silently fetched 10 arbitrary catalog competencies and generated fake recommendations.
6. In `backend/app/admin/service.py`, the user management list defaulted unassigned roles to `"Statistical Officer"`.

---

## 2. Silent Fallbacks Discovered

| Area | Location | Legacy Code / Behavior | Risk |
|---|---|---|---|
| **Role Resolver** | `backend/app/roles/resolver.py:59-71` | `default_role = db.roles.find_one({"role_code": "STATISTICAL_OFFICER"}) ... return default_role["_id"]` | Unmapped departments/designations silently received Statistical Officer requirements. |
| **Secondary Role Resolver** | `backend/app/roles/resolver.py:65-71` | `return roles[0]["_id"]` | If `STATISTICAL_OFFICER` not found, arbitrary first role was assigned. |
| **Recommendation Engine** | `backend/app/learning_resources/service.py:328-333` | Fallback generated 10 arbitrary competencies from catalog if user lacked role | Unresolved users saw leaked or fake recommendations. |
| **Admin User List** | `backend/app/admin/service.py:623` | `role_doc.get("role_name", "Statistical Officer")` | Admins saw misleading role assignments in management UI. |

---

## 3. Root Cause

The original implementation prioritized "always returning a role to avoid empty screens" over authoritative data integrity. This violated the core ShikshaSetu invariant that role-specific competency requirements, skill gaps, and personalized recommendations must only be derived from explicitly resolved roles.

---

## 4. New Unresolved-Role Behavior

1. **Strict Deterministic Resolution:** `resolve_role_for_user()` returns `None` if the user's `department` and `designation` do not match any configured role mapping.
2. **Explicit Role State:** A user without a valid mapping has `role_id: None` (UNRESOLVED).
3. **Identity & Data Preservation:** Unresolved users retain their:
   - Department and Designation
   - Identity, credentials, and access role (`OFFICIAL`, `TRAINER`, `ADMIN`)
   - Supporting and Authoritative historical evidence (`competency_evidence`, `quiz_attempts`, `learning_activities`)
4. **Clean API Semantics:**
   - `GET /api/v1/skill-gaps/me`: Returns HTTP 422 with `{"detail": "Role mapping pending. Please contact an administrator or update your department/designation."}`.
   - `GET /api/v1/recommendations`: Returns empty list `[]` with metadata status `"ROLE_MAPPING_PENDING"`.
   - `GET /api/v1/competencies/me`: Returns user's actual profile records without injecting unauthorized role requirements.

---

## 5. Admin Resolution Path

Implemented the minimum secure administrative role assignment workflow:

- **Endpoint:** `POST /api/v1/admin/users/{user_id}/assign-role`
- **Security:**
  - `require_admin` dependency (ADMIN access role only).
  - Validates target `user_id` exists.
  - Validates target `role_id` exists and is active in `roles`.
  - Blocks self-promotion / access-role mutation (preserves RBAC separation).
  - Reconciles competency requirements via `reconcile_user_competencies(db, user_id, new_role_id)`.
  - Audit-friendly log and updated timestamps.

---

## 6. Existing User Audit

Audited configured role mappings and user documents:
- Configured Roles in Database/Fixtures: `STATISTICAL_OFFICER`, `DIRECTOR_STATISTICS`, `DATA_ANALYST`, `EDUCATION_OFFICER`.
- Total database users evaluated: All demo accounts and seed users.
- Users mapped to valid roles: Successfully resolve without fallback.
- Migration notes created in `PHASE_5E_ROLE_MIGRATION_NOTES.md`.

---

## 7. Demo Account Verification

Verified demo account: `ap17052005@gmail.com`
- **Department:** `Ministry of Education`
- **Designation:** `Teacher`
- **Resolved Role:** `EDUCATION_OFFICER` (`Education Officer`)
- **Resolution Path:** Exact mapping (`department="Ministry of Education"`, `designation="Teacher"`).
- **Fallback Dependency:** **None.** Resolves deterministically under the explicit rule set without relying on fallback logic.

---

## 8. Competency Pipeline Behavior

| Pipeline Stage | Resolved User | Unresolved User |
|---|---|---|
| **Role Requirements** | Active requirements from `role_requirements` for assigned `role_id`. | No requirements loaded. |
| **Competency Profiles** | Initialized/active profiles for required competencies. | Active profiles deactivated; no arbitrary requirements created. |
| **Skill Gap Calculation** | Computes gap between target level and current score. | Returns 422 ("Role mapping pending"). |
| **Supporting Evidence** | Recorded and preserved historically. | Recorded and preserved historically. |
| **Authoritative Evidence** | Recorded and updates active competency levels. | Recorded in immutable evidence log. |

---

## 9. Recommendation Behavior

- **Resolved User:** Generates personalized recommendations targeted at the user's active skill gaps derived from their authoritative role.
- **Unresolved User:** Does not guess or leak recommendations from `STATISTICAL_OFFICER` or other roles. Returns empty recommendation list with `"ROLE_MAPPING_PENDING"` status.

---

## 10. Role-Change Behavior

When an official updates their `department` or `designation` via `PUT /api/v1/users/me` or an Admin updates it via `POST /api/v1/admin/users/{user_id}/assign-role`:
1. `resolve_role_for_user()` is re-executed.
2. If mapped to a new role:
   - `reconcile_user_competencies(db, user_id, new_role_id)` deactivates obsolete role profiles and activates target profiles for the new role.
3. If unmapped:
   - User `role_id` is set to `None`.
   - Previous role profiles are marked `status: "inactive"`.

---

## 11. Historical Evidence Behavior

- **Immutability Invariant:** Assessment attempts, quiz results, and supporting learning activity records remain completely immutable in `competency_evidence`, `quiz_attempts`, and `learning_activities`.
- Changing roles or entering an unresolved state never deletes or mutates past scores, evidence timestamps, or assessment logs.

---

## 12. Files Changed

1. `backend/app/roles/resolver.py`
   - Removed silent fallback to `STATISTICAL_OFFICER` and first active role.
   - Updated `reconcile_user_competencies` to support `new_role_id=None` (deactivating profiles safely).
2. `backend/app/learning_resources/service.py`
   - Removed fallback that fetched 10 arbitrary competencies when user had no role.
3. `backend/app/users/router.py`
   - Updated profile update route to handle role unmapping cleanly when new dept/desig has no configured role.
4. `backend/app/admin/schemas.py`
   - Added `AdminAssignRoleRequest` schema.
5. `backend/app/admin/service.py`
   - Added `assign_user_role` service function.
   - Replaced fallback `"Statistical Officer"` in `list_users` with `"Unresolved"`.
6. `backend/app/admin/router.py`
   - Added `POST /api/v1/admin/users/{user_id}/assign-role` endpoint.
7. `backend/tests/test_department_competency_intelligence.py`
   - Updated `test_13_department_validation_rejects_invalid_names` to assert `resolve_role_for_user` returns `None` for unmapped inputs.
8. `backend/tests/test_role_resolution_integrity.py`
   - Comprehensive Phase 5E regression test suite covering all 16 required invariants.

---

## 13. Tests Added

Created `backend/tests/test_role_resolution_integrity.py` covering:
1. `test_01_exact_department_and_designation_resolves_correctly`
2. `test_02_unknown_department_and_designation_does_not_fall_back`
3. `test_03_unknown_designation_in_known_department_does_not_fall_back`
4. `test_04_unknown_department_with_known_designation_does_not_fall_back_if_no_global`
5. `test_05_case_and_whitespace_handling_follows_mapping_rules`
6. `test_06_unresolved_user_does_not_receive_other_role_requirements`
7. `test_07_unresolved_user_does_not_receive_other_role_recommendations`
8. `test_08_resolved_user_a_cannot_receive_user_b_role_requirements`
9. `test_09_department_or_designation_change_triggers_re_resolution`
10. `test_10_historical_evidence_remains_unchanged_after_role_change`
11. `test_11_admin_can_assign_role_and_rbac_protects_endpoint`

---

## 14. Full Test Results

```
================ 364 passed, 4 skipped, 87 warnings in 36.75s =================
```
- **Passed:** 364
- **Skipped:** 4 (Live LLM tests requiring external API keys)
- **Failed:** 0
- **Regressions:** 0

---

## 15. Frontend Check

```powershell
Push-Location frontend
npm run check
# Output: tsc --noEmit -> Exit Code 0 (Passed)
Pop-Location
```

---

## 16. Frontend Build

```powershell
Push-Location frontend
npm run build
# Output: vite build && esbuild -> built in 6.21s -> Exit Code 0 (Passed)
Pop-Location
```

---

## 17. Remaining Role-Mapping Limitations

1. **Mapping Coverage:** Currently, the system uses configured department/designation mappings present in the database `roles` collection. If an organization introduces novel designation titles not yet registered in `roles`, the user remains in `UNRESOLVED` status until an Admin either assigns the role or configures the role mapping.
2. **Explicit Governance:** Role mappings are not inferred through fuzzy or speculative matching, ensuring strict adherence to civil service competency frameworks.
