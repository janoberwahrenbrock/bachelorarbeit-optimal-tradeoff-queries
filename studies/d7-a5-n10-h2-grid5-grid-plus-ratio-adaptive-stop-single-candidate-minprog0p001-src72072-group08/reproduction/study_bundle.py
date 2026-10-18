#!/usr/bin/env python3
"""Build and verify immutable study downloads without importing the algorithm.

Only files named by a publication manifest are included. This tool never runs a
solver, restores controller state, or modifies the source study.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import sys
from typing import BinaryIO
import zipfile


MANIFEST_MEMBER = "_publication/publication-manifest.json"
MAX_ARCHIVE_BYTES = 2 * 1024**3
CHUNK_BYTES = 1024 * 1024
FIXED_TIMESTAMP = (1980, 1, 1, 0, 0, 0)
WINDOWS_RESERVED_NAMES = {"con", "prn", "aux", "nul"} | {
    f"{prefix}{number}" for prefix in ("com", "lpt") for number in range(1, 10)
}


class BundleError(ValueError):
    """The supplied files or archive violate the publication contract."""


def safe_relative_path(value: object) -> str:
    """Accept only canonical portable relative paths, without normalization."""
    if not isinstance(value, str) or not value:
        raise BundleError("A file path must be a nonempty string")
    if "\\" in value or ":" in value or any(ord(char) < 32 for char in value):
        raise BundleError(f"Unsafe file path: {value!r}")
    parts = value.split("/")
    if value.startswith("/") or any(part in {"", ".", ".."} for part in parts):
        raise BundleError(f"Unsafe file path: {value!r}")
    if any(part.endswith((" ", ".")) for part in parts):
        raise BundleError(f"Nonportable file path: {value!r}")
    if any(part.split(".")[0].casefold() in WINDOWS_RESERVED_NAMES for part in parts):
        raise BundleError(f"Nonportable file path: {value!r}")
    return value


def read_manifest(path: Path) -> tuple[bytes, dict, list[dict]]:
    raw = path.read_bytes()
    try:
        document = json.loads(raw)
    except (ValueError, UnicodeError) as exc:
        raise BundleError("The publication manifest is not valid UTF-8 JSON") from exc
    if (not isinstance(document, dict) or type(document.get("schema_version")) is not int
            or document["schema_version"] != 1):
        raise BundleError("The publication manifest must have schema_version 1")
    if not isinstance(document.get("study_id"), str) or not document["study_id"].strip():
        raise BundleError("The publication manifest must identify the study")
    records = document.get("files")
    if not isinstance(records, list):
        raise BundleError("The publication manifest must contain a files list")
    paths = []
    for record in records:
        if not isinstance(record, dict):
            raise BundleError("Each file record must be an object")
        path_value = safe_relative_path(record.get("path"))
        safe_relative_path(record.get("source_path"))
        if path_value.split("/")[0].casefold() == "_publication":
            raise BundleError("The _publication directory is reserved for bundle metadata")
        if type(record.get("bytes")) is not int or record["bytes"] < 0:
            raise BundleError(f"Invalid file size for {path_value}")
        if not isinstance(record.get("sha256"), str) or not re.fullmatch(
            r"[0-9a-f]{64}", record["sha256"]
        ):
            raise BundleError(f"Invalid SHA-256 for {path_value}")
        paths.append(path_value)
    if paths != sorted(set(paths)):
        raise BundleError("Manifest file paths must be sorted and unique")
    folded_paths = [path.casefold() for path in paths]
    if len(set(folded_paths)) != len(paths):
        raise BundleError("Manifest file paths must be unique on case-insensitive filesystems")
    path_set = set(paths)
    folded_path_set = set(folded_paths)
    for path_value in paths:
        for parent in PurePosixPath(path_value).parents:
            if str(parent) in path_set or str(parent).casefold() in folded_path_set:
                raise BundleError(f"A file is also a parent directory: {parent}")
    return raw, document, records


def open_source(root: Path, relative: str) -> BinaryIO:
    """Open beneath a directory descriptor, refusing symlinks in every component."""
    nofollow = getattr(os, "O_NOFOLLOW", None)
    directory = getattr(os, "O_DIRECTORY", None)
    if nofollow is None or directory is None or os.open not in os.supports_dir_fd:
        raise BundleError("Safe source opening requires directory descriptors and O_NOFOLLOW")
    descriptor = os.open(root, os.O_RDONLY | nofollow | directory)
    try:
        parts = relative.split("/")
        for part in parts[:-1]:
            child = os.open(part, os.O_RDONLY | nofollow | directory, dir_fd=descriptor)
            os.close(descriptor)
            descriptor = child
        file_descriptor = os.open(
            parts[-1], os.O_RDONLY | nofollow | os.O_NONBLOCK, dir_fd=descriptor
        )
        try:
            if not stat.S_ISREG(os.fstat(file_descriptor).st_mode):
                raise BundleError(f"Source is not a regular file: {relative}")
            return os.fdopen(file_descriptor, "rb")
        except BaseException:
            os.close(file_descriptor)
            raise
    finally:
        os.close(descriptor)


def transfer_checked(source: BinaryIO, record: dict, destination: BinaryIO | None = None) -> None:
    digest = hashlib.sha256()
    size = 0
    while block := source.read(CHUNK_BYTES):
        size += len(block)
        if size > record["bytes"]:
            raise BundleError(f"File exceeds its recorded size: {record['path']}")
        digest.update(block)
        if destination is not None:
            destination.write(block)
    if size != record["bytes"] or digest.hexdigest() != record["sha256"]:
        raise BundleError(f"Size or SHA-256 mismatch: {record['path']}")


def zip_info(name: str) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(name, date_time=FIXED_TIMESTAMP)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.compress_level = 6
    info.create_system = 3
    info.external_attr = (stat.S_IFREG | 0o644) << 16
    return info


def archive_receipt(archive: Path, raw: bytes, document: dict, records: list[dict]) -> dict:
    digest = hashlib.sha256()
    with archive.open("rb") as stream:
        while block := stream.read(CHUNK_BYTES):
            digest.update(block)
    return {
        "study_id": document["study_id"],
        "files": len(records),
        "bytes": sum(record["bytes"] for record in records),
        "archive_bytes": archive.stat().st_size,
        "archive_sha256": digest.hexdigest(),
        "manifest_sha256": hashlib.sha256(raw).hexdigest(),
    }


def build(project_root: Path, manifest: Path, output: Path) -> dict:
    raw, document, records = read_manifest(manifest)
    # Exclusive creation avoids replacing even an existing incomplete archive.
    with output.open("xb") as output_stream:
        try:
            with zipfile.ZipFile(output_stream, "w", compression=zipfile.ZIP_DEFLATED,
                                 compresslevel=6, allowZip64=True) as archive:
                for record in records:
                    with open_source(project_root, record["source_path"]) as source:
                        if os.fstat(source.fileno()).st_size != record["bytes"]:
                            raise BundleError(f"Source size mismatch: {record['source_path']}")
                        with archive.open(zip_info(record["path"]), "w", force_zip64=True) as target:
                            transfer_checked(source, record, target)
                archive.writestr(zip_info(MANIFEST_MEMBER), raw, compresslevel=6)
            output_stream.flush()
            if output_stream.tell() >= MAX_ARCHIVE_BYTES:
                raise BundleError("The archive must be smaller than 2 GiB")
        except BaseException:
            output_stream.close()
            output.unlink(missing_ok=True)
            raise
    return archive_receipt(output, raw, document, records)


def verify(manifest: Path, archive_path: Path, destination: Path | None = None) -> dict:
    raw, document, records = read_manifest(manifest)
    if destination is not None and os.path.lexists(destination):
        raise BundleError("The extraction destination must not exist")
    if archive_path.is_symlink() or not archive_path.is_file():
        raise BundleError("The archive must be a regular file, not a symlink")
    if archive_path.stat().st_size >= MAX_ARCHIVE_BYTES:
        raise BundleError("The archive must be smaller than 2 GiB")
    with zipfile.ZipFile(archive_path, "r") as archive:
        names = []
        for info in archive.infolist():
            safe_relative_path(info.orig_filename)
            if info.orig_filename != info.filename:
                raise BundleError("Archive member names must not contain null bytes")
            mode = info.external_attr >> 16
            if info.is_dir() or stat.S_IFMT(mode) not in {0, stat.S_IFREG}:
                raise BundleError(f"Archive member is not a regular file: {info.filename}")
            if info.flag_bits & 1:
                raise BundleError("Encrypted archive members are not supported")
            names.append(info.filename)
        expected = {record["path"] for record in records} | {MANIFEST_MEMBER}
        if len(names) != len(set(names)) or set(names) != expected:
            raise BundleError("Archive membership differs from the supplied manifest")
        if archive.getinfo(MANIFEST_MEMBER).file_size != len(raw):
            raise BundleError("The embedded manifest differs from the supplied manifest")
        if archive.read(MANIFEST_MEMBER) != raw:
            raise BundleError("The embedded manifest differs from the supplied manifest")
        for record in records:
            if archive.getinfo(record["path"]).file_size != record["bytes"]:
                raise BundleError(f"Archive member size mismatch: {record['path']}")
            with archive.open(record["path"]) as source:
                transfer_checked(source, record)
        # Validation finishes before creating the destination. Recheck content
        # during extraction so a concurrent archive mutation cannot go unnoticed.
        if destination is not None:
            destination.mkdir()
            try:
                for record in records:
                    target = destination.joinpath(*record["path"].split("/"))
                    target.parent.mkdir(parents=True, exist_ok=True)
                    with archive.open(record["path"]) as source, target.open("xb") as stream:
                        transfer_checked(source, record, stream)
                metadata = destination / MANIFEST_MEMBER
                metadata.parent.mkdir(parents=True, exist_ok=True)
                metadata.write_bytes(raw)
            except BaseException:
                shutil.rmtree(destination)
                raise
    receipt = archive_receipt(archive_path, raw, document, records)
    receipt["verified"] = True
    receipt["extracted"] = destination is not None
    return receipt


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    build_parser = commands.add_parser("build", help="Create one immutable study ZIP")
    build_parser.add_argument("--project-root", type=Path, required=True)
    build_parser.add_argument("--manifest", type=Path, required=True)
    build_parser.add_argument("--output", type=Path, required=True)
    verify_parser = commands.add_parser("verify", help="Verify and optionally extract a study ZIP")
    verify_parser.add_argument("--manifest", type=Path, required=True)
    verify_parser.add_argument("--archive", type=Path, required=True)
    verify_parser.add_argument("--destination", type=Path)
    arguments = parser.parse_args(argv)
    try:
        if arguments.command == "build":
            receipt = build(arguments.project_root, arguments.manifest, arguments.output)
        else:
            receipt = verify(arguments.manifest, arguments.archive, arguments.destination)
    except (BundleError, OSError, ValueError, RuntimeError, zipfile.BadZipFile) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1
    print(json.dumps(receipt, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
