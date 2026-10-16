"""Real SDK answer prefixes with constructed, explicitly unqualified provenance.

These tests check proof transport and admission, not platform certification or
power-loss behavior. Origin bytes always live in the temporary marked project.
"""
from copy import deepcopy
import shutil
from uuid import uuid4

import pytest

import otqa
from otqa._build_metadata import inventory_digest
from otqa.answers import SimulatedAnswers
from otqa.application_types import ContinuationExportRequest
from otqa.runtime.case import timings
from otqa.runtime.codec import DocumentError, decode, digest, encode, mathematical_hex, read_json, utc_now
from otqa.runtime.continuation import export_continuation, import_continuation, verify_continuation_document
from otqa.runtime.documents import file_ref, materialize_inputs, resolve_ref
from otqa.runtime.journal import verify_prefix
from otqa.runtime.serialization import domain_inputs, mathematical_input_digest
from otqa.runtime.recorder import WireRecorder
from otqa.runtime.storage import RunStore
from otqa.runtime.validation import journal_policy, verify_result

from test_runtime_policy_readers import recorded_result


def origin_fixture(tmp_path, *, boundary='answer_received', larger_problem=False, prior=None):
    """Retain a genuinely confirmed SDK prefix, then construct its interrupted envelope."""
    context, root, manifest, payload, envelope = recorded_result(tmp_path, depth=3, horizon_execution='countdown')
    problem = read_json(root / 'problem.json')
    config = read_json(root / 'config.json')
    oracle = read_json(root / 'oracle.json')
    if larger_problem:
        problem['alternative_ids'].append('middle')
        problem['alternatives'].append([.6, .6])
        oracle['target_weights'] = [.55, .45]
        (root / 'problem.json').write_bytes(encode(problem))
        (root / 'oracle.json').write_bytes(encode(oracle))
        manifest['inputs']['problem'] = file_ref(root / 'problem.json', root)
        manifest['inputs']['oracle'] = file_ref(root / 'oracle.json', root)
    inventory = {'schema_version': 1, 'inventory_format': 'otqa-source-v1',
        'files': [{'path': 'otqa/constructed.py', 'bytes': 0, 'sha256': digest(b'')}]}
    (root / 'inventory.json').write_bytes(encode(inventory))
    manifest['source'] = {**manifest['source'], 'source_sha256': inventory_digest(inventory)}
    manifest['source_inventory'] = file_ref(root / 'inventory.json', root)
    (root / 'environment-lock.txt').write_bytes(b'constructed-test-environment\n')
    profile = {'schema_version': 1, 'profile_id': 'constructed-continuation-profile', 'platform_family': 'linux',
        'python_version': 'constructed', 'packages': {}, 'backend_capabilities': {},
        'environment_lock': file_ref(root / 'environment-lock.txt', root),
        'certification': {'status': 'qualifying', 'evidence': None}}
    (root / 'profile.json').write_bytes(encode(profile))
    manifest['execution_profile'] = file_ref(root / 'profile.json', root)
    refs = {name: file_ref(root / filename, root) for name, filename in (
        ('problem', 'problem.json'), ('configuration', 'config.json'), ('oracle', 'oracle.json'),
        ('execution_profile', 'profile.json'))}
    receipt = {'schema_version': 2, 'materialization_id': str(uuid4()), 'created_at_utc': utc_now(),
        'entrypoints': refs, 'entries': [{'document_kind': 'problem', 'source_relative_path': 'problem.json',
            'original': refs['problem'], 'materialized': refs['problem'], 'transformation': 'byte_copy',
            'semantic_sha256': refs['problem']['sha256'], 'reference_map': []}]}
    prior_doc = None
    if prior is None:
        (root / 'materialization_receipt.json').write_bytes(encode(receipt))
    else:
        old_context, previous = prior
        # Real reference rewriting copies the nested immutable origin bytes.
        receipt = materialize_inputs(old_context.project_root,
            {'continuation': ('continuation', previous.continuation_path)}, root, context=context)
        manifest['inputs']['continuation'] = receipt['entrypoints']['continuation']
        prior_doc = read_json(resolve_ref(root, manifest['inputs']['continuation']))
        manifest['execution_kind'] = 'continuation'
        manifest['initial_execution_cursor'] = prior_doc['execution_cursor']
    manifest['materialization_receipt'] = file_ref(root / 'materialization_receipt.json', root)
    intent = {'schema_version': 1, **{key: manifest[key] for key in (
        'run_id', 'attempt_id', 'series_id', 'job_id', 'problem_id', 'configuration_id')},
        'created_at_utc': utc_now(), 'owner_token': 'constructed', 'nonce': 'constructed',
        'controller': manifest['process'], 'materialization_receipt': manifest['materialization_receipt']}
    (root / 'launch_intent.json').write_bytes(encode(intent))
    manifest['launch_intent'] = file_ref(root / 'launch_intent.json', root)
    manifest['mathematical_input_sha256'] = mathematical_input_digest(problem, config, 'simulated', None,
        oracle, None, continuation=prior_doc)
    (root / 'manifest.json').write_bytes(encode(manifest))
    if larger_problem or prior is not None:
        (root / 'events.jsonl').unlink()
        cursor = manifest['initial_execution_cursor']
        store = RunStore(context, root, root, manifest['run_id'], manifest['attempt_id'], manifest['process'],
            cursor['answered_total'], schema_version=2, execution_cursor=cursor)
        recorder = WireRecorder(store, problem['alternative_ids'], stop_aware=False, trace_level='standard')
        recorder.event('run_started', {'manifest_sha256': file_ref(root / 'manifest.json', root)['sha256']}, commit=True)

        def interrupting_recorder(event):
            recorder(event)
            if ((boundary == 'answer_received' and type(event).__name__ == 'AnswerReceived')
                    or (boundary == 'query_dispatched' and type(event).__name__ == 'QueryDispatched')):
                raise KeyboardInterrupt('constructed recorder boundary')

        domain, algorithm, budget, execution, _ = domain_inputs(problem, config, None)
        checkpoint = (import_continuation(resolve_ref(root, manifest['inputs']['continuation']), reference_root=root,
            problem=problem, configuration=config, source=manifest['source'], profile=profile) if prior_doc else None)
        with pytest.raises(KeyboardInterrupt, match='constructed recorder boundary'):
            otqa.solve(domain, algorithm, SimulatedAnswers(oracle['target_weights']), budget=budget,
                execution=execution, continuation=checkpoint, recorder=interrupting_recorder)
        store.close()
    events = [decode(line) for line in (root / 'events.jsonl').read_bytes().splitlines()]
    events[0]['payload']['manifest_sha256'] = file_ref(root / 'manifest.json', root)['sha256']
    events[0]['numeric_hex'] = mathematical_hex(events[0]['payload'], '/payload')
    until = next(index for index, event in enumerate(events, 1) if event['event_type'] == boundary)
    events = events[:until]
    raw = b''.join(encode(event) for event in events)
    (root / 'events.jsonl').write_bytes(raw)
    policy = journal_policy(manifest, root, root / 'manifest.json')
    verified = verify_prefix(raw, len(raw), digest(raw), len(events), **policy)
    envelope.update(execution_status='interrupted', solver_result=None,
        interruption={'reason': 'user_cancel', 'message': 'constructed accepted-boundary interruption'},
        query_counts=verified['query_counts'], error=None, numeric_hex={},
        quality={'status': 'not_selected', 'audit_status': 'not_available', 'true_winner_ids': [],
                 'regret_fraction': None, 'findings': []},
        timings=timings(case_elapsed=1., partial=.5, complete=False),
        journal={'path': 'events.jsonl', 'sha256': digest(raw), 'bytes': len(raw),
            'valid_prefix_bytes': len(raw), 'valid_prefix_sha256': digest(raw),
            'last_good_sequence': len(events), 'trailing_partial_line': False, 'uncommitted_suffix_bytes': 0})
    (root / 'result.json').write_bytes(encode(envelope))
    assert verify_result(root / 'result.json', root, payload) == envelope
    return context, root, manifest, profile, problem, config, envelope


