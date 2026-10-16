"""Explicit byte-identical portable archives of quiescent terminal series.

An inventory is the final commit marker. Its verification checks an offline
snapshot, not permission to execute/resume it under another project binding.
"""
from __future__ import annotations

import fcntl
import hashlib
import os
from pathlib import Path
import stat
from uuid import uuid4

from otqa.runtime.codec import DocumentError, canonical_digest, decode, digest, encode, utc_now
from otqa.runtime.processes import group_status, identity_status
from otqa.runtime.ownership import verified_process_chain
from otqa.runtime.project import ProjectContext, bound_directory, portable_path, verify_binding
from otqa.runtime.schema import all_validators, versioned_definitions, validate
from otqa.runtime.validation import verify_result

_INVENTORY = "archive_inventory.json"
_CHUNK = 1024 * 1024


def _stamp(info):
    return info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns, info.st_ctime_ns


def _directory(parent, name):
    return os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent)


def _walk(directory, prefix="", *, excluded=None):
    """No symlinks/special files; return payload paths and bound object stamps."""
    files, directories = {}, set()
    for name in sorted(os.listdir(directory)):
        relative = prefix + name
        portable_path(relative)
        if relative == excluded or (excluded and relative.startswith(excluded + "/")):
            continue
        info = os.stat(name, dir_fd=directory, follow_symlinks=False)
        if stat.S_ISDIR(info.st_mode):
            following = _directory(directory, name)
            try:
                if _stamp(os.fstat(following)) != _stamp(info):
                    raise DocumentError("Archive directory changed while binding it")
                children, descendants = _walk(following, relative + "/", excluded=excluded)
                files.update(children)
                directories.add(relative)
                directories.update(descendants)
            finally:
                os.close(following)
        elif stat.S_ISREG(info.st_mode):
            files[relative] = _stamp(info)
        else:
            raise DocumentError(f"Archive payload is a symlink or special file: {relative}")
    return files, directories


def _parent(directory, relative, *, create=False):
    parts = portable_path(relative).split("/")
    current = os.dup(directory)
    try:
        for name in parts[:-1]:
            if create:
                try:
                    os.mkdir(name, mode=0o755, dir_fd=current)
                    os.fsync(current)
                except FileExistsError:
                    pass
            following = _directory(current, name)
            os.close(current)
            current = following
        return current, parts[-1]
    except BaseException:
        os.close(current)
        raise


def _read(directory, relative, *, destination=None, expected=None, collect=True):
    """Read one bound file once; optionally copy to a bound destination fd."""
    parent, name = _parent(directory, relative)
    source = None
    try:
        source = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=parent)
        before = os.fstat(source)
        if not stat.S_ISREG(before.st_mode) or (expected is not None and _stamp(before) != expected):
            raise DocumentError(f"Archive source changed or is not a regular file: {relative}")
        checksum = hashlib.sha256()
        chunks, count = [], 0
        while chunk := os.read(source, _CHUNK):
            checksum.update(chunk)
            count += len(chunk)
            if destination is not None:
                _write(destination, chunk)
            elif collect:
                chunks.append(chunk)
        after = os.fstat(source)
        linked = os.stat(name, dir_fd=parent, follow_symlinks=False)
        if _stamp(before) != _stamp(after) or _stamp(before) != _stamp(linked) or count != before.st_size:
            raise DocumentError(f"Archive source changed while being read: {relative}")
        return b"".join(chunks) if destination is None and collect else None, count, checksum.hexdigest()
    finally:
        if source is not None:
            os.close(source)
        os.close(parent)


def _write(descriptor, data):
    view = memoryview(data)
    while view:
        count = os.write(descriptor, view)
        if count <= 0:
            raise OSError("Short archive write")
        view = view[count:]


def _document(directory, path, kind):
    raw, _, _ = _read(directory, path)
    return validate(kind, decode(raw)), raw


def _reference(directory, reference):
    if set(reference) != {"path", "sha256"}:
        raise DocumentError("Archive reference requires exactly path and sha256")
    _payload_reference(reference)
    raw, _, checksum = _read(directory, reference["path"])
    if checksum != reference["sha256"]:
        raise DocumentError("Archive reference bytes differ from their bound hash")
    return raw


