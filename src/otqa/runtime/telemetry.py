"""Optional display policy, distinct from the fail-closed required recorder."""
from __future__ import annotations

import time
from pathlib import Path

from .codec import DocumentError
from .error_serialization import error_wire
from .storage import publish_json


class TelemetryObserver:
    """Own an optional sink; persist its first failure before continuing/raising.

    A broken display is disabled after its first failure. Diagnostic publication
    uses the same bound durable publisher as other required runtime artifacts;
    failure there propagates, regardless of the optional display policy.
    """
    def __init__(self, context, attempt_dir: Path, failure_policy: str, sink):
        if failure_policy not in ("continue", "abort") or not callable(sink):
            raise DocumentError("Telemetry needs a callable sink and explicit continue/abort policy")
        self.context, self.attempt_dir = context, attempt_dir
        self.failure_policy, self.sink = failure_policy, sink
        self.errors = []
        self.elapsed = 0.0

    def __call__(self, event):
        if self.sink is None:
            return
        started = time.perf_counter()
        try:
            self.sink(event)
        except Exception as exc:
            diagnostic = error_wire(exc, "observer")
            diagnostic["code"] = "observer"
            diagnostic["context"]["event_type"] = type(event).__name__
            diagnostic["context"]["failure_policy"] = self.failure_policy
            publish_json(self.context, self.attempt_dir / "telemetry" / f"error{len(self.errors) + 1:06d}.json", diagnostic)
            self.errors.append(diagnostic)
            self.sink = None
            if self.failure_policy == "abort":
                raise
        finally:
            self.elapsed += time.perf_counter() - started


def terminal_display(stream):
    """Return a display only for a real terminal; redirected logs are silent."""
    if not stream.isatty():
        return None
    def display(event):
        # These public immutable events contain already-computed values only.
        from otqa.models.results import QueryCompleted, SolveFinished
        if isinstance(event, QueryCompleted):
            record = event.record
            print(f"query {record.after.answered_total}: {record.after.candidate_count} candidates", file=stream, flush=True)
        elif isinstance(event, SolveFinished):
            print(f"finished: {event.result.termination_reason}", file=stream, flush=True)
    return display
