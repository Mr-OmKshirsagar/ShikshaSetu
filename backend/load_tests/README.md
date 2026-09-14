# ShikshaSetu Controlled Concurrency & Load Testing Suite

This directory contains the automated performance and capacity testing suite for the ShikshaSetu backend.

## Architecture

- **`locustfile.py`**: Declares realistic, weighted user workflows (70% Official, 20% Trainer, 10% Admin) with simulated user think time (1–3 seconds).
- **`run_baseline.py`**: Executes sequential single-user benchmarks across 18 read endpoints to establish initial latency baselines.
- **`results/`**: Output directory for CSV logs, JSON metrics, and latency percentiles.

## Execution

To run a headless load test for 50 concurrent users over 2 minutes:
```bash
locust -f backend/load_tests/locustfile.py --headless -u 50 -r 10 -t 2m --host http://127.0.0.1:8000 --csv backend/load_tests/results/load_50
```