def _payload_reference(reference):
    relative = portable_path(reference["path"])
    if relative.split("/", 1)[0] == "seals":
        raise DocumentError("Native artifact reference points into excluded seals/ archives")


def _declared_references(schema, value, common):
    """Follow declared schema edges, never arbitrary free metadata objects."""
    if "$ref" in schema:
        ref = schema['$ref']
        name = ref.rsplit('/', 1)[-1]
        version = int(ref.split(':v', 1)[1].split(':', 1)[0])
        common, _ = versioned_definitions(version)
        if name in {"FileRef", "JournalProof"}:
            if isinstance(value, dict):
                yield value
            return
        yield from _declared_references(common[name], value, common)
    for keyword in ("oneOf", "anyOf", "allOf"):
        for child in schema.get(keyword, ()):
            yield from _declared_references(child, value, common)
    if isinstance(value, dict):
        for name, child in schema.get("properties", {}).items():
            if name in value:
                if name == "journal_path":
                    yield {"path": value[name]}
                else:
                    yield from _declared_references(child, value[name], common)
        additional = schema.get("additionalProperties")
        if isinstance(additional, dict):
            declared = schema.get("properties", {})
            for name, child in value.items():
                if name not in declared:
                    yield from _declared_references(additional, child, common)
    elif isinstance(value, list) and "items" in schema:
        for child in value:
            yield from _declared_references(schema["items"], child, common)


def _check_native_references(directory, snapshots):
    validators = all_validators()
    for relative, stamp in snapshots.items():
        # Original input provenance retains its former source-root addresses;
        # those documents are bytes, not native SeriesRoot reference edges.
        if not relative.endswith(".json") or relative.startswith("provenance/original/"):
            continue
        raw, _, _ = _read(directory, relative, expected=stamp)
        try:
            document = decode(raw)
        except DocumentError:
            continue  # Unrelated JSON-named blobs are still archived byte-for-byte.
        if not isinstance(document, dict) or type(document.get('schema_version')) is not int:
            continue
        for (kind, version), validator in validators.items():
            if version != document['schema_version']:
                continue
            if validator.is_valid(document):
                common, schemas = versioned_definitions(version)
                if kind == 'continuation':
                    from otqa.runtime.schema_v2 import continuation_schema
                    schema = continuation_schema()
                else:
                    schema = schemas[kind]
                for reference in _declared_references(schema, document, common):
                    _payload_reference(reference)
                break


