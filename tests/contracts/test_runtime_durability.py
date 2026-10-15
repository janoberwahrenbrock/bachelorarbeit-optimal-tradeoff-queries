"""Constructed persistence faults; these are not power-loss qualification."""
import time
from uuid import uuid4

import pytest

from otqa.runtime.codec import digest, encode, read_json, utc_now
from otqa.runtime.project import load_project_context
from otqa.runtime.storage import PersistenceError, RunStore, create_directory


def store_at(tmp_path, initial=0):
    (tmp_path / "otqa-project.json").write_bytes(encode({"schema_version": 1, "project_kind": "otqa_project", "project_id": str(uuid4())}))
    context = load_project_context(tmp_path)
    directory = context.project_root / "runs" / "attempt"
    create_directory(context, directory)
    identity = {"pid": 100, "hostname": "constructed", "identity_method": "owned_child", "boot_id": None,
                "start_ticks": None, "pgid": 100, "sid": 100, "owner_token": "constructed"}
    return RunStore(context, directory, directory, str(uuid4()), "attempt0001", identity, initial)


def event(store, kind, payload, query_id=None):
    from otqa.runtime.codec import mathematical_hex
    return {"schema_version": 1, "run_id": store.run_id, "attempt_id": store.attempt_id, "sequence": store.sequence + 1,
        "occurred_at_utc": utc_now(), "monotonic_ns": time.monotonic_ns(), "event_type": kind, "query_id": query_id,
        "payload": payload, "numeric_hex": mathematical_hex(payload, "/payload")}


def test_append_does_not_invent_a_durable_start(tmp_path):
    store = store_at(tmp_path, initial=2)
    try:
        store.append(event(store, "run_started", {"manifest_sha256": "0" * 64}))
        assert store.cursor is None
        assert not (store.attempt_dir / "progress.json").exists()
        cursor = store.commit()
        assert cursor["query_counts"]["answered_total"] == 2
        assert read_json(store.attempt_dir / "progress.json") == cursor
    finally:
        store.close()


def test_failed_cursor_publication_preserves_only_the_previous_confirmation(tmp_path, monkeypatch):
    store = store_at(tmp_path)
    try:
        store.append(event(store, "run_started", {"manifest_sha256": "0" * 64}))
        previous = store.commit()
        store.append(event(store, "answer_received", {"query": {"goal_index_a": 0, "goal_index_b": 1, "value": 1.0},
            "answer": ">", "answered_new": 1, "answered_total": 1}, "q000001"))
        def fail(*args, **kwargs):
            raise OSError("Injected fsynced-journal/cursor window")
        monkeypatch.setattr("otqa.runtime.storage.publish_json", fail)
        with pytest.raises(OSError):
            store.commit()
        assert store.cursor == previous
        assert store.cursor["query_counts"]["answered_total"] == 0
        assert store.failed
        with pytest.raises(PersistenceError):
            store.append(event(store, "run_started", {"manifest_sha256": "0" * 64}))
        proof = store.journal_proof()
        assert proof["uncommitted_suffix_bytes"] > 0
        assert proof["valid_prefix_sha256"] == previous["valid_prefix_sha256"]
    finally:
        store.close()


def test_later_raw_bytes_do_not_change_confirmed_prefix(tmp_path):
    from otqa.runtime.journal import verify_prefix
    store = store_at(tmp_path)
    store.append(event(store, "run_started", {"manifest_sha256": "0" * 64}))
    cursor = store.commit()
    store.close()
    with (store.attempt_dir / "events.jsonl").open("ab") as output:
        output.write(b'{"unfinished":')
    raw = (store.attempt_dir / "events.jsonl").read_bytes()
    verified = verify_prefix(raw, cursor["valid_prefix_bytes"], cursor["valid_prefix_sha256"], cursor["last_good_sequence"])
    assert verified["query_counts"]["answered_total"] == 0
    assert digest(raw) != cursor["valid_prefix_sha256"]
    proof = store.journal_proof()
    assert proof["trailing_partial_line"]


def test_unknown_start_cannot_be_recovered_from_raw_start_line(tmp_path):
    from otqa.runtime.supervisor import RecoveryBlockedError, finalize_ended_attempt
    store = store_at(tmp_path)
    store.append(event(store, "run_started", {"manifest_sha256": "0" * 64}))
    store.close()
    payload = {"attempt_dir": str(store.attempt_dir), "reference_root": str(store.reference_root)}
    with pytest.raises(RecoveryBlockedError, match="without a confirmed start cursor"):
        finalize_ended_attempt(payload, context=store.context)
    assert not (store.attempt_dir / "result.json").exists()


def test_owned_child_cleanup_retries_transient_unknown_until_proven_dead(monkeypatch):
    import otqa.runtime.supervisor as module
    child = object()
    identity = {'pid': 15}
    observations = iter(('unknown', 'alive', 'unknown', 'dead'))
    seen = []
    def status(current, *, owned_child):
        assert current is identity and owned_child is child
        value = next(observations)
        seen.append(value)
        return value
    monkeypatch.setattr(module, 'group_status', status)
    monkeypatch.setattr(module.time, 'sleep', lambda seconds: None)
    module._confirm_group_end(identity, child)
    assert seen == ['unknown', 'alive', 'unknown', 'dead']


@pytest.mark.parametrize('status', ['unknown', 'alive'])
def test_unproven_cleanup_stays_blocked_after_bounded_read_retries(monkeypatch, status):
    import otqa.runtime.supervisor as module
    observed = []
    def group_status(*args, **kwargs):
        observed.append(status)
        return status
    monkeypatch.setattr(module, 'group_status', group_status)
    monkeypatch.setattr(module.time, 'sleep', lambda seconds: None)
    monkeypatch.setattr(module, 'terminate_owned_group', lambda *args, **kwargs: pytest.fail('Read retry must not signal a group'))
    with pytest.raises(module.RecoveryBlockedError, match='live or unknown'):
        module._confirm_group_end({'pid': 15}, object())
    assert len(observed) == 101
