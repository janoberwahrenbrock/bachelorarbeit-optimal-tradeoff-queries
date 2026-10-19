"""Exact single-relocation admission and preserved technical-history contract.

No process actions or numerical computation. The original seven-subject inputs
remain authoritative; this adapter changes only the one authorized physical
series location, owner and destination-host provenance.
"""
from copy import deepcopy
import hashlib
import json
from pathlib import Path, PurePosixPath

RUN = 'runs/seven-h3-grid5-followups-20261018T011350Z'
SCOPE_SHA256 = '4dbca0964c03476cb38a40681d9c9798228eac39b3aeb4aa4f68a9d56c7235cf'
SOURCE = '720726607ae451b319e59e01453b6ba69b9950ef42420e700ed6b4eaa5b34d0e'
COMMIT = '62d1d01339f91802e2916b63660a4e640d99c9cc'
MAX_DEPTH = 3
OWNER = 'fda7a4f9c2894b99b5c81a2c2105580b'
STUDY_ID = 'd7-a5-n1-h3-grid5-grid-plus-ratio-receding-stop-single-candidate-minprog0p001-src72072-case000024'
SERIES_PATH = 'runs/seven-h3-grid5-followups-20261018T011350Z/native-relocations170/fda7a4f9c2894b99b5c81a2c2105580b/d7-a5-n1-h3-grid5-grid-plus-ratio-receding-stop-single-candidate-minprog0p001-src72072-case000024'
PLAN_SHA256 = 'd9cf82c67abe5a1aa46405567ac375f67c5f9f726720c71bfa007f48d831081d'
SERIES_ID = 'f0f66acc-7a05-4e13-acc8-374ed13ff2f4'
REQUEST = {'bytes': 2598,
 'path': 'runs/seven-h3-grid5-followups-20261018T011350Z/control/relocations170/fda7a4f9c2894b99b5c81a2c2105580b/launch-request.json',
 'sha256': '5bd230b0425d75ed48a9dfa15f44f209a484802ba46c32f71889614ba1151194'}
RELOCATION_SCOPE = {'bytes': 6428,
 'path': 'runs/seven-h3-grid5-followups-20261018T011350Z/control/relocations170/fda7a4f9c2894b99b5c81a2c2105580b/relocation-scope.json',
 'sha256': '39e5f3e64d8813ee0c633f5cc47ce658c923300b2cfa98c6a5304ed4d3fbf4f4'}
HISTORICAL_OBSERVATION = {'bytes': 12416,
 'path': 'runs/seven-h3-grid5-followups-20261018T011350Z/monitoring/host170-native-resume-observed-a20c61ca6ff146d0ad142512388e3b11.json',
 'sha256': 'f303534f487569708c91511d5e309dd0bd9d6c9e4b088b9fc65fe9df54f0fe74'}
SUBJECTS = {'d7-a5-n1-h3-grid5-grid-plus-ratio-receding-stop-single-candidate-minprog0p001-src72072-case000024': {'case_id': 'd7-m5-c000024',
                                                                                                       'configuration': {'bytes': 825,
                                                                                                                         'path': 'runs/seven-h3-grid5-followups-20261018T011350Z/inputs/d7-a5-n1-h3-grid5-grid-plus-ratio-receding-stop-single-candidate-minprog0p001-src72072-case000024/configuration.json',
                                                                                                                         'sha256': '69da087385986d29e27a84aa6af7b5f237a10cad1fc862e0ad8b38a8a252bbca'},
                                                                                                       'dataset': {'bytes': 819,
                                                                                                                   'path': 'runs/seven-h3-grid5-followups-20261018T011350Z/inputs/d7-a5-n1-h3-grid5-grid-plus-ratio-receding-stop-single-candidate-minprog0p001-src72072-case000024/dataset.json',
                                                                                                                   'sha256': 'c3a8103bdddd1a97433fe0b9789aff43df508f88905473c5217096e53f5c3c9d'},
                                                                                                       'host': '170',
                                                                                                       'mode': 'receding',
                                                                                                       'oracle': {'path': 'runs/seven-h3-grid5-followups-20261018T011350Z/inputs/d7-a5-n1-h3-grid5-grid-plus-ratio-receding-stop-single-candidate-minprog0p001-src72072-case000024/oracle.json',
                                                                                                                  'sha256': '621c9bad39515eece8d31a37cdc00770cc9ff163110c07557455d7140760da31'},
                                                                                                       'problem': {'path': 'runs/seven-h3-grid5-followups-20261018T011350Z/inputs/d7-a5-n1-h3-grid5-grid-plus-ratio-receding-stop-single-candidate-minprog0p001-src72072-case000024/problem.json',
                                                                                                                   'sha256': '96737c02286c3079e6877a02faa611edf7dcdeecfd24f45fb747b8c4281d7d63'},
                                                                                                       'suite': {'bytes': 1209,
                                                                                                                 'path': 'runs/seven-h3-grid5-followups-20261018T011350Z/inputs/d7-a5-n1-h3-grid5-grid-plus-ratio-receding-stop-single-candidate-minprog0p001-src72072-case000024/suite.json',
                                                                                                                 'sha256': 'c85a3fffe739534e9b0f57ea5be9698dcb984673758d6794a090a37815781cff'}}}

