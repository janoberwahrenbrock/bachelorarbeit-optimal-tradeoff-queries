"""Matched installed-wheel CLI screening, separate from SDK and quality studies.

Proposal/probe/prepare never start a solver. Run requires an explicit frozen new
source and qualified profile; all old/new CLI calls execute serially. Artifacts
are never overwritten and a partial campaign has no implicit retry.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import json
import os
from pathlib import Path
import statistics
import subprocess
import time
from uuid import uuid4


OLD_SOURCE = 'b40342c2cbf7712992ce6a62b01647b5c275dbc3b6358430b637b206e1d41e4a'
THREADS = ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS',
           'BLIS_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS', 'NUMEXPR_NUM_THREADS')
EXCLUDE = frozenset(('execution_cursor', 'planning_cycles', 'planning_cycle', 'continuation_binding'))
SCALARS = frozenset(('value', 'probability', 'expected_terminal_candidates', 'expected_terminal_loss',
    'expected_queries', 'gain', 'rate', 'maximum_volume_share', 'selected_candidate_volume', 'selected_candidate_volume_share'))
MAPS = frozenset(('candidate_volumes', 'candidate_volume_shares', 'answer_probabilities', 'lexicographic_expected_values'))

PROBE = """
from pathlib import Path
import json,sys,platform,importlib.metadata
from otqa.runtime.source import loaded_source
from otqa.runtime.profiles import production_resolver
root, path = Path(sys.argv[1]),Path(sys.argv[2])
profile=json.loads(path.read_bytes())
admitted=production_resolver(root,profile,'standalone')
source,inventory,provenance=loaded_source()
print(json.dumps({'source':source,'python_version':platform.python_version(),'python_full':sys.version,
 'platform':platform.platform(),'packages':{n:importlib.metadata.version(n) for n in profile['packages']},
 'profile':profile,'production_standalone_admission':True,'interpreter':sys.executable}))
"""

VERIFY = """
from pathlib import Path
import json,sys
from otqa.runtime.validation import verify_result
from otqa.runtime.source import loaded_source
root=Path(sys.argv[1]); result_path=root/'result.json'
manifest=json.loads((root/'manifest.json').read_bytes())
source,_,_=loaded_source()
result=verify_result(result_path,root,manifest)
if source['source_sha256'] != manifest['source']['source_sha256']:
 raise ValueError('result was not produced by the expected installed source')
