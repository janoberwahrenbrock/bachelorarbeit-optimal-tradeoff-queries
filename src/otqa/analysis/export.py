"""Exports bind one explicit audit or one freshly captured consistent audit."""
from __future__ import annotations

import csv
import io
import json
from pathlib import Path
from uuid import uuid4

from otqa.runtime.codec import DocumentError, digest, encode
from otqa.runtime.documents import file_ref, load_document, resolve_ref
from otqa.runtime.project import verify_binding
from otqa.runtime.storage import publish_bytes, publish_json

from .audit import audit_series
from .summary import build_summary


def export_series(request, *, _allow_qualification=False):
    from otqa.application_types import AuditRequest, ExportReceipt
    context, root = request.context, Path(request.series_dir).absolute()
    context.binding(root)
    output = Path(request.output_path).absolute()
    context.relative_output(output)
    try:
        relative = output.relative_to(root)
    except ValueError as exc:
        raise DocumentError("Export must remain inside its own series") from exc
    if len(relative.parts) != 2 or relative.parts[0] != "exports":
        raise DocumentError("Exports belong directly under SeriesRoot/exports/")
    if output.exists() or output.with_name(output.name + ".receipt.json").exists():
        raise DocumentError("Export output already exists")
    if request.format not in ("json", "csv"):
        raise DocumentError("Export format must be json or csv")
    if request.audit_ref is None:
        outcome = audit_series(AuditRequest(context, root, root / "reports" / str(uuid4()) / "audit.json"), _allow_qualification=_allow_qualification)
        audit_ref = file_ref(outcome.report_path, root)
        audit = outcome.report
    else:
        audit_ref = dict(request.audit_ref)
        audit_path = resolve_ref(root, audit_ref)
        from .audit import report_directory
        report_directory(root, audit_path)
        audit = load_document("audit", audit_path, reference_root=root)
    plan = load_document("series_plan", resolve_ref(root, audit["plan"]), reference_root=root)
    verify_binding(context, root, plan["project_binding"])
    if plan["run_purpose"] != "production" and not _allow_qualification:
        raise DocumentError("Public exports accept production plans only")
    summary = build_summary(root, audit, audit_ref)
    summary_path = root / audit_ref["path"]
    summary_path = summary_path.parent / "summary.json"
    if summary_path.exists():
        if summary_path.read_bytes() != encode(summary):
            raise DocumentError("Existing immutable summary differs from independently recomputed raw data")
    else:
        publish_json(context, summary_path, summary, kind="summary")
    if request.format == "json":
        data = encode(summary)
    else:
        stream = io.StringIO(newline="")
        metadata_keys = ["audit_path", "audit_sha256", "plan_sha256", "state_snapshot_sha256", "scope"]
        keys = list(summary["rows"][0])
        writer = csv.DictWriter(stream, fieldnames=metadata_keys + keys, lineterminator="\n")
        writer.writeheader()
        for row in summary["rows"]:
            encoded = {key: json.dumps(value, separators=(",", ":"), ensure_ascii=False) if isinstance(value, (dict, list)) else value for key, value in row.items()}
            writer.writerow({"audit_path": audit_ref["path"], "audit_sha256": audit_ref["sha256"], "plan_sha256": audit["plan"]["sha256"],
                "state_snapshot_sha256": audit["state"]["sha256"], "scope": summary["scope"], **encoded})
        data = stream.getvalue().encode("utf-8")
    publish_bytes(context, output, data)
    receipt = {"schema_version": 1, "output": file_ref(output, root), "audit": audit_ref, "plan": audit["plan"], "state": audit["state"],
               "prefix_snapshots": audit["prefix_snapshots"], "scope": summary["scope"], "format": request.format}
    publish_json(context, output.with_name(output.name + ".receipt.json"), receipt)
    return ExportReceipt(output, digest(data), root, audit_ref, audit["plan"], audit["state"], summary["scope"])
