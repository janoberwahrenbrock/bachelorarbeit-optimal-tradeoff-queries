"""One public application facade; requests are neutral immutable wire adapters."""
from __future__ import annotations

from pathlib import Path

from .application_types import (
    RunRequest,
    RunOutcome,
    GenerateDatasetRequest,
    DatasetOutcome,
    CreateSuiteRequest,
    SuiteOutcome,
    PlanRequest,
    PlanOutcome,
    SeriesOutcome,
    SeriesStatus,
    AuditRequest,
    AuditOutcome,
    ExportRequest,
    ExportReceipt
)
from .runtime.project import ProjectContext, load_project_context

def generate_dataset(request: GenerateDatasetRequest) -> DatasetOutcome:
    from .experiments.dataset import generate_dataset as implementation
    return implementation(request)


def create_suite(request: CreateSuiteRequest) -> SuiteOutcome:
    from .experiments.suite import create_suite as implementation
    return implementation(request)


def run_problem(request: RunRequest) -> RunOutcome:
    from .runtime.supervisor import run_problem as implementation
    return implementation(request)


def plan_suite(request: PlanRequest) -> PlanOutcome:
    from .experiments.controller import plan_suite as implementation
    return implementation(request)


def run_suite(plan_path: Path, *, context: ProjectContext) -> SeriesOutcome:
    from .experiments.controller import run_suite as implementation
    return implementation(plan_path, context=context)


def resume_suite(series_dir: Path, *, context: ProjectContext) -> SeriesOutcome:
    from .experiments.controller import resume_suite as implementation
    return implementation(series_dir, context=context)


def inspect_series(series_dir: Path, *, context: ProjectContext) -> SeriesStatus:
    from .experiments.controller import inspect_series as implementation
    return implementation(series_dir, context=context)


def audit_series(request: AuditRequest) -> AuditOutcome:
    from .analysis.audit import audit_series as implementation
    return implementation(request)


def export_series(request: ExportRequest) -> ExportReceipt:
    from .analysis.export import export_series as implementation
    return implementation(request)


__all__ = ['RunRequest', 'RunOutcome', 'GenerateDatasetRequest', 'DatasetOutcome', 'CreateSuiteRequest', 'SuiteOutcome', 'PlanRequest', 'PlanOutcome', 'SeriesOutcome', 'SeriesStatus', 'AuditRequest', 'AuditOutcome', 'ExportRequest', 'ExportReceipt', 'ProjectContext', 'load_project_context', 'generate_dataset', 'create_suite', 'run_problem', 'plan_suite', 'run_suite', 'resume_suite', 'inspect_series', 'audit_series', 'export_series']
