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
