"""Verified native continuations from immutable, durably accepted journal prefixes.

Origin documents are copied as bytes. Their references are indexed by their
original paths rather than rewritten: rewriting an origin manifest would break
the journal's manifest hash. Ordinary continuation input references can still be
materialized by the common input adapter.
"""
from __future__ import annotations

from pathlib import Path

from .codec import DocumentError, canonical_digest, decode, digest, float_projection, read_json
from .documents import file_ref, load_document, references, resolve_ref, typed_projection
from .schema import validate


def _same_mathematics(left, right):
    return canonical_digest(float_projection(left)) == canonical_digest(float_projection(right))


def _origin_edges(kind, document):
    """Declared provenance edges only; arbitrary metadata never becomes a path."""
    if kind == "manifest":
        for name, target in (("source_inventory", "source_inventory"),
                             ("execution_profile", "execution_profile"),
                             ("materialization_receipt", "materialization_receipt"),
                             ("launch_intent", "launch_intent")):
            yield target, document[name]
        for name, ref in document["inputs"].items():
            if ref is not None:
                target = {"configuration": "config", "initial_answers": "answer_history",
                          "replay_answers": "answer_history"}.get(name, name)
                yield target, ref
    elif kind == "materialization_receipt":
        for entry in document["entries"]:
            yield "raw_report", entry["original"]
            yield "raw_report", entry["materialized"]
    elif kind == "launch_intent":
        yield "materialization_receipt", document["materialization_receipt"]
    else:
        for _, target, ref in references(kind, document):
            yield target, ref


def _collect_origin(root, manifest_path):
    """Snapshot and hash-check the complete declared, small evidence closure."""
    documents = {}
    active = set()

    def visit(kind, reference):
        key = reference["path"]
        if key in documents:
            if digest(documents[key]) != reference["sha256"]:
                raise DocumentError("Origin references disagree about the same path")
            return
        if key in active:
            raise DocumentError("Cyclic continuation origin closure")
        active.add(key)
        data = resolve_ref(root, reference).read_bytes()
        if kind not in ("raw_report", "environment_lock"):
            document = validate(kind, decode(data))
            for target, child in _origin_edges(kind, document):
                visit(target, child)
        documents[key] = data
        active.remove(key)

    visit("manifest", file_ref(manifest_path, root))
    return documents


def _profile_mathematics(profile):
    return {key: profile[key] for key in ("platform_family", "python_version", "packages", "backend_capabilities")} | {
        "environment_lock_sha256": profile["environment_lock"]["sha256"]}


