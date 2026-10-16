"""Strict UTF-8 JSON and explicit binary64 evidence; no numerical imports."""
from __future__ import annotations

import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class DocumentError(ValueError):
    """A document or reference violates the native wire contract."""


def _pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result = {}
    for key, value in pairs:
        if key in result:
            raise DocumentError(f"Duplicate JSON key: {key!r}")
        result[key] = value
    return result


def _float(value: str) -> float:
    parsed = float(value)
    if not math.isfinite(parsed):
        raise DocumentError(f"Non-finite JSON number: {value}")
    return parsed


def decode(data: bytes) -> Any:
    if data.startswith(b"\xef\xbb\xbf"):
        raise DocumentError("UTF-8 BOM is not permitted")
    try:
        return json.loads(data.decode("utf-8"), object_pairs_hook=_pairs,
                          parse_float=_float,
                          parse_constant=lambda value: _reject_constant(value))
    except (ValueError, UnicodeError) as exc:
        raise DocumentError(str(exc)) from exc


def _reject_constant(value: str) -> None:
    raise DocumentError(f"Non-finite JSON token: {value}")


def encode(document: Any, *, newline: bool = True) -> bytes:
    try:
        text = json.dumps(document, ensure_ascii=False, sort_keys=True,
                          separators=(",", ":"), allow_nan=False)
    except (ValueError, TypeError) as exc:
        raise DocumentError(str(exc)) from exc
    return (text + ("\n" if newline else "")).encode("utf-8")


def read_json(path: Path) -> Any:
    return decode(path.read_bytes())


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_digest(document: Any) -> str:
    return digest(encode(document, newline=False))


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


def pointer_escape(value: str) -> str:
    return value.replace("~", "~0").replace("/", "~1")


def float_projection(value: Any) -> Any:
    """Canonical mathematical identity after the caller's typed float projection."""
    if isinstance(value, float):
        if not math.isfinite(value):
            raise DocumentError("Non-finite mathematical value")
        return {"float_hex": value.hex()}
    if isinstance(value, dict):
        return {key: float_projection(child) for key, child in value.items()}
    if isinstance(value, (list, tuple)):
        return [float_projection(child) for child in value]
    return value


def numeric_hex(value: Any, pointer: str = "") -> dict[str, str]:
    """Record explicit floats only; integer counts and indices remain integers."""
    result = {}
    if isinstance(value, float):
        if not math.isfinite(value):
            raise DocumentError("Cannot serialize non-finite mathematical value")
        result[pointer] = value.hex()
    elif isinstance(value, dict):
        for key, child in value.items():
            result.update(numeric_hex(child, pointer + "/" + pointer_escape(key)))
    elif isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            result.update(numeric_hex(child, pointer + "/" + str(index)))
    return result


def mathematical_hex(value: Any, pointer: str = "", *, all_numbers: bool = False) -> dict[str, str]:
    """Typed mathematical evidence, including mathematical JSONinteger spelling."""
    scalar_names = {"value", "probability", "expected_terminal_candidates", "expected_terminal_loss", "expected_queries",
                    "gain", "rate", "min_expected_progress", "starting_value", "expected_terminal_value", "expected_progress", "threshold", "maximum_volume_share", "selected_candidate_volume", "selected_candidate_volume_share"}
    containers = {"candidate_volumes", "candidate_volume_shares", "answer_probabilities", "lexicographic_expected_values"}
    result = {}
    if all_numbers and type(value) in (int, float):
        binary = float(value)
        if not math.isfinite(binary):
            raise DocumentError("Non-finite mathematical number")
        return {pointer: binary.hex()}
    if isinstance(value, dict):
        for key, child in value.items():
            if key in ("error", "context", "telemetry_errors", "numeric_hex"):
                continue
            result.update(mathematical_hex(child, pointer + "/" + pointer_escape(key),
                                          all_numbers=all_numbers or key in scalar_names or key in containers))
    elif isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            result.update(mathematical_hex(child, pointer + "/" + str(index), all_numbers=all_numbers))
    return result
