"""Argument parsing and lightweight bootstrap; no numerical imports here."""
from __future__ import annotations

import argparse
import os
from dataclasses import asdict
from pathlib import Path
from uuid import uuid4


def parser():
    root = argparse.ArgumentParser(prog="otqa", description="Exact geometric optimal trade-off query experiments")
    root.add_argument("--project-root", type=Path, help="Explicit marked project root (default: invocation directory)")
    root.add_argument("--version", action="version", version="otqa 0.1.0")
    commands = root.add_subparsers(dest="command", required=True)
    solve = commands.add_parser("solve", help="Solve one problem through an isolated durable CaseProcess")
    for option in ("source-root", "problem", "config", "execution-profile", "output"):
        solve.add_argument("--" + option, type=Path, required=True)
    solve.add_argument("--answers", choices=("interactive", "simulated", "replay"), required=True)
    for option in ("oracle", "answers-file", "initial-answers"):
        solve.add_argument("--" + option, type=Path)
    dataset = commands.add_parser("dataset", help="Generate stored independent problem/oracle inputs")
    generate = dataset.add_subparsers(dest="operation", required=True).add_parser("generate")
    generate.add_argument("--dataset-id", required=True)
    generate.add_argument("--master-seed", type=int, required=True)
    generate.add_argument("--objectives", nargs="+", type=int, required=True)
    generate.add_argument("--alternatives", nargs="+", type=int, required=True)
    generate.add_argument("--cases-per-shape", type=int, required=True)
    generate.add_argument("--output", type=Path, required=True)
    suite = commands.add_parser("suite", help="Create an explicit suite without running solvers")
    create = suite.add_subparsers(dest="operation", required=True).add_parser("create")
    for option in ("source-root", "dataset", "selection-file", "output"):
        create.add_argument("--" + option, type=Path, required=True)
    create.add_argument("--suite-id", required=True)
    create.add_argument("--config", type=Path, nargs="+", required=True)
    create.add_argument("--repetitions", type=int, required=True)
    benchmark = commands.add_parser("benchmark", help="Plan, run, resume, inspect, audit and export saved experiments")
    operations = benchmark.add_subparsers(dest="operation", required=True)
    plan = operations.add_parser("plan")
    for option in ("source-root", "suite", "execution-profile", "output"):
        plan.add_argument("--" + option, type=Path, required=True)
    run = operations.add_parser("run")
    run.add_argument("--plan", type=Path, required=True)
    for operation in ("status", "resume", "audit", "export"):
        sub = operations.add_parser(operation)
        sub.add_argument("--series", type=Path, required=True)
        if operation == "audit":
            sub.add_argument("--output", type=Path)
        elif operation == "export":
            sub.add_argument("--format", choices=("json", "csv"), required=True)
            sub.add_argument("--output", type=Path, required=True)
            sub.add_argument("--audit-ref", help="Exact reports/<UUID>/audit.json path relative to this series")
    return root


def _path(value):
    return Path(os.path.abspath(value)) if value is not None else None


def _json_default(value):
    if isinstance(value, Path):
        return str(value)
    raise TypeError(type(value).__name__)


def main(argv=None):
    import json
    args = parser().parse_args(argv)
    from otqa.runtime.codec import DocumentError, read_json
    from otqa.runtime.project import load_project_context
    from otqa.runtime.supervisor import RecoveryBlockedError
    try:
        context = load_project_context(_path(args.project_root) if args.project_root else Path.cwd())
        from otqa import application as app
        if args.command == "solve":
            from otqa.runtime.documents import load_config_document
            from otqa.runtime.profiles import set_native_threads
            config = load_config_document(_path(args.config), reference_root=_path(args.source_root))
            set_native_threads(config["execution"]["native_threads"])
            outcome = app.run_problem(app.RunRequest(context, _path(args.source_root), _path(args.problem), _path(args.config), _path(args.execution_profile),
                args.answers, _path(args.output), _path(args.oracle), _path(args.answers_file), _path(args.initial_answers)))
            result = outcome.result
            response = {"run_id": result["run_id"], "attempt_id": result["attempt_id"], "execution_status": result["execution_status"],
                "termination_reason": result["solver_result"]["termination_reason"] if result["solver_result"] else None,
                "result_path": str(outcome.result_path), "query_counts": result["query_counts"]}
            code = outcome.exit_code
        elif args.command == "dataset":
            from otqa.runtime.profiles import set_native_threads
            set_native_threads(1)
            outcome = app.generate_dataset(app.GenerateDatasetRequest(context, args.dataset_id, args.master_seed, args.objectives, args.alternatives, args.cases_per_shape, _path(args.output)))
            response, code = {"dataset_path": str(outcome.dataset_path), "case_count": len(outcome.dataset["cases"])}, 0
        elif args.command == "suite":
            selection = read_json(_path(args.selection_file))
            outcome = app.create_suite(app.CreateSuiteRequest(context, _path(args.source_root), args.suite_id, _path(args.dataset), tuple(_path(path) for path in args.config),
                selection, args.repetitions, _path(args.output)))
            response, code = {"suite_path": str(outcome.suite_path)}, 0
        elif args.operation == "plan":
            outcome = app.plan_suite(app.PlanRequest(context, _path(args.source_root), _path(args.suite), _path(args.execution_profile), _path(args.output)))
            response, code = {"series_dir": str(outcome.series_dir), "plan_path": str(outcome.plan_path), "planned_jobs": len(outcome.plan["jobs"])}, 0
        elif args.operation in ("run", "resume"):
            outcome = app.run_suite(_path(args.plan), context=context) if args.operation == "run" else app.resume_suite(_path(args.series), context=context)
            response, code = {"series_dir": str(outcome.series_dir), "status": outcome.state["status"], "jobs": outcome.state["jobs"]}, outcome.exit_code
        elif args.operation == "status":
            outcome = app.inspect_series(_path(args.series), context=context)
            response, code = asdict(outcome), 0
        elif args.operation == "audit":
            output = _path(args.output) if args.output else _path(args.series) / "reports" / str(uuid4()) / "audit.json"
            outcome = app.audit_series(app.AuditRequest(context, _path(args.series), output))
            response, code = {"audit_path": str(outcome.report_path), "status": outcome.report["status"]}, outcome.exit_code
        else:
            from otqa.runtime.documents import file_ref, resolve_ref
            root = _path(args.series)
            audit_ref = file_ref(root / args.audit_ref, root) if args.audit_ref else None
            if audit_ref is not None:
                resolve_ref(root, audit_ref)
            outcome = app.export_series(app.ExportRequest(context, root, args.format, _path(args.output), audit_ref))
            response, code = asdict(outcome), 0
        print(json.dumps(response, ensure_ascii=False, sort_keys=True, default=_json_default, allow_nan=False))
        return code
    except (DocumentError, FileNotFoundError, NotADirectoryError) as exc:
        print(json.dumps({"error": {"code": "invalid_input", "type": type(exc).__name__, "message": str(exc)}}))
        return 2
    except KeyboardInterrupt:
        print(json.dumps({"error": {"code": "user_cancel", "message": "User interrupted the command"}}))
        return 130
    except (RecoveryBlockedError, OSError, RuntimeError) as exc:
        print(json.dumps({"error": {"code": "runtime_failure", "type": type(exc).__name__, "message": str(exc)}}))
        return 1
