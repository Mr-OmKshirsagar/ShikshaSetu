"""Recommendation service - orchestrates candidate generation, scoring, and ranking."""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, UTC
from pymongo.database import Database

from app.skill_gaps import service as gaps_service
from .candidates import CandidateResource, CandidateGenerationService
from .scoring import ScoringService, RecommendationScore, ScoringFormula
from .repository import LearningResourceRepository
from .models import (
    LearningRecommendation,
    RecommendationResponse,
    LearningResource,
    Competency,
    ScoreComponent as ScoreComponentModel,
    RecommendationExplanation,
)


class RecommendationService:
    """
    Main recommendation service.

    Orchestrates:
    1. Skill gap identification
    2. Candidate resource generation
    3. Deterministic scoring
    4. Ranking
    5. Explanation generation
    """

    def __init__(
        self,
        database: Database,
        scoring_formula: Optional[ScoringFormula] = None,
    ):
        self.db = database
        self.repo = LearningResourceRepository(database)
        self.candidate_service = CandidateGenerationService(database)
        self.scoring_service = ScoringService(scoring_formula)

    def get_recommendations_for_user(
        self,
        user_id: str,
        limit: Optional[int] = None,
        skip_unmapped: bool = True,
        precomputed_gaps: Optional[List[Dict[str, Any]]] = None,
    ) -> RecommendationResponse:
        """
        Generate personalized learning recommendations for a user.

        Args:
            user_id: The user ID
            limit: Maximum number of recommendations to return (None = no limit)
            skip_unmapped: If True, only include resources with competency mappings
            precomputed_gaps: Optional pre-calculated skill gaps list to avoid duplicate queries

        Returns:
            RecommendationResponse with ranked recommendations
        """
        from bson import ObjectId

        # 1. Check user and resolved professional role
        user = self.db.users.find_one({"$or": [{"_id": ObjectId(user_id) if ObjectId.is_valid(user_id) else None}, {"_id": user_id}]})
        user_role = (user.get("designation") or user.get("role") or "Unresolved") if user else "Unresolved"

        role_doc = None
        if user and user.get("role_id"):
            role_doc = self.db.roles.find_one({"_id": user["role_id"]})
        if not role_doc and user:
            from app.roles.resolver import resolve_role_for_user
            resolved_role_id = resolve_role_for_user(self.db, user.get("department"), user.get("designation"))
            if resolved_role_id:
                role_doc = self.db.roles.find_one({"_id": resolved_role_id})

        if not role_doc:
            return RecommendationResponse(
                user_id=user_id,
                role="Role Mapping Pending",
                total_recommendations=0,
                recommendations=[],
                metadata={"status": "ROLE_MAPPING_PENDING", "reason": "Role mapping pending: No active professional role assigned."},
            )

        gaps = []
        try:
            if precomputed_gaps is not None:
                all_gaps = precomputed_gaps
            else:
                gap_response = gaps_service.calculate_skill_gaps(self.db, user_id)
                all_gaps = [gap.model_dump() if hasattr(gap, 'model_dump') else gap for gap in gap_response.gaps]
            # Filter strictly for ACTIVE gaps (deficit > 0)
            gaps = [g for g in all_gaps if (g.get("gap") or 0.0) > 0.0 and g.get("gap_category") != "NO_GAP"]
        except Exception:
            gaps = []

        if not gaps:
            return RecommendationResponse(
                user_id=user_id,
                role=role_doc.get("role_name", user_role),
                total_recommendations=0,
                recommendations=[],
                metadata={"reason": "All mapped competencies are currently at or above required levels for your role."},
            )

        # 3. Generate candidates for active gaps
        all_candidates: Dict[str, List[CandidateResource]] = (
            self.candidate_service.generate_candidates_for_gaps(gaps, user_role)
        )

        # 4. Flatten and deduplicate candidates across all gaps
        # Also track all gaps addressed by each unique resource
        flattened_candidates: List[Tuple[CandidateResource, Dict[str, Any]]] = []
        seen_resources: Dict[str, float] = {}  # resource_id -> best_priority
        resource_addressed_codes: Dict[str, List[str]] = {}  # resource_id -> list of competency_codes

        for gap in gaps:
            candidates = all_candidates.get(gap["competency_code"], [])

            for candidate in candidates:
                resource_id = str(candidate.resource.get("_id"))

                # Track all competency codes addressed by this resource
                if resource_id not in resource_addressed_codes:
                    resource_addressed_codes[resource_id] = []
                if gap["competency_code"] not in resource_addressed_codes[resource_id]:
                    resource_addressed_codes[resource_id].append(gap["competency_code"])

                # Only include once per resource, with the highest priority gap
                if resource_id not in seen_resources:
                    flattened_candidates.append((candidate, gap))
                    seen_resources[resource_id] = gap.get("priority_score", 0.5)
                else:
                    # Update if this gap has higher priority
                    if gap.get("priority_score", 0.5) > seen_resources[resource_id]:
                        # Remove old entry and add new one
                        flattened_candidates = [
                            (c, g)
                            for c, g in flattened_candidates
                            if str(c.resource.get("_id")) != resource_id
                        ]
                        flattened_candidates.append((candidate, gap))
                        seen_resources[resource_id] = gap.get("priority_score", 0.5)

        if not flattened_candidates:
            # No candidates found
            return RecommendationResponse(
                user_id=user_id,
                role=user_role or "Unknown",
                total_recommendations=0,
                recommendations=[],
                metadata={"reason": "No mapped learning resources are currently available for your active gaps."},
            )

        # 5. Score all candidates
        scored_candidates: List[
            Tuple[CandidateResource, RecommendationScore, Dict[str, Any]]
        ] = []

        for candidate, gap in flattened_candidates:
            # Get user's current level for this competency
            user_current_level = gap["current_level"]

            score = self.scoring_service.formula.score_candidate(
                candidate=candidate,
                provider=candidate.provider,
                user_current_level=user_current_level,
                user_role=user_role,
            )

            scored_candidates.append((candidate, score, gap))

        # 6. Sort by score (highest first)
        scored_candidates.sort(key=lambda x: x[1].total_score, reverse=True)

        # 7. Apply limit
        if limit:
            scored_candidates = scored_candidates[:limit]

        # 8. Build recommendation response
        recommendations: List[LearningRecommendation] = []

        for rank, (candidate, score, gap) in enumerate(scored_candidates, start=1):
            resource_id = str(candidate.resource.get("_id"))
            addressed_codes = resource_addressed_codes.get(resource_id, [gap["competency_code"]])
            recommendation = self._build_recommendation(
                rank=rank,
                candidate=candidate,
                score=score,
                gap=gap,
                user_role=user_role,
                addressed_codes=addressed_codes,
            )
            recommendations.append(recommendation)

        return RecommendationResponse(
            user_id=user_id,
            role=user_role or "Unknown",
            total_recommendations=len(recommendations),
            recommendations=recommendations,
            metadata={
                "total_gaps": len(gaps),
                "candidates_generated": len(flattened_candidates),
                "candidates_scored": len(scored_candidates),
                "scoring_weights": self.scoring_service.formula.weights,
            },
        )

    def _build_recommendation(
        self,
        rank: int,
        candidate: CandidateResource,
        score: RecommendationScore,
        gap: Dict[str, Any],
        user_role: Optional[str] = None,
        addressed_codes: Optional[List[str]] = None,
    ) -> LearningRecommendation:
        """Build a complete LearningRecommendation object."""

        resource = candidate.resource
        addressed_list = addressed_codes or [gap["competency_code"]]

        # Build resource model
        resource_model = LearningResource(
            resource_id=resource.get("resource_id", ""),
            provider=resource.get("provider", ""),
            resource_type=resource.get("resource_type", ""),
            title=resource.get("title", ""),
            metadata={
                "duration_hours": resource.get("metadata", {}).get("duration_hours"),
                "difficulty": resource.get("metadata", {}).get("difficulty"),
                "target_roles": resource.get("metadata", {}).get("target_roles", []),
                "prerequisites": resource.get("metadata", {}).get(
                    "prerequisites", []
                ),
            },
            competencies=resource.get("competencies", []),
            source={
                "source_type": resource.get("source", {}).get("source_type", ""),
                "source_url": resource.get("source", {}).get("source_url"),
                "source_document": resource.get("source", {}).get(
                    "source_document", ""
                ),
                "verification_status": resource.get("source", {}).get(
                    "verification_status", ""
                ),
            },
            provider_specific={
                "course_id": resource.get("provider_specific", {}).get("course_id"),
                "programme_id": resource.get("provider_specific", {}).get(
                    "programme_id"
                ),
                "course_url": resource.get("provider_specific", {}).get("course_url"),
                "provider_name": resource.get("provider_specific", {}).get(
                    "provider_name"
                ),
                "extraction_note": resource.get("provider_specific", {}).get(
                    "extraction_note"
                ),
            },
            status=resource.get("status", "ACTIVE"),
            created_at=resource.get("created_at") or datetime.now(UTC),
            updated_at=resource.get("updated_at") or datetime.now(UTC),
        )

        # Build explanation
        explanation = self._build_explanation(
            candidate=candidate,
            score=score,
            gap=gap,
        )

        return LearningRecommendation(
            rank=rank,
            resource=resource_model,
            provider=resource.get("provider", ""),
            competency_code=gap["competency_code"],
            competency_name=candidate.competency_name,
            current_level=gap.get("current_level"),
            required_level=gap.get("required_level"),
            gap=gap.get("gap", 0),
            score=score.total_score,
            why_recommended=explanation.why_recommended,
            addressed_gaps_count=len(addressed_list),
            addressed_competency_codes=addressed_list,
            explanation=explanation,
            source_verification=resource.get("source", {}).get(
                "verification_status", "UNKNOWN"
            ),
        )

    def _build_explanation(
        self,
        candidate: CandidateResource,
        score: RecommendationScore,
        gap: Dict[str, Any],
    ) -> RecommendationExplanation:
        """Build explanation for why this resource was recommended."""

        # Generate summary and deterministic why_recommended
        summary = self._generate_summary(candidate, gap)
        why_recommended = self._generate_why_recommended(candidate, gap)

        # Build score breakdown
        score_components = [
            ScoreComponentModel(
                name=comp.name,
                weight=comp.weight,
                score=comp.score,
                value=comp.value,
            )
            for comp in score.components
        ]

        # Provider note
        provider = candidate.resource.get("provider", "")
        provider_note = None
        if provider == "IGOT":
            provider_note = "iGOT Karmayogi (Curated Catalogue)"
        elif provider == "NSSTA":
            if candidate.resource.get("source", {}).get("verification_status") == "TENTATIVE":
                provider_note = "NSSTA Training Programme (Official Calendar — Tentative Schedule)"
            else:
                provider_note = "NSSTA Training Programme (MoSPI Official Calendar)"

        priority_str = gap.get("gap_category", "MEDIUM").upper()

        return RecommendationExplanation(
            summary=summary,
            why_recommended=why_recommended,
            competency_gap=f"{gap['competency_code']}",
            current_level=gap.get("current_level"),
            required_level=gap.get("required_level"),
            gap_size=gap.get("gap", 0),
            priority=priority_str,
            score_breakdown=score_components,
            provider_note=provider_note,
        )

    def _generate_why_recommended(
        self, candidate: CandidateResource, gap: Dict[str, Any]
    ) -> str:
        """Generate deterministic why_recommended string."""
        comp_name = candidate.competency_name or gap.get("competency_code", "Competency")
        current_lvl = gap.get("current_level")
        current_str = f"{current_lvl:.1f}" if current_lvl is not None else "Unassessed (0.0)"
        req_lvl = gap.get("required_level", 0.0)
        gap_val = gap.get("gap", 0.0)
        priority = gap.get("gap_category", "MEDIUM").upper()
        provider = candidate.resource.get("provider", "Curated")
        resource_title = candidate.resource.get("title", "Mapped Resource")

        return (
            f"Your {comp_name} competency is at level {current_str} against the required role level of {req_lvl:.1f} "
            f"(gap: {gap_val:.1f}, priority: {priority}). '{resource_title}' is explicitly mapped to {gap['competency_code']} ({provider})."
        )

    def _generate_summary(
        self, candidate: CandidateResource, gap: Dict[str, Any]
    ) -> str:
        """Generate human-readable explanation summary."""

        resource_title = candidate.resource.get("title", "Unknown")
        provider = candidate.resource.get("provider", "Unknown")
        gap_size_cat = gap.get("gap_category", "medium").upper()
        
        current_level = gap.get("current_level") or 0.0
        required_level = gap.get("required_level", 0.0)

        return (
            f"Your {gap['competency_code']} competency is {current_level:.1f}/5.0 while your role requires {required_level:.1f}/5.0. "
            f"This {provider} {gap_size_cat.lower()} gap is a priority. "
            f'"{resource_title}" is mapped to {gap["competency_code"]} and can help close this gap.'
        )

    def get_unmapped_resources(
        self, provider: Optional[str] = None, limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get unmapped resources (browseable but not competency-based).

        Args:
            provider: Filter by provider (None = all providers)
            limit: Maximum number to return

        Returns:
            List of unmapped resource dicts
        """
        unmapped = self.candidate_service.get_unmapped_resources(provider)

        if limit:
            unmapped = unmapped[:limit]

        return unmapped

    def get_resource_details(self, resource_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific resource."""
        return self.repo.get_resource_by_id(resource_id)

    def get_resources_by_competency(
        self, competency_code: str, provider: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get all resources for a competency, optionally filtered by provider."""
        if provider:
            return self.repo.get_resources_by_competency_and_provider(
                competency_code, provider
            )
        return self.repo.get_resources_by_competency(competency_code)
