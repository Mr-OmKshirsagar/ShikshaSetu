"""
ShikshaSetu Capability Assistant Service — Phase 6B Latency Hardened.

Architecture (Phase 6B):
  User message
    → QueryIntentRouter (deterministic, no LLM)
    → OUT_OF_SCOPE      → immediate polite refusal (< 5ms)
    → DETERMINISTIC GAP → direct MongoDB skill gap data (< 150ms)
    → DETERMINISTIC REC → direct 5-factor recommendation data (< 150ms)
    → RAG KNOWLEDGE     → scoped curriculum retrieval → MMR → LLM (streaming SSE)
    → HYBRID ADVISORY   → cached user context + RAG → LLM (streaming SSE)

Public API is unchanged:
  AssistantService(database, settings).process_chat(user_id, request) -> AssistantChatResponse
  AssistantService(database, settings).stream_chat(user_id, request) -> Generator[str, None, None] (SSE)
"""

from __future__ import annotations

import json
import logging
import time
from typing import Any, Dict, Generator, List, Optional, Tuple

from pymongo.database import Database

from app.ai.models import DocumentChunk
from app.ai.providers.gemini_provider import GeminiLLMProvider
from app.ai.providers.mock_provider import MockLLMProvider
from app.core.config import Settings, get_settings
from app.rag.groundedness import (
    GroundednessResult,
    StructuredCitation,
    build_citations,
    insufficient_evidence_response,
    score_groundedness,
)
from app.rag.hybrid_retrieval import retrieve_for_chatbot
from app.rag.intent_router import QueryIntent, classify_intent
from app.rag.reranker import mmr_rerank
from .context import build_user_capability_context
from .prompts import CAPABILITY_COPILOT_SYSTEM_PROMPT, build_copilot_user_prompt
from .schemas import (
    AssistantChatRequest,
    AssistantChatResponse,
    AssistantSourceCitation,
    SuggestedAction,
)

logger = logging.getLogger(__name__)


