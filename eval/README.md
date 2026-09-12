# Evaluation harness

```
python eval/evaluate.py
```

Runs the real `MockFallDetector` + `SafetyPipeline` against every scenario in
`scenarios.json` and prints/writes (`results.json`) precision, recall, F1,
false-positive rate, and per-scenario detection latency (in frames).

`scenarios.json` is currently a **synthetic** dataset: hand-authored
per-frame score sequences standing in for real labeled video clips, so the
detection logic, the pipeline, and this evaluation harness could all be
built and tested before recorded footage existed. See
`../docs/TEST_VIDEOS.md` for the plan to replace it with real clips — the
schema (`frames`, `expect_alert`, `expected_event_type`) is designed to stay
the same either way, so `evaluate.py` doesn't need to change.

`tests/test_evaluate.py` runs this same harness as part of the test suite,
so a detector tuning change that regresses a known scenario fails CI
immediately instead of only showing up on demo day.
