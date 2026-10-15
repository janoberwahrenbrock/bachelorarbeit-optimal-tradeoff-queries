import hashlib
import json

import pytest

from otqa._build_metadata import build_inventory, inventory_digest, write_build_metadata
from otqa.runtime.codec import DocumentError
from otqa.runtime.source import loaded_source, same_source


def package(tmp_path):
    root = tmp_path / "src" / "otqa"
    (root / "schemas").mkdir(parents=True)
    (root / "api.py").write_bytes(b"def independently_constructed_control():\n    return None\n")
    (root / "schemas" / "control.json").write_bytes(b'{"type":"object"}\n')
    return root


def test_inventory_hash_includes_whole_versioned_document_without_final_newline(tmp_path):
    root = package(tmp_path)
    inventory = build_inventory(root)
    canonical = json.dumps(inventory, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()
    assert inventory_digest(inventory) == hashlib.sha256(canonical).hexdigest()
    assert inventory_digest(inventory) != hashlib.sha256(canonical + b"\n").hexdigest()
    assert [entry["path"] for entry in inventory["files"]] == ["otqa/api.py", "otqa/schemas/control.json"]


def test_docs_and_run_bytes_do_not_change_production_source(tmp_path):
    root = package(tmp_path)
    before = build_inventory(root)
    (tmp_path / "runs").mkdir()
    (tmp_path / "runs" / "result.json").write_text('{"new_run":true}')
    (tmp_path / "README.md").write_text("Fresh documentation")
    assert build_inventory(root) == before


@pytest.mark.parametrize("mutation", ["changed", "added", "missing"])
def test_actual_package_mutation_invalidates_the_stamp(tmp_path, mutation):
    root = package(tmp_path)
    write_build_metadata(root, "control", None, True)
    loaded_source(root)
    if mutation == "changed":
        (root / "api.py").write_text("changed = True\n")
    elif mutation == "added":
        (root / "unexpected.py").write_text("added = True\n")
    else:
        (root / "api.py").unlink()
    with pytest.raises(DocumentError):
        loaded_source(root)


def test_preserving_verified_build_metadata_does_not_relabel_source(tmp_path):
    root = package(tmp_path)
    first = write_build_metadata(root, "first-build", None, True)
    second = write_build_metadata(root, "different-requested-version", "a" * 40, False, preserve_existing=True)
    assert first == second
    source, _, provenance = loaded_source(root)
    assert source == first["source"] == provenance["source"]
    assert same_source(source, {**source, "version": "other-provenance", "dirty": False})


def test_source_symlink_is_never_a_hash_alias(tmp_path):
    root = package(tmp_path)
    (root / "alias.py").symlink_to(root / "api.py")
    with pytest.raises(ValueError, match="Symlink"):
        build_inventory(root)
