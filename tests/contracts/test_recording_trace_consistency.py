"""Retained full trees must agree at attempt, selection, dispatch and result."""
from uuid import uuid4

import pytest

from otqa import AlgorithmPolicy, Problem, SingleCandidateStop, VolumeConfidenceStop, solve
from otqa.answers import SimulatedAnswers
from otqa.runtime.codec import encode
from otqa.runtime.journal import verify_cursor
from otqa.runtime.processes import process_identity
from otqa.runtime.project import load_project_context
from otqa.runtime.recorder import WireRecorder
from otqa.runtime.serialization import record_wire
from otqa.runtime.storage import RunStore, create_directory


@pytest.mark.parametrize('trace', ['standard', 'full'])
@pytest.mark.parametrize('strategy,mode', [('fixed', 'receding'), ('fixed', 'countdown'),
                                          ('reduction_per_query', 'receding')])
@pytest.mark.parametrize('evaluation', ['candidate_count', 'stop_aware'])
def test_live_recording_projects_the_same_selected_plan_everywhere(tmp_path, trace, strategy, mode, evaluation):
    (tmp_path / 'otqa-project.json').write_bytes(encode({'schema_version': 1,
        'project_kind': 'otqa_project', 'project_id': str(uuid4())}))
    context = load_project_context(tmp_path)
    attempt = tmp_path / 'runs' / 'trace'
    create_directory(context, attempt)
    cursor = {'answered_total': 0, 'remaining_depth': 2}
    store = RunStore(context, attempt, attempt, str(uuid4()), 'attempt0001', process_identity(uuid4().hex),
                     0, schema_version=2, execution_cursor=cursor)
    aware = evaluation == 'stop_aware'
    recorder = WireRecorder(store, ['a', 'b', 'c'], stop_aware=aware, trace_level=trace)
    recorder.event('run_started', {'manifest_sha256': 'a' * 64}, commit=True)
    stopping = VolumeConfidenceStop(.99) if aware else SingleCandidateStop()
    policy = AlgorithmPolicy(strategy, 2, 'both', 5, evaluation, stopping, horizon_execution=mode)
    try:
        result = solve(Problem(((1., 0.), (0., 1.), (.6, .6))), policy,
                       SimulatedAnswers((.9, .1)), recorder=recorder)
        recorder.event('run_finished', {'termination_reason': result.termination_reason,
            'solved': result.solved, 'query_counts': dict(store.counts)}, commit=True)
        algorithm = {'query_strategy': strategy, 'depth': 2, 'higher_depth_query_source': 'both',
            'grid_size': 5, 'planning_evaluation': evaluation,
            'stopping': {'rule': 'volume_confidence', 'threshold': .99} if aware else {'rule': 'single_candidate'},
            'horizon_execution': mode, 'min_expected_progress': .001}
        verified = verify_cursor((attempt / 'events.jsonl').read_bytes(), store.cursor,
            algorithm=algorithm, budget={'max_queries': None}, alternative_ids=['a', 'b', 'c'],
            initial_execution_cursor=cursor)
        planned = [event['payload']['planning'] for event in verified['events'] if event['event_type'] == 'query_planned']
        cycles = verified['planning_cycles']
        for plan, cycle, record in zip(planned, cycles, result.queries, strict=True):
            assert plan == cycle['selected_plan']
            assert (plan['plan_tree'] is not None) == (trace == 'full')
            wire = record_wire(record, 'q000001', stop_aware=aware, trace_level=trace)
            assert wire['planning'] == wire['planning_cycle']['selected_plan'] == plan
    finally:
        store.close()
