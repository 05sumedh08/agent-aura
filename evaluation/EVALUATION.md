# Agent Aura – Evaluation Guide

This guide provides a reproducible approach to validate the claimed metrics: latency per analysis, batch throughput, and improvement percentage in risk scores after simulated interventions.

## Metrics
- Latency per student analysis (seconds)
- Batch throughput (students per minute)
- Improvement percentage (pre vs. post risk scores)

## Reproducible Script
Run the evaluation harness:
```powershell
S:/Courses/Kaggle/Agent_Aura_GIT/.venv/Scripts/Activate.ps1
S:/Courses/Kaggle/Agent_Aura_GIT/.venv/Scripts/python.exe evaluation/run_evaluation.py
```

Outputs:
- `output/evaluation_latency.json`
- `output/evaluation_improvement.json`

## Method
1. Load student IDs from `data/student_data.csv`.
2. For each student:
   - Call `analyze_student_risk` and time the call.
   - Simulate intervention by reducing risk score by 0.15 (bounded to [0,1]).
   - Track progress via `track_student_progress`.
3. Compute:
   - Average latency and distribution.
   - Total processed and throughput.
   - Improvement percentage per student and overall average.

## Notes
- Deterministic tools ensure repeatable results.
- Replace the simple improvement simulation with real intervention outcomes when available.
- Pair with `/metrics` endpoint for live Prometheus scraping.
