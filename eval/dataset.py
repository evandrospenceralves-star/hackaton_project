"""Loader for the evaluation scenario manifest (eval/scenarios.json).

Swapping this synthetic manifest for one built from real recorded/labeled
clips (see docs/TEST_VIDEOS.md) does not require changing evaluate.py: keep
the same {frames: [{fall_score, immobility_score, tracking_confidence}, ...],
expect_alert, expected_event_type} shape and point ScenarioCase.load_all at
the new file.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List, Optional

from safety_layer.detector import FrameFeatures

DEFAULT_MANIFEST = Path(__file__).parent / "scenarios.json"
FRAME_INTERVAL = timedelta(milliseconds=200)  # 5 fps feature stream


@dataclass
class ScenarioCase:
    name: str
    description: str
    camera_id: str
    expect_alert: bool
    expected_event_type: Optional[str]
    frames: List[FrameFeatures]

    @staticmethod
    def load_all(manifest_path: Path = DEFAULT_MANIFEST) -> List["ScenarioCase"]:
        raw = json.loads(manifest_path.read_text())
        base_time = datetime(2026, 1, 1, tzinfo=timezone.utc)
        cases = []
        for scenario in raw["scenarios"]:
            frames = [
                FrameFeatures(
                    camera_id=scenario["camera_id"],
                    timestamp=base_time + i * FRAME_INTERVAL,
                    fall_score=frame["fall_score"],
                    immobility_score=frame["immobility_score"],
                    tracking_confidence=frame["tracking_confidence"],
                )
                for i, frame in enumerate(scenario["frames"])
            ]
            cases.append(
                ScenarioCase(
                    name=scenario["name"],
                    description=scenario["description"],
                    camera_id=scenario["camera_id"],
                    expect_alert=scenario["expect_alert"],
                    expected_event_type=scenario.get("expected_event_type"),
                    frames=frames,
                )
            )
        return cases
