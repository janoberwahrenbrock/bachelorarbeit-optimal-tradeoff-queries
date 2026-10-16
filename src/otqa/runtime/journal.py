"""Versioned journal readers with strict execution-cycle and durable cursor binding."""
from __future__ import annotations
from . import journal_v1 as legacy
from .codec import DocumentError, decode, digest, mathematical_hex
from .schema import validate
from .journal_structure import _fold_validated_events, mathematically_equal, validate_planning

actual_stop = legacy.actual_stop


def verify_planning_policy(planning, algorithm, answered_total, *, requested_depth=None):
    if 'min_expected_progress' not in algorithm:
        return legacy.verify_planning_policy(planning, algorithm, answered_total)
    depth = algorithm['depth'] if requested_depth is None else requested_depth
    if planning['planning_stop_aware'] != (algorithm['planning_evaluation'] == 'stop_aware'):
        raise DocumentError('Recorded planning path differs from its effective policy')
    expected = {depth} if algorithm['query_strategy'] == 'fixed' else set(range(1, depth + 1))
    if {h['horizon'] for h in planning['horizons']} != expected:
        raise DocumentError('Recorded horizon coverage differs from the effective policy')
    if planning['selected']['horizon'] not in expected or planning['selected']['score']['kind'] != algorithm['query_strategy']:
        raise DocumentError('Selected plan differs from the effective strategy/horizon')
    validate_planning(planning)


def _equal(left, right, message):
    if not mathematically_equal(left, right):
        raise DocumentError(message)


def _progress(evidence, plan, algorithm, count):
    if evidence is None or plan is None:
        raise DocumentError('Progress evidence lacks its evaluated plan')
    validate_planning(plan)
    score = plan['selected']['score']
    if score['kind'] != algorithm['query_strategy'] or plan['planning_stop_aware'] != (algorithm['planning_evaluation'] == 'stop_aware'):
        raise DocumentError('Progress witness uses a different strategy or planning evaluation')
    basis = 'effective_loss' if algorithm['planning_evaluation'] == 'stop_aware' else 'candidate_count'
    terminal = score['expected_terminal_loss' if basis == 'effective_loss' else 'expected_terminal_candidates']
    expected = float(count) - float(terminal)
    threshold = algorithm['min_expected_progress']
    valid = threshold is None or expected > threshold
    _equal(evidence, {'basis': basis, 'starting_value': float(count), 'expected_terminal_value': terminal,
        'expected_progress': expected, 'threshold': threshold, 'comparison': 'strict_greater', 'admissible': valid},
        'Stored progress, binary64 subtraction or strict threshold comparison differs')
    if score['kind'] == 'reduction_per_query':
        _equal(score['gain'], expected, 'Adaptive gain differs from terminal loss')
        _equal(score['rate'], expected / score['expected_queries'], 'Adaptive rate differs from gain/cost')
    return valid, expected


