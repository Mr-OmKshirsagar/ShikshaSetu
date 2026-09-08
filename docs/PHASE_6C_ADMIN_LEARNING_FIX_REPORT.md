# Phase 6C — Admin Workforce Learning & Progress: Implementation Report

**Date:** August 2026  
**Status:** Complete  
**Tests:** 15/15 new tests passing · 393 total passing · 0 regressions  
**Build:** `npm run check` — 0 errors · `npm run build` — success (10.90s)

---

## 1. Executive Summary

Phase 6C adds an **Individual Workforce Profile (User 360)** to the Admin Users page. An administrator can now click any user in the directory and open a slide-in panel showing that user's full capability-development journey: identity, current authoritative capability, active skill gaps, all learning activities with explicit progress, formal assessment history, and an evidence ledger clearly separating supporting from authoritative records — along with a chronological timeline of learning and assessment events.

The feature is read-only for Admin. No mutation powers were added. All data is scoped server-side to the target user. RBAC is enforced at the router level (existing `require_admin_role` dependency), so OFFICIAL and TRAINER callers receive 403 automatically.

---

## 2. Existing Learning Data Model (as audited)

### `learning_activities` collection
| Field | Type | Semantics |
|-------|------|-----------|
| `user_id` | ObjectId | Owning user |
| `resource_id` | string | Learning resource identifier |
| `competency_id` | string | Competency addressed |
| `status` | enum | `not_started` / `in_progress` / `completed` / `abandoned` |
| `progress_percent` | float 0–100 | **Explicitly stored on PUT call** — not derived |
| `duration_minutes` | float | Total time spent |
| `started_at` | datetime | Created/started |
| `completed_at` | datetime \| null | Set on complete call |
| `last_accessed_at` | datetime | Updated on every interaction |

**Progress semantics:** `progress_percent` is stored by the learner or system via `PUT /learning-activities/{id}`. It is not derived from any proxy metric. The frontend labels this "Learning Progress" — never "Competency Progress". These two concepts are kept strictly separate.

### `competency_profiles` collection
Stores authoritative current competency levels (`current_level` 1–5). Updated exclusively by assessment/quiz evidence. Learning completion does not update this collection.

### `competency_evidence` collection
- `type: LEARNING_ACTIVITY` → **supporting evidence**, confidence 0.30
- `type: CAPABILITY_ASSESSMENT` → **authoritative evidence**, confidence 0.85

Evidence is append-only. Admin can view it but cannot edit or delete through this feature.

### `capability_assessments` collection
Formal capability assessment records. Only `status: SUBMITTED` assessments are marked as `authoritative: true` in the response.

---

## 3. Gap in Previous Admin Experience

The `AdminUsers.tsx` page rendered a workforce directory table with no interactivity. Clicking a user row did nothing. There was no drill-down, no individual capability view, no learning progress visibility, and no evidence ledger access for any specific user.

Administrators had org-level aggregates (dashboard, workforce overview, skill gap analytics) but no way to answer: *"How is this specific official progressing through their capability-development journey?"*

---

## 4. New Functionality

### Admin can now:
- Click any user row in the Users directory → opens Individual Workforce Profile panel
- Keyboard navigate (Enter/Space on rows, Escape to close)
- View 6 tabbed sections for a complete User 360 view
- Refresh the profile data without leaving the panel

### Admin cannot (by design):
- Edit evidence records
- Alter competency levels
- Modify learning progress
- Change assessment scores
- Any write operation — the panel is strictly read-only

---

## 5. API Endpoint

### `GET /api/v1/admin/users/{user_id}/profile`

**Access control:** `require_admin_role` (inherited from router-level dependency)  
**Method:** GET — read-only  
**Path parameter:** `user_id` — resolved server-side from MongoDB  

**Response:** `AdminWorkforceProfileResponse`

```json
{
  "user": { "id", "full_name", "email", "employee_id", "department",
            "designation", "professional_role", "access_role", "status",
            "created_at", "last_login_at" },
  "capabilities": [{ "competency_code", "competency_name", "domain",
                     "current_level", "required_level", "gap", "gap_category" }],
  "active_gaps": [ ...same shape, filtered to gap > 0, sorted by priority... ],
  "learning_summary": {
    "total_activities", "completed", "in_progress", "not_started", "abandoned",
    "total_learning_hours", "overall_learning_progress_pct",
    "progress_note"
  },
  "learning_activities": [{ "activity_id", "resource_id", "resource_title",
                            "provider", "competency_id", "status",
                            "progress_percent", "started_at", "last_accessed_at",
                            "completed_at", "duration_minutes" }],
  "assessments": [{ "assessment_id", "assessment_type", "competency_code",
                    "status", "score", "percentage", "assessed_at",
                    "authoritative" }],
  "evidence_summary": { "supporting_count", "supporting_confidence",
                        "authoritative_count", "authoritative_confidence",
                        "total_records", "governance_note" },
  "evidence": [{ "evidence_id", "evidence_type", "competency_code",
                 "confidence", "source", "recorded_at" }],
  "timeline": [{ "timestamp", "event_type", "title", "detail", "icon" }]
}
```

