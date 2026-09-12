"""End-to-end integration test: synthetic frame stream -> detector -> pipeline
-> alert sink, asserting the emitted Event matches the documented wire
format exactly (the JSON contract shared with the dashboard/eval/webhook)."""

from datetime import datetime, timedelta, timezone

from safety_layer.alerting import InMemoryAlertSink
from safety_layer.detector import FrameFeatures, MockFallDetector
from safety_layer.pipeline import SafetyPipeline

BASE_TIME = datetime(2026, 9, 12, 10, 22, 15, tzinfo=timezone.utc)


def build_clip():
    scores = [
        (0.75, 0.65, 0.95),
        (0.88, 0.70, 0.93),
        (0.91, 0.86, 0.94),
    ]
    return [
        FrameFeatures(
            camera_id="cam_02",
            timestamp=BASE_TIME + timedelta(milliseconds=200 * i),
            fall_score=fall,
            immobility_score=immobility,
            tracking_confidence=tracking,
        )
        for i, (fall, immobility, tracking) in enumerate(scores)
    ]


def test_full_pipeline_emits_and_delivers_a_well_formed_event():
    sink = InMemoryAlertSink()
    pipeline = SafetyPipeline(detector=MockFallDetector(min_consecutive_frames=3), sinks=[sink])

    events = pipeline.ingest_stream(build_clip())

    assert len(events) == 1
    assert sink.events == events  # sink actually received what the pipeline emitted

    payload = events[0].to_dict()
    assert set(payload.keys()) == {
        "camera_id",
        "event_type",
        "fall_score",
        "immobility_score",
        "tracking_confidence",
        "overall_confidence",
        "timestamp",
    }
    assert payload["camera_id"] == "cam_02"
    assert payload["event_type"] == "possible_fall"
    assert 0.0 <= payload["overall_confidence"] <= 1.0


def test_pipeline_fans_out_to_multiple_sinks():
    sink_a, sink_b = InMemoryAlertSink(), InMemoryAlertSink()
    pipeline = SafetyPipeline(
        detector=MockFallDetector(min_consecutive_frames=3), sinks=[sink_a, sink_b]
    )

    pipeline.ingest_stream(build_clip())

    assert len(sink_a.events) == 1
    assert len(sink_b.events) == 1
    assert sink_a.events[0].to_dict() == sink_b.events[0].to_dict()


def test_calm_clip_never_alerts():
    sink = InMemoryAlertSink()
    pipeline = SafetyPipeline(detector=MockFallDetector(), sinks=[sink])

    calm_frames = [
        FrameFeatures(
            camera_id="cam_02",
            timestamp=BASE_TIME + timedelta(milliseconds=200 * i),
            fall_score=0.1,
            immobility_score=0.1,
            tracking_confidence=0.95,
        )
        for i in range(10)
    ]
    events = pipeline.ingest_stream(calm_frames)

    assert events == []
    assert sink.events == []
