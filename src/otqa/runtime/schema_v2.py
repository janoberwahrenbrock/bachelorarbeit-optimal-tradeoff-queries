"""Version-two execution contracts; historical definitions remain frozen."""
from __future__ import annotations
from copy import deepcopy
from . import schema_v1 as old

BASE = 'urn:otqa:v2:'
KINDS = frozenset(('config', 'manifest', 'event', 'result', 'progress', 'partial_snapshot',
                   'summary', 'series_plan', 'series_state', 'materialization_receipt'))


def definitions():
    def rewrite(value):
        if isinstance(value, dict):
            return {k: (v.replace(old.BASE, BASE) if k == '$ref' else rewrite(v)) for k, v in value.items()}
        if isinstance(value, (list, tuple)):
            return [rewrite(v) for v in value]
        return value
    d, all_docs = rewrite(deepcopy(old.definitions()))
    docs = {k: v for k, v in all_docs.items() if k in KINDS}
    obj, arr, num, integer, nullable, choices = old.object_of, old.array_of, old.number, old.integer, old.nullable, old.choices
    def r(name):
        return {'$ref': BASE + 'common#/$defs/' + name}
    def extend(name, fields):
        value = d[name]
        value['properties'].update(fields)
        value['required'].extend(k for k in fields if k not in value['required'])
    for name, doc in docs.items():
        if name != 'event':
            doc['properties']['schema_version'] = {'const': 2}
    d['AlgorithmPolicy']['properties']['min_expected_progress'] = nullable(num(0))
    d['AlgorithmPolicy']['required'] += ['horizon_execution', 'min_expected_progress']
    d['AlgorithmPolicy']['properties']['horizon_execution'].pop('default', None)
    d['ExecutionCursor'] = obj({'answered_total': integer(), 'remaining_depth': integer(1, 3)})
    d['ProgressEvidence'] = obj({'basis': choices('candidate_count', 'effective_loss'),
        'starting_value': num(0), 'expected_terminal_value': num(), 'expected_progress': num(),
        'threshold': nullable(num(0)), 'comparison': {'const': 'strict_greater'}, 'admissible': old.BOOL})
    outcome = choices('available', 'no_query', 'insufficient_expected_progress')
    d['HorizonSelectionEvidence'] = obj({'horizon': integer(1, 3), 'generated_query_count': integer(),
        'evaluated_query_count': integer(), 'outcome': outcome, 'selected_plan': nullable(r('Planning')),
        'selected_progress': nullable(r('ProgressEvidence')), 'best_progress_witness': nullable(r('Planning')),
        'best_progress': nullable(r('ProgressEvidence'))})
    d['PlanningAttempt'] = obj({'requested_depth': integer(1, 3), 'evaluated_horizons': arr(integer(1, 3), 1, unique=True),
        'outcome': outcome, 'selected_plan': nullable(r('Planning')), 'selected_progress': nullable(r('ProgressEvidence')),
        'best_progress_witness': nullable(r('Planning')), 'horizon_evidence': arr(r('HorizonSelectionEvidence'), 1)})
    d['PlanningCycle'] = obj({'cursor_before': r('ExecutionCursor'), 'attempts': arr(r('PlanningAttempt'), 1),
        'selected_plan': nullable(r('Planning')), 'outcome': outcome,
        'restart_reason': nullable(choices('no_query', 'insufficient_expected_progress')),
        'proposed_cursor_after_answer': nullable(r('ExecutionCursor'))})
    extend('State', {'execution_cursor': r('ExecutionCursor')})
    extend('QueryRecord', {'planning_cycle': r('PlanningCycle')})
    reasons = choices('exact_single_candidate', 'volume_confidence', 'no_query', 'max_questions', 'insufficient_expected_progress')
    d['SolverResult']['properties']['termination_reason'] = reasons
    extend('SolverResult', {'execution_cursor': r('ExecutionCursor'), 'planning_cycles': arr(r('PlanningCycle'))})
    manifest = docs['manifest']['properties']
    manifest['execution_kind'] = choices('fresh', 'warm_start', 'continuation', 'replay')
    manifest['inputs']['properties']['continuation'] = nullable(r('FileRef'))
    manifest['inputs']['required'].append('continuation')
    manifest['initial_execution_cursor'] = r('ExecutionCursor')
    docs['manifest']['required'].append('initial_execution_cursor')
    for kind in ('progress', 'partial_snapshot'):
        docs[kind]['properties']['execution_cursor'] = nullable(r('ExecutionCursor'))
        docs[kind]['required'].append('execution_cursor')
    variants = docs['event']['oneOf']
    for variant in variants:
        variant['properties']['schema_version'] = {'const': 2}
        event_type = variant['properties']['event_type']['const']
        payload = variant['properties']['payload']
        if event_type == 'answer_received':
            payload['properties']['execution_cursor'] = r('ExecutionCursor')
            payload['required'].append('execution_cursor')
        if event_type == 'run_started':
            payload['properties']['execution_cursor'] = r('ExecutionCursor')
            payload['required'].append('execution_cursor')
        if event_type == 'run_finished':
            payload['properties']['termination_reason'] = reasons
            payload['properties']['execution_cursor'] = r('ExecutionCursor')
            payload['required'].append('execution_cursor')
    proto = deepcopy(variants[0])
    for name, payload in (
        ('planning_attempt_started', obj({'state_before_index': integer(), 'execution_cursor': r('ExecutionCursor'),
            'attempt_index': integer(1, 2), 'requested_depth': integer(1, 3)})),
        ('planning_attempt_completed', obj({'state_before_index': integer(), 'execution_cursor': r('ExecutionCursor'),
            'attempt_index': integer(1, 2), 'attempt': r('PlanningAttempt')})),
        ('planning_resolved', obj({'state_before_index': integer(), 'cycle': r('PlanningCycle')}))):
        item = deepcopy(proto)
        item['properties']['event_type'] = {'const': name}
        item['properties']['payload'] = payload
        variants.append(item)
    row_fields = {'query_strategy': choices('fixed', 'reduction_per_query'), 'horizon_execution': choices('receding', 'countdown'),
        'depth': integer(1, 3), 'min_expected_progress': nullable(num(0)),
        'planning_attempts_started': nullable(integer()), 'planning_attempts_completed': nullable(integer()),
        'fallback_selections': nullable(integer()), 'terminal_expected_progress': nullable(num()), 'terminal_planning_depth': nullable(integer(1, 3))}
    d['SummaryRow']['properties']['termination_reason'] = nullable(reasons)
    extend('SummaryRow', row_fields)
    extend('SummaryGroup', {k: v for k, v in row_fields.items() if k in ('query_strategy', 'horizon_execution', 'depth', 'min_expected_progress')})
    extend('SummaryGroup', {'insufficient_expected_progress': integer()})
    receipt = docs['materialization_receipt']['properties']['entries']['items']['properties']['document_kind']
    receipt['enum'] += ['continuation', 'manifest', 'source_inventory']
    return d, docs


def continuation_schema():
    def r(name):
        return {'$ref': BASE + 'common#/$defs/' + name}
    return old.object_of({'schema_version': {'const': 1}, 'algorithm_contract': {'const': 'otqa-execution-v2'},
        'problem': r('FileRef'), 'configuration': r('FileRef'), 'answers': old.array_of(r('AnsweredQuery')),
        'execution_cursor': r('ExecutionCursor'),
        'origin_proof': old.object_of({'manifest': r('FileRef'), 'journal_prefix': r('FileRef'),
            'valid_prefix_bytes': old.integer(), 'valid_prefix_sha256': old.HASH, 'last_good_sequence': old.integer(1),
            'artifacts': old.array_of(old.object_of({'original_path': old.PATH, 'artifact': r('FileRef')}), 1)})})
