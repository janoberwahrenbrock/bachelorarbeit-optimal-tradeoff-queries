"""Fresh real-SDK journals plus deliberately corrupted reader inputs."""
import os
import time
from uuid import uuid4

import pytest

import otqa
from otqa.answers import SimulatedAnswers
from otqa.runtime.case import timings
from otqa.runtime.codec import DocumentError, encode, mathematical_hex, read_json, utc_now
from otqa.runtime.documents import file_ref
from otqa.runtime.journal import actual_stop, verify_actual_policy, verify_cursor
from otqa.runtime.project import load_project_context
from otqa.runtime.recorder import WireRecorder
from otqa.runtime.serialization import domain_inputs, result_wire
from otqa.runtime.storage import RunStore, create_directory, publish_json
from otqa.runtime.validation import verify_result


def recorded_result(tmp_path, *, matrix=((1., 0.), (0., 1.)), threshold=None):
    case_started = time.perf_counter()
    (tmp_path / 'otqa-project.json').write_bytes(encode({'schema_version': 1, 'project_kind': 'otqa_project', 'project_id': str(uuid4())}))
    context = load_project_context(tmp_path)
    root = tmp_path / 'runs' / 'case'
    create_directory(context, root)
    stopping = {'rule': 'single_candidate'} if threshold is None else {'rule': 'volume_confidence', 'threshold': threshold}
    config = {'schema_version': 1, 'configuration_id': 'actual-reader-control',
        'algorithm': {'query_strategy': 'fixed', 'depth': 1, 'grid_size': 5, 'higher_depth_query_source': 'both',
                      'planning_evaluation': 'candidate_count', 'stopping': stopping},
        'budget': {'max_queries': 5},
        'execution': {'workers': 1, 'native_threads': 1, 'start_method': 'forkserver', 'cache_policy_id': 'bounded_v1', 'case_timeout_seconds': None},
        'recording': {'durability': 'per_answer', 'trace_level': 'standard', 'profile': False, 'telemetry_failure_policy': 'continue'}}
    problem = {'schema_version': 1, 'problem_id': 'reader-control', 'alternative_ids': ['z-first', 'a-second'],
               'objective_ids': ['x', 'y'], 'alternatives': [list(row) for row in matrix]}
    oracle = {'schema_version': 1, 'problem_id': problem['problem_id'], 'target_weights': [.7, .3]}
    for name, document in [('problem', problem), ('config', config), ('oracle', oracle)]:
        publish_json(context, root / (name + '.json'), document)
    from otqa.numerics.profile import resolved_cache_policy, resolved_numerical_profile
    process = {'pid': os.getpid(), 'hostname': 'constructed-sdk-reader-control', 'identity_method': 'owned_child',
        'boot_id': None, 'start_ticks': None, 'pgid': os.getpid(), 'sid': os.getpid(), 'owner_token': 'constructed'}
    dummy = {'path': 'unused-control-reference.json', 'sha256': '0' * 64}
    run_id = str(uuid4())
    manifest = {'schema_version': 1, 'run_id': run_id, 'attempt_id': 'attempt0001', 'series_id': None, 'job_id': None,
        'problem_id': problem['problem_id'], 'configuration_id': config['configuration_id'],
        'execution_kind': 'fresh', 'answer_source': 'simulated', 'created_at_utc': utc_now(),
        'source': {'inventory_format': 'otqa-source-v1', 'version': 'constructed-control', 'git_commit': None, 'dirty': False, 'source_sha256': 'a' * 64},
        'source_inventory': dummy, 'project_binding': context.binding(root), 'run_purpose': 'qualification',
        'materialization_receipt': dummy, 'launch_intent': dummy,
        'inputs': {'problem': file_ref(root / 'problem.json', root), 'configuration': file_ref(root / 'config.json', root),
                   'oracle': file_ref(root / 'oracle.json', root), 'initial_answers': None, 'replay_answers': None},
        'mathematical_input_sha256': '0' * 64, 'effective_algorithm': config['algorithm'], 'effective_budget': config['budget'],
        'effective_execution': config['execution'], 'effective_recording': config['recording'], 'execution_profile': dummy,
        'numerical_profile': resolved_numerical_profile(), 'resolved_cache_policy': resolved_cache_policy(),
        'environment': {'hostname': 'constructed-sdk-reader-control', 'platform_family': 'linux', 'platform': 'constructed', 'python': 'constructed',
                        'packages': {}, 'cpu_model': None, 'physical_cores': None, 'logical_cpus': None, 'native_thread_environment': {}, 'backend_capabilities': {}},
        'process': process}
    publish_json(context, root / 'manifest.json', manifest, kind='manifest')
    store = RunStore(context, root, root, run_id, 'attempt0001', process, 0)
    recorder = WireRecorder(store, problem['alternative_ids'], stop_aware=False, trace_level='standard')
    recorder.event('run_started', {'manifest_sha256': file_ref(root / 'manifest.json', root)['sha256']}, commit=True)
    domain, policy, budget, execution, initial = domain_inputs(problem, config, None)
    api_started = time.perf_counter()
    result = otqa.solve(domain, policy, SimulatedAnswers(oracle['target_weights']), budget=budget, execution=execution, recorder=recorder)
    elapsed = time.perf_counter() - api_started
    recorder.event('run_finished', {'termination_reason': result.termination_reason, 'solved': result.solved, 'query_counts': dict(store.counts)}, commit=True)
    proof = store.journal_proof()
    solver = result_wire(result, problem['alternative_ids'], stop_aware=False, trace_level='standard')
    from otqa.analysis.quality import evaluate_quality
    envelope = {'schema_version': 1, 'run_id': run_id, 'attempt_id': 'attempt0001', 'problem_id': problem['problem_id'], 'configuration_id': config['configuration_id'],
        'execution_status': 'completed', 'execution_stage': 'solver', 'finalized_by': 'case_process', 'started_at_utc': utc_now(), 'finished_at_utc': utc_now(),
        'query_counts': dict(store.counts), 'timings': timings(case_elapsed=time.perf_counter() - case_started, api_elapsed=elapsed, complete=True),
        'solver_result': solver, 'quality': evaluate_quality(problem, oracle, solver['selected_candidate_id'], solver['answered_queries']),
        'error': None, 'interruption': None, 'telemetry_errors': [], 'journal': proof, 'numeric_hex': mathematical_hex(solver, '/solver_result')}
    publish_json(context, root / 'result.json', envelope, kind='result')
    payload = {key: envelope[key] for key in ('run_id', 'attempt_id', 'problem_id', 'configuration_id')}
    payload['project_binding'] = context.binding(root)
    return context, root, manifest, payload, envelope


