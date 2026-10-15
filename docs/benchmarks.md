# Reproducible benchmark workflow

Generate and store cases once, create explicit configuration selections, freeze a
plan on the execution host, then run the plan. A resumed series never regenerates
cases or silently changes worker count, grid, depth or stopping policy.

## Generate new inputs

```sh
otqa dataset generate --dataset-id pilot --master-seed 5721 \
  --objectives 3 5 --alternatives 5 --cases-per-shape 3 \
  --output inputs/datasets/pilot
```

Each shape/case uses its own `SeedSequence([master_seed, objective_count,
alternative_count, case_index])` and PCG64 generator. It draws the matrix first,
then Dirichlet(ones) weights, storing the values unchanged. Shape iteration order
does not change another case's stream. NumPy version and concrete seed provenance
are recorded. Stored bytes remain authoritative after library upgrades.

Prepare complete configuration documents and a selection JSON list containing
exactly one entry per configuration:

```json
[
  {"configuration_id":"fixed2","case_ids":["d3-m5-c000000","d3-m5-c000001"]},
  {"configuration_id":"adaptive2","case_ids":["d3-m5-c000000","d3-m5-c000001"]}
]
```

```sh
otqa suite create --source-root . --suite-id pilot \
  --dataset inputs/datasets/pilot/dataset.json \
  --config inputs/configurations/fixed2.json inputs/configurations/adaptive2.json \
  --selection-file inputs/selection.json --repetitions 1 \
  --output inputs/suites/pilot/suite.json
```

Suite creation runs no solver. It validates saved cases and the full configurations
and never interprets configuration IDs as defaults or overrides.

## Freeze and execute

Use a natively qualified profile for the execution host:

```sh
otqa benchmark plan --source-root . --suite inputs/suites/pilot/suite.json \
  --execution-profile runs/native-qualification/profile.json --output runs/pilot
otqa benchmark run --plan runs/pilot/plan.json
```

Cases run serially. The order is case, repetition, rotated configuration order;
the rotation offset is `(case_index + repetition_index) % configuration_count`.
This reduces systematic first-configuration ordering without randomizing inputs.
Eight solver workers mean eight root workers inside one case, not eight cases.

For a clean comparison, keep problem/oracle bytes, worker count, native threads,
numerical profile, cache policy, trace level, profiling and measurement boundaries
equal. Change only the intended algorithm configuration. A lower grid, smaller
depth, changed threshold or excluded hard case is a different method, not a code
performance optimization. Profiled runs are diagnostics and are not pooled with
unprofiled runtime measurements.

## Progress, interruptions and analysis

```sh
otqa benchmark status --series runs/pilot
otqa benchmark resume --series runs/pilot
otqa benchmark audit --series runs/pilot
otqa benchmark export --series runs/pilot --format csv --output runs/pilot/exports/jobs.csv
```

Live progress counts only the verified durable cursor. A partially evaluated query
is not a completed problem. Resume skips completed outcomes, including regular
no-query results, and terminal failures. It creates a fresh attempt for an
interrupted job only after group ownership and end are proven. Unknown starts
block rather than start a duplicate solver. All old attempts remain visible.

Reports separate the number of unique problems from repetitions and jobs. They
retain unsuccessful, incorrect, failed, pending and interrupted outcomes. A fast
regular no-query return contributes to completed-call time, not solution time.
Incorrect confidence selections contribute to solution time and their separate
incorrect count, not correct-solution time. All measured controller attempt costs
remain available, including failed attempts; unknown times are counted explicitly.

Statistics include sample size, total, mean, median, range and linear p90. One to
three original problems provide pilot observations rather than a population
estimate. A projected `100 × mean completed attempt cost` estimates attempt cost,
not the time needed for 100 correct solutions. Independent repeated trials remain
distinguishable from unique problem instances.

API call time includes synchronous provider, recorder, observer and worker
lifecycle costs. Case time and controller time have narrower documented endpoints
and do not substitute for an externally measured complete CLI duration.

Generated dataset and suite directories are reserved with exclusive directory
creation. An existing directory, including an empty directory created concurrently,
is never replaced. The final `dataset.json` or `suite.json` is the commit marker,
published only after its payload files and directories are durable. A failed
creation may retain forensic payload files without that final entrypoint; it is
not a usable dataset/suite and is not silently retried or overwritten.
