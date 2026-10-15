import pytest

from otqa.runtime.codec import DocumentError, encode
from otqa.runtime.qualification_evidence import METHOD_CASES, verify_raw_report


def report_and_evidence():
    subject = {"purpose": "native_runtime", "method": "installed-wheel-v1", "check_id": "installation", "scope": "sdk", "inventory_format": "otqa-source-v1",
        "source_sha256": "a" * 64, "profile_projection_sha256": "b" * 64, "numerical_values_sha256": "c" * 64, "cache_policy_id": "bounded_v1"}
    report = {"schema_version": 1, **subject, "started_at_utc": "2026-10-15T00:00:00Z", "finished_at_utc": "2026-10-15T00:00:01Z",
        "observations": [{"case_id": case, "expected": True, "observed": True, "passed": True, "details": {"constructed_format_control": True}} for case in METHOD_CASES["installation"]],
        "status": "passed", "harness_sha256": "d" * 64}
    return report, subject


def test_known_complete_method_report_has_a_structural_reader():
    report, evidence = report_and_evidence()
    assert verify_raw_report(encode(report), evidence) == report


@pytest.mark.parametrize("mutation", ["missing_case", "failed_observation", "boolean_as_integer", "wrong_subject", "opaque_report", "missing_details"])
def test_arbitrary_existing_raw_bytes_are_not_qualification(mutation):
    report, evidence = report_and_evidence()
    if mutation == "missing_case":
        report["observations"].pop()
    elif mutation == "failed_observation":
        report["observations"][0]["observed"] = False
    elif mutation == "boolean_as_integer":
        report["schema_version"] = True
    elif mutation == "wrong_subject":
        report["source_sha256"] = "e" * 64
    elif mutation == "opaque_report":
        report = {"status": "passed"}
    else:
        report["observations"][0]["details"] = {}
    with pytest.raises(DocumentError):
        verify_raw_report(encode(report), evidence)


def test_qualifier_binds_actual_active_jsonschema_dependency_closure():
    from tools.qualification.qualify import PRODUCTION_PACKAGES, production_dependency_versions
    import importlib.metadata
    versions = production_dependency_versions()
    assert set(versions) == set(PRODUCTION_PACKAGES)
    assert {'attrs', 'jsonschema-specifications', 'referencing', 'rpds-py'}.issubset(versions)
    assert versions == {name: importlib.metadata.version(name) for name in PRODUCTION_PACKAGES}


def test_qualifier_rejects_an_unbound_new_active_dependency(monkeypatch):
    import tools.qualification.qualify as module
    from types import SimpleNamespace
    original = module.importlib.metadata.distribution
    def distribution(name):
        value = original(name)
        if name == 'jsonschema':
            return SimpleNamespace(requires=[*(value.requires or ()), 'unbound-validator-helper>=1'])
        return value
    monkeypatch.setattr(module.importlib.metadata, 'distribution', distribution)
    with pytest.raises(RuntimeError, match='Unbound active production dependency'):
        module.production_dependency_versions()