def verify_continuation_document(document, *, reference_root, problem=None, configuration=None,
                                 source=None, profile=None, _resolve=None, _depth=0):
    """Verify proof bytes and phase independently, without running a solver.

    ``source`` and ``profile`` are mandatory at the import/execution boundary;
    offline origin export may verify historical bytes without claiming that the
    current machine can reproduce their numerical decisions.
    """
    from otqa._build_metadata import inventory_digest
    from .journal import verify_prefix
    from .source import same_source

    if _depth > 64:
        raise DocumentError("Continuation origin nesting exceeds its verified bound")
    validate("continuation", document)
    root = Path(reference_root)
    resolve = _resolve or (lambda reference: resolve_ref(root, reference))
    stored_problem = load_document("problem", resolve(document["problem"]), reference_root=root)
    stored_config = load_document("config", resolve(document["configuration"]), reference_root=root)
    if stored_config["schema_version"] != 2:
        raise DocumentError("An explicit continuation requires the v2 execution contract")
    proof = document["origin_proof"]
    index = {}
    paths = {}
    for item in proof["artifacts"]:
        if item["original_path"] in index:
            raise DocumentError("Duplicate original path in continuation proof")
        paths[item["original_path"]] = resolve(item["artifact"])
        index[item["original_path"]] = paths[item["original_path"]].read_bytes()

    def origin(reference, kind):
        try:
            data = index[reference["path"]]
        except KeyError as exc:
            raise DocumentError("Continuation origin is missing a referenced artifact") from exc
        if digest(data) != reference["sha256"]:
            raise DocumentError("Continuation origin artifact differs from its original hash")
        return data if kind in ("raw_report", "environment_lock") else validate(kind, decode(data))

    manifest_bytes = resolve(proof["manifest"]).read_bytes()
    manifest = validate("manifest", decode(manifest_bytes))
    if manifest["schema_version"] != 2:
        raise DocumentError("Historical modulo execution cannot be imported as a regular continuation")
    seen = set()

    def check_closure(kind, value):
        for target, ref in _origin_edges(kind, value):
            key = (ref["path"], ref["sha256"], target)
            if key in seen:
                continue
            seen.add(key)
            child = origin(ref, target)
            if target not in ("raw_report", "environment_lock"):
                check_closure(target, child)

    check_closure("manifest", manifest)
    origin_problem = origin(manifest["inputs"]["problem"], "problem")
    origin_config = origin(manifest["inputs"]["configuration"], "config")
    if (manifest['problem_id'] != origin_problem['problem_id']
            or manifest['configuration_id'] != origin_config['configuration_id']):
        raise DocumentError('Origin manifest input identities differ from its bound documents')
    for kind, current, original in (("problem", stored_problem, origin_problem),
                                     ("config", stored_config, origin_config)):
        if not _same_mathematics(typed_projection(kind, current), typed_projection(kind, original)):
            raise DocumentError("Continuation binding differs from its original problem or configuration")
    for current, stored, kind in ((problem, stored_problem, "problem"), (configuration, stored_config, "config")):
        if current is not None and not _same_mathematics(typed_projection(kind, current), typed_projection(kind, stored)):
            raise DocumentError("Continuation belongs to a different problem or configuration")
    for name, key in (("effective_algorithm", "algorithm"), ("effective_budget", "budget"),
                      ("effective_execution", "execution"), ("effective_recording", "recording")):
        if not _same_mathematics(manifest[name], origin_config[key]):
            raise DocumentError("Origin manifest effective policy differs from its configuration")
    inventory = origin(manifest["source_inventory"], "source_inventory")
    if inventory_digest(inventory) != manifest["source"]["source_sha256"]:
        raise DocumentError("Origin inventory does not bind the manifest source")
    if source is not None and not same_source(source, manifest["source"]):
        raise DocumentError("Continuation source differs from the actually loaded source")
    origin_profile = origin(manifest["execution_profile"], "execution_profile")
    if profile is not None and not _same_mathematics(_profile_mathematics(profile), _profile_mathematics(origin_profile)):
        raise DocumentError("Continuation requires the original numerical execution environment")
    if (manifest["environment"]["packages"] != origin_profile["packages"]
            or manifest["environment"]["python"] != origin_profile["python_version"]
            or manifest['environment']['platform_family'] != origin_profile['platform_family']
            or manifest['environment']['backend_capabilities'] != origin_profile['backend_capabilities']):
        raise DocumentError("Origin manifest environment differs from its execution profile")
    initial = []
    initial_doc = None
    if manifest["inputs"]["initial_answers"] is not None:
        initial_doc = origin(manifest["inputs"]["initial_answers"], "answer_history")
        if initial_doc['problem_id'] != origin_problem['problem_id']:
            raise DocumentError('Origin starting history belongs to a different problem')
        initial = initial_doc["answers"]
    prior = manifest["inputs"].get("continuation")
    prior_doc = None
    if prior is not None:
        if initial_doc is not None:
            raise DocumentError('Origin mixes a continuation with a separate initial history')
        prior_doc = origin(prior, "continuation")
        def resolve_prior(reference):
            origin(reference, "raw_report")
            return paths[reference["path"]]
        verify_continuation_document(prior_doc, reference_root=root, problem=origin_problem,
            configuration=origin_config, source=manifest["source"], profile=origin_profile,
            _resolve=resolve_prior, _depth=_depth + 1)
        initial = prior_doc["answers"]
    expected_cursor = (prior_doc['execution_cursor'] if prior_doc is not None else {
        'answered_total': len(initial), 'remaining_depth': manifest['effective_algorithm']['depth']})
    if manifest['initial_execution_cursor'] != expected_cursor:
        raise DocumentError('Origin starting cursor differs from its verified starting input')
    expected_kind = ('continuation' if prior_doc is not None else 'warm_start' if initial_doc is not None
                     else 'replay' if manifest['answer_source'] == 'replay' else 'fresh')
    if manifest['execution_kind'] != expected_kind:
        raise DocumentError('Origin execution kind differs from its bound starting input')
    from .serialization import mathematical_input_digest
    oracle_ref, replay_ref = manifest['inputs']['oracle'], manifest['inputs']['replay_answers']
    oracle = origin(oracle_ref, 'oracle') if oracle_ref is not None else None
    replay = origin(replay_ref, 'answer_history') if replay_ref is not None else None
    expected_digest = mathematical_input_digest(origin_problem, origin_config, manifest['answer_source'],
        initial_doc, oracle, replay, continuation=prior_doc)
    if manifest['mathematical_input_sha256'] != expected_digest:
        raise DocumentError('Origin mathematical starting identity differs from its bound inputs')
    prefix = resolve(proof["journal_prefix"]).read_bytes()
    if len(prefix) != proof["valid_prefix_bytes"] or digest(prefix) != proof["valid_prefix_sha256"]:
        raise DocumentError("Continuation immutable prefix byte proof differs")
    verified = verify_prefix(prefix, len(prefix), proof["valid_prefix_sha256"], proof["last_good_sequence"],
        initial_answers=len(initial), algorithm=manifest["effective_algorithm"], budget=manifest["effective_budget"],
        alternative_ids=origin_problem["alternative_ids"], initial_execution_cursor=manifest["initial_execution_cursor"])
    if verified["events"][0]["payload"]["manifest_sha256"] != digest(manifest_bytes):
        raise DocumentError("Continuation journal does not bind its immutable origin manifest")
    if verified["last_event_type"] != "answer_received":
        raise DocumentError("An explicit continuation must end at an accepted answer boundary")
    if verified["query_counts"]["dispatched_new"] != verified["query_counts"]["answered_new"]:
        raise DocumentError("An unanswered dispatch is not an exportable answer boundary")
    accepted = initial + [{**event["payload"]["query"], "answer": event["payload"]["answer"]}
                          for event in verified["events"] if event["event_type"] == "answer_received"]
    objective_count = len(origin_problem['objective_ids'])
    if any(item['goal_index_a'] == item['goal_index_b']
           or max(item['goal_index_a'], item['goal_index_b']) >= objective_count for item in accepted):
        raise DocumentError('Continuation answer query lies outside its bound problem')
    if not _same_mathematics(accepted, document["answers"]) or verified["execution_cursor"] != document["execution_cursor"]:
        raise DocumentError("Declared continuation answers or cursor differ from the verified prefix")
    return stored_problem, stored_config, verified


