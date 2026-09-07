# PHASE 5C - ADMIN ANALYTICS AUDIT

## Scope

This audit traces the Admin dashboard analytics through `backend/app/admin/service.py`, its repository reads and response schemas, plus the Emerging Skills and Capacity Planning frontend consumers. The audit was completed before implementation changes for Phase 5C.

| Metric | Current Source | Real Data? | Calculation | Risk | Required Action |
|---|---|---|---|---|---|
| Workforce total and department/role counts | `users` collection via `get_all_users` | Yes | Counts returned users, optionally filtered by department | Low when the collection is available | Keep; expose source context where practical |
| Active users and access-role counts | `users` collection | Yes | Counts status/access-role values | Low | Keep |
| Average capability level | `competency_profiles` | Partly | Mean of `current_level`; falls back to `3.2` when empty | High: empty data appears measured | Return an explicit empty/insufficient state or a data-derived null representation |
| Critical gaps on Dashboard | `users`, `role_requirements`, `competency_profiles` | Derived from real data, with defaults | Compares current levels with required levels; missing profiles count as critical | Medium: missing-profile treatment needs to be explicit | Keep derivation and document its basis |
| Assessment coverage | `competency_profiles` and `users` | Yes | Distinct users with assessed profiles divided by users | Low | Keep |
| Learning hours | `learning_activities` | Yes | Sum of stored `duration_minutes` | Low | Keep; do not add fallback duration |
| Quiz score and activity metrics | `quiz_attempts`, `quizzes`, `learning_activities` | Partly | Stored aggregates, but empty data falls back to demo values such as `82.5`, `78.5`, `15`, `12`, `360`, `6.0`, and `8` | High: empty installations look populated | Remove fabricated empty-state values across Admin analytics |
| Domain capability breakdown | `competencies`, `competency_profiles` | Partly | Mean profile levels grouped by competency domain; empty state uses fixed CORE/DOMAIN/BEHAVIORAL values | High | Return only stored-data groups and show insufficient data in UI |
| Competency taxonomy count/domain breakdown | `competencies` | Yes | Counts catalog documents; current UI has fallback counts `42`, `12`, `18`, `12` | Medium | Remove frontend fallback numbers; use API data or an honest empty state |
| Competency required level | `role_requirements` | Partly | Mean required levels; defaults each missing requirement to `4.0` | Medium | Preserve only where the requirement is stored; distinguish missing requirements |
| Competency current level and average gap | `competency_profiles`, `role_requirements` | Partly | Means and non-negative difference; empty current level uses `2.5` | High | Do not display a measured average for unassessed competencies |
| Competency meeting percentage | `competency_profiles`, `role_requirements` | Partly | Assessed profiles meeting average required level; empty data uses `35.0` | High | Return zero/empty with explicit denominator, never `35.0` as measured |
| Skill-gap counts and priority | `users`, `role_requirements`, `competency_profiles`, `competencies` | Derived from real data, with a missing-role fallback | Compares each user to role requirements; users without roles use first three global requirements | High: fallback requirements can assign gaps to users outside a role | Use only role-mapped requirements; retain actual gap classifications |
| Skill-gap officials affected and distributions | Same as above | Derived from real data | Counts positive gaps by competency/domain/department | Medium | Keep; add provenance/denominator where practical |
| Training completion and evidence | `learning_activities`, `competency_evidence`, `capability_assessments` | Partly | Stored counts, but empty evidence/activity values use fabricated fallback counts/rates | High | Remove fallback counts and rates |
| Emerging strategic focus domains | Hardcoded list in service and frontend fallback | No | Fixed modernization domain labels | Medium: labels imply a data finding | Rename as prototype taxonomy/context or derive from observed competencies |
| Emerging urgency score | `competencies`, `role_requirements`, `competency_profiles` plus hardcoded defaults | No | `max(0.5, gap) * strategic multiplier * 2.0` | Critical: predictive-looking score is heuristic/fabricated | Replace with current-state gap metrics and no trend claim |
| Emerging demand index | `role_requirements`, profiles | No | `len(reqs) * 8 + int(gap * 10)` | Critical: arbitrary units and no historical demand data | Remove demand index or replace with observed counts |
| Emerging officials in deficit | Profiles plus formula | No | `max(3, len(cur_levels) + 2)` | Critical: manufactures official counts | Replace with actual positive-gap count based on user-role requirements |
| Emerging average gap | Profiles and requirements plus defaults | Partly | First requirement level, current mean, `max(0.5, ...)`, and default current level `2.4` | Critical: minimum/default makes empty data look deficient | Use actual matched profiles and requirements; omit when insufficient |
| Emerging rationale/focus | Hardcoded explanatory text | No | Text describes priority and cohort training for every competency | High: claims strategic priority without evidence | Use observed-gap wording and state data basis |
| Capacity competency selection | `competencies` | Yes, but incomplete | First eight catalog documents | Medium: arbitrary ordering limits coverage | Include competencies with observed gaps, or all relevant competencies |
| Capacity target officials | No stored planning field | No | Constant `12` per competency | Critical | Use actual officials with positive/high/critical gaps |
| Capacity estimated training hours | `learning_resources` only for resource matching; no duration calculation | No | Constant `24.0` per competency | Critical | Sum stored resource duration only; otherwise report unavailable |
| Capacity recommended course count | `learning_resources` | Partly | Matching resource count, but falls back to `2` | High | Return actual mapped resource count, including zero |
| Capacity top resource title/provider | `learning_resources` or fabricated fallback | Partly | First matched resource; otherwise `National Curriculum on {name}` and `iGOT Karmayogi` | Critical: invents a course and live-looking provider | Return no mapped resource; only show provider stored on a matched catalog resource |
| Capacity cohort size | No stored/configured planning field | No | Constant `6` | Critical | Return `Not configured`/nullable state |
| Capacity priority | Competency domain | Heuristic | `CRITICAL` for DOMAIN/TECHNOLOGY, otherwise `HIGH` | High: priority is not gap-derived | Derive priority from observed gap severity, or label as prototype rule |
| Capacity totals | Derived from capacity constants | No | Sums fabricated `12` and `24.0` values | Critical | Sum only actual gap counts and stored durations |
| Admin Reports workforce/gap/training summaries | Service methods above | Partly | Reuses dashboard, gap, and training responses | Inherits source risks | Correct upstream methods; keep valid summaries |
| Admin authorization | Admin router dependency/role guard | Yes | Admin endpoints are tested for ADMIN, OFFICIAL, TRAINER, and unauthenticated access | Low | Preserve unchanged and add regression coverage for changed endpoints |

## Data conclusions

- Stored competency profiles, role requirements, user records, learning activities, assessments, quizzes, evidence, and learning resources support current-state descriptive analytics.
- The repository does not provide sufficient time-series history for forecasting or trend claims in the inspected analytics path.
- Learning-resource matching uses `competency_code` or `competency_id`; a missing match is not evidence that an iGOT resource exists.
- iGOT is a curated/prototype adapter in this product, not a live government catalog. Provider text must therefore come from an actual stored resource record.

## Phase 5C implementation direction

1. Replace Emerging Skills scores with observed skill-gap signals: affected officials, average observed gap, required/current levels, and an explicit historical-data status.
2. Make officials affected count only users whose stored current level is below a stored role requirement.
3. Make Capacity Planning gap-driven and resource-aware; use only stored duration values and return unavailable/not-configured states for absent planning data.
4. Remove fabricated course/provider fallbacks and update the frontend labels and empty states.
5. Remove misleading frontend fallback numbers on the touched Admin views and add focused API regression tests while preserving Admin RBAC.