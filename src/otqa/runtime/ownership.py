"""Verify the durable launch chain before trusting a recorded process group."""
import os
from pathlib import Path
import stat

from .codec import DocumentError, digest
from .documents import load_document
from .project import portable_path


def _artifact(root, path, kind, expected=None):
    """Bind validation and hash to the same immutable byte snapshot."""
    relative = portable_path(path.relative_to(root).as_posix())
    if expected is not None and expected["path"] != relative:
        raise DocumentError("Launch artifact points outside its reserved attempt")
    descriptor = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        for part in Path(relative).parts[:-1]:
            following = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=descriptor)
            os.close(descriptor)
            descriptor = following
        file_descriptor = os.open(Path(relative).name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=descriptor)
        try:
            if not stat.S_ISREG(os.fstat(file_descriptor).st_mode):
                raise DocumentError("Launch artifact is not a regular file")
            with os.fdopen(file_descriptor, "rb", closefd=False) as stream:
                data = stream.read()
        finally:
            os.close(file_descriptor)
    finally:
        os.close(descriptor)
    reference = {"path": relative, "sha256": digest(data)}
    if expected is not None and reference != expected:
        raise DocumentError("Launch artifact bytes differ from their durable reference")
    return load_document(kind, path, reference_root=root, _bytes=data), reference


def verified_process_chain(root: Path, directory: Path, *, identities: dict,
                           intent_ref: dict | None, registration_ref: dict | None,
                           grant_ref: dict | None, recorded_process: dict | None,
                           running: bool = False) -> tuple[dict | None, dict | None, dict | None]:
    """Return only identity/refs proven by Intent -> Registration -> Grant.

    A missing registration preserves the uncertain spawn gap. A mutable status
    field alone is never authority for which process group ended.
    """
    if intent_ref is None:
        raise DocumentError("Reserved attempt has no durable launch intent")
    intent, actual_intent = _artifact(root, directory / "launch_intent.json", "launch_intent", intent_ref)
    for key in ("run_id", "attempt_id", "series_id", "job_id", "problem_id", "configuration_id"):
        if intent[key] != identities[key]:
            raise DocumentError("Launch intent belongs to another reserved attempt")
    if intent["controller"]["owner_token"] != intent["owner_token"]:
        raise DocumentError("Intent controller and owner token differ")
    registration_path = directory / "child_registration.json"
    if not registration_path.exists():
        if (registration_ref is not None or recorded_process is not None or grant_ref is not None or running
                or (directory / "start_grant.json").exists() or (directory / "manifest.json").exists()):
            raise DocumentError("Recorded launch phase lacks its immutable registration")
        return None, None, None
    registration, actual_registration = _artifact(root, registration_path, "child_registration", registration_ref)
    if (registration["run_id"] != identities["run_id"] or registration["attempt_id"] != identities["attempt_id"]
            or registration["intent"] != actual_intent or registration["nonce"] != intent["nonce"]):
        raise DocumentError("Child registration is not bound to this intent and attempt")
    identity = registration["process"]
    if identity["owner_token"] != intent["owner_token"] or identity["pid"] != identity["pgid"] or identity["pid"] != identity["sid"]:
        raise DocumentError("Child identity is not its reserved owner's isolated group")
    if recorded_process is not None and recorded_process != identity:
        raise DocumentError("Mutable controller process differs from immutable registration")
    actual_grant = None
    grant_path = directory / "start_grant.json"
    if grant_path.exists():
        grant, actual_grant = _artifact(root, grant_path, "start_grant", grant_ref)
        if (grant["run_id"] != identities["run_id"] or grant["attempt_id"] != identities["attempt_id"]
                or grant["nonce"] != intent["nonce"] or grant["intent"] != actual_intent
                or grant["registration"] != actual_registration or grant["process"] != identity):
            raise DocumentError("Start grant differs from the reserved registered child")
    elif grant_ref is not None or running:
        raise DocumentError("A granted/running attempt lacks its immutable start grant")
    manifest_path = directory / "manifest.json"
    if manifest_path.exists():
        manifest, _ = _artifact(root, manifest_path, "manifest")
        if actual_grant is None or manifest["process"] != identity or manifest["launch_intent"] != actual_intent:
            raise DocumentError("Solver manifest is not bound to its granted process")
        for key in identities:
            if manifest[key] != identities[key]:
                raise DocumentError("Solver manifest belongs to another reserved attempt")
    return identity, actual_registration, actual_grant
