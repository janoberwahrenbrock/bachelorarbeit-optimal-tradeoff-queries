"""Private scoped H3/N1 adaptation of frozen 618 standalone reporting.

No otqa/NumPy/geometry imports, solver execution, audits, resumption or completion
claims. API analyze(project_root, series_path) returns a portable report document.
The CLI writes only a fresh private provisional-reports directory for review.
"""
from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
from datetime import datetime, timezone
import csv
import hashlib
import io
import json
import math
from pathlib import Path, PurePosixPath
import statistics

from h3_study_contract import require_series

SOURCE = '720726607ae451b319e59e01453b6ba69b9950ef42420e700ed6b4eaa5b34d0e'
COMMIT = '62d1d01339f91802e2916b63660a4e640d99c9cc'
PROVISIONAL = Path('/Users/janoberwahrenbrock/Code/bachelorarbeit-optimal-tradeoff-queries/runs/seven-h3-grid5-followups-20261018T011350Z/monitoring/provisional-reports')


def require(value, message):
    if not value:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def encoded(value):
    return (json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + '\n').encode()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def number(value):
    require(value is None or (type(value) in (int, float) and math.isfinite(value) and value >= 0),
            'Invalid nonnegative saved cost/count')
    return value


class Reader:
    def __init__(self, root):
        self.root = Path(root).absolute()
        require(self.root.resolve(strict=True) == self.root, 'Symlink or missing project root')
        self.refs = {}

    def path(self, relative):
        portable = PurePosixPath(relative)
        require(not portable.is_absolute() and '..' not in portable.parts
                and portable.parts and portable.as_posix() == relative, 'Unsafe artifact path')
        path = self.root / portable
        for part in (path, *path.parents):
            require(not part.is_symlink(), 'Symlink artifact refused')
            if part == self.root:
                break
        return path

    def bytes(self, relative, expected=None):
        path = self.path(relative)
        data = path.read_bytes()
        sha = digest(data)
        require(expected is None or sha == expected, 'Hash differs: ' + relative)
        self.refs[relative] = {'path': relative, 'sha256': sha, 'bytes': len(data)}
        return data

    def document(self, relative, expected=None):
        return json.loads(self.bytes(relative, expected))

    def resolve(self, reference, prefix=''):
        relative = (PurePosixPath(prefix) / reference['path']).as_posix()
        return self.document(relative, reference['sha256'])

    def reference(self, relative):
        if relative not in self.refs:
            self.bytes(relative)
        return deepcopy(self.refs[relative])


def quantile(values, probability):
    if not values:
        return None
    ordered = sorted(values)
    position = (len(ordered) - 1) * probability
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (position - lower)


def distribution(values):
    values = [number(v) for v in values if v is not None]
    return {'n': len(values), 'total': math.fsum(values) if values else None,
            'mean': statistics.mean(values) if values else None,
            'median_across_cases_or_attempts': statistics.median(values) if values else None,
            'minimum': min(values) if values else None, 'p90': quantile(values, .9),
            'maximum': max(values) if values else None}


