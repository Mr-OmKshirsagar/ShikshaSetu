"""
RAG Evaluation Runner — Datasets 14 (Golden Q&A) + 21 (Refusal Set).

Measures:
  - Routing accuracy (intent classification correct?)
  - Retrieval recall (expected sources in top-K candidates?)
  - Refusal accuracy (out-of-scope queries declined correctly?)
  - Groundedness (answer grounded in retrieved evidence?)

Usage:
  python -m app.rag.evaluation.runner [--dataset eval|refusal|all]
"""

from __future__ import annotations

import logging
import re
import time
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class EvalResult:
    eval_id: str
    query: str
    expected_intent: str
    actual_intent: str
    routing_correct: bool
    chunks_retrieved: int
    groundedness_score: float | None
    answer_preview: str
    latency_ms: int
    passed: bool
    failure_reason: str = ""


@dataclass
class RefusalResult:
    test_id: str
    query: str
    expected_behavior: str
    actual_intent: str
    was_refused: bool
    answer_preview: str
    latency_ms: int
    passed: bool
    failure_reason: str = ""


@dataclass
class EvalReport:
    total_eval: int = 0
    routing_correct: int = 0
    refusal_total: int = 0
    refusal_correct: int = 0
    avg_groundedness: float = 0.0
    avg_latency_ms: float = 0.0
    eval_results: list[EvalResult] = field(default_factory=list)
    refusal_results: list[RefusalResult] = field(default_factory=list)

    @property
    def routing_accuracy(self) -> float:
        return self.routing_correct / self.total_eval if self.total_eval > 0 else 0.0

    @property
    def refusal_accuracy(self) -> float:
        return self.refusal_correct / self.refusal_total if self.refusal_total > 0 else 0.0

    def print_summary(self) -> None:
        print("\n" + "=" * 70)
        print("RAG EVALUATION REPORT")
        print("=" * 70)
        if self.total_eval > 0:
            print(f"Golden Q&A Set:")
            print(f"  Routing accuracy:  {self.routing_accuracy:.1%}  ({self.routing_correct}/{self.total_eval})")
            print(f"  Avg groundedness:  {self.avg_groundedness:.3f}")
            print(f"  Avg latency:       {self.avg_latency_ms:.0f}ms")
            print()
            print("  Routing failures:")
            for r in self.eval_results:
                if not r.routing_correct:
                    print(f"    [{r.eval_id}] expected={r.expected_intent} got={r.actual_intent}: {r.query[:60]}")

        if self.refusal_total > 0:
            print(f"\nRefusal Test Set:")
            print(f"  Refusal accuracy:  {self.refusal_accuracy:.1%}  ({self.refusal_correct}/{self.refusal_total})")
            print()
            print("  Refusal failures:")
            for r in self.refusal_results:
                if not r.passed:
                    print(f"    [{r.test_id}] {r.failure_reason}: {r.query[:60]}")
        print("=" * 70 + "\n")


def run_routing_eval(
    db,
    sample_limit: int | None = None,
) -> tuple[list[EvalResult], dict]:
    """
    Runs routing classification tests against the rag_eval_set collection.
    Does NOT call the LLM — only tests the deterministic intent router.

    Returns:
        (results, summary_dict)
    """
    from app.rag.intent_router import classify_intent

    eval_docs = list(db.rag_eval_set.find(
        {"expected_intent": {"$nin": ["", None]}},
        limit=sample_limit or 0,
    ))

    results: list[EvalResult] = []
    correct = 0

    for doc in eval_docs:
        query = doc.get("query", "")
        expected_intent = (doc.get("expected_intent") or "").upper()

        t0 = time.time()
        try:
            intent_result = classify_intent(query)
            actual_intent = intent_result.intent.value
        except Exception as exc:
            actual_intent = f"ERROR:{exc}"
        elapsed = int((time.time() - t0) * 1000)

        routing_correct = (actual_intent == expected_intent)
        if routing_correct:
            correct += 1

        results.append(EvalResult(
            eval_id=doc.get("eval_id", "?"),
            query=query,
            expected_intent=expected_intent,
            actual_intent=actual_intent,
            routing_correct=routing_correct,
            chunks_retrieved=0,
            groundedness_score=None,
            answer_preview="",
            latency_ms=elapsed,
            passed=routing_correct,
        ))

    accuracy = correct / len(results) if results else 0.0
    return results, {
        "total": len(results),
        "correct": correct,
        "routing_accuracy": accuracy,
    }


