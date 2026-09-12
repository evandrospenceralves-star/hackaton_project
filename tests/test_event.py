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


def test_raw_string_event_type_is_rejected_with_a_clear_error():
    # Constructing an Event straight from wire-format field values (rather than
    # via from_dict) must fail loudly here, not with a confusing AttributeError
    # later on inside to_dict().
    with pytest.raises(ValueError, match="event_type"):
        make_event(event_type="possible_fall")


def test_raw_string_timestamp_is_rejected_with_a_clear_error():
    with pytest.raises(ValueError, match="timestamp"):
        make_event(timestamp="2026-09-12T10:22:16-07:00")


def test_from_dict_round_trips_the_documented_wire_format():
    payload = {
        "camera_id": "cam_02",
        "event_type": "possible_fall",
        "fall_score": 0.91,
        "immobility_score": 0.86,
        "tracking_confidence": 0.94,
        "overall_confidence": 0.88,
        "timestamp": "2026-09-12T10:22:16-07:00",
    }
    event = Event.from_dict(payload)

    assert event.event_type is EventType.POSSIBLE_FALL
    assert event.to_dict() == payload


def test_from_dict_rejects_an_unknown_event_type():
    payload = {
        "camera_id": "cam_02",
        "event_type": "nonsense_event",
        "fall_score": 0.1,
        "immobility_score": 0.1,
        "tracking_confidence": 0.1,
        "overall_confidence": 0.1,
        "timestamp": "2026-09-12T10:22:16-07:00",
    }
    with pytest.raises(ValueError):
        Event.from_dict(payload)


def test_wire_format_matches_the_published_json_schema():
    """Guards against the Event model and schema.json silently drifting apart."""
    import json
    from pathlib import Path

    jsonschema = pytest.importorskip("jsonschema")

    schema = json.loads(
        (Path(__file__).parent.parent / "src" / "safety_layer" / "schema.json").read_text()
    )

    jsonschema.validate(make_event().to_dict(), schema)

    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate({**make_event().to_dict(), "fall_score": 1.5}, schema)

    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate({**make_event().to_dict(), "event_type": "nonsense"}, schema)

    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate({**make_event().to_dict(), "extra_field": "nope"}, schema)
