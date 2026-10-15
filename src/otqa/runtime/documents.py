"""Strict native readers, reference closure and deterministic materialization."""
from __future__ import annotations

import copy
import os
import stat
from pathlib import Path
from uuid import uuid4

from .codec import DocumentError, canonical_digest, decode, digest, encode, float_projection, utc_now
from .project import ProjectContext, portable_path
from .schema import validate
from .storage import publish_bytes, publish_json


class VerifiedArtifactPath(type(Path())):
    """A path carrying the immutable bytes that actually passed hash verification.

    Path consumers keep their normal interface. read_bytes() returns the bound
    snapshot, preventing a second unverified read after reference admission.
    """
    def __new__(cls, *paths, verified_bytes=None):
        instance = super().__new__(cls, *paths)
        instance._verified_bytes = verified_bytes
        return instance

    def __init__(self, *paths, verified_bytes=None):
        super().__init__(*paths)

    def read_bytes(self):
        return self._verified_bytes if self._verified_bytes is not None else super().read_bytes()


def file_ref(path: Path, root: Path) -> dict:
    relative = path.absolute().relative_to(root.absolute()).as_posix()
    portable_path(relative)
    return {"path": relative, "sha256": digest(path.read_bytes())}


def resolve_ref(root: Path, reference: dict) -> Path:
    if set(reference) != {"path", "sha256"}:
        raise DocumentError("A FileRef has exactly path and sha256")
    relative = portable_path(reference["path"])
    base = Path(root).resolve(strict=True)
    path = (base / relative).resolve(strict=True)
    try:
        path.relative_to(base)
    except ValueError as exc:
        raise DocumentError("Reference escapes its explicit root") from exc
    descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    try:
        if not stat.S_ISREG(os.fstat(descriptor).st_mode):
            raise DocumentError("Referenced artifact is not a regular file")
        chunks = []
        while chunk := os.read(descriptor, 1024 * 1024):
            chunks.append(chunk)
        data = b"".join(chunks)
    finally:
        os.close(descriptor)
    if digest(data) != reference["sha256"]:
        raise DocumentError(f"Artifact hash differs: {relative}")
    return VerifiedArtifactPath(path, verified_bytes=data)


def _entry(path: Path, root: Path) -> Path:
    resolved = Path(path).resolve(strict=True)
    try:
        resolved.relative_to(Path(root).resolve(strict=True))
    except ValueError as exc:
        raise DocumentError("Entry lies outside the explicit source root") from exc
    if not resolved.is_file():
        raise DocumentError("Document entry is not a regular file")
    return resolved


def load_document(kind: str, path: Path, *, reference_root: Path, _bytes: bytes | None = None) -> dict:
    _entry(path, reference_root)
    document = validate(kind, decode(path.read_bytes() if _bytes is None else _bytes))
    if kind == "problem":
        m, n = len(document["alternative_ids"]), len(document["objective_ids"])
        if len(document["alternatives"]) != m or any(len(row) != n for row in document["alternatives"]):
            raise DocumentError("Problem IDs and rectangular matrix dimensions differ")
    elif kind == "oracle":
        if sum(document["target_weights"]) <= 0:
            raise DocumentError("Oracle weights need a positive finite sum")
        if not _finite_sum(document["target_weights"]):
            raise DocumentError("Oracle weight sum is not finite")
    elif kind == "answer_history":
        for answer in document["answers"]:
            if answer["goal_index_a"] == answer["goal_index_b"]:
                raise DocumentError("Query objectives must be distinct")
    elif kind == "dataset":
        _unique([case["case_id"] for case in document["cases"]], "case IDs")
    elif kind == "suite":
        configs = [item["configuration_id"] for item in document["configurations"]]
        selected = [item["configuration_id"] for item in document["selection"]]
        _unique(configs, "configuration IDs")
        _unique(selected, "selection IDs")
        if set(configs) != set(selected):
            raise DocumentError("Suite selection must explicitly cover each configuration exactly once")
    return document


def _finite_sum(values):
    import math
    return math.isfinite(sum(values))


def _unique(values, name):
    if len(values) != len(set(values)):
        raise DocumentError(f"Duplicate {name}")


def typed_projection(kind: str, document: dict) -> dict:
    """Bind consumed binary64 fields, preserving indices, counts and metadata."""
    value = copy.deepcopy(document)
    if kind == "problem":
        value["alternatives"] = [[float(item) for item in row] for row in value["alternatives"]]
    elif kind == "oracle":
        value["target_weights"] = [float(item) for item in value["target_weights"]]
    elif kind == "answer_history":
        for answer in value["answers"]:
            answer["value"] = float(answer["value"])
    elif kind == "config":
        stopping = value["algorithm"]["stopping"]
        if stopping["rule"] == "volume_confidence":
            stopping["threshold"] = float(stopping["threshold"])
    return value


def load_problem(path: Path, *, reference_root: Path) -> dict:
    return load_document("problem", path, reference_root=reference_root)


def load_config_document(path: Path, *, reference_root: Path) -> dict:
    return load_document("config", path, reference_root=reference_root)


def load_execution_profile(path: Path, *, reference_root: Path) -> dict:
    return load_document("execution_profile", path, reference_root=reference_root)


