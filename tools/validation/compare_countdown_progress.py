"""Frozen, serial SDK comparisons; neither native CLI qualification nor a study.

Prepare does not import the solver. Run uses separate source-isolated processes,
identical explicit disabled progress, eight workers and one native thread.
"""
from __future__ import annotations

import argparse
from dataclasses import fields, is_dataclass
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import importlib.metadata
import json
import math
import os
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import time
import traceback
from uuid import uuid4

THREAD_VARIABLES = ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS',
                    'BLIS_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS', 'NUMEXPR_NUM_THREADS')
NEW_EXECUTION_FIELDS = frozenset(('execution_cursor', 'planning_cycles', 'continuation_binding', 'cycle'))


def digest_bytes(value):
    return hashlib.sha256(value).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def write_new(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n')
        stream.flush()
        os.fsync(stream.fileno())


def load_plan(directory):
    path = directory / 'plan.json'
    expected = (directory / 'plan-sha256.json').read_text()
    if digest_bytes(path.read_bytes()) != json.loads(expected)['sha256']:
        raise ValueError('comparison plan changed after preparation')
    return json.loads(path.read_text())


def source_inventory(source):
    return [{'path': item.relative_to(source).as_posix(), 'sha256': digest_bytes(item.read_bytes())}
            for item in sorted(source.rglob('*')) if item.is_file() and item.suffix in ('.py', '.json')]


def mathematical(value):
    if is_dataclass(value):
        return {item.name: mathematical(getattr(value, item.name)) for item in fields(value)
                if item.name not in NEW_EXECUTION_FIELDS}
    if isinstance(value, float):
        return {'float_hex': value.hex()}
    if isinstance(value, (list, tuple)):
        return [mathematical(item) for item in value]
    if isinstance(value, dict):
        return {key: mathematical(item) for key, item in value.items()}
    if value is None or isinstance(value, (bool, int, str)):
        return value
    raise TypeError(f'Unsupported comparison value {type(value).__name__}')


def declared_cases():
    return {
        'analytic-g2-a3': {'alternatives': [[1., 0.], [0., 1.], [.6, .6]], 'weights': [.55, .45],
                           'scope': 'complete two-objective analytical control'},
        'structured-g5-a5-left': {
            'alternatives': [[1., 0., .8, .8, .8], [0., 1., .8, .8, .8],
                             [0., 0., 0., 0., 0.], [.05, .05, .05, .05, .05], [.15, .1, .2, .1, .2]],
            'weights': [.45, .15, .1, .15, .15],
            'scope': 'structured five-objective/five-alternative full-call control; two initially relevant alternatives'},
        'structured-g5-a5-right': {
            'alternatives': [[1., 0., .8, .8, .8], [0., 1., .8, .8, .8],
                             [0., 0., 0., 0., 0.], [.05, .05, .05, .05, .05], [.15, .1, .2, .1, .2]],
            'weights': [.15, .45, .15, .1, .15],
            'scope': 'structured five-objective/five-alternative full-call control; two initially relevant alternatives'},
    }


def conditions():
    rows = []
    for strategy, depths, modes in [('fixed', (1, 2, 3), ('receding',)),
                                    ('fixed', (2, 3), ('countdown',)),
                                    ('reduction_per_query', (1, 2, 3), ('receding',))]:
        for mode in modes:
            for depth in depths:
                for evaluation in ('candidate_count', 'stop_aware'):
                    rows.append({'case_id': 'analytic-g2-a3', 'strategy': strategy, 'depth': depth,
                                 'mode': mode, 'evaluation': evaluation})
    for case_id, strategy in [('structured-g5-a5-left', 'fixed'),
                              ('structured-g5-a5-right', 'reduction_per_query')]:
        for evaluation in ('candidate_count', 'stop_aware'):
            rows.append({'case_id': case_id, 'strategy': strategy, 'depth': 2,
                         'mode': 'receding', 'evaluation': evaluation})
    for index, row in enumerate(rows, 1):
        row['condition_id'] = f'condition{index:03d}'
    return rows


def policy_conditions(rows):
    wanted = (
        ('analytic-g2-a3', 'fixed', 2, 'receding', 'candidate_count'),
        ('analytic-g2-a3', 'fixed', 2, 'countdown', 'candidate_count'),
        ('analytic-g2-a3', 'reduction_per_query', 3, 'receding', 'stop_aware'),
        ('structured-g5-a5-right', 'reduction_per_query', 2, 'receding', 'stop_aware'),
    )
    return [next(row for row in rows if tuple(row[key] for key in
        ('case_id', 'strategy', 'depth', 'mode', 'evaluation')) == identity) for identity in wanted]


def prepare(root, output, *, new_source=Path('src')):
    root, output = root.resolve(), output.resolve()
    if not output.is_relative_to(root / 'runs'):
        raise ValueError('comparison artifacts must be inside the marked project runs directory')
    if output.exists():
        raise FileExistsError(output)
    baseline = Path('runs/countdown-progress-integration-20261016T030055Z/baseline/files/src')
    resolved_new_source = (root / new_source).resolve()
    if not resolved_new_source.is_relative_to(root):
        raise ValueError('new SDK source must be inside the marked project')
    sources = {'old': baseline.as_posix(), 'new': resolved_new_source.relative_to(root).as_posix()}
    inventories = {key: source_inventory(root / path) for key, path in sources.items()}
    if any(not items for items in inventories.values()):
        raise ValueError('missing frozen source inventory')
    rows, jobs = conditions(), []
    for condition in rows:
        for block in range(1, 4):
            for variant in (('old', 'new') if block % 2 else ('new', 'old')):
                jobs.append({'job_id': f'job{len(jobs) + 1:04d}', 'condition_id': condition['condition_id'],
                             'block': block, 'variant': variant, 'group': 'sdk_parity_timing',
                             'minimum': None})
    quality_rows = policy_conditions(rows)
    for condition in quality_rows:
        for minimum in (None, 0.001):
            jobs.append({'job_id': f'job{len(jobs) + 1:04d}', 'condition_id': condition['condition_id'],
                         'block': None, 'variant': 'new', 'group': 'progress_policy', 'minimum': minimum})
    plan = {'schema_version': 1, 'purpose': 'matched_complete_sdk_calls_progress_disabled',
        'comparison_id': str(uuid4()), 'created_at_utc': datetime.now(timezone.utc).isoformat(),
        'sources': sources, 'source_inventories': inventories,
        'harness_sha256': digest_bytes(Path(__file__).read_bytes()),
        'runtime': {'workers': 8, 'native_threads': 1, 'start_method': 'forkserver', 'grid_size': 5,
                    'higher_depth_query_source': 'both', 'max_queries': 12, 'min_expected_progress': None,
                    'profile': False, 'capture': False, 'paired_blocks': 3},
        'cases': declared_cases(), 'conditions': rows, 'jobs': jobs,
        'policy_condition_ids': [row['condition_id'] for row in quality_rows],
        'gates': {'median_new_over_old_maximum': 1.05, 'exact_math_required': True,
                  'unexpected_fallback_permitted': False, 'complete_calls_required': True},
        'limits': ['small analytical/structured controls, no representative full five-objective study',
                   'native CLI and installed-wheel qualification are separate',
                   'new cursor/cycle/binding fields excluded explicitly; all common mathematical fields compare float.hex',
                   'a mismatch stops the serial campaign; no case is replaced or dropped',
                   'progress-policy group uses the same new source with None versus 0.001; differences are policy effects, not speedup',
                   'analytical zero/preparatory-gain cases are independently tested units, not timed solver cases']}
    output.mkdir(parents=True)
    write_new(output / 'plan.json', plan)
    write_new(output / 'plan-sha256.json', {'sha256': digest_bytes((output / 'plan.json').read_bytes())})
    return plan


def check_frozen(root, plan):
    if digest_bytes(Path(__file__).read_bytes()) != plan['harness_sha256']:
        raise ValueError('harness changed after preparation')
    for variant, source in plan['sources'].items():
        if source_inventory(root / source) != plan['source_inventories'][variant]:
            raise ValueError(f'{variant} source changed after preparation')


def quality(case, result):
    weights = tuple(Fraction.from_float(value) for value in case['weights'])
    utilities = [sum((Fraction.from_float(value) * weight for value, weight in zip(row, weights, strict=True)), Fraction())
                 for row in case['alternatives']]
    winners = [index for index, value in enumerate(utilities) if value == max(utilities)]
    answers_correct = True
    for answer in result.answers:
        query = answer.query
        difference = weights[query.goal_index_a] - Fraction.from_float(query.value) * weights[query.goal_index_b]
        expected = '>' if difference > 0 else '<' if difference < 0 else '='
        answers_correct &= answer.answer == expected
    return {'exact_target_winners': winners, 'actual_answer_signs_correct': answers_correct,
            'selection_correct': None if result.selected_candidate_index is None else result.selected_candidate_index in winners}


def child(root, directory, job_id):
    plan = load_plan(directory)
    check_frozen(root, plan)
    job = next(item for item in plan['jobs'] if item['job_id'] == job_id)
    condition = next(item for item in plan['conditions'] if item['condition_id'] == job['condition_id'])
    case = plan['cases'][condition['case_id']]
    source = (root / plan['sources'][job['variant']]).resolve()
    import multiprocessing
    import otqa
    from otqa import AlgorithmPolicy, QueryBudget, SingleCandidateStop, SolverExecution, VolumeConfidenceStop
    from otqa.answers import SimulatedAnswers
    if Path(otqa.__file__).resolve() != source / 'otqa/__init__.py':
        raise ValueError('SDK source isolation failed')
    policy_values = dict(query_strategy=condition['strategy'], depth=condition['depth'],
        higher_depth_query_source='both', grid_size=5, planning_evaluation=condition['evaluation'],
        stopping=VolumeConfidenceStop(.99) if condition['evaluation'] == 'stop_aware' else SingleCandidateStop(),
        horizon_execution=condition['mode'])
    if job['variant'] == 'new':
        policy_values['min_expected_progress'] = job['minimum']
    policy = AlgorithmPolicy(**policy_values)
    execution = SolverExecution(8, multiprocessing.get_context('forkserver'))
    problem = otqa.Problem(tuple(tuple(row) for row in case['alternatives']))
    provider = SimulatedAnswers(tuple(case['weights']))
    started = time.perf_counter()
    try:
        result = otqa.solve(problem, policy, provider, budget=QueryBudget(12), execution=execution)
        elapsed = time.perf_counter() - started
        record = {'job': job, 'status': 'returned', 'api_call_wall_seconds': elapsed,
                  'source_path': str(source), 'python': sys.version, 'platform': platform.platform(),
                  'dependencies': {name: importlib.metadata.version(name) for name in ('numpy', 'scipy', 'highspy')},
                  'native_thread_environment': {key: os.environ.get(key) for key in THREAD_VARIABLES},
                  'mathematical_result': mathematical(result), 'quality': quality(case, result),
                  'execution_evidence': mathematical(getattr(result, 'planning_cycles', ())),
                  'fallbacks': sum(cycle.restart_reason is not None for cycle in getattr(result, 'planning_cycles', ())),
                  'solved': result.solved, 'exactly_solved': result.exactly_solved,
                  'termination_reason': result.termination_reason,
                  'selected_candidate_index': result.selected_candidate_index,
                  'final_candidate_count': result.final_state.candidate_count,
                  'final_candidate_indices': list(result.final_state.candidate_indices),
                  'final_candidate_volume_shares': mathematical(result.final_state.candidate_volume_shares),
                  'query_counts': mathematical(result.query_counts), 'answered_new': result.query_counts.answered_new}
    except BaseException as error:
        record = {'job': job, 'status': 'failed', 'api_call_wall_seconds': None,
                  'failed_call_elapsed_seconds': time.perf_counter() - started,
                  'error': {'type': type(error).__name__, 'message': str(error), 'traceback': traceback.format_exc()}}
    check_frozen(root, plan)
    write_new(directory / 'results' / (job_id + '.json'), record)
    return 0 if record['status'] == 'returned' else 1


def read_record(path, job):
    record = json.loads(path.read_text())
    if record.get('job') != job:
        raise ValueError(f'result job identity mismatch: {job["job_id"]}')
    if record.get('status') not in ('returned', 'failed'):
        raise ValueError(f'invalid result status: {job["job_id"]}')
    if record['status'] == 'returned':
        elapsed = record.get('api_call_wall_seconds')
        if isinstance(elapsed, bool) or not isinstance(elapsed, (float, int)) or not math.isfinite(elapsed) or elapsed <= 0:
            raise ValueError(f'invalid full-call timing: {job["job_id"]}')
        if any(record['native_thread_environment'].get(key) != '1' for key in THREAD_VARIABLES):
            raise ValueError(f'nonmatching native thread environment: {job["job_id"]}')
    return record


def outcome(record):
    if record['status'] != 'returned':
        return {'status': record['status'], 'error': record.get('error')}
    keys = ('solved', 'exactly_solved', 'termination_reason', 'selected_candidate_index',
            'final_candidate_count', 'final_candidate_indices', 'final_candidate_volume_shares',
            'query_counts', 'quality', 'fallbacks', 'api_call_wall_seconds')
    return {'status': record['status'], **{key: record[key] for key in keys}}


def audit(directory, plan):
    rows, pairs = [], []
    for condition in plan['conditions']:
        group = []
        for block in range(1, 4):
            jobs = [job for job in plan['jobs'] if job['group'] == 'sdk_parity_timing' and
                    job['condition_id'] == condition['condition_id'] and job['block'] == block]
            paths = {job['variant']: directory / 'results' / (job['job_id'] + '.json') for job in jobs}
            if not all(path.exists() for path in paths.values()):
                continue
            data = {job['variant']: read_record(paths[job['variant']], job) for job in jobs}
            comparable = all(item['status'] == 'returned' for item in data.values())
            same_math = comparable and data['old']['mathematical_result'] == data['new']['mathematical_result']
            same_environment = comparable and all(data['old'][key] == data['new'][key] for key in
                ('python', 'platform', 'dependencies', 'native_thread_environment'))
            eligible = same_math and same_environment and data['new']['fallbacks'] == 0 and all(
                item['quality']['actual_answer_signs_correct'] for item in data.values())
            ratio = data['new']['api_call_wall_seconds'] / data['old']['api_call_wall_seconds'] if eligible else None
            pair = {'condition_id': condition['condition_id'], 'block': block, 'math_equal': same_math,
                    'environment_equal': same_environment,
                    'eligible': eligible, 'ratio_new_over_old': ratio,
                    'old': data['old'].get('api_call_wall_seconds'), 'new': data['new'].get('api_call_wall_seconds'),
                    'outcomes': {variant: outcome(item) for variant, item in data.items()},
                    'result_sha256': {variant: digest_bytes(path.read_bytes()) for variant, path in paths.items()}}
            pairs.append(pair)
            group.append(pair)
        complete = len(group) == 3 and all(pair['eligible'] for pair in group)
        old = [pair['old'] for pair in group] if complete else []
        new = [pair['new'] for pair in group] if complete else []
        median_ratio = statistics.median(new) / statistics.median(old) if complete else None
        rows.append({'condition': condition, 'paired_blocks_complete': len(group), 'eligible': complete,
                     'old_seconds': old, 'new_seconds': new, 'ratio_of_medians': median_ratio,
                     'aggregate_ratio': sum(new) / sum(old) if complete else None,
                     'screening_passed': complete and median_ratio <= 1.05})
    policy_rows = []
    for condition_id in plan['policy_condition_ids']:
        jobs = [job for job in plan['jobs'] if job['group'] == 'progress_policy' and job['condition_id'] == condition_id]
        results = []
        for job in jobs:
            path = directory / 'results' / (job['job_id'] + '.json')
            if path.exists():
                record = read_record(path, job)
                results.append({'minimum': job['minimum'], 'job_id': job['job_id'], 'outcome': outcome(record),
                                'result_sha256': digest_bytes(path.read_bytes())})
        policy_rows.append({'condition_id': condition_id, 'complete': len(results) == len(jobs), 'results': results})
    expected_pairs = sum(job['group'] == 'sdk_parity_timing' for job in plan['jobs']) // 2
    all_complete = len(pairs) == expected_pairs and all(row['eligible'] for row in rows)
    policy_complete = all(row['complete'] and all(result['outcome']['status'] == 'returned' and
        result['outcome']['quality']['actual_answer_signs_correct'] for result in row['results']) for row in policy_rows)
    ledger = []
    for job in plan['jobs']:
        path = directory / 'results' / (job['job_id'] + '.json')
        ledger.append({'job': job, 'outcome': outcome(read_record(path, job)) if path.exists() else {'status': 'pending'},
                       'result_sha256': digest_bytes(path.read_bytes()) if path.exists() else None})
    return {'purpose': plan['purpose'], 'plan_sha256': digest_bytes((directory / 'plan.json').read_bytes()),
            'completed_pairs': len(pairs), 'planned_pairs': expected_pairs,
            'complete_and_math_valid': all_complete, 'pairs': pairs, 'conditions': rows,
            'all_planned_calls': ledger,
            'policy_effect_conditions': policy_rows, 'policy_effect_calls_complete_and_answer_valid': policy_complete,
            'screening_passed': all_complete and all(row['screening_passed'] for row in rows)}


def run(root, directory):
    plan = load_plan(directory)
    check_frozen(root, plan)
    if (directory / 'report.json').exists():
        raise FileExistsError('terminal comparison report already exists')
    for job in plan['jobs']:
        result_path = directory / 'results' / (job['job_id'] + '.json')
        if result_path.exists():
            raise FileExistsError('SDK campaign has no implicit retry/resume; preserve its partial run')
        check_frozen(root, plan)
        env = {**os.environ, 'PYTHONPATH': str(root / plan['sources'][job['variant']]),
               'PYTHONDONTWRITEBYTECODE': '1', **{key: '1' for key in THREAD_VARIABLES}}
        with (directory / (job['job_id'] + '.stdout')).open('xb') as stdout, (
             directory / (job['job_id'] + '.stderr')).open('xb') as stderr:
            completed = subprocess.run([sys.executable, str(Path(__file__).resolve()), 'child', '--project-root', str(root),
                '--output', str(directory), '--job-id', job['job_id']], cwd=root, env=env, stdout=stdout, stderr=stderr)
        if completed.returncode or not result_path.exists():
            break
        if job['group'] == 'sdk_parity_timing' and job['variant'] == ('new' if job['block'] % 2 else 'old'):
            current = audit(directory, plan)
            if not current['pairs'][-1]['eligible']:
                break
    check_frozen(root, plan)
    report = audit(directory, plan)
    write_new(directory / 'report.json', report)
    return 0 if report['screening_passed'] and report['policy_effect_calls_complete_and_answer_valid'] else 1


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('prepare', 'run', 'audit', 'child'))
    parser.add_argument('--project-root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--job-id')
    parser.add_argument('--new-source', type=Path, default=Path('src'),
                        help='project-relative frozen new SDK src directory; prepare only')
    args = parser.parse_args(argv)
    root, directory = args.project_root.resolve(), args.output.resolve()
    if args.command == 'prepare':
        plan = prepare(root, directory, new_source=args.new_source)
        print(json.dumps({'conditions': len(plan['conditions']), 'calls': len(plan['jobs']), 'plan': str(directory / 'plan.json')}))
        return 0
    if args.command == 'child':
        return child(root, directory, args.job_id)
    if args.command == 'audit':
        plan = load_plan(directory)
        check_frozen(root, plan)
        print(json.dumps(audit(directory, plan), indent=2))
        return 0
    return run(root, directory)


if __name__ == '__main__':
    raise SystemExit(main())