def attempt_row(reader, prefix, plan, job, saved):
    result = reader.resolve(saved['result'], prefix)
    require(result['run_id'] == saved['run_id'] and result['attempt_id'] == saved['attempt_id']
            and result['problem_id'] == job['problem_id']
            and result['configuration_id'] == job['configuration_id']
            and result['execution_status'] == saved['execution_status'], 'Attempt/result identities differ')
    directory = (PurePosixPath(prefix) / saved['directory']).as_posix()
    manifest_path = directory + '/manifest.json'
    manifest = reader.document(manifest_path) if reader.path(manifest_path).exists() else None
    if manifest:
        require(manifest['source'] == plan['source'] and manifest['run_id'] == saved['run_id']
                and manifest['attempt_id'] == saved['attempt_id']
                and manifest['series_id'] == plan['series_id']
                and manifest['numerical_profile']['profile_id'] == 'otqa-exact-v3', 'Manifest/source differs')
        for kind in ('problem', 'oracle', 'configuration'):
            require(manifest['inputs'][kind] == job[kind], 'Manifest input differs')
    initial = None
    final_observed = None
    event_counts = Counter()
    journal = result.get('journal')
    journal_ref = None
    if journal is not None:
        relative = (PurePosixPath(prefix) / journal['path']).as_posix()
        data = reader.bytes(relative, journal['sha256'])
        valid = data[:journal['valid_prefix_bytes']]
        require(len(data) == journal['bytes'] and len(valid) == journal['valid_prefix_bytes']
                and digest(valid) == journal['valid_prefix_sha256'], 'Journal prefix differs')
        for line in valid.splitlines():
            event = json.loads(line)
            require(event['run_id'] == saved['run_id'] and event['attempt_id'] == saved['attempt_id'],
                    'Journal identity differs')
            event_counts[event['event_type']] += 1
            if event['event_type'] == 'state_analyzed':
                final_observed = event['payload']
                if initial is None and event['payload']['state_index'] == 0:
                    initial = event['payload']
        journal_ref = reader.reference(relative)
    solver = result.get('solver_result')
    require(result['execution_status'] != 'completed' or solver is not None,
            'Completed result lacks its solver payload')
    require(solver is None or type(solver['solved']) is bool, 'Invalid saved solved flag')
    timings = result['timings']
    api = number(timings.get('api_call_wall_seconds'))
    partial = number(timings.get('partial_api_elapsed_seconds'))
    if not timings.get('complete_api_measurement'):
        require(api is None, 'Incomplete API measurement must not be presented as a full API time')
    counts = result.get('query_counts')
    queries = None if counts is None else counts['answered_new']
    if queries is not None:
        require(type(queries) is int and queries >= 0, 'Invalid answered-query count')
    quality = result['quality']
    final_state = solver['final_state'] if solver else final_observed
    return {'case_id': job['case_id'], 'job_id': job['job_id'], 'configuration_id': job['configuration_id'],
            'attempt_id': saved['attempt_id'], 'run_id': saved['run_id'], 'status': result['execution_status'],
            'quality': quality['status'], 'solved': None if solver is None else solver['solved'],
            'exactly_solved': None if solver is None else solver['exactly_solved'],
            'termination_reason': None if solver is None else solver['termination_reason'],
            'queries': queries, 'query_counts': counts, 'api_seconds': api, 'partial_api_seconds': partial,
            'api_measurement_complete': timings.get('complete_api_measurement', False),
            'case_seconds': number(timings.get('case_elapsed_seconds')),
            'controller_seconds': number(saved.get('controller_elapsed_seconds')),
            'initial_candidate_ids': None if initial is None else initial['candidate_ids'],
            'initial_candidate_count': None if initial is None else len(initial['candidate_ids']),
            'initial_candidate_volume_shares_recorded': None if initial is None else initial['candidate_volume_shares'],
            'final_candidate_ids': None if final_state is None else final_state['candidate_ids'],
            'final_candidate_volume_shares_recorded': None if final_state is None else final_state['candidate_volume_shares'],
            'selected_candidate_id': None if solver is None else solver['selected_candidate_id'],
            'true_winner_ids_recorded': quality.get('true_winner_ids'), 'quality_findings': quality.get('findings'),
            'error': result.get('error'), 'interruption': result.get('interruption'),
            'telemetry_errors': result.get('telemetry_errors'), 'timings': timings,
            'journal_event_counts': dict(sorted(event_counts.items())),
            'result': reader.reference((PurePosixPath(prefix) / saved['result']['path']).as_posix()),
            'manifest': None if manifest is None else reader.reference(manifest_path), 'journal': journal_ref,
            '_manifest': manifest}


