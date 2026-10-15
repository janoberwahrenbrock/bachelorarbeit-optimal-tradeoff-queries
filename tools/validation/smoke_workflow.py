"""Run a fresh, small public-CLI workflow against an installed wheel.

All generated inputs, command receipts and native results stay in the explicitly
marked project. This is functional validation, not a performance comparison.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
from uuid import uuid4


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project-root', type=Path, required=True)
    parser.add_argument('--execution-profile', type=Path, required=True)
    parser.add_argument('--label', default='smoke-' + uuid4().hex[:12])
    parser.add_argument('--master-seed', type=int, default=20261015)
    args = parser.parse_args()
    project = args.project_root.resolve()
    profile = args.execution_profile.resolve()
    label = args.label
    if not label or any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_' for c in label):
        parser.error('label must contain only ASCII letters, digits, hyphens or underscores')
    from otqa.runtime.codec import encode
    from otqa.runtime.source import loaded_source
    source = loaded_source()[0]
    receipt_root = project / 'runs' / (label + '-validation')
    receipt_root.mkdir(parents=True, exist_ok=False)
    receipt_path = receipt_root / 'receipt.json'
    receipt = {'scope': 'fresh installed public CLI functional workflow; not a timing gate',
               'source': source, 'status': 'in_progress', 'commands': []}

    def persist():
        receipt_path.write_bytes(encode(receipt))

    def command(*arguments):
        invocation = [sys.executable, '-m', 'otqa', '--project-root', str(project), *map(str, arguments)]
        started = time.perf_counter()
        result = subprocess.run(invocation, cwd=project, capture_output=True, text=True, timeout=300)
        record = {'arguments': invocation, 'exit_code': result.returncode,
                  'wall_seconds': time.perf_counter() - started, 'stdout': result.stdout, 'stderr': result.stderr}
        receipt['commands'].append(record)
        persist()
        if result.returncode:
            raise RuntimeError(f'CLI exited {result.returncode}: {result.stdout} {result.stderr}')
        return json.loads(result.stdout)

    persist()
    try:
        dataset_dir = project / 'inputs' / 'datasets' / label
        command('dataset', 'generate', '--dataset-id', label, '--master-seed', args.master_seed,
                '--objectives', 2, 3, '--alternatives', 3, '--cases-per-shape', 2, '--output', dataset_dir)
        dataset = json.loads((dataset_dir / 'dataset.json').read_text())
        configurations = project / 'inputs' / 'configurations' / label
        configurations.mkdir(parents=True, exist_ok=False)
        paths, selection = [], []
        for name, strategy in [('fixed2-profile', 'fixed'), ('adaptive2', 'reduction_per_query')]:
            configuration = {'schema_version': 1, 'configuration_id': name,
                'algorithm': {'query_strategy': strategy, 'depth': 2, 'higher_depth_query_source': 'both',
                              'grid_size': 5, 'planning_evaluation': 'candidate_count',
                              'stopping': {'rule': 'single_candidate'}},
                'budget': {'max_queries': None},
                'execution': {'workers': 8, 'native_threads': 1, 'start_method': 'forkserver',
                              'cache_policy_id': 'bounded_v1', 'case_timeout_seconds': None},
                'recording': {'durability': 'per_answer', 'trace_level': 'standard',
                              'profile': name == 'fixed2-profile', 'telemetry_failure_policy': 'continue'}}
            path = configurations / (name + '.json')
            path.write_bytes(encode(configuration))
            paths.append(path)
            selection.append({'configuration_id': name, 'case_ids': [case['case_id'] for case in dataset['cases']]})
        selection_path = receipt_root / 'selection.json'
        selection_path.write_bytes(encode(selection))
        suite_path = project / 'inputs' / 'suites' / label / 'suite.json'
        command('suite', 'create', '--source-root', project, '--suite-id', label,
                '--dataset', dataset_dir / 'dataset.json', '--config', *paths,
                '--selection-file', selection_path, '--repetitions', 1, '--output', suite_path)
        series = project / 'runs' / label
        command('benchmark', 'plan', '--source-root', project, '--suite', suite_path,
                '--execution-profile', profile, '--output', series)
        command('benchmark', 'run', '--plan', series / 'plan.json')
        command('benchmark', 'status', '--series', series)
        audit = command('benchmark', 'audit', '--series', series)
        audit_ref = str(Path(audit['audit_path']).relative_to(series))
        for format_name in ('json', 'csv'):
            command('benchmark', 'export', '--series', series, '--audit-ref', audit_ref,
                    '--format', format_name, '--output', series / 'exports' / ('jobs.' + format_name))
        before = (series / 'state.json').read_bytes()
        command('benchmark', 'resume', '--series', series)
        after = json.loads((series / 'state.json').read_text())
        previous = json.loads(before)
        assert [j['attempts'] for j in previous['jobs']] == [j['attempts'] for j in after['jobs']]
        archive = command('benchmark', 'seal', '--series', series)
        from otqa.analysis.seal import verify_seal
        inventory = verify_seal(Path(archive['bundle_root']), inventory_ref=archive['inventory'])
        summary = json.loads((series / 'exports' / 'jobs.json').read_text())
        assert len(summary['rows']) == 8
        assert all(row['quality_status'] == 'correct' and row['solved'] for row in summary['rows'])
        profile_files = sorted(str(path.relative_to(series)) for path in series.rglob('*.pstats') if 'seals' not in path.parts)
        assert len(profile_files) == 4
        assert loaded_source()[0] == source
        receipt.update(status='passed', series=str(series), summary=summary, resumed_new_attempts=0,
                       profile_files=profile_files, seal=archive, sealed_payload_files=len(inventory['files']))
        persist()
        print(json.dumps({'status': 'passed', 'jobs': 8, 'correct': 8, 'receipt': str(receipt_path)}))
    except BaseException as exc:
        receipt.update(status='failed', error={'type': type(exc).__name__, 'message': str(exc)})
        persist()
        raise


if __name__ == '__main__':
    main()
