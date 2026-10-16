"""Publication checks use tiny synthetic files, never stored study artifacts."""

import hashlib
import importlib.util
import json
from pathlib import Path
import stat
import subprocess
import sys
import zipfile

import pytest


TOOL = Path(__file__).resolve().parents[1] / "tools/publication/study_bundle.py"
SPEC = importlib.util.spec_from_file_location("study_bundle", TOOL)
bundle = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(bundle)


@pytest.fixture
def publication(tmp_path):
    root = tmp_path / "original"
    root.mkdir()
    (root / "data").mkdir()
    payloads = {"data/answers.jsonl": b'{"answer": ">"}\n', "data/empty": b""}
    records = []
    for name, content in sorted(payloads.items()):
        (root / name).write_bytes(content)
        records.append({
            "path": "runs/study/" + name,
            "source_path": name,
            "bytes": len(content),
            "sha256": hashlib.sha256(content).hexdigest(),
        })
    document = {"schema_version": 1, "study_id": "synthetic-study", "files": records,
                "extra_metadata": {"no_solver": True}}
    manifest = tmp_path / "publication-manifest.json"
    manifest.write_text(json.dumps(document, indent=2) + "\n")
    archive = tmp_path / "download.zip"
    return root, manifest, archive, document, payloads


def rewrite_zip(path, changes=None, omit=(), extra=None):
    with zipfile.ZipFile(path) as original:
        entries = [(entry, original.read(entry)) for entry in original.infolist()]
    with zipfile.ZipFile(path, "w") as updated:
        for entry, content in entries:
            if entry.filename not in omit:
                updated.writestr(entry, (changes or {}).get(entry.filename, content))
        for name, content in (extra or {}).items():
            updated.writestr(name, content)


def test_roundtrip_is_deterministic_and_does_not_edit_sources(publication, tmp_path):
    root, manifest, archive, document, payloads = publication
    before = {str(file.relative_to(root)): file.read_bytes() for file in root.rglob("*") if file.is_file()}
    receipt = bundle.build(root, manifest, archive)
    second_archive = tmp_path / "second.zip"
    assert bundle.build(root, manifest, second_archive) == receipt
    assert archive.read_bytes() == second_archive.read_bytes()
    destination = tmp_path / "extracted"
    verified = bundle.verify(manifest, archive, destination)
    assert verified["verified"] and verified["extracted"]
    assert receipt["files"] == 2
    assert receipt["bytes"] == sum(map(len, payloads.values()))
    assert receipt["manifest_sha256"] == hashlib.sha256(manifest.read_bytes()).hexdigest()
    assert receipt["archive_sha256"] == hashlib.sha256(archive.read_bytes()).hexdigest()
    for record in document["files"]:
        assert (destination / record["path"]).read_bytes() == payloads[record["source_path"]]
    assert (destination / bundle.MANIFEST_MEMBER).read_bytes() == manifest.read_bytes()
    assert {str(file.relative_to(root)): file.read_bytes() for file in root.rglob("*")
            if file.is_file()} == before
    with zipfile.ZipFile(archive) as stream:
        assert all(info.date_time == bundle.FIXED_TIMESTAMP for info in stream.infolist())
        assert all(info.compress_type == zipfile.ZIP_DEFLATED for info in stream.infolist())


def test_cli_receipts_and_read_only_verification(publication):
    root, manifest, archive, _, _ = publication
    created = subprocess.run(
        [sys.executable, str(TOOL), "build", "--project-root", str(root),
         "--manifest", str(manifest), "--output", str(archive)], capture_output=True, text=True,
    )
    assert created.returncode == 0, created.stderr
    assert json.loads(created.stdout)["files"] == 2
    checked = subprocess.run(
        [sys.executable, str(TOOL), "verify", "--manifest", str(manifest), "--archive", str(archive)],
        capture_output=True, text=True,
    )
    assert checked.returncode == 0, checked.stderr
    assert json.loads(checked.stdout)["verified"]
    assert not json.loads(checked.stdout)["extracted"]


@pytest.mark.parametrize("modification", ["tamper", "missing", "extra", "manifest"])
def test_invalid_download_never_creates_destination(publication, tmp_path, modification):
    root, manifest, archive, document, _ = publication
    bundle.build(root, manifest, archive)
    name = document["files"][0]["path"]
    if modification == "tamper":
        rewrite_zip(archive, changes={name: b"x" * document["files"][0]["bytes"]})
    elif modification == "missing":
        rewrite_zip(archive, omit=[name])
    elif modification == "extra":
        rewrite_zip(archive, extra={"extra.txt": b"extra"})
    else:
        rewrite_zip(archive, changes={bundle.MANIFEST_MEMBER: manifest.read_bytes().replace(b"true", b"null")})
    destination = tmp_path / "must-not-exist"
    with pytest.raises(bundle.BundleError):
        bundle.verify(manifest, archive, destination)
    assert not destination.exists()


@pytest.mark.parametrize("unsafe", ["/absolute", "../escape", "a/../escape", "./relative",
                                   "a//b", "C:/file", "a\\b", "a\x00b", "a/", "a. /b",
                                   "CON", "files/aux.txt"])
@pytest.mark.parametrize("field", ["path", "source_path"])
def test_unsafe_manifest_paths_are_refused(publication, unsafe, field):
    root, manifest, archive, document, _ = publication
    document["files"][0][field] = unsafe
    manifest.write_text(json.dumps(document))
    with pytest.raises(bundle.BundleError):
        bundle.build(root, manifest, archive)
    assert not archive.exists()


