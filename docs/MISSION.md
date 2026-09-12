# Mission

We're building a safety layer for physical spaces — not a medical diagnostic
system, but an early-warning system that can help a human responder notice
distress sooner.

## What that means in practice

- **We detect signal, we don't diagnose.** The system never claims to know
  someone has been medically harmed. It surfaces a pattern — a possible fall,
  a period of unusual immobility — and routes it to a human who decides what
  to do next.
- **A human is always in the loop.** Every event this system emits is a
  *possible* event (`possible_fall`, `possible_distress`,
  `prolonged_immobility`), scored with an explicit confidence. It is a page
  to a responder, not an automated action.
- **False alarms have a cost too.** A system that cries wolf gets ignored or
  switched off. We debounce and fuse signal specifically so momentary noise
  (bending down, sitting quickly, brief occlusion) doesn't page anyone.
- **Privacy is part of the design, not an afterthought.** The safety layer
  operates on derived scores (fall/immobility/tracking-confidence), not on
  raw video leaving the room, and camera identity is scoped to a `camera_id`
  rather than personal identity.

## Who this is for

Anyone responsible for people in a physical space who can't watch every
camera feed all the time: a small care facility with a lean overnight staff,
a building manager, a family member monitoring an aging relative — anyone
where "a person might be in trouble and nobody would know for several
minutes" is the actual risk we're reducing.

## Non-goals

- Not a replacement for medical alert devices, clinical monitoring, or
  emergency services.
- Not a facial-recognition or identity-tracking product.
- Not a claim of diagnostic accuracy — it is explicitly an *early-warning*
  layer, evaluated on how much sooner a human notices, not on clinical
  ground truth.
