"""Integration test for the evaluation harness itself: run it against the
committed scenario dataset and make sure the metrics come back sane and
every hand-labeled scenario is classified correctly. If this test starts
failing after a detector tuning change, either the tuning regressed or the
dataset's expectations need updating -- either way it caught something."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "eval"))

from evaluate import run_evaluation


def test_evaluation_report_shape():
    report = run_evaluation()
    assert "metrics" in report and "results" in report
    metrics = report["metrics"]
    for key in ("precision", "recall", "f1", "false_positive_rate", "total_scenarios"):
        assert key in metrics


def test_every_scenario_is_classified_correctly():
    report = run_evaluation()
    failures = [r["name"] for r in report["results"] if not r["correct"]]
    assert failures == [], f"misclassified scenarios: {failures}"


def test_no_false_positives_on_the_known_tricky_cases():
    report = run_evaluation()
    metrics = report["metrics"]
    assert metrics["false_positives"] == 0
    assert metrics["recall"] == 1.0