def exported_fixture(tmp_path):
    origin = origin_fixture(tmp_path)
    context, root = origin[:2]
    destination = tmp_path / 'inputs' / 'continuation-bundle'
    exported = export_continuation(ContinuationExportRequest(context, root, root / 'result.json', destination))
    return origin, exported


def test_accepted_answer_before_query_completed_exports_and_imports_real_sdk_phase(tmp_path):
    origin, exported = exported_fixture(tmp_path)
    context, root, manifest, profile, problem, config, _ = origin
    document = exported.continuation
    proof_raw = resolve_ref(context.project_root, document['origin_proof']['journal_prefix']).read_bytes()
    events = [decode(line) for line in proof_raw.splitlines()]
    assert events[-1]['event_type'] == 'answer_received'
    assert not any(event['event_type'] == 'query_completed' for event in events)
    assert document['execution_cursor'] == {'answered_total': 1, 'remaining_depth': 2}
    checkpoint = import_continuation(exported.continuation_path, reference_root=context.project_root,
        problem=problem, configuration=config, source=manifest['source'], profile=profile)
    domain, policy, budget, execution, _ = domain_inputs(problem, config, None)
    continued = otqa.solve(domain, policy, SimulatedAnswers((.7, .3)), continuation=checkpoint,
                           budget=budget, execution=execution)
    full = otqa.solve(domain, policy, SimulatedAnswers((.7, .3)), budget=budget, execution=execution)
    assert continued.answers == full.answers
    assert continued.execution_cursor == full.execution_cursor
    assert continued.selected_candidate_index == full.selected_candidate_index
    if continued.queries:
        assert continued.queries[0].planning.horizon == 2
    assert root.exists()