def _terminal(directory, context, root):
    plan, plan_bytes = _document(directory, "plan.json", "series_plan")
    state, _ = _document(directory, "state.json", "series_state")
    verify_binding(context, root, plan["project_binding"])
    if state["series_id"] != plan["series_id"] or state["plan_sha256"] != digest(plan_bytes):
        raise DocumentError("Archive state does not bind this series plan")
    if state["status"] not in {"completed", "completed_with_failures"} or state["active_job_id"] is not None:
        raise DocumentError("Only terminal complete series can be sealed")
    if state["controller"] is not None and identity_status(state["controller"]) != "dead":
        raise DocumentError("Archive controller is alive or cannot be proven ended")
    if [job["job_id"] for job in state["jobs"]] != [job["job_id"] for job in plan["jobs"]]:
        raise DocumentError("Archive state omitted, added or reordered a planned job")
    for job, planned in zip(state["jobs"], plan["jobs"], strict=True):
        if job["status"] not in {"completed", "failed", "interrupted"} or not job["attempts"]:
            raise DocumentError("Archive contains unfinished jobs")
        for attempt in job["attempts"]:
            if attempt["execution_status"] not in {"completed", "failed", "interrupted"} or attempt["result"] is None:
                raise DocumentError("Archive contains an unfinished attempt")
            identities = {"series_id": plan["series_id"], "job_id": job["job_id"],
                "run_id": attempt["run_id"], "attempt_id": attempt["attempt_id"],
                "problem_id": planned["problem_id"], "configuration_id": planned["configuration_id"]}
            process, _, _ = verified_process_chain(root, root / attempt["directory"], identities=identities,
                intent_ref=attempt["launch_intent"], registration_ref=attempt["child_registration"],
                grant_ref=attempt["start_grant"], recorded_process=attempt["process"])
            if process is None or group_status(process) != "dead":
                raise DocumentError("Archive solver group is alive or cannot be proven ended")
            result = validate("result", decode(_reference(directory, attempt["result"])))
            result_path = root / attempt["result"]["path"]
            if result_path.parent != root / attempt["directory"]:
                raise DocumentError("Archive result is outside its reserved attempt directory")
            verified = verify_result(
                result_path, root,
                {**identities, "source": plan["source"], "project_binding": plan["project_binding"]},
            )
            if verified != result:
                raise DocumentError("Archive result changed after its verified byte snapshot")
            _reference(directory, attempt["result"])
            if any(result[key] != value for key, value in {
                "run_id": attempt["run_id"], "attempt_id": attempt["attempt_id"],
                "problem_id": planned["problem_id"], "configuration_id": planned["configuration_id"],
                "execution_status": attempt["execution_status"],
            }.items()):
                raise DocumentError("Archive attempt result identity/status differs")
        if job["attempts"][-1]["execution_status"] != job["status"]:
            raise DocumentError("Archive job differs from its final attempt")
    failed = any(job["status"] in {"failed", "interrupted"} for job in state["jobs"])
    if state["status"] != ("completed_with_failures" if failed else "completed"):
        raise DocumentError("Archive series status differs from its terminal jobs")
    for relative, checksum in plan["frozen_files"].items():
        _reference(directory, {"path": relative, "sha256": checksum})
    return plan["series_id"]


def _assert_binding(context, path, descriptor):
    with bound_directory(context, path) as current:
        actual, expected = os.fstat(current), os.fstat(descriptor)
        if (actual.st_dev, actual.st_ino) != (expected.st_dev, expected.st_ino):
            raise DocumentError("Archive directory binding changed during publication")


def _copy(source, destination, relative, stamp):
    parent, name = _parent(destination, relative, create=True)
    descriptor = None
    try:
        descriptor = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o644, dir_fd=parent)
        _, count, checksum = _read(source, relative, destination=descriptor, expected=stamp)
        os.fsync(descriptor)
        os.fsync(parent)
        return {"path": relative, "bytes": count, "sha256": checksum}
    finally:
        if descriptor is not None:
            os.close(descriptor)
        os.close(parent)


def _commit(directory, document):
    temporary = ".inventory-" + uuid4().hex + ".tmp"
    descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o644, dir_fd=directory)
    try:
        _write(descriptor, encode(document))
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
    linked = False
    try:
        os.link(temporary, _INVENTORY, src_dir_fd=directory, dst_dir_fd=directory, follow_symlinks=False)
        linked = True
        os.unlink(temporary, dir_fd=directory)
        os.fsync(directory)
    except BaseException:
        if linked:
            os.unlink(_INVENTORY, dir_fd=directory)
        try:
            os.unlink(temporary, dir_fd=directory)
        except FileNotFoundError:
            pass
        raise