@pytest.mark.parametrize("member", ["../escape", "/absolute", "a\\b"])
def test_unsafe_archive_paths_are_refused(publication, member):
    root, manifest, archive, _, _ = publication
    bundle.build(root, manifest, archive)
    rewrite_zip(archive, extra={member: b"unsafe"})
    with pytest.raises(bundle.BundleError):
        bundle.verify(manifest, archive)


def test_duplicate_members_are_refused(publication):
    root, manifest, archive, document, _ = publication
    bundle.build(root, manifest, archive)
    with pytest.warns(UserWarning, match="Duplicate name"):
        with zipfile.ZipFile(archive, "a") as stream:
            stream.writestr(document["files"][0]["path"], b"duplicate")
    with pytest.raises(bundle.BundleError, match="membership"):
        bundle.verify(manifest, archive)


def test_symlink_archive_members_are_refused(publication):
    root, manifest, archive, document, _ = publication
    bundle.build(root, manifest, archive)
    with zipfile.ZipFile(archive) as stream:
        entries = [(info, stream.read(info)) for info in stream.infolist()]
    with zipfile.ZipFile(archive, "w") as stream:
        for info, content in entries:
            if info.filename == document["files"][0]["path"]:
                info.create_system = 3
                info.external_attr = (stat.S_IFLNK | 0o777) << 16
            stream.writestr(info, content)
    with pytest.raises(bundle.BundleError, match="regular file"):
        bundle.verify(manifest, archive)


@pytest.mark.parametrize("link_kind", ["file", "directory"])
def test_symlink_sources_are_refused(publication, tmp_path, link_kind):
    root, manifest, archive, _, _ = publication
    if link_kind == "file":
        source = root / "data/answers.jsonl"
        outside = tmp_path / "outside"
        outside.write_bytes(source.read_bytes())
        source.unlink()
        source.symlink_to(outside)
    else:
        directory = root / "data"
        outside = tmp_path / "outside-data"
        directory.rename(outside)
        directory.symlink_to(outside, target_is_directory=True)
    with pytest.raises((bundle.BundleError, OSError)):
        bundle.build(root, manifest, archive)
    assert not archive.exists()


@pytest.mark.parametrize("kind", ["size", "hash", "missing"])
def test_source_changes_fail_and_remove_incomplete_archive(publication, kind):
    root, manifest, archive, _, _ = publication
    source = root / "data/answers.jsonl"
    if kind == "size":
        source.write_bytes(b"different-size")
    elif kind == "hash":
        source.write_bytes(b"x" * source.stat().st_size)
    else:
        source.unlink()
    with pytest.raises((bundle.BundleError, OSError)):
        bundle.build(root, manifest, archive)
    assert not archive.exists()


def test_build_preserves_existing_output_and_verify_preserves_existing_destination(publication, tmp_path):
    root, manifest, archive, _, _ = publication
    archive.write_bytes(b"keep existing bytes")
    with pytest.raises(FileExistsError):
        bundle.build(root, manifest, archive)
    assert archive.read_bytes() == b"keep existing bytes"
    archive.unlink()
    bundle.build(root, manifest, archive)
    destination = tmp_path / "existing"
    destination.mkdir()
    marker = destination / "marker"
    marker.write_bytes(b"keep")
    with pytest.raises(bundle.BundleError, match="must not exist"):
        bundle.verify(manifest, archive, destination)
    assert marker.read_bytes() == b"keep"


def test_archive_size_limit_removes_build_output(publication, monkeypatch):
    root, manifest, archive, _, _ = publication
    monkeypatch.setattr(bundle, "MAX_ARCHIVE_BYTES", 1)
    with pytest.raises(bundle.BundleError, match="2 GiB"):
        bundle.build(root, manifest, archive)
    assert not archive.exists()


def test_archive_size_limit_is_checked_during_verification(publication, monkeypatch):
    root, manifest, archive, _, _ = publication
    bundle.build(root, manifest, archive)
    monkeypatch.setattr(bundle, "MAX_ARCHIVE_BYTES", archive.stat().st_size)
    with pytest.raises(bundle.BundleError, match="2 GiB"):
        bundle.verify(manifest, archive)


@pytest.mark.parametrize("modification", ["duplicate", "unsorted", "parent", "reserved", "case"])
def test_manifest_requires_unambiguous_sorted_paths(publication, modification):
    root, manifest, archive, document, _ = publication
    if modification == "duplicate":
        document["files"].append(document["files"][0])
    elif modification == "unsorted":
        document["files"].reverse()
    elif modification == "parent":
        document["files"][0]["path"] = "runs"
    elif modification == "reserved":
        document["files"][0]["path"] = bundle.MANIFEST_MEMBER
    else:
        document["files"][0]["path"] = document["files"][1]["path"].upper()
    manifest.write_text(json.dumps(document))
    with pytest.raises(bundle.BundleError):
        bundle.build(root, manifest, archive)
    assert not archive.exists()


@pytest.mark.parametrize("field,value", [("schema_version", True), ("study_id", ""), ("files", {})])
def test_invalid_manifest_structure(publication, field, value):
    root, manifest, archive, document, _ = publication
    document[field] = value
    manifest.write_text(json.dumps(document))
    with pytest.raises(bundle.BundleError):
        bundle.build(root, manifest, archive)
    assert not archive.exists()


def test_nonregular_sources_are_refused_without_reading(publication):
    root, manifest, archive, _, _ = publication
    source = root / "data/answers.jsonl"
    source.unlink()
    source.mkdir()
    with pytest.raises(bundle.BundleError, match="regular file"):
        bundle.build(root, manifest, archive)
    assert not archive.exists()
