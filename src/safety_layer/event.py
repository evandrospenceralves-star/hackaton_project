"""The alert event contract emitted by the safety layer.

This is the single format every downstream consumer (dashboard, SMS bridge,
webhook, eval harness) agrees on. Keeping it in one place means the camera
pipeline, the mock detector used in tests/demos, and the evaluation harness
can never drift out of sync with each other.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum


class EventType(str, Enum):
    POSSIBLE_FALL = "possible_fall"
    POSSIBLE_DISTRESS = "possible_distress"
    PROLONGED_IMMOBILITY = "prolonged_immobility"


_SCORE_FIELDS = (
    "fall_score",
    "immobility_score",
    "tracking_confidence",
    "overall_confidence",
)


@dataclass(frozen=True)
class Event:
    camera_id: str
    event_type: EventType
    fall_score: float
    immobility_score: float
    tracking_confidence: float
    overall_confidence: float
    timestamp: datetime

    def __post_init__(self) -> None:
        if not self.camera_id:
            raise ValueError("camera_id must be a non-empty string")

        for field in _SCORE_FIELDS:
            value = getattr(self, field)
            if not isinstance(value, (int, float)):
                raise ValueError(f"{field} must be numeric, got {type(value)!r}")
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{field} must be within [0.0, 1.0], got {value}")

        if self.timestamp.tzinfo is None:
            raise ValueError(
                "timestamp must be timezone-aware (e.g. include a UTC offset)"
            )

    def to_dict(self) -> dict:
        """Serialize to the exact wire format the demo/eval/dashboard share."""
        data = asdict(self)
        data["event_type"] = self.event_type.value
        data["timestamp"] = self.timestamp.isoformat()
        return data