def test_real_sdk_journal_and_result_satisfy_shared_policy_reader(tmp_path):
    _, root, manifest, payload, envelope = recorded_result(tmp_path)
    assert verify_result(root / 'result.json', root, payload) == envelope
    cursor = read_json(root / 'progress.json')
    prefix = verify_cursor((root / 'events.jsonl').read_bytes(), cursor,
        algorithm=manifest['effective_algorithm'], budget=manifest['effective_budget'], alternative_ids=['z-first', 'a-second'])
    assert prefix['query_phase'] == 'completed' and prefix['active_query_id'] is None


@pytest.mark.parametrize('field,value', [('query_phase', 'started'), ('query_phase', 'awaiting_answer'), ('active_query_id', 'foreign')])
def test_cursor_phase_and_active_query_must_match_even_with_valid_counts_and_hash(tmp_path, field, value):
    _, root, _, _, _ = recorded_result(tmp_path)
    cursor = read_json(root / 'progress.json')
    cursor[field] = value
    with pytest.raises(DocumentError, match=field):
        verify_cursor((root / 'events.jsonl').read_bytes(), cursor)


def test_confidence_selection_requires_maximum_even_when_other_candidate_exceeds_threshold(tmp_path):
    _, root, _, payload, envelope = recorded_result(tmp_path, matrix=((1., 0.), (0., .5)), threshold=.2)
    assert envelope['solver_result']['selected_candidate_id'] == 'z-first'
    assert verify_result(root / 'result.json', root, payload) == envelope
    solver = envelope['solver_result']
    solver['selected_candidate_id'] = 'a-second'
    solver['selected_candidate_volume'] = solver['final_state']['candidate_volumes']['a-second']
    solver['selected_candidate_volume_share'] = solver['final_state']['candidate_volume_shares']['a-second']
    assert solver['selected_candidate_volume_share'] >= .2
    envelope['numeric_hex'] = mathematical_hex(solver, '/solver_result')
    (root / 'result.json').write_bytes(encode(envelope))
    with pytest.raises(DocumentError, match='maximum-share/original-index'):
        verify_result(root / 'result.json', root, payload)


def test_result_manifest_cannot_adopt_a_different_series_binding(tmp_path):
    _, root, _, payload, _ = recorded_result(tmp_path)
    payload['project_binding'] = {**payload['project_binding'], 'relative_root': 'runs/foreign'}
    with pytest.raises(DocumentError, match='project binding'):
        verify_result(root / 'result.json', root, payload)


def state(candidates=('z-first', 'a-second'), shares=(.5, .5), index=0):
    return {'state_index': index, 'last_answer_query_id': None, 'candidate_ids': list(candidates),
            'candidate_volumes': dict(zip(candidates, shares, strict=True)), 'candidate_volume_shares': dict(zip(candidates, shares, strict=True))}


