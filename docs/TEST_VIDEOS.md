# Test video plan

Goal: replace the synthetic scenarios in `eval/scenarios.json` with real
recorded, labeled clips, and produce the demo footage for the pitch video.
This doc is the checklist for the "product/demo" role.

## Before recording anything: consent and privacy

- Only record people who have explicitly consented to be filmed for this
  demo, and are aware falls will be simulated (use trained actors/teammates,
  not bystanders).
- Don't record real bystanders, minors, or anyone in a real care setting.
- If any footage is shared publicly (Devpost video, README), blur faces or
  use actors comfortable being identifiable, and say in the video that falls
  are staged/simulated.
- Store raw footage somewhere access-controlled; don't commit raw video into
  this git repo (see `.gitignore` / keep it out entirely — link to external
  storage instead).

## Scenario matrix to record

Each row should become one labeled clip. Mirror the structure already in
`eval/scenarios.json` (`expect_alert`, `expected_event_type`) so labels are
consistent between synthetic and real data.

| Scenario | Should alert? | Why it's in the set |
|---|---|---|
| Clear fall, good lighting, camera facing subject | Yes | Baseline true positive |
| Fall at a bad camera angle (side-on, partial view) | Yes | Stress-tests tracking confidence under a harder angle |
| Slow collapse / gradual slump against furniture | Yes | Not all falls are sudden |
| Fall partially behind furniture (occluded) | Depends — see note | Tests whether low tracking confidence correctly suppresses a shaky auto-alert |
| Person bends down to tie a shoe / pick something up | No | Known false-positive trap (already in synthetic set) |
| Person sits down on a couch quickly | No | Known false-positive trap (already in synthetic set) |
| Person lies down normally to rest/nap | No | Must not be treated as a fall just because they're immobile |
| Two people in frame, one falls | Yes | Tests that per-person tracking doesn't get confused by a second body |
| Low light / nighttime | Depends | Tests degraded tracking confidence, not a new event type |
| Fall, recovers, walks away, falls again later | Yes (twice) | Tests cooldown behavior doesn't suppress a second real event |

> Note on the occluded case: the current tuning intentionally does **not**
> auto-alert when tracking confidence is too low (see
> `occluded_tracking_low_confidence` in `eval/scenarios.json`) — the product
> stance is "don't page a human on a low-confidence guess," so a real
> recorded occluded-fall clip is expected to *not* fire under the current
> thresholds unless tracking confidence recovers. If a real clip disagrees,
> that's a genuine product conversation (do we lower the confidence floor,
> or accept the miss?), not a bug to silently patch around.

## Recording checklist per clip

- [ ] Consent obtained from everyone on camera
- [ ] Camera ID assigned (`cam_01`, `cam_02`, ...) and noted
- [ ] Lighting/angle noted
- [ ] Ground-truth label recorded: `expect_alert` (true/false),
      `expected_event_type`
- [ ] Clip trimmed to the relevant window (a few seconds before/after the
      event)
- [ ] Added to the eval manifest (see below) once features are extracted

## Turning a recorded clip into an eval scenario

`eval/scenarios.json` expects per-frame `fall_score` / `immobility_score` /
`tracking_confidence`, which in a real system come from the upstream pose/
motion model (out of scope for this repo — see `docs/ARCHITECTURE.md`).
Until that model is integrated:

1. Record the clip.
2. Hand-annotate (or run through whatever pose model becomes available)
   approximate per-frame scores at a fixed interval (the harness assumes
   ~5 fps; see `FRAME_INTERVAL` in `eval/dataset.py`).
3. Add a new entry to `eval/scenarios.json` with those scores and the
   ground-truth label.
4. Run `python eval/evaluate.py` — it should classify the new scenario the
   same way a human watching the clip would.

## Demo video (for Devpost submission)

Separate from the labeled evaluation clips: a single short (~2-3 min) video
following the demo script in `docs/PITCH.md` — problem, architecture, live
`eval/evaluate.py` run, a sample event payload, close. This is the video
that goes on the actual Devpost submission page, not the evaluation dataset.