def native_exports(reader, prefix, plan, state):
    receipts = {}
    for kind in ('json', 'csv'):
        rel = prefix + '/exports/fleet-final.' + kind + '.receipt.json'
        receipt = reader.document(rel)
        require(receipt['scope'] == 'complete' and receipt['format'] == kind
                and receipt['plan']['sha256'] == reader.reference(prefix + '/plan.json')['sha256'],
                'Export receipt differs')
        reader.bytes((PurePosixPath(prefix) / receipt['output']['path']).as_posix(), receipt['output']['sha256'])
        receipts[kind] = receipt
    require(receipts['json']['audit'] == receipts['csv']['audit']
            and receipts['json']['state'] == receipts['csv']['state'], 'JSON/CSV audit snapshots differ')
    audit = reader.resolve(receipts['json']['audit'], prefix)
    require(audit['status'] == 'passed' and audit['series_id'] == plan['series_id']
            and audit['auditor'] == plan['source'] and audit['state'] == receipts['json']['state']
            and audit['plan'] == receipts['json']['plan'], 'Native audit/source differs')
    require(reader.resolve(audit['state'], prefix) == state, 'Audit and current terminal state differ')
    summary = reader.resolve(receipts['json']['output'], prefix)
    require(summary['scope'] == 'complete' and summary['basis'] == 'verified_raw_attempts'
            and summary['audit'] == receipts['json']['audit'], 'Summary audit/scope differs')
    csvdata = reader.bytes(prefix + '/exports/fleet-final.csv').decode()
    csvrows = list(csv.DictReader(io.StringIO(csvdata)))
    require(len(csvrows) == len(summary['rows']) == len(plan['jobs']), 'Native export coverage differs')
    by_job = {row['job_id']: row for row in summary['rows']}
    require(len(by_job) == len(summary['rows']), 'Duplicate native export rows')
    for row in csvrows:
        native = by_job[row['job_id']]
        require(row['status'] == native['status'] and row['quality_status'] == native['quality_status']
                and (None if row['query_counts'] == '' else json.loads(row['query_counts'])) == native['query_counts']
                and json.loads(row['attempt_results']) == native['attempt_results'], 'CSV/JSON values differ')
        require((None if row['api_call_wall_seconds'] == '' else float(row['api_call_wall_seconds']))
                == native['api_call_wall_seconds'], 'CSV/JSON API time differs')
    return summary, receipts