def test_unanswered_dispatch_is_not_exported_and_leaves_no_bundle(tmp_path):
    context, root, *_ = origin_fixture(tmp_path, boundary='query_dispatched')
    destination = tmp_path / 'inputs' / 'rejected'
    with pytest.raises(DocumentError, match='exportable confirmed answer boundary'):
        export_continuation(ContinuationExportRequest(context, root, root / 'result.json', destination))
    assert not destination.exists()


@pytest.mark.parametrize('field', ['execution_cursor', 'answers'])
def test_declared_phase_and_answers_must_match_immutable_origin_prefix(tmp_path, field):
    origin, exported = exported_fixture(tmp_path)
    context = origin[0]
    document = deepcopy(exported.continuation)
    if field == 'execution_cursor':
        document[field]['remaining_depth'] = 1
    else:
        document[field][0]['answer'] = '<' if document[field][0]['answer'] != '<' else '>'
    with pytest.raises(DocumentError, match='answers or cursor'):
        verify_continuation_document(document, reference_root=context.project_root)


@pytest.mark.parametrize('field', ['problem', 'configuration', 'source', 'profile'])
def test_import_checks_mathematical_inputs_source_and_numerical_profile(tmp_path, field):
    origin, exported = exported_fixture(tmp_path)
    context, _, manifest, profile, problem, config, _ = origin
    arguments = {'problem': deepcopy(problem), 'configuration': deepcopy(config),
                 'source': deepcopy(manifest['source']), 'profile': deepcopy(profile)}
    if field == 'problem':
        arguments[field]['alternatives'][0][0] = .9
    elif field == 'configuration':
        arguments[field]['algorithm']['min_expected_progress'] = .1
    elif field == 'source':
        arguments[field]['source_sha256'] = 'b' * 64
    else:
        arguments[field]['python_version'] = 'other'
    with pytest.raises(DocumentError, match='different|differs|original numerical'):
        import_continuation(exported.continuation_path, reference_root=context.project_root, **arguments)


@pytest.mark.parametrize('field', ['source', 'profile'])
def test_native_import_cannot_disable_environment_admission_with_none(tmp_path, field):
    origin, exported = exported_fixture(tmp_path)
    context, _, manifest, profile, problem, config, _ = origin
    arguments = {'problem': problem, 'configuration': config, 'source': manifest['source'], 'profile': profile}
    arguments[field] = None
    with pytest.raises(DocumentError, match='requires an actual source'):
        import_continuation(exported.continuation_path, reference_root=context.project_root, **arguments)


