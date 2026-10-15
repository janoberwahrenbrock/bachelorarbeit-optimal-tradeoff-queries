"""Fast analytical checks against an installed wheel, outside the checkout.

Run with isolated Python (-I). This is a functional packaging check, without
legacy sources, benchmark data, process workers or a performance acceptance claim.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
import sysconfig
import time


def main() -> None:
    started = time.perf_counter()
    import otqa
    from otqa.answers import SimulatedAnswers
    from otqa.geometry import GeometrySession
    from otqa.numerics.lp import LinearProgramBackend
    from otqa.numerics.profile import actual_backend_capabilities
    from otqa.runtime.source import loaded_source

    package = Path(otqa.__file__).resolve().parent
    installed_roots = {Path(sysconfig.get_path(name)).resolve() for name in ('purelib', 'platlib')}
    assert any(package.is_relative_to(root) for root in installed_roots), (
        'The smoke check must load the installed distribution', package, installed_roots,
    )
    source_before = loaded_source()
    capabilities = actual_backend_capabilities()
    assert capabilities['scipy_highs'] and capabilities['scipy_qhull']

    backend = LinearProgramBackend()
    try:
        optimum = backend.solve(c=[-1.], A_ub=[[1.]], b_ub=[2.], bounds=[(None, None)])
        assert optimum.success and math.isclose(float(optimum.fun), -2., abs_tol=1e-12)
    finally:
        backend.close()
    with GeometrySession() as geometry:
        volume = geometry.volume(geometry.weight_space((), 3))
        assert math.isclose(volume, math.sqrt(3.) / 2., rel_tol=0., abs_tol=1e-12)

    # All three alternatives are useful: A0 and A1 win at the respective ends,
    # while (.6,.6) wins around equal weights. Raw weights (.9,.1) select A0.
    problem = otqa.Problem(((1., 0.), (0., 1.), (.6, .6)))
    policies = (
        otqa.AlgorithmPolicy('fixed', 2, 'both', 5, 'candidate_count', otqa.SingleCandidateStop()),
        otqa.AlgorithmPolicy('reduction_per_query', 3, 'both', 5, 'stop_aware', otqa.VolumeConfidenceStop(.99)),
    )
    results = []
    for policy in policies:
        result = otqa.solve(problem, policy, SimulatedAnswers((.9, .1)),
                            execution=otqa.SolverExecution(1), budget=otqa.QueryBudget(16))
        assert result.solved and result.selected_candidate_index == 0
        assert result.query_counts.answered_new > 0
        assert result.query_counts.initial_answers == 0
        horizons = [item.horizon for item in result.queries[0].planning.horizons]
        assert horizons == ([2] if policy.query_strategy == 'fixed' else [1, 2, 3])
        if isinstance(policy.stopping, otqa.SingleCandidateStop):
            assert result.exactly_solved and result.final_state.candidate_indices == (0,)
        else:
            assert result.selected_candidate_volume_share >= .99
        results.append({'strategy': policy.query_strategy, 'depth': policy.depth,
                        'initial_answers': result.query_counts.initial_answers, 'evaluated_horizons': horizons,
                        'answered_new': result.query_counts.answered_new,
                        'selected_candidate_index': result.selected_candidate_index})
    assert loaded_source() == source_before, 'Installed source changed during the checks'
    print(json.dumps({'status': 'passed', 'scope': 'installed analytical functional smoke',
                      'version': otqa.__version__, 'package': str(package), 'source': source_before[0],
                      'backend_capabilities': capabilities, 'solves': results,
                      'elapsed_seconds': time.perf_counter() - started}, sort_keys=True))


if __name__ == '__main__':
    main()
