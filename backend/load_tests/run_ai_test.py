"""
Separate controlled concurrency test for AI / RAG operations (Phase 12).
Tests Karmayogi AI assistant chat across [1, 2, 5, 10] concurrent requests.
Measures latency, success rate, timeout rate, and external LLM/Gemini behavior.
"""

import time
import requests
import statistics
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_URL = "http://127.0.0.1:8000/api/v1"
TEST_PROMPTS = [
    "What is the required level for STAT_SAMPLING in MoSPI?",
    "Recommend learning modules to close my statistical sampling skill gap.",
    "Explain the difference between authoritative and self-reported competency evidence.",
    "What are the key responsibilities of a Statistical Officer under NDQS?",
]


def get_official_token() -> str:
    res = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": "official@shikshasetu.gov.in", "password": "Password123!"},
        timeout=10,
    )
    if res.status_code != 200:
        raise RuntimeError(f"Login failed: {res.status_code} {res.text}")
    return res.json()["access_token"]


def send_ai_chat_request(token: str, message: str, timeout: int = 30) -> dict:
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    t0 = time.perf_counter()
    status = 0
    error_msg = None
    response_length = 0

    try:
        res = requests.post(
            f"{BASE_URL}/assistant/chat",
            json={"message": message},
            headers=headers,
            timeout=timeout,
        )
        t1 = time.perf_counter()
        status = res.status_code
        if status == 200:
            data = res.json()
            reply = data.get("reply", "")
            response_length = len(reply)
        else:
            error_msg = f"HTTP {status}: {res.text[:100]}"
    except requests.exceptions.Timeout:
        t1 = time.perf_counter()
        status = 408
        error_msg = "Client request timed out"
    except Exception as exc:
        t1 = time.perf_counter()
        status = 500
        error_msg = str(exc)[:100]

    return {
        "duration_ms": round((t1 - t0) * 1000.0, 1),
        "status": status,
        "success": status == 200,
        "response_length": response_length,
        "error": error_msg,
    }


def run_ai_concurrency_level(concurrency: int, total_requests: int = 10) -> dict:
    print(f"\n[AI Test] Testing Concurrency: {concurrency} (Total Requests: {total_requests})...")
    token = get_official_token()

    results = []
    t_start = time.perf_counter()

    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = []
        for i in range(total_requests):
            prompt = TEST_PROMPTS[i % len(TEST_PROMPTS)]
            futures.append(executor.submit(send_ai_chat_request, token, prompt, 30))

        for f in as_completed(futures):
            results.append(f.result())

    t_end = time.perf_counter()
    total_time = t_end - t_start

    durations = [r["duration_ms"] for r in results]
    successes = [r for r in results if r["success"]]
    failures = [r for r in results if not r["success"]]
    durations.sort()

    p50 = statistics.median(durations) if durations else 0.0
    p95 = durations[int(len(durations) * 0.95)] if durations else 0.0
    max_d = max(durations) if durations else 0.0
    mean_d = statistics.mean(durations) if durations else 0.0

    summary = {
        "concurrency": concurrency,
        "total_requests": total_requests,
        "success_count": len(successes),
        "failure_count": len(failures),
        "error_pct": round(len(failures) / total_requests * 100.0, 1),
        "throughput_rps": round(total_requests / total_time, 2),
        "mean_latency_ms": round(mean_d, 1),
        "p50_latency_ms": round(p50, 1),
        "p95_latency_ms": round(p95, 1),
        "max_latency_ms": round(max_d, 1),
        "errors": [f["error"] for f in failures[:3]],
    }

    print(f"  -> Success: {summary['success_count']}/{total_requests}, Errors: {summary['error_pct']}%")
    print(f"  -> Throughput: {summary['throughput_rps']} RPS")
    print(f"  -> Latency: mean={summary['mean_latency_ms']}ms, p50={summary['p50_latency_ms']}ms, p95={summary['p95_latency_ms']}ms, max={summary['max_latency_ms']}ms")

    return summary


def main():
    print("=" * 80)
    print("SHIKSHASETU AI / RAG CONTROLLED CONCURRENCY BENCHMARK (PHASE 12)")
    print("=" * 80)

    ai_levels = [1, 2, 5, 10]
    results = []

    for c in ai_levels:
        res = run_ai_concurrency_level(concurrency=c, total_requests=max(c * 2, 6))
        results.append(res)
        time.sleep(2)  # pause between levels to avoid immediate burst limits

    out_file = "backend/load_tests/results/ai_rag_results.json"
    with open(out_file, "w") as f:
        json.dump(results, f, indent=2)

    print("\n" + "=" * 80)
    print("AI / RAG CONCURRENCY SUMMARY TABLE")
    print("=" * 80)
    print(f"{'Concurrency':<12} {'Requests':<10} {'RPS':<8} {'Error %':<9} {'Mean ms':<10} {'p50 ms':<10} {'p95 ms':<10} {'Max ms':<10}")
    print("-" * 80)
    for r in results:
        print(f"{r['concurrency']:<12} {r['total_requests']:<10} {r['throughput_rps']:<8.2f} {r['error_pct']:<9.1f} {r['mean_latency_ms']:<10.1f} {r['p50_latency_ms']:<10.1f} {r['p95_latency_ms']:<10.1f} {r['max_latency_ms']:<10.1f}")
    print(f"\nAI results saved to {out_file}")


if __name__ == "__main__":
    main()