def analyze(project_root, series_path):
    reader = Reader(project_root)
    prefix = PurePosixPath(series_path).as_posix()
    _, contract = require_series(series_path)
    plan = reader.document(prefix + '/plan.json')
    state = reader.document(prefix + '/state.json')
    sid = plan['suite_id']
    require(PurePosixPath(prefix).name == sid and state['series_id'] == plan['series_id']
            and state['plan_sha256'] == reader.reference(prefix + '/plan.json')['sha256'], 'Series binding differs')
    require(plan['source']['source_sha256'] == SOURCE and plan['source']['git_commit'] == COMMIT
            and plan['source']['dirty'] is False, 'This reporter supports only the pinned v3 study source')
    require(state['status'] in ('completed', 'completed_with_failures') and state['controller'] is None
            and state['active_job_id'] is None and len(plan['jobs']) == 1
            and len(state['jobs']) == len(plan['jobs'])
            and all(j['status'] in ('completed', 'failed') and j['attempts'] for j in state['jobs']),
            'Study is not wholly terminal; no provisional partial report is permitted')
    for relative, expected in plan['frozen_files'].items():
        reader.bytes((PurePosixPath(prefix) / relative).as_posix(), expected)
    summary, receipts = native_exports(reader, prefix, plan, state)
    exported = {row['job_id']: row for row in summary['rows']}
    dataset = reader.resolve(plan['dataset'], prefix)
    configuration_refs = {canonical(job['configuration']) for job in plan['jobs']}
    require(len(configuration_refs) == 1, 'Standalone study must contain one configuration')
    configuration = reader.resolve(plan['jobs'][0]['configuration'], prefix)
    algorithm = configuration['algorithm']
    require(configuration == contract['configuration'] and plan['jobs'][0]['case_id'] == contract['case_id'], 'Wrong H3 frozen subject/configuration')
    mode = ('adaptive' if algorithm['query_strategy'] == 'reduction_per_query'
            else algorithm['horizon_execution'])
    cases = {case['case_id']: case for case in dataset['cases']}
    require(len(cases) == len(plan['jobs']) and set(cases) == {job['case_id'] for job in plan['jobs']}, 'Dataset coverage differs')
    require(all(job['repetition_index'] == 0 for job in plan['jobs']), 'Expected one execution per cell')
    rows, attempts, environments, numerics = [], [], {}, {}
    for job, saved in zip(plan['jobs'], state['jobs']):
        require(job['job_id'] == saved['job_id'] and job['case_id'] == job['problem_id'], 'Job order/case differs')
        for kind in ('problem', 'oracle'):
            require(job[kind] == cases[job['case_id']][kind], 'Dataset/job input differs')
        problem = reader.resolve(job['problem'], prefix)
        row_attempts = []
        for attempt in saved['attempts']:
            row = attempt_row(reader, prefix, plan, job, attempt)
            manifest = row.pop('_manifest')
            if manifest:
                require(manifest['effective_algorithm'] == algorithm, 'Mixed algorithm manifests')
                environments[canonical(manifest['environment']).decode()] = manifest['environment']
                numerics[canonical(manifest['numerical_profile']).decode()] = manifest['numerical_profile']
            row_attempts.append(row)
            attempts.append(row)
        final = deepcopy(row_attempts[-1])
        final.update({'mode': mode, 'grid': algorithm['grid_size'], 'objectives': len(problem['objective_ids']),
                      'alternatives': len(problem['alternatives']), 'attempt_count': len(row_attempts),
                      'all_attempt_controller_seconds': (math.fsum(r['controller_seconds'] for r in row_attempts)
                                                         if all(r['controller_seconds'] is not None for r in row_attempts) else None),
                      'known_all_attempt_controller_seconds_sum': (math.fsum(r['controller_seconds'] for r in row_attempts
                                                                          if r['controller_seconds'] is not None)
                                                                   if any(r['controller_seconds'] is not None for r in row_attempts) else None),
                      'all_attempt_controller_missing': sum(r['controller_seconds'] is None for r in row_attempts)})
        require(final['status'] == saved['status'], 'Primary/last attempt status differs')
        final['classification'] = ('failed' if final['status'] == 'failed' else 'incorrect'
                                   if final['quality'] == 'incorrect' else 'regular_unsolved'
                                   if not final['solved'] else 'correct' if final['quality'] == 'correct'
                                   else 'solved_quality_unverified')
        native = exported[job['job_id']]
        require(native['case_id'] == final['case_id'] and native['configuration_id'] == final['configuration_id']
                and native['status'] == final['status'] and native['quality_status'] == final['quality']
                and native['query_counts'] == final['query_counts'] and native['api_call_wall_seconds'] == final['api_seconds']
                and native['attempt_results'] == [a['result'] for a in saved['attempts']], 'Native export and saved primary values differ')
        final['initial_candidate_ids'] = row_attempts[0]['initial_candidate_ids']
        final['initial_candidate_count'] = row_attempts[0]['initial_candidate_count']
        final['initial_candidate_volume_shares_recorded'] = row_attempts[0]['initial_candidate_volume_shares_recorded']
        rows.append(final)
    rows.sort(key=lambda row: row['case_id'])
    require(len({row['case_id'] for row in rows}) == len(rows), 'Duplicate primary cases')
    require(len(numerics) <= 1 and all(r['objectives'] in (3, 5, 7) and r['alternatives'] == 5 for r in rows),
            'Mixed method or unsupported dimensions')
    cohort = [{'case_id': cid, 'problem_sha256': cases[cid]['problem']['sha256'],
               'oracle_sha256': cases[cid]['oracle']['sha256']} for cid in sorted(cases)]
    correct = [r for r in rows if r['classification'] == 'correct']
    completed = [r for r in rows if r['status'] == 'completed']
    finite = [r['api_seconds'] for r in rows if r['api_seconds'] is not None]
    q1, q3 = quantile(finite, .25), quantile(finite, .75)
    fence = None if q1 is None else q3 + 1.5 * (q3 - q1)
    stats = {'primary_status_counts': dict(Counter(r['status'] for r in rows)),
             'classification_counts': dict(Counter(r['classification'] for r in rows)),
             'quality_counts_recorded': dict(Counter(r['quality'] for r in rows)),
             'termination_reason_counts': dict(Counter(str(r['termination_reason']) for r in rows)),
             'correct': len(correct), 'correct_denominator': len(rows), 'correct_fraction': len(correct) / len(rows),
             'initial_candidate_count_distribution': dict(sorted(Counter(str(r['initial_candidate_count']) for r in rows).items())),
             'zero_query_correct': sum(r['queries'] == 0 for r in correct),
             'one_query_correct': sum(r['queries'] == 1 for r in correct),
             'queries_all_completed': distribution(r['queries'] for r in completed),
             'queries_correct': distribution(r['queries'] for r in correct),
             'api_seconds_all_primary_measured': distribution(r['api_seconds'] for r in rows),
             'api_seconds_correct': distribution(r['api_seconds'] for r in correct),
             'all_attempts': len(attempts),
             'all_attempt_queries': distribution(r['queries'] for r in attempts),
             'missing_all_attempt_query_counts': sum(r['queries'] is None for r in attempts),
             'all_attempt_costs': {key: distribution(r[key] for r in attempts)
                                   for key in ('api_seconds', 'partial_api_seconds', 'case_seconds', 'controller_seconds')},
             'all_attempt_status_counts': dict(Counter(r['status'] for r in attempts)),
             'missing_all_attempt_costs': {key: sum(r[key] is None for r in attempts)
                                          for key in ('api_seconds', 'case_seconds', 'controller_seconds')},
             'outlier_rule': {'metric': 'one recorded API duration per primary case', 'rule': 'greater than Q3 + 1.5 IQR',
                              'q1': q1, 'q3': q3, 'upper_fence': fence, 'action': 'descriptive only; no exclusion'},
             'api_outlier_case_ids': [r['case_id'] for r in rows if r['api_seconds'] is not None and r['api_seconds'] > fence],
             'largest_api_cases': [{k: r[k] for k in ('case_id', 'api_seconds', 'queries', 'status', 'classification')}
                                   for r in sorted((r for r in rows if r['api_seconds'] is not None),
                                                   key=lambda r: -r['api_seconds'])[:10]]}
    # Recheck all retained source references after analysis, including mutable
    # terminal state and immutable journals, before returning the snapshot.
    for reference in list(reader.refs.values()):
        reader.bytes(reference['path'], reference['sha256'])
    return {'schema_version': 1, 'report_status': 'provisional_pending_independent_raw_and_final_hash_review',
            'generated_at_utc': datetime.now(timezone.utc).isoformat(), 'study_id': sid, 'series_id': plan['series_id'],
            'independent_problems': len(rows), 'primary_cells': len(rows), 'conditions': 1, 'repetitions': 1,
            'source': plan['source'], 'configuration': configuration, 'mode': mode,
            'input_cohort': {'case_count': len(cohort), 'cohort_sha256': digest(canonical(cohort)),
                             'contract': 'ordered case_id/problem_sha256/oracle_sha256 triples; canonical sorted-key compact JSON, no paths'},
            'numerical_profile': next(iter(numerics.values()), None), 'actual_environments_recorded': list(environments.values()),
            'rows': rows, 'all_attempts': attempts, 'summary': stats,
            'provenance': {'reference_root': 'project_root', 'series_path': prefix,
                           'plan': reader.reference(prefix + '/plan.json'), 'state': reader.reference(prefix + '/state.json'),
                           'audit': {**receipts['json']['audit'], 'path': prefix + '/' + receipts['json']['audit']['path']},
                           'json_csv_same_audit_ref': True, 'file_references': sorted(reader.refs.values(), key=lambda r: r['path'])},
            'limitations': ['Native status/quality and geometric candidate data are recorded observations; independent answer/winner/raw review is a separate artifact.',
                           'No process-liveness, final backup, publication or verified-completion state is established by this report.',
                           'One execution per problem/configuration, no repetition medians. Medians summarize different cases/attempts.',
                           'Single-condition study: no paired strategy/query-generator deltas or pooling across unrelated problems.',
                           'One full API time per primary row; case and controller costs are distinct scopes and are never added to API time.',
                           'All attempts and partial API costs are retained separately; unavailable costs remain null, not zero.',
                           'No LP, geometry volume, hypothetical-tree recertification or new solver execution is performed.']}


