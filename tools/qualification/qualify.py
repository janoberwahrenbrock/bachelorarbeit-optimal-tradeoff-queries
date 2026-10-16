"""Qualify an installed distribution using new native controls.

Run with the Python interpreter containing the built wheel. This harness is
outside the production package and has no public production trust/skip flag.
"""
from __future__ import annotations

import argparse
import importlib.metadata
import json
import math
import os
import re
import subprocess
import sys
import time
import traceback
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from uuid import uuid4

from otqa.runtime.codec import canonical_digest, digest, float_projection, read_json, utc_now
from otqa.runtime.documents import file_ref
from otqa.runtime.profiles import CHECK_SCOPE, METHODS, SCOPE_CHECKS, SCOPE_ORDER, THREAD_VARIABLES, _candidate_resolver, profile_digest
from otqa.runtime.project import load_project_context
from otqa.runtime.qualification_evidence import METHOD_CASES
from otqa.runtime.source import loaded_source
from otqa.runtime.storage import create_directory, publish_bytes, publish_json


PRODUCTION_PACKAGES = ("bachelorarbeit-optimal-tradeoff-queries", "numpy", "scipy", "jsonschema",
                       "attrs", "jsonschema-specifications", "referencing", "rpds-py")


def production_dependency_versions():
    """Bind the full active production closure for supported Python 3.13/3.14.

    Optional extras are inactive. The only active-installation Python marker in
    this fixed metadata family is referencing's pre-3.13 typing-extensions edge.
    Unexpected marker syntax or new dependencies require a deliberate harness
    review, rather than silently omitting an unbound validator dependency.
    """
    if sys.version_info[:2] not in ((3, 13), (3, 14)):
        raise RuntimeError("The production dependency closure is qualified only for Python 3.13/3.14")
    allowed, visited, pending = set(PRODUCTION_PACKAGES), set(), [PRODUCTION_PACKAGES[0]]
    while pending:
        name = pending.pop()
        if name in visited:
            continue
        if name not in allowed:
            raise RuntimeError(f"Unbound active production dependency: {name}")
        visited.add(name)
        for requirement in importlib.metadata.distribution(name).requires or ():
            dependency, separator, marker = requirement.partition(";")
            if separator:
                marker = marker.strip()
                if re.search(r'''\bextra\s*==\s*["'][^"']+["']''', marker) and " or " not in marker:
                    continue
                if re.fullmatch(r'''python_version\s*<\s*["']3\.13["']''', marker):
                    continue  # Supported interpreters are both >=3.13.
                raise RuntimeError(f"Unreviewed production dependency marker: {requirement}")
            match = re.match(r"\s*([A-Za-z0-9][A-Za-z0-9._-]*)", dependency)
            if match is None:
                raise RuntimeError(f"Invalid production dependency metadata: {requirement}")
            pending.append(re.sub(r"[-_.]+", "-", match.group(1)).lower())
    if visited != allowed:
        raise RuntimeError("Declared production package set differs from the installed active dependency closure")
    return {name: importlib.metadata.version(name) for name in PRODUCTION_PACKAGES}


