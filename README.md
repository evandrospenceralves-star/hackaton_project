# Safety Layer

> We're building a safety layer for physical spaces — not a medical
> diagnostic system, but an early-warning system that can help a human
> responder notice distress sooner.

See [`docs/MISSION.md`](docs/MISSION.md) for the full mission and explicit
non-goals, [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for the system
diagram, [`docs/PITCH.md`](docs/PITCH.md) for the pitch/demo script, and
[`docs/DEVPOST.md`](docs/DEVPOST.md) for the submission draft.

## The event contract

The safety layer emits one event format to every downstream consumer
(dashboard, webhook, evaluation harness):

```json
{
  "camera_id": "cam_02",
  "event_type": "possible_fall",
  "fall_score": 0.91,
  "immobility_score": 0.86,
  "tracking_confidence": 0.94,
  "overall_confidence": 0.88,
  "timestamp": "2026-09-12T10:22:16-07:00"
}
```

Defined and validated in [`src/safety_layer/event.py`](src/safety_layer/event.py),
with a matching JSON Schema at
[`src/safety_layer/schema.json`](src/safety_layer/schema.json).

## Quickstart

```bash
python3 -m pip install -r requirements.txt

# run the test suite (unit + integration)
python3 -m pytest -q

# run the evaluation harness against the labeled scenario dataset
python3 eval/evaluate.py
```

## Layout

```
src/safety_layer/   Core package: Event, Detector, SafetyPipeline, AlertSink
eval/                Evaluation harness + labeled scenario dataset
tests/               Unit + end-to-end integration tests
docs/                Mission, architecture, pitch, Devpost draft, test video plan
```

## How it fits together

An upstream vision model (not part of this repo) watches a camera and scores
each frame for fall-likeness, immobility, and tracking confidence. This
repo's `Detector` fuses those scores over a sustained window (so momentary
noise doesn't fire) and, when a real event is decided, hands it to a
`SafetyPipeline`, which delivers it to one or more `AlertSink`s (console,
in-memory for tests, or a webhook into something like Slack). A human
responder always makes the final call — see
[`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for the full diagram and
[`docs/MISSION.md`](docs/MISSION.md) for why that boundary is deliberate.

## Status

Working end-to-end on synthetic data: 22 passing tests, 100% recall / 0
false positives across every scenario in `eval/scenarios.json` (including
known false-positive traps like tying a shoe or sitting down quickly). Next
up is replacing that synthetic dataset with real recorded, labeled footage —
see [`docs/TEST_VIDEOS.md`](docs/TEST_VIDEOS.md).
