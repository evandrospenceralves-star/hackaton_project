#!/usr/bin/env python3
"""Run the detector against the evaluation dataset and report accuracy metrics.

    python eval/evaluate.py

This is the "does it actually work" check we point at during the demo/pitch:
precision, recall, false-positive rate, and detection latency (in frames)
across the labeled scenario set.
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent))

from safety_layer.detector import MockFallDetector
from safety_layer.pipeline import SafetyPipeline
from safety_layer.alerting import InMemoryAlertSink

from dataset import ScenarioCase, DEFAULT_MANIFEST


@dataclass
class ScenarioResult:
    name: str
    expect_alert: bool
    got_alert: bool
    detection_latency_frames: Optional[int]
    correct: bool = field(init=False)

    def __post_init__(self) -> None:
        self.correct = self.expect_alert == self.got_alert


def run_scenario(case: ScenarioCase) -> ScenarioResult:
    sink = InMemoryAlertSink()
    pipeline = SafetyPipeline(detector=MockFallDetector(), sinks=[sink])

    latency = None
    for i, frame in enumerate(case.frames):
        event = pipeline.ingest(frame)
        if event is not None and latency is None:
            latency = i

    return ScenarioResult(
        name=case.name,
        expect_alert=case.expect_alert,
        got_alert=len(sink.events) > 0,
        detection_latency_frames=latency,
    )


def summarize(results: List[ScenarioResult]) -> dict:
    true_positives = sum(1 for r in results if r.expect_alert and r.got_alert)
    false_positives = sum(1 for r in results if not r.expect_alert and r.got_alert)
    false_negatives = sum(1 for r in results if r.expect_alert and not r.got_alert)
    true_negatives = sum(1 for r in results if not r.expect_alert and not r.got_alert)

    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) else 1.0
    recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) else 1.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
    false_positive_rate = false_positives / (false_positives + true_negatives) if (false_positives + true_negatives) else 0.0

    latencies = [r.detection_latency_frames for r in results if r.expect_alert and r.got_alert]
    avg_latency = sum(latencies) / len(latencies) if latencies else None

    return {
        "total_scenarios": len(results),
        "true_positives": true_positives,
        "false_positives": false_positives,
        "false_negatives": false_negatives,
        "true_negatives": true_negatives,
        "precision": round(precision, 3),
        "recall": round(recall, 3),
        "f1": round(f1, 3),
        "false_positive_rate": round(false_positive_rate, 3),
        "avg_detection_latency_frames": round(avg_latency, 2) if avg_latency is not None else None,
    }


def run_evaluation(manifest_path: Path = DEFAULT_MANIFEST) -> dict:
    cases = ScenarioCase.load_all(manifest_path)
    results = [run_scenario(case) for case in cases]
    metrics = summarize(results)
    return {
        "metrics": metrics,
        "results": [
            {
                "name": r.name,
                "expect_alert": r.expect_alert,
                "got_alert": r.got_alert,
                "correct": r.correct,
                "detection_latency_frames": r.detection_latency_frames,
            }
            for r in results
        ],
    }


def main() -> int:
    report = run_evaluation()

    print("Scenario results:")
    for r in report["results"]:
        status = "PASS" if r["correct"] else "FAIL"
        print(f"  [{status}] {r['name']:<40} expected_alert={r['expect_alert']!s:<5} "
              f"got_alert={r['got_alert']!s:<5} latency_frames={r['detection_latency_frames']}")

    print("\nMetrics:")
    for key, value in report["metrics"].items():
        print(f"  {key}: {value}")

    out_path = Path(__file__).parent / "results.json"
    out_path.write_text(json.dumps(report, indent=2))
    print(f"\nFull report written to {out_path}")

    any_failed = any(not r["correct"] for r in report["results"])
    return 1 if any_failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