def _attempt(attempt, algorithm, count):
    depth = attempt['requested_depth']
    expected = [depth] if algorithm['query_strategy'] == 'fixed' else list(range(1, depth + 1))
    if attempt['evaluated_horizons'] != expected or [h['horizon'] for h in attempt['horizon_evidence']] != expected:
        raise DocumentError('Planning attempt omitted or repeated a required horizon')
    available, witnesses = [], []
    for h in attempt['horizon_evidence']:
        if h['generated_query_count'] != h['evaluated_query_count']:
            raise DocumentError('Planning horizon does not cover its complete generated query inventory')
        if h['outcome'] == 'no_query':
            if h['evaluated_query_count'] != 0 or any(h[k] is not None for k in ('selected_plan', 'selected_progress', 'best_progress_witness', 'best_progress')):
                raise DocumentError('NoQuery evidence claims an evaluated available plan')
            continue
        if h['evaluated_query_count'] == 0:
            raise DocumentError('Progress evidence claims a plan without evaluated queries')
        witness = h['best_progress_witness']
        ok, gain = _progress(h['best_progress'], witness, algorithm, count)
        if witness['selected']['horizon'] != h['horizon']:
            raise DocumentError('Progress witness belongs to a different horizon')
        witnesses.append((gain, witness))
        if h['outcome'] == 'available':
            valid, selected_gain = _progress(h['selected_progress'], h['selected_plan'], algorithm, count)
            if not valid or not ok or selected_gain > gain:
                raise DocumentError('Selected plan is inadmissible or exceeds its maximum-progress witness')
            if h['selected_plan']['selected']['horizon'] != h['horizon']:
                raise DocumentError('Selected plan belongs to a different horizon')
            available.append(h['selected_plan'])
        elif ok or h['selected_plan'] is not None or h['selected_progress'] is not None:
            raise DocumentError('Insufficient-progress horizon has an admissible plan')
    expected_outcome = 'available' if available else 'insufficient_expected_progress' if witnesses else 'no_query'
    if attempt['outcome'] != expected_outcome:
        raise DocumentError('Attempt outcome disagrees with required horizon evidence')
    selected = attempt['selected_plan']
    if available:
        if selected is None or not any(mathematically_equal(selected['selected'], p['selected']) for p in available):
            raise DocumentError('Attempt winner is absent from its eligible horizon plans')
        _progress(attempt['selected_progress'], selected, algorithm, count)
        if algorithm['query_strategy'] == 'reduction_per_query':
            def rank(plan):
                item = plan['selected']
                query, score = item['query'], item['score']
                return (-score['rate'], score['expected_queries'], item['horizon'],
                    query['goal_index_a'], query['goal_index_b'], query['value'])
            expected_winner = min(available, key=rank)
            _equal(selected['selected'], expected_winner['selected'], 'Adaptive winner differs from the eligible horizon ranking')
        verify_planning_policy(selected, algorithm, 0, requested_depth=depth)
    elif selected is not None or attempt['selected_progress'] is not None:
        raise DocumentError('Terminal planning attempt retains a selected plan')
    witness = attempt['best_progress_witness']
    if witnesses:
        maximum = max(g for g, _ in witnesses)
        if witness is None or not any(g == maximum and mathematically_equal(witness['selected'], p['selected']) for g, p in witnesses):
            raise DocumentError('Attempt lacks its maximum-progress witness')
    elif witness is not None:
        raise DocumentError('Empty query inventory retains a progress witness')