class AssistantService:
    """
    Orchestrates query intent routing, hybrid retrieval, MMR reranking,
    user-context injection, LLM inference, streaming SSE, and groundedness scoring.
    """

    def __init__(self, database: Database, settings: Optional[Settings] = None) -> None:
        self.db = database
        self.settings = settings or get_settings()
        self._llm_provider = self._init_llm()
        self._embedding_provider = self._init_embedding()

    # ── Provider initialisation ───────────────────────────────────────────────

    def _init_llm(self):
        provider = getattr(self.settings, "llm_provider", "gemini").lower()
        api_key = getattr(self.settings, "llm_api_key", "")
        model = getattr(self.settings, "llm_model", "models/gemini-3.6-flash")
        if provider == "gemini" and api_key:
            return GeminiLLMProvider(api_key=api_key, model=model)
        return MockLLMProvider()

    def _init_embedding(self):
        provider = getattr(self.settings, "embedding_provider", "gemini").lower()
        api_key = (
            getattr(self.settings, "embedding_api_key", "")
            or getattr(self.settings, "llm_api_key", "")
        )
        model = getattr(self.settings, "embedding_model", "models/gemini-embedding-001")

        if provider == "gemini" and api_key:
            try:
                from app.ai.embeddings.gemini_provider import GeminiEmbeddingProvider
                return GeminiEmbeddingProvider(api_key=api_key, model=model)
            except Exception as exc:
                logger.warning("Embedding provider init failed: %s — vector branch disabled", exc)
                return None
        if provider == "mock":
            from app.ai.embeddings.mock_provider import MockEmbeddingProvider
            return MockEmbeddingProvider(dimension=getattr(self.settings, "embedding_dimension", 768))
        return None

    # ── Query Classification Helpers ──────────────────────────────────────────

    def _is_gap_query(self, message: str) -> bool:
        msg_lower = message.lower()
        return any(
            signal in msg_lower
            for signal in (
                "my gap", "my skill", "my score", "priority gap", "highest priority",
                "what are my skill gaps", "what is my skill gap", "what is my current capability",
                "what is my required level", "show my skill gaps", "view my gaps",
            )
        )

    def _is_rec_query(self, message: str) -> bool:
        msg_lower = message.lower()
        return any(
            signal in msg_lower
            for signal in (
                "recommend igot", "recommend courses for me", "recommend courses",
                "recommend training", "recommend for my current role", "recommendation for my role",
                "suggest courses", "courses for my role", "courses for my current role",
                "recommend igot courses for my current role", "show my recommendations",
                "what courses should i take",
            )
        )

    # ── Main synchronous entry point (100% backward-compatible) ───────────────

    def process_chat(
        self,
        user_id: str,
        request: AssistantChatRequest,
    ) -> AssistantChatResponse:
        """
        Process a chat request end-to-end with strict latency hardening.
        Deterministic queries (skill gaps, recommendations) bypass LLM.
        Knowledge queries use lean context and scoped RAG.
        """
        t_start = time.perf_counter()
        t_ctx_start = 0.0
        t_ctx_end = 0.0
        t_rag_start = 0.0
        t_rag_end = 0.0
        t_llm_start = 0.0
        t_llm_end = 0.0

        message = request.message

        # ── 1. Intent routing ─────────────────────────────────────────────────
        intent_result = classify_intent(message)
        logger.debug(
            "Intent: %s (confidence=%.2f) — %s",
            intent_result.intent, intent_result.confidence, intent_result.reason,
        )

        # ── 2. Immediate refusal for out-of-scope / injection ─────────────────
        if intent_result.refuse:
            refusal = (
                "I'm the Karmayogi AI Co-Pilot for ShikshaSetu, focused on your "
                "competency development. I'm not able to help with that request."
            )
            t_total = (time.perf_counter() - t_start) * 1000
            return AssistantChatResponse(
                answer=refusal,
                sources=[],
                context_summary={
                    "intent": intent_result.intent.value,
                    "refused": True,
                    "latency_metrics": {"total_ms": round(t_total, 2)},
                },
                suggested_actions=self._generate_suggested_actions(message, {}),
                model_provider="rule-based-refusal",
            )

        # ── 3. Query Intent Fast Paths ────────────────────────────────────────
        is_gap = self._is_gap_query(message)
        is_rec = self._is_rec_query(message)

        if is_gap or is_rec:
            t_ctx_start = time.perf_counter()
            context_data = build_user_capability_context(
                self.db,
                user_id,
                request.current_competency_code,
                include_recommendations=is_rec,
                use_cache=True,
            )
            t_ctx_end = time.perf_counter()

            if is_rec:
                answer = self._generate_deterministic_recommendations_response(message, context_data)
                citations = self._build_recommendation_citations(context_data)
            else:
                answer = self._generate_deterministic_gaps_response(message, context_data)
                citations = self._build_recommendation_citations(context_data)[:1] if context_data.get("recommendations") else []

            suggested_actions = self._generate_suggested_actions(message, context_data)
            t_total = (time.perf_counter() - t_start) * 1000

            return AssistantChatResponse(
                answer=answer,
                sources=citations,
                context_summary={
                    "intent": "DETERMINISTIC_FAST_PATH",
                    "profile": context_data.get("profile"),
                    "top_gap_count": len(context_data.get("top_gaps", [])),
                    "rag_chunks_used": 0,
                    "latency_metrics": {
                        "total_ms": round(t_total, 2),
                        "context_ms": round((t_ctx_end - t_ctx_start) * 1000, 2),
                        "llm_ms": 0.0,
                    },
                },
                suggested_actions=suggested_actions,
                model_provider="rule-based-fast",
            )

        # ── 4. RAG / Knowledge / Hybrid Path ──────────────────────────────────
        context_data: Dict[str, Any] = {}
        if intent_result.intent == QueryIntent.HYBRID or intent_result.use_user_data:
            t_ctx_start = time.perf_counter()
            needs_recs = any(w in message.lower() for w in ("course", "training", "recommend"))
            context_data = build_user_capability_context(
                self.db,
                user_id,
                request.current_competency_code,
                include_recommendations=needs_recs,
                use_cache=True,
            )
            t_ctx_end = time.perf_counter()

        reranked_chunks: List[Tuple[DocumentChunk, float]] = []
        if intent_result.use_rag:
            t_rag_start = time.perf_counter()
            try:
                raw_candidates = retrieve_for_chatbot(
                    database=self.db,
                    query=message,
                    embedding_provider=(
                        self._embedding_provider
                        if getattr(self.settings, "rag_chat_vector_enabled", False)
                        else None
                    ),
                    top_k_keyword=min(self.settings.rag_top_k_keyword, 10),
                    top_k_vector=min(self.settings.rag_top_k_vector, 10),
                    competency_code=request.current_competency_code,
                )
                reranked_chunks = mmr_rerank(
                    candidates=raw_candidates,
                    query=message,
                    top_k=min(self.settings.rag_rerank_top_k, 4),
                    mmr_lambda=self.settings.rag_mmr_lambda,
                    embedding_provider=(
                        self._embedding_provider
                        if getattr(self.settings, "rag_chat_vector_enabled", False)
                        else None
                    ),
                )
            except Exception as exc:
                logger.warning("Hybrid retrieval failed: %s", exc)
            t_rag_end = time.perf_counter()

        retrieved_text_chunks: List[Dict[str, Any]] = []
        for chunk, _ in reranked_chunks:
            source_id = str(chunk.id or chunk.material_id)
            label_parts = [source_id]
            if chunk.source_page:
                label_parts.append(f"p{chunk.source_page}")
            if chunk.source_section:
                label_parts.append(chunk.source_section[:30])
            retrieved_text_chunks.append({
                "source_id": " | ".join(label_parts),
                "text": (chunk.text or "")[:350],
            })

        # ── 5. Build prompt ───────────────────────────────────────────────────
        prompt = build_copilot_user_prompt(
            user_message=message,
            context_data=context_data,
            retrieved_text_chunks=retrieved_text_chunks,
            context_page=request.context_page,
        )

        # ── 6. LLM inference ──────────────────────────────────────────────────
        provider_name = "gemini"
        answer = ""
        t_llm_start = time.perf_counter()
        try:
            if hasattr(self._llm_provider, "generate"):
                answer = self._llm_provider.generate(
                    f"{CAPABILITY_COPILOT_SYSTEM_PROMPT}\n\n{prompt}",
                    max_tokens=500,
                )
            else:
                answer = self._generate_fallback_response(message, context_data, reranked_chunks)
                provider_name = "capability-fallback"
        except Exception as exc:
            logger.warning("LLM inference failed: %s — using fallback", exc)
            answer = self._generate_fallback_response(message, context_data, reranked_chunks)
            provider_name = "capability-fallback"
        t_llm_end = time.perf_counter()

        # ── 7. Groundedness check ─────────────────────────────────────────────
        gnd: Optional[GroundednessResult] = None
        if intent_result.use_rag and reranked_chunks:
            try:
                gnd = score_groundedness(
                    answer=answer,
                    retrieved_chunks=reranked_chunks,
                    threshold=self.settings.rag_groundedness_threshold,
                )
                if not gnd.is_grounded and provider_name == "gemini":
                    answer = insufficient_evidence_response(message)
                    provider_name = "groundedness-fallback"
            except Exception:
                pass

        # ── 8. Build structured citations ─────────────────────────────────────
        structured_citations = build_citations(reranked_chunks, max_citations=4)
        for rec in context_data.get("recommendations", [])[:2]:
            doc_id = rec.get("source_doc") or "iGOT-CATALOG"
            if not any(c.source_id == doc_id for c in structured_citations):
                structured_citations.append(StructuredCitation(
                    source_id=doc_id,
                    title=f"{rec.get('provider', 'iGOT')} — {rec.get('title', 'Course')}",
                    source_type="IGOT_COURSE" if (rec.get("provider") or "").upper() == "IGOT" else "NSSTA_PROGRAMME",
                    url=rec.get("url"),
                    excerpt=f"Target: {rec.get('competency_code')} (Score: {rec.get('score')})",
                ))

        api_citations = [
            AssistantSourceCitation(
                source_id=c.source_id,
                title=c.title,
                source_type=c.source_type,
                url=c.url,
                excerpt=c.excerpt,
            )
            for c in structured_citations
        ]

        suggested_actions = self._generate_suggested_actions(message, context_data)
        t_total = (time.perf_counter() - t_start) * 1000

        latency_metrics = {
            "total_ms": round(t_total, 2),
            "context_ms": round((t_ctx_end - t_ctx_start) * 1000, 2) if t_ctx_start else 0.0,
            "rag_ms": round((t_rag_end - t_rag_start) * 1000, 2) if t_rag_start else 0.0,
            "llm_ms": round((t_llm_end - t_llm_start) * 1000, 2) if t_llm_start else 0.0,
        }
        logger.info("copilot_metrics: %s provider=%s", latency_metrics, provider_name)

        context_summary: Dict[str, Any] = {
            "intent": intent_result.intent.value,
            "profile": context_data.get("profile"),
            "top_gap_count": len(context_data.get("top_gaps", [])),
            "rag_chunks_used": len(reranked_chunks),
            "latency_metrics": latency_metrics,
        }
        if gnd is not None:
            context_summary["groundedness_score"] = gnd.score
            context_summary["groundedness_passed"] = gnd.is_grounded

        return AssistantChatResponse(
            answer=answer,
            sources=api_citations,
            context_summary=context_summary,
            suggested_actions=suggested_actions,
            model_provider=provider_name,
        )

    # ── Server-Sent Events (SSE) Streaming generator ──────────────────────────

    def stream_chat(
        self,
        user_id: str,
        request: AssistantChatRequest,
    ) -> Generator[str, None, None]:
        """
        Yields structured SSE events:
          - data: {"type": "status", "stage": "...", "message": "..."}
          - data: {"type": "delta", "delta": "..."}
          - data: {"type": "done", "response": AssistantChatResponse...}
        """
        t_start = time.perf_counter()
        message = request.message

        yield f"data: {json.dumps({'type': 'status', 'stage': 'thinking', 'message': 'Thinking...'})}\n\n"

        # 1. Intent Routing
        intent_result = classify_intent(message)
        if intent_result.refuse:
            refusal = (
                "I'm the Karmayogi AI Co-Pilot for ShikshaSetu, focused on your "
                "competency development. I'm not able to help with that request."
            )
            resp = AssistantChatResponse(
                answer=refusal,
                sources=[],
                context_summary={"intent": intent_result.intent.value, "refused": True},
                suggested_actions=self._generate_suggested_actions(message, {}),
                model_provider="rule-based-refusal",
            )
            yield f"data: {json.dumps({'type': 'delta', 'delta': refusal})}\n\n"
            yield f"data: {json.dumps({'type': 'done', 'response': resp.model_dump()})}\n\n"
            return

        # 2. Fast Path Routing
        is_gap = self._is_gap_query(message)
        is_rec = self._is_rec_query(message)

        if is_gap or is_rec:
            yield f"data: {json.dumps({'type': 'status', 'stage': 'checking_context', 'message': 'Checking your competency profile...'})}\n\n"
            context_data = build_user_capability_context(
                self.db,
                user_id,
                request.current_competency_code,
                include_recommendations=is_rec,
                use_cache=True,
            )

            if is_rec:
                answer = self._generate_deterministic_recommendations_response(message, context_data)
                citations = self._build_recommendation_citations(context_data)
            else:
                answer = self._generate_deterministic_gaps_response(message, context_data)
                citations = self._build_recommendation_citations(context_data)[:1] if context_data.get("recommendations") else []

            actions = self._generate_suggested_actions(message, context_data)
            t_total = (time.perf_counter() - t_start) * 1000

            # Yield chunks smoothly
            words = answer.split(" ")
            chunk_size = 5
            for i in range(0, len(words), chunk_size):
                chunk_str = " ".join(words[i:i + chunk_size]) + " "
                yield f"data: {json.dumps({'type': 'delta', 'delta': chunk_str})}\n\n"

            final_resp = AssistantChatResponse(
                answer=answer,
                sources=citations,
                context_summary={
                    "intent": "DETERMINISTIC_FAST_PATH",
                    "profile": context_data.get("profile"),
                    "top_gap_count": len(context_data.get("top_gaps", [])),
                    "rag_chunks_used": 0,
                    "latency_metrics": {"total_ms": round(t_total, 2)},
                },
                suggested_actions=actions,
                model_provider="rule-based-fast",
            )
            yield f"data: {json.dumps({'type': 'done', 'response': final_resp.model_dump()})}\n\n"
            return

        # 3. RAG Knowledge / Hybrid Path
        context_data = {}
        if intent_result.intent == QueryIntent.HYBRID or intent_result.use_user_data:
            yield f"data: {json.dumps({'type': 'status', 'stage': 'checking_context', 'message': 'Checking your role context...'})}\n\n"
            context_data = build_user_capability_context(
                self.db,
                user_id,
                request.current_competency_code,
                include_recommendations=any(w in message.lower() for w in ("course", "training", "recommend")),
                use_cache=True,
            )

        reranked_chunks: List[Tuple[DocumentChunk, float]] = []
        if intent_result.use_rag:
            yield f"data: {json.dumps({'type': 'status', 'stage': 'retrieving', 'message': 'Checking National Competency Framework & curriculum...'})}\n\n"
            try:
                raw_candidates = retrieve_for_chatbot(
                    database=self.db,
                    query=message,
                    embedding_provider=(
                        self._embedding_provider
                        if getattr(self.settings, "rag_chat_vector_enabled", False)
                        else None
                    ),
                    top_k_keyword=min(self.settings.rag_top_k_keyword, 10),
                    top_k_vector=min(self.settings.rag_top_k_vector, 10),
                    competency_code=request.current_competency_code,
                )
                reranked_chunks = mmr_rerank(
                    candidates=raw_candidates,
                    query=message,
                    top_k=min(self.settings.rag_rerank_top_k, 4),
                    mmr_lambda=self.settings.rag_mmr_lambda,
                    embedding_provider=(
                        self._embedding_provider
                        if getattr(self.settings, "rag_chat_vector_enabled", False)
                        else None
                    ),
                )
            except Exception as exc:
                logger.warning("Hybrid retrieval stream failed: %s", exc)

        retrieved_text_chunks = [
            {
                "source_id": f"{chunk.id or chunk.material_id}" + (f" | p{chunk.source_page}" if chunk.source_page else ""),
                "text": (chunk.text or "")[:350],
            }
            for chunk, _ in reranked_chunks
        ]

        prompt = build_copilot_user_prompt(
            user_message=message,
            context_data=context_data,
            retrieved_text_chunks=retrieved_text_chunks,
            context_page=request.context_page,
        )

        yield f"data: {json.dumps({'type': 'status', 'stage': 'generating', 'message': 'Generating your answer...'})}\n\n"

        answer_parts = []
        provider_name = "gemini"
        try:
            if hasattr(self._llm_provider, "generate_stream"):
                for delta in self._llm_provider.generate_stream(
                    f"{CAPABILITY_COPILOT_SYSTEM_PROMPT}\n\n{prompt}",
                    max_tokens=500,
                ):
                    answer_parts.append(delta)
                    yield f"data: {json.dumps({'type': 'delta', 'delta': delta})}\n\n"
            else:
                text = self._llm_provider.generate(
                    f"{CAPABILITY_COPILOT_SYSTEM_PROMPT}\n\n{prompt}",
                    max_tokens=500,
                )
                answer_parts.append(text)
                yield f"data: {json.dumps({'type': 'delta', 'delta': text})}\n\n"
        except Exception as exc:
            logger.warning("LLM streaming inference failed: %s — falling back", exc)
            fallback_text = self._generate_fallback_response(message, context_data, reranked_chunks)
            answer_parts = [fallback_text]
            provider_name = "capability-fallback"
            yield f"data: {json.dumps({'type': 'delta', 'delta': fallback_text})}\n\n"

        full_answer = "".join(answer_parts)

        # Groundedness Check
        gnd: Optional[GroundednessResult] = None
        if intent_result.use_rag and reranked_chunks:
            try:
                gnd = score_groundedness(
                    answer=full_answer,
                    retrieved_chunks=reranked_chunks,
                    threshold=self.settings.rag_groundedness_threshold,
                )
            except Exception:
                pass

        # Citations
        structured_citations = build_citations(reranked_chunks, max_citations=4)
        for rec in context_data.get("recommendations", [])[:2]:
            doc_id = rec.get("source_doc") or "iGOT-CATALOG"
            if not any(c.source_id == doc_id for c in structured_citations):
                structured_citations.append(StructuredCitation(
                    source_id=doc_id,
                    title=f"{rec.get('provider', 'iGOT')} — {rec.get('title', 'Course')}",
                    source_type="IGOT_COURSE" if (rec.get("provider") or "").upper() == "IGOT" else "NSSTA_PROGRAMME",
                    url=rec.get("url"),
                    excerpt=f"Target: {rec.get('competency_code')} (Score: {rec.get('score')})",
                ))

        api_citations = [
            AssistantSourceCitation(
                source_id=c.source_id,
                title=c.title,
                source_type=c.source_type,
                url=c.url,
                excerpt=c.excerpt,
            )
            for c in structured_citations
        ]

        t_total = (time.perf_counter() - t_start) * 1000
        final_resp = AssistantChatResponse(
            answer=full_answer,
            sources=api_citations,
            context_summary={
                "intent": intent_result.intent.value,
                "profile": context_data.get("profile"),
                "rag_chunks_used": len(reranked_chunks),
                "latency_metrics": {"total_ms": round(t_total, 2)},
            },
            suggested_actions=self._generate_suggested_actions(message, context_data),
            model_provider=provider_name,
        )
        yield f"data: {json.dumps({'type': 'done', 'response': final_resp.model_dump()})}\n\n"

    # ── Deterministic Response Builders ───────────────────────────────────────

    def _generate_deterministic_gaps_response(
        self,
        message: str,
        context_data: Dict[str, Any],
    ) -> str:
        profile = context_data.get("profile", {})
        name = profile.get("full_name", "Officer")
        role = profile.get("role_name", "Official")
        top_gaps = context_data.get("top_gaps", [])

        if not top_gaps:
            return (
                f"Hello **{name}**. No active competency deficits are currently identified for your role as **{role}**.\n\n"
                f"All assessed competencies meet or exceed your role's required proficiency standards."
            )

        gap_items = []
        for g in top_gaps[:5]:
            cur = float(g.get("current_level") if g.get("current_level") is not None else 0.0)
            req = float(g.get("required_level") if g.get("required_level") is not None else 0.0)
            gap = float(g.get("gap") if g.get("gap") is not None else 0.0)
            prio = g.get("priority") or "MEDIUM"
            comp_name = g.get("competency_name") or g.get("competency_code") or "Competency"
            comp_code = g.get("competency_code") or "CODE"
            gap_items.append(
                f"- **{comp_name}** (`{comp_code}`): Current {cur:.1f}/5.0 vs Target {req:.1f}/5.0 "
                f"(Deficit: **{gap:.1f}**, Priority: **{prio}**)"
            )
        gap_summary = "\n".join(gap_items)

        return (
            f"Hello **{name}**. Here is your active capability deficit analysis for your role as **{role}**:\n\n"
            f"### 📊 Your Highest Priority Skill Gaps:\n{gap_summary}\n\n"
            f"> 💡 **Actionable Next Step**: Explore targeted learning in **Recommendations** "
            f"or validate updated skills via an **Adaptive Capability Assessment**."
        )

    def _generate_deterministic_recommendations_response(
        self,
        message: str,
        context_data: Dict[str, Any],
    ) -> str:
        profile = context_data.get("profile", {})
        name = profile.get("full_name", "Officer")
        role = profile.get("role_name", "Official")
        recs = context_data.get("recommendations", [])

        if not recs:
            return (
                f"Hello **{name}**. Based on your current role as **{role}**, "
                f"all mapped competencies are currently at or above required proficiency levels.\n\n"
                f"> 💡 You can explore advanced courses on the [iGOT Karmayogi Portal](https://igotkarmayogi.gov.in)."
            )

        items = []
        for i, r in enumerate(recs[:5], 1):
            provider = r.get("provider", "iGOT")
            title = r.get("title", "Course")
            comp = r.get("competency_code", "COMPETENCY")
            score = float(r.get("score") if r.get("score") is not None else 0.0)
            url = r.get("url")
            link_str = f"[{title}]({url})" if url else f"**{title}**"
            items.append(
                f"{i}. {link_str} ({provider})\n"
                f"   - **Target Competency**: `{comp}`\n"
                f"   - **Relevance Match**: `{score:.2f}`\n"
                f"   - **Source**: Verified {provider} Catalog"
            )

        rec_body = "\n\n".join(items)
        return (
            f"Hello **{name}**. Here are the highest-priority learning interventions recommended for your role as **{role}**:\n\n"
            f"{rec_body}\n\n"
            f"> 💡 **Governance Notice**: Completing learning courses records "
            f"**Supporting Evidence (0.30)** in your capability ledger. "
            f"Your formal competency rating updates after completing an **Authoritative Capability Assessment (0.85)**."
        )

    def _build_recommendation_citations(self, context_data: Dict[str, Any]) -> List[AssistantSourceCitation]:
        citations: List[AssistantSourceCitation] = []
        for r in context_data.get("recommendations", [])[:4]:
            source_id = r.get("source_doc") or f"IGOT-{r.get('resource_id', 'CAT')}"
            citations.append(AssistantSourceCitation(
                source_id=source_id,
                title=f"{r.get('provider', 'iGOT')} — {r.get('title', 'Course')}",
                source_type="IGOT_CATALOG" if (r.get("provider") or "").upper() == "IGOT" else "NSSTA_PROGRAMME",
                url=r.get("url"),
                excerpt=f"Target: {r.get('competency_code')} (Score: {r.get('score')})",
            ))
        return citations

    def _generate_fallback_response(
        self,
        message: str,
        context_data: Dict[str, Any],
        chunks: Optional[List[Tuple[DocumentChunk, float]]] = None,
    ) -> str:
        """Graceful fallback when LLM API is unavailable or times out."""
        # 1. If chunks exist, use them for grounded fallback
        if chunks:
            snippets = []
            for c, _ in chunks[:3]:
                title = getattr(c, "material_title", None) or "Curriculum Document"
                text = (getattr(c, "text", "") or "").strip()[:240]
                if text:
                    snippets.append(f"- **{title}**: {text}...")
            if snippets:
                return (
                    f"### 📚 Verified Curriculum Information:\n\n" + "\n\n".join(snippets) +
                    "\n\n> ℹ️ **Notice**: Generated via offline grounded retrieval from official training materials."
                )

        # 2. Fallback to capability context summary
        return self._generate_deterministic_fallback(message, context_data)

    def _generate_deterministic_fallback(
        self,
        message: str,
        context_data: Dict[str, Any],
    ) -> str:
        profile = context_data.get("profile", {})
        name = profile.get("full_name", "Officer")
        top_gaps = context_data.get("top_gaps", [])
        recs = context_data.get("recommendations", [])

        gap_summary = "\n".join([
            f"- **{g.get('competency_name', g.get('competency_code'))}**: "
            f"Current {g.get('current_level')}/5.0 vs Target {g.get('required_level')}/5.0 "
            f"(Deficit: **{g.get('gap')}**, Priority: **{g.get('priority')}**)"
            for g in top_gaps[:3]
        ]) or "No critical capability deficits identified for your current role."

        rec_summary = ""
        if recs:
            rec_summary = "\n\n### 🎯 Recommended Interventions:\n" + "\n".join([
                f"- **{r.get('title')}** ({r.get('provider')}) — "
                f"Target: `{r.get('competency_code')}` (Match Score: {r.get('score')})"
                for r in recs[:2]
            ])

        return (
            f"Hello **{name}**. Here is your current capability intelligence summary:\n\n"
            f"### 📊 Your Top Skill Gaps:\n{gap_summary}"
            f"{rec_summary}\n\n"
            f"> 💡 **Governance Notice**: Completing learning courses records "
            f"**Supporting Evidence (0.30)** in your capability ledger. "
            f"Your formal competency rating updates after completing an **Authoritative Capability Assessment (0.85)**."
        )

    def _generate_suggested_actions(
        self,
        user_message: str,
        context_data: Dict[str, Any],
    ) -> List[SuggestedAction]:
        actions: List[SuggestedAction] = []
        msg_lower = user_message.lower()

        if any(w in msg_lower for w in ["gap", "deficit", "weakness", "improve", "priority"]):
            actions.append(SuggestedAction(
                action_type="VIEW_GAP",
                label="View My Skill Gaps",
                target_page="Skill Gaps",
            ))
        if any(w in msg_lower for w in ["course", "recommend", "learn", "igot", "nssta", "training"]):
            actions.append(SuggestedAction(
                action_type="START_LEARNING",
                label="Browse Recommended Courses",
                target_page="Recommendations",
            ))
        if any(w in msg_lower for w in ["quiz", "assess", "test", "exam", "validate", "competency"]):
            actions.append(SuggestedAction(
                action_type="TAKE_ASSESSMENT",
                label="Take Capability Quiz",
                target_page="Quizzes",
            ))
        if any(w in msg_lower for w in ["evidence", "proof", "score", "record"]):
            actions.append(SuggestedAction(
                action_type="NAVIGATE",
                label="Check Evidence Ledger",
                target_page="Evidence Ledger",
            ))
        if not actions:
            actions.extend([
                SuggestedAction(
                    action_type="START_LEARNING",
                    label="Browse Recommendations",
                    target_page="Recommendations",
                ),
                SuggestedAction(
                    action_type="TAKE_ASSESSMENT",
                    label="Validate Competency",
                    target_page="Assessments",
                ),
            ])
        return actions
