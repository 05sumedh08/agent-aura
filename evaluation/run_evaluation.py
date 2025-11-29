import time
import json
import os
from agent_aura.tools import (
    analyze_student_risk,
    track_student_progress,
)

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "student_data.csv")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def load_student_ids(path):
    ids = []
    with open(path, "r", encoding="utf-8") as f:
        next(f)
        for line in f:
            sid = line.split(",")[0].strip()
            if sid:
                ids.append(sid)
    return ids


def main():
    student_ids = load_student_ids(DATA_PATH)
    latencies = []
    improvements = []
    total_start = time.time()

    for sid in student_ids:
        # Measure analysis latency
        start = time.time()
        risk = analyze_student_risk(sid)
        latency = time.time() - start
        latencies.append(latency)

        # Simulate intervention improvement (naive)
        pre = float(risk.get("risk_score", 0.0) or 0.0)
        improved = max(pre - 0.15, 0.0)
        track_student_progress(sid, risk.get("risk_level", "LOW"), pre, risk.get("student_name", ""))
        track_student_progress(sid, risk.get("risk_level", "LOW"), improved, risk.get("student_name", ""), notes="Simulated intervention")

        if pre > 0.0:
            improvements.append((pre - improved) / pre * 100.0)
        else:
            improvements.append(0.0)

    total_time = time.time() - total_start
    throughput_spm = len(student_ids) / (total_time / 60.0) if total_time > 0 else 0.0

    results_latency = {
        "total_students": len(student_ids),
        "avg_latency_sec": sum(latencies) / len(latencies) if latencies else 0.0,
        "min_latency_sec": min(latencies) if latencies else 0.0,
        "max_latency_sec": max(latencies) if latencies else 0.0,
        "throughput_students_per_min": throughput_spm,
        "total_time_sec": total_time,
    }

    results_improvement = {
        "avg_improvement_pct": sum(improvements) / len(improvements) if improvements else 0.0,
        "min_improvement_pct": min(improvements) if improvements else 0.0,
        "max_improvement_pct": max(improvements) if improvements else 0.0,
    }

    with open(os.path.join(OUTPUT_DIR, "evaluation_latency.json"), "w", encoding="utf-8") as f:
        json.dump(results_latency, f, indent=2)

    with open(os.path.join(OUTPUT_DIR, "evaluation_improvement.json"), "w", encoding="utf-8") as f:
        json.dump(results_improvement, f, indent=2)

    print("Latency:", json.dumps(results_latency, indent=2))
    print("Improvement:", json.dumps(results_improvement, indent=2))


if __name__ == "__main__":
    main()
