"""Bound, durable file publication and the single-writer journal protocol."""
from __future__ import annotations

import hashlib
import os
from pathlib import Path
from uuid import uuid4

from .codec import DocumentError, digest, encode, utc_now
from .project import ProjectContext, bound_directory
from .schema import validate


class PersistenceError(OSError):
    """A required persistence barrier failed; the writer cannot continue."""


def create_directory(context: ProjectContext, path: Path, *, namespace: str = "runs") -> None:
    context.relative_output(path, namespace=namespace)
    with bound_directory(context, path.parent, create=True, namespace=namespace) as parent:
        try:
            os.mkdir(path.name, mode=0o755, dir_fd=parent)
        except FileExistsError as exc:
            raise DocumentError(f"Output already exists: {path}") from exc
        os.fsync(parent)


def publish_bytes(context: ProjectContext, path: Path, data: bytes, *, replace: bool = False,
                  namespace: str = "runs") -> None:
    """Write/fsync/link-or-replace/fsync-directory through bound descriptors."""
    context.relative_output(path, namespace=namespace)
    temporary = "." + path.name + "." + uuid4().hex + ".tmp"
    try:
        with bound_directory(context, path.parent, create=True, namespace=namespace) as parent:
            descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                                 0o644, dir_fd=parent)
            try:
                view = memoryview(data)
                while view:
                    written = os.write(descriptor, view)
                    if written <= 0:
                        raise PersistenceError("Short publication write")
                    view = view[written:]
                os.fsync(descriptor)
            finally:
                os.close(descriptor)
            try:
                if replace:
                    # Only progress/controller revisions may replace existing bytes.
                    os.replace(temporary, path.name, src_dir_fd=parent, dst_dir_fd=parent)
                else:
                    # POSIX link gives no-overwrite publication; rename would overwrite.
                    os.link(temporary, path.name, src_dir_fd=parent, dst_dir_fd=parent,
                            follow_symlinks=False)
                    os.unlink(temporary, dir_fd=parent)
                os.fsync(parent)
            except BaseException:
                try:
                    os.unlink(temporary, dir_fd=parent)
                except FileNotFoundError:
                    pass
                raise
    except OSError as exc:
        raise PersistenceError(str(exc)) from exc


def publish_json(context: ProjectContext, path: Path, document: dict, *, kind: str | None = None,
                 replace: bool = False, namespace: str = "runs") -> None:
    if kind is not None:
        validate(kind, document)
    publish_bytes(context, path, encode(document), replace=replace, namespace=namespace)


def empty_counts(initial: int = 0) -> dict:
    return {"initial_answers": initial, "dispatched_new": 0, "answered_new": 0,
            "answered_total": initial}


