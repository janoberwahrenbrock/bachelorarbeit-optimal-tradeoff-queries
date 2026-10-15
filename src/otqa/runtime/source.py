"""Verify actual installed production source against its immutable build stamp."""
from __future__ import annotations

from pathlib import Path

from otqa._build_metadata import build_inventory, inventory_digest

from .codec import DocumentError, read_json
from .schema import validate


def loaded_source(package_root: Path | None = None) -> tuple[dict, dict, dict]:
    root = Path(package_root) if package_root is not None else Path(__file__).resolve().parents[1]
    inventory = validate("source_inventory", read_json(root / "_source_inventory.json"))
    provenance = validate("source_build_provenance", read_json(root / "_build_provenance.json"))
    actual = build_inventory(root)
    actual_digest = inventory_digest(actual)
    if actual != inventory:
        raise DocumentError("Loaded package files differ from the build source inventory")
    if provenance["inventory_sha256"] != actual_digest or provenance["source"]["source_sha256"] != actual_digest:
        raise DocumentError("Build source digest does not match actual inventory")
    return provenance["source"], inventory, provenance


def same_source(left: dict, right: dict) -> bool:
    return (left["inventory_format"], left["source_sha256"]) == (right["inventory_format"], right["source_sha256"])
