"""Opt-in CaseProcess-only cProfile; no worker or exclusive phase claims."""
from __future__ import annotations

import io
import marshal
import os
from pathlib import Path
import pstats

from .documents import file_ref
from .storage import publish_bytes, publish_json


class ParentCallProfiler:
    def __init__(self):
        import cProfile
        self.profiler = cProfile.Profile()
        self.pid = os.getpid()

    def start(self):
        self.profiler.enable()

    def stop(self):
        self.profiler.disable()

    def publish(self, context, attempt: Path, root: Path, run_id, attempt_id, metrics):
        """Save actual pstats plus an identity-bearing readable raw report."""
        self.profiler.create_stats()
        data = marshal.dumps(self.profiler.stats)
        binary = attempt / "profiles" / "case-api.pstats"
        publish_bytes(context, binary, data)
        report = io.StringIO()
        report.write(f"collector=cProfile; process_pid={self.pid}; scope=CaseProcess public solve call only\n")
        report.write("Workers are not instrumented. Inclusive function times are not exclusive phase totals.\n")
        pstats.Stats(self.profiler, stream=report).sort_stats("cumulative").print_stats()
        text = attempt / "profiles" / "case-api.txt"
        publish_bytes(context, text, report.getvalue().encode("utf-8"))
        publish_json(context, attempt / "profile.json", {"schema_version": 1, "run_id": run_id, "attempt_id": attempt_id,
            "manifest": file_ref(attempt / "manifest.json", root), "collector": "cprofile", "metrics": metrics,
            "raw_reports": [file_ref(binary, root), file_ref(text, root)]}, kind="profile")