def load_oracle(path: Path, problem: dict, *, reference_root: Path) -> dict:
    data = load_document("oracle", path, reference_root=reference_root)
    if data["problem_id"] != problem["problem_id"] or len(data["target_weights"]) != len(problem["objective_ids"]):
        raise DocumentError("Oracle does not bind this problem/dimension")
    return data


def load_answer_history(path: Path, problem: dict, *, reference_root: Path) -> dict:
    data = load_document("answer_history", path, reference_root=reference_root)
    if data["problem_id"] != problem["problem_id"]:
        raise DocumentError("Answer history belongs to a different problem")
    count = len(problem["objective_ids"])
    if any(answer["goal_index_a"] >= count or answer["goal_index_b"] >= count for answer in data["answers"]):
        raise DocumentError("Answer history query index exceeds problem dimension")
    return data


def references(kind: str, document: dict):
    """Only declared FileRef positions are edges; arbitrary metadata is inert."""
    if kind == "dataset":
        for index, case in enumerate(document["cases"]):
            for key in ("problem", "oracle"):
                yield f"/cases/{index}/{key}", key, case[key]
    elif kind == "suite":
        yield "/dataset", "dataset", document["dataset"]
        for index, config in enumerate(document["configurations"]):
            yield f"/configurations/{index}", "config", {key: config[key] for key in ("path", "sha256")}
    elif kind == "execution_profile":
        yield "/environment_lock", "environment_lock", document["environment_lock"]
        if document["certification"]["evidence"] is not None:
            yield "/certification/evidence", "certification", document["certification"]["evidence"]
    elif kind == "certification":
        yield "/environment_lock", "environment_lock", document["environment_lock"]
        for index, check in enumerate(document["checks"]):
            yield f"/checks/{index}/evidence", "certification_check_evidence", check["evidence"]
    elif kind == "certification_check_evidence":
        for index, report in enumerate(document["raw_reports"]):
            yield f"/raw_reports/{index}", "raw_report", report


def _at(document, pointer):
    current = document
    for component in pointer.split("/")[1:]:
        component = component.replace("~1", "/").replace("~0", "~")
        current = current[int(component)] if isinstance(current, list) else current[component]
    return current


def verified_closure(source_root: Path, entries: dict[str, tuple[str, Path]]) -> dict:
    root = Path(source_root).resolve(strict=True)
    closure, visiting = {}, set()

    def visit(kind, path):
        resolved = _entry(path, root)
        relative = resolved.relative_to(root).as_posix()
        if relative in visiting:
            raise DocumentError("Cyclic input reference closure")
        if relative in closure:
            if closure[relative]["kind"] != kind:
                raise DocumentError("One artifact has conflicting document kinds")
            return
        visiting.add(relative)
        data = path.read_bytes()
        document = None if kind in ("environment_lock", "raw_report") else load_document(kind, resolved, reference_root=root, _bytes=data)
        edges = list(references(kind, document)) if document is not None else []
        for _, target_kind, ref in edges:
            visit(target_kind, resolve_ref(root, ref))
        closure[relative] = {"kind": kind, "bytes": data, "document": document, "edges": edges}
        visiting.remove(relative)

    for kind, path in entries.values():
        visit(kind, path)
    return closure


def materialize_inputs(source_root: Path, entries: dict[str, tuple[str, Path]], target_root: Path,
                       *, context: ProjectContext) -> dict:
    """Verify the entire DAG before writing and rewrite refs in dependency order."""
    root = Path(source_root).resolve(strict=True)
    closure = verified_closure(root, entries)
    mapped, receipts = {}, []
    for relative, node in closure.items():
        original = target_root / "provenance" / "original" / relative
        native = target_root / "inputs" / relative
        publish_bytes(context, original, node["bytes"])
        rewritten = copy.deepcopy(node["document"])
        semantic = typed_projection(node["kind"], node["document"]) if node["document"] is not None else None
        mapping = []
        for pointer, _, old_ref in node["edges"]:
            source_path = resolve_ref(root, old_ref).relative_to(root).as_posix()
            replacement = mapped[source_path]
            target = _at(rewritten, pointer)
            target.update(replacement)
            original_target = _at(semantic, pointer)
            original_target.pop("path")
            original_target.pop("sha256")
            original_target["source_artifact_sha256"] = old_ref["sha256"]
            mapping.append({"json_pointer": pointer, "source_path": source_path, "materialized_path": replacement["path"]})
        data = encode(rewritten) if node["edges"] else node["bytes"]
        publish_bytes(context, native, data)
        native_ref = file_ref(native, target_root)
        mapped[relative] = native_ref
        semantic_hash = digest(node["bytes"]) if semantic is None else canonical_digest(float_projection(semantic))
        receipts.append({"document_kind": "blob" if node["kind"] in ("environment_lock", "raw_report") else node["kind"], "source_relative_path": relative,
            "original": file_ref(original, target_root), "materialized": native_ref,
            "transformation": "reference_rewrite" if node["edges"] else "byte_copy", "semantic_sha256": semantic_hash, "reference_map": mapping})
    receipt = {"schema_version": 1, "materialization_id": str(uuid4()), "created_at_utc": utc_now(),
        "entrypoints": {key: mapped[_entry(path, root).relative_to(root).as_posix()] for key, (_, path) in entries.items()}, "entries": receipts}
    publish_json(context, target_root / "materialization_receipt.json", receipt, kind="materialization_receipt")
    return receipt
