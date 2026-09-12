"""Wires a Detector to one or more AlertSinks.

This is the piece integration tests exercise end-to-end: feed in a stream of
FrameFeatures, assert the right Event comes out the other side and lands in
every configured sink.
"""

from __future__ import annotations

from typing import Iterable, List, Optional

from .alerting import AlertSink
from .detector import Detector, FrameFeatures
from .event import Event


class SafetyPipeline:
    def __init__(self, detector: Detector, sinks: Iterable[AlertSink]) -> None:
        self.detector = detector
        self.sinks: List[AlertSink] = list(sinks)

    def ingest(self, features: FrameFeatures) -> Optional[Event]:
        event = self.detector.process_frame(features)
        if event is not None:
            for sink in self.sinks:
                sink.send(event)
        return event

    def ingest_stream(self, stream: Iterable[FrameFeatures]) -> List[Event]:
        """Convenience for feeding a whole clip's worth of frames at once."""
        return [event for f in stream if (event := self.ingest(f)) is not None]
