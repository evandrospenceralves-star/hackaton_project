from datetime import datetime, timedelta, timezone

from safety_layer.detector import FrameFeatures, MockFallDetector

BASE_TIME = datetime(2026, 1, 1, tzinfo=timezone.utc)


def frame(i, fall=0.0, immobility=0.0, tracking=0.95):
    return FrameFeatures(
        camera_id="cam_01",
        timestamp=BASE_TIME + timedelta(milliseconds=200 * i),
        fall_score=fall,
        immobility_score=immobility,
        tracking_confidence=tracking,
    )


def test_single_high_scoring_frame_does_not_fire():
    detector = MockFallDetector(min_consecutive_frames=3)
    event = detector.process_frame(frame(0, fall=0.95, immobility=0.9))
    assert event is None


def test_sustained_high_scores_fire_a_possible_fall_event():
    detector = MockFallDetector(min_consecutive_frames=3)
    events = [
        detector.process_frame(frame(i, fall=0.9, immobility=0.85))
        for i in range(3)
    ]
    assert events[0] is None
    assert events[1] is None
    assert events[2] is not None
    assert events[2].event_type.value == "possible_fall"


def test_streak_resets_if_scores_dip():
    detector = MockFallDetector(min_consecutive_frames=3)
    detector.process_frame(frame(0, fall=0.9, immobility=0.85))
    detector.process_frame(frame(1, fall=0.9, immobility=0.85))
    # dip breaks the streak (e.g. sitting down quickly, then settling)
    detector.process_frame(frame(2, fall=0.2, immobility=0.2))
    event = detector.process_frame(frame(3, fall=0.9, immobility=0.85))
    assert event is None  # streak restarted, only 1 frame long so far


def test_low_tracking_confidence_suppresses_alert():
    detector = MockFallDetector(min_consecutive_frames=3, min_tracking_confidence=0.5)
    events = [
        detector.process_frame(frame(i, fall=0.9, immobility=0.85, tracking=0.2))
        for i in range(5)
    ]
    assert all(event is None for event in events)


def test_cooldown_prevents_immediate_re_alert_but_allows_it_later():
    detector = MockFallDetector(min_consecutive_frames=2, cooldown_frames=3)
    idx = 0

    def push(fall, immobility, tracking=0.95):
        nonlocal idx
        event = detector.process_frame(frame(idx, fall, immobility, tracking))
        idx += 1
        return event

    push(0.9, 0.85)
    second = push(0.9, 0.85)
    assert second is not None  # first alert

    # Immediately sustained again -- should be suppressed by cooldown.
    immediate_repeat = push(0.9, 0.85)
    immediate_repeat_2 = push(0.9, 0.85)
    assert immediate_repeat is None
    assert immediate_repeat_2 is None

    # Let the cooldown lapse with quiet frames, then a real second fall fires.
    push(0.1, 0.1)
    later_first = push(0.9, 0.85)
    later_second = push(0.9, 0.85)
    assert later_first is None
    assert later_second is not None
