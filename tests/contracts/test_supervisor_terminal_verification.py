"""Pure process-loop controls; no child or numerical solver is started.

Real temporary project files, durable launch/grant publication and release pipe
are used. Popen, process observations, wall clock and terminal reader are explicit
boundary doubles; separate reader/native qualification tests own file validity.
"""
from types import SimpleNamespace
from uuid import uuid4
import os

import pytest

from otqa.runtime import supervisor as subject
from otqa.runtime.codec import DocumentError, encode, read_json, utc_now
from otqa.runtime.documents import file_ref
from otqa.runtime.project import load_project_context
from otqa.runtime.storage import create_directory, publish_json


VALID = {'execution_status': 'completed', 'solver_result': {'solved': True}}


def controls(tmp_path, monkeypatch, *, deadline=None, publish_early=True,
             invalid_early=False, invalid_final=False, group_end='dead'):
    (tmp_path / 'otqa-project.json').write_bytes(encode({'schema_version': 1,
        'project_kind': 'otqa_project', 'project_id': str(uuid4())}))
    context = load_project_context(tmp_path)
    attempt = tmp_path / 'runs/attempt'
    create_directory(context, attempt)
    payload = {'attempt_dir': str(attempt), 'reference_root': str(attempt),
        'run_id': str(uuid4()), 'attempt_id': 'attempt0001', 'series_id': None,
        'job_id': None, 'problem_id': 'analytical', 'configuration_id': 'fixed2',
        'materialization_receipt': {'path': 'materialization_receipt.json', 'sha256': '0' * 64},
        'native_threads': 1, 'answer_source': 'simulated', 'case_timeout_seconds': deadline}
    state = SimpleNamespace(clock=0., trace=[], verifications=[], phases=[], child=None,
                            group_proved=False, terminations=0, finalized=0)

    def identity(owner, pid):
        return {'pid': pid, 'hostname': 'pure-supervisor-control', 'identity_method': 'owned_child',
                'boot_id': None, 'start_ticks': None, 'pgid': pid, 'sid': pid, 'owner_token': owner}

    class Child:
        pid = 5432
        def __init__(self, command, **kwargs):
            assert command[1:3] == ['-m', 'otqa.runtime.case']
            assert kwargs['start_new_session'] is True
            self.waited = self.terminated = False
            self.polls = 0
            self.reader = os.dup(kwargs['pass_fds'][0])
            intent = read_json(attempt / 'launch_intent.json')
            self.identity = identity(intent['owner_token'], self.pid)
            publish_json(context, attempt / 'child_registration.json', {'schema_version': 1,
                'run_id': payload['run_id'], 'attempt_id': payload['attempt_id'],
                'created_at_utc': utc_now(), 'intent': file_ref(attempt / 'launch_intent.json', attempt),
                'nonce': intent['nonce'], 'process': self.identity}, kind='child_registration')
            state.child = self
        def poll(self):
            self.polls += 1
            state.clock += 1.
            if self.reader is not None:
                assert os.read(self.reader, 1) == b'G'
                os.close(self.reader)
                self.reader = None
                state.trace.append('released')
            if publish_early and self.polls == 1:
                publish_json(context, attempt / 'result.json', {'invalid': True} if invalid_early else VALID)
                state.trace.append('result_published')
            return 0 if self.terminated or self.polls > 4 else None
        def wait(self):
            self.waited = True
            state.trace.append('wait')
            if invalid_final:
                (attempt / 'result.json').write_bytes(encode({'invalid': True}))
            elif not publish_early and not self.terminated:
                publish_json(context, attempt / 'result.json', VALID)
            return 0
        def kill(self):
            self.terminated = True

    def group_status(current, *, owned_child):
        assert current == state.child.identity and owned_child is state.child
        if not owned_child.waited:
            return 'alive'
        state.trace.append('group_' + group_end)
        if group_end == 'dead':
            state.group_proved = True
        return group_end

    def verify(path, root, expected_payload):
        assert root == attempt and expected_payload is payload
        state.verifications.append({'waited': state.child.waited, 'group_proved': state.group_proved})
        state.trace.append('verify_final' if state.child.waited else 'verify_early')
        value = read_json(path)
        if value.get('invalid'):
            raise DocumentError('invalid terminal fixture')
        return value

    def terminate(current, *, owned_child, force):
        assert current == state.child.identity and owned_child is state.child and force is True
        state.terminations += 1
        state.child.terminated = True
        state.trace.append('terminate')

    def finalize(expected_payload, *, context, interruption):
        assert expected_payload is payload and state.child.waited and state.group_proved
        state.finalized += 1
        assert interruption['reason'] == 'timeout'
        publish_json(context, attempt / 'result.json', {'execution_status': 'interrupted',
            'solver_result': None, 'interruption': interruption})

    def phase(name, data):
        state.phases.append(name)
        state.trace.append('phase_' + name)
        if name == 'terminal':
            assert state.group_proved and state.verifications[-1]['waited']

    monkeypatch.setattr(subject.subprocess, 'Popen', Child)
    monkeypatch.setattr(subject, 'process_identity', lambda owner: identity(owner, 211))
    monkeypatch.setattr(subject, 'identity_status', lambda *args, **kwargs: 'alive')
    monkeypatch.setattr(subject, 'group_status', group_status)
    monkeypatch.setattr(subject, 'verify_result', verify)
    monkeypatch.setattr(subject, 'terminate_owned_group', terminate)
    monkeypatch.setattr(subject, 'finalize_ended_attempt', finalize)
    monkeypatch.setattr(subject.time, 'perf_counter', lambda: state.clock)
    monkeypatch.setattr(subject.time, 'sleep', lambda duration: None)
    state.run = lambda: subject.supervise_attempt(payload, context=context, on_phase=phase)
    return state