def seal_inventory(context: ProjectContext, reference_root: Path, output_path: Path) -> dict:
    """Copy a terminal series to a new bundle; return its inventory FileRef.

    output_path is <new-bundle>/archive_inventory.json under ProjectRoot/runs.
    A failed operation leaves an uncommitted directory and never overwrites it.
    """
    root, output = Path(os.path.abspath(reference_root)), Path(os.path.abspath(output_path))
    context.binding(root)
    context.relative_output(output)
    if output.name != _INVENTORY:
        raise DocumentError("Seal output must be <new-bundle>/archive_inventory.json")
    bundle = output.parent
    if root == bundle or root.is_relative_to(bundle):
        raise DocumentError("Seal destination must not contain or equal the source series")
    if bundle.is_relative_to(root):
        relative = bundle.relative_to(root)
        if len(relative.parts) < 2 or relative.parts[0] != "seals":
            raise DocumentError("An in-series seal belongs below the reserved seals/ namespace")
    excluded = "seals"
    with bound_directory(context, root) as source:
        lock = os.open("controller.lock", os.O_RDWR | os.O_NOFOLLOW, dir_fd=source)
        try:
            if not stat.S_ISREG(os.fstat(lock).st_mode):
                raise DocumentError("Controller lock is not a regular file")
            try:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError as exc:
                raise DocumentError("A controller currently owns this series") from exc
            series_id = _terminal(source, context, root)
            snapshots, _ = _walk(source, excluded=excluded)
            snapshots.pop(_INVENTORY, None)
            _check_native_references(source, snapshots)
            with bound_directory(context, bundle.parent, create=True) as parent:
                try:
                    os.mkdir(bundle.name, mode=0o755, dir_fd=parent)
                except FileExistsError as exc:
                    raise DocumentError("Seal bundle output already exists") from exc
                os.fsync(parent)
                destination = _directory(parent, bundle.name)
                try:
                    files = [_copy(source, destination, relative, stamp) for relative, stamp in sorted(snapshots.items())]
                    observed, _ = _walk(source, excluded=excluded)
                    observed.pop(_INVENTORY, None)
                    if observed != snapshots:
                        raise DocumentError("Series changed during seal creation")
                    if _terminal(source, context, root) != series_id:
                        raise DocumentError("Series identity changed during seal creation")
                    document = validate("archive_inventory", {"schema_version": 1, "series_id": series_id,
                        "created_at_utc": utc_now(), "inventory_sha256": canonical_digest(files), "files": files})
                    _verify_payload(destination, document)
                    _assert_binding(context, root, source)
                    _assert_binding(context, bundle, destination)
                    _commit(destination, document)
                    return {"path": _INVENTORY, "sha256": digest(encode(document))}
                finally:
                    os.close(destination)
        finally:
            os.close(lock)


def _verify_payload(directory, inventory):
    files = inventory["files"]
    paths = [portable_path(entry["path"]) for entry in files]
    if paths != sorted(set(paths)) or _INVENTORY in paths:
        raise DocumentError("Archive paths must be unique, sorted and exclude the inventory")
    if canonical_digest(files) != inventory["inventory_sha256"]:
        raise DocumentError("Archive canonical inventory digest differs")
    present, directories = _walk(directory)
    present.pop(_INVENTORY, None)
    if set(present) != set(paths):
        raise DocumentError("Archive has missing or extra payload files")
    expected_directories = {str(parent) for value in paths for parent in Path(value).parents if str(parent) != "."}
    if directories != expected_directories:
        raise DocumentError("Archive has missing or extra payload directories")
    for entry in files:
        _, size, checksum = _read(directory, entry["path"], expected=present[entry["path"]], collect=False)
        if size != entry["bytes"] or checksum != entry["sha256"]:
            raise DocumentError(f"Archive payload bytes differ: {entry['path']}")
    observed, _ = _walk(directory)
    observed.pop(_INVENTORY, None)
    if observed != present:
        raise DocumentError("Archive changed during verification")


def verify_seal(bundle_root: Path, *, inventory_ref: dict | None = None) -> dict:
    """Verify offline whole-bundle integrity; grants no execution permission."""
    root = Path(os.path.abspath(bundle_root))
    descriptor = os.open(root.anchor, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        for component in root.parts[1:]:
            following = _directory(descriptor, component)
            os.close(descriptor)
            descriptor = following
        inventory, inventory_bytes = _document(descriptor, _INVENTORY, "archive_inventory")
        if inventory_ref is not None and inventory_ref != {"path": _INVENTORY, "sha256": digest(inventory_bytes)}:
            raise DocumentError("Archive inventory differs from its external FileRef")
        _verify_payload(descriptor, inventory)
        current, _, _ = _read(descriptor, _INVENTORY)
        if current != inventory_bytes:
            raise DocumentError("Archive inventory changed during verification")
        return inventory
    finally:
        os.close(descriptor)


seal_series = seal_inventory
