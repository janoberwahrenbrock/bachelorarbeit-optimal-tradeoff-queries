"""Actual environment binding and native runtime qualification admission.

Production never treats an example, a user-set status or external comparison
report as runtime qualification. Qualification uses a private resolver at the
same preparation boundary; it is not a command-line bypass.
"""
from __future__ import annotations

import importlib.metadata
import os
import platform
import sys
from dataclasses import dataclass
from pathlib import Path

from .codec import DocumentError, canonical_digest, float_projection
from .documents import load_document, resolve_ref
from .source import loaded_source, same_source

THREAD_VARIABLES = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "BLIS_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS")
METHODS = {"installation": "installed-wheel-v1", "backend_conformance": "lp-qhull-conformance-v1", "numerical_conformance": "analytical-numerics-v1",
           "sdk_lifecycle": "sdk-session-v1", "standalone_io": "durable-standalone-v1", "linux_recovery": "durable-linux-recovery-v1"}
SCOPE_CHECKS = {"sdk": tuple(list(METHODS)[:4]), "standalone": tuple(list(METHODS)[:5]), "series_linux_recovery": tuple(METHODS)}
CHECK_SCOPE = {check: "sdk" for check in SCOPE_CHECKS["sdk"]} | {"standalone_io": "standalone", "linux_recovery": "series_linux_recovery"}
SCOPE_ORDER = ("sdk", "standalone", "series_linux_recovery")


def platform_family() -> str:
    if sys.platform.startswith("linux"):
        return "linux"
    if sys.platform == "darwin":
        return "macos"
    raise DocumentError("Only qualified Linux/macOS process adapters are supported")


