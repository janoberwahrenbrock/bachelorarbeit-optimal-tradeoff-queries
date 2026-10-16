"""Explicit suite selections; deterministic serial rotated job order."""
from __future__ import annotations

from pathlib import Path

from otqa.runtime.codec import DocumentError
from otqa.runtime.documents import file_ref, load_document, resolve_ref, verified_closure
from otqa.runtime.project import identifier
from otqa.runtime.schema import latest_version, validate
from otqa.runtime.storage import create_directory, publish_json


def create_suite(request):
    from otqa.application_types import SuiteOutcome
    context = request.context
    suite_id = identifier(request.suite_id)
    destination = context.project_root / "inputs" / "suites" / suite_id
    if Path(request.output_path).absolute() != destination / "suite.json":
        raise DocumentError("Suite output must be ProjectRoot/inputs/suites/<suite-id>/suite.json")
    context.relative_output(destination, namespace="inputs")
    if destination.exists():
        raise DocumentError("Suite destination already exists")
    root = Path(request.source_root).resolve(strict=True)
    try:
        destination.relative_to(root)
    except ValueError as exc:
        raise DocumentError("Suite output must also lie under its explicit reference source root") from exc
    dataset = load_document("dataset", request.dataset_path, reference_root=root)
    configurations = []
    for path in request.configuration_paths:
        config = load_document("config", path, reference_root=root)
        if config["schema_version"] != latest_version("config"):
            raise DocumentError("New suites require explicitly converted current configurations")
        configurations.append({"configuration_id": config["configuration_id"], **file_ref(path, root)})
    suite = {"schema_version": 1, "suite_id": suite_id, "dataset": file_ref(request.dataset_path, root), "configurations": configurations,
        "selection": list(request.selection), "repetitions": request.repetitions,
        "execution": {"max_concurrent_cases": 1, "job_order": "case_repetition_config_rotated"}}
    validate("suite", suite)
    _validate_selection(suite, dataset)
    entries = {"dataset": ("dataset", request.dataset_path)}
    entries.update({f"config{index}": ("config", path) for index, path in enumerate(request.configuration_paths)})
    verified_closure(root, entries)
    # Reserve the exact destination without replacing even an empty directory.
    # suite.json is published last and is the only committed suite entrypoint.
    create_directory(context, destination, namespace="inputs")
    publish_json(context, destination / "suite.json", suite, kind="suite", namespace="inputs")
    return SuiteOutcome(destination / "suite.json", suite, file_ref(destination / "suite.json", root), root)


def _validate_selection(suite, dataset):
    configurations = [item["configuration_id"] for item in suite["configurations"]]
    selections = [item["configuration_id"] for item in suite["selection"]]
    if len(configurations) != len(set(configurations)) or len(selections) != len(set(selections)) or set(configurations) != set(selections):
        raise DocumentError("Suite needs exactly one explicit selection per unique configuration")
    known_cases = {case["case_id"] for case in dataset["cases"]}
    for selection in suite["selection"]:
        if not set(selection["case_ids"]).issubset(known_cases):
            raise DocumentError("Suite selection names an unknown dataset case")


def ordered_jobs(suite: dict, dataset: dict, reference_root: Path) -> list[dict]:
    _validate_selection(suite, dataset)
    configurations = suite["configurations"]
    selection = {item["configuration_id"]: set(item["case_ids"]) for item in suite["selection"]}
    jobs = []
    for case_index, case in enumerate(dataset["cases"]):
        problem = load_document("problem", resolve_ref(reference_root, case["problem"]), reference_root=reference_root)
        for repetition in range(suite["repetitions"]):
            offset = (case_index + repetition) % len(configurations)
            rotated = configurations[offset:] + configurations[:offset]
            for configuration in rotated:
                if case["case_id"] not in selection[configuration["configuration_id"]]:
                    continue
                jobs.append({"job_id": f"job{len(jobs) + 1:06d}", "case_id": case["case_id"], "problem_id": problem["problem_id"],
                    "configuration_id": configuration["configuration_id"], "repetition_index": repetition,
                    "problem": case["problem"], "oracle": case["oracle"], "configuration": {key: configuration[key] for key in ("path", "sha256")}})
    return jobs
