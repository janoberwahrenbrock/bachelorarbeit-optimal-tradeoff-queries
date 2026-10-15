"""Neutral immutable application request/outcome types; no orchestration imports."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Sequence

from .runtime.project import ProjectContext


@dataclass(frozen=True)
class RunRequest:
    context: ProjectContext
    source_root: Path
    problem_path: Path
    config_path: Path
    execution_profile_path: Path
    answer_source: Literal["interactive", "simulated", "replay"]
    output_dir: Path
    oracle_path: Path | None = None
    replay_path: Path | None = None
    initial_answers_path: Path | None = None


@dataclass(frozen=True)
class RunOutcome:
    result_path: Path
    result: dict
    exit_code: int


@dataclass(frozen=True)
class GenerateDatasetRequest:
    context: ProjectContext
    dataset_id: str
    master_seed: int
    objective_counts: Sequence[int]
    alternative_counts: Sequence[int]
    cases_per_shape: int
    output_dir: Path


@dataclass(frozen=True)
class DatasetOutcome:
    dataset_path: Path
    dataset: dict
    artifacts: tuple[dict, ...]
    reference_root: Path


@dataclass(frozen=True)
class CreateSuiteRequest:
    context: ProjectContext
    source_root: Path
    suite_id: str
    dataset_path: Path
    configuration_paths: Sequence[Path]
    selection: Sequence[dict]
    repetitions: int
    output_path: Path


@dataclass(frozen=True)
class SuiteOutcome:
    suite_path: Path
    suite: dict
    artifact: dict
    reference_root: Path


@dataclass(frozen=True)
class PlanRequest:
    context: ProjectContext
    source_root: Path
    suite_path: Path
    execution_profile_path: Path
    output_dir: Path


@dataclass(frozen=True)
class PlanOutcome:
    series_dir: Path
    plan_path: Path
    plan: dict


@dataclass(frozen=True)
class SeriesOutcome:
    series_dir: Path
    state: dict
    exit_code: int


@dataclass(frozen=True)
class SeriesStatus:
    series_dir: Path
    plan: dict
    state: dict
    processes: tuple[dict, ...]
    warnings: tuple[str, ...]


@dataclass(frozen=True)
class AuditRequest:
    context: ProjectContext
    series_dir: Path
    output_path: Path


@dataclass(frozen=True)
class AuditOutcome:
    report_path: Path
    report: dict
    exit_code: int


@dataclass(frozen=True)
class ExportRequest:
    context: ProjectContext
    series_dir: Path
    format: Literal["json", "csv"]
    output_path: Path
    audit_ref: dict | None = None


@dataclass(frozen=True)
class ExportReceipt:
    output_path: Path
    sha256: str
    reference_root: Path
    audit: dict
    plan: dict
    state: dict
    scope: Literal["complete", "partial"]


