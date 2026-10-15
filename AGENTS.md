# Working agreements

This repository is a standalone implementation of the Optimal Tradeoff Query algorithm. Maintain the documented mathematical behavior and explicit configuration boundaries.

- `models` and `config` are lightweight domain modules. They must not import numerical libraries, runtime, CLI, experiments, or analysis.
- Numerical, geometry, state, query, planning, and solver modules do not read files, set thread environment variables, or know run IDs, target weights, and oracle winners.
- Keep state ownership and history unambiguous. Mutable native models and bounded caches belong to one solver or worker session; never clear another session's caches.
- Use the same solver loop for SDK and application runs. Required recorders fail closed. Persisted cursor claims must reflect successful durable barriers.
- Store new run artifacts inside the explicitly marked project under `runs/`. Preserve all attempts, unfinished jobs, errors, and original inputs. Do not overwrite terminal artifacts.
- Keep fixtures independently constructed and analytical where possible. Runtime and CI must work without another checkout or personal machine paths.
- Do not change grid, depth, query sources, branch coverage, tolerances, or success denominators to obtain faster timings. Validate numerical values and query identity before comparing complete unprofiled runtimes.
- Add specific tests and current product documentation with each implemented contract. Document untested guarantees and inconclusive measurements honestly.

Development commands are in `docs/development.md`. Run the relevant tests before committing. Release checks include a built wheel installed outside the checkout and verified source build metadata.