def test_exported_bundle_is_immutable_self_contained_and_materializable(tmp_path):
    origin, exported = exported_fixture(tmp_path)
    context, root, manifest, profile, problem, config, _ = origin
    document = exported.continuation
    for artifact in document['origin_proof']['artifacts']:
        copied = resolve_ref(context.project_root, artifact['artifact']).read_bytes()
        assert copied == (root / artifact['original_path']).read_bytes()
    shutil.rmtree(root)
    verify_continuation_document(document, reference_root=context.project_root)
    target = tmp_path / 'runs' / 'materialized'
    target.mkdir()
    receipt = materialize_inputs(context.project_root, {'continuation': ('continuation', exported.continuation_path)},
                                  target, context=context)
    admitted_path = resolve_ref(target, receipt['entrypoints']['continuation'])
    admitted = import_continuation(admitted_path, reference_root=target, problem=problem,
        configuration=config, source=manifest['source'], profile=profile)
    assert admitted.execution_cursor.remaining_depth == 2
    assert document == read_json(exported.continuation_path)


def test_manipulated_origin_artifact_hash_is_rejected(tmp_path):
    origin, exported = exported_fixture(tmp_path)
    document = deepcopy(exported.continuation)
    document['origin_proof']['artifacts'][0]['artifact']['sha256'] = 'f' * 64
    with pytest.raises(DocumentError, match='hash differs'):
        verify_continuation_document(document, reference_root=origin[0].project_root)


@pytest.mark.parametrize('field', ['initial_execution_cursor', 'mathematical_input_sha256', 'execution_kind'])
def test_origin_start_must_bind_input_not_just_self_consistent_journal(tmp_path, field):
    origin, exported = exported_fixture(tmp_path)
    context = origin[0]
    document = deepcopy(exported.continuation)
    original = resolve_ref(context.project_root, document['origin_proof']['manifest'])
    manifest = read_json(original)
    if field == 'initial_execution_cursor':
        manifest[field]['remaining_depth'] = 2
    elif field == 'mathematical_input_sha256':
        manifest[field] = 'a' * 64
    else:
        manifest[field] = 'warm_start'
    modified = exported.continuation_path.parent / 'modified-manifest.json'
    modified.write_bytes(encode(manifest))
    document['origin_proof']['manifest'] = file_ref(modified, context.project_root)
    with pytest.raises(DocumentError, match='starting cursor|starting identity|execution kind'):
        verify_continuation_document(document, reference_root=context.project_root)


def test_export_refuses_to_replace_existing_bundle(tmp_path):
    origin, exported = exported_fixture(tmp_path)
    context, root = origin[:2]
    before = exported.continuation_path.read_bytes()
    with pytest.raises(DocumentError, match='already exists'):
        export_continuation(ContinuationExportRequest(context, root, root / 'result.json', exported.continuation_path.parent))
    assert exported.continuation_path.read_bytes() == before


def test_second_native_continuation_verifies_recursive_phase_and_provenance(tmp_path):
    first_dir = tmp_path / 'first'
    first_dir.mkdir()
    first = origin_fixture(first_dir, larger_problem=True)
    context, root = first[:2]
    checkpoint1 = export_continuation(ContinuationExportRequest(context, root, root / 'result.json',
        first_dir / 'inputs' / 'first-checkpoint'))
    second_dir = tmp_path / 'second'
    second_dir.mkdir()
    second = origin_fixture(second_dir, larger_problem=True, prior=(context, checkpoint1))
    second_context, second_root, manifest, profile, problem, config, _ = second
    checkpoint2 = export_continuation(ContinuationExportRequest(second_context, second_root, second_root / 'result.json',
        second_dir / 'inputs' / 'second-checkpoint'))
    assert checkpoint2.continuation['execution_cursor'] == {'answered_total': 2, 'remaining_depth': 1}
    assert len(checkpoint2.continuation['answers']) == 2
    shutil.rmtree(first_dir)
    shutil.rmtree(second_root)
    admitted = import_continuation(checkpoint2.continuation_path, reference_root=second_context.project_root,
        problem=problem, configuration=config, source=manifest['source'], profile=profile)
    assert admitted.execution_cursor == otqa.ExecutionCursor(2, 1)