def environment_snapshot(packages: dict[str, str], capabilities: dict) -> dict:
    actual = {}
    for package in packages:
        try:
            actual[package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError as exc:
            raise DocumentError(f"Required distribution is not installed: {package}") from exc
    return {"hostname": platform.node(), "platform_family": platform_family(), "platform": platform.platform(),
        "python": platform.python_version(), "packages": actual, "cpu_model": platform.processor() or None,
        "physical_cores": None, "logical_cpus": os.cpu_count(),
        "native_thread_environment": {key: os.environ[key] for key in THREAD_VARIABLES if key in os.environ},
        "backend_capabilities": capabilities}


def set_native_threads(count: int) -> None:
    if type(count) is not int or count <= 0:
        raise DocumentError("native_threads must be a positive integer")
    if any(name in sys.modules for name in ("numpy", "scipy")):
        raise DocumentError("Numerical libraries were imported before the CLI thread bootstrap")
    for key in THREAD_VARIABLES:
        os.environ[key] = str(count)


def profile_projection(profile: dict) -> dict:
    return {key: profile[key] for key in ("schema_version", "profile_id", "platform_family", "python_version", "packages", "backend_capabilities")} | {
        "environment_lock_sha256": profile["environment_lock"]["sha256"]}


def profile_digest(profile: dict) -> str:
    return canonical_digest(float_projection(profile_projection(profile)))


def verify_environment(profile: dict) -> dict:
    actual = environment_snapshot(profile["packages"], profile["backend_capabilities"])
    if actual["platform_family"] != profile["platform_family"] or actual["python"] != profile["python_version"] or actual["packages"] != profile["packages"]:
        raise DocumentError("Actual Python/platform/package versions differ from the execution profile")
    if not {"numpy", "scipy"}.issubset(profile["packages"]):
        raise DocumentError("Execution profile must bind NumPy and SciPy distribution versions")
    # Backend capabilities are concretely exercised by source/environment-bound
    # check evidence and verified again by the numerical adapter in qualification.
    if not profile["backend_capabilities"]:
        raise DocumentError("Empty backend capability profiles are not admissible")
    return actual


@dataclass(frozen=True)
class VerifiedExecutionProfile:
    document: dict
    environment: dict
    source: dict
    requested_scope: str
    run_purpose: str


def verify_certification(reference_root: Path, profile: dict, source: dict,
                         requested_scope: str) -> VerifiedExecutionProfile:
    if requested_scope not in SCOPE_CHECKS:
        raise DocumentError("Unknown qualification scope")
    if profile["certification"]["status"] != "validated" or profile["certification"]["evidence"] is None:
        raise DocumentError("Production requires a validated native runtime certificate")
    certificate = load_document("certification", resolve_ref(reference_root, profile["certification"]["evidence"]), reference_root=reference_root)
    _verify_certificate(reference_root, profile, source, requested_scope, certificate)
    return VerifiedExecutionProfile(profile, verify_environment(profile), source, requested_scope, "production")


def _verify_certificate(root: Path, profile: dict, source: dict, scope: str, certificate: dict) -> None:
    from otqa.numerics.profile import resolved_cache_policy, resolved_numerical_profile
    numerics, cache = resolved_numerical_profile(), resolved_cache_policy()
    values_hash = canonical_digest(float_projection(numerics["values"]))
    projection_hash = profile_digest(profile)
    if not same_source(certificate["source"], source) or certificate["purpose"] != "native_runtime":
        raise DocumentError("Certificate source identity or purpose differs")
    if certificate["illustrative_only"] or certificate["status"] != "passed" or scope not in certificate["scopes"]:
        raise DocumentError("Certificate is illustrative, failed or insufficient for this scope")
    if certificate["profile_projection_sha256"] != projection_hash or certificate["environment_lock"]["sha256"] != profile["environment_lock"]["sha256"]:
        raise DocumentError("Certificate profile or lock binding differs")
    resolve_ref(root, profile["environment_lock"])
    resolve_ref(root, certificate["environment_lock"])
    if certificate["numerical_profile_id"] != numerics["profile_id"] or certificate["numerical_values_sha256"] != values_hash or certificate["cache_policy_id"] != cache["policy_id"]:
        raise DocumentError("Certificate numerical/cache binding differs")
    required_scopes = set(SCOPE_ORDER[:SCOPE_ORDER.index(scope) + 1])
    if not required_scopes.issubset(certificate["scopes"]):
        raise DocumentError("Higher runtime scopes require their lower-scope qualifications")
    pairs = [(item["check_id"], item["scope"]) for item in certificate["checks"]]
    if len(pairs) != len(set(pairs)) or any(CHECK_SCOPE[item["check_id"]] != item["scope"] for item in certificate["checks"]):
        raise DocumentError("Certificate check scopes are duplicated or assigned incorrectly")
    matching = [item for item in certificate["checks"] if item["check_id"] in SCOPE_CHECKS[scope]]
    if len(matching) != len(SCOPE_CHECKS[scope]) or {item["check_id"] for item in matching} != set(SCOPE_CHECKS[scope]):
        raise DocumentError("Certificate check coverage is incomplete or duplicated")
    for item in matching:
        evidence = load_document("certification_check_evidence", resolve_ref(root, item["evidence"]), reference_root=root)
        expected = {"purpose": "native_runtime", "inventory_format": source["inventory_format"], "check_id": item["check_id"], "scope": item["scope"],
            "source_sha256": source["source_sha256"], "profile_projection_sha256": projection_hash,
            "numerical_values_sha256": values_hash, "cache_policy_id": cache["policy_id"], "method": METHODS[item["check_id"]], "status": "passed", "illustrative_only": False}
        if item["status"] != "passed" or any(evidence[key] != value for key, value in expected.items()):
            raise DocumentError("Check evidence is failed, illustrative or bound to another subject")
        for report in evidence["raw_reports"]:
            from .qualification_evidence import verify_raw_report
            verify_raw_report(resolve_ref(root, report).read_bytes(), evidence)


def production_resolver(root: Path, profile: dict, scope: str) -> VerifiedExecutionProfile:
    source, _, _ = loaded_source()
    return verify_certification(root, profile, source, scope)


def _candidate_resolver(root: Path, profile: dict, scope: str) -> VerifiedExecutionProfile:
    """Only tools/qualification calls this private entry; no public CLI switch."""
    source, _, _ = loaded_source()
    if profile["certification"] != {"status": "qualifying", "evidence": None}:
        raise DocumentError("Qualification requires an explicit qualifying candidate profile")
    if scope == "series_linux_recovery" and platform_family() != "linux":
        raise DocumentError("Linux recovery qualification cannot be asserted on another platform")
    resolve_ref(root, profile["environment_lock"])
    return VerifiedExecutionProfile(profile, verify_environment(profile), source, scope, "qualification")
