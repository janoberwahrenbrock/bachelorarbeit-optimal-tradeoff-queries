"""Optional bounded capture of values the planner has already computed.

No file IO, numerical work, or extra search occurs here. Capture is an
internal acceptance-test boundary and deliberately fails closed.
"""

from __future__ import annotations

from dataclasses import dataclass, fields, is_dataclass
import pickle
import struct
from typing import Literal, Protocol

from otqa.errors import EvaluationCaptureError


def _capture_failure(message: str, *, partial_context: object = None) -> EvaluationCaptureError:
    error = EvaluationCaptureError(message)
    error.diagnostic_context = partial_context
    error.complete = False
    return error


@dataclass(frozen=True, slots=True)
class Computed:
    value: object


@dataclass(frozen=True, slots=True)
class NotComputed:
    reason: str


@dataclass(frozen=True, slots=True)
class ObjectProjection:
    """A detached typed record; a sink cannot mutate the planner's objects."""
    type_name: str
    fields: tuple[tuple[str, object], ...]


@dataclass(frozen=True, slots=True)
class MappingProjection:
    entries: tuple[tuple[object, object], ...]


def _snapshot(value: object) -> object:
    if value is None or isinstance(value, (bool, int, float, str, bytes)):
        return value
    if is_dataclass(value):
        return ObjectProjection(type(value).__qualname__, tuple(
            (field.name, _snapshot(getattr(value, field.name))) for field in fields(value)))
    if isinstance(value, dict) or hasattr(value, "items"):
        return MappingProjection(tuple((_snapshot(key), _snapshot(item)) for key, item in value.items()))
    if isinstance(value, (tuple, list)):
        return tuple(_snapshot(item) for item in value)
    raise _capture_failure(f"unsupported capture value type: {type(value).__qualname__}")


def _identity_key(value: object) -> object:
    """Compare diagnostic addresses by binary64 bits, including signed zero."""
    if isinstance(value, float):
        return ("binary64", struct.pack("!d", value))
    if isinstance(value, tuple):
        return tuple(_identity_key(item) for item in value)
    return value


ObservationKind = Literal[
    "plan_boundary", "candidate_inventory", "root_evaluation", "child_options",
    "frontier_projection", "combination_choice", "cache", "error",
]


@dataclass(frozen=True, slots=True)
class EvaluationObservation:
    kind: ObservationKind
    mathematical_address: tuple
    existing_observation_ordinal: int
    value: Computed | NotComputed


@dataclass(frozen=True, slots=True)
class EvaluationBlock:
    plan_address: tuple
    task_address: tuple
    block_ordinal: int
    observations: tuple[EvaluationObservation, ...]
    task_end: bool


class EvaluationCapture(Protocol):
    def accept(self, block: EvaluationBlock) -> None: ...


@dataclass(frozen=True, slots=True)
class EvaluationCaptureOptions:
    sink: EvaluationCapture
    max_block_bytes: int
    max_task_bytes: int
    max_pending_bytes: int
    max_session_bytes: int

    def __post_init__(self) -> None:
        for name in ("max_block_bytes", "max_task_bytes", "max_pending_bytes", "max_session_bytes"):
            if type(getattr(self, name)) is not int or getattr(self, name) <= 0:
                raise ValueError(f"{name} must be a positive integer")
        if self.max_block_bytes > self.max_task_bytes:
            raise ValueError("block budget exceeds task budget")
        if self.max_task_bytes > min(self.max_pending_bytes, self.max_session_bytes):
            raise ValueError("task budget exceeds pending or session budget")


class TaskCapture:
    """A worker-local collector whose entire result has an explicit byte cap."""

    def __init__(self, plan_address: tuple, task_address: tuple, max_block_bytes: int, max_task_bytes: int):
        self.plan_address = plan_address
        self.task_address = task_address
        self.max_block_bytes = max_block_bytes
        self.max_task_bytes = max_task_bytes
        self.blocks: list[EvaluationBlock] = []
        self._bytes = 0
        self._identities: set[tuple] = set()
        self._closed = False

    def observe(self, kind: ObservationKind, address: tuple, ordinal: int, value: object,
                *, not_computed: str | None = None) -> None:
        if self._closed:
            raise _capture_failure("capture task is already complete")
        identity = kind, _identity_key(address), ordinal
        if identity in self._identities:
            raise _capture_failure("duplicate capture observation", partial_context=identity)
        observation = EvaluationObservation(kind, address, ordinal,
            NotComputed(not_computed) if not_computed else Computed(_snapshot(value)))
        block = EvaluationBlock(self.plan_address, self.task_address, len(self.blocks), (observation,), False)
        self._append(block)
        self._identities.add(identity)

    def _append(self, block: EvaluationBlock) -> None:
        size = len(pickle.dumps(block, protocol=5))
        if size > self.max_block_bytes or self._bytes + size > self.max_task_bytes:
            raise _capture_failure("capture byte budget exceeded", partial_context=(self.task_address, len(self.blocks)))
        self.blocks.append(block)
        self._bytes += size

    def finish(self) -> tuple[EvaluationBlock, ...]:
        if self._closed:
            raise _capture_failure("duplicate capture task completion")
        self._append(EvaluationBlock(self.plan_address, self.task_address, len(self.blocks), (), True))
        self._closed = True
        return tuple(self.blocks)


def deliver(options: EvaluationCaptureOptions, blocks: tuple[EvaluationBlock, ...], *, complete: bool = True) -> None:
    """Deliver synchronously in the parent and retain the original sink cause."""
    size = sum(len(pickle.dumps(block, protocol=5)) for block in blocks)
    if size > min(options.max_pending_bytes, options.max_session_bytes):
        raise _capture_failure("pending capture budget exceeded")
    try:
        for expected, block in enumerate(blocks):
            if block.block_ordinal != expected or (block.task_end and expected != len(blocks) - 1) or (
                complete and block.task_end != (expected == len(blocks) - 1)
            ):
                raise _capture_failure("capture blocks are incomplete or unordered")
            options.sink.accept(block)
    except EvaluationCaptureError:
        raise
    except Exception as error:
        raise _capture_failure("evaluation capture sink failed", partial_context=blocks[-1] if blocks else None) from error
