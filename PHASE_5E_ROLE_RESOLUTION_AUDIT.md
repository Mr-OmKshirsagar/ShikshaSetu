# PHASE 5E — ROLE RESOLUTION INTEGRITY AUDIT

**Date:** 2026-09-06  
**Auditor:** Antigravity (Google DeepMind)  
**System:** ShikshaSetu Role Mapping & Competency Engine

---

## 1. Executive Summary

This audit assesses the role resolution pipeline across user registration, profile updates, competency listing, skill gap computation, learning recommendations, and admin governance.

The primary objective is eliminating silent default fallbacks (e.g. defaulting to `STATISTICAL_OFFICER` or the first active role in the database) when a user's Department + Designation cannot be deterministically resolved to a configured civil service role.

---

## 2. Role Resolution Audit Matrix

| Input (Department + Designation) | Resolution Method | Pre-Remediation Fallback | Risk / Failure Mode | Correct Invariant Behavior |
| :--- | :--- | :--- | :--- | :--- |
| **Known Dept + Exact Designation** (e.g., MoE + Teacher) | Step 1: Matching department + designation in role taxonomy | None (Exact match) | None | Resolves to `EDUCATION_OFFICER`. |
| **Known Dept + Case/Whitespace Variant** (e.g., "  ministry of education " + "teacher") | Normalized string matching within department | None (Normalized match) | None | Resolves to `EDUCATION_OFFICER`. |
| **Unknown Designation in Known Dept** (e.g., MoE + "Aviation Pilot") | Step 3: Dept-only match | Assigned first role in department (`EDUCATION_OFFICER`) | **High:** Official assigned curriculum competency requirements despite unrelated function. | **UNRESOLVED (`None`)**: No role assigned; pending Admin review. |
| **Unknown Dept + Known Designation** (e.g., "Dept of Unknowns" + "Statistical Officer") | Step 2: Global designation match across all roles | None (Designation match) | Low (Designation matches canonical role) | Resolves to `STATISTICAL_OFFICER` if unique designation match exists. |
| **Unknown Dept + Unknown Designation** (e.g., "Custom Dept" + "Special Consultant") | Step 4 & 5: Default role fallback | Silently assigned `STATISTICAL_OFFICER` or `roles[0]` | **Critical:** Completely arbitrary competency requirements, false skill gaps, and irrelevant training recommendations. | **UNRESOLVED (`None`)**: Returns `None`. Role mapping pending. |
| **Empty / Missing Dept & Designation** | Step 5: Fallback to first role | Silently assigned `roles[0]` | **Critical:** Defaulted to arbitrary role. | **UNRESOLVED (`None`)**: Returns `None`. |
| **Recommendations for Unresolved User** | `RecommendationService:get_recommendations_for_user` | Fell back to 10 arbitrary competencies from catalog | **High:** Showed generic recommendations claiming they were personalized gaps. | Returns empty recommendations with status `ROLE_MAPPING_PENDING`. |
| **Skill Gaps for Unresolved User** | `SkillGapService:calculate_skill_gaps` | If role missing, attempted fallback resolution | Failed safely with 422 if unresolvable, but fallback masked unknown roles. | Returns 422 `Role mapping pending`. |
| **Admin User Directory** | `AdminService:get_admin_users` | Defaulted `prof_role` to `"Statistical Officer"` | **Medium:** Displayed misleading role in admin directory. | Displays `"Unresolved"` or `"Pending Role Mapping"`. |

---

## 3. Subsystem Consumers of Role Resolution

1. **`app/auth/router.py`**:
   - Registration and Login resolve user role based on payload department/designation.
   - Unresolved users must retain `role_id: None` without silent default assignment.
2. **`app/users/router.py`**:
   - Profile update on department/designation triggers re-resolution. If unmapped, deactivates previous active role requirements without destroying historical assessment evidence.
3. **`app/competencies/service.py`**:
   - `list_user_competencies` requires an active resolved role. For unresolved users, returns empty list or pending status.
4. **`app/skill_gaps/service.py`**:
   - `calculate_skill_gaps` calculates gaps exclusively from the resolved role's requirements. Unresolved users receive HTTP 422 `Role mapping pending`.
5. **`app/learning_resources/service.py`**:
   - Recommendations are strictly generated from active skill gaps. Unresolved users receive 0 recommendations with metadata `ROLE_MAPPING_PENDING`.
6. **`app/admin/`**:
   - Admin directory displays `"Unresolved"` for unmapped officials.
   - Protected endpoint `POST /api/v1/admin/users/{user_id}/assign-role` allows administrators to formally assign a configured role.

---

## 4. Historical Assessment & Evidence Invariant

- **Role Drift Safety:** When an official transitions between departments or designations (e.g. from Education to Statistics), previous competency profiles are deactivated, but **all historical evidence in `competency_evidence` and past assessment attempts remain completely immutable**.