def _verify_v2_policy(events, algorithm, budget, alternative_ids, initial_execution_cursor=None):
    state = None
    cursor = events[0]['payload']['execution_cursor']
    if initial_execution_cursor is not None:
        _equal(cursor, initial_execution_cursor, 'Journal initial cursor differs from manifest')
    depth = algorithm['depth']
    if not 1 <= cursor['remaining_depth'] <= depth:
        raise DocumentError('Initial cursor exceeds configured depth')
    countdown = algorithm['horizon_execution'] == 'countdown'
    if not countdown and cursor['remaining_depth'] != depth:
        raise DocumentError('Receding execution retains a shortened horizon')
    attempts, begun, cycle = [], None, None
    cycles = []
    started_count = completed_count = fallback_count = 0
    for event in events:
        kind, p = event['event_type'], event['payload']
        if kind == 'state_analyzed':
            state = p
            _equal(p['execution_cursor'], cursor, 'Actual state cursor differs from accepted answers')
            if p['state_index'] != cursor['answered_total']:
                raise DocumentError('Actual state index differs from execution cursor')
            actual_stop(state, algorithm, budget, alternative_ids)
        elif kind == 'planning_attempt_started':
            if state is None or actual_stop(state, algorithm, budget, alternative_ids)[0] is not None or begun is not None:
                raise DocumentError('Planning began without a nonterminal current state')
            if cycle is not None:
                raise DocumentError('Planning began again after this state was already resolved')
            if p['state_before_index'] != cursor['answered_total'] or p['attempt_index'] != len(attempts) + 1:
                raise DocumentError('Planning attempt has wrong state or ordinal')
            _equal(p['execution_cursor'], cursor, 'Planning attempt changed the cursor')
            expected = cursor['remaining_depth']
            if attempts:
                if not countdown or expected == depth or attempts[0]['outcome'] == 'available' or len(attempts) != 1:
                    raise DocumentError('Unjustified or repeated countdown fallback')
                expected = depth
            if p['requested_depth'] != expected:
                raise DocumentError('Planning attempt uses the wrong remaining/full horizon')
            begun = p
            started_count += 1
        elif kind == 'planning_attempt_completed':
            if begun is None or p['state_before_index'] != begun['state_before_index'] or p['attempt_index'] != begun['attempt_index']:
                raise DocumentError('Attempt completion has no matching start')
            _equal(p['execution_cursor'], cursor, 'Completed attempt changed the cursor')
            if p['attempt']['requested_depth'] != begun['requested_depth']:
                raise DocumentError('Completed attempt changed its requested horizon')
            _attempt(p['attempt'], algorithm, len(state['candidate_ids']))
            attempts.append(p['attempt'])
            begun = None
            completed_count += 1
        elif kind == 'planning_resolved':
            c = p['cycle']
            if state is None or begun is not None or not attempts or cycle is not None or p['state_before_index'] != cursor['answered_total']:
                raise DocumentError('Resolved cycle lacks its completed actual attempts')
            _equal(c['cursor_before'], cursor, 'Resolved cycle changed initial cursor')
            _equal(c['attempts'], attempts, 'Resolved cycle differs from actual planning attempts')
            last = attempts[-1]
            requires_fallback = countdown and cursor['remaining_depth'] < depth and attempts[0]['outcome'] != 'available'
            if len(attempts) != (2 if requires_fallback else 1):
                raise DocumentError('Shortened countdown lacks its full fallback attempt')
            reason = attempts[0]['outcome'] if requires_fallback else None
            if c['restart_reason'] != reason or c['outcome'] != last['outcome']:
                raise DocumentError('Cycle fallback reason/outcome differs')
            _equal(c['selected_plan'], last['selected_plan'], 'Cycle winner differs from final actual attempt')
            proposal = None
            if last['outcome'] == 'available':
                h = last['selected_plan']['selected']['horizon']
                proposal = {'answered_total': cursor['answered_total'] + 1,
                    'remaining_depth': h - 1 if countdown and h > 1 else depth}
                if requires_fallback:
                    fallback_count += 1
            _equal(c['proposed_cursor_after_answer'], proposal, 'Cycle proposes wrong post-answer cursor')
            cycle = c
            cycles.append(c)
        elif kind == 'query_planned':
            if cycle is None or cycle['outcome'] != 'available' or p['state_before_index'] != cursor['answered_total']:
                raise DocumentError('Query has no available resolved planning cycle')
            _equal(p['planning'], cycle['selected_plan'], 'Query differs from resolved selection')
        elif kind == 'answer_received':
            if cycle is None:
                raise DocumentError('Accepted answer has no resolved planning cycle')
            _equal(p['execution_cursor'], cycle['proposed_cursor_after_answer'], 'Answer advanced the wrong execution phase')
            cursor = p['execution_cursor']
        elif kind == 'query_completed':
            _equal(p['planning_cycle'], cycle, 'Query record lost its actual planning cycle')
            attempts, begun, cycle = [], None, None
        elif kind == 'run_finished':
            if state is None:
                raise DocumentError('Normal finish lacks an actual state')
            _equal(p['execution_cursor'], cursor, 'Terminal cursor differs from accepted answers')
            expected, _ = actual_stop(state, algorithm, budget, alternative_ids)
            if expected is None:
                if cycle is None or cycle['outcome'] not in ('no_query', 'insufficient_expected_progress'):
                    raise DocumentError('Planning termination lacks its terminal decision evidence')
                expected = cycle['outcome']
            if p['termination_reason'] != expected:
                raise DocumentError('Terminal reason violates stopping precedence or planning evidence')
    return {'execution_cursor': cursor, 'planning_cycles': cycles, 'planning_attempts_started': started_count,
        'planning_attempts_completed': completed_count, 'fallback_selections': fallback_count, 'active_planning_attempt': begun}


def verify_actual_policy(events, algorithm, budget, alternative_ids):
    if events and events[0].get('schema_version') == 2:
        return _verify_v2_policy(events, algorithm, budget, alternative_ids)
    return legacy.verify_actual_policy(events, algorithm, budget, alternative_ids)


