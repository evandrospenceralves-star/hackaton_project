# Pitch

## Name

**GuardianMesh** — Privacy-preserving AI for recognizing human distress.
*Detect the emergency. Not the identity.*

## One-liner

A safety layer for physical spaces that helps a human responder notice
distress sooner — not a medical diagnosis, an early warning.

## The problem (15s)

Falls and medical emergencies in places like care facilities, group homes,
or a family member's house often go unnoticed for minutes, because there
isn't always a person watching every camera feed at the moment it happens.
Existing options are either expensive dedicated hardware (wearable alert
buttons someone has to remember to press) or nothing at all.

## The solution (20s)

A safety layer that sits between an existing camera's motion/pose signal
and a human responder. When fall-like motion plus sustained immobility is
detected with enough confidence — and tracking is reliable enough to trust —
it emits a `possible_fall` event and pages a responder. It's tuned to *not*
fire on things that look similar but aren't emergencies: tying a shoe,
sitting down quickly, someone resting normally on a couch.

## How it works (20s)

1. An upstream vision model watches the camera and scores each frame for
   fall-likeness, immobility, and how confidently it's tracking the subject.
2. Our safety layer fuses those three signals and requires them to hold for
   several consecutive frames before treating it as real — this is the
   debouncing that keeps the system from crying wolf.
3. When it fires, a structured event goes to whatever the responder
   actually watches — a dashboard, Slack, SMS via webhook.
4. A human decides what happens next. The system never calls anyone but a
   human.

## Why we can back this up, not just claim it (15s)

We built an evaluation harness (`eval/evaluate.py`) that runs the exact
detector code against a labeled scenario set and reports precision, recall,
false-positive rate, and detection latency — not vibes. Today: 100% recall,
0 false positives across the known tricky cases (shoe-tying, quick sitting,
occluded tracking, normal resting). That evaluation dataset is designed to
grow with real recorded test footage, not stay synthetic.

## Demo script (for the video)

1. Open on the name and tagline: "GuardianMesh — privacy-preserving AI for
   recognizing human distress. Detect the emergency. Not the identity."
   Then the mission / problem in one sentence.
2. Show the architecture diagram — camera → vision model → safety layer →
   alert → human. Emphasize: not diagnosing, just noticing sooner.
3. Live run: `python eval/evaluate.py` — walk through 2-3 scenarios (a real
   fall firing, a false-positive case correctly *not* firing).
4. Show the JSON event that comes out (`camera_id`, `fall_score`,
   `immobility_score`, `tracking_confidence`, `overall_confidence`,
   `timestamp`) landing in a console/webhook sink.
5. Close on the mission statement again + what's next.

## What's next / ask

- Replace the synthetic evaluation scenarios with real recorded, labeled
  footage (plan in `docs/TEST_VIDEOS.md`).
- Integrate a real pose/motion model upstream instead of the mock.
- Pilot with a real responder workflow (which dashboard/paging tool they
  actually use) rather than assuming console/Slack.
