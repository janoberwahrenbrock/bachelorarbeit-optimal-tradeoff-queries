"""Explicit project roots and directory-handle-bound output operations."""
from __future__ import annotations

import os
import re
import stat
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Iterator
from uuid import UUID

from .codec import DocumentError, read_json


def portable_path(value: str) -> str:
    if not isinstance(value, str) or not value or "\\" in value or ":" in value:
        raise DocumentError("Expected a portable relative path")
    if any(ord(char) < 32 or ord(char) == 127 for char in value):
        raise DocumentError("Control character in path")
    parts = value.split("/")
    if any(part in ("", ".", "..") for part in parts):
        raise DocumentError("Empty, dot or parent path segment")
    if PurePosixPath(value).is_absolute():
        raise DocumentError("Absolute internal path")
    return value


def identifier(value: str) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}", value):
        raise DocumentError("Invalid identifier")
    return value


@dataclass(frozen=True)
class ProjectContext:
    project_root: Path
    project_id: UUID

    def __post_init__(self):
        root = Path(self.project_root)
        if not root.is_absolute() or root != root.resolve(strict=True) or not root.is_dir():
            raise DocumentError("ProjectContext requires an absolute resolved real directory")
        if not isinstance(self.project_id, UUID):
            raise DocumentError("ProjectContext requires a UUID project identity")
        marker = root / "otqa-project.json"
        if marker.is_symlink():
            raise DocumentError("Project marker must not be a symlink")
        value = read_json(marker)
        expected = {"schema_version": 1, "project_kind": "otqa_project", "project_id": str(self.project_id)}
        if value != expected or type(value.get("schema_version")) is not int:
            raise DocumentError("ProjectContext identity differs from its explicit project marker")

    def binding(self, bundle_root: Path) -> dict:
        path = self.relative_output(bundle_root, namespace="runs")
        if len(path.parts) < 2:
            raise DocumentError("A bundle must be below runs/")
        return {"project_id": str(self.project_id), "relative_root": path.as_posix()}

    def relative_output(self, path: Path, *, namespace: str = "runs") -> Path:
        absolute = Path(os.path.abspath(path))
        try:
            relative = absolute.relative_to(self.project_root)
        except ValueError as exc:
            raise DocumentError("Output must remain inside the explicit project root") from exc
        if not relative.parts or relative.parts[0] != namespace:
            raise DocumentError(f"Output must be inside ProjectRoot/{namespace}/")
        current = self.project_root
        for part in relative.parts:
            if part in ("", ".", ".."):
                raise DocumentError("Invalid output component")
            current = current / part
            try:
                mode = current.lstat().st_mode
            except FileNotFoundError:
                continue
            if stat.S_ISLNK(mode):
                raise DocumentError("Symlink in output chain")
            if current != absolute and not stat.S_ISDIR(mode):
                raise DocumentError("Output ancestor is not a directory")
        return relative


def load_project_context(project_root: Path) -> ProjectContext:
    root = Path(project_root).resolve(strict=True)
    if not root.is_dir():
        raise DocumentError("Project root is not a directory")
    marker = root / "otqa-project.json"
    if marker.is_symlink():
        raise DocumentError("Project marker must not be a symlink")
    data = read_json(marker)
    if not isinstance(data, dict) or set(data) != {"schema_version", "project_kind", "project_id"}:
        raise DocumentError("Invalid project marker fields")
    if type(data["schema_version"]) is not int or data["schema_version"] != 1 or data["project_kind"] != "otqa_project":
        raise DocumentError("Unsupported project marker")
    try:
        project_id = UUID(data["project_id"])
    except (ValueError, TypeError, AttributeError) as exc:
        raise DocumentError("Invalid project UUID") from exc
    return ProjectContext(root, project_id)


def verify_binding(context: ProjectContext, root: Path, binding: dict) -> None:
    if context.binding(root) != binding:
        raise DocumentError("Project marker or bundle-relative binding differs")


@contextmanager
def bound_directory(context: ProjectContext, path: Path, *, create: bool = False,
                    namespace: str = "runs") -> Iterator[int]:
    """Walk with openat/O_NOFOLLOW; an ancestor swap cannot redirect writes."""
    relative = context.relative_output(path, namespace=namespace)
    if not hasattr(os, "O_NOFOLLOW") or os.open not in os.supports_dir_fd:
        raise DocumentError("This platform lacks the required no-follow directory adapter")
    descriptor = os.open(context.project_root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        for component in relative.parts:
            if create:
                try:
                    os.mkdir(component, mode=0o755, dir_fd=descriptor)
                    os.fsync(descriptor)
                except FileExistsError:
                    pass
            following = os.open(component, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                                dir_fd=descriptor)
            os.close(descriptor)
            descriptor = following
    except OSError as exc:
        os.close(descriptor)
        raise DocumentError(f"Cannot bind output directory: {exc}") from exc
    try:
        yield descriptor
    finally:
        os.close(descriptor)
