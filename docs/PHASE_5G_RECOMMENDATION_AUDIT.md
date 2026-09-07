# PHASE 5G — RECOMMENDATION INTEGRITY & EXPLAINABILITY AUDIT

## Executive Summary
This document provides a comprehensive audit of the ShikshaSetu recommendation engine across candidate generation, role filtering, competency filtering, explicit resource mapping, scoring weights, ranking, deduplication, caching, explainability ("Why Recommended"), and provider provenance.

---

## Pipeline Audit Matrix

| Stage | Current Behavior | Data Source | Integrity Risk | Required Change |
| :--- | :--- | :--- | :--- | :--- |
| **1. Candidate Generation** | `CandidateGenerationService.generate_candidates_for_gaps()` queries providers for resources mapped to active gap competency codes. | `competency_resource_mappings`, `learning_resources` | Low risk if mappings are verified; unmapped resources might leak if queried without filter. | Ensure candidate generation strictly queries explicit mappings for active gaps only. |
| **2. Role Filtering** | Service resolves role from user's `role_id` or `resolve_role_for_user(department, designation)`. Unresolved users return `ROLE_MAPPING_PENDING`. | `users`, `roles`, `role_mappings` | No silent fallback to Statistical Officer or arbitrary roles exists after Phase 5E. | Preserve strict Phase 5E role resolution invariant. Return 0 recommendations with pending status if unresolved. |
| **3. Competency Filtering** | Evaluates active competency gaps derived strictly from resolved role requirements minus authoritative competency profile. | `skill_gaps.service.calculate_skill_gaps()` | If user has no gaps, engine must not fabricate candidate recommendations. | Return explicit honest no-gap state (`"All mapped competencies are currently at or above required levels"`). |
| **4. Resource Mapping** | Providers look up explicit mapping records in `competency_resource_mappings` collection matching competency code and provider. | `competency_resource_mappings` | Unmapped resources or keyword-based inferences could produce irrelevant recommendations. | Strictly prohibit heuristic or keyword-inferred recommendations. Only explicit database mappings are eligible. |
| **5. Gap Severity Weighting** | `gap_priority` component uses `gap.priority_score` (derived from gap size, role requirement level, and core vs elective weight). | `skill_gaps` output | Weighting is mathematically bounded (0.0 to 1.0). | Preserve deterministic formula; do not alter weight constants arbitrarily. |
| **6. Recommendation Scoring** | 5-factor deterministic model: `competency_match` (0.40), `gap_priority` (0.25), `role_match` (0.20), `difficulty_match` (0.10), `prerequisite_match` (0.05). | `ScoringFormula` / `ScoringService` | Arbitrary weight tuning breaks deterministic auditability. | Preserve exact 40/25/20/10/5 weights. Ensure all factor calculations handle nulls and edge cases safely. |
| **7. Ranking** | Scored candidates sorted in descending order by `total_score`. Ties preserved stably. | Scored candidate list | If same resource addresses multiple gaps, separate cards could duplicate UI tiles. | Deduplicate multi-gap resources into a single high-priority card with multi-gap metadata (`addressed_gaps_count`, `addressed_competency_codes`). |
| **8. Caching** | Short-term in-memory cache keyed by `f"{user_id}:{limit}"` with 180s TTL. | `_RECOMMENDATION_CACHE` dictionary | Stale recommendations after formal capability assessment completion or role reconfiguration. | Trigger `invalidate_recommendations_cache(user_id)` on capability assessment submission and initial assessment submission in addition to adaptive assessments. |
| **9. User Isolation** | Recommendations calculated strictly per `user_id` using user's own resolved role and own competency profile. | `user_id`, `competency_profiles` | Leaking role or gap data between concurrent user sessions. | Cache keys strictly user-isolated (`f"{user_id}:{limit}"`). No cross-user state sharing. |
| **10. "Why Recommended" Explainability** | Summary generated with template: `"Your {competency} competency is {current}/5.0 while your role requires {required}/5.0..."`. | `gap` record, `candidate.resource`, `score.components` | Generic or ungrounded AI text could hallucinate rationale. | Use deterministic, structured explainability with exact role requirement, current level, gap size, priority category, provider note, and score breakdown. |
| **11. Handling of Unmapped Resources** | Unmapped resources stored with `status="ACTIVE"`, browseable via `/resources/unmapped` or catalogue endpoint, excluded from personalized recs. | `learning_resources` where ID not in mappings | Unmapped resources accidentally appearing in personalized feed. | Invariant: Personalized recommendation candidate generation NEVER includes unmapped resources. |
| **12. Handling of Unresolved Roles** | Users without resolved role receive `RecommendationResponse` with `role="Role Mapping Pending"`, `total_recommendations=0`, `metadata.status="ROLE_MAPPING_PENDING"`. | `users`, `roles` | Falling back to default role. | Preserve Phase 5E invariant: unresolved users receive no role-specific recommendations. |
| **13. Handling of No Gaps** | When `calculate_skill_gaps` yields 0 gaps, returns 0 recommendations with clear honest message. | `skill_gaps` | Fabricating general courses as "recommendations" when no deficit exists. | Return `total_recommendations=0`, message indicating all competencies meet or exceed required levels. |
| **14. Handling of Missing Resources** | When user has active gaps but no resources are mapped in the database, returns 0 recommendations with honest message. | `candidate_service` empty result | Fabricating placeholder or hallucinated course titles. | Return `total_recommendations=0`, `metadata.reason="No mapped learning resources available"`. |