def csv_bytes(rows, fields):
    out = io.StringIO(newline='')
    writer = csv.DictWriter(out, fieldnames=fields, extrasaction='ignore')
    writer.writeheader()
    for row in rows:
        writer.writerow({key: json.dumps(row.get(key), sort_keys=True, separators=(',', ':'))
                         if isinstance(row.get(key), (dict, list)) else row.get(key) for key in fields})
    return out.getvalue().encode()


def markdown(result):
    stats = result['summary']
    counts = stats['classification_counts']
    n = result['independent_problems']
    alg = result['configuration']['algorithm']
    execution = result['configuration']['execution']
    lines = [f"# {result['study_id']}", '',
             'Vorläufige Auswertung; unabhängige Rohprüfung und finaler Hashvergleich stehen separat aus.', '',
             f"{n} unabhängige Probleme, eine Konfiguration, eine Ausführung je Zelle; {stats['all_attempts']} tatsächliche Versuche.",
             f"{result['mode']}, H{alg['depth']}, Grid {alg['grid_size']}, Queryquelle {alg['higher_depth_query_source']}, Stopp {alg['stopping']['rule']}, Mindestfortschritt {alg['min_expected_progress']}; {execution['workers']} Worker, ein nativer Thread.", '',
             f"Korrekt: {counts.get('correct', 0)}/{n}; regulär ungelöst: {counts.get('regular_unsolved', 0)}/{n}; fehlgeschlagen: {counts.get('failed', 0)}/{n}; falsche Auswahl: {counts.get('incorrect', 0)}/{n}; Auswahlqualität unbestätigt: {counts.get('solved_quality_unverified', 0)}/{n}.", '',
             '| Kennzahl | Fälle/Versuche mit Wert | Mittel | Summe |', '| --- | ---: | ---: | ---: |']
    for title, metric in [('Queries, alle regulär abgeschlossenen Fälle', stats['queries_all_completed']),
                          ('Queries, korrekte Lösungen', stats['queries_correct']),
                          ('Queries, sämtliche Versuche mit gespeichertem Zähler', stats['all_attempt_queries']),
                          ('API-Sekunden, Primärfälle mit vollständigem Messwert', stats['api_seconds_all_primary_measured']),
                          ('API-Sekunden, korrekte Lösungen', stats['api_seconds_correct']),
                          ('Controller-Sekunden, sämtliche Versuche', stats['all_attempt_costs']['controller_seconds']),
                          ('Partielle API-Sekunden, sämtliche Teilversuche', stats['all_attempt_costs']['partial_api_seconds'])]:
        def fmt(value):
            return '–' if value is None else f'{value:.6g}'
        lines.append(f"| {title} | {metric['n']} | {fmt(metric['mean'])} | {fmt(metric['total'])} |")
    lines += ['', 'Eine API-Zeit je Fall ist die Laufzeitkennzahl. Controller- und Fallprozesskosten haben andere Messgrenzen und werden separat ausgewiesen. Fehlende Werte werden nicht als Null interpretiert.', '',
              'Alle Fälle einschließlich Ausreißern bleiben enthalten. Der IQR-Hinweis ist rein beschreibend: ' + ', '.join(stats['api_outlier_case_ids'] or ['keine']), '',
              '| Problem | Anfangskandidaten | Queries | API s | Status/Qualität | Endgrund |',
              '| --- | ---: | ---: | ---: | --- | --- |']
    for row in result['rows']:
        api = '–' if row['api_seconds'] is None else f"{row['api_seconds']:.6g}"
        lines.append(f"| {row['case_id']} | {row['initial_candidate_count']} | {row['queries']} | {api} | {row['status']}/{row['classification']} | {row['termination_reason']} |")
    lines += ['', f"Gemessene Quelle: `{result['source']['source_sha256']}`, Buildcommit `{result['source']['git_commit']}`; numerisches Profil `otqa-exact-v3`.",
              f"Eingabekohorte: `{result['input_cohort']['cohort_sha256']}`.", '',
              'Die Quellen-, Eingabe-, Audit- und Resultatreferenzen stehen in results.json. Das Rohdatenpaket und die unabhängige Prüfung werden separat gebunden. Keine historischen Laufzeiten oder anderen Studienarchive werden für diese Auswertung benötigt.', '',
              'Es gibt weder Wiederholungsmediane noch gepaarte Strategievergleiche innerhalb dieser Einzelstudie. Gespeicherte Kandidatenvolumen werden nicht geometrisch neu zertifiziert.', '']
    return '\n'.join(lines).encode()


