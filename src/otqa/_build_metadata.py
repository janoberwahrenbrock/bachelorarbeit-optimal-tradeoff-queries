"""Dependency-free build/source identity shared by distribution and runtime."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

INVENTORY_FORMAT = "otqa-source-v1"
STAMP_FILES = frozenset({"_source_inventory.json", "_build_provenance.json"})


def canonical_bytes(document: dict) -> bytes:
    return json.dumps(document, sort_keys=True, ensure_ascii=False,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def build_inventory(package_root: Path) -> dict:
    root = Path(package_root)
    if root.is_symlink() or not root.is_dir():
        raise ValueError("Package root must be a real directory")
    files = []
    for path in root.rglob("*"):
        relative = path.relative_to(root)
        if path.is_symlink():
            raise ValueError(f"Symlink in package source: {relative}")
        include = path.suffix == ".py" or (relative.parts[0] == "schemas" and path.suffix == ".json")
        if not path.is_file() or not include or relative.as_posix() in STAMP_FILES:
            continue
        data = path.read_bytes()
        files.append({"path": "otqa/" + relative.as_posix(), "bytes": len(data),
                      "sha256": hashlib.sha256(data).hexdigest()})
    files.sort(key=lambda item: item["path"].encode("utf-8"))
    if not files:
        raise ValueError("An empty package cannot have a production identity")
    return {"schema_version": 1, "inventory_format": INVENTORY_FORMAT, "files": files}


def inventory_digest(inventory: dict) -> str:
    return hashlib.sha256(canonical_bytes(inventory)).hexdigest()


def write_build_metadata(package_root: Path, version: str, git_commit: str | None,
                         dirty: bool, *, preserve_existing: bool = False) -> dict:
    """Stamp actual package bytes. Preserving a stamp always verifies both files."""
    root = Path(package_root)
    actual = build_inventory(root)
    digest = inventory_digest(actual)
    inventory_path = root / "_source_inventory.json"
    provenance_path = root / "_build_provenance.json"
    if preserve_existing and (inventory_path.exists() or provenance_path.exists()):
        if not inventory_path.exists() or not provenance_path.exists():
            raise ValueError("Incomplete source build metadata")
        recorded = json.loads(inventory_path.read_bytes())
        provenance = json.loads(provenance_path.read_bytes())
        if recorded != actual or provenance.get("inventory_sha256") != digest:
            raise ValueError("Existing build source inventory differs from actual package")
        source = provenance.get("source", {})
        if source.get("inventory_format") != INVENTORY_FORMAT or source.get("source_sha256") != digest:
            raise ValueError("Existing build source stamp is inconsistent")
        return provenance
    source = {"inventory_format": INVENTORY_FORMAT, "version": version,
              "git_commit": git_commit, "dirty": dirty, "source_sha256": digest}
    provenance = {"schema_version": 1, "source": source, "inventory_sha256": digest}
    inventory_path.write_bytes(canonical_bytes(actual) + b"\n")
    provenance_path.write_bytes(canonical_bytes(provenance) + b"\n")
    return provenance
