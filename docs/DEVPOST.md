# Devpost submission draft

> Fill in the bracketed placeholders (team name, hackathon name, links) before
> submitting. Section headings match Devpost's standard submission form.

## Project name

[Project name]

## Elevator pitch

A safety layer for physical spaces — not a medical diagnostic system, but an
early-warning system that helps a human responder notice distress sooner.

## Inspiration

Falls and medical emergencies often go unnoticed for critical minutes simply
because no one happened to be watching at the right moment. We wanted to
build something that sits on top of existing cameras and turns "nobody was
watching" into "a person got paged in seconds" — without pretending to be a
medical device, and without paging someone every time an occupant bends down
to tie a shoe.

## What it does

The safety layer takes per-frame signal from an upstream vision model
(fall-likeness, immobility, tracking confidence) and fuses it over time. Once
the signal is strong *and sustained* — not a single noisy frame — it emits a
structured event:

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

That event is routed to a human responder (console, dashboard, or webhook
into Slack/paging tools). It never takes action on its own — a person always
makes the call.

## How we built it

- **Python** core: a validated `Event` model (with a matching JSON Schema),
  a `Detector` interface with a threshold + sustained-window + cooldown
  reference implementation (`MockFallDetector`), a `SafetyPipeline` that
  wires detection to pluggable alert sinks (console / in-memory / webhook).
- **Evaluation harness**: a labeled scenario dataset (`eval/scenarios.json`)
  covering both true emergencies and known false-positive traps (tying a
  shoe, sitting down quickly, occluded tracking, resting normally), replayed
  through the real detector code (`eval/evaluate.py`) to compute precision,
  recall, F1, false-positive rate, and detection latency.
- **Integration tests** (`tests/`) exercising the full pipeline end-to-end,
  not just unit-level pieces, so a change to the detector's tuning is caught
  immediately if it regresses a known scenario.

## Challenges we ran into

- Tuning debouncing so real falls are still caught quickly (few-frame
  latency) while momentary noise (bending, sitting) doesn't fire — the
  fix was requiring a sustained multi-frame window plus a tracking-confidence
  floor, rather than a single-frame threshold.
- Deciding where the "safety layer" boundary should sit relative to the
  computer-vision model, so the parts we could build and evaluate in the
  hackathon timeframe (fusion, debouncing, alert routing, evaluation) are
  cleanly separated from the parts that need a real model and real footage
  (pose/motion estimation itself).

## Accomplishments that we're proud of

- A working, tested pipeline you can run end-to-end (`pytest`,
  `python eval/evaluate.py`) with **zero false positives** across every known
  tricky scenario in our evaluation set.
- A clear mission and explicit non-goals (not diagnostic, not a replacement
  for emergency services, human always in the loop) baked into both the docs
  and the design of the event schema itself.

## What we learned

Precision without recall isn't safety, and recall without precision isn't
usable — the debouncing/cooldown logic exists because either failure mode
kills trust in a system like this.

## What's next for [Project name]

- Swap the synthetic evaluation dataset for real recorded, labeled test
  footage (see `docs/TEST_VIDEOS.md` for the recording plan).
- Integrate an actual pose/motion-estimation model upstream of the safety
  layer.
- Pilot the alerting integration with a real responder workflow.

## Built with

python, pytest, mermaid (architecture diagram)