**HTTP status codes:**
- `200` — profile returned
- `401` — no/invalid token
- `403` — caller is not ADMIN
- `404` — `user_id` not found

---

## 6. Learning Progress Calculation

```
overall_learning_progress_pct =
    sum(activity.progress_percent for activity in user_activities)
    ÷ count(user_activities)
```

- Calculated **only** when `total_activities > 0`
- Returns `null` when no activities exist — never fabricated
- Labeled **"Learning Progress"** throughout — not "Competency Progress"
- Note included in every response: *"Learning progress reflects learner-reported engagement. Competency updates require formal assessment evidence."*

---

## 7. Skill Gap Integration

Active gaps are derived from:
1. User's role requirements (`role_requirements` collection, filtered by `role_id`)
2. User's authoritative competency profiles (`competency_profiles`)
3. `gap = max(0, required_level − current_level)`
4. Categories: `CRITICAL` (≥2.0) · `HIGH` (≥1.0) · `MEDIUM` (>0.0) · `MET` (0)

Gaps are sorted highest-priority first. Only the selected user's role requirements and profiles are used — no cross-user data leakage.

---

## 8. Assessment Integration

Only `capability_assessments` records are surfaced in the assessments tab. Practice quiz results (`quiz_attempts`) are not included. Assessments with `status: SUBMITTED` are flagged `authoritative: true`. In-progress assessments are shown with `authoritative: false` and an "In Progress" badge.

---

## 9. Evidence Integration

Evidence records are fetched from `competency_evidence` scoped to the target user. Two evidence types are distinguished:

| Evidence Type | Confidence | Competency Impact | Source |
|---------------|------------|-------------------|--------|
| `LEARNING_ACTIVITY` | 0.30 | None — supporting only | Learning completion |
| `CAPABILITY_ASSESSMENT` / `ADAPTIVE_ASSESSMENT` | 0.85 | Updates competency profile | Formal assessment |

The governance note in every response explicitly states that supporting evidence does not update the competency profile.

---

## 10. Timeline Construction

Timeline events are assembled from two sources (chronological ascending):
1. **Learning activities** — `started_at` event + `completed_at` event (if present, also adds supporting evidence event)
2. **Capability assessments** — `started_at` event + `submitted_at` event (if present, also adds authoritative evidence event)

Only events with real timestamps are included. No fabricated events.

---

## 11. RBAC Verification

| Caller | Expected | Actual (tested) |
|--------|----------|-----------------|
| ADMIN token | 200 | ✅ 200 |
| OFFICIAL token | 403 | ✅ 403 |
| TRAINER token | 403 | ✅ 403 |
| No token | 401 | ✅ 401 |

The `require_admin_role` dependency on the admin router covers all routes including the new endpoint. No additional RBAC code was required.

---

## 12. Data Isolation Verification

- All queries use `user_id`-scoped repository functions (not full-collection scans)
- `get_user_learning_activities(db, user_id)` — filters by `user_id` in MongoDB query
- `get_user_capability_assessments(db, user_id)` — same
- `get_user_evidence_records(db, user_id)` — same
- `get_user_competency_profiles(db, user_id)` — same
- Test 7 (`test_other_user_activities_not_mixed`) explicitly verifies this: `res-other-only` activity from another user does not appear in official's profile
- Test 15 (`test_skill_gaps_match_selected_user_role`) verifies gap values and categories are derived from the correct user's profile

---

## 13. Performance Approach

- No N+1 queries: all data for a single user is fetched in one pass per collection (4 targeted queries)
- Learning resources fetched once and indexed by `resource_id` for O(1) title enrichment
- Results bounded: `limit=200` for activities, `limit=50` for assessments, `limit=100` for evidence
- Large lists (learning activities) are returned as-is; pagination can be added if needed
- `skipCache: true` on `api.admin.userProfile()` so refreshed data is always current
- User directory (`GET /admin/users`) remains lightweight — individual profile details are only fetched on click

---

## 14. Files Changed

### Backend (3 files)

| File | Change |
|------|--------|
| `backend/app/admin/repository.py` | Added 4 user-scoped query functions: `get_user_by_id`, `get_user_learning_activities`, `get_user_capability_assessments`, `get_user_evidence_records`, `get_user_competency_profiles` |
| `backend/app/admin/service.py` | Added `get_user_workforce_profile(db, user_id)` — assembles full profile from 4 targeted queries |
| `backend/app/admin/router.py` | Added `GET /admin/users/{user_id}/profile` endpoint |

### Frontend (4 files)

