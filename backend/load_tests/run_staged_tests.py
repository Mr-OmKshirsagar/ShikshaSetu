"""
Automated staged concurrency runner for ShikshaSetu.
Runs Locust headless across [10, 25, 50, 100, 250, 500] concurrent users.
Collects and logs throughput, error rate, p50, p90, p95, p99, and system resource metrics.
Stops escalation if the system becomes UNSTABLE.
"""

import os
import sys
import time
import csv
import json
import subprocess
import psutil

LEVELS = [
    {"users": 10, "spawn_rate": 2, "duration": "60s"},
    {"users": 25, "spawn_rate": 5, "duration": "60s"},
    {"users": 50, "spawn_rate": 10, "duration": "60s"},
    {"users": 100, "spawn_rate": 20, "duration": "60s"},
    {"users": 250, "spawn_rate": 25, "duration": "60s"},
    {"users": 500, "spawn_rate": 50, "duration": "60s"},
]

RESULTS_DIR = "backend/load_tests/results"
LOCUSTFILE = "backend/load_tests/locustfile.py"
HOST = "http://127.0.0.1:8000"


def evaluate_status(failure_pct: float, p95_ms: float) -> str:
    if failure_pct > 5.0 or p95_ms > 5000:
        return "UNSTABLE"
    elif failure_pct >= 1.0 or p95_ms >= 2000:
        return "DEGRADED"
    else:
        return "STABLE"


def parse_locust_stats(csv_prefix: str) -> dict:
    stats_file = f"{csv_prefix}_stats.csv"
    if not os.path.exists(stats_file):
        return {}

    with open(stats_file, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("Name") == "Aggregated":
                req_count = int(row.get("Request Count", 0))
                fail_count = int(row.get("Failure Count", 0))
                rps = float(row.get("Requests/s", 0.0))
                p50 = float(row.get("50%", 0.0))
                p90 = float(row.get("90%", 0.0))
                p95 = float(row.get("95%", 0.0))
                p99 = float(row.get("99%", 0.0))
                max_lat = float(row.get("Max Response Time", 0.0))
                fail_pct = (fail_count / req_count * 100.0) if req_count > 0 else 0.0

                return {
                    "total_requests": req_count,
                    "successful_requests": req_count - fail_count,
                    "failed_requests": fail_count,
                    "error_pct": round(fail_pct, 2),
                    "rps": round(rps, 2),
                    "p50_ms": round(p50, 1),
                    "p90_ms": round(p90, 1),
                    "p95_ms": round(p95, 1),
                    "p99_ms": round(p99, 1),
                    "max_ms": round(max_lat, 1),
                }
    return {}


def run_stage(users: int, spawn_rate: int, duration: str) -> dict:
    csv_prefix = os.path.join(RESULTS_DIR, f"after_stage_{users}")
    stdout_log = f"{csv_prefix}_stdout.log"
    stderr_log = f"{csv_prefix}_stderr.log"

    cmd = [
        sys.executable,
        "-m", "locust",
        "-f", LOCUSTFILE,
        "--headless",
        "-u", str(users),
        "-r", str(spawn_rate),
        "-t", duration,
        "--host", HOST,
        "--csv", csv_prefix,
        "--only-summary",
    ]

    print(f"\n[{time.strftime('%H:%M:%S')}] Starting Stage: {users} Concurrent Users (Spawn: {spawn_rate}/s, Duration: {duration})...")

    # Monitor CPU and RAM during execution
    cpu_samples = []
    ram_samples = []

    with open(stdout_log, "w", encoding="utf-8") as out_f, open(stderr_log, "w", encoding="utf-8") as err_f:
        proc = subprocess.Popen(cmd, stdout=out_f, stderr=err_f)

        while proc.poll() is None:
            cpu_samples.append(psutil.cpu_percent(interval=None))
            ram_samples.append(psutil.virtual_memory().percent)
            time.sleep(1.0)

    avg_cpu = round(sum(cpu_samples) / max(len(cpu_samples), 1), 1)
    max_cpu = round(max(cpu_samples) if cpu_samples else 0.0, 1)
    avg_ram = round(sum(ram_samples) / max(len(ram_samples), 1), 1)

    parsed = parse_locust_stats(csv_prefix)
    if not parsed:
        print("  WARNING: Could not parse Locust CSV statistics!")
        return {"users": users, "status": "UNKNOWN"}

    status = evaluate_status(parsed["error_pct"], parsed["p95_ms"])
    parsed.update({
        "users": users,
        "status": status,
        "avg_cpu_pct": avg_cpu,
        "max_cpu_pct": max_cpu,
        "avg_ram_pct": avg_ram,
    })

    print(f"  -> Total Requests: {parsed['total_requests']}, RPS: {parsed['rps']}")
    print(f"  -> Errors: {parsed['failed_requests']} ({parsed['error_pct']}%)")
    print(f"  -> Latency: p50={parsed['p50_ms']}ms, p90={parsed['p90_ms']}ms, p95={parsed['p95_ms']}ms, p99={parsed['p99_ms']}ms, Max={parsed['max_ms']}ms")
    print(f"  -> System: CPU avg={avg_cpu}%, max={max_cpu}% | RAM avg={avg_ram}%")
    print(f"  -> Evaluation: **{status}**")

    return parsed


def main():
    print("=" * 85)
    print("SHIKSHASETU CONTROLLED CONCURRENCY & CAPACITY STAGE RUNNER (AFTER CACHING)")
    print("=" * 85)

    os.makedirs(RESULTS_DIR, exist_ok=True)
    all_results = []

    for cfg in LEVELS:
        res = run_stage(cfg["users"], cfg["spawn_rate"], cfg["duration"])
        all_results.append(res)

        # Stop escalation if unstable
        if res.get("status") == "UNSTABLE":
            print(f"\n[ALERT] Stopping escalation: Level {cfg['users']} reached UNSTABLE status.")
            break

        # Brief cool-down between stages
        print("  Cooldown: 10s...")
        time.sleep(10)

    # Save summary
    summary_file = os.path.join(RESULTS_DIR, "after_caching_summary.json")
    with open(summary_file, "w") as f:
        json.dump(all_results, f, indent=2)

    print("\n" + "=" * 85)
    print("AFTER CACHING STAGED TEST SUMMARY TABLE")
    print("=" * 85)
    print(f"{'Users':<8} {'Requests':<10} {'RPS':<8} {'Error %':<9} {'p50 ms':<9} {'p90 ms':<9} {'p95 ms':<9} {'p99 ms':<9} {'Status':<10}")
    print("-" * 85)
    for r in all_results:
        print(f"{r.get('users', 0):<8} {r.get('total_requests', 0):<10} {r.get('rps', 0.0):<8.1f} {r.get('error_pct', 0.0):<9.2f} {r.get('p50_ms', 0):<9.1f} {r.get('p90_ms', 0):<9.1f} {r.get('p95_ms', 0):<9.1f} {r.get('p99_ms', 0):<9.1f} {r.get('status', 'N/A'):<10}")
    print(f"\nResults saved to {summary_file}")


if __name__ == "__main__":
    main()
