# PHASE 5G — RECOMMENDATION INTEGRITY & EXPLAINABILITY REPORT

## Executive Summary
Phase 5G establishes end-to-end integrity, explainability, role isolation, multi-gap deduplication, and cache invalidation for the ShikshaSetu Personalized Recommendation Engine. Personalized recommendations are strictly grounded in the official chain:
$$\text{User} \rightarrow \text{Resolved Professional Role} \rightarrow \text{Active Role Requirements} \rightarrow \text{Authoritative Competency Profile} \rightarrow \text{Active Skill Deficit} \rightarrow \text{Explicit Resource-Competency Mapping} \rightarrow \text{Personalized Ranked Recommendations}$$

---

## 1. Recommendation Pipeline Before
- The recommendation service fetched competency gaps from `calculate_skill_gaps` but did not filter out non-deficit items (items where $\text{gap} \le 0.0$ or $\text{gap\_category} = \text{"NO\_GAP"}$).
- Candidates were scored and returned even if the user met or exceeded role competency requirements.
- Multiple mappings for a single resource across different competencies produced either redundant candidate processing or omitted multi-gap context.
- "Why Recommended" explainability was limited to basic string summaries without structured priority, current/required level values, or honest provider provenance metadata.
- Cache invalidation was not explicitly called upon formal capability assessment or initial assessment completion.

---

## 2. Recommendation Pipeline After
1. **User Role Resolution**: Validates that the user has a resolved professional role via `role_id` or explicit `(department, designation)` mapping. Unresolved users receive `ROLE_MAPPING_PENDING` with 0 recommendations.
2. **Active Gap Filtering**: Queries `calculate_skill_gaps` and strictly filters for **active skill gaps** ($\text{gap} > 0.0$ and $\text{gap\_category} \ne \text{"NO\_GAP"}$).
3. **No-Gap Honesty**: If all competencies meet or exceed required levels, immediately returns $0$ recommendations with honest message: `"All mapped competencies are currently at or above required levels for your role."`
4. **Candidate Generation**: Queries providers (`IGOT`, `NSSTA`) for learning resources explicitly mapped in `learning_resource_mappings` to active gap competency codes.
5. **Multi-Gap Aggregation & Deduplication**: If a resource addresses multiple active gaps, it is unified into a single recommendation card preserving highest-priority scoring while embedding `addressed_gaps_count` and `addressed_competency_codes`.
6. **Deterministic 5-Factor Scoring**: Evaluates candidates against preserved weights ($40\%$ competency match, $25\%$ gap priority, $20\%$ role match, $10\%$ difficulty appropriateness, $5\%$ prerequisite fulfillment).
7. **Deterministic Explainability**: Generates grounded `"Why Recommended"` explanations referencing exact competency name, current level, required level, gap size, priority, and provider provenance.
8. **User-Isolated Caching & Event Invalidation**: Caches responses per `user_id` and limit with automatic invalidation upon assessment completion and role changes.

---

## 3. Candidate Eligibility Rules
A resource is eligible for personalized recommendation **ONLY** when ALL of the following criteria are met:
1. User has an **explicitly resolved professional role**.
2. User has an **active competency gap** ($\text{gap} > 0.0$).
3. Resource is **explicitly mapped** to that competency in `learning_resource_mappings`.
4. Resource is in **ACTIVE** status (`status == "ACTIVE"`).
5. Resource has **valid verification status** (`VERIFIED` or official calendar `TENTATIVE`).

---

## 4. Role Isolation
- Recommendation generation derives solely from the authenticated user's resolved role requirements.
- Global competency lists, first active roles, or arbitrary default fallbacks (e.g. Statistical Officer) are strictly prohibited.
- User A's recommendations and competency profiles never leak into User B's recommendation feed.

---

## 5. Resource Mapping Behavior
- Candidate generation strictly queries the `learning_resource_mappings` collection using explicit database relationships (`resource_id`, `competency_id`, `competency_code`, `provider`).
- Heuristic keyword guessing, title matching, and description scraping are prohibited.