| File | Change |
|------|--------|
| `frontend/client/src/lib/api.ts` | Added `AdminWorkforceProfileResponse` type + `api.admin.userProfile(userId)` method |
| `frontend/client/src/pages/admin/AdminUserProfile.tsx` | New: panel shell with tab bar, loading/error states, identity header |
| `frontend/client/src/pages/admin/AdminUserProfileTabs.tsx` | New: 6 tab components (Overview, Learning, Skill Gaps, Assessments, Evidence, Timeline) + shared types |
| `frontend/client/src/pages/admin/AdminUsers.tsx` | Updated: added click/keyboard handler on rows, renders `AdminUserProfile` panel |

### Tests (1 file)

| File | Change |
|------|--------|
| `backend/tests/test_admin_user_profile.py` | New: 15 test cases |

### Documentation (2 files)

| File |
|------|
| `PHASE_6C_ADMIN_LEARNING_AUDIT.md` |
| `PHASE_6C_ADMIN_LEARNING_FIX_REPORT.md` (this file) |

---

## 15. Tests Added

| # | Test | Result |
|---|------|--------|
| 1 | Admin can retrieve a user's workforce profile | ✅ |
| 2 | Official cannot retrieve profile — 403 | ✅ |
| 3 | Trainer cannot retrieve profile — 403 | ✅ |
| 4 | Unauthenticated request returns 401 | ✅ |
| 5 | Non-existent user_id returns 404 | ✅ |
| 6 | Correct user's learning activities returned | ✅ |
| 7 | Another user's activities not mixed in | ✅ |
| 8 | Completed activity shows status "completed" | ✅ |
| 9 | In-progress activity shows stored progress_percent | ✅ |
| 10 | Not-started activity represented correctly | ✅ |
| 11 | No learning activity → empty list + null progress | ✅ |
| 12 | Supporting vs authoritative evidence distinguished | ✅ |
| 13 | Quiz results not presented as authoritative capability | ✅ |
| 14 | Evidence records unchanged after profile fetch | ✅ |
| 15 | Skill gaps match selected user's role, not another's | ✅ |

---

## 16. Test Suite Results

| Metric | Before | After |
|--------|--------|-------|
| Passing | 378 | 393 (+15) |
| Failing | 4 | 4 (unchanged, pre-existing) |
| Skipped | 4 | 4 (unchanged) |
| Errors | 2 | 2 (unchanged, MongoDB network teardown) |
| Regressions | — | 0 |

Pre-existing failures (`test_config_security.py` × 4) are environment-specific config validation tests unrelated to this feature. Pre-existing errors (`test_learning_resources.py` × 2) are transient MongoDB Atlas connection resets during test teardown, also unrelated.

---

## 17. Frontend Build Results

```
npm run check    →  0 TypeScript errors
npm run build    →  ✓ built in 10.90s
AdminUsers bundle: 31.52 kB (gzip: 7.65 kB)
```

One TypeScript fix applied: `useRef<HTMLButtonElement | null>` (React 19 requires nullable ref type).

---

## 18. Known Limitations

| Limitation | Impact | Mitigation |
|------------|--------|------------|
| Resource titles — if `resource_id` not in `learning_resources`, raw ID shown | Low — most resources have titles | Fallback label used |
| No historical capability trend | Cannot show before/after gap closure | Shown only when multiple evidence records exist for same competency |
| No real-time push — data reflects state at load time | Low — Refresh button provided | Future: WebSocket or polling |
| No pagination on large activity lists | Could be slow for users with 200+ activities | Bounded at 200 activities; pagination can be added |
| `duration_minutes` accuracy depends on learner updating it | May under-report learning hours | Clearly labeled "recorded" |

---

## 19. SIH Demo Recommendation

This feature directly supports the demo narrative:

> *"From an organizational perspective, we can move from simply knowing who our employees are to understanding how they are progressing through their capability-development journey."*

**Recommended demo flow:**

1. Log in as Admin
2. Open **Users** page — show the workforce directory
3. Click any user (e.g., "Abhishek Pathak")
4. Panel opens — point to the **identity header** (role, department, designation)
5. **Overview tab** — show capability level, active gaps, learning summary, evidence counts
6. **Learning tab** — show activity list with explicit stored progress bars; point to the note: *"This is not competency progress"*
7. **Skill Gaps tab** — show current vs required vs gap for each competency
8. **Assessments tab** — show formal capability assessments with authoritative badge
9. **Evidence tab** — show supporting (0.30) vs authoritative (0.85) records, governance note
10. **Timeline tab** — show chronological learning → evidence → assessment → competency update sequence

**Closing line:**
> *"This lets administrators monitor whether identified workforce gaps are actually being addressed through learning and formal assessment — while maintaining the integrity of the authoritative competency evidence."*

---

*Phase 6C complete. No commits made. Awaiting review.*