---

## Detailed Audit Findings

### 1. Scoring Formula Integrity
The current scoring model in `backend/app/learning_resources/scoring.py` evaluates:
- **`competency_match` (40%)**: Uses explicit mapping confidence score $[0.0, 1.0]$.
- **`gap_priority` (25%)**: Uses normalized gap priority score $[0.0, 1.0]$.
- **`role_match` (20%)**: Uses provider role-matching score (neutral $0.5$ if unspecified).
- **`difficulty_match` (10%)**: Compares resource difficulty (`Beginner` = 1.0, `Intermediate` = 2.5, `Advanced` = 4.0) against user's current level ($1.0$ for match, $0.8$ for stretch $+1.5$, $0.6$ for slightly below, $0.4$ for hard misfit).
- **`prerequisite_match` (5%)**: Evaluates prerequisites met (neutral $0.5$ when unconfigured).
- **Sum of Weights**: $0.40 + 0.25 + 0.20 + 0.10 + 0.05 = 1.00$.
- **Decision**: Preserve exact weights. No arbitrary adjustments.

### 2. Provider Provenance Honesty
- **iGOT Karmayogi**: Curated catalogue integration with structured URLs (`https://igot.example.com/...` or official deep links). Model metadata must clearly indicate curated catalogue status without falsely claiming live two-way sync APIs.
- **NSSTA**: Official training calendar programmes (MoSPI). Tentative calendar listings are marked `verification_status="TENTATIVE"` with honest notes explaining tentative schedule status.

### 3. Deduplication & Multi-Gap Representation
- When a single comprehensive learning resource maps to multiple competencies where the user has gaps, the candidate deduplication selects the highest-priority gap as primary but should record all addressed gaps.
- The `LearningRecommendation` model should include `addressed_gaps_count` and `addressed_competency_codes` to give officials complete transparency.

### 4. Event-Driven Cache Invalidation
- Recommendation cache is in-memory per user ID.
- Invalidation must be called on:
  1. Authoritative capability assessment submission (`capability_assessments/service.py`)
  2. Initial assessment submission (`assessments/service.py`)
  3. Adaptive assessment completion (`adaptive_assessments/service.py`)
  4. Role assignment / resolution changes (`roles/resolver.py`)