class Controls:
    def __init__(self, context, root, profile):
        self.context, self.root, self.profile = context, root, profile
        self.facts = {}
        self.source = loaded_source()[0]
        self.problem = {"schema_version": 1, "problem_id": "native-control", "alternative_ids": ["left", "right"],
                        "objective_ids": ["g0", "g1"], "alternatives": [[1.0, 0.0], [0.0, 1.0]]}
        self.oracle = {"schema_version": 1, "problem_id": "native-control", "target_weights": [0.7, 0.3]}
        self.config = {"schema_version": 2, "configuration_id": "native-fixed1", "algorithm": {"query_strategy": "fixed", "depth": 1,
            "higher_depth_query_source": "both", "grid_size": 5, "planning_evaluation": "candidate_count", "stopping": {"rule": "single_candidate"},
            "horizon_execution": "receding", "min_expected_progress": 0.001},
            "budget": {"max_queries": None}, "execution": {"workers": 1, "start_method": "forkserver", "native_threads": 1, "case_timeout_seconds": None, "cache_policy_id": "bounded_v1"},
            "recording": {"durability": "per_answer", "trace_level": "full", "profile": False, "telemetry_failure_policy": "continue"}}
        for name, value, kind in (("problem", self.problem, "problem"), ("oracle", self.oracle, "oracle"), ("config", self.config, "config")):
            publish_json(context, root / "controls" / f"{name}.json", value, kind=kind)

    def sdk(self, provider=None, **kwargs):
        from otqa import AlgorithmPolicy, Problem, SingleCandidateStop, solve
        from otqa.answers import SimulatedAnswers
        problem = Problem(((1.0, 0.0), (0.0, 1.0)))
        policy = AlgorithmPolicy("fixed", 1, "both", 5, "candidate_count", SingleCandidateStop())
        return solve(problem, policy, provider or SimulatedAnswers((0.7, 0.3)), **kwargs)

    def observed(self, check, case):
        return getattr(self, check)(case)

    def installation(self, case):
        import otqa
        if case == "installed_distribution":
            distribution = importlib.metadata.distribution("bachelorarbeit-optimal-tradeoff-queries")
            direct = distribution.read_text("direct_url.json")
            metadata = json.loads(direct) if direct else {}
            editable = metadata.get("dir_info", {}).get("editable", False)
            location = Path(otqa.__file__).resolve()
            assert not editable and "site-packages" in location.parts
            return {"package_path": str(location), "editable": editable, "version": distribution.version}
        if case in ("external_cwd_import", "light_import"):
            script = "import json,sys,otqa;print(json.dumps({'file':otqa.__file__,'numerical_imports':[x for x in ('numpy','scipy') if x in sys.modules]}))"
            run = subprocess.run([sys.executable, "-c", script], cwd=self.root, capture_output=True, text=True, check=True)
            observation = json.loads(run.stdout)
            assert "site-packages" in Path(observation["file"]).parts
            assert not observation["numerical_imports"]
            return observation
        if case == "console_help":
            run = subprocess.run([str(Path(sys.executable).with_name("otqa")), "--help"], cwd=self.root, capture_output=True, text=True, check=True)
            assert "benchmark" in run.stdout and "dataset" in run.stdout
            return {"returncode": run.returncode, "stdout_sha256": digest(run.stdout.encode())}
        if case == "source_inventory":
            source, inventory, _ = loaded_source()
            assert source == self.source and inventory["files"]
            return {"source_sha256": source["source_sha256"], "files": len(inventory["files"])}
        if case == "offline_schemas":
            from otqa.runtime.schema import all_validators
            from otqa.runtime.schema_immutable import _thaw_schema
            validators = all_validators()
            assert validators and ("config", 1) in validators and ("config", 2) in validators
            schemas = list((Path(otqa.__file__).parent / "schemas").glob("*.schema.json"))
            schema_ids = {read_json(path)["$id"] for path in schemas}
            for validator in validators.values():
                assert validator.schema["$id"] in schema_ids
                # The metaschema expects JSON containers; check a faithful fresh
                # view of this actual compiled schema with the same validator.
                validator.check_schema(_thaw_schema(validator.schema))
            assert len(schema_ids) == len(schemas)
            return {"document_validators": len(validators), "schema_resources": len(schemas),
                    "versions": sorted({version for _, version in validators})}
        versions = production_dependency_versions()
        assert versions == self.profile["packages"]
        return {"packages": versions, "python": self.profile["python_version"], "active_production_closure_verified": True}

    def backend_conformance(self, case):
        import numpy as np
        from scipy.spatial import ConvexHull, QhullError
        from otqa.numerics.lp import LinearProgramBackend
        if case == "capabilities":
            from otqa.numerics.profile import actual_backend_capabilities
            actual = actual_backend_capabilities()
            assert actual == self.profile["backend_capabilities"]
            return actual
        if case == "qhull_full_dimensional":
            hull = ConvexHull(np.array([[0., 0.], [1., 0.], [0., 1.]]))
            assert hull.volume == 0.5
            return {"volume": float(hull.volume)}
        if case == "qhull_degenerate":
            try:
                ConvexHull(np.array([[0., 0.], [1., 0.], [2., 0.]]))
            except QhullError:
                return {"exception": "QhullError", "degenerate_points": 3}
            raise AssertionError("Degenerate hull unexpectedly succeeded")
        backend = LinearProgramBackend()
        try:
            if case == "lp_optimal":
                result = backend.solve(c=[-1.], A_ub=[[1.]], b_ub=[2.], bounds=[(None, None)])
                assert result.success and abs(float(result.x[0]) - 2.) < 1e-12
            elif case == "lp_infeasible":
                result = backend.solve(c=[0.], A_ub=[[1.], [-1.]], b_ub=[0., -1.], bounds=[(None, None)])
                assert not result.success and int(result.status) == 2
            elif case == "lp_unbounded":
                result = backend.solve(c=[-1.], bounds=[(None, None)])
                assert not result.success and int(result.status) == 3
            else:
                backend.close()
                backend = LinearProgramBackend(native=False)
                injected = SimpleNamespace(success=False, status=4, message="Injected numerical failure")
                with patch("otqa.numerics.lp.linprog", return_value=injected):
                    result = backend.solve(c=[1.], bounds=[(None, None)])
                assert not result.success and int(result.status) == 4 and backend.calls >= 2
            return {"success": bool(result.success), "status": int(result.status), "calls": backend.calls}
        finally:
            backend.close()

    def numerical_conformance(self, case):
        from otqa import AnsweredQuery, Query
        from otqa.geometry import GeometrySession
        if case == "binary64_input_identity":
            from otqa.runtime.codec import float_projection
            assert float_projection(-0.0) == {"float_hex": "-0x0.0p+0"}
            return {"negative_zero_hex": (-0.0).hex()}
        with GeometrySession() as geometry:
            if case == "equality_dimension":
                region = geometry.weight_space((AnsweredQuery(Query(0, 1, 1.0), "="),), 3)
                vertices = geometry.vertices(region)
                assert vertices.affine_dimension == 1
                return {"affine_dimension": vertices.affine_dimension, "vertex_count": len(vertices.vertices)}
            region = geometry.weight_space((), 3)
            if case == "simplex_volume":
                volume = geometry.volume(region)
                expected = math.sqrt(3.) / 2.
                assert abs(volume - expected) < 1e-12
                return {"volume": volume, "analytical_volume": expected, "absolute_error": abs(volume - expected)}
            probabilities = geometry.probabilities(region, Query(0, 1, 1.0))
            assert probabilities["="] == 0.0 and abs(probabilities["<"] - .5) < 1e-12 and abs(probabilities[">"] - .5) < 1e-12
            return {"probabilities": dict(probabilities)}

    def sdk_lifecycle(self, case):
        from otqa import AlgorithmPolicy, AnsweredQuery, Problem, Query, QueryBudget, SingleCandidateStop, SolverExecution, solve
        from otqa.answers import SimulatedAnswers
        if case == "singleton_stop":
            result = solve(Problem(((1., 1.), (0., 0.))), AlgorithmPolicy("fixed", 1, "both", 5, "candidate_count", SingleCandidateStop()), SimulatedAnswers((.7, .3)))
            assert result.solved and result.query_counts.answered_total == 0
        elif case == "initial_history":
            result = self.sdk(initial_answers=(AnsweredQuery(Query(0, 1, 1.0), ">"),), budget=QueryBudget(max_queries=1))
            assert result.solved and result.query_counts.initial_answers == result.query_counts.answered_total == 1 and result.query_counts.dispatched_new == 0
        elif case in ("provider_failure", "recorder_failure", "observer_failure"):
            def fail(*_):
                raise RuntimeError("Native qualification injected callback failure")
            expected = {"provider_failure": "AnswerProviderError", "recorder_failure": "RecorderError", "observer_failure": "ObserverError"}[case]
            try:
                if case == "provider_failure":
                    self.sdk(provider=fail)
                else:
                    self.sdk(**{"recorder" if case == "recorder_failure" else "observer": fail})
            except BaseException as exc:
                assert type(exc).__name__ == expected
                return {"exception": type(exc).__name__, "partial_context": exc.partial_context is not None}
            raise AssertionError("Callback failure was swallowed")
        elif case == "reentrant_sessions":
            first, second = self.sdk(), self.sdk()
            assert first == second
            return {"same_result": True, "first_queries": first.query_counts.answered_total, "second_queries": second.query_counts.answered_total}
        elif case == "owned_worker_pool":
            import multiprocessing
            from otqa.models.results import QueryPlanned
            seen = set()
            def observe(event):
                if isinstance(event, QueryPlanned):
                    seen.update(child.pid for child in multiprocessing.active_children())
            result = solve(Problem(((1., 0., 0.), (0., 1., 0.), (0., 0., 1.))),
                AlgorithmPolicy("fixed", 1, "both", 5, "candidate_count", SingleCandidateStop()), SimulatedAnswers((.7, .2, .1)),
                execution=SolverExecution(workers=2, multiprocessing_context=multiprocessing.get_context("forkserver")), observer=observe)
            assert result.solved and seen and len(seen) <= 2
            remaining = {child.pid for child in multiprocessing.active_children()}
            assert not seen.intersection(remaining)
            return {"solved": result.solved, "queries": result.query_counts.answered_total, "observed_worker_pids": sorted(seen), "workers_remaining": 0}
        else:
            result = self.sdk()
            assert result.solved and result.query_counts.answered_new == 1
        return {"termination_reason": result.termination_reason, "queries": result.query_counts.answered_total, "solved": result.solved}

    def request(self, name, *, mode="simulated", replay_path=None):
        from otqa.application import RunRequest
        return RunRequest(self.context, self.context.project_root, self.root / "controls" / "problem.json", self.root / "controls" / "config.json",
            self.root / "candidate-profile.json", mode, self.root / "cases" / name,
            self.root / "controls" / "oracle.json" if mode == "simulated" else None, replay_path)

    def native_case(self):
        if "native_case" not in self.facts:
            from otqa.runtime.supervisor import prepare_standalone, supervise_attempt
            payload = prepare_standalone(self.request("normal"), resolver=_candidate_resolver)
            self.facts["native_case"] = supervise_attempt(payload, context=self.context)
        return self.facts["native_case"]

    def standalone_io(self, case):
        from otqa.runtime.schema import validate
        if case in ("isolated_case", "durable_launch_chain", "durable_journal_counts"):
            outcome = self.native_case()
            result, directory = outcome.result, outcome.result_path.parent
            assert outcome.exit_code == 0 and result["execution_status"] == "completed" and result["solver_result"]["solved"]
            if case == "isolated_case":
                identity = read_json(directory / "child_registration.json")["process"]
                assert identity["pid"] == identity["pgid"] == identity["sid"] and identity["pid"] != os.getpid()
                return {"identity": identity, "case_elapsed": result["timings"]["case_elapsed_seconds"]}
            if case == "durable_launch_chain":
                intent, registration, grant = [read_json(directory / (name + ".json")) for name in ("launch_intent", "child_registration", "start_grant")]
                assert intent["nonce"] == registration["nonce"] == grant["nonce"] and registration["process"] == grant["process"]
                return {"nonce": intent["nonce"], "intent_sha256": file_ref(directory / "launch_intent.json", directory)["sha256"], "grant_sha256": file_ref(directory / "start_grant.json", directory)["sha256"]}
            cursor = validate("progress", read_json(directory / "progress.json"))
            assert cursor["query_counts"] == result["query_counts"] == {"initial_answers": 0, "dispatched_new": 1, "answered_new": 1, "answered_total": 1}
            assert cursor["query_phase"] == "completed" and result["journal"]["uncommitted_suffix_bytes"] == 0
            return {"query_counts": cursor["query_counts"], "last_good_sequence": cursor["last_good_sequence"], "valid_prefix_sha256": cursor["valid_prefix_sha256"]}
        if case == "provider_failure_counts":
            replay = self.root / "controls" / "divergent-replay.json"
            publish_json(self.context, replay, {"schema_version": 1, "problem_id": self.problem["problem_id"], "answers": [{"goal_index_a": 0, "goal_index_b": 1, "value": 123.0, "answer": ">"}]}, kind="answer_history")
            from otqa.runtime.supervisor import prepare_standalone, supervise_attempt
            payload = prepare_standalone(self.request("provider-failure", mode="replay", replay_path=replay), resolver=_candidate_resolver)
            outcome = supervise_attempt(payload, context=self.context)
            assert outcome.result["execution_status"] == "failed" and outcome.result["query_counts"]["dispatched_new"] == 1 and outcome.result["query_counts"]["answered_new"] == 0
            return {"status": outcome.result["execution_status"], "query_counts": outcome.result["query_counts"], "error": outcome.result["error"]["code"]}
        if case == "project_boundary":
            from otqa.runtime.codec import DocumentError
            try:
                self.context.relative_output(self.context.project_root / "outside-runs" / "case")
            except DocumentError:
                return {"rejected": "outside ProjectRoot/runs"}
            raise AssertionError("Outside run output accepted")
        if case == "cursor_publication_failure":
            return self.cursor_failure()
        if case == "pre_release_eof":
            return self.pre_release_eof()
        return self.series_audit_export()

    def cursor_failure(self):
        from otqa.runtime.processes import process_identity
        from otqa.runtime.storage import RunStore
        directory = self.root / "faults" / "cursor"
        create_directory(self.context, directory)
        run_id = str(uuid4())
        store = RunStore(self.context, directory, directory, run_id, "attempt0001", process_identity(uuid4().hex), 0)
        event = {"schema_version": 1, "run_id": run_id, "attempt_id": "attempt0001", "sequence": 1, "occurred_at_utc": utc_now(), "monotonic_ns": time.monotonic_ns(),
                 "event_type": "run_started", "query_id": None, "payload": {"manifest_sha256": "0" * 64}, "numeric_hex": {}}
        store.append(event)
        try:
            with patch("otqa.runtime.storage.publish_json", side_effect=OSError("Injected cursor publication failure")):
                store.commit()
        except OSError:
            assert store.failed and store.cursor is None and not (directory / "progress.json").exists()
            assert (directory / "events.jsonl").read_bytes()
            return {"cursor": None, "poisoned": store.failed, "raw_journal_bytes": (directory / "events.jsonl").stat().st_size}
        finally:
            store.close()
        raise AssertionError("Cursor failure was not propagated")

    def pre_release_eof(self):
        from otqa.runtime.supervisor import prepare_standalone
        payload = prepare_standalone(self.request("pre-release-eof"), resolver=_candidate_resolver)
        directory = Path(payload["attempt_dir"])
        owner, nonce = uuid4().hex, uuid4().hex
        from otqa.runtime.processes import process_identity
        intent = {"schema_version": 1, "run_id": payload["run_id"], "attempt_id": payload["attempt_id"], "series_id": None, "job_id": None,
            "problem_id": payload["problem_id"], "configuration_id": payload["configuration_id"], "created_at_utc": utc_now(), "owner_token": owner,
            "nonce": nonce, "controller": process_identity(owner), "materialization_receipt": payload["materialization_receipt"]}
        publish_json(self.context, directory / "launch_intent.json", intent, kind="launch_intent")
        publish_json(self.context, directory / "case-request.json", payload)
        read_fd, write_fd = os.pipe()
        child = subprocess.Popen([sys.executable, "-m", "otqa.runtime.case", "--request", str(directory / "case-request.json"), "--release-fd", str(read_fd)],
                                 pass_fds=(read_fd,), start_new_session=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        os.close(read_fd)
        os.close(write_fd)
        stdout, stderr = child.communicate(timeout=20)
        assert child.returncode != 0 and not (directory / "manifest.json").exists() and not (directory / "events.jsonl").exists()
        assert (directory / "child_registration.json").exists()
        return {"returncode": child.returncode, "solver_started": False, "registration_present": True, "stderr_sha256": digest(stderr)}

    def series_audit_export(self):
        from otqa.application import AuditRequest, ExportRequest, PlanRequest
        from otqa.analysis.audit import audit_series
        from otqa.analysis.export import export_series
        from otqa.experiments.controller import _execute, plan_suite
        dataset_path = self.root / "controls" / "dataset.json"
        publish_json(self.context, dataset_path, {"schema_version": 1, "dataset_id": "qualification-dataset", "generator": None,
            "cases": [{"case_id": "control", "problem": file_ref(self.root / "controls" / "problem.json", self.context.project_root), "oracle": file_ref(self.root / "controls" / "oracle.json", self.context.project_root)}]}, kind="dataset")
        # A qualification suite is operational evidence stored under runs/, not
        # a public dataset-generating command with a different output contract.
        suite_path = self.root / "controls" / "suite.json"
        publish_json(self.context, suite_path, {"schema_version": 1, "suite_id": "qualification-suite", "dataset": file_ref(dataset_path, self.context.project_root),
            "configurations": [{"configuration_id": self.config["configuration_id"], **file_ref(self.root / "controls" / "config.json", self.context.project_root)}],
            "selection": [{"configuration_id": self.config["configuration_id"], "case_ids": ["control"]}], "repetitions": 1,
            "execution": {"max_concurrent_cases": 1, "job_order": "case_repetition_config_rotated"}}, kind="suite")
        planned = plan_suite(PlanRequest(self.context, self.context.project_root, suite_path, self.root / "candidate-profile.json", self.root / "series"), resolver=_candidate_resolver)
        # On macOS the required series admission scope is standalone. Linux's
        # recovery path is qualified by its own subsequent method controls.
        outcome = _execute(planned.series_dir, context=self.context, resume=False, resolver=_candidate_resolver)
        assert outcome.exit_code == 0 and outcome.state["status"] == "completed"
        audit = audit_series(AuditRequest(self.context, planned.series_dir, planned.series_dir / "reports" / str(uuid4()) / "audit.json"), _allow_qualification=True)
        assert audit.exit_code == 0 and audit.report["status"] == "passed"
        exported = export_series(ExportRequest(self.context, planned.series_dir, "json", planned.series_dir / "exports" / "controls.json", file_ref(audit.report_path, planned.series_dir)), _allow_qualification=True)
        summary = read_json(exported.output_path)
        assert len(summary["rows"]) == 1 and summary["groups"][0]["correct"] == 1 and summary["groups"][0]["planned_jobs"] == 1
        return {"series_status": outcome.state["status"], "jobs": len(summary["rows"]), "audit_status": audit.report["status"], "export_sha256": exported.sha256}

    def linux_recovery(self, case):
        if not sys.platform.startswith("linux"):
            raise RuntimeError("Linux recovery cannot be qualified on this platform")
        from linux_controls import run_linux_control
        return run_linux_control(self, case)


def qualify(project_root: Path, output: Path, scope: str):
    context = load_project_context(project_root)
    context.binding(output)
    if scope not in SCOPE_CHECKS:
        raise ValueError("Unknown qualification scope")
    if scope == "series_linux_recovery" and not sys.platform.startswith("linux"):
        raise ValueError("Linux recovery scope requires a Linux execution host")
    create_directory(context, output)
    for key in THREAD_VARIABLES:
        os.environ[key] = "1"
    from otqa.numerics.profile import actual_backend_capabilities, resolved_cache_policy, resolved_numerical_profile
    import platform
    versions = production_dependency_versions()
    lock_bytes = "".join(f"{name}=={versions[name]}\n" for name in sorted(versions)).encode()
    publish_bytes(context, output / "environment-lock.txt", lock_bytes)
    profile = {"schema_version": 1, "profile_id": "native-" + uuid4().hex, "platform_family": "linux" if sys.platform.startswith("linux") else "macos",
        "python_version": platform.python_version(), "packages": versions, "backend_capabilities": actual_backend_capabilities(),
        "environment_lock": file_ref(output / "environment-lock.txt", context.project_root), "certification": {"status": "qualifying", "evidence": None}}
    publish_json(context, output / "candidate-profile.json", profile, kind="execution_profile")
    controls = Controls(context, output, profile)
    source, _, _ = loaded_source()
    numerics, cache = resolved_numerical_profile(), resolved_cache_policy()
    values_hash = canonical_digest(float_projection(numerics["values"]))
    checks, all_passed = [], True
    harness_files = [Path(__file__)]
    linux_helper = Path(__file__).with_name("linux_controls.py")
    if linux_helper.exists():
        harness_files.append(linux_helper)
    harness_hash = canonical_digest({"files": [{"path": path.name, "sha256": digest(path.read_bytes())} for path in sorted(harness_files)]})
    for check in SCOPE_CHECKS[scope]:
        started = utc_now()
        observations = []
        for case in METHOD_CASES[check]:
            try:
                details = controls.observed(check, case)
                passed = True
            except BaseException as exc:
                details = {"exception": type(exc).__name__, "message": str(exc), "traceback": traceback.format_exc()}
                passed = False
            observations.append({"case_id": case, "expected": True, "observed": passed, "passed": passed, "details": details})
        status = "passed" if all(item["passed"] for item in observations) else "failed"
        all_passed = all_passed and status == "passed"
        check_scope = CHECK_SCOPE[check]
        subject = {"purpose": "native_runtime", "method": METHODS[check], "check_id": check, "scope": check_scope, "inventory_format": source["inventory_format"],
            "source_sha256": source["source_sha256"], "profile_projection_sha256": profile_digest(profile), "numerical_values_sha256": values_hash, "cache_policy_id": cache["policy_id"]}
        raw_path = output / "raw" / f"{check}.json"
        raw = {"schema_version": 1, **subject, "started_at_utc": started, "finished_at_utc": utc_now(), "observations": observations, "status": status, "harness_sha256": harness_hash}
        publish_json(context, raw_path, raw)
        evidence_path = output / "checks" / f"{check}.json"
        evidence = {"schema_version": 1, **subject, "status": status, "raw_reports": [file_ref(raw_path, context.project_root)], "illustrative_only": False}
        publish_json(context, evidence_path, evidence, kind="certification_check_evidence")
        checks.append({"check_id": check, "scope": check_scope, "status": status, "evidence": file_ref(evidence_path, context.project_root)})
        print(json.dumps({"check": check, "status": status, "passed_controls": sum(item["passed"] for item in observations), "total_controls": len(observations)}), flush=True)
    certification = {"schema_version": 1, "certification_id": "native-" + uuid4().hex, "created_at_utc": utc_now(), "purpose": "native_runtime", "source": source,
        "profile_projection_sha256": profile_digest(profile), "environment_lock": profile["environment_lock"], "numerical_profile_id": numerics["profile_id"],
        "numerical_values_sha256": values_hash, "cache_policy_id": cache["policy_id"], "scopes": list(SCOPE_ORDER[:SCOPE_ORDER.index(scope) + 1]),
        "checks": checks, "status": "passed" if all_passed else "failed", "illustrative_only": False}
    publish_json(context, output / "certification.json", certification, kind="certification")
    if all_passed:
        final_profile = {**profile, "certification": {"status": "validated", "evidence": file_ref(output / "certification.json", context.project_root)}}
        from otqa.runtime.profiles import verify_certification
        verify_certification(context.project_root, final_profile, source, scope)
        publish_json(context, output / "profile.json", final_profile, kind="execution_profile")
    return all_passed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--scope", choices=tuple(SCOPE_CHECKS), required=True)
    args = parser.parse_args()
    return 0 if qualify(args.project_root.resolve(), args.output.absolute(), args.scope) else 1


if __name__ == "__main__":
    raise SystemExit(main())