def study_contract(study_id):
    if study_id not in SUBJECTS:
        raise ValueError('Study is outside the exact authorized case024 relocation')
    row = deepcopy(SUBJECTS[study_id])
    mode = row['mode']
    row.update(study_id=study_id, host='179', original_host='170', dimension=7, count=1, grid=5, configuration={
        'schema_version': 2, 'configuration_id': study_id + '-config',
        'algorithm': {'query_strategy': 'reduction_per_query' if mode == 'adaptive' else 'fixed',
            'depth': 3, 'higher_depth_query_source': 'both', 'grid_size': 5,
            'planning_evaluation': 'candidate_count', 'stopping': {'rule': 'single_candidate'},
            'horizon_execution': 'countdown' if mode == 'countdown' else 'receding',
            'min_expected_progress': .001}, 'budget': {'max_queries': None},
        'execution': {'workers': 16, 'start_method': 'forkserver', 'native_threads': 1,
                      'case_timeout_seconds': None, 'cache_policy_id': 'bounded_v1'},
        'recording': {'durability': 'per_answer', 'trace_level': 'standard', 'profile': False,
                      'telemetry_failure_policy': 'continue'}})
    return row


def require(condition, message):
    if not condition:
        raise ValueError(message)


def require_series(series_path):
    relative = PurePosixPath(series_path)
    require(not relative.is_absolute() and relative.as_posix() == series_path
            and '..' not in relative.parts and series_path == SERIES_PATH,
            'Outside the exact case024 relocation namespace')
    return relative, study_contract(STUDY_ID)


def pinned_document(root, reference, read_bytes):
    relative = PurePosixPath(reference['path'])
    require(not relative.is_absolute() and relative.as_posix() == reference['path']
            and '..' not in relative.parts, 'Unsafe relocation evidence reference')
    path = Path(root) / relative
    for part in (path, *path.parents):
        require(not part.is_symlink(), 'Relocation evidence symlink refused')
        if part == Path(root):
            break
    data = read_bytes(path)
    require(hashlib.sha256(data).hexdigest() == reference['sha256']
            and ('bytes' not in reference or len(data) == reference['bytes']),
            'Relocation evidence hash/size differs: ' + reference['path'])
    return json.loads(data)


