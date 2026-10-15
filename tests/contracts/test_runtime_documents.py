from uuid import uuid4

import pytest

from otqa.runtime.codec import DocumentError, decode, encode, float_projection
from otqa.runtime.documents import load_document, resolve_ref
from otqa.runtime.project import load_project_context
from otqa.runtime.schema import definitions, registry_and_validators, validate
from otqa.runtime.storage import publish_bytes


@pytest.mark.parametrize("data", [b'{"x":1,"x":2}', b'{"x":NaN}', b'{"x":Infinity}', b'{"x":1e999}', b'\xef\xbb\xbf{}', b'\xff'])
def test_strict_json_rejects_nonportable_values(data):
    with pytest.raises(DocumentError):
        decode(data)


def test_binary64_projection_preserves_signed_zero_and_integer_counts():
    assert float_projection({"float": -0.0, "count": 1}) == {"float": {"float_hex": "-0x0.0p+0"}, "count": 1}


@pytest.mark.parametrize("value", [True, 2.0, "2", 0, 4])
def test_depth_is_a_strict_bounded_integer(value):
    document = {"schema_version": 1, "configuration_id": "x", "algorithm": {"query_strategy": "fixed", "depth": value,
        "higher_depth_query_source": "both", "grid_size": 5, "planning_evaluation": "candidate_count", "stopping": {"rule": "single_candidate"}},
        "budget": {"max_queries": None}, "execution": {"workers": 1, "start_method": "forkserver", "native_threads": 1, "case_timeout_seconds": None, "cache_policy_id": "bounded_v1"},
        "recording": {"durability": "per_answer", "trace_level": "standard", "profile": False, "telemetry_failure_policy": "continue"}}
    with pytest.raises(DocumentError):
        validate("config", document)


def test_all_native_schemas_have_offline_validators():
    assert len(definitions()[1]) == 27
    assert len(registry_and_validators()) == 27


def project(tmp_path):
    (tmp_path / "otqa-project.json").write_bytes(encode({"schema_version": 1, "project_kind": "otqa_project", "project_id": str(uuid4())}))
    return load_project_context(tmp_path)


def test_output_boundary_and_internal_symlink_are_rejected(tmp_path):
    context = project(tmp_path)
    (tmp_path / "runs").mkdir()
    (tmp_path / "runs" / "target").mkdir()
    (tmp_path / "runs" / "alias").symlink_to(tmp_path / "runs" / "target", target_is_directory=True)
    with pytest.raises(DocumentError):
        publish_bytes(context, tmp_path / "runs" / "alias" / "bad", b"no")
    with pytest.raises(DocumentError):
        publish_bytes(context, tmp_path / "elsewhere" / "bad", b"no")


def test_unique_artifacts_are_never_overwritten(tmp_path):
    context = project(tmp_path)
    target = tmp_path / "runs" / "case" / "result.json"
    publish_bytes(context, target, b"original")
    with pytest.raises(OSError):
        publish_bytes(context, target, b"replacement")
    assert target.read_bytes() == b"original"


def test_source_reference_hash_and_root_are_checked(tmp_path):
    from otqa.runtime.codec import digest
    (tmp_path / "x.json").write_bytes(b"{}")
    assert resolve_ref(tmp_path, {"path": "x.json", "sha256": digest(b"{}")}) == tmp_path / "x.json"
    for reference in ({"path": "../x.json", "sha256": "0" * 64}, {"path": "x.json", "sha256": "0" * 64}):
        with pytest.raises(DocumentError):
            resolve_ref(tmp_path, reference)


def test_reference_reader_uses_the_hash_checked_snapshot_after_replacement(tmp_path):
    from otqa.runtime.codec import digest
    original = {"schema_version": 1, "problem_id": "x", "alternative_ids": ["a"], "objective_ids": ["g"], "alternatives": [[0.25]]}
    raw = encode(original)
    path = tmp_path / "p.json"
    path.write_bytes(raw)
    bound = resolve_ref(tmp_path, {"path": "p.json", "sha256": digest(raw)})
    path.write_bytes(encode({**original, "alternatives": [[0.75]]}))
    assert load_document("problem", bound, reference_root=tmp_path) == original


def test_reference_reader_rejects_fifo_without_blocking_before_fstat(tmp_path, monkeypatch):
    import os
    import otqa.runtime.documents as module
    fifo = tmp_path / 'race.fifo'
    os.mkfifo(fifo)
    original_open = module.os.open
    observed = []
    def checked_open(path, flags, *args, **kwargs):
        assert flags & os.O_NONBLOCK, 'A FIFO replacement must not block before its regular-file check'
        observed.append(path)
        return original_open(path, flags, *args, **kwargs)
    monkeypatch.setattr(module.os, 'open', checked_open)
    with pytest.raises(DocumentError, match='not a regular file'):
        resolve_ref(tmp_path, {'path': 'race.fifo', 'sha256': '0' * 64})
    assert observed == [fifo]