@pytest.mark.parametrize('publish_early', [False, True])
def test_no_deadline_has_one_complete_reader_only_after_wait_and_proved_group_end(tmp_path, monkeypatch, publish_early):
    state = controls(tmp_path, monkeypatch, publish_early=publish_early)
    result = state.run()
    assert result.exit_code == 0 and result.result == VALID
    assert state.verifications == [{'waited': True, 'group_proved': True}]
    assert state.trace.index('wait') < state.trace.index('group_dead') < state.trace.index('verify_final') < state.trace.index('phase_terminal')
    assert state.terminations == state.finalized == 0


def test_deadline_retains_early_and_final_reader_and_accepted_result_disables_watchdog(tmp_path, monkeypatch):
    state = controls(tmp_path, monkeypatch, deadline=.5)
    result = state.run()
    assert result.exit_code == 0
    assert state.clock > .5 and state.child.polls == 5
    assert state.verifications == [{'waited': False, 'group_proved': False}, {'waited': True, 'group_proved': True}]
    assert state.trace.index('verify_early') < state.trace.index('wait') < state.trace.index('verify_final')
    assert state.terminations == 0


def test_deadline_without_terminal_result_still_terminates_and_finalizes_after_group_end(tmp_path, monkeypatch):
    state = controls(tmp_path, monkeypatch, deadline=.5, publish_early=False)
    result = state.run()
    assert result.exit_code == 1 and result.result['interruption']['reason'] == 'timeout'
    assert state.terminations == state.finalized == 1
    assert state.verifications == [{'waited': True, 'group_proved': True}]
    assert state.trace.index('terminate') < state.trace.index('wait') < state.trace.index('group_dead') < state.trace.index('verify_final')


def test_invalid_no_deadline_result_fails_after_group_end_without_terminal_outcome(tmp_path, monkeypatch):
    state = controls(tmp_path, monkeypatch, invalid_early=True)
    with pytest.raises(DocumentError, match='invalid terminal'):
        state.run()
    assert state.verifications == [{'waited': True, 'group_proved': True}]
    assert state.child.waited and state.group_proved and 'terminal' not in state.phases


def test_invalid_deadline_result_keeps_early_error_before_wait(tmp_path, monkeypatch):
    state = controls(tmp_path, monkeypatch, deadline=.5, invalid_early=True)
    with pytest.raises(DocumentError, match='invalid terminal'):
        state.run()
    assert state.verifications == [{'waited': False, 'group_proved': False}]
    assert not state.child.waited and 'terminal' not in state.phases


def test_deadline_early_acceptance_does_not_skip_final_tamper_rejection(tmp_path, monkeypatch):
    state = controls(tmp_path, monkeypatch, deadline=.5, invalid_final=True)
    with pytest.raises(DocumentError, match='invalid terminal'):
        state.run()
    assert state.verifications == [{'waited': False, 'group_proved': False}, {'waited': True, 'group_proved': True}]
    assert state.child.waited and state.group_proved and 'terminal' not in state.phases


@pytest.mark.parametrize('group_end', ['alive', 'unknown'])
@pytest.mark.parametrize('deadline', [None, .5])
def test_no_result_acceptance_or_outcome_before_complete_group_end_proof(tmp_path, monkeypatch, group_end, deadline):
    state = controls(tmp_path, monkeypatch, deadline=deadline, group_end=group_end)
    with pytest.raises(subject.RecoveryBlockedError, match='live or unknown'):
        state.run()
    assert state.child.waited and not state.group_proved
    assert state.verifications == ([] if deadline is None else [{'waited': False, 'group_proved': False}])
    assert 'terminal' not in state.phases and state.terminations == 0