def verify_prefix(data, byte_count, sha256, last_sequence, *, initial_answers=0, algorithm=None, budget=None,
                  alternative_ids=None, initial_execution_cursor=None, manifest_sha256=None):
    first = decode(data.split(b'\n', 1)[0]) if data else {}
    if first.get('schema_version') != 2:
        result = legacy.verify_prefix(data, byte_count, sha256, last_sequence, initial_answers=initial_answers,
            algorithm=algorithm, budget=budget, alternative_ids=alternative_ids)
    else:
        if type(byte_count) is not int or byte_count <= 0 or byte_count > len(data):
            raise DocumentError('Cursor extends beyond available journal bytes')
        prefix = data[:byte_count]
        if digest(prefix) != sha256 or not prefix.endswith(b'\n'):
            raise DocumentError('Journal prefix digest or complete-line boundary differs')
        events, projected = [], []
        last_monotonic = None
        for sequence, line in enumerate(prefix.splitlines(), 1):
            e = validate('event', decode(line))
            if e['schema_version'] != 2 or e['sequence'] != sequence:
                raise DocumentError('Journal version changed or nonconsecutive sequence')
            if events and (e['run_id'], e['attempt_id']) != (events[0]['run_id'], events[0]['attempt_id']):
                raise DocumentError('Journal identity changed')
            if last_monotonic is not None and e['monotonic_ns'] < last_monotonic:
                raise DocumentError('Journal monotonic timestamp regressed')
            last_monotonic = e['monotonic_ns']
            if e['numeric_hex'] != mathematical_hex(e['payload'], '/payload'):
                raise DocumentError('Incomplete or incorrect event binary64 evidence')
            if events and events[-1]['event_type'] in ('run_finished', 'run_failed', 'run_interrupted'):
                raise DocumentError('Event follows a terminal event')
            events.append(e)
            if e['event_type'].startswith('planning_'):
                if e['query_id'] is not None:
                    raise DocumentError('Planning-cycle evidence claims an actual query ID')
                continue
            p = dict(e['payload'])
            p.pop('execution_cursor', None)
            p.pop('planning_cycle', None)
            if p.get('termination_reason') == 'insufficient_expected_progress':
                p['termination_reason'] = 'no_query'
            # These are private semantic records, not synthetic v1 wire bytes.
            # The retained fields already passed the original v2 schema and
            # binary64 checks; stripping only the declared v2 extensions needs
            # no second JSON/schema/hex roundtrip.
            projected.append({'run_id': e['run_id'], 'attempt_id': e['attempt_id'],
                'occurred_at_utc': e['occurred_at_utc'], 'event_type': e['event_type'],
                'query_id': e['query_id'], 'payload': p})
        if len(events) != last_sequence or not events:
            raise DocumentError('Cursor last sequence differs from verified prefix')
        result = _fold_validated_events(projected, len(projected), initial_answers=initial_answers)
        result['events'] = events
        result['last_event_type'] = events[-1]['event_type']
        result['last_state'] = next((e['payload'] for e in reversed(events) if e['event_type'] == 'state_analyzed'), None)
        if any(x is not None for x in (algorithm, budget, alternative_ids)):
            if any(x is None for x in (algorithm, budget, alternative_ids)):
                raise DocumentError('Actual policy verification requires policy, budget and alternative IDs together')
            result.update(_verify_v2_policy(events, algorithm, budget, alternative_ids, initial_execution_cursor))
        else:
            result['execution_cursor'] = next((e['payload']['execution_cursor'] for e in reversed(events)
                if 'execution_cursor' in e['payload']), None)
        if events[-1]['event_type'].startswith('planning_'):
            result['query_phase'] = 'planning'
    if manifest_sha256 is not None and result['events'][0]['payload']['manifest_sha256'] != manifest_sha256:
        raise DocumentError('Cursor prefix start does not bind its actual manifest')
    return result


def verify_cursor(data, cursor, *, initial_answers=0, algorithm=None, budget=None, alternative_ids=None,
                  manifest_sha256=None, initial_execution_cursor=None):
    result = verify_prefix(data, cursor['valid_prefix_bytes'], cursor['valid_prefix_sha256'], cursor['last_good_sequence'],
        initial_answers=initial_answers, algorithm=algorithm, budget=budget, alternative_ids=alternative_ids,
        manifest_sha256=manifest_sha256, initial_execution_cursor=initial_execution_cursor)
    if cursor.get('schema_version') != result['events'][0]['schema_version']:
        raise DocumentError('Cursor schema version differs from its journal contract')
    keys = ('run_id', 'attempt_id', 'query_counts', 'query_phase', 'active_query_id')
    if cursor.get('schema_version') == 2:
        keys += ('execution_cursor',)
    for key in keys:
        if not mathematically_equal(cursor[key], result[key]):
            raise DocumentError(f'Cursor {key} differs from its verified journal prefix')
    return result
