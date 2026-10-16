"""Independent supervisor error-order controls with no child/solver process."""
import json
import os
from uuid import uuid4

import pytest

from otqa.runtime import supervisor
from otqa.runtime.codec import DocumentError
from otqa.runtime.project import load_project_context


def control(tmp_path, monkeypatch, *, deadline, malformed, already_ended=False):
    (tmp_path / 'otqa-project.json').write_text(json.dumps({'schema_version': 1,
        'project_kind': 'otqa_project', 'project_id': str(uuid4())}))
    context = load_project_context(tmp_path)
    attempt = tmp_path / 'runs' / 'case'
    attempt.mkdir(parents=True)
    trace, stored = [], {}
    payload = {'attempt_dir': str(attempt), 'reference_root': str(attempt),
        'run_id': str(uuid4()), 'attempt_id': 'attempt0001', 'series_id': None,
        'job_id': None, 'problem_id': 'controlled', 'configuration_id': 'controlled',
        'materialization_receipt': {'path': 'unused.json', 'sha256': 'a' * 64},
        'native_threads': 1, 'answer_source': 'simulated', 'case_timeout_seconds': deadline}
    class Child:
        pid = 424242
        waited = False
        polls = 0
        reader = None
        def poll(self):
            if self.reader is not None:
                assert os.read(self.reader, 1) == b'G'
                os.close(self.reader)
                self.reader = None
            self.polls += 1
            return 0 if already_ended or self.polls > 1 else None
        def wait(self):
            self.waited = True
            trace.append('wait')
            return 0
    child = Child()
    def publish(context, path, document, **kwargs):
        stored[path.name] = document
        path.write_text(json.dumps(document))
    def launch(*args, **kwargs):
        child.reader = os.dup(kwargs['pass_fds'][0])
        intent = stored['launch_intent.json']
        identity = {'pid': child.pid, 'owner_token': intent['owner_token']}
        registration = {'process': identity,
            'intent': supervisor.file_ref(attempt / 'launch_intent.json', attempt),
            'nonce': intent['nonce'], 'run_id': payload['run_id'],
            'attempt_id': payload['attempt_id']}
        (attempt / 'child_registration.json').write_text(json.dumps(registration))
        (attempt / 'result.json').write_text('malformed' if malformed else '{}')
        return child
    def group(*args, **kwargs):
        if child.waited:
            trace.append('group_dead')
            return 'dead'
        return 'alive'
    def verify(*args, **kwargs):
        trace.append('verify_after_wait' if child.waited else 'verify_live')
        if malformed:
            raise DocumentError('Constructed malformed terminal result')
        return {'execution_status': 'completed', 'solver_result': {'solved': True}}
    clock = iter([0., 1., 100., 101.])
    monkeypatch.setattr(supervisor, 'publish_json', publish)
    monkeypatch.setattr(supervisor, 'process_identity', lambda token: {'owner_token': token})
    monkeypatch.setattr(supervisor.subprocess, 'Popen', launch)
    monkeypatch.setattr(supervisor, 'validate', lambda kind, document: document)
    monkeypatch.setattr(supervisor, 'identity_status', lambda *args, **kwargs: 'alive')
    monkeypatch.setattr(supervisor, 'group_status', group)
    monkeypatch.setattr(supervisor, 'verify_result', verify)
    monkeypatch.setattr(supervisor.time, 'perf_counter', lambda: next(clock))
    monkeypatch.setattr(supervisor.time, 'sleep', lambda value: None)
    monkeypatch.setattr(supervisor, 'terminate_owned_group',
        lambda *args, **kwargs: pytest.fail('Accepted terminal result must disable watchdog'))
    def run():
        return supervisor.supervise_attempt(payload, context=context,
            on_phase=lambda phase, details: trace.append('phase:' + phase))
    return run, trace


def test_no_deadline_malformed_result_fails_after_end_without_terminal_publication(tmp_path, monkeypatch):
    run, trace = control(tmp_path, monkeypatch, deadline=None, malformed=True)
    with pytest.raises(DocumentError, match='malformed terminal'):
        run()
    assert trace[-3:] == ['wait', 'group_dead', 'verify_after_wait']
    assert 'verify_live' not in trace and 'phase:terminal' not in trace


def test_deadline_malformed_result_keeps_early_error_contract(tmp_path, monkeypatch):
    run, trace = control(tmp_path, monkeypatch, deadline=.001, malformed=True)
    with pytest.raises(DocumentError, match='malformed terminal'):
        run()
    assert trace[-1] == 'verify_live'
    assert 'wait' not in trace and 'phase:terminal' not in trace


@pytest.mark.parametrize('deadline', [None, .001])
def test_already_ended_child_still_requires_final_complete_check(tmp_path, monkeypatch, deadline):
    run, trace = control(tmp_path, monkeypatch, deadline=deadline,
        malformed=False, already_ended=True)
    run()
    assert trace[-4:] == ['wait', 'group_dead', 'verify_after_wait', 'phase:terminal']
    assert 'verify_live' not in trace
