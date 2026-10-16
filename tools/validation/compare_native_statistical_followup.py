"""Separate prospective fixed-30 native followup; never rewrites old screening.

prepare is LOCAL, copies already bound inputs/admission evidence and creates the
complete 720-call plan. run needs separate authorization, rechecks installed
admission and executes one serial pass. No implicit retries or extensions.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from fractions import Fraction
import importlib.util
import json
import math
import os
from pathlib import Path
import random
import statistics

ORIGINAL_SHA = '50e0a80cc94505a407da04960c53686fdf4bb3b83575fb3cb2007c3e795316d0'
NEW_SOURCE = '47c3d8b2f66446e1ba07f4538879ac9a99bdb567f3082bff254564ff2736ca76'
NEW_PROFILE = 'd44db93f74d77843f96c6a8c6d6e1e004f27c8e6e3f6117d810cc2c676e9cadf'
N, SEED, MARGIN, ALPHA = 30, 2026101603, 1.05, Fraction(1, 240)


def original_tool():
    path = Path(__file__).with_name('compare_native_countdown_progress.py')
    import hashlib
    if hashlib.sha256(path.read_bytes()).hexdigest() != ORIGINAL_SHA:
        raise ValueError('Original screening harness bytes changed')
    spec = importlib.util.spec_from_file_location('_otqa_original_native_screen', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


original = original_tool()
def read(path):
    return json.loads(path.read_bytes())


def sha(path):
    return original.digest(path.read_bytes())


def exact_tail(q):
    if type(q) is not int or not 0 <= q <= N:
        raise ValueError('q must be an integer in 0..30')
    return Fraction(sum(math.comb(N, k) for k in range(q, N + 1)), 2**N)


def classify(ratios):
    if len(ratios) != N or any(type(r) not in (int, float) or not math.isfinite(r) or r <= 0 for r in ratios):
        raise ValueError('Exactly30 finite positive paired ratios required')
    below, ties = sum(r < MARGIN for r in ratios), sum(r == MARGIN for r in ratios)
    p = exact_tail(below)
    median = statistics.median(ratios)
    passed = p <= ALPHA and median <= MARGIN
    return {'n': N, 'strictly_below': below, 'ties_fail': ties, 'above': N - below - ties,
        'ratios': ratios, 'median_pair_ratio': median, 'exact_upper_tail': {'numerator': p.numerator, 'denominator': p.denominator},
        'classification': 'prospective_sign_gate_pass' if passed else 'inconclusive', 'passed': passed}


def schedule(condition_ids):
    if len(condition_ids) != 12 or len(set(condition_ids)) != 12:
        raise ValueError('Exactly12 unique matched conditions required')
    rng = random.Random(SEED)
    first = {}
    for cid in condition_ids:
        first[cid] = ['old'] * 15 + ['new'] * 15
        rng.shuffle(first[cid])
    rounds, jobs = [], []
    for block in range(1, N + 1):
        order = list(condition_ids)
        rng.shuffle(order)
        rounds.append(order)
        for cid in order:
            variants = ('old', 'new') if first[cid][block - 1] == 'old' else ('new', 'old')
            jobs.extend({'job_id': f'{cid}-b{block}-{v}', 'condition_id': cid, 'block': block,
                         'variant': v, 'conditional': False} for v in variants)
    return rounds, first, jobs


def validate_plan(plan):
    ids = [c['condition_id'] for c in plan['conditions']]
    rounds, first, jobs = schedule(ids)
    if (plan.get('seed') != SEED or plan['jobs'] != jobs or plan['round_condition_order'] != rounds
            or plan['first_variant_by_condition'] != first or len(jobs) != 720
            or plan['paired_blocks'] != list(range(1, 31)) or plan['conditional_extra_blocks'] != []):
        raise ValueError('Fixed720-call schedule differs from prospective seed/order')
    if plan['harness_sha256'] != ORIGINAL_SHA or plan['source_probes']['new']['source']['source_sha256'] != NEW_SOURCE:
        raise ValueError('Frozen source/harness mismatch')
    if plan['profiles']['new']['sha256'] != NEW_PROFILE or plan['conditions'] != original.conditions() or plan['cases'] != original.cases():
        raise ValueError('Frozen cases/configurations/profile differ')


def protocol():
    return {'purpose': 'NEW separate prospective native qualification after original max-rule screens remained inconclusive',
        'created_at_utc': datetime.now(timezone.utc).isoformat(), 'timing_pairs': 360, 'native_cli_calls': 720,
        'independent_analytical_problems': 2, 'matched_conditions': 12, 'fresh_pairs_per_condition': N,
        'source_sha256': NEW_SOURCE, 'new_profile_sha256': NEW_PROFILE,
        'threshold_binary64_hex': MARGIN.hex(), 'strict_sign': 'new_cli_wall / old_cli_wall < binary64(1.05); ties are failures',
        'test': 'H0 P(R<1.05)<=1/2 against greater, fixed N30; exact sum(comb(30,k),k=q..30)/2**30 <=1/240',
        'additional_gate': 'median paired ratio <=1.05; all720 calls and360 strict semantic pairs complete, correct, error-free, source-bound; groups proved dead',
        'q_boundary': {'q22_passes': exact_tail(22) <= ALPHA, 'q23_passes': exact_tail(23) <= ALPHA},
        'no_extension_or_selection': 'No outlier deletion, retries, old-pair carryover, early statistical success or extra blocks. Missing/duplicate/error/math mismatch prevents acceptance.',
        'ordering': 'Seed2026101603; for each condition exactly15 old-first and15 new-first; seeded shuffled condition order every round, recorded fully before any call.',
        'assumptions': 'The exact sign-test interpretation requires independent Bernoulli signs with the same success probability within each condition. Serial timing drift, autocorrelation or order effects can violate this. Balance/shuffling do not establish IID.',
        'multiplicity': 'Bonferroni alpha=0.05/12=1/240 across12 prespecified conditions; does not repair dependent signs within a condition. No unconditional95% performance guarantee.',
        'power': 'Fixed30 can remain inconclusive. There is no mirrored regression test: nonpassing conditions remain inconclusive, with above/tie/below counts fully shown.',
        'scope': 'Two small analytical problems,12 matched controls; timing repetitions are not360 independent quality problems or evidence of general five-objective throughput. No geometry recertification.',
        'old_rule': 'Original reports are immutable. Once ratios straddle1.05, adding measurements cannot remove that min/max crossing; the old declared extension cannot resolve that classification. This separate fresh experiment does not relabel those reports.',
        'primary_reference': {'title': 'SciPy binomtest: exact binomial test and greater alternative', 'url': 'https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.binomtest.html'}}


def prepare(root, directory, reference_path):
    original.project_output(root, directory)
    reference = read(reference_path)
    if reference['harness_sha256'] != ORIGINAL_SHA or reference['source_probes']['new']['source']['source_sha256'] != NEW_SOURCE:
        raise ValueError('Reference must be frozen release11 admission')
    original.check_frozen(root, reference_path.parent, reference)
    if reference['profiles']['new']['sha256'] != NEW_PROFILE:
        raise ValueError('Wrong release11 profile')
    declared = protocol()
    original.write_new(directory / 'protocol.json', declared)
    proposed = {key: reference[key] for key in ('cases', 'conditions', 'runtime', 'semantic_gates')}
    proposed.update(schema_version=1, purpose='prospective_native_sign_followup_30_pairs_720_calls', seed=SEED,
                    paired_blocks=list(range(1, 31)), conditional_extra_blocks=[], protocol_sha256=sha(directory / 'protocol.json'))
    original.write_new(directory / 'proposal.json', proposed)
    inputs = {}
    for relative, expected in reference['input_sha256'].items():
        source = root / relative
        if sha(source) != expected:
            raise ValueError('Reference input changed')
        target = directory / 'inputs' / source.name
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open('xb') as stream:
            stream.write(source.read_bytes())
        inputs[target.relative_to(root).as_posix()] = sha(target)
    rounds, first, jobs = schedule([c['condition_id'] for c in proposed['conditions']])
    plan = {**proposed, 'harness_sha256': ORIGINAL_SHA, 'followup_harness_sha256': sha(Path(__file__)),
        'proposal_sha256': sha(directory / 'proposal.json'), 'reference_plan': reference_path.relative_to(root).as_posix(),
        'reference_plan_sha256': sha(reference_path), 'source_probes': reference['source_probes'],
        'profiles': reference['profiles'], 'interpreters': reference['interpreters'], 'comparison_contract': reference['comparison_contract'],
        'input_sha256': inputs, 'jobs': jobs, 'round_condition_order': rounds, 'first_variant_by_condition': first}
    validate_plan(plan)
    original.write_new(directory / 'plan.json', plan)
    return plan


def frozen(root, directory, plan):
    validate_plan(plan)
    if read(directory / 'plan.json') != plan:
        raise ValueError('Frozen plan changed while executing')
    if sha(Path(__file__)) != plan['followup_harness_sha256'] or sha(directory / 'protocol.json') != plan['protocol_sha256']:
        raise ValueError('Prospective tool/protocol changed')
    if sha(root / plan['reference_plan']) != plan['reference_plan_sha256']:
        raise ValueError('Original reference plan changed')
    original.check_frozen(root, directory, plan)


def valid_receipt(receipt):
    return (receipt.get('verified') is True and receipt.get('cli_returncode') == receipt.get('reader_returncode') == 0
        and receipt.get('status') == 'completed' and receipt.get('solved') is True
        and receipt.get('fallbacks') == 0 and receipt.get('quality', {}).get('selected_correct') is True
        and receipt.get('quality', {}).get('actual_answers_correct') is True)


def raw_binding(root, directory, plan, receipt):
    job = receipt['job']
    target = directory / 'cases' / job['job_id']
    result, manifest = read(target / 'result.json'), read(target / 'manifest.json')
    if sha(target / 'result.json') != receipt['result_sha256'] or manifest['source'] != plan['source_probes'][job['variant']]['source']:
        raise ValueError('Raw result/source changed')
    journal = result['journal']
    data = (target / journal['path']).read_bytes()
    if (original.digest(data) != journal['sha256'] or journal['sha256'] != receipt['journal_sha256']
            or len(data) != journal['bytes'] or journal['valid_prefix_bytes'] != len(data)
            or journal['valid_prefix_sha256'] != journal['sha256'] or journal['uncommitted_suffix_bytes'] != 0):
        raise ValueError('Raw journal changed or has uncommitted suffix')
    events = [json.loads(line) for line in data.splitlines()]
    if not events or events[0]['payload']['manifest_sha256'] != sha(target / 'manifest.json'):
        raise ValueError('Raw manifest is not bound to the unchanged journal')
    for reference in [*manifest['inputs'].values(), manifest['execution_profile'], manifest['source_inventory'],
                      manifest['launch_intent'], manifest['materialization_receipt']]:
        if reference is None:
            continue
        referenced = (target / reference['path']).resolve()
        if not referenced.is_relative_to(target.resolve()) or sha(referenced) != reference['sha256']:
            raise ValueError('Bound native input/control artifact changed')
    if result['execution_status'] != 'completed' or not result['solver_result']['solved'] or result['quality']['status'] != 'correct':
        raise ValueError('Raw native completion/quality is invalid')
    if original.actual_sequence(events) != receipt['actual_sequence'] or original.mathematical(result['solver_result']) != receipt['mathematical_result']:
        raise ValueError('Raw mathematical/actual sequence differs from receipt')
    condition = next(c for c in plan['conditions'] if c['condition_id'] == job['condition_id'])
    expected_config = original.config(condition, job['variant'])
    if any(manifest['effective_' + field] != expected_config[field] for field in ('algorithm', 'execution', 'recording', 'budget')):
        raise ValueError('Raw native configuration differs')
    problem = read(directory / 'inputs' / (condition['case_id'] + '-problem.json'))
    if original.quality(plan['cases'][condition['case_id']], problem, result['solver_result']) != receipt['quality']:
        raise ValueError('Raw answers/winner differ from independent rational signs')
    answers = result['solver_result']['answered_queries']
    if len(answers) != receipt['answered_queries'] or result['query_counts']['answered_new'] != len(answers):
        raise ValueError('Raw actual query count differs')



def write_job_binding(root, directory, plan, receipt):
    """Attest immutable raw bytes immediately after the original strict reader."""
    raw_binding(root, directory, plan, receipt)
    key = receipt['job']['job_id']
    target = directory / 'cases' / key
    result = read(target / 'result.json')
    files = {'receipt': directory / 'receipts' / (key + '.json'),
             'manifest': target / 'manifest.json', 'result': target / 'result.json',
             'journal': target / result['journal']['path']}
    binding = {'job': receipt['job'], 'files': {name: {'path': path.relative_to(root).as_posix(), 'sha256': sha(path)}
               for name, path in files.items()}}
    original.write_new(directory / 'bindings' / (key + '.json'), binding)


def check_job_binding(root, directory, receipt):
    key = receipt['job']['job_id']
    binding = read(directory / 'bindings' / (key + '.json'))
    if binding['job'] != receipt['job'] or set(binding['files']) != {'receipt', 'manifest', 'result', 'journal'}:
        raise ValueError('Per-job byte binding differs')
    for reference in binding['files'].values():
        path = (root / reference['path']).resolve()
        if not path.is_relative_to(directory.resolve()) or sha(path) != reference['sha256']:
            raise ValueError('Previously verified raw artifact/receipt bytes changed')


def audit(root, directory, plan, *, complete=True):
    frozen(root, directory, plan)
    expected = {j['job_id']: j for j in plan['jobs']}
    receipts = {}
    for path in (directory / 'receipts').glob('*.json'):
        receipt = read(path)
        job = receipt['job']
        key = job['job_id']
        if key in receipts or expected.get(key) != job or path.stem != key:
            raise ValueError('Duplicate/unplanned receipt or job identity')
        if not valid_receipt(receipt):
            raise ValueError('Unverified/error/unsolved/incorrect result prevents qualification')
        for name in ('cli_wall_seconds', 'api_seconds', 'case_seconds'):
            if type(receipt.get(name)) not in (int, float) or not math.isfinite(receipt[name]) or receipt[name] <= 0:
                raise ValueError('Nonfinite/nonpositive timing')
        check_job_binding(root, directory, receipt)
        raw_binding(root, directory, plan, receipt)
        receipts[key] = receipt
    binding_ids = {p.stem for p in (directory / 'bindings').glob('*.json')}
    case_ids = {p.name for p in (directory / 'cases').iterdir() if p.is_dir()} if (directory / 'cases').is_dir() else set()
    if complete and (binding_ids != set(expected) or case_ids != set(expected)):
        raise ValueError('All720 matching binding records and case directories required')
    if complete and set(receipts) != set(expected):
        raise ValueError('All720 unique prospective calls required')
    pairs, conditions = [], []
    for condition in plan['conditions']:
        cid = condition['condition_id']
        ratios = []
        for block in range(1, N + 1):
            old, new = (receipts.get(f'{cid}-b{block}-{v}') for v in ('old', 'new'))
            if old is None or new is None:
                continue
            if old['mathematical_result'] != new['mathematical_result'] or old['actual_sequence'] != new['actual_sequence']:
                raise ValueError('Strict paired mathematical or journal mismatch')
            ratio = new['cli_wall_seconds'] / old['cli_wall_seconds']
            if not math.isfinite(ratio) or ratio <= 0:
                raise ValueError('Invalid paired ratio')
            ratios.append(ratio)
            pairs.append({'condition_id': cid, 'block': block, 'cli_ratio': ratio,
                'old_cli_seconds': old['cli_wall_seconds'], 'new_cli_seconds': new['cli_wall_seconds'],
                'api_ratio': new['api_seconds'] / old['api_seconds'],
                'answered_queries': old['answered_queries'], 'strict_math_and_sequence_equal': True})
        conditions.append({'condition': condition, **(classify(ratios) if len(ratios) == N else {'n': len(ratios), 'passed': False, 'classification': 'incomplete', 'ratios': ratios})})
    return {'purpose': plan['purpose'], 'plan_sha256': sha(directory / 'plan.json'), 'native_calls': len(receipts),
        'timing_pairs': len(pairs), 'all_calls_complete': len(receipts) == 720, 'all_semantic_checks_passed': True,
        'all_statistical_conditions_passed': len(pairs) == 360 and all(c['passed'] for c in conditions),
        'conditions': conditions, 'pairs': pairs, 'original_classifications_unchanged': True,
        'iid_assumption_required': True, 'unconditional_95_percent_guarantee': False,
        'process_end_acceptance': 'pending independent exact controller/group proof',
        'binding_inventory': {p.relative_to(root).as_posix(): sha(p) for p in sorted((directory / 'bindings').glob('*.json'))}}



def prove_process_end(directory):
    """One independent /proc snapshot; no signals and no unknown-as-dead."""
    if not Path('/proc/sys/kernel/random/boot_id').is_file():
        raise ValueError('Exact Linux process proof is required')
    boot = Path('/proc/sys/kernel/random/boot_id').read_text().strip()
    identities = {}
    for path in (directory / 'cases').rglob('manifest.json'):
        identity = read(path)['process']
        identities[identity['pid'], identity['start_ticks']] = identity
    driver = read(directory / 'driver-process.json')
    identities[driver['pid'], driver['start_ticks']] = driver
    rows = []
    for path in Path('/proc').iterdir():
        if not path.name.isdigit():
            continue
        try:
            values = (path / 'stat').read_text().rsplit(')', 1)[1].split()
            rows.append({'pid': int(path.name), 'start_ticks': int(values[19]), 'pgid': int(values[2]), 'state': values[0]})
        except (FileNotFoundError, ProcessLookupError):
            continue
    for identity in identities.values():
        if identity['boot_id'] != boot or type(identity['start_ticks']) is not int:
            raise ValueError('Process ownership is not bound to this Linux boot')
        if any(row['state'] != 'Z' and ((row['pid'] == identity['pid'] and row['start_ticks'] == identity['start_ticks'])
                or row['pgid'] == identity['pgid']) for row in rows):
            raise ValueError('A recorded controller/case group remains live')
    if len(identities) != 721:
        raise ValueError('All720 unique case identities and driver identity required')
    return {'all_groups_dead': True, 'actual_groups_checked': len(identities), 'checked_at_utc': datetime.now(timezone.utc).isoformat(),
            'identities': list(identities.values()), 'method': 'Exact boot/pid/startticks plus complete PGID, non-zombies; no signals'}


def no_other_solvers():
    if not Path('/proc').is_dir():
        raise ValueError('Execution requires Linux process identity proof')
    found = []
    for p in Path('/proc').iterdir():
        if not p.name.isdigit() or int(p.name) == os.getpid():
            continue
        try:
            fields = (p / 'stat').read_text().rsplit(')', 1)[1].split()
            cmd = (p / 'cmdline').read_bytes().replace(b'\0', b' ').decode(errors='replace')
            if fields[0] != 'Z' and ('.venv-countdown' in cmd and 'python' in cmd or 'multiprocessing.forkserver' in cmd or 'otqa.runtime.case' in cmd):
                found.append({'pid': int(p.name), 'start_ticks': int(fields[19]), 'pgid': int(fields[2]), 'command': cmd})
        except (FileNotFoundError, ProcessLookupError):
            continue
        except PermissionError as exc:
            raise ValueError('A live/unknown process cannot be inspected; no solver start') from exc
    if found:
        raise ValueError('Another possible solver/driver is live: ' + repr(found))


def run(root, directory):
    import fcntl
    plan = read(directory / 'plan.json')
    frozen(root, directory, plan)
    if (directory / 'driver-process.json').exists() or (directory / 'report.json').exists() or any((directory / 'receipts').glob('*.json')):
        raise FileExistsError('No implicit followup restart or reuse')
    with (directory / 'driver.lock').open('a+') as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        no_other_solvers()
        for variant in ('old', 'new'):
            actual = original.probe(root, Path(plan['interpreters'][variant]), root / plan['profiles'][variant]['path'])
            if actual != plan['source_probes'][variant]:
                raise ValueError('Installed admission changed after freeze')
        identity = {**original.process_identity(), 'pgid': os.getpgid(0), 'sid': os.getsid(0)}
        original.write_new(directory / 'driver-process.json', identity)
        error = None
        try:
            for index, job in enumerate(plan['jobs']):
                frozen(root, directory, plan)
                original.update_status(directory, {'phase': 'running_fixed720', 'current_job': job, 'completed_calls': index, 'process': identity})
                receipt = original.run_job(root, directory, plan, job)
                if not valid_receipt(receipt):
                    raise ValueError('Native call failed; preserved with no retry')
                write_job_binding(root, directory, plan, receipt)
                if index % 2:
                    before = read(directory / 'receipts' / (plan['jobs'][index - 1]['job_id'] + '.json'))
                    if before['mathematical_result'] != receipt['mathematical_result'] or before['actual_sequence'] != receipt['actual_sequence']:
                        raise ValueError('Paired math/journal mismatch; no further calls')
            report = audit(root, directory, plan)
        except Exception as exc:
            error = {'type': type(exc).__name__, 'message': str(exc)}
            report = {'purpose': plan['purpose'], 'plan_sha256': sha(directory / 'plan.json'), 'all_calls_complete': False,
                      'all_statistical_conditions_passed': False, 'error': error}
        report['completed_at_utc'] = datetime.now(timezone.utc).isoformat()
        original.write_new(directory / 'report.json', report)
        original.update_status(directory, {'phase': 'completed_pending_end_proof' if error is None else 'failed',
            'process': identity, 'completed_calls': len(list((directory / 'receipts').glob('*.json'))), 'error': error,
            'report_sha256': sha(directory / 'report.json')})
        return 0 if error is None and report['all_statistical_conditions_passed'] else 1


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('command', choices=['prepare', 'run', 'audit'])
    p.add_argument('--project-root', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--reference-plan', type=Path)
    args = p.parse_args(argv)
    root, directory = args.project_root.resolve(), args.output.resolve()
    original.project_output(root, directory)
    if args.command == 'prepare':
        if args.reference_plan is None:
            p.error('prepare requires frozen release11 --reference-plan')
        plan = prepare(root, directory, args.reference_plan.resolve())
        print(json.dumps({'command': 'prepare', 'native_calls': len(plan['jobs']), 'plan_sha256': sha(directory / 'plan.json')}))
        return 0
    if args.command == 'run':
        return run(root, directory)
    report = audit(root, directory, read(directory / 'plan.json'))
    retained_report = read(directory / 'report.json')
    if retained_report['binding_inventory'] != report['binding_inventory']:
        raise ValueError('Published per-job binding inventory changed')
    end = prove_process_end(directory)
    report['process_end_acceptance'] = end
    report['accepted'] = report['all_statistical_conditions_passed'] and end['all_groups_dead']
    original.write_new(directory / 'independent-replay-audit.json', report)
    print(json.dumps({'native_calls': report['native_calls'], 'pairs': report['timing_pairs'], 'statistical_pass': report['all_statistical_conditions_passed']}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