def check_projection(root, series_path, read_bytes):
    """Bind the one actual destination request; never rewrite an old request."""
    require_series(series_path)
    q = pinned_document(root, REQUEST, read_bytes)
    relocation = pinned_document(root, RELOCATION_SCOPE, read_bytes)
    original = pinned_document(root, {'path': RUN + '/scope.json', 'sha256': SCOPE_SHA256}, read_bytes)
    require(q['owner'] == OWNER and q['study_id'] == STUDY_ID and q['series_path'] == SERIES_PATH
            and q['plan_sha256'] == PLAN_SHA256 and q['series_id'] == SERIES_ID
            and q['execution_path'] == RUN and q['planned_jobs'] == 1,
            'Relocation owner/request/plan differs')
    require(q['ip'] == '192.168.188.179' and q['hostname'] == 'machine3'
            and q['boot_id'] == '1478e15e-1c97-4d0a-8397-79cf7122bf69'
            and q['machine_id'] == 'd1e1744eb9f64988a8d30d1235c30759',
            'Relocation destination identity differs')
    require(q['source'] == relocation['source'] == original['source']
            and q['source']['source_sha256'] == SOURCE and q['source']['pinned_commit'] == COMMIT,
            'Relocation measured source differs')
    require(q['relocation_scope'] == RELOCATION_SCOPE
            and relocation['status'] == 'authorized_same_logical_cell_relocation'
            and relocation['owner'] == OWNER and relocation['study_id'] == STUDY_ID
            and relocation['N'] == 1 and relocation['new_logical_quality_case'] is False
            and relocation['logical_primary_cells'] == original['primary_cells'] == 7
            and relocation['distinct_problem_oracle_pairs'] == 5
            and relocation['retain_original_attempts_and_unknown_costs'] is True
            and relocation['new_attempt_inputs'] == {'initial_answers': None, 'replay_answers': None, 'continuation': None},
            'Relocation scientific/technical scope differs')
    entry = next(e for e in original['entries'] if e['study_id'] == STUDY_ID)
    require(entry['N'] == 1 and entry['problem_id'] == 'd7-m5-c000024'
            and entry['proposed_host_suffix'] == '170'
            and relocation['destination_host_suffix'] == '179', 'Original logical subject differs')
    root_review = pinned_document(root, relocation['root_review'], read_bytes)
    peer = pinned_document(root, root_review['independent_review'], read_bytes)
    require(root_review['status'] == 'authorized_relocation_plan_and_single_launch'
            and root_review['reviewer'] in ('root', '/root')
            and root_review['tools'] == relocation['tools']
            and peer['status'] == 'gate_pass' and peer['findings'] == []
            and peer['reviewer'] in ('ht_study_design', '/root/ht_study_design')
            and peer['tools'] == relocation['tools'], 'Relocation independent authorization differs')
    plan = pinned_document(root, {'path': SERIES_PATH + '/plan.json', 'sha256': PLAN_SHA256}, read_bytes)
    require(plan['series_id'] == SERIES_ID and plan['suite_id'] == STUDY_ID
            and len(plan['jobs']) == 1 and not plan['source']['dirty']
            and plan['source']['source_sha256'] == SOURCE and plan['source']['git_commit'] == COMMIT,
            'Relocation native plan/source differs')
    job = plan['jobs'][0]
    require(job['case_id'] == job['problem_id'] == entry['problem_id']
            and job['repetition_index'] == 0, 'Relocation planned cell differs')
    for kind in ('configuration', 'problem', 'oracle'):
        require(job[kind]['sha256'] == entry[kind]['sha256'] == relocation['original_inputs'][kind]['sha256'],
                'Relocation mathematical input changed')
        value = pinned_document(root, {'path': SERIES_PATH + '/' + job[kind]['path'],
                                      'sha256': job[kind]['sha256']}, read_bytes)
        if kind == 'configuration':
            require(value == study_contract(STUDY_ID)['configuration'], 'Relocation algorithm changed')
    return {'request_document': q, 'scope_document': relocation, 'native_plan': plan}


def check_finish(finish):
    require(finish['launch_owner'] == OWNER and finish['study_id'] == STUDY_ID
            and finish['plan_sha256'] == PLAN_SHA256 and finish['series_id'] == SERIES_ID
            and finish['request'] == {k: REQUEST[k] for k in ('path', 'sha256')},
            'Wrong case024 relocation finish identity')


def technical_history(root, read_bytes):
    """Report saved observations separately; no current liveness or cost guess."""
    saved = pinned_document(root, HISTORICAL_OBSERVATION, read_bytes)
    require(saved['state']['plan_sha256'] == '6feba45646c760dec86d4ec2c9057b500ef5bd26ab52745632bddadc329ad35a'
            and saved['state']['series_id'] == 'faf9e579-465e-40b4-a51f-f3ae41e9b4ad',
            'Wrong original case024 observation')
    attempts = []
    for item in saved['attempts']:
        result, progress = item.get('result'), item['progress']
        attempts.append({'attempt_id': item['attempt_id'],
            'status_at_saved_observation': item['execution_status'],
            'confirmed_committed_answers_at_snapshot': progress['query_counts']['answered_new'],
            'partial_api_seconds_at_snapshot': progress.get('partial_api_elapsed_seconds'),
            'complete_api_seconds': None if result is None else result['timings']['api_call_wall_seconds'],
            'controller_seconds': None, 'progress_credit_to_relocated_attempt': 0,
            'result_available_at_snapshot': result is not None,
            'snapshot_afterwards_activity_and_final_costs': 'unknown; no later native result or costs inferred'})
    require([a['confirmed_committed_answers_at_snapshot'] for a in attempts] == [2, 0]
            and attempts[0]['partial_api_seconds_at_snapshot'] == 255.0806905630002,
            'Original confirmed prefix changed')
    return {'new_logical_quality_case': False, 'logical_primary_cells_in_original_scope': 7,
            'distinct_original_problem_oracle_pairs': 5,
            'physical_relocation_owner': OWNER, 'original_observation': deepcopy(HISTORICAL_OBSERVATION),
            'original_observation_is_historical_not_current_process_status': True,
            'original_attempts': attempts, 'original_complete_total_controller_seconds': None,
            'original_complete_total_api_seconds': None,
            'relocated_attempt_starts_from_original_inputs_with_zero_answers': True,
            'native_rows_and_all_attempts_describe_destination_series_only': True,
            'limitation': 'Technical attempts and known partial costs remain separate from the one logical quality cell; original full costs and post-snapshot answers are unavailable.'}

