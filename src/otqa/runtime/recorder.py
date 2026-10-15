"""Synchronous event adapter: mandatory persistence and optional display differ."""
from __future__ import annotations

import time

from .codec import mathematical_hex, utc_now
from .serialization import planning_wire, query_wire, record_wire, state_wire


class WireRecorder:
    def __init__(self, store, alternative_ids, *, stop_aware, trace_level):
        self.store = store
        self.alternative_ids = alternative_ids
        self.stop_aware, self.trace_level = stop_aware, trace_level
        self.active_query_id = None
        self.last_answer_query_id = None
        self.next_query = 1
        self.api_started = None
        self.elapsed = 0.0

    def event(self, kind, payload, query_id=None, *, commit=False):
        start = time.perf_counter()
        event = {"schema_version": 1, "run_id": self.store.run_id, "attempt_id": self.store.attempt_id,
            "sequence": self.store.sequence + 1, "occurred_at_utc": utc_now(), "monotonic_ns": time.monotonic_ns(),
            "event_type": kind, "query_id": query_id, "payload": payload, "numeric_hex": mathematical_hex(payload, "/payload")}
        self.store.append(event)
        if commit:
            partial = None if self.api_started is None else time.perf_counter() - self.api_started
            self.store.commit(partial)
        self.elapsed += time.perf_counter() - start

    def __call__(self, event):
        # Imports are deliberately here, after the CaseProcess release barrier.
        from otqa.models.results import AnswerReceived, QueryCompleted, QueryDispatched, QueryPlanned, SolveFinished, StateAnalyzed
        if isinstance(event, StateAnalyzed):
            payload = state_wire(event.state, self.alternative_ids, self.last_answer_query_id)
            self.event("state_analyzed", payload, self.last_answer_query_id)
        elif isinstance(event, QueryPlanned):
            self.active_query_id = f"q{self.next_query:06d}"
            self.event("query_planned", {"state_before_index": event.state.answered_total,
                "planning": planning_wire(event.planning, stop_aware=self.stop_aware, trace_level=self.trace_level, candidate_count=event.state.candidate_count)}, self.active_query_id)
        elif isinstance(event, QueryDispatched):
            self.event("query_dispatched", {"query": query_wire(event.query), "dispatched_new": event.query_counts.dispatched_new}, self.active_query_id, commit=True)
        elif isinstance(event, AnswerReceived):
            self.event("answer_received", {"query": query_wire(event.answered_query.query), "answer": event.answered_query.answer,
                "answered_new": event.query_counts.answered_new, "answered_total": event.query_counts.answered_total}, self.active_query_id, commit=True)
            self.last_answer_query_id = self.active_query_id
        elif isinstance(event, QueryCompleted):
            self.event("query_completed", record_wire(event.record, self.active_query_id, stop_aware=self.stop_aware, trace_level=self.trace_level), self.active_query_id)
            self.active_query_id = None
            self.next_query += 1
        elif isinstance(event, SolveFinished):
            # The API owns this event; the runtime terminal line follows API return
            # so its measured interval contains all synchronous SDK callbacks.
            return
        else:
            raise TypeError(f"Unknown solver event {type(event).__name__}")
