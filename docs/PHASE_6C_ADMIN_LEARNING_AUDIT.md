# Phase 6C — Admin Workforce Learning & Progress: Pre-Implementation Audit

**Date:** August 2026  
**Type:** Read-only audit — no code changed during this document  
**Scope:** Admin individual user learning/progress observability feature

---

## 1. Objective

Enable Admin to click any user in the Users/Workforce directory and open a full **Individual Workforce Profile (User 360)** showing:

- Who the user is (identity, role, department)
- Current authoritative capability
- Active skill gaps
- Learning activities (all statuses)
- Learning progress (stored explicitly, not derived)
- Assessment history (baseline + capability)
- Evidence summary (supporting vs authoritative)
- Chronological timeline of learning events

---

## 2. Existing Learning Data Model

### Collection: `learning_activities`

| Field | Type | Semantics |
|-------|------|-----------|
| `_id` | ObjectId | Activity identifier |
| `user_id` | ObjectId | Owning user |
| `resource_id` | string | Learning resource identifier |
| `competency_id` | string | Competency this resource addresses |
| `status` | enum | `not_started` / `in_progress` / `completed` / `abandoned` |
| `progress_percent` | float 0–100 | **Explicitly stored on update** — not derived |
| `duration_minutes` | float | Total time spent learning |
| `started_at` | datetime | When activity was created/started |
| `completed_at` | datetime \| null | Set on completion call |
| `last_accessed_at` | datetime | Updated on every update/complete call |
| `notes` | string \| null | Optional learner notes |

**Progress semantics:**  
`progress_percent` is explicitly recorded via `PUT /learning-activities/{id}` → `service.update_learning_activity()`.  
It is **not calculated** from pages viewed, time spent, or any other proxy.  
If not updated by the learner, it stays at 0 even if the status is `in_progress`.

**Do NOT label `progress_percent` as "Competency Progress".**  
It is "Learning Progress" — a learner-reported or system-updated engagement metric.

### Collection: `competency_profiles`

| Field | Type | Semantics |
|-------|------|-----------|
| `user_id` | ObjectId | Owning user |
| `competency_id` | ObjectId/string | Competency |
| `current_level` | float 1–5 | **Authoritative** level — updated only by assessment/quiz evidence |

### Collection: `capability_assessments`

| Field | Type | Semantics |
|-------|------|-----------|
| `user_id` | string/ObjectId | |
| `competency_code` | string | |
| `status` | string | `IN_PROGRESS` / `SUBMITTED` |
| `score` | float \| null | Raw score |
| `percentage` | float \| null | 0–100 |
| `started_at` | datetime | |
| `submitted_at` | datetime \| null | |

### Collection: `competency_evidence`

| Field | Type | Semantics |
|-------|------|-----------|
| `user_id` | ObjectId | |
| `competency_id` | string | |
| `type` | string | `LEARNING_ACTIVITY` = supporting (0.3) / `CAPABILITY_ASSESSMENT` = authoritative (0.85) |
| `confidence` | float | 0.3 for learning, 0.85 for capability assessment |
| `score` | float | |
| `recorded_at` | datetime | Append-only |
| `source` | dict | `{activity_id, resource_id}` or `{assessment_id}` |

**Evidence is append-only.** Admin can view but MUST NOT be able to edit or delete evidence through this feature.

### Collection: `role_requirements`

| Field | Semantics |
|-------|-----------|
| `role_id` | Professional role |
| `competency_id` | Required competency |
| `required_level` | Expected level (1–5) |

---

## 3. Existing Admin Backend

### admin/schemas.py — Already Defined (no changes needed)

The following schemas are **already present** in `admin/schemas.py`:

| Schema | Status |
|--------|--------|
| `AdminWorkforceProfileResponse` | ✅ Defined |
| `AdminUserItem` | ✅ Defined |
| `AdminCapabilityItem` | ✅ Defined |
| `AdminLearningActivityItem` | ✅ Defined |
| `AdminAssessmentItem` | ✅ Defined |
| `AdminEvidenceItem` | ✅ Defined |

### admin/router.py — Gap

**Missing:** `GET /admin/users/{user_id}/profile` endpoint.  
All existing endpoints are protected by `require_admin_role` router-level dependency.  
The new endpoint will inherit this protection automatically.

### admin/service.py — Gap

**Missing:** `get_user_workforce_profile(db, user_id)` function.  
All data sources are already accessible via existing `repository.*` functions.

### admin/repository.py — Sufficient

Existing functions cover all needed queries:
- `get_all_users(db)` — for user lookup
- `get_all_roles(db)` — for professional role name resolution
- `get_all_competencies(db)` — for competency name/domain lookup
- `get_all_role_requirements(db)` — for required level per competency
- `get_all_competency_profiles(db)` — for current capability level
- `get_all_learning_activities(db)` — for learning activity history
- `get_all_capability_assessments(db)` — for assessment history
- `get_all_evidence_records(db)` — for evidence ledger
- `get_all_learning_resources(db)` — for resource title/provider enrichment

