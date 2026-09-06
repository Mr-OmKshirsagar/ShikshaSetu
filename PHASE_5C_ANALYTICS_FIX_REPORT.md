# PHASE 5C - ADMIN ANALYTICS DATA-INTEGRITY FIX REPORT

## 1. Problems discovered

Admin analytics included predictive-looking values that were not supported by stored historical data. Emerging Skills used hardcoded gap floors, strategic multipliers, arbitrary demand points, and `max(3, ...)` for officials in deficit. Capacity Planning assigned every selected competency `12` target officials, `24` hours, and cohort size `6`, and invented an iGOT course/provider when no catalog resource matched.

Several shared Admin analytics also supplied demo values when collections were empty. Those values were removed so sparse datasets now return actual zero/empty states rather than appearing populated.

## 2. Metrics audited

The complete pre-change trace is in [PHASE_5C_ANALYTICS_AUDIT.md](PHASE_5C_ANALYTICS_AUDIT.md). It covers Workforce Overview, Competency Analytics, Skill Gap Analytics, Training Effectiveness, Emerging Skills, Capacity Planning, Admin Reports, Dashboard summaries, repository sources, and Admin RBAC.

## 3. Metrics that were genuinely data-driven

User/workforce counts, department and role distributions, stored competency profiles, role requirements, assessed gap classifications, learning activity duration, quiz/evidence counts, and catalog resource counts are based on MongoDB documents or direct derivations from them. These paths were retained, with role-less users no longer assigned arbitrary global requirements.

## 4. Heuristic/fabricated metrics removed

- Emerging urgency score and demand index.
- Synthetic officials-in-deficit count.
- Minimum/default current and gap values in Emerging Skills.
- Capacity target count, fixed duration, and fixed cohort size.
- Capacity fake course title and `iGOT Karmayogi` provider.
- Empty-state demo metrics across Admin dashboard, competency, workforce, training, and reports views.

## 5. Changes made

- Emerging Skills now counts only assessed officials below their stored role requirement.
- Emerging Skills reports observed average current level, required level, and gap, plus `historical_trend_available: false` and a data-basis message.
- Capacity Planning uses assessed role-mapped gaps and derives priority from observed gap severity.
- Training hours are calculated only from stored learning-resource `metadata.duration_hours`; otherwise the API returns `null` and the UI says `Duration data unavailable`.
- Cohort size is nullable and displays `Not configured` when no value is stored.
- Resource title/provider are returned only from a matched catalog resource; missing mappings display `No mapped learning resource available` and `No mapped resource`.
- Admin screens now use current-state labels such as `Skill Gap Signals`, `Observed Competency Gaps`, and `Officials With Observed Gaps`.
- Added provenance text to Emerging Skills and Capacity Planning.

## 6. Emerging Skills before/after

Before: heuristic urgency and demand formulas, default levels, and fabricated deficit counts implied strategic prediction.

After: observed positive gaps are grouped by competency using actual user profiles and role requirements. No trend is claimed because the inspected data path has no sufficient time-series history.

## 7. Capacity Planning before/after

Before: first eight competencies received fixed `12` personnel, `24` hours, and cohort size `6` regardless of data.

After: only competencies with observed assessed gaps become interventions. Personnel counts are distinct affected officials. Duration is based on mapped catalog metadata or unavailable, and cohort size is not configured unless stored.

## 8. Fabricated resource fallback before/after

Before: missing mappings produced `National Curriculum on {competency}` and `iGOT Karmayogi`.

After: missing mappings return null resource fields and the UI displays `No mapped learning resource available`. iGOT provider text is shown only when present on an actual matched catalog resource.

## 9. Data provenance improvements

The Emerging Skills response states that it is based on assessed competency profiles and stored role requirements and that historical trend is unavailable. Capacity Planning states that it is based on assessed officials below stored requirements and mapped catalog resources. UI labels explain unavailable duration and unconfigured cohort data.

## 10. Tests added

Added API regression tests covering observed gap counts, removal of urgency/demand fields, no trend claim, sparse-state behavior, actual target officials, missing duration, missing cohort configuration, zero mapped resources, and no fabricated resource/provider.

Existing Admin endpoint authorization tests continue to cover ADMIN access and OFFICIAL/TRAINER/unauthenticated rejection for all Admin endpoints.

## 11. Test results

- `python -m pytest backend/tests/test_admin.py -q`: **39 passed**.
- `python -m pytest backend/tests/test_department_competency_intelligence.py -q`: **17 passed**.
- Full `python -m pytest backend/tests -q`: **blocked during collection** because `mongomock` is not installed in the active `.venv`; failure is `ModuleNotFoundError: No module named 'mongomock'` in `test_evidence_governance.py`.
- Changed-file diagnostics and Python compilation: **passed**.

## 12. Frontend check result

From `frontend/`, `npm run check`: **passed**.

## 13. Frontend build result

From `frontend/`, `npm run build`: **passed**. Vite transformed 1904 modules and the server bundle completed successfully.

## 14. Remaining analytics limitations

- Historical forecasting is intentionally unavailable until timestamped competency observations provide sufficient time-series evidence.
- Missing competency profiles are not counted as assessed gaps; they represent an unassessed population and should not be treated as a measured deficit.
- Training-hour totals are unavailable when mapped resources lack stored duration metadata.
- Cohort sizing remains unconfigured because no authoritative cohort-size setting exists.
- Other non-Admin product areas and unrelated pre-existing security/configuration changes were not modified.

No commit was created.