print(json.dumps({'source':source,'verified_result':True,'result':result,'manifest':manifest}))
"""


def digest(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def write_new(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n')
        stream.flush()
        os.fsync(stream.fileno())


def update_status(directory, value):
    """Only operational progress replaces bytes; raw results remain immutable."""
    temporary = directory / ('.live-status-' + uuid4().hex + '.tmp')
    write_new(temporary, {**value, 'updated_at_utc': datetime.now(timezone.utc).isoformat()})
    os.replace(temporary, directory / 'live-status.json')
    descriptor = os.open(directory, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def process_identity():
    value = {'pid': os.getpid(), 'hostname': os.uname().nodename, 'boot_id': None, 'start_ticks': None}
    if Path('/proc/self/stat').is_file():
        value['start_ticks'] = int(Path('/proc/self/stat').read_text().rsplit(')', 1)[1].split()[19])
        value['boot_id'] = Path('/proc/sys/kernel/random/boot_id').read_text().strip()
    return value


def environment():
    env = dict(os.environ)
    env.pop('PYTHONPATH', None)
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    env['PYTHONNOUSERSITE'] = '1'
    env.update({name: '1' for name in THREADS})
    return env


def project_output(root, directory):
    if not (root / 'otqa-project.json').is_file() or not directory.is_relative_to(root / 'runs'):
        raise ValueError('native comparison needs a marked project and an output below runs/')


def probe(root, python, profile):
    completed = subprocess.run([str(python), '-c', PROBE, str(root), str(profile)], cwd=root,
        env=environment(), text=True, capture_output=True, check=True)
    return json.loads(completed.stdout)


def cases():
    return {
        'analytic-g2-a3': {'alternatives': [[1., 0.], [0., 1.], [.6, .6]], 'weights': [.55, .45]},
        'analytic-g3-a3': {'alternatives': [[1., 0., 0.], [0., 1., 0.], [.4, .4, 1.]],
                           'weights': [.45, .35, .2]},
    }


def conditions():
    rows = []
    for case_id in cases():
        for strategy, mode in (('fixed', 'receding'), ('fixed', 'countdown'), ('reduction_per_query', 'receding')):
            for evaluation in ('candidate_count', 'stop_aware'):
                rows.append({'condition_id': f'condition{len(rows) + 1:02d}', 'case_id': case_id,
                    'query_strategy': strategy, 'horizon_execution': mode, 'planning_evaluation': evaluation,
                    'depth': 2, 'stopping': {'rule': 'volume_confidence', 'threshold': .99}
                        if evaluation == 'stop_aware' else {'rule': 'single_candidate'}})
    return rows


def proposal(root, directory):
    project_output(root, directory)
    rows = conditions()
    value = {'schema_version': 1, 'purpose': 'matched_complete_native_cli_calls_progress_disabled',
        'created_at_utc': datetime.now(timezone.utc).isoformat(), 'cases': cases(), 'conditions': rows,
        'paired_blocks': [1, 2, 3], 'conditional_extra_blocks': [4, 5, 6],
        'ordering': 'all initial conditions, then one extension of affected inconclusive conditions; old/new order alternates by block',
        'runtime': {'workers': 8, 'native_threads': 1, 'start_method': 'forkserver', 'grid_size': 5,
                    'max_queries': 12, 'case_timeout_seconds': None, 'profile': False, 'trace_level': 'standard'},
        'screening': {'maximum_median_pair_ratio': 1.05,
            'clear_pass': 'all measured paired native CLI ratios <=1.05',
            'clear_regression': 'all measured paired native CLI ratios >1.05',
            'inconclusive': 'ratios cross1.05; after3blocks add exactly3more for every such condition; still crossing remains inconclusive'},
        'semantic_gates': {'same_actual_query_identity_and_all_common_scores_bits': True,
            'same_candidates_and_winner': True, 'correct_complete_solutions': True, 'new_fallbacks': 0},
        'limits': ['small analytical full native calls, not representative five-objective throughput',
            'candidate and stop-aware modes have separate matched conditions',
            'v2 execution metadata explicitly excluded from old/v2 mathematical comparison',
            'all source qualification/admission checks outside solver remain part of measured CLI walltime',
            'no solver starts before root authorizes frozen new wheel/profile and SDK screening has ended',
            'no fallback-dependent old/new case may be substituted or silently dropped']}
    write_new(directory / 'proposal.json', value)
    return value


def config(condition, variant):
    algorithm = {name: condition[name] for name in ('query_strategy', 'depth', 'horizon_execution', 'planning_evaluation', 'stopping')}
    algorithm.update(grid_size=5, higher_depth_query_source='both')
    if variant == 'new':
        algorithm['min_expected_progress'] = None
    return {'schema_version': 2 if variant == 'new' else 1,
        'configuration_id': condition['condition_id'] + '-' + variant, 'algorithm': algorithm,
        'budget': {'max_queries': 12}, 'execution': {'workers': 8, 'native_threads': 1, 'start_method': 'forkserver',
            'cache_policy_id': 'bounded_v1', 'case_timeout_seconds': None},
        'recording': {'durability': 'per_answer', 'trace_level': 'standard', 'profile': False,
                      'telemetry_failure_policy': 'continue'}}


def prepare(root, directory, args):
    project_output(root, directory)
    proposal_path = directory / 'proposal.json'
    proposed = json.loads(proposal_path.read_bytes()) if proposal_path.exists() else proposal(root, directory)
    probes = {variant: probe(root, getattr(args, variant + '_python'), getattr(args, variant + '_profile'))
              for variant in ('old', 'new')}
    expected = {'old': OLD_SOURCE, 'new': args.expected_new_source}
    for variant, evidence in probes.items():
        if evidence['source']['source_sha256'] != expected[variant]:
            raise ValueError(f'{variant} installed source differs from its explicitly frozen identity')
    def numerical_environment(value):
        return {'python': value['python_full'], 'platform': value['platform'],
            'packages': {key: item for key, item in value['packages'].items()
                         if key != 'bachelorarbeit-optimal-tradeoff-queries'}}
    if numerical_environment(probes['old']) != numerical_environment(probes['new']):
        raise ValueError('old/new actual Python/platform/runtime packages are not identical')
    inputs = {}
    for case_id, case in proposed['cases'].items():
        problem = {'schema_version': 1, 'problem_id': case_id,
            'alternative_ids': [f'a{i}' for i in range(len(case['alternatives']))],
            'objective_ids': [f'g{i}' for i in range(len(case['weights']))], 'alternatives': case['alternatives']}
        oracle = {'schema_version': 1, 'problem_id': case_id, 'target_weights': case['weights']}
        for name, value in (('problem', problem), ('oracle', oracle)):
            path = directory / 'inputs' / (case_id + '-' + name + '.json')
            write_new(path, value)
            inputs[path.relative_to(root).as_posix()] = digest(path.read_bytes())
    for condition in proposed['conditions']:
        for variant in ('old', 'new'):
            path = directory / 'inputs' / (condition['condition_id'] + '-' + variant + '.json')
            write_new(path, config(condition, variant))
            inputs[path.relative_to(root).as_posix()] = digest(path.read_bytes())
    jobs = [{'job_id': f'{condition["condition_id"]}-b{block}-{variant}', 'condition_id': condition['condition_id'],
            'block': block, 'variant': variant, 'conditional': block > 3}
            for block in range(1, 7) for condition in proposed['conditions']
            for variant in (('old', 'new') if block % 2 else ('new', 'old'))]
    plan = {**proposed, 'proposal_sha256': digest(proposal_path.read_bytes()),
        'harness_sha256': digest(Path(__file__).read_bytes()), 'source_probes': probes,
        'interpreters': {variant: str(getattr(args, variant + '_python').absolute()) for variant in ('old', 'new')},
        'profiles': {variant: {'path': str(getattr(args, variant + '_profile').relative_to(root)),
            'sha256': digest(getattr(args, variant + '_profile').read_bytes())} for variant in ('old', 'new')},
        'input_sha256': inputs, 'jobs': jobs}
    write_new(directory / 'plan.json', plan)
    return plan


def check_frozen(root, directory, plan):
    if digest(Path(__file__).read_bytes()) != plan['harness_sha256']:
        raise ValueError('native comparison harness changed after preparation')
    if digest((directory / 'proposal.json').read_bytes()) != plan['proposal_sha256']:
        raise ValueError('native comparison proposal changed after preparation')
    for path, expected in plan['input_sha256'].items():
        if digest((root / path).read_bytes()) != expected:
            raise ValueError('frozen native input changed: ' + path)
    for reference in plan['profiles'].values():
        if digest((root / reference['path']).read_bytes()) != reference['sha256']:
            raise ValueError('frozen execution profile changed')


def mathematical(value, name='', all_numbers=False):
    if type(value) in (int, float) and (all_numbers or name in SCALARS):
        return {'float_hex': float(value).hex()}
    if isinstance(value, dict):
        return {key: mathematical(item, key, all_numbers or name in MAPS) for key, item in value.items() if key not in EXCLUDE}
    if isinstance(value, list):
        return [mathematical(item, name, all_numbers or name in MAPS) for item in value]
    return value


def quality(case, problem, solver):
    weights = [Fraction.from_float(value) for value in case['weights']]
    utilities = [sum((Fraction.from_float(value) * weight for value, weight in zip(row, weights, strict=True)), Fraction())
                 for row in case['alternatives']]
    winners = [identifier for identifier, utility in zip(problem['alternative_ids'], utilities, strict=True) if utility == max(utilities)]
    for answer in solver['answered_queries']:
        delta = weights[answer['goal_index_a']] - Fraction.from_float(float(answer['value'])) * weights[answer['goal_index_b']]
        expected = '>' if delta > 0 else '<' if delta < 0 else '='
        if answer['answer'] != expected:
            raise ValueError('stored actual answer differs from exact rational sign')
    return {'winner_ids': winners, 'selected_correct': solver['selected_candidate_id'] in winners,
            'actual_answers_correct': True}


def verify_job(root, directory, plan, job, target, condition, receipt):
    """Attach verified evidence; the caller preserves a receipt for gate failures."""
    variant, case_id = job['variant'], condition['case_id']
    python = plan['interpreters'][variant]
    verified = subprocess.run([python, '-c', VERIFY, str(target)], cwd=root, env=environment(),
                              text=True, capture_output=True)
    receipt['reader_returncode'] = verified.returncode
    if verified.returncode:
        receipt['reader_error'] = verified.stderr
        return
    evidence = json.loads(verified.stdout)
    result, manifest = evidence['result'], evidence['manifest']
    expected_source = plan['source_probes'][variant]['source']['source_sha256']
    if evidence['source']['source_sha256'] != expected_source:
        raise ValueError('native job source changed after frozen admission')
    actual = manifest['environment']
    admitted = plan['source_probes'][variant]
    if actual['python'] != admitted['python_version'] or actual['packages'] != admitted['packages']:
        raise ValueError('native job environment changed after frozen admission')
    if any(actual['native_thread_environment'].get(name) != '1' for name in THREADS):
        raise ValueError('native job did not retain exactly one native thread per process')
    expected_config = config(condition, variant)
    if (manifest['effective_algorithm'] != expected_config['algorithm']
            or manifest['effective_execution'] != expected_config['execution']
            or manifest['effective_recording'] != expected_config['recording']
            or manifest['effective_budget'] != expected_config['budget']):
        raise ValueError('native job effective configuration differs from frozen controls')
    solver = result['solver_result']
    receipt.update(source=manifest['source'], result_sha256=digest((target / 'result.json').read_bytes()),
        journal_sha256=result['journal']['sha256'] if result['journal'] else None,
        result_ref=(target / 'result.json').relative_to(root).as_posix(), status=result['execution_status'],
        api_seconds=result['timings']['api_call_wall_seconds'], case_seconds=result['timings']['case_elapsed_seconds'],
        effective_execution=manifest['effective_execution'], native_thread_environment=actual['native_thread_environment'])
    if solver is not None:
        problem = json.loads((directory / 'inputs' / (case_id + '-problem.json')).read_bytes())
        receipt.update(solved=solver['solved'], termination_reason=solver['termination_reason'],
            answered_queries=result['query_counts']['answered_new'], mathematical_result=mathematical(solver),
            quality=quality(plan['cases'][case_id], problem, solver),
            fallbacks=sum(cycle['restart_reason'] is not None for cycle in solver.get('planning_cycles', ())))
    receipt['verified'] = True


def run_job(root, directory, plan, job):
    check_frozen(root, directory, plan)
    condition = next(item for item in plan['conditions'] if item['condition_id'] == job['condition_id'])
    variant, case_id = job['variant'], condition['case_id']
    python = plan['interpreters'][variant]
    target = directory / 'cases' / job['job_id']
    receipt_path = directory / 'receipts' / (job['job_id'] + '.json')
    if target.exists() or receipt_path.exists():
        raise FileExistsError('native comparison never implicitly retries an existing attempt')
    command = [python, '-m', 'otqa', '--project-root', str(root), 'solve', '--source-root', str(root),
        '--problem', str(directory / 'inputs' / (case_id + '-problem.json')),
        '--oracle', str(directory / 'inputs' / (case_id + '-oracle.json')),
        '--config', str(directory / 'inputs' / (job['condition_id'] + '-' + variant + '.json')),
        '--execution-profile', str(root / plan['profiles'][variant]['path']),
        '--answers', 'simulated', '--output', str(target)]
    logs = directory / 'logs'
    logs.mkdir(exist_ok=True)
    with (logs / (job['job_id'] + '.stdout')).open('xb') as stdout, (logs / (job['job_id'] + '.stderr')).open('xb') as stderr:
        start = time.perf_counter()
        completed = subprocess.run(command, cwd=root, env=environment(), stdout=stdout, stderr=stderr)
        elapsed = time.perf_counter() - start
    receipt = {'job': job, 'cli_returncode': completed.returncode, 'cli_wall_seconds': elapsed,
        'command': command, 'verified': False}
    try:
        if (target / 'result.json').exists():
            verify_job(root, directory, plan, job, target, condition, receipt)
        check_frozen(root, directory, plan)
    except Exception as exc:
        receipt.update(verified=False, gate_error={'type': type(exc).__name__, 'message': str(exc)})
    write_new(receipt_path, receipt)
    return receipt


def pairs(directory, plan):
    rows = []
    for condition in plan['conditions']:
        for block in range(1, 7):
            data = {}
            for variant in ('old', 'new'):
                path = directory / 'receipts' / f'{condition["condition_id"]}-b{block}-{variant}.json'
                if path.exists():
                    data[variant] = json.loads(path.read_bytes())
            if set(data) != {'old', 'new'}:
                continue
            eligible = all(value['verified'] and value['cli_returncode'] == 0 and value.get('solved')
                and value['quality']['selected_correct'] and value.get('fallbacks') == 0 for value in data.values())
            same = eligible and data['old']['mathematical_result'] == data['new']['mathematical_result']
            rows.append({'condition_id': condition['condition_id'], 'block': block, 'eligible': same,
                'math_equal': same, 'cli_ratio': data['new']['cli_wall_seconds'] / data['old']['cli_wall_seconds'] if same else None,
                'api_ratio': data['new']['api_seconds'] / data['old']['api_seconds'] if same else None,
                'old_cli_seconds': data['old']['cli_wall_seconds'], 'new_cli_seconds': data['new']['cli_wall_seconds'],
                'old_api_seconds': data['old'].get('api_seconds'), 'new_api_seconds': data['new'].get('api_seconds')})
    return rows


def screening(values):
    if not values:
        return 'pending'
    if max(values) <= 1.05:
        return 'screening_pass'
    if min(values) > 1.05:
        return 'screening_regression'
    return 'inconclusive'


def audit(directory, plan):
    paired, rows = pairs(directory, plan), []
    for condition in plan['conditions']:
        group = [item for item in paired if item['condition_id'] == condition['condition_id']]
        ratios = [item['cli_ratio'] for item in group if item['eligible']]
        rows.append({'condition': condition, 'complete_pairs': len(group), 'mathematically_eligible': len(ratios) == len(group),
            'median_pair_cli_ratio': statistics.median(ratios) if ratios else None,
            'minimum_pair_cli_ratio': min(ratios) if ratios else None, 'maximum_pair_cli_ratio': max(ratios) if ratios else None,
            'screening': screening(ratios),
            'median_pair_api_ratio': statistics.median(item['api_ratio'] for item in group if item['eligible']) if ratios else None})
    return {'purpose': plan['purpose'], 'plan_sha256': digest((directory / 'plan.json').read_bytes()),
        'pairs': paired, 'conditions': rows, 'all_initial_pairs_complete': all(item['complete_pairs'] >= 3 for item in rows),
        'all_completed_pairs_math_valid': all(item['eligible'] for item in paired),
        'limits': plan['limits'], 'no_geometric_recertification_claimed': True}


def run(root, directory):
    import fcntl
    project_output(root, directory)
    plan = json.loads((directory / 'plan.json').read_bytes())
    if (directory / 'report.json').exists():
        raise FileExistsError('native screening already has a terminal report')
    check_frozen(root, directory, plan)
    with (directory / 'driver.lock').open('a+') as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        identity = process_identity()
        write_new(directory / 'driver-process.json', identity)
        failed = False
        for job in (item for item in plan['jobs'] if not item['conditional']):
            update_status(directory, {'phase': 'running_initial_blocks', 'current_job': job,
                'process': identity, 'completed_cli_calls': len(list((directory / 'receipts').glob('*.json')))})
            value = run_job(root, directory, plan, job)
            if not value['verified'] or value['cli_returncode'] != 0:
                failed = True
                break
            if job['variant'] == ('new' if job['block'] % 2 else 'old'):
                pair = next(item for item in pairs(directory, plan)
                            if (item['condition_id'], item['block']) == (job['condition_id'], job['block']))
                if not pair['eligible']:
                    failed = True
                    break
        initial = audit(directory, plan)
        write_new(directory / 'initial-screening.json', initial)
        affected = [row['condition']['condition_id'] for row in initial['conditions'] if row['screening'] == 'inconclusive'] if not failed else []
        write_new(directory / 'extension-decision.json', {'affected_conditions': affected,
            'blocks': [4, 5, 6] if affected else [], 'additional_blocks_after_this': False})
        if not failed:
            for job in (item for item in plan['jobs'] if item['conditional'] and item['condition_id'] in affected):
                update_status(directory, {'phase': 'running_declared_extension', 'current_job': job,
                    'process': identity, 'completed_cli_calls': len(list((directory / 'receipts').glob('*.json')))})
                value = run_job(root, directory, plan, job)
                if not value['verified'] or value['cli_returncode'] != 0:
                    failed = True
                    break
                if job['variant'] == ('new' if job['block'] % 2 else 'old'):
                    pair = next(item for item in pairs(directory, plan)
                                if (item['condition_id'], item['block']) == (job['condition_id'], job['block']))
                    if not pair['eligible']:
                        failed = True
                        break
        final = audit(directory, plan)
        final.update(stopped_for_failure_or_math_mismatch=failed, extended_conditions=affected,
            completed_at_utc=datetime.now(timezone.utc).isoformat())
        final['screening_regressions'] = [row['condition']['condition_id'] for row in final['conditions']
                                         if row['screening'] == 'screening_regression']
        final['screening_inconclusive'] = [row['condition']['condition_id'] for row in final['conditions']
                                          if row['screening'] == 'inconclusive']
        final['screening_passed'] = (not failed and final['all_initial_pairs_complete']
            and final['all_completed_pairs_math_valid']
            and all(row['screening'] == 'screening_pass' for row in final['conditions']))
        write_new(directory / 'report.json', final)
        update_status(directory, {'phase': 'completed' if not failed else 'stopped_for_failure',
            'process': identity, 'current_job': None,
            'completed_cli_calls': len(list((directory / 'receipts').glob('*.json'))),
            'screening_passed': final['screening_passed'],
            'report_sha256': digest((directory / 'report.json').read_bytes())})
    if final['screening_passed']:
        return 0
    if final['screening_inconclusive'] and not failed and not final['screening_regressions']:
        return 2
    return 1


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('proposal', 'probe', 'prepare', 'run', 'audit'))
    parser.add_argument('--project-root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    for variant in ('old', 'new'):
        parser.add_argument('--' + variant + '-python', type=Path)
        parser.add_argument('--' + variant + '-profile', type=Path)
    parser.add_argument('--expected-new-source')
    args = parser.parse_args(argv)
    root, directory = args.project_root.resolve(), args.output.resolve()
    project_output(root, directory)
    if args.command == 'proposal':
        value = proposal(root, directory)
    elif args.command == 'probe':
        if args.old_python is None or args.old_profile is None:
            parser.error('probe needs --old-python and --old-profile')
        value = probe(root, args.old_python, args.old_profile)
        write_new(directory / 'old-admission.json', value)
    elif args.command == 'prepare':
        if any(getattr(args, name) is None for name in ('old_python', 'old_profile', 'new_python', 'new_profile', 'expected_new_source')):
            parser.error('prepare needs both interpreters/profiles and the frozen expected new source')
        value = prepare(root, directory, args)
    elif args.command == 'audit':
        value = audit(directory, json.loads((directory / 'plan.json').read_bytes()))
    else:
        return run(root, directory)
    print(json.dumps({'command': args.command, 'conditions': len(value.get('conditions', [])), 'output': str(directory)}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