def algorithm(stopping):
    return {'query_strategy': 'fixed', 'depth': 1, 'grid_size': 5, 'higher_depth_query_source': 'both', 'planning_evaluation': 'candidate_count', 'stopping': stopping}


@pytest.mark.parametrize('stopping,actual_state,budget', [
    ({'rule': 'single_candidate'}, state(('z-first',), (1.,)), {'max_queries': None}),
    ({'rule': 'volume_confidence', 'threshold': .4}, state(), {'max_queries': None}),
    ({'rule': 'single_candidate'}, state(index=2), {'max_queries': 2}),
])
def test_planning_is_forbidden_after_first_actual_stop_or_budget(stopping, actual_state, budget):
    events = [{'event_type': 'state_analyzed', 'payload': actual_state}, {'event_type': 'query_planned', 'payload': {}}]
    with pytest.raises(DocumentError, match='continued after'):
        verify_actual_policy(events, algorithm(stopping), budget, ['z-first', 'a-second'])


@pytest.mark.parametrize('actual_state,rule,expected', [
    (state(('a-second',), (1.,), index=3), {'rule': 'volume_confidence', 'threshold': .2}, ('exact_single_candidate', 'a-second')),
    (state(index=3), {'rule': 'volume_confidence', 'threshold': .4}, ('volume_confidence', 'z-first')),
    (state(index=3), {'rule': 'single_candidate'}, ('max_questions', None)),
])
def test_actual_stop_precedence_is_singleton_then_confidence_then_budget(actual_state, rule, expected):
    assert actual_stop(actual_state, algorithm(rule), {'max_queries': 3}, ['z-first', 'a-second']) == expected


def test_confidence_exact_tie_uses_original_document_index_even_when_state_and_ids_sort_differently():
    actual = state(('a-second', 'z-first'), (.5, .5))
    assert actual_stop(actual, algorithm({'rule': 'volume_confidence', 'threshold': .2}), {'max_queries': None},
                       ['z-first', 'a-second']) == ('volume_confidence', 'z-first')


def test_controller_rejects_existing_manifest_from_another_series(tmp_path):
    from otqa.experiments.controller import _verify_manifest_bindings
    _, root, manifest, _, _ = recorded_result(tmp_path)
    plan = {'project_binding': {**manifest['project_binding'], 'relative_root': 'runs/other'}}
    state_doc = {'jobs': [{'attempts': [{'directory': '.'}]}]}
    with pytest.raises(DocumentError, match='project binding'):
        _verify_manifest_bindings(root, plan, state_doc)


def test_audit_prefix_rejects_manifest_from_another_project_binding(tmp_path):
    from otqa.analysis.audit import capture_prefix
    context, root, manifest, payload, _ = recorded_result(tmp_path)
    manifest['project_binding']['project_id'] = str(uuid4())
    (root / 'manifest.json').write_bytes(encode(manifest))
    with pytest.raises(DocumentError, match='project binding'):
        capture_prefix(root, {**payload, 'directory': '.'}, root / 'snapshot.json', context=context)


def test_shared_cursor_reader_matches_real_writer_at_every_event_including_completion(tmp_path):
    context, root, _, _, _ = recorded_result(tmp_path)
    source = [read_json_line for read_json_line in (root / 'events.jsonl').read_bytes().splitlines()]
    from otqa.runtime.codec import decode
    events = [decode(line) for line in source]
    target = tmp_path / 'runs' / 'event-prefixes'
    create_directory(context, target)
    process = read_json(root / 'progress.json')['process']
    store = RunStore(context, target, target, events[0]['run_id'], events[0]['attempt_id'], process, 0)
    observed = []
    try:
        for event in events:
            store.append(event)
            cursor = store.commit()
            prefix = verify_cursor((target / 'events.jsonl').read_bytes(), cursor)
            observed.append((event['event_type'], prefix['query_phase'], prefix['active_query_id']))
        assert ('query_dispatched', 'awaiting_answer', 'q000001') in observed
        assert ('answer_received', 'answer_committed', 'q000001') in observed
        assert ('query_completed', 'analyzing', None) in observed
        assert observed[-1] == ('run_finished', 'completed', None)
    finally:
        store.close()


@pytest.mark.parametrize('reason', ['no_query', 'max_questions', 'volume_confidence'])
def test_terminal_cannot_skip_first_actual_singleton_stop(reason):
    events = [{'event_type': 'state_analyzed', 'payload': state(('z-first',), (1.,), index=5)},
              {'event_type': 'run_finished', 'payload': {'termination_reason': reason}}]
    with pytest.raises(DocumentError, match='precedence'):
        verify_actual_policy(events, algorithm({'rule': 'volume_confidence', 'threshold': .2}), {'max_queries': 5}, ['z-first', 'a-second'])