def import_continuation(path, *, reference_root, problem, configuration, source, profile):
    """Admit native provenance before constructing the lightweight SDK value."""
    from otqa.continuation import SolveContinuation
    from otqa.models.execution import ExecutionCursor
    from .serialization import domain_inputs, history_answers
    if source is None or profile is None:
        raise DocumentError('Native continuation import requires an actual source and execution profile')
    document = load_document("continuation", path, reference_root=reference_root)
    verify_continuation_document(document, reference_root=reference_root, problem=problem,
                                 configuration=configuration, source=source, profile=profile)
    domain_problem, policy, _, _, _ = domain_inputs(problem, configuration, None)
    history = history_answers({"answers": document["answers"]})
    return SolveContinuation(domain_problem, policy, history, ExecutionCursor(**document["execution_cursor"]))


def export_continuation(request):
    """Publish a new, self-contained proof bundle under the marked inputs tree."""
    from otqa.application_types import ContinuationExportOutcome
    from .journal import verify_prefix
    from .storage import create_directory, publish_bytes, publish_json
    from .validation import journal_policy, verify_result

    context = request.context
    root = Path(request.reference_root).resolve(strict=True)
    result_path = Path(request.result_path).resolve(strict=True)
    try:
        result_path.relative_to(root)
    except ValueError as exc:
        raise DocumentError("Result lies outside its explicit origin root") from exc
    manifest_path = result_path.parent / "manifest.json"
    manifest = load_document("manifest", manifest_path, reference_root=root)
    if manifest["schema_version"] != 2:
        raise DocumentError("Explicit continuation export requires a v2 origin")
    result = verify_result(result_path, root, manifest)
    proof = result["journal"]
    if proof is None or result["query_counts"]["dispatched_new"] != result["query_counts"]["answered_new"]:
        raise DocumentError("Result has no exportable confirmed answer boundary")
    raw = resolve_ref(root, {"path": proof["path"], "sha256": proof["sha256"]}).read_bytes()
    policy = journal_policy(manifest, root, manifest_path)
    policy.pop("manifest_sha256", None)
    verified = verify_prefix(raw, proof["valid_prefix_bytes"], proof["valid_prefix_sha256"],
                             proof["last_good_sequence"], **policy)
    answered_sequences = [event["sequence"] for event in verified["events"] if event["event_type"] == "answer_received"]
    if not answered_sequences:
        raise DocumentError("Origin has no durably accepted answer to export")
    last_answer = answered_sequences[-1]
    prefix = b"".join(raw.splitlines(keepends=True)[:last_answer])
    accepted_prefix = verify_prefix(prefix, len(prefix), digest(prefix), last_answer, **policy)
    origin_bytes = _collect_origin(root, manifest_path)
    destination = Path(request.output_dir).absolute()
    context.relative_output(destination, namespace="inputs")
    if destination.exists():
        raise DocumentError("Continuation output already exists")
    problem_bytes = resolve_ref(root, manifest["inputs"]["problem"]).read_bytes()
    config_bytes = resolve_ref(root, manifest["inputs"]["configuration"]).read_bytes()
    initial = []
    if manifest["inputs"]["initial_answers"] is not None:
        initial = read_json(resolve_ref(root, manifest["inputs"]["initial_answers"]))["answers"]
    if manifest["inputs"].get("continuation") is not None:
        initial = read_json(resolve_ref(root, manifest["inputs"]["continuation"]))["answers"]
    accepted = initial + [{**event["payload"]["query"], "answer": event["payload"]["answer"]}
                          for event in accepted_prefix["events"] if event["event_type"] == "answer_received"]
    create_directory(context, destination, namespace="inputs")
    for name, data in (("problem.json", problem_bytes), ("configuration.json", config_bytes),
                       ("origin-manifest.json", manifest_path.read_bytes()), ("journal-prefix.jsonl", prefix)):
        publish_bytes(context, destination / name, data, namespace="inputs")
    artifacts = []
    for relative, data in sorted(origin_bytes.items()):
        path = destination / "origin-artifacts" / relative
        publish_bytes(context, path, data, namespace="inputs")
        artifacts.append({"original_path": relative, "artifact": file_ref(path, context.project_root)})
    document = {"schema_version": 1, "algorithm_contract": "otqa-execution-v2",
        "problem": file_ref(destination / "problem.json", context.project_root),
        "configuration": file_ref(destination / "configuration.json", context.project_root),
        "answers": accepted, "execution_cursor": accepted_prefix["execution_cursor"],
        "origin_proof": {"manifest": file_ref(destination / "origin-manifest.json", context.project_root),
            "journal_prefix": file_ref(destination / "journal-prefix.jsonl", context.project_root),
            "valid_prefix_bytes": len(prefix), "valid_prefix_sha256": digest(prefix), "last_good_sequence": last_answer,
            "artifacts": artifacts}}
    verify_continuation_document(document, reference_root=context.project_root)
    output = destination / "continuation.json"
    publish_json(context, output, document, kind="continuation", namespace="inputs")
    return ContinuationExportOutcome(output, document, context.project_root)
