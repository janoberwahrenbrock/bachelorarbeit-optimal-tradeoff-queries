from uuid import uuid4

import pytest

from otqa.application import GenerateDatasetRequest, generate_dataset
from otqa.experiments.suite import ordered_jobs
from otqa.runtime.codec import DocumentError, encode
from otqa.runtime.documents import load_document, resolve_ref
from otqa.runtime.project import load_project_context


def context_at(tmp_path):
    (tmp_path / "otqa-project.json").write_bytes(encode({"schema_version": 1, "project_kind": "otqa_project", "project_id": str(uuid4())}))
    return load_project_context(tmp_path)


def test_case_streams_are_independent_of_other_shape_order(tmp_path):
    context = context_at(tmp_path)
    first = generate_dataset(GenerateDatasetRequest(context, "forward", 87, (2, 3), (2,), 1, context.project_root / "inputs/datasets/forward"))
    second = generate_dataset(GenerateDatasetRequest(context, "reverse", 87, (3, 2), (2,), 1, context.project_root / "inputs/datasets/reverse"))
    left = {case["case_id"]: case for case in first.dataset["cases"]}
    right = {case["case_id"]: case for case in second.dataset["cases"]}
    for case_id in left:
        for kind in ("problem", "oracle"):
            assert resolve_ref(context.project_root, left[case_id][kind]).read_bytes() == resolve_ref(context.project_root, right[case_id][kind]).read_bytes()


@pytest.mark.parametrize("seed,objectives,cases", [(True, (2,), 1), (-1, (2,), 1), (1, (True,), 1), (1, (2, 2), 1), (1, (2,), 1.0)])
def test_generator_rejects_implicit_types_before_creating_inputs(tmp_path, seed, objectives, cases):
    context = context_at(tmp_path)
    target = context.project_root / "inputs/datasets/invalid"
    with pytest.raises(DocumentError):
        generate_dataset(GenerateDatasetRequest(context, "invalid", seed, objectives, (2,), cases, target))
    assert not target.exists()


def test_order_rotates_per_case_and_repetition(tmp_path):
    from otqa.runtime.codec import digest
    problem = {"schema_version": 1, "problem_id": "p", "alternative_ids": ["a"], "objective_ids": ["g"], "alternatives": [[1.0]]}
    raw = encode(problem)
    (tmp_path / "problem.json").write_bytes(raw)
    problem_ref = {"path": "problem.json", "sha256": digest(raw)}
    dataset = {"cases": [{"case_id": case, "problem": problem_ref, "oracle": {"path": "oracle.json", "sha256": "0" * 64}} for case in ("c0", "c1")]}
    suite = {"configurations": [{"configuration_id": key, "path": key + ".json", "sha256": "0" * 64} for key in ("a", "b")],
             "selection": [{"configuration_id": key, "case_ids": ["c0", "c1"]} for key in ("a", "b")], "repetitions": 2}
    jobs = ordered_jobs(suite, dataset, tmp_path)
    assert [(job["case_id"], job["repetition_index"], job["configuration_id"]) for job in jobs] == [
        ("c0", 0, "a"), ("c0", 0, "b"), ("c0", 1, "b"), ("c0", 1, "a"),
        ("c1", 0, "b"), ("c1", 0, "a"), ("c1", 1, "a"), ("c1", 1, "b")]


def test_regenerating_a_dataset_does_not_overwrite(tmp_path):
    context = context_at(tmp_path)
    request = GenerateDatasetRequest(context, "once", 5, (2,), (2,), 1, context.project_root / "inputs/datasets/once")
    first = generate_dataset(request)
    with pytest.raises(DocumentError):
        generate_dataset(request)
    assert load_document("dataset", first.dataset_path, reference_root=context.project_root) == first.dataset