---

## 6. Unmapped Resource Behavior
- Unmapped resources remain in the catalogue with `status="ACTIVE"` and are browseable via `/api/v1/recommendations/resources/unmapped` or catalogue browsing.
- Unmapped resources are **never** included in personalized recommendation feeds.

---

## 7. Scoring Formula Actually Used
The deterministic 5-component scoring model is strictly preserved without arbitrary modifications:
$$\text{Total Score} = 0.40 \cdot S_{\text{comp\_match}} + 0.25 \cdot S_{\text{gap\_prio}} + 0.20 \cdot S_{\text{role\_match}} + 0.10 \cdot S_{\text{diff\_match}} + 0.05 \cdot S_{\text{prereq\_match}}$$

- **Competency Match ($40\%$)**: Mapping confidence score $[0.0, 1.0]$.
- **Gap Priority ($25\%$)**: Normalized gap priority $[0.0, 1.0]$.
- **Role Match ($20\%$)**: Role alignment match (neutral $0.5$ when unconfigured).
- **Difficulty Match ($10\%$)**: Comparison of resource difficulty (`Beginner` 1.0, `Intermediate` 2.5, `Advanced` 4.0) vs user's current level ($1.0$ exact/close, $0.8$ stretch $+1.5$, $0.6$ slightly below, $0.4$ misfit).
- **Prerequisite Match ($5\%$)**: Prerequisites met (neutral $0.5$ when unconfigured).

---