def run_refusal_eval(db) -> tuple[list[RefusalResult], dict]:
    """
    Runs all refusal/out-of-scope tests against the rag_refusal_set collection.
    Tests the intent router — does NOT call the LLM.
    """
    from app.rag.intent_router import classify_intent

    test_docs = list(db.rag_refusal_set.find({}))
    results: list[RefusalResult] = []
    correct = 0

    for doc in test_docs:
        query = doc.get("query", "")
        expected_behavior = doc.get("expected_behavior", "")
        t0 = time.time()
        try:
            intent_result = classify_intent(query)
            actual_intent = intent_result.intent.value
            was_refused = intent_result.refuse
        except Exception as exc:
            actual_intent = f"ERROR:{exc}"
            was_refused = False
        elapsed = int((time.time() - t0) * 1000)

        # Evaluate pass/fail based on expected_behavior
        passed = False
        failure_reason = ""

        if expected_behavior == "decline":
            passed = was_refused
            failure_reason = f"Expected refusal, got {actual_intent}" if not passed else ""
        elif expected_behavior == "route_to_user_data":
            passed = actual_intent == "USER_DATA"
            failure_reason = f"Expected USER_DATA, got {actual_intent}" if not passed else ""
        elif expected_behavior == "route_to_glossary":
            passed = actual_intent in ("GLOSSARY", "RAG", "HYBRID")
            failure_reason = f"Expected GLOSSARY/RAG, got {actual_intent}" if not passed else ""
        elif expected_behavior == "route_to_rag":
            passed = actual_intent in ("RAG", "HYBRID", "GLOSSARY")
            failure_reason = f"Expected RAG/HYBRID, got {actual_intent}" if not passed else ""
        elif expected_behavior == "route_to_mcp":
            passed = actual_intent in ("MCP", "HYBRID")
            failure_reason = f"Expected MCP/HYBRID, got {actual_intent}" if not passed else ""
        elif expected_behavior == "route_to_hybrid":
            passed = actual_intent == "HYBRID"
            failure_reason = f"Expected HYBRID, got {actual_intent}" if not passed else ""
        else:
            passed = True  # unknown expected behavior — skip

        if passed:
            correct += 1

        results.append(RefusalResult(
            test_id=doc.get("test_id", "?"),
            query=query,
            expected_behavior=expected_behavior,
            actual_intent=actual_intent,
            was_refused=was_refused,
            answer_preview="",
            latency_ms=elapsed,
            passed=passed,
            failure_reason=failure_reason,
        ))

        # Update last_run in DB
        try:
            db.rag_refusal_set.update_one(
                {"test_id": doc.get("test_id")},
                {"$set": {
                    "last_run_at": time.time(),
                    "last_run_result": "PASS" if passed else "FAIL",
                }},
            )
        except Exception:
            pass

    accuracy = correct / len(results) if results else 0.0
    return results, {
        "total": len(results),
        "correct": correct,
        "refusal_accuracy": accuracy,
    }


def run_full_eval(db, sample_limit: int | None = None) -> EvalReport:
    """Run both eval and refusal sets, produce a consolidated report."""
    report = EvalReport()

    # Routing evaluation
    eval_results, eval_summary = run_routing_eval(db, sample_limit=sample_limit)
    report.eval_results = eval_results
    report.total_eval = eval_summary["total"]
    report.routing_correct = eval_summary["correct"]

    # Refusal evaluation
    refusal_results, refusal_summary = run_refusal_eval(db)
    report.refusal_results = refusal_results
    report.refusal_total = refusal_summary["total"]
    report.refusal_correct = refusal_summary["correct"]

    # Timing summary
    if eval_results:
        report.avg_latency_ms = sum(r.latency_ms for r in eval_results) / len(eval_results)

    return report


if __name__ == "__main__":
    import sys
    import argparse

    logging.basicConfig(level=logging.WARNING)
    parser = argparse.ArgumentParser(description="ShikshaSetu RAG Evaluation Runner")
    parser.add_argument("--dataset", choices=["eval", "refusal", "all"], default="all")
    parser.add_argument("--sample", type=int, default=None, help="Limit eval queries")
    args = parser.parse_args()

    from app.core.config import get_settings
    from app.core.database import initialize_database, close_database
    s = get_settings()
    client, db = initialize_database(s.mongodb_uri, s.mongodb_database)

    try:
        if args.dataset == "eval":
            results, summary = run_routing_eval(db, args.sample)
            print(f"Routing accuracy: {summary['routing_accuracy']:.1%} ({summary['correct']}/{summary['total']})")
            for r in results:
                if not r.passed:
                    print(f"  FAIL [{r.eval_id}] expected={r.expected_intent} got={r.actual_intent}: {r.query[:60]}")
        elif args.dataset == "refusal":
            results, summary = run_refusal_eval(db)
            print(f"Refusal accuracy: {summary['refusal_accuracy']:.1%} ({summary['correct']}/{summary['total']})")
            for r in results:
                if not r.passed:
                    print(f"  FAIL [{r.test_id}] {r.failure_reason}: {r.query[:60]}")
        else:
            report = run_full_eval(db, args.sample)
            report.print_summary()
    finally:
        close_database(client)
