"""Independent stdlib raw checker for frozen v3 standalone studies.

No otqa import, solver call, LP/geometry calculation, remote access, or Git write.
The output is provisional evidence for peer review, never a completion marker.
Journal/progress arithmetic derives from the historical independently tested
checker; configuration, source, materialization and standalone exports are bound
again here. Recorded geometric values and inventory counts are NOT recertified.
"""
from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
import csv
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import io
import json
import math
import os
from pathlib import Path, PurePosixPath
import re
import statistics
import time
import zipfile

ROOT = Path('/Users/janoberwahrenbrock/Code/bachelorarbeit-optimal-tradeoff-queries')
E = ROOT / 'runs/five-host-study-execution-20261017T2200Z'
SOURCE = '720726607ae451b319e59e01453b6ba69b9950ef42420e700ed6b4eaa5b34d0e'
COMMIT = '62d1d01339f91802e2916b63660a4e640d99c9cc'
WHEEL = '24e4a5c901690895bdb1557a5a90ef1e9d5f6d3eb06381df58031d8ce02f1a97'
NUMERICS = '1374fa8394bffe9b7f84585b29ea2a0b353f105500f28f6b2c6a79fbcec4a56c'
FILES = {}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def decode(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError('Duplicate JSON key: ' + key)
            result[key] = value
        return result
    def finite(text):
        value = float(text)
        if not math.isfinite(value):
            raise ValueError('Nonfinite JSON value')
        return value
    if raw.startswith(b'\xef\xbb\xbf'):
        raise ValueError('UTF8 BOM is not permitted')
    return json.loads(raw, object_pairs_hook=pairs, parse_float=finite,
                      parse_constant=lambda text: (_ for _ in ()).throw(ValueError(text)))


def file_bytes(path):
    path = Path(path).absolute()
    for part in (path, *path.parents):
        if part.is_symlink():
            raise ValueError('Symlink raw path: ' + str(part))
    data = path.read_bytes()
    evidence = {'sha256': sha(data), 'bytes': len(data)}
    if path in FILES and FILES[path] != evidence:
        raise ValueError('Artifact changed during raw verification: ' + str(path))
    FILES[path] = evidence
    return data


def read(path):
    return decode(file_bytes(path))


def resolve(base, reference):
    raw = reference['path']
    relative = PurePosixPath(raw)
    if relative.is_absolute() or relative.as_posix() != raw or '..' in relative.parts:
        raise ValueError('Unsafe artifact reference: ' + raw)
    path = Path(base) / relative
    if sha(file_bytes(path)) != reference['sha256']:
        raise ValueError('Artifact SHA differs: ' + raw)
    return path


def require(ok, message):
    if not ok:
        raise ValueError(message)


def fraction(value):
    return Fraction.from_float(float(value))


def utc_stamp(value, label):
    require(isinstance(value, str) and re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z', value),
            'Missing/malformed native UTC timestamp: ' + label)
    parsed = datetime.fromisoformat(value[:-1] + '+00:00')
    require(parsed.utcoffset().total_seconds() == 0, 'Native timestamp is not UTC: ' + label)
    return parsed


def check_hex(document):
    for pointer, expected in document.get('numeric_hex', {}).items():
        value = document
        for key in pointer.lstrip('/').split('/'):
            key = key.replace('~1', '/').replace('~0', '~')
            value = value[int(key)] if isinstance(value, list) else value[key]
        require(float(value).hex() == expected, 'Stored binary64 evidence differs')
    scalar = {'value', 'probability', 'expected_terminal_candidates', 'expected_terminal_loss',
              'expected_queries', 'gain', 'rate', 'min_expected_progress', 'starting_value',
              'expected_terminal_value', 'expected_progress', 'threshold', 'maximum_volume_share',
              'selected_candidate_volume', 'selected_candidate_volume_share'}
    containers = {'candidate_volumes', 'candidate_volume_shares', 'answer_probabilities',
                  'lexicographic_expected_values'}
    expected_map = {}
    def visit(value, pointer, mathematical=False):
        if mathematical and type(value) in (int, float):
            require(math.isfinite(float(value)), 'Nonfinite mathematical value')
            expected_map[pointer] = float(value).hex()
        elif isinstance(value, dict):
            for key, child in value.items():
                if key in ('numeric_hex', 'error', 'context', 'telemetry_errors'):
                    continue
                escaped = key.replace('~', '~0').replace('/', '~1')
                visit(child, pointer + '/' + escaped, mathematical or key in scalar or key in containers)
        elif isinstance(value, list):
            for index, child in enumerate(value):
                visit(child, pointer + '/' + str(index), mathematical)
    if 'solver_result' in document:
        visit(document['solver_result'], '/solver_result')
    elif 'payload' in document:
        visit(document['payload'], '/payload')
    else:
        return
    require(document.get('numeric_hex') == expected_map, 'Missing or unexpected binary64 evidence')


def verify_attempt(attempt, algorithm, count):
    depth = attempt['requested_depth']
    expected = [depth] if algorithm['query_strategy'] == 'fixed' else list(range(1, depth + 1))
    require(attempt['evaluated_horizons'] == expected, 'Required horizon omitted')
    require([h['horizon'] for h in attempt['horizon_evidence']] == expected, 'Horizon evidence differs')
    available = []
    gains = []
    for h in attempt['horizon_evidence']:
        require(type(h['generated_query_count']) is int and h['generated_query_count'] >= 0,
                'Invalid generated query count')
        require(h['generated_query_count'] == h['evaluated_query_count'], 'Generated query was not evaluated')
        if h['outcome'] == 'no_query':
            require(h['evaluated_query_count'] == 0 and h['best_progress_witness'] is None and h['selected_plan'] is None, 'NoQuery has evaluated options')
            continue
        witness = h['best_progress_witness']['selected']
        score = witness['score']
        gain = float(count) - score['expected_terminal_candidates']
        progress = h['best_progress']
        require(progress['basis'] == 'candidate_count' and progress['starting_value'] == float(count)
            and progress['expected_terminal_value'] == score['expected_terminal_candidates']
            and progress['expected_progress'] == gain and progress['threshold'] == .001
            and progress['comparison'] == 'strict_greater' and progress['admissible'] == (gain > .001), 'Progress witness arithmetic/policy differs')
        require(witness['horizon'] == h['horizon'] and h['evaluated_query_count'] > 0, 'Witness horizon/inventory differs')
        gains.append(gain)
        if h['outcome'] == 'available':
            chosen = h['selected_plan']['selected']
            require(chosen['horizon'] == h['horizon'], 'Chosen horizon differs')
            selected_gain = float(count) - chosen['score']['expected_terminal_candidates']
            require(selected_gain > .001 and selected_gain <= gain, 'Dispatched plan violates threshold/maximum witness')
            require(h['selected_progress']['expected_progress'] == selected_gain, 'Selected progress differs')
            available.append(chosen)
        else:
            require(h['outcome'] == 'insufficient_expected_progress' and gain <= .001 and h['selected_plan'] is None, 'Inconsistent rejected horizon')
    expected_outcome = 'available' if available else 'insufficient_expected_progress' if gains else 'no_query'
    require(attempt['outcome'] == expected_outcome, 'Attempt outcome differs from its complete horizon evidence')
    if available:
        chosen = attempt['selected_plan']['selected']
        require(chosen in available, 'Chosen plan absent from horizon evidence')
        chosen_horizon = next(h for h in attempt['horizon_evidence'] if h['horizon'] == chosen['horizon'])
        require(attempt['selected_progress'] == chosen_horizon['selected_progress'],
                'Attempt selected progress differs from its selected horizon')
        if algorithm['query_strategy'] == 'reduction_per_query':
            def rank(plan):
                score, q = plan['score'], plan['query']
                gain = float(count) - score['expected_terminal_candidates']
                require(math.isfinite(score['expected_queries']) and score['expected_queries'] > 0,
                        'Adaptive expected query count is not positive')
                require(score['gain'] == gain and score['rate'] == gain / score['expected_queries'], 'Adaptive rate arithmetic differs')
                return (-score['rate'], score['expected_queries'], plan['horizon'], q['goal_index_a'], q['goal_index_b'], q['value'])
            require(chosen == min(available, key=rank), 'Adaptive horizon winner differs')
    else:
        require(attempt['selected_plan'] is None, 'Terminal attempt retains a selected plan')


def verify_job(series, job, attempt, protocol):
    series = Path(series).resolve(strict=True)
    result_path = resolve(series, attempt['result'])
    result = read(result_path)
    check_hex(result)
    started_at = utc_stamp(result['started_at_utc'], 'result.started_at_utc')
    finished_at = utc_stamp(result['finished_at_utc'], 'result.finished_at_utc')
    require(started_at <= finished_at, 'Wall-clock case ordering anomaly requires explicit review')
    directory = result_path.parent
    manifest = read(directory / 'manifest.json') if (directory / 'manifest.json').exists() else None
    configuration = read(resolve(series, job['configuration']))
    cid = configuration['configuration_id']
    mode, grid = protocol['mode'], protocol['grid']
    require(configuration == protocol['configuration'], 'Frozen v3 configuration changed')
    problem, oracle = (read(resolve(series, job[k])) for k in ('problem', 'oracle'))
    dimensions = len(problem['objective_ids'])
    require(dimensions in (3, 5, 7) and len(problem['alternative_ids']) == 5,
        'Unexpected objective or alternative count')
    require(dimensions == int(job['case_id'].split('-')[0][1:]), 'Case ID and mathematical dimension differ')
    require(problem['problem_id'] == oracle['problem_id'] == job['case_id'], 'Problem/oracle identity differs')
    weights = [fraction(w) for w in oracle['target_weights']]
    require(len(weights) == dimensions and all(w >= 0 for w in weights)
        and all(len(row) == dimensions for row in problem['alternatives']), 'Input dimensions differ')
    utilities = [sum((fraction(x) * w for x, w in zip(row, weights)), Fraction()) for row in problem['alternatives']]
    winners = [aid for aid, u in zip(problem['alternative_ids'], utilities) if u == max(utilities)]
    solver = result['solver_result']
    require(result['execution_status'] in ('completed', 'failed', 'interrupted'), 'Nonterminal attempt')
    require((result['execution_status'] == 'completed') == (solver is not None), 'Status/result presence differs')
    selected = solver['selected_candidate_id'] if solver else None
    quality = 'not_selected' if selected is None else 'correct' if selected in winners else 'incorrect'
    require(result['quality']['status'] == quality, 'Stored winner quality differs from rational oracle calculation')
    require(result['schema_version'] == 2, 'Study result is not the v2 execution contract')
    require(result['execution_stage'] in ('solver', 'bootstrap'), 'Unknown execution stage')
    if result['execution_status'] == 'completed':
        require(result['error'] is None and result['interruption'] is None
                and result['timings']['complete_api_measurement']
                and result['timings']['api_call_wall_seconds'] is not None
                and result['finalized_by'] == 'case_process', 'Invalid completed result envelope')
    elif result['execution_status'] == 'failed':
        require(result['error'] is not None and result['interruption'] is None, 'Invalid failed envelope')
    else:
        require(result['error'] is None and result['interruption'] is not None
                and not result['timings']['complete_api_measurement'], 'Invalid interrupted envelope')
    require(result['problem_id'] == job['case_id'] and result['configuration_id'] == cid
        and result['attempt_id'] == attempt['attempt_id'], 'Result identity differs from mapped attempt')
    if 'run_id' in attempt:
        require(result['run_id'] == attempt['run_id'], 'Result run identity differs')
    if 'execution_status' in attempt:
        require(result['execution_status'] == attempt['execution_status'], 'Attempt/result status differs')
    timings = result['timings']
    require(timings['scope_version'] == 1 and type(timings['complete_api_measurement']) is bool
            and timings['complete_api_measurement'] == (timings['api_call_wall_seconds'] is not None),
            'API measurement scope/completeness differs')
    for key, value in timings.items():
        if key in ('scope_version', 'complete_api_measurement'):
            continue
        require(value is None or type(value) in (int, float) and math.isfinite(value) and value >= 0,
            'Invalid elapsed time')
    if timings['case_elapsed_seconds'] is not None and timings['api_call_wall_seconds'] is not None:
        require(timings['case_elapsed_seconds'] >= timings['api_call_wall_seconds'],
                'Case scope is shorter than included API measurement')
    row = {'case_id': job['case_id'], 'configuration_id': cid, 'mode': mode, 'grid': grid,
        'objectives': dimensions,
        'status': result['execution_status'], 'solved': bool(solver and solver['solved']), 'quality': quality,
        'winner_ids': winners, 'selected_candidate_id': selected,
        'termination_reason': solver['termination_reason'] if solver else None,
        'queries': result['query_counts']['answered_new'], 'api_seconds': timings['api_call_wall_seconds'],
        'partial_api_seconds': timings.get('partial_api_elapsed_seconds'),
        'case_seconds': timings['case_elapsed_seconds'], 'result_ref': attempt['result'],
        'attempt_id': attempt['attempt_id'], 'controller_seconds': attempt['controller_elapsed_seconds'],
        'candidate_count_path': [], 'expected_candidates': [], 'actual_horizons': [], 'fallbacks': 0,
        'successful_fallbacks': 0, 'unsuccessful_fallbacks': 0,
        'fallback_attempts_started': 0, 'fallback_attempts_completed': 0,
        'attempts_started': 0, 'attempts_completed': 0, 'answers_checked': 0, 'error': result['error'], 'interruption': result['interruption'],
        'initial_singleton': False, 'initial_candidate_count': None, 'stagnant_answer_steps': 0,
        'error_code': result['error'].get('code') if result['error'] else None,
        'state_winner_lost_indices': [],
        'started_at_utc': result.get('started_at_utc'), 'finished_at_utc': result.get('finished_at_utc')}
    proof = result['journal']
    if proof is None:
        require(result['execution_stage'] == 'bootstrap' and solver is None, 'Missing solver journal')
        require(all(result['query_counts'][key] == 0 for key in
            ('initial_answers', 'dispatched_new', 'answered_new', 'answered_total')),
            'Bootstrap failure has unverified answers')
        return row
    require(result['quality'].get('true_winner_ids', winners) == winners, 'Stored true-winner identities differ')
    require(result['quality'].get('audit_status', 'passed') == 'passed' and not result['quality'].get('findings', []), 'Native oracle consistency findings are unresolved')
    if selected is not None:
        regret = str(max(utilities) - utilities[problem['alternative_ids'].index(selected)])
        require(result['quality'].get('regret_fraction', regret) == regret, 'Stored rational regret differs')
    require(manifest is not None and manifest['source'] == protocol['source'], 'Source differs from frozen study')
    for key in ('run_id', 'attempt_id', 'problem_id', 'configuration_id'):
        require(manifest[key] == result[key], 'Manifest/result direct identity differs: ' + key)
    manifest_created = utc_stamp(manifest['created_at_utc'], 'manifest.created_at_utc')
    require(started_at <= manifest_created <= finished_at,
            'Wall-clock manifest ordering anomaly requires explicit review')
    inventory = read(resolve(series, manifest['source_inventory']))
    require(sha(canonical(inventory)) == protocol['source']['source_sha256'], 'Source inventory content differs from frozen source identity')
    require(manifest['effective_algorithm'] == configuration['algorithm'], 'Manifest policy differs')
    require(manifest['effective_execution'] == configuration['execution'], 'Manifest worker/thread profile differs')
    for key in ('budget', 'recording'):
        require(manifest['effective_' + key] == configuration[key], 'Manifest budget/recording differs')
    if '_native_execution_profile' in protocol:
        require(manifest['execution_profile'] == protocol['_native_execution_profile'],
            'Manifest execution profile differs')
    require(manifest['initial_execution_cursor'] == {'answered_total': 0, 'remaining_depth': 2}, 'Study has nonempty initial history/phase')
    for key in ('problem', 'oracle', 'configuration'):
        require(manifest['inputs'][key] == job[key], 'Manifest frozen input differs from mapped job')
    raw = file_bytes(resolve(series, {'path': proof['path'], 'sha256': proof['sha256']}))
    prefix = raw[:proof['valid_prefix_bytes']]
    require(len(raw) == proof['bytes'] and sha(prefix) == proof['valid_prefix_sha256']
        and proof['uncommitted_suffix_bytes'] == len(raw) - len(prefix) and prefix.endswith(b'\n'), 'Journal hash/size proof differs')
    events = [decode(line) for line in prefix.splitlines()]
    require(proof['trailing_partial_line'] == bool(raw and not raw.endswith(b'\n')),
            'Trailing journal line metadata differs')
    require(len(events) == proof['last_good_sequence'], 'Prefix sequence count differs')
    require(events[0]['payload']['manifest_sha256'] == sha((directory / 'manifest.json').read_bytes()), 'Start does not bind manifest')
    cursor = {'answered_total': 0, 'remaining_depth': 2}
    completed_attempts, started, cycle, state = [], None, None, None
    accepted, records, planned, cycles = [], [], {}, []
    dispatched, answered = set(), set()
    terminal_event = None
    active_query = None
    clock = -1
    wall_clock = manifest_created
    for sequence, event in enumerate(events, 1):
        require(terminal_event is None, 'Event follows terminal event')
        require(event['schema_version'] == 2 and event['sequence'] == sequence, 'Event version/sequence differs')
        require(event['run_id'] == result['run_id'] and event['attempt_id'] == result['attempt_id'], 'Event identity differs')
        require(type(event['monotonic_ns']) is int and event['monotonic_ns'] >= max(0, clock),
                'Event monotonic clock invalid/regressed')
        clock = event['monotonic_ns']
        occurred = utc_stamp(event['occurred_at_utc'], 'journal.occurred_at_utc')
        # UTC ordering is a review gate for clock anomalies, never a duration
        # measurement or a claim that operating-system wall clocks cannot step.
        require(wall_clock <= occurred <= finished_at, 'Wall-clock journal ordering anomaly requires explicit review')
        wall_clock = occurred
        check_hex(event)
        kind, p = event['event_type'], event['payload']
        if kind == 'run_started':
            require(sequence == 1 and p['execution_cursor'] == cursor, 'Unexpected start phase')
        elif kind == 'state_analyzed':
            state = p
            require(p['state_index'] == len(accepted) and p['execution_cursor'] == cursor, 'State/cursor differs from accepted history')
            require(p['state_index'] == len(row['candidate_count_path'])
                    and len(p['candidate_ids']) == len(set(p['candidate_ids']))
                    and bool(p['candidate_ids']) and set(p['candidate_ids']).issubset(problem['alternative_ids']),
                    'State index/candidate identity differs')
            row['candidate_count_path'].append(len(p['candidate_ids']))
            if not set(winners).intersection(p['candidate_ids']):
                row['state_winner_lost_indices'].append(p['state_index'])
        elif kind == 'planning_attempt_started':
            require(active_query is None and cycle is None and state is not None,
                    'Planning attempt started during an open query/cycle or before actual state')
            require(started is None and p['attempt_index'] == len(completed_attempts) + 1 and p['execution_cursor'] == cursor, 'Attempt start phase/ordinal differs')
            expected = cursor['remaining_depth'] if not completed_attempts else 2
            if completed_attempts:
                require(mode == 'countdown' and cursor['remaining_depth'] < 2 and completed_attempts[0]['outcome'] != 'available', 'Illegal fallback')
            require(p['requested_depth'] == expected, 'Requested depth differs from explicit cursor')
            started = p
            row['attempts_started'] += 1
            if p['attempt_index'] == 2:
                row['fallback_attempts_started'] += 1
        elif kind == 'planning_attempt_completed':
            require(started is not None and p['attempt_index'] == started['attempt_index']
                and p['attempt']['requested_depth'] == started['requested_depth'], 'Attempt completion lacks its start')
            verify_attempt(p['attempt'], configuration['algorithm'], len(state['candidate_ids']))
            completed_attempts.append(p['attempt'])
            started = None
            row['attempts_completed'] += 1
            if p['attempt_index'] == 2:
                row['fallback_attempts_completed'] += 1
        elif kind == 'planning_resolved':
            require(cycle is None and state is not None, 'Duplicate or stateless resolved cycle')
            cycle = p['cycle']
            require(started is None and cycle['attempts'] == completed_attempts and cycle['cursor_before'] == cursor, 'Resolved attempts/cursor differ')
            fallback = mode == 'countdown' and cursor['remaining_depth'] < 2 and completed_attempts[0]['outcome'] != 'available'
            require(len(completed_attempts) == (2 if fallback else 1), 'Required full-depth fallback missing or repeated')
            require(cycle['restart_reason'] == (completed_attempts[0]['outcome'] if fallback else None), 'Fallback reason differs')
            require(cycle['outcome'] == completed_attempts[-1]['outcome'] and cycle['selected_plan'] == completed_attempts[-1]['selected_plan'], 'Cycle selection differs')
            cycles.append(cycle)
            if fallback:
                row['fallbacks'] += 1
                row['successful_fallbacks' if cycle['outcome'] == 'available' else 'unsuccessful_fallbacks'] += 1
        elif kind == 'query_planned':
            require(active_query is None and event['query_id'] == f'q{len(accepted) + 1:06d}',
                    'Actual query ordinal/open phase differs')
            require(cycle is not None and cycle['outcome'] == 'available' and p['planning'] == cycle['selected_plan'], 'Query has no selected actual cycle')
            require(event['query_id'] not in planned, 'Repeated actual query identity')
            planned[event['query_id']] = p['planning']['selected']
            active_query = event['query_id']
            row['actual_horizons'].append(p['planning']['selected']['horizon'])
            row['expected_candidates'].append(p['planning']['selected']['score']['expected_terminal_candidates'])
        elif kind == 'query_dispatched':
            qid = event['query_id']
            require(qid == active_query and p['dispatched_new'] == len(dispatched) + 1,
                    'Dispatch phase/count differs')
            require(qid in planned and qid not in dispatched and p['query'] == planned[qid]['query'], 'Dispatch differs from planned query')
            dispatched.add(qid)
        elif kind == 'answer_received':
            q = p['query']
            require(type(q['goal_index_a']) is type(q['goal_index_b']) is int
                and 0 <= q['goal_index_a'] < dimensions and 0 <= q['goal_index_b'] < dimensions
                and q['goal_index_a'] != q['goal_index_b'] and math.isfinite(q['value']) and q['value'] > 0,
                'Invalid actual query')
            require(event['query_id'] in dispatched and event['query_id'] not in answered, 'Answer lacks one unique dispatch')
            answered.add(event['query_id'])
            delta = weights[q['goal_index_a']] - fraction(q['value']) * weights[q['goal_index_b']]
            expected = '<' if delta < 0 else '>' if delta > 0 else '='
            require(p['answer'] == expected, 'Stored answer differs from exact rational oracle comparison')
            require(q == planned[event['query_id']]['query'], 'Answered query differs from actual plan')
            accepted.append({**q, 'answer': p['answer']})
            require(p['answered_new'] == p['answered_total'] == len(accepted), 'Answer event count differs')
            h = planned[event['query_id']]['horizon']
            cursor = {'answered_total': len(accepted), 'remaining_depth': h - 1 if mode == 'countdown' and h > 1 else 2}
            require(p['execution_cursor'] == cursor and cycle['proposed_cursor_after_answer'] == cursor, 'Answer consumed wrong countdown phase')
            row['answers_checked'] += 1
        elif kind == 'query_completed':
            require(event['query_id'] == active_query == p['query_id']
                    and active_query in answered
                    and p['state_before_index'] == len(accepted) - 1
                    and p['state_after_index'] == len(accepted) == state['state_index']
                    and state['last_answer_query_id'] == active_query
                    and p['query'] == planned[active_query]['query']
                    and p['answer'] == accepted[-1]['answer'] and p['planning'] == cycle['selected_plan'],
                    'Query completion does not bind the actual answer and successor state')
            require(p['planning_cycle'] == cycle, 'Query record lost its cycle')
            records.append(p)
            completed_attempts, started, cycle = [], None, None
            active_query = None
        elif kind == 'run_finished':
            terminal_event = kind
            require(active_query is None and event['query_id'] is None
                    and p['query_counts'] == result['query_counts']
                    and p['termination_reason'] == solver['termination_reason']
                    and p['solved'] == solver['solved'], 'Terminal decision/counts differ')
            require(result['execution_status'] == 'completed', 'Success event differs from envelope status')
            require(p['execution_cursor'] == cursor, 'Terminal cursor differs')
            reason = p['termination_reason']
            if reason in ('no_query', 'insufficient_expected_progress'):
                require(cycle is not None and cycle['outcome'] == reason, 'Planning terminal lacks evidence')
            else:
                require(reason == 'exact_single_candidate' and len(state['candidate_ids']) == 1, 'Unexpected success/limit/confidence termination')
        elif kind in ('run_failed', 'run_interrupted'):
            terminal_event = kind
            require(result['execution_status'] == ('failed' if kind == 'run_failed' else 'interrupted'), 'Failure event differs from envelope status')
        else:
            raise ValueError('Unknown version-two journal event: ' + kind)
    counts = result['query_counts']
    require(counts['initial_answers'] == 0 and counts['answered_new'] == counts['answered_total'] == len(accepted), 'Actual answer counters differ')
    require(counts['dispatched_new'] == len(dispatched), 'Actual dispatch counters differ')
    if result['execution_status'] == 'completed':
        require(terminal_event == 'run_finished', 'Completed run has no terminal journal event')
    if solver:
        require(solver['answered_queries'] == accepted and solver['query_records'] == records and solver['planning_cycles'] == cycles, 'Result histories differ from raw journal')
        require(solver['execution_cursor'] == cursor and counts['dispatched_new'] == len(accepted), 'Completed cursor/dispatch count differs')
        require(solver['final_state'] == state, 'Final actual state differs')
        require(solver['termination_reason'] in ('exact_single_candidate', 'no_query', 'insufficient_expected_progress'), 'Unexpected study termination')
        require(solver['solved'] == (solver['termination_reason'] == 'exact_single_candidate'), 'Solved flag contradicts stop reason')
        require((len(state['candidate_ids']) == 1) == (solver['termination_reason'] == 'exact_single_candidate'),
                'Actual singleton must stop before a regular planning termination')
        if solver['solved']:
            require(solver['termination_reason'] == 'exact_single_candidate' and state['candidate_ids'] == [selected], 'Invalid accepted singleton')
            require(solver['exactly_solved'] and selected in winners, 'Accepted singleton is not an exact oracle winner')
        else:
            require(not solver['exactly_solved'] and selected is None, 'Unsolved result claims a selection')
        for field, mapping in [('selected_candidate_volume', 'candidate_volumes'),
                               ('selected_candidate_volume_share', 'candidate_volume_shares')]:
            expected_value = state[mapping].get(selected) if selected is not None and state[mapping] is not None else None
            require(solver[field] == expected_value, 'Selected recorded volume/share differs from final state')
    require(not row['state_winner_lost_indices'], 'Recorded candidate set excludes all exact oracle winners')
    row['initial_singleton'] = bool(row['candidate_count_path'] and row['candidate_count_path'][0] == 1)
    row['initial_candidate_count'] = row['candidate_count_path'][0] if row['candidate_count_path'] else None
    row['final_execution_cursor'] = cursor
    row['last_good_sequence'] = len(events)
    row['journal_ref'] = {'path': proof['path'], 'sha256': proof['sha256']}
    row['manifest_ref'] = {'path': (directory / 'manifest.json').relative_to(series).as_posix(),
        'sha256': sha((directory / 'manifest.json').read_bytes())}
    row['stagnant_answer_steps'] = sum(a == b for a, b in zip(row['candidate_count_path'], row['candidate_count_path'][1:]))
    return row


def float_projection(value):
    if isinstance(value, float):
        require(math.isfinite(value), 'Nonfinite mathematical input')
        return {'float_hex': value.hex()}
    if isinstance(value, dict):
        return {key: float_projection(child) for key, child in value.items()}
    if isinstance(value, list):
        return [float_projection(child) for child in value]
    return value


def typed(kind, value):
    value = deepcopy(value)
    if kind == 'problem':
        value['alternatives'] = [[float(x) for x in row] for row in value['alternatives']]
    elif kind == 'oracle':
        value['target_weights'] = [float(x) for x in value['target_weights']]
    elif kind == 'config':
        value['algorithm']['min_expected_progress'] = float(value['algorithm']['min_expected_progress'])
    return value


def artifact(base, path):
    return {'path': Path(path).relative_to(base).as_posix(), **FILES[Path(path).absolute()]}


def document_refs(value, pointer=''):
    if isinstance(value, dict):
        if {'path', 'sha256'}.issubset(value) and isinstance(value['path'], str):
            yield pointer, value
            return
        for key, child in value.items():
            yield from document_refs(child, pointer + '/' + key.replace('~', '~0').replace('/', '~1'))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from document_refs(child, pointer + '/' + str(index))


def at(document, pointer):
    current = document
    for key in pointer.split('/')[1:]:
        key = key.replace('~1', '/').replace('~0', '~')
        current = current[int(key)] if isinstance(current, list) else current[key]
    return current


def verify_materialization(series, plan):
    receipt = read(resolve(series, plan['materialization_receipt']))
    entries = {entry['source_relative_path']: entry for entry in receipt['entries']}
    require(len(entries) == len(receipt['entries']), 'Duplicate materialized original')
    documents = {}
    for name, entry in entries.items():
        original_path = resolve(series, entry['original'])
        current_path = resolve(series, entry['materialized'])
        require(entry['original']['path'] == 'provenance/original/' + name, 'Original namespace differs')
        if entry['document_kind'] == 'blob':
            require(file_bytes(original_path) == file_bytes(current_path)
                    and sha(file_bytes(original_path)) == entry['semantic_sha256'], 'Blob changed')
            continue
        original, current = read(original_path), read(current_path)
        expected = deepcopy(original)
        projection = typed(entry['document_kind'], original)
        mapping = []
        for pointer, reference in document_refs(original):
            child = entries[reference['path']]
            require(child['original']['sha256'] == reference['sha256'], 'Original reference binding differs')
            at(expected, pointer).update(child['materialized'])
            projected_ref = at(projection, pointer)
            projected_ref.pop('path')
            projected_ref.pop('sha256')
            projected_ref['source_artifact_sha256'] = reference['sha256']
            mapping.append({'json_pointer': pointer, 'source_path': reference['path'],
                            'materialized_path': child['materialized']['path']})
        require(expected == current and sorted(mapping, key=lambda row: row['json_pointer'])
                == sorted(entry['reference_map'], key=lambda row: row['json_pointer']),
                'Materialization changed values or undeclared references: ' + name)
        require(sha(canonical(float_projection(projection))) == entry['semantic_sha256'],
                'Materialized semantic digest differs')
        if entry['transformation'] == 'byte_copy':
            require(file_bytes(original_path) == file_bytes(current_path), 'Byte-copy original changed')
        if entry['document_kind'] in ('suite', 'dataset', 'config', 'execution_profile'):
            require(entry['document_kind'] not in documents, 'Repeated materialized entrypoint kind')
            documents[entry['document_kind']] = {'original': original, 'materialized': current, 'entry': entry}
    for reference in receipt['entrypoints'].values():
        resolve(series, reference)
        require(any(entry['materialized'] == reference for entry in entries.values()), 'Unmapped entrypoint')
    require(documents['suite']['entry']['materialized'] == plan['suite']
            and documents['dataset']['entry']['materialized'] == plan['dataset']
            and documents['execution_profile']['entry']['materialized'] == plan['execution_profile'],
            'Plan entrypoints differ from materialized originals')
    return documents


def study_contract(study_id):
    match = re.fullmatch(r'd(3|5|7)-a5-n(10|100)-h2-grid(3|5|10|20)-(grid-plus-ratio|grid)-'
                         r'(receding|countdown|adaptive)-stop-single-candidate-minprog0p001-src72072'
                         r'(?:-group(\d{2}))?', study_id)
    require(match is not None, 'Study ID is outside the authorized v3 family')
    dimension, count, grid, generator, mode, group = match.groups()
    dimension, count, grid = int(dimension), int(count), int(grid)
    require((dimension == 7 and count == 10 and group is not None and 1 <= int(group) <= 10)
            or (dimension in (3, 5) and count == 100 and group is None), 'Study denominator/group differs')
    require(dimension == 5 or (grid == 5 and generator == 'grid-plus-ratio'), 'Dimension/grid family differs')
    require(generator != 'grid' or mode in ('countdown', 'adaptive'), 'Unplanned grid-only mode')
    workers = 8 if dimension == 3 else 16
    configuration = {'schema_version': 2, 'configuration_id': study_id + '-config',
        'algorithm': {'query_strategy': 'reduction_per_query' if mode == 'adaptive' else 'fixed',
            'depth': 2, 'higher_depth_query_source': 'both' if generator == 'grid-plus-ratio' else 'grid',
            'grid_size': grid, 'planning_evaluation': 'candidate_count',
            'stopping': {'rule': 'single_candidate'}, 'horizon_execution': 'countdown' if mode == 'countdown' else 'receding',
            'min_expected_progress': .001}, 'budget': {'max_queries': None},
        'execution': {'workers': workers, 'start_method': 'forkserver', 'native_threads': 1,
                      'case_timeout_seconds': None, 'cache_policy_id': 'bounded_v1'},
        'recording': {'durability': 'per_answer', 'trace_level': 'standard', 'profile': False,
                      'telemetry_failure_policy': 'continue'}}
    return {'study_id': study_id, 'dimension': dimension, 'count': count, 'grid': grid,
            'mode': mode, 'configuration': configuration}


def verify_source(series, plan, wheel):
    source = plan['source']
    require(source['source_sha256'] == SOURCE and source['git_commit'] == COMMIT
            and source['inventory_format'] == 'otqa-source-v1' and not source['dirty'], 'Pinned source differs')
    inventory = read(series / 'source/inventory.json')
    provenance = read(series / 'source/build-provenance.json')
    require(sha(canonical(inventory)) == SOURCE and provenance['source'] == source
            and provenance['inventory_sha256'] == SOURCE, 'Source inventory/build provenance differs')
    require(sha(file_bytes(wheel)) == WHEEL, 'Pinned production wheel differs')
    with zipfile.ZipFile(io.BytesIO(file_bytes(wheel))) as archive:
        require(decode(archive.read('otqa/_source_inventory.json')) == inventory
                and decode(archive.read('otqa/_build_provenance.json')) == provenance, 'Wheel provenance differs')
        for row in inventory['files']:
            payload = archive.read(row['path'])
            require(len(payload) == row['bytes'] and sha(payload) == row['sha256'], 'Actual wheel source file differs')
    return source


def verify_attempt_bindings(series, plan, job, attempt, row):
    directory = series / attempt['directory']
    result = read(resolve(series, attempt['result']))
    require(directory == resolve(series, attempt['result']).parent, 'Attempt directory differs')
    request = read(directory / 'case-request.json')
    require(request['source'] == plan['source'] and request['series_id'] == plan['series_id']
            and request['project_binding'] == plan['project_binding']
            and request['materialization_receipt'] == plan['materialization_receipt']
            and request['execution_profile'] == plan['execution_profile']
            and request['run_purpose'] == 'production' and request['answer_source'] == 'simulated'
            and request['case_timeout_seconds'] is None and request['native_threads'] == 1,
            'Case request source/profile/series/purpose differs')
    for key in ('run_id', 'attempt_id'):
        require(request[key] == attempt[key] == result[key], 'Case request attempt identity differs')
    for key in ('problem', 'oracle', 'configuration'):
        require(request['inputs'][key] == job[key], 'Case request input differs')
    for key in ('initial_answers', 'continuation', 'replay_answers'):
        require(request['inputs'][key] is None, 'Unexpected starting history/replay')
    intent = read(resolve(series, attempt['launch_intent']))
    registration = read(resolve(series, attempt['child_registration']))
    grant = read(resolve(series, attempt['start_grant']))
    require(intent['series_id'] == plan['series_id'] and intent['job_id'] == job['job_id']
            and intent['run_id'] == registration['run_id'] == grant['run_id'] == attempt['run_id']
            and intent['attempt_id'] == registration['attempt_id'] == grant['attempt_id'] == attempt['attempt_id']
            and registration['intent'] == grant['intent'] == attempt['launch_intent']
            and grant['registration'] == attempt['child_registration']
            and registration['process'] == grant['process'] == attempt['process']
            and intent['owner_token'] == attempt['process']['owner_token']
            and intent['nonce'] == registration['nonce'] == grant['nonce'], 'Native launch ownership chain differs')
    if result['journal'] is None:
        return
    manifest = read(directory / 'manifest.json')
    require(manifest['job_id'] == job['job_id'] and manifest['series_id'] == plan['series_id']
            and manifest['run_purpose'] == 'production' and manifest['execution_kind'] == 'fresh'
            and manifest['project_binding'] == plan['project_binding']
            and manifest['process'] == attempt['process'] and manifest['launch_intent'] == attempt['launch_intent']
            and manifest['answer_source'] == 'simulated' and manifest['inputs'] == request['inputs'],
            'Manifest native identity differs')
    require(manifest['numerical_profile']['profile_id'] == 'otqa-exact-v3'
            and sha(canonical(float_projection(manifest['numerical_profile']['values']))) == NUMERICS,
            'Manifest mathematical numerical profile differs')
    require(manifest['resolved_cache_policy']['policy_id'] == 'bounded_v1', 'Cache policy differs')
    thread_keys = {'OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS',
                   'VECLIB_MAXIMUM_THREADS', 'BLIS_NUM_THREADS', 'NUMEXPR_NUM_THREADS'}
    require(manifest['environment']['native_thread_environment'] == {key: '1' for key in thread_keys},
            'Native thread environment differs')
    profile = read(resolve(series, plan['execution_profile']))
    require(manifest['environment']['packages'] == profile['packages']
            and manifest['environment']['python'] == profile['python_version']
            and manifest['environment']['platform_family'] == profile['platform_family'] == 'linux'
            and manifest['environment']['backend_capabilities'] == profile['backend_capabilities'],
            'Manifest environment differs from its actual qualified profile')
    problem = typed('problem', read(resolve(series, job['problem'])))
    oracle = typed('oracle', read(resolve(series, job['oracle'])))
    configuration = typed('config', read(resolve(series, job['configuration'])))
    identity = {'problem': problem, 'algorithm': configuration['algorithm'], 'budget': configuration['budget'],
                'answer_source': 'simulated', 'initial_answers': [], 'oracle': oracle, 'replay_answers': None,
                'execution_start': {'kind': 'fresh', 'algorithm_contract': 'otqa-execution-v2',
                                    'execution_cursor': {'answered_total': 0, 'remaining_depth': 2}}}
    require(manifest['mathematical_input_sha256'] == sha(canonical(float_projection(identity))),
            'Mathematical original matrix/preference/configuration identity differs')
    journal = file_bytes(resolve(series, {'path': result['journal']['path'], 'sha256': result['journal']['sha256']}))
    progress = read(directory / 'progress.json')
    progress_updated = utc_stamp(progress['updated_at_utc'], 'progress.updated_at_utc')
    require(progress['schema_version'] == 2 and progress['run_id'] == attempt['run_id']
            and progress['attempt_id'] == attempt['attempt_id'] and progress['process'] == attempt['process'],
            'Progress identity differs')
    prefix = journal[:progress['valid_prefix_bytes']]
    require(len(prefix) == progress['valid_prefix_bytes'] and sha(prefix) == progress['valid_prefix_sha256']
            and (not prefix or prefix.endswith(b'\n')), 'Progress prefix SHA/size differs')
    events = [decode(line) for line in prefix.splitlines()]
    require(not events or utc_stamp(events[-1]['occurred_at_utc'], 'progress.bound_event_utc')
            <= progress_updated <= utc_stamp(result['finished_at_utc'], 'result.finished_at_utc'),
            'Wall-clock durable progress ordering anomaly requires explicit review')
    require(len(events) == progress['last_good_sequence'] <= result['journal']['last_good_sequence'],
            'Progress sequence exceeds confirmed result prefix')
    counts = {'initial_answers': 0, 'answered_new': 0, 'answered_total': 0, 'dispatched_new': 0}
    cursor, active, phase = {'answered_total': 0, 'remaining_depth': 2}, None, 'bootstrapping'
    for event in events:
        kind, payload = event['event_type'], event['payload']
        if kind == 'run_started':
            phase = 'started'
        elif kind == 'state_analyzed':
            phase = 'state_committed'
        elif kind == 'query_planned':
            active, phase = event['query_id'], 'planned'
        elif kind == 'query_dispatched':
            counts['dispatched_new'] += 1
            phase = 'awaiting_answer'
        elif kind == 'answer_received':
            counts['answered_new'] += 1
            counts['answered_total'] += 1
            cursor = payload['execution_cursor']
            phase = 'answer_committed'
        elif kind == 'query_completed':
            active = None
        elif kind in ('run_finished', 'run_failed', 'run_interrupted'):
            active = None
            phase = {'run_finished': 'completed', 'run_failed': 'failed', 'run_interrupted': 'interrupted'}[kind]
    require(progress['query_counts'] == counts and progress['execution_cursor'] == cursor
            and progress['active_query_id'] == active, 'Progress actual answer/cursor phase differs')
    # Intermediate state/planning phase names are allowed to reflect the last
    # explicit recorder barrier; terminal/native answer phases must match exactly.
    if phase in ('completed', 'failed', 'interrupted', 'answer_committed', 'awaiting_answer'):
        require(progress['query_phase'] == phase, 'Progress terminal/answer phase differs')
    if result['execution_status'] == 'completed':
        require(progress['last_good_sequence'] == result['journal']['last_good_sequence']
                and counts == result['query_counts'] and cursor == row['final_execution_cursor'],
                'Completed progress does not match full terminal result')
    partial = progress['partial_api_elapsed_seconds']
    require(partial is None or math.isfinite(partial) and partial >= 0, 'Invalid progress elapsed time')
    row['progress_ref'] = artifact(series, directory / 'progress.json')
    row['progress_matches_full_result_prefix'] = progress['last_good_sequence'] == result['journal']['last_good_sequence']
    # Retain and check even complete answer lines outside an accepted failed
    # prefix; they remain uncommitted evidence and never receive query credit.
    extra_answers = 0
    suffix = journal[result['journal']['valid_prefix_bytes']:]
    for line in suffix.splitlines(keepends=True):
        if not line.endswith(b'\n'):
            continue
        event = decode(line)
        if event.get('event_type') == 'answer_received':
            query = event['payload']['query']
            weights = [fraction(x) for x in oracle['target_weights']]
            delta = weights[query['goal_index_a']] - fraction(query['value']) * weights[query['goal_index_b']]
            require(event['payload']['answer'] == ('<' if delta < 0 else '>' if delta > 0 else '='),
                    'Uncommitted recorded answer differs from rational oracle')
            extra_answers += 1
    row['uncommitted_recorded_answers_checked_no_credit'] = extra_answers


def distribution(values):
    values = list(values)
    if not values:
        return {'n': 0, **{key: None for key in ('total', 'mean', 'median', 'minimum', 'maximum', 'p90')}}
    ordered = sorted(values)
    position = .9 * (len(values) - 1)
    lo, hi = math.floor(position), math.ceil(position)
    return {'n': len(values), 'total': math.fsum(values), 'mean': statistics.mean(values),
            'median': statistics.median(values), 'minimum': ordered[0], 'maximum': ordered[-1],
            'p90': ordered[lo] + (ordered[hi] - ordered[lo]) * (position - lo)}


def compare_aggregate(actual, expected, pointer=''):
    if isinstance(expected, dict):
        require(set(actual) == set(expected), 'Aggregate fields differ: ' + pointer)
        for key, value in expected.items():
            compare_aggregate(actual[key], value, pointer + '/' + key)
    elif isinstance(expected, list):
        require(isinstance(actual, list) and len(actual) == len(expected), 'Aggregate list differs: ' + pointer)
        for index, (left, right) in enumerate(zip(actual, expected)):
            compare_aggregate(left, right, pointer + '/' + str(index))
    elif type(expected) is float and type(actual) in (int, float) and any(
            '/' + key + '/' in pointer for key in ('solution_time', 'correct_solution_time',
                'completed_call_time', 'controller_attempt_time', 'failed_api_call_time')):
        # Costs are preserved individually. Aggregate-only tolerance covers the
        # documented Python3.9 versus3.12+ change to compensated builtin sum.
        require(actual == expected or abs(actual - expected) <= 32 * max(math.ulp(float(actual)), math.ulp(expected)),
                'Aggregate numeric differs beyond32ULP: ' + pointer)
    else:
        require(actual == expected, 'Aggregate value differs: ' + pointer)


def verify_exports(series, plan, state, finish, primary_rows):
    base = series.parents[2]
    artifacts = finish['artifacts']
    for reference in artifacts.values():
        resolve(base, reference)
    audit_path = resolve(base, artifacts['audit'])
    audit = read(audit_path)
    require(audit['status'] == 'passed' and audit['auditor'] == plan['source']
            and audit['series_id'] == plan['series_id'] and not audit['prefix_snapshots']
            and all(check['status'] == 'passed' for check in audit['checks']), 'Native audit not wholly passed')
    require(len(list((series / 'reports').glob('*/audit.json'))) == 1, 'Expected exactly one native audit')
    expected_audit_checks = {'plan-state-and-frozen-inputs': None, 'materialization': None}
    for job in state['jobs']:
        for attempt in job['attempts']:
            expected_audit_checks[job['job_id'] + '-' + attempt['attempt_id']] = attempt['result']
    require({item['check_id']: item['artifact'] for item in audit['checks']} == expected_audit_checks
            and len(audit['checks']) == len(expected_audit_checks), 'Native audit attempt coverage differs')
    require(audit['plan'] == {'path': 'plan.json', 'sha256': finish['plan_sha256']}, 'Audit plan binding differs')
    snapshot = read(resolve(series, audit['state']))
    require(snapshot == state and sha(file_bytes(resolve(series, audit['state']))) == finish['terminal_state_sha256'],
            'Audit snapshot differs from final native state')
    audit_ref = {'path': audit_path.relative_to(series).as_posix(), 'sha256': artifacts['audit']['sha256']}
    require(finish['native_audit_ref'] == audit_ref, 'Finish audit ref differs')
    summary = read(resolve(base, artifacts['json']))
    require(file_bytes(resolve(base, artifacts['json'])) == file_bytes(resolve(base, artifacts['summary'])),
            'JSON export and immutable summary bytes differ')
    for key, value in {'schema_version': 2, 'series_id': plan['series_id'], 'scope': 'complete',
                       'basis': 'verified_raw_attempts', 'plan': audit['plan'], 'state': audit['state'],
                       'audit': audit_ref, 'prefix_snapshots': [], 'generated_at_utc': audit['created_at_utc']}.items():
        require(summary[key] == value, 'JSON export binding differs: ' + key)
    expected_rows, groups = [], []
    state_jobs = {job['job_id']: job for job in state['jobs']}
    attempts_by_job = {}
    for job, checked in zip(plan['jobs'], primary_rows):
        job_state = state_jobs[job['job_id']]
        attempts = job_state['attempts']
        results = [read(resolve(series, attempt['result'])) for attempt in attempts]
        attempts_by_job[job['job_id']] = list(zip(attempts, results))
        result = results[-1]
        solver, configuration = result['solver_result'], read(resolve(series, job['configuration']))
        algorithm = configuration['algorithm']
        expected = {'job_id': job['job_id'], 'case_id': job['case_id'], 'configuration_id': job['configuration_id'],
                    'repetition_index': 0, 'objective_count': checked['objectives'], 'alternative_count': 5,
                    'status': job_state['status'], 'accepted_attempt_id': attempts[-1]['attempt_id'],
                    'termination_reason': solver['termination_reason'] if solver else None,
                    'solved': solver['solved'] if solver else None,
                    'selected_candidate_id': solver['selected_candidate_id'] if solver else None,
                    'quality_status': checked['quality'], 'query_counts': result['query_counts'],
                    'api_call_wall_seconds': result['timings']['api_call_wall_seconds'] if result['timings']['complete_api_measurement'] else None,
                    'attempt_results': [attempt['result'] for attempt in attempts],
                    **{key: algorithm[key] for key in ('query_strategy', 'horizon_execution', 'depth', 'min_expected_progress')},
                    'planning_attempts_started': checked['attempts_started'] if result['journal'] else None,
                    'planning_attempts_completed': checked['attempts_completed'] if result['journal'] else None,
                    'fallback_selections': checked['fallbacks'] if result['journal'] else None,
                    'terminal_expected_progress': None, 'terminal_planning_depth': None}
        if solver and solver['termination_reason'] == 'insufficient_expected_progress':
            terminal = solver['planning_cycles'][-1]['attempts'][-1]
            expected['terminal_expected_progress'] = max(h['best_progress']['expected_progress'] for h in terminal['horizon_evidence'] if h['best_progress'] is not None)
            expected['terminal_planning_depth'] = terminal['requested_depth']
        expected_rows.append(expected)
    require(summary['rows'] == expected_rows, 'JSON export rows differ from independently checked raw attempts')
    csv_data = file_bytes(resolve(base, artifacts['csv']))
    csv_rows = list(csv.DictReader(io.StringIO(csv_data.decode())))
    require(len(csv_rows) == len(expected_rows), 'CSV export denominator differs')
    metadata = {'audit_path': audit_ref['path'], 'audit_sha256': audit_ref['sha256'],
                'plan_sha256': audit['plan']['sha256'], 'state_snapshot_sha256': audit['state']['sha256'], 'scope': 'complete'}
    for csv_row, expected in zip(csv_rows, expected_rows):
        encoded = {key: json.dumps(value, separators=(',', ':'), ensure_ascii=False) if isinstance(value, (dict, list))
                   else '' if value is None else str(value) for key, value in expected.items()}
        require(csv_row == {**metadata, **encoded}, 'CSV export row/snapshot differs')
    for kind in ('json', 'csv'):
        receipt = read(resolve(base, artifacts[kind + '_receipt']))
        require(receipt == {'schema_version': 1,
            'output': {'path': Path(artifacts[kind]['path']).relative_to(series.relative_to(base)).as_posix(),
                       'sha256': artifacts[kind]['sha256']}, 'audit': audit_ref, 'plan': audit['plan'],
            'state': audit['state'], 'prefix_snapshots': [], 'scope': 'complete', 'format': kind},
            'Export receipt differs: ' + kind)
    require(len(summary['groups']) == 1, 'Standalone study has unexpected group count')
    rows = expected_rows
    completed = [row for row in rows if row['status'] == 'completed']
    solved = [row for row in completed if row['solved']]
    correct = [row for row in solved if row['quality_status'] == 'correct']
    all_attempts = [attempt for state_job in state['jobs'] for attempt in state_job['attempts']]
    failed_times = [result['timings']['api_call_wall_seconds'] for values in attempts_by_job.values()
                    for _, result in values if result['execution_status'] == 'failed'
                    and result['timings']['complete_api_measurement'] and result['timings']['api_call_wall_seconds'] is not None]
    def times(sample):
        return [row['api_call_wall_seconds'] for row in sample if row['api_call_wall_seconds'] is not None]
    def queries(sample):
        return [row['query_counts']['answered_new'] for row in sample]
    group = {'configuration_id': rows[0]['configuration_id'], 'objective_count': rows[0]['objective_count'],
        'alternative_count': 5, 'planned_jobs': len(rows), 'unique_cases': len({row['case_id'] for row in rows}),
        'completed_native': len(completed), 'solved': len(solved),
        'singleton_stops': sum(row['termination_reason'] == 'exact_single_candidate' for row in completed),
        'confidence_stops': 0, 'no_query': sum(row['termination_reason'] == 'no_query' for row in completed),
        'query_cap': 0, 'correct': len(correct), 'incorrect': sum(row['quality_status'] == 'incorrect' for row in solved),
        'unknown_quality': sum(row['quality_status'] == 'unknown' for row in completed),
        **{status: sum(row['status'] == status for row in rows) for status in ('failed', 'interrupted', 'pending', 'launching', 'running')},
        'total_attempts': len(all_attempts), 'unknown_controller_attempt_times': sum(a['controller_elapsed_seconds'] is None for a in all_attempts),
        'solution_time': distribution(times(solved)), 'correct_solution_time': distribution(times(correct)),
        'completed_call_time': distribution(times(completed)),
        'controller_attempt_time': distribution(a['controller_elapsed_seconds'] for a in all_attempts if a['controller_elapsed_seconds'] is not None),
        'failed_api_call_time': distribution(failed_times), 'answered_new_solved': distribution(queries(solved)),
        'answered_new_correct': distribution(queries(correct)), 'answered_new_completed': distribution(queries(completed)),
        'solution_sample_job_ids': [row['job_id'] for row in solved], 'correct_sample_job_ids': [row['job_id'] for row in correct],
        'completed_sample_job_ids': [row['job_id'] for row in completed],
        **{key: rows[0][key] for key in ('query_strategy', 'horizon_execution', 'depth', 'min_expected_progress')},
        'insufficient_expected_progress': sum(row['termination_reason'] == 'insufficient_expected_progress' for row in completed)}
    groups.append(group)
    compare_aggregate(summary['groups'], groups)
    require(finish['groups'] == summary['groups'], 'Native finish group evidence differs from export')
    return {'audit': artifact(series, audit_path), 'json': artifacts['json'], 'csv': artifacts['csv'],
            'state_snapshot': audit['state'], 'row_count': len(rows), 'group_count': 1,
            'aggregate_rounding_tolerance': '32ULP for aggregate floating values only; individual costs retained unchanged'}


def raw_directory_coverage(series, state):
    """Discover unreferenced raw attempts rather than trusting state alone."""
    expected_jobs = {job['job_id'] for job in state['jobs']}
    actual_jobs = {path.name for path in (series / 'jobs').iterdir()}
    unexpected = []
    if actual_jobs != expected_jobs:
        unexpected.append({'check': 'raw_job_directory_coverage', 'expected': sorted(expected_jobs),
                           'actual': sorted(actual_jobs)})
    for job in state['jobs']:
        base = series / 'jobs' / job['job_id'] / 'attempts'
        expected = {attempt['attempt_id'] for attempt in job['attempts']}
        actual = {path.name for path in base.iterdir()} if base.is_dir() else set()
        for attempt in job['attempts']:
            require(attempt['directory'] == 'jobs/' + job['job_id'] + '/attempts/' + attempt['attempt_id'],
                    'Declared attempt directory is outside its actual job/ordinal')
        if expected != actual:
            unexpected.append({'check': 'raw_attempt_directory_coverage', 'job_id': job['job_id'],
                               'expected': sorted(expected), 'actual': sorted(actual)})
    expected_results = {attempt['result']['path'] for job in state['jobs'] for attempt in job['attempts']}
    actual_results = {path.relative_to(series).as_posix()
                      for path in (series / 'jobs').glob('*/attempts/*/result.json')}
    if actual_results != expected_results:
        unexpected.append({'check': 'raw_result_path_coverage', 'expected': sorted(expected_results),
                           'actual': sorted(actual_results)})
    if unexpected:
        # Preserve evidence, including any cost/result files outside the native
        # state, but never give them primary-case or successful-query credit.
        for path in (series / 'jobs').rglob('*'):
            require(not path.is_symlink(), 'Symlink in raw attempt namespace')
            if path.is_file():
                file_bytes(path)
    return unexpected


def check_series(project_root, series_path, finish_path, wheel, prepared_index):
    project_root = Path(project_root).absolute()
    relative = PurePosixPath(series_path)
    require(not relative.is_absolute() and '..' not in relative.parts
            and len(relative.parts) == 3 and relative.parts[:2] == ('runs', 'studies'), 'Unsafe native series path')
    series = project_root / relative
    plan, state, finish = read(series / 'plan.json'), read(series / 'state.json'), read(finish_path)
    contract = study_contract(plan['suite_id'])
    require(plan['suite_id'] == relative.name and plan['run_purpose'] == 'production', 'Native series purpose/ID differs')
    source = verify_source(series, plan, wheel)
    require(state['series_id'] == plan['series_id'] == finish['series_id']
            and state['plan_sha256'] == sha(file_bytes(series / 'plan.json')) == finish['plan_sha256']
            and sha(file_bytes(series / 'state.json')) == finish['terminal_state_sha256'], 'Native plan/state/finish binding differs')
    require(finish['study_id'] == contract['study_id'] and finish['status'] == 'native_stage_verified_not_scientific_complete'
            and finish['planned_jobs'] == contract['count'], 'Wrong native finish proof')
    require(state['status'] in ('completed', 'completed_with_failures')
            and state['active_job_id'] is None and state['controller'] is None, 'Native series is not wholly terminal')
    utc_stamp(plan['created_at_utc'], 'plan.created_at_utc')
    utc_stamp(state['updated_at_utc'], 'state.updated_at_utc')
    require(all(group['group_status'] == 'dead' for group in finish['quiescence']['controller_and_observer']
                + finish['quiescence']['attempts']) and not finish['quiescence']['unexpected_study_processes'],
            'Finish has no complete historical group-end proof')
    require(len(plan['jobs']) == len(state['jobs']) == contract['count']
            and [job['job_id'] for job in plan['jobs']] == [job['job_id'] for job in state['jobs']]
            and len({job['job_id'] for job in plan['jobs']}) == contract['count'], 'Original planned denominator differs')
    for path, expected in plan['frozen_files'].items():
        resolve(series, {'path': path, 'sha256': expected})
    documents = verify_materialization(series, plan)
    profile = documents['execution_profile']['materialized']
    require(profile['certification']['status'] == 'validated', 'Execution profile not validated')
    certification = read(resolve(series, profile['certification']['evidence']))
    require(certification['status'] == 'passed' and certification['source'] == source
            and certification['numerical_profile_id'] == 'otqa-exact-v3'
            and certification['numerical_values_sha256'] == NUMERICS
            and certification['cache_policy_id'] == 'bounded_v1'
            and certification['scopes'] == ['sdk', 'standalone', 'series_linux_recovery']
            and all(check['status'] == 'passed' for check in certification['checks']),
            'Actual qualified profile/source/numerics differs')
    require(documents['config']['original'] == contract['configuration'], 'Original frozen configuration differs')
    input_contract = read(prepared_index)
    # Offline standalone packages may contain only this study's original
    # prepared record rather than the private full53-study scheduling index.
    expected_input = (next(row for row in input_contract['studies'] if row['study_id'] == contract['study_id'])
                      if 'studies' in input_contract else input_contract)
    require(expected_input['study_id'] == contract['study_id'], 'Wrong independent input contract')
    for kind in ('suite', 'dataset', 'configuration'):
        document_kind = 'config' if kind == 'configuration' else kind
        entry = documents[document_kind]['entry']
        require(entry['original']['sha256'] == expected_input[kind]['sha256']
                and entry['source_relative_path'] == expected_input[kind]['path'],
                'Native original differs from independent prepared input contract: ' + kind)
    original_suite, original_dataset = documents['suite']['original'], documents['dataset']['original']
    require(original_suite['repetitions'] == 1 and len(original_suite['configurations']) == 1
            and len(original_suite['selection']) == 1 and original_suite['execution']['max_concurrent_cases'] == 1,
            'Standalone suite repetitions/configurations differ')
    start = (int(relative.name.rsplit('-group', 1)[1]) - 1) * 10 if contract['dimension'] == 7 else 0
    expected_cases = [f"d{contract['dimension']}-m5-c{index:06d}" for index in range(start, start + contract['count'])]
    require([case['case_id'] for case in original_dataset['cases']] == expected_cases
            and original_suite['selection'][0]['case_ids'] == expected_cases
            and [job['case_id'] for job in plan['jobs']] == expected_cases == expected_input['case_ids'],
            'Original selected problem set/order or unfilted denominator changed')
    originals = {case['case_id']: case for case in original_dataset['cases']}
    bound_protocol = {**contract, 'source': source, '_native_execution_profile': plan['execution_profile']}
    attempts, primary = [], []
    findings = raw_directory_coverage(series, state)
    for job, job_state in zip(plan['jobs'], state['jobs']):
        require(job['configuration_id'] == contract['configuration']['configuration_id']
                and job['repetition_index'] == 0, 'Unplanned configuration/repetition')
        require(job_state['status'] in ('completed', 'failed') and job_state['attempts'], 'Final primary job is not terminal')
        for kind in ('problem', 'oracle'):
            require(job[kind]['sha256'] == originals[job['case_id']][kind]['sha256'], 'Original problem/oracle bytes changed')
        if len(job_state['attempts']) != 1:
            findings.append({'job_id': job['job_id'], 'check': 'one_primary_attempt_policy',
                             'message': 'All attempts retained, but the study expected exactly one attempt per cell'})
        last = None
        for attempt in job_state['attempts']:
            cost = attempt['controller_elapsed_seconds']
            require(cost is None or type(cost) in (int, float) and math.isfinite(cost) and cost >= 0,
                    'Invalid controller attempt cost')
            retained = {'job_id': job['job_id'], 'case_id': job['case_id'], 'attempt_id': attempt['attempt_id'],
                        'run_id': attempt['run_id'], 'execution_status': attempt['execution_status'],
                        'result': attempt['result'], 'controller_elapsed_seconds': cost, 'verified': False}
            attempts.append(retained)
            try:
                result = read(resolve(series, attempt['result']))
                retained['timings'] = result['timings']
                retained['error'] = result['error']
                retained['interruption'] = result['interruption']
                checked = verify_job(series, job, attempt, bound_protocol)
                verify_attempt_bindings(series, plan, job, attempt, checked)
                checked['job_id'] = job['job_id']
                retained.update(verified=True, evidence=checked)
                last = checked
            except (ValueError, KeyError, IndexError, TypeError, OSError) as error:
                retained['finding'] = str(error)
                findings.append({'job_id': job['job_id'], 'attempt_id': attempt['attempt_id'],
                                 'check': 'independent_raw_attempt', 'message': str(error)})
                last = None
        if last is not None:
            require(last['status'] == job_state['status'], 'Accepted last attempt and primary status differ')
            primary.append(last)
    require(finish['total_attempts'] == len(attempts), 'Finish attempt denominator differs')
    exports = None
    if len(primary) == contract['count']:
        try:
            exports = verify_exports(series, plan, state, finish, primary)
        except (ValueError, KeyError, IndexError, TypeError, OSError) as error:
            findings.append({'check': 'independent_native_export_snapshot', 'message': str(error)})
    else:
        findings.append({'check': 'independent_native_export_snapshot',
                         'message': 'Export proof cannot pass because one or more primary raw attempts did not pass'})
    primary_quality = Counter(row['quality'] for row in primary)
    actual_attempts = [row['evidence'] for row in attempts if row['verified']]
    result = {'schema_version': 1, 'status': 'provisional_pass' if not findings else 'provisional_failed',
        'scientific_completion': False, 'publication_completion': False,
        'study_id': contract['study_id'], 'series_id': plan['series_id'], 'source': source,
        'plan': artifact(series, series / 'plan.json'), 'state': artifact(series, series / 'state.json'),
        'finish_proof_sha256': sha(file_bytes(finish_path)), 'configuration': contract['configuration'],
        'expected_original_inputs': {key: expected_input[key] for key in ('configuration', 'dataset', 'suite')},
        'expected_original_case_ids': expected_cases, 'independent_problems': contract['count'],
        'primary_cells': contract['count'], 'repetitions': 1, 'primary_rows_verified': len(primary),
        'all_attempts': attempts, 'rows': primary, 'exports': exports, 'findings': findings,
        'counts': {'primary_rows': len(primary), 'all_attempts': len(attempts),
            'attempts_verified': sum(row['verified'] for row in attempts),
            'answers_checked_exact_fraction': sum(row['answers_checked'] for row in actual_attempts),
            'winner_sets_checked_exact_fraction': len(actual_attempts),
            'uncommitted_recorded_answers_checked_no_credit': sum(row.get('uncommitted_recorded_answers_checked_no_credit', 0) for row in actual_attempts),
            'solved': sum(row['solved'] for row in primary), 'correct': primary_quality['correct'],
            'incorrect': primary_quality['incorrect'],
            'regular_unsolved': sum(row['status'] == 'completed' and not row['solved'] for row in primary),
            'failed': sum(row['status'] == 'failed' for row in primary),
            'interrupted_attempts': sum(row['execution_status'] == 'interrupted' for row in attempts),
            'unknown_controller_costs': sum(row['controller_elapsed_seconds'] is None for row in attempts)},
        'terminal_reasons': dict(Counter(row['termination_reason'] or row['status'] for row in primary)),
        'ordered_problem_oracle_sha256': sha(canonical([{'case_id': case['case_id'],
            'problem_sha256': case['problem']['sha256'], 'oracle_sha256': case['oracle']['sha256']}
            for case in original_dataset['cases']])),
        'limitations': [
            'Provisional independent evidence only; root and peer review, final cross-host hash proof, packaging and download verification remain separate.',
            'No geometric region, LP feasibility, hypothetical branch probability, alternative plan inventory or global score optimum was recomputed or certified.',
            'Stored generated/evaluated inventory counts, horizon decisions and progress threshold arithmetic were checked against recorded evidence.',
            'Exact Fraction comparisons interpret the preserved binary64 matrix, preferences and actual query thresholds; they do not prove other-weight region geometry.',
            'Historical process-group end is bound to the native finish evidence; this offline checker makes no fresh Linux process-liveness claim.',
            'Intermediate progress phase labels are not independently reconstructed beyond durable identities, prefix, counts/cursor, and terminal/answer phase barriers.',
            'Native aggregate floating values permit32ULP rounding difference across Python summation implementations; every individual original timing and attempt cost is retained.',
            'UTC format and observed ordering are checked only as a clock-anomaly review gate; operating-system wall clocks can step, and no performance duration is calculated from UTC timestamps.',
        ]}
    return result


def verify_study(project_root, series_path, finish_proof, wheel, prepared_index):
    """Portable no-write API; all five paths/identities are supplied explicitly.

    prepared_index may be the original index or its byte-value-identical single
    study record. Output paths/timestamps carry no scientific meaning. The API
    returns provisional evidence and never creates a raw file or completion.
    """
    FILES.clear()
    project_root = Path(project_root).absolute()
    external = {Path(finish_proof).absolute(): '@finish_proof', Path(wheel).absolute(): '@wheel',
                Path(prepared_index).absolute(): '@prepared_input_contract'}
    started = time.monotonic()
    try:
        result = check_series(project_root, series_path, Path(finish_proof), Path(wheel), Path(prepared_index))
    except (ValueError, KeyError, IndexError, TypeError, OSError, zipfile.BadZipFile, StopIteration) as error:
        result = {'schema_version': 1, 'status': 'provisional_failed', 'scientific_completion': False,
                  'publication_completion': False, 'study_id': PurePosixPath(series_path).name,
                  'findings': [{'check': 'global_study_binding', 'message': str(error)}]}
    for path, expected in list(FILES.items()):
        if not path.is_file() or {'sha256': sha(path.read_bytes()), 'bytes': path.stat().st_size} != expected:
            result['status'] = 'provisional_failed'
            result['findings'].append({'check': 'final_read_artifact_stability', 'message': str(path)})
    result['created_at_utc'] = datetime.now(timezone.utc).isoformat()
    result['elapsed_seconds'] = time.monotonic() - started
    result['verifier'] = {'path': Path(__file__).name, 'sha256': sha(Path(__file__).read_bytes()),
                          'standard_library_only': True, 'native_package_imported': False}
    result['verified_read_artifacts'] = sorted([
        {'path': external.get(path, path.relative_to(project_root).as_posix()
                              if path.is_relative_to(project_root) else str(path)), **proof}
        for path, proof in FILES.items()], key=lambda item: item['path'])
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project-root', type=Path, required=True, help='Existing Mac mirror project root')
    parser.add_argument('--series-path', required=True)
    parser.add_argument('--finish-proof', type=Path, required=True)
    parser.add_argument('--wheel', type=Path, default=ROOT / 'runs/four-host-readiness-20261017T2140Z/bootstrap/wheel/bachelorarbeit_optimal_tradeoff_queries-0.2.0-py3-none-any.whl')
    parser.add_argument('--prepared-index', type=Path, default=ROOT / 'runs/four-host-readiness-20261017T2140Z/prepared-suites/index.json')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    output = args.output.absolute()
    require(output.is_relative_to(E / 'monitoring/provisional-rawchecks') and not output.exists(),
            'Raw-check output must be a fresh path under E/monitoring/provisional-rawchecks')
    result = verify_study(args.project_root, args.series_path, args.finish_proof, args.wheel, args.prepared_index)
    output.parent.mkdir(parents=True, exist_ok=True)
    for part in (output.parent, *output.parent.parents):
        require(not part.is_symlink(), 'Output symlink refused')
    with output.open('xb') as stream:
        stream.write(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False).encode() + b'\n')
        stream.flush()
        os.fsync(stream.fileno())
    print(json.dumps({'status': result['status'], 'study_id': result.get('study_id'), 'counts': result.get('counts'),
                      'findings': result['findings'], 'output': str(output)}, ensure_ascii=False))
    return 0 if result['status'] == 'provisional_pass' else 1


if __name__ == '__main__':
    raise SystemExit(main())


