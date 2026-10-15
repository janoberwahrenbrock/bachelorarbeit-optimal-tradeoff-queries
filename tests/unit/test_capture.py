import math
import struct

import pytest

from otqa.planning.capture import (
    Computed, EvaluationCaptureError, EvaluationCaptureOptions, NotComputed,
    MappingProjection, TaskCapture, deliver,
)


class Sink:
    def __init__(self):
        self.blocks = []

    def accept(self, block):
        self.blocks.append(block)


def test_capture_preserves_bits_and_explicit_lazy_absence():
    sink = Sink()
    options = EvaluationCaptureOptions(sink, 4096, 16384, 16384, 16384)
    task = TaskCapture(("session", 1), ("root", 0), 4096, 16384)
    values = (-0.0, math.inf, -math.inf, math.nan)
    task.observe("root_evaluation", (0,), 0, values)
    task.observe("root_evaluation", (1,), 1, None, not_computed="lazy_refinement_not_required")
    blocks = task.finish()
    deliver(options, blocks)
    actual = sink.blocks[0].observations[0].value
    assert isinstance(actual, Computed)
    assert tuple(struct.pack("!d", value) for value in actual.value) == tuple(struct.pack("!d", value) for value in values)
    assert sink.blocks[1].observations[0].value == NotComputed("lazy_refinement_not_required")
    assert [block.block_ordinal for block in sink.blocks] == [0, 1, 2]
    assert sink.blocks[-1].task_end


def test_capture_does_not_silently_drop_oversized_record():
    task = TaskCapture((1,), (0,), 256, 1000)
    with pytest.raises(EvaluationCaptureError, match="byte budget"):
        task.observe("root_evaluation", (0,), 0, "x" * 5000)


def test_sink_gets_detached_immutable_projection():
    value = {"shares": [0.99, 0.01]}
    task = TaskCapture((1,), (0,), 4096, 16384)
    task.observe("root_evaluation", (0,), 0, value)
    value["shares"][0] = 0
    snapshot = task.finish()[0].observations[0].value.value
    assert snapshot == MappingProjection((("shares", (0.99, 0.01)),))


def test_duplicate_identity_and_completion_are_errors():
    task = TaskCapture((1,), (0,), 4096, 16384)
    task.observe("root_evaluation", (0,), 0, 1.0)
    with pytest.raises(EvaluationCaptureError, match="duplicate"):
        task.observe("root_evaluation", (0,), 0, 2.0)
    task.finish()
    with pytest.raises(EvaluationCaptureError, match="duplicate"):
        task.finish()


def test_diagnostic_address_identity_distinguishes_binary_signed_zero():
    task = TaskCapture((1,), (0,), 4096, 16384)
    task.observe("root_evaluation", (0.0,), 0, 1.0)
    task.observe("root_evaluation", (-0.0,), 0, 1.0)
    with pytest.raises(EvaluationCaptureError, match="duplicate"):
        task.observe("root_evaluation", (-0.0,), 0, 1.0)
    assert len(task.finish()) == 3


def test_sink_exception_retains_original_cause():
    cause = OSError("sink failed")

    class BadSink:
        def accept(self, block):
            raise cause

    options = EvaluationCaptureOptions(BadSink(), 4096, 16384, 16384, 16384)
    task = TaskCapture((1,), (0,), 4096, 16384)
    with pytest.raises(EvaluationCaptureError) as error:
        deliver(options, task.finish())
    assert error.value.__cause__ is cause
    assert error.value.complete is False


@pytest.mark.parametrize("field", ["max_block_bytes", "max_task_bytes", "max_pending_bytes", "max_session_bytes"])
@pytest.mark.parametrize("value", [0, -1, True, 1.5])
def test_invalid_budgets_are_rejected(field, value):
    fields = dict(sink=Sink(), max_block_bytes=1000, max_task_bytes=4000,
                  max_pending_bytes=8000, max_session_bytes=8000)
    fields[field] = value
    with pytest.raises(ValueError):
        EvaluationCaptureOptions(**fields)