def test_dataset_destination_race_cannot_replace_empty_directory(tmp_path, monkeypatch):
    import otqa.experiments.dataset as module
    context = context_at(tmp_path)
    target = context.project_root / 'inputs/datasets/race'
    original = module.create_directory
    def race(context, path, **kwargs):
        target.mkdir(parents=True)
        return original(context, path, **kwargs)
    monkeypatch.setattr(module, 'create_directory', race)
    with pytest.raises(DocumentError, match='already exists'):
        generate_dataset(GenerateDatasetRequest(context, 'race', 5, (2,), (2,), 1, target))
    assert target.is_dir() and list(target.iterdir()) == []


def test_dataset_payload_failure_never_publishes_commit_marker(tmp_path, monkeypatch):
    import otqa.experiments.dataset as module
    context = context_at(tmp_path)
    target = context.project_root / 'inputs/datasets/partial'
    original = module.publish_bytes
    calls = 0
    def fail(context, path, data, **kwargs):
        nonlocal calls
        calls += 1
        if calls == 2:
            raise OSError('injected payload failure')
        return original(context, path, data, **kwargs)
    monkeypatch.setattr(module, 'publish_bytes', fail)
    request = GenerateDatasetRequest(context, 'partial', 5, (2,), (2,), 1, target)
    with pytest.raises(OSError, match='injected'):
        generate_dataset(request)
    assert (target / 'problems/d2-m2-c000000.json').is_file()
    assert not (target / 'dataset.json').exists()
    with pytest.raises(FileNotFoundError):
        load_document('dataset', target / 'dataset.json', reference_root=context.project_root)
    with pytest.raises(DocumentError, match='already exists'):
        generate_dataset(request)


def _suite_request(context):
    from otqa.application_types import CreateSuiteRequest
    from otqa.runtime.storage import publish_json
    dataset = generate_dataset(GenerateDatasetRequest(context, 'suite-data', 3, (2,), (2,), 1, context.project_root / 'inputs/datasets/suite-data'))
    config_path = context.project_root / 'inputs/config.json'
    config = {'schema_version': 2, 'configuration_id': 'fixed',
              'algorithm': {'query_strategy': 'fixed', 'depth': 1, 'higher_depth_query_source': 'both', 'grid_size': 5,
                            'planning_evaluation': 'candidate_count', 'stopping': {'rule': 'single_candidate'},
                            'horizon_execution': 'receding', 'min_expected_progress': 0.001},
              'budget': {'max_queries': None},
              'execution': {'workers': 1, 'native_threads': 1, 'start_method': 'forkserver', 'cache_policy_id': 'bounded_v1', 'case_timeout_seconds': None},
              'recording': {'durability': 'per_answer', 'trace_level': 'standard', 'profile': False, 'telemetry_failure_policy': 'continue'}}
    publish_json(context, config_path, config, kind='config', namespace='inputs')
    return CreateSuiteRequest(context, context.project_root, 'suite-race', dataset.dataset_path, (config_path,),
                              ({'configuration_id': 'fixed', 'case_ids': [dataset.dataset['cases'][0]['case_id']]},), 1,
                              context.project_root / 'inputs/suites/suite-race/suite.json')


def test_suite_destination_race_cannot_replace_empty_directory(tmp_path, monkeypatch):
    import otqa.experiments.suite as module
    context = context_at(tmp_path)
    request = _suite_request(context)
    original = module.create_directory
    def race(context, path, **kwargs):
        path.mkdir(parents=True)
        return original(context, path, **kwargs)
    monkeypatch.setattr(module, 'create_directory', race)
    with pytest.raises(DocumentError, match='already exists'):
        module.create_suite(request)
    assert list(request.output_path.parent.iterdir()) == []


def test_suite_publication_failure_is_not_a_committed_suite(tmp_path, monkeypatch):
    import otqa.experiments.suite as module
    context = context_at(tmp_path)
    request = _suite_request(context)
    def fail(*args, **kwargs):
        raise OSError('injected suite publication failure')
    monkeypatch.setattr(module, 'publish_json', fail)
    with pytest.raises(OSError, match='injected'):
        module.create_suite(request)
    assert request.output_path.parent.is_dir()
    assert not request.output_path.exists()
    with pytest.raises(FileNotFoundError):
        load_document('suite', request.output_path, reference_root=context.project_root)
