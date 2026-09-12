"""Detection logic that turns per-frame features into Events.

This module is intentionally decoupled from any specific pose-estimation or
motion-tracking model. Upstream, a computer-vision model (out of scope for
this repo) watches a camera feed and produces per-frame scores; this module
fuses those scores over time and decides whether they add up to something a
human responder should be notified about.

That boundary matters for the pitch: we are not claiming to diagnose a fall
from pixels ourselves, and we are not making a clinical judgment call -- we
are fusing and debouncing signal so a human isn't paged over one noisy frame.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from datetime import datetime
from typing import Deque, Optional, Protocol

from .event import Event, EventType


@dataclass(frozen=True)
class FrameFeatures:
    """One frame's worth of output from the upstream vision model."""

    camera_id: str
    timestamp: datetime
    fall_score: float
    immobility_score: float
    tracking_confidence: float


def compute_overall_confidence(features: FrameFeatures) -> float:
    """Weighted fusion of the raw signals into one headline confidence score.

    Tracking confidence is included because a "fall" reading from a model that
    has half-lost the subject is worth much less than one with a clean lock.
    """
    return round(
        0.5 * features.fall_score
        + 0.3 * features.immobility_score
        + 0.2 * features.tracking_confidence,
        4,
    )


class Detector(Protocol):
    def process_frame(self, features: FrameFeatures) -> Optional[Event]:
        """Consume one frame of features, optionally emitting an Event."""
        ...


class MockFallDetector:
    """Reference/demo detector: threshold + sustained-window debouncing.

    Requiring the fall/immobility signal to hold for several consecutive
    frames (rather than firing on frame one) is what keeps "bent down to tie
    a shoe" from paging a human responder.
    """

    def __init__(
        self,
        fall_score_threshold: float = 0.7,
        immobility_score_threshold: float = 0.6,
        min_tracking_confidence: float = 0.5,
        min_consecutive_frames: int = 3,
        cooldown_frames: int = 10,
    ) -> None:
        self.fall_score_threshold = fall_score_threshold
        self.immobility_score_threshold = immobility_score_threshold
        self.min_tracking_confidence = min_tracking_confidence
        self.min_consecutive_frames = min_consecutive_frames
        self.cooldown_frames = cooldown_frames

        self._streak: Deque[FrameFeatures] = deque(maxlen=min_consecutive_frames)
        self._frames_since_last_event = cooldown_frames

    def _is_candidate(self, features: FrameFeatures) -> bool:
        return (
            features.tracking_confidence >= self.min_tracking_confidence
            and features.fall_score >= self.fall_score_threshold
            and features.immobility_score >= self.immobility_score_threshold
        )

    def process_frame(self, features: FrameFeatures) -> Optional[Event]:
        self._frames_since_last_event += 1

        if not self._is_candidate(features):
            self._streak.clear()
            return None

        self._streak.append(features)

        sustained = (
            len(self._streak) == self.min_consecutive_frames
            and self._frames_since_last_event >= self.cooldown_frames
        )
        if not sustained:
            return None

        self._frames_since_last_event = 0
        latest = self._streak[-1]
        event = Event(
            camera_id=latest.camera_id,
            event_type=EventType.POSSIBLE_FALL,
            fall_score=latest.fall_score,
            immobility_score=latest.immobility_score,
            tracking_confidence=latest.tracking_confidence,
            overall_confidence=compute_overall_confidence(latest),
            timestamp=latest.timestamp,
        )
        self._streak.clear()
        return event