## 8. "Why Recommended" Implementation
Every personalized recommendation produces a deterministic explanation object containing:
- `why_recommended`: Structured, human-readable sentence directly referencing computed values (e.g., `"Your Communication & Interpersonal Skills competency is at level 2.0 against the required role level of 3.0 (gap: 1.0, priority: HIGH). 'Government Communication & Briefing' is explicitly mapped to COMM_COMMUNICATION (IGOT)."`).
- `competency_gap`: Competency code.
- `current_level`: Assessed level or `None` if unassessed.
- `required_level`: Role requirement level.
- `gap_size`: Exact difference ($\text{required} - \text{current}$).
- `priority`: Priority classification (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`).
- `score_breakdown`: Full 5-factor component weights, scores, and weighted values.
- `provider_note`: Explicit provenance label.

---

## 9. Provider/Provenance Behavior
- **iGOT Karmayogi**: Labeled as `"iGOT Karmayogi (Curated Catalogue)"` with deep links. Prototype mode status is transparently indicated.
- **NSSTA**: Labeled as `"NSSTA Training Programme (MoSPI Official Calendar)"` with tentative calendar flags noted where applicable (`"NSSTA Training Programme (Official Calendar — Tentative Schedule)"`).

---

## 10. Duplicate Handling
- If a comprehensive course maps to multiple competencies where the user has deficits, candidate deduplication groups them under a single recommendation card.
- The card includes `addressed_gaps_count` and `addressed_competency_codes` (e.g., `addressed_gaps_count=2`, `addressed_competency_codes=["COMM_COMMUNICATION", "STAT_SAMPLING"]`).

---

## 11. Learning History Behavior
- Enrolling in or completing learning activities creates supporting evidence in `competency_evidence` (`type="LEARNING_ACTIVITY"`) for auditing and progress tracking.
- Course completion does not alter authoritative competency profiles or bypass assessment validation, preserving Phase 5D/5F invariants.

---

## 12. Cache Behavior
- In-memory cache is strictly keyed by `f"{user_id}:{limit}"` with 180s TTL safety boundary.
- Event-driven invalidation via `invalidate_recommendations_cache(user_id)` triggers on:
  - Capability assessment submission (`backend/app/capability_assessments/service.py`)
  - Initial assessment submission (`backend/app/assessments/service.py`)
  - Adaptive assessment completion (`backend/app/adaptive_assessments/service.py`)
  - Role reconciliation / assignment changes (`backend/app/roles/resolver.py`)

---

## 13. No-Gap Behavior
- When a user has zero active skill deficits ($\text{gap} \le 0.0$ across all role competencies), returns `total_recommendations=0` with `metadata.reason="All mapped competencies are currently at or above required levels for your role."`

---

## 14. Unresolved-Role Behavior
- When a user does not have a resolved professional role, returns `total_recommendations=0` with `role="Role Mapping Pending"` and `metadata.status="ROLE_MAPPING_PENDING"`.

---

## 15. Files Changed
1. `backend/app/learning_resources/models.py`: Added `why_recommended`, `priority`, `addressed_gaps_count`, and `addressed_competency_codes` fields.
2. `backend/app/learning_resources/service.py`: Filtered for active gaps, added multi-gap aggregation, structured deterministic explainability, honest provider notes, and honest no-gap/no-resource states.
3. `backend/app/learning_resources/repository.py`: Made `get_mapping` and `get_mappings_for_resource` query resilient for both `ObjectId` and `str` resource references.
4. `backend/app/capability_assessments/service.py`: Added `invalidate_recommendations_cache(user_id)` on assessment submission.
5. `backend/app/assessments/service.py`: Added `invalidate_recommendations_cache(user_id)` on initial assessment submission.
6. `backend/tests/test_recommendation_integrity.py`: Created 19 new comprehensive Phase 5G integrity tests.
7. `PHASE_5G_RECOMMENDATION_AUDIT.md`: Created pre-implementation audit matrix.

---

## 16. Tests Added
`backend/tests/test_recommendation_integrity.py`:
- `test_1_user_with_communication_gap_receives_comm_mapped_resource`
- `test_2_user_with_comm_gap_does_not_receive_unrelated_unmapped_resource`
- `test_3_user_with_role_a_does_not_receive_role_b_recommendations`
- `test_4_user_a_recommendations_do_not_leak_to_user_b`
- `test_5_unresolved_role_returns_role_mapping_pending`
- `test_6_unresolved_user_receives_no_role_specific_recommendations`
- `test_7_no_active_gaps_returns_honest_no_gap_state`
- `test_8_active_gap_with_no_mapped_resources_returns_honest_unavailable_state`
- `test_9_unmapped_resources_excluded_from_personalized_recs`
- `test_10_inactive_resources_are_excluded`
- `test_11_duplicate_resource_mappings_do_not_create_duplicate_cards`
- `test_12_multi_gap_resource_represented_with_addressed_gaps_count`
- `test_13_why_recommended_values_match_actual_role_and_profile_data`
- `test_14_provider_provenance_preserved`
- `test_15_igot_prototype_resources_are_not_represented_as_live_apis`
- `test_16_completed_learning_creates_supporting_evidence_without_corrupting_gaps`
- `test_17_cache_is_user_isolated`
- `test_18_cache_invalidates_after_authoritative_capability_assessment`
- `test_19_cache_invalidates_after_role_change`

---

## 17. Full Test Results
```
pytest backend/tests/ -v
================ 392 passed, 4 skipped, 101 warnings in 35.36s ================
```
- **0 failed**
- **4 skipped** (optional remote/unseeded endpoints)
- **392 passed** across all Phase 5A–5G test suites.

---

## 18. Frontend Check
```
npm run check
> tsc --noEmit
✓ Exit code 0 (Clean TypeScript check)
```

---

## 19. Frontend Build
```
npm run build
> vite build && esbuild server/index.ts ...
✓ 1904 modules transformed.
✓ built in 6.38s
✓ Exit code 0 (Clean production bundle)
```

---

## 20. Remaining Limitations
1. **Live iGOT Karmayogi API Integration**: Current iGOT courses use verified curated catalogue metadata and deep links; live two-way enrollment synchronization will be activated once official Karmayogi Bharat API gateway credentials are provided.
2. **In-Memory Cache Scalability**: The current in-memory recommendation cache (`_RECOMMENDATION_CACHE` with 180s TTL) is suitable for single-instance prototype deployments; a distributed cache (e.g., Redis) can be connected when scaling across multiple worker processes.
