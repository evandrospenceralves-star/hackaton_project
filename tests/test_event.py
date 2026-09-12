from datetime import datetime, timezone

import pytest

from safety_layer.event import Event, EventType


def make_event(**overrides):
    defaults = dict(
        camera_id="cam_02",
        event_type=EventType.POSSIBLE_FALL,
        fall_score=0.91,
        immobility_score=0.86,
        tracking_confidence=0.94,
        overall_confidence=0.88,
        timestamp=datetime(2026, 9, 12, 10, 22, 16, tzinfo=timezone.utc),
    )
    defaults.update(overrides)
    return Event(**defaults)


def test_valid_event_round_trips_to_the_documented_wire_format():
    event = make_event()
    data = event.to_dict()

    assert data == {
        "camera_id": "cam_02",
        "event_type": "possible_fall",
        "fall_score": 0.91,
        "immobility_score": 0.86,
        "tracking_confidence": 0.94,
        "overall_confidence": 0.88,
        "timestamp": "2026-09-12T10:22:16+00:00",
    }


@pytest.mark.parametrize("field", ["fall_score", "immobility_score", "tracking_confidence", "overall_confidence"])
def test_score_above_one_is_rejected(field):
    with pytest.raises(ValueError):
        make_event(**{field: 1.5})


@pytest.mark.parametrize("field", ["fall_score", "immobility_score", "tracking_confidence", "overall_confidence"])
def test_score_below_zero_is_rejected(field):
    with pytest.raises(ValueError):
        make_event(**{field: -0.1})


def test_empty_camera_id_is_rejected():
    with pytest.raises(ValueError):
        make_event(camera_id="")


def test_naive_timestamp_is_rejected():
    with pytest.raises(ValueError):
        make_event(timestamp=datetime(2026, 9, 12, 10, 22, 16))
