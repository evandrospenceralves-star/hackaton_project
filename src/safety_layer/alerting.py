"""Where Events go once the detector decides a human should be notified."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import List, Protocol

from .event import Event


class AlertSink(Protocol):
    def send(self, event: Event) -> None: ...


class ConsoleAlertSink:
    """Prints alerts to stdout. Good enough for a live demo."""

    def send(self, event: Event) -> None:
        print(f"[ALERT] {event.event_type.value} on {event.camera_id} "
              f"(confidence={event.overall_confidence:.2f}) at {event.timestamp.isoformat()}")


class InMemoryAlertSink:
    """Collects alerts in a list. Used by tests and the eval harness."""

    def __init__(self) -> None:
        self.events: List[Event] = []

    def send(self, event: Event) -> None:
        self.events.append(event)


class WebhookAlertSink:
    """POSTs the event JSON to a webhook (Slack incoming webhook, dashboard
    ingest endpoint, etc). Uses stdlib only so the demo has no extra
    dependency to install at 2am before the deadline."""

    def __init__(self, url: str, timeout_seconds: float = 5.0) -> None:
        if not url.startswith(("http://", "https://")):
            raise ValueError(f"webhook url must be http(s), got {url!r}")
        self.url = url
        self.timeout_seconds = timeout_seconds

    def send(self, event: Event) -> None:
        payload = json.dumps(event.to_dict()).encode("utf-8")
        request = urllib.request.Request(
            self.url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout_seconds):
                pass
        except urllib.error.URLError as exc:
            raise RuntimeError(f"failed to deliver alert to {self.url}: {exc}") from exc
