"""
Single-user baseline benchmark for ShikshaSetu API endpoints.
Runs sequential requests against http://127.0.0.1:8000 to establish baseline latencies.
"""

import time
import requests
import statistics
import json

BASE_URL = "http://127.0.0.1:8000/api/v1"

PERSONAS = {
    "OFFICIAL": ("official@shikshasetu.gov.in", "Password123!"),
    "TRAINER": ("trainer@shikshasetu.gov.in", "Password123!"),
    "ADMIN": ("admin@shikshasetu.gov.in", "Password123!"),
}


def get_token(email: str, password: str) -> str:
    res = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": email, "password": password},
        timeout=10,
    )
    if res.status_code != 200:
        raise RuntimeError(f"Login failed for {email}: {res.status_code} {res.text}")
    return res.json()["access_token"]


def measure_endpoint(method: str, path: str, headers: dict, iterations: int = 10) -> dict:
    durations = []
    statuses = []
    sizes = []
    for _ in range(iterations):
        t0 = time.perf_counter()
        res = requests.request(method, f"{BASE_URL}{path}", headers=headers, timeout=15)
        t1 = time.perf_counter()
        durations.append((t1 - t0) * 1000.0)  # ms
        statuses.append(res.status_code)
        sizes.append(len(res.content))
        time.sleep(0.05)  # brief pause

    durations.sort()
    return {
        "path": path,
        "method": method,
        "status": statuses[0],
        "size_bytes": int(statistics.mean(sizes)),
        "min_ms": round(min(durations), 2),
        "mean_ms": round(statistics.mean(durations), 2),
        "p50_ms": round(statistics.median(durations), 2),
        "p95_ms": round(durations[int(len(durations) * 0.95)], 2),
        "max_ms": round(max(durations), 2),
    }


def main():
    print("=" * 80)
    print("SHIKSHASETU BASELINE ENDPOINT LATENCY BENCHMARK (1 USER / SEQUENTIAL)")
    print("=" * 80)

    # 1. Login Tokens
    print("\n[1] Authenticating Demo Personas...")
    tokens = {}
    for role, (email, pwd) in PERSONAS.items():
        t0 = time.perf_counter()
        tok = get_token(email, pwd)
        t1 = time.perf_counter()
        tokens[role] = tok
        print(f"  + {role:<10} ({email}): authenticated in {(t1 - t0)*1000:.1f} ms")

    # 2. Endpoints by Persona
    tests = [
        # System
        ("SYSTEM", "GET", "/health", {}),

        # Official Learner Workflow
        ("OFFICIAL", "GET", "/users/me", {"Authorization": f"Bearer {tokens['OFFICIAL']}"}),
        ("OFFICIAL", "GET", "/competencies/me", {"Authorization": f"Bearer {tokens['OFFICIAL']}"}),
        ("OFFICIAL", "GET", "/skill-gaps/me", {"Authorization": f"Bearer {tokens['OFFICIAL']}"}),
        ("OFFICIAL", "GET", "/recommendations/me", {"Authorization": f"Bearer {tokens['OFFICIAL']}"}),
        ("OFFICIAL", "GET", "/learning-activities", {"Authorization": f"Bearer {tokens['OFFICIAL']}"}),
        ("OFFICIAL", "GET", "/quizzes/assigned", {"Authorization": f"Bearer {tokens['OFFICIAL']}"}),
        ("OFFICIAL", "GET", "/igot/status", {"Authorization": f"Bearer {tokens['OFFICIAL']}"}),
        ("OFFICIAL", "GET", "/igot/courses", {"Authorization": f"Bearer {tokens['OFFICIAL']}"}),

        # Trainer Workflow
        ("TRAINER", "GET", "/trainer/dashboard", {"Authorization": f"Bearer {tokens['TRAINER']}"}),
        ("TRAINER", "GET", "/trainer/materials", {"Authorization": f"Bearer {tokens['TRAINER']}"}),
        ("TRAINER", "GET", "/trainer/questions", {"Authorization": f"Bearer {tokens['TRAINER']}"}),
        ("TRAINER", "GET", "/trainer/quizzes", {"Authorization": f"Bearer {tokens['TRAINER']}"}),
        ("TRAINER", "GET", "/trainer/learners", {"Authorization": f"Bearer {tokens['TRAINER']}"}),

        # Admin Workflow
        ("ADMIN", "GET", "/admin/dashboard", {"Authorization": f"Bearer {tokens['ADMIN']}"}),
        ("ADMIN", "GET", "/admin/workforce", {"Authorization": f"Bearer {tokens['ADMIN']}"}),
        ("ADMIN", "GET", "/admin/competencies", {"Authorization": f"Bearer {tokens['ADMIN']}"}),
        ("ADMIN", "GET", "/admin/skill-gaps", {"Authorization": f"Bearer {tokens['ADMIN']}"}),
    ]

    print("\n[2] Benchmarking Read Endpoints (10 sequential iterations each)...")
    results = []
    print(f"{'Role':<10} {'Method':<6} {'Endpoint':<35} {'HTTP':<6} {'Mean ms':<10} {'p50 ms':<10} {'p95 ms':<10} {'Max ms':<10}")
    print("-" * 105)

    for role, method, path, headers in tests:
        res = measure_endpoint(method, path, headers, iterations=10)
        res["role"] = role
        results.append(res)
        print(f"{role:<10} {method:<6} {path:<35} {res['status']:<6} {res['mean_ms']:<10.1f} {res['p50_ms']:<10.1f} {res['p95_ms']:<10.1f} {res['max_ms']:<10.1f}")

    # Save results to json for reporting
    out_path = "backend/load_tests/results/baseline_results.json"
    import os
    os.makedirs("backend/load_tests/results", exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved baseline results to {out_path}")


if __name__ == "__main__":
    main()