**Performance approach:** All queries will be scoped to the specific `user_id` at the repository layer to avoid full-collection scans. New targeted repository functions will be added for user-scoped queries.

---

## 4. Existing Frontend

### AdminUsers.tsx — Current State

- Fetches and renders workforce directory table ✅
- Displays: name, email, department, professional role, access role, status, registered date ✅
- Has search + role filter ✅
- **No click handler on rows** — no drill-down possible ❌
- No detail view exists anywhere in Admin pages ❌

### Shared Components Available

- Existing Admin card/panel pattern (white rounded cards, purple/violet accent)
- No existing drawer or modal component observed in Admin pages
- Will implement as a **slide-in panel** (right side, fixed, with backdrop) to match admin UX patterns

---

## 5. RBAC Boundary

| Role | Can access `/admin/users/{id}/profile` |
|------|----------------------------------------|
| ADMIN | ✅ YES — inherits router-level `require_admin_role` |
| TRAINER | ❌ NO — 403 |
| OFFICIAL | ❌ NO — 403 |
| Unauthenticated | ❌ NO — 401 |

The endpoint resolves the target user server-side from the URL parameter.  
Admin cannot access user data from a different tenant (single-tenant architecture).  
Admin does NOT gain mutation power through this endpoint — it is GET-only.

---

## 6. Learning Progress Calculation

**Formula used:**

```
overall_learning_progress =
  (sum of progress_percent across all activities) / (count of all activities)
```

Only used when `total_activities > 0`. Returns `null` / "No data" when count is 0.

**This is "Learning Progress" — NOT "Competency Progress".**  
These are kept strictly separate in both backend response and frontend labels.

---

## 7. Evidence Distinction

| Evidence Type | Source | Confidence | Competency Impact |
|---------------|--------|------------|-------------------|
| SUPPORTING | Learning activity completion | 0.30 | **No direct competency update** |
| AUTHORITATIVE | Formal capability assessment | 0.85 | **Updates competency profile** |

The frontend must display this distinction visually and with explicit labels.  
Admin must never see quiz/learning percentages presented as authoritative capability.

---

## 8. Timeline Construction

Timeline events are assembled from four sources (sorted chronologically):

1. Learning activity `started_at` → "Learning started"
2. Learning activity `completed_at` → "Learning completed" + "Supporting evidence recorded"
3. Capability assessment `started_at` → "Formal assessment started"
4. Capability assessment `submitted_at` → "Assessment submitted" + "Capability updated" (if score present)

Only events with real timestamps are included. No fabricated events.

---

## 9. What Will Be Built

### Backend (minimum required changes)

1. **`admin/repository.py`** — Add 4 user-scoped query functions:
   - `get_user_learning_activities(db, user_id)` — scoped to one user
   - `get_user_capability_assessments(db, user_id)` — scoped to one user
   - `get_user_evidence_records(db, user_id)` — scoped to one user
   - `get_user_competency_profiles(db, user_id)` — scoped to one user

2. **`admin/service.py`** — Add `get_user_workforce_profile(db, user_id)` function

3. **`admin/router.py`** — Add `GET /admin/users/{user_id}/profile` endpoint

### Frontend (minimum required changes)

4. **`pages/admin/AdminUserProfile.tsx`** — New component: User 360 slide-in panel

5. **`pages/admin/AdminUsers.tsx`** — Add click handler on rows + panel state management

6. **`lib/api.ts`** — Add `api.admin.userProfile(userId)` method + `AdminWorkforceProfileResponse` type

### Tests

7. **`tests/test_admin_user_profile.py`** — 15 test cases (new file)

---

## 10. What Will NOT Change

| Item | Reason |
|------|--------|
| Competency scoring formula | Not touched |
| Evidence governance (append-only) | Not touched |
| Recommendation scoring | Not touched |
| Assessment architecture | Not touched |
| Existing admin endpoints | Not touched |
| Other admin frontend pages | Not touched |
| Learning activities endpoint | Not touched |
| RBAC dependencies | Not touched (inherits existing) |

---

## 11. Limitations

- **No learning resource titles** — if a resource_id is not in `learning_resources`, the resource_id itself is displayed as a fallback
- **No historical capability** — before/after gap closure only shown if multiple evidence records exist for same competency
- **No real-time updates** — data reflects state at page load; "Refresh" button provided
- **No predictive analytics** — all data is observed, not forecasted
- **Learning hours** — only accurate if `duration_minutes` is updated by the learner; not estimated from content length

---

*Audit complete. No code was modified during this audit.*