class RunStore:
    """Exactly one CaseProcess owns this append-only journal and cursor.

    append() is deliberately not a commit. commit() returns only after both the
    journal fsync and durable progress publication succeed. Any failure poisons
    the writer, retaining the last returned cursor as its only confirmed state.
    """
    def __init__(self, context: ProjectContext, attempt_dir: Path, reference_root: Path,
                 run_id: str, attempt_id: str, process: dict, initial_answers: int, *, schema_version=1, execution_cursor=None):
        self.context, self.attempt_dir, self.reference_root = context, attempt_dir, reference_root
        self.run_id, self.attempt_id, self.process = run_id, attempt_id, process
        self.initial_answers = initial_answers
        self.schema_version = schema_version
        self.execution_cursor = execution_cursor
        self.counts = empty_counts()
        self.sequence = 0
        self.phase = "started"
        self.active_query_id = None
        self.cursor = None
        self.failed = False
        self._hash = hashlib.sha256()
        self._bytes = 0
        self._owner_pid = os.getpid()
        with bound_directory(context, attempt_dir) as directory:
            self._fd = os.open("events.jsonl", os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_APPEND | os.O_NOFOLLOW,
                               0o644, dir_fd=directory)
            os.fsync(directory)

    def _assert_writer(self):
        if self.failed or os.getpid() != self._owner_pid or self._fd is None:
            raise PersistenceError("RunStore is closed, failed or owned by another process")

    def append(self, event: dict) -> None:
        self._assert_writer()
        validate("event", event)
        if event["sequence"] != self.sequence + 1 or event["run_id"] != self.run_id or event["attempt_id"] != self.attempt_id:
            raise PersistenceError("Journal identity or sequence mismatch")
        data = encode(event)
        try:
            view = memoryview(data)
            while view:
                written = os.write(self._fd, view)
                if written <= 0:
                    raise PersistenceError("Short journal write")
                view = view[written:]
            self._hash.update(data)
            self._bytes += len(data)
            self.sequence += 1
            kind = event["event_type"]
            if event['schema_version'] != self.schema_version:
                raise PersistenceError('Writer event version differs from its run contract')
            if self.schema_version == 2 and kind in ('run_started', 'answer_received'):
                self.execution_cursor = event['payload']['execution_cursor']
            if kind == "run_started":
                self.counts = empty_counts(self.initial_answers)
                self.phase = "started"
            elif kind == "state_analyzed":
                self.phase = "analyzing"
            elif kind in ("planning_attempt_started", "planning_attempt_completed", "planning_resolved"):
                self.phase = "planning"
            elif kind == "query_planned":
                self.active_query_id = event["query_id"]
                self.phase = "planning"
            elif kind == "query_dispatched":
                self.counts["dispatched_new"] += 1
                self.phase = "awaiting_answer"
            elif kind == "answer_received":
                self.counts["answered_new"] += 1
                self.counts["answered_total"] += 1
                self.phase = "answer_committed"
                if event["payload"]["answered_new"] != self.counts["answered_new"] or event["payload"]["answered_total"] != self.counts["answered_total"]:
                    raise PersistenceError("Accepted answer count mismatch")
            elif kind == "query_completed":
                self.active_query_id = None
            elif kind in ("run_finished", "run_failed", "run_interrupted"):
                self.phase = {"run_finished": "completed", "run_failed": "failed", "run_interrupted": "interrupted"}[kind]
                self.active_query_id = None
        except BaseException:
            self.failed = True
            raise

    def commit(self, partial_api_elapsed_seconds: float | None = None) -> dict:
        self._assert_writer()
        cursor = {"schema_version": self.schema_version, "run_id": self.run_id, "attempt_id": self.attempt_id,
            "updated_at_utc": utc_now(), "last_good_sequence": self.sequence,
            "valid_prefix_bytes": self._bytes, "valid_prefix_sha256": self._hash.hexdigest(),
            "query_counts": dict(self.counts), "partial_api_elapsed_seconds": partial_api_elapsed_seconds,
            "query_phase": self.phase, "active_query_id": self.active_query_id, "process": self.process}
        if self.schema_version == 2:
            cursor['execution_cursor'] = self.execution_cursor
        try:
            os.fsync(self._fd)
            publish_json(self.context, self.attempt_dir / "progress.json", cursor,
                         kind="progress", replace=True)
        except BaseException:
            self.failed = True
            raise
        self.cursor = cursor
        return cursor

    def close(self):
        if self._fd is not None:
            os.close(self._fd)
            self._fd = None

    def journal_proof(self) -> dict:
        self.close()
        data = (self.attempt_dir / "events.jsonl").read_bytes()
        cursor = self.cursor
        if cursor is None:
            raise PersistenceError("No confirmed start cursor exists")
        return {"path": (self.attempt_dir / "events.jsonl").relative_to(self.reference_root).as_posix(),
            "sha256": digest(data), "bytes": len(data), "valid_prefix_bytes": cursor["valid_prefix_bytes"],
            "valid_prefix_sha256": cursor["valid_prefix_sha256"], "last_good_sequence": cursor["last_good_sequence"],
            "trailing_partial_line": bool(data and not data.endswith(b"\n")),
            "uncommitted_suffix_bytes": len(data) - cursor["valid_prefix_bytes"]}
