"""Independent per-case seed streams and exclusively reserved native datasets."""
from __future__ import annotations

from pathlib import Path

from otqa.runtime.codec import DocumentError, digest, encode
from otqa.runtime.project import identifier
from otqa.runtime.schema import validate
from otqa.runtime.storage import create_directory, publish_bytes


def _positive(value, name):
    if type(value) is not int or value < 1:
        raise DocumentError(f"{name} must be a positive integer")


def _shapes(values, name):
    if not values or len(values) != len(set(values)):
        raise DocumentError(f"{name} must be nonempty and unique")
    for value in values:
        _positive(value, name)


def generate_dataset(request):
    from otqa.application_types import DatasetOutcome
    context = request.context
    dataset_id = identifier(request.dataset_id)
    if type(request.master_seed) is not int or request.master_seed < 0:
        raise DocumentError("master_seed must be a nonnegative integer")
    _shapes(request.objective_counts, "objective_counts")
    _shapes(request.alternative_counts, "alternative_counts")
    _positive(request.cases_per_shape, "cases_per_shape")
    destination = context.project_root / "inputs" / "datasets" / dataset_id
    if Path(request.output_dir).absolute() != destination:
        raise DocumentError("Dataset output must be ProjectRoot/inputs/datasets/<dataset-id>/")
    context.relative_output(destination, namespace="inputs")
    if destination.exists():
        raise DocumentError("Dataset output already exists")
    # Validation intentionally precedes the only numerical dependency import.
    import numpy as np
    # mkdirat is the no-overwrite reservation: even an empty concurrent target
    # must cause failure. The final dataset.json is the bundle commit marker;
    # interrupted payload files remain inspectable without a readable dataset.
    create_directory(context, destination, namespace="inputs")
    cases, artifacts, seed_records = [], [], []
    for dimensions in request.objective_counts:
        for alternatives in request.alternative_counts:
            for index in range(request.cases_per_shape):
                case_id = f"d{dimensions}-m{alternatives}-c{index:06d}"
                seed = [request.master_seed, dimensions, alternatives, index]
                rng = np.random.Generator(np.random.PCG64(np.random.SeedSequence(seed)))
                matrix = rng.random((alternatives, dimensions))
                weights = rng.dirichlet(np.ones(dimensions))
                problem = {"schema_version": 1, "problem_id": case_id,
                    "alternative_ids": [f"a{j}" for j in range(alternatives)], "objective_ids": [f"g{j}" for j in range(dimensions)],
                    "alternatives": matrix.tolist()}
                oracle = {"schema_version": 1, "problem_id": case_id, "target_weights": weights.tolist()}
                refs = {}
                for kind, data in (("problem", problem), ("oracle", oracle)):
                    validate(kind, data)
                    relative = f"{kind}s/{case_id}.json"
                    raw = encode(data)
                    publish_bytes(context, destination / relative, raw, namespace="inputs")
                    reference = {"path": (destination / relative).relative_to(context.project_root).as_posix(), "sha256": digest(raw)}
                    refs[kind] = reference
                    artifacts.append(reference)
                cases.append({"case_id": case_id, **refs})
                seed_records.append({"case_id": case_id, "seed_sequence_entropy": seed})
    dataset = {"schema_version": 1, "dataset_id": dataset_id,
        "generator": {"name": "uniform_matrix_dirichlet_weights_v1", "version": 1, "master_seed": request.master_seed,
            "parameters": {"objective_counts": list(request.objective_counts), "alternative_counts": list(request.alternative_counts), "cases_per_shape": request.cases_per_shape},
            "rng": "PCG64", "numpy_version": np.__version__, "weights_distribution": "Dirichlet(alpha=1)",
            "matrix_distribution": "Uniform[0,1)", "case_seed_provenance": seed_records}, "cases": cases}
    validate("dataset", dataset)
    dataset_bytes = encode(dataset)
    publish_bytes(context, destination / "dataset.json", dataset_bytes, namespace="inputs")
    dataset_ref = {"path": (destination / "dataset.json").relative_to(context.project_root).as_posix(), "sha256": digest(dataset_bytes)}
    return DatasetOutcome(destination / "dataset.json", dataset, tuple(artifacts + [dataset_ref]), context.project_root)