def write_report(result, output):
    output = Path(output).absolute()
    require(output.is_relative_to(PROVISIONAL) and not output.exists(), 'Fresh output must be under provisional-reports')
    for path in (output, *output.parents):
        require(not path.is_symlink(), 'Symlink output refused')
    fields = ['case_id', 'job_id', 'configuration_id', 'mode', 'grid', 'objectives', 'alternatives',
              'status', 'classification', 'quality', 'solved', 'exactly_solved', 'termination_reason',
              'initial_candidate_count', 'initial_candidate_ids', 'queries', 'api_seconds', 'api_measurement_complete',
              'partial_api_seconds', 'case_seconds', 'controller_seconds', 'attempt_count',
              'all_attempt_controller_seconds', 'known_all_attempt_controller_seconds_sum',
              'all_attempt_controller_missing', 'selected_candidate_id',
              'final_candidate_ids', 'true_winner_ids_recorded', 'result']
    afields = ['case_id', 'job_id', 'configuration_id', 'attempt_id', 'run_id', 'status', 'quality', 'solved',
               'termination_reason', 'queries', 'api_seconds', 'partial_api_seconds', 'api_measurement_complete',
               'case_seconds', 'controller_seconds', 'initial_candidate_count', 'final_candidate_ids', 'error', 'result']
    outputs = {'results.json': encoded(result), 'results.csv': csv_bytes(result['rows'], fields),
               'attempts.csv': csv_bytes(result['all_attempts'], afields), 'report.md': markdown(result)}
    output.mkdir(parents=True, exist_ok=False)
    for name, data in outputs.items():
        with (output / name).open('xb') as stream:
            stream.write(data)
    inventory = {'status': result['report_status'], 'study_id': result['study_id'],
                 'scientific_completion': False, 'final_backup_verified': False, 'publication_completion': False,
                 'files': [{'path': name, 'bytes': len(data), 'sha256': digest(data)} for name, data in sorted(outputs.items())]}
    with (output / 'report-files.json').open('xb') as stream:
        stream.write(encoded(inventory))
    return inventory


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project-root', type=Path, required=True)
    parser.add_argument('--series-path', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    report = analyze(args.project_root, args.series_path)
    files = write_report(report, args.output)
    print(json.dumps({'status': files['status'], 'study_id': report['study_id'], 'rows': len(report['rows']),
                      'attempts': len(report['all_attempts']), 'summary': report['summary'], 'output': str(args.output)}, sort_keys=True))
