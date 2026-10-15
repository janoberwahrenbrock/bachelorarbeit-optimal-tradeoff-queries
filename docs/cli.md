# Command-line execution

`otqa --help` lists the commands. The CLI imports no NumPy or SciPy before it has
selected the native thread environment. All command paths are resolved against
the invocation directory, even when `--project-root` points somewhere else.

The explicit project root contains `otqa-project.json`. A command does not search
parent directories, infer a Git root, or create a marker automatically. When
running outside the marked directory, use:

```sh
otqa --project-root /absolute/project benchmark status --series /absolute/project/runs/my-series
```

## Installation and native qualification

Build and install the wheel using the project's documented development workflow.
An editable installation is suitable for development and SDK use; it does not
pass the installed-distribution qualification control. Use the Python interpreter
containing the wheel to run the native harness:

```sh
python tools/qualification/qualify.py --project-root "$PWD" \
  --output "$PWD/runs/native-qualification" --scope standalone
```

The `standalone` scope is sufficient for standalone solves on either host and
for series on macOS. Linux `benchmark plan`, `run` and `resume` require the
`series_linux_recovery` scope; a standalone-only profile cannot admit them.
For a Linux benchmark series, qualify a fresh output destination instead:

```sh
python tools/qualification/qualify.py --project-root "$PWD" \
  --output "$PWD/runs/native-qualification-linux" --scope series_linux_recovery
```

Use `runs/native-qualification-linux/profile.json` as `--execution-profile` in
the benchmark examples below when running on Linux. A Mac cannot qualify Linux
recovery. The harness writes all observations, including failures,
under its output root. Only a completely passing run creates a new `profile.json`
with a validated native runtime certificate. A failed run retains its candidate
profile and failed evidence. Public commands have no trust or skip switch.

Native qualification covers installation, backend behavior, analytical controls,
SDK lifecycle and the requested persistence/process scope. It does not assert
mathematical equivalence to another implementation or performance acceptance.

## Solve one problem

```sh
otqa solve --source-root . --problem inputs/problem.json \
  --config inputs/config.json --execution-profile runs/native-qualification/profile.json \
  --answers simulated --oracle inputs/oracle.json --output runs/first-problem
```

All options shown are required. `--answers interactive` prompts on stderr and
accepts exactly `<`, `=` or `>`; invalid text repeats the same prompt. `--answers
replay --answers-file inputs/replay.json` consumes exact ordered query identities.
A changed value, objective order or exhausted script fails visibly. The full
script remains stored, including any suffix unused because the solver stopped.

`--initial-answers inputs/initial.json` declares a separate continuation run. Its
answers count toward the query budget and are never queried again. A benchmark
retry instead starts a fresh attempt from the original problem.

The complete configuration is supplied through `--config`. There are no scalar
depth, grid, worker or confidence flags that override its contents. Answer
probabilities are always computed geometrically; the final planning level uses
ratio queries. Fixed/adaptive depth and candidate-count/stop-aware evaluation are
independent policy choices.

Each standalone invocation uses the same isolated CaseProcess supervisor and
durable recorder as a benchmark attempt. Existing output directories are never
overwritten. New outputs must remain under the marked project's real `runs/`
directory; symlinks in the entire output chain are rejected.

## Serial benchmark commands

```sh
otqa benchmark plan --source-root . --suite inputs/suites/pilot/suite.json \
  --execution-profile runs/native-qualification/profile.json --output runs/pilot
otqa benchmark run --plan runs/pilot/plan.json
otqa benchmark status --series runs/pilot
otqa benchmark resume --series runs/pilot
otqa benchmark audit --series runs/pilot
otqa benchmark export --series runs/pilot --format json --output runs/pilot/exports/jobs.json
```

Plan freezes the input closure and job order on the execution host. Run starts
one case at a time; configured solver workers operate inside that case. Status
reports committed cursor progress and actual process ownership without starting
or stopping a solver.

Resume preserves every old attempt. It skips terminal completed and failed jobs
and retries interrupted jobs once per invocation. A live group, unknown process
ownership, or an unproven durable start blocks automatic resume. A readable start
line alone never supplies a missing start cursor. A failed terminal job requires
a new series for another measurement.

An audit creates `reports/<UUID>/audit.json` plus its own immutable state and
prefix snapshots. To export one particular snapshot, use its exact series-relative
path; there is no implicit latest selection:

```sh
otqa benchmark export --series runs/pilot --audit-ref reports/REPORT_UUID/audit.json \
  --format csv --output runs/pilot/exports/selected.csv
```

Without `--audit-ref`, export creates exactly one fresh audit and uses only that
snapshot. JSON and CSV preserve every planned job and all attempt-result links.

## Portable archive

After the series and all its groups have ended:

```sh
otqa benchmark seal --series runs/pilot
```

This creates a new bundle below `runs/pilot/seals/<UUID>/` and returns its
inventory FileRef. `--output runs/archive-name/archive_inventory.json` selects a
different new bundle inside the same project. Nothing is overwritten. A live or
unknown group, unfinished attempt or invalid raw artifact blocks the operation.
The inventory is published last; an unfinished destination is not a valid
archive. [Portable archives](seal.md) explains offline verification and its
distinction from executable project relocation.

## Exit status and timing

| Code | Meaning |
|---:|---|
| 0 | `solve` or benchmark `run`/`resume`: regular solved outcome(s); setup, status, audit, export and seal: command success |
| 3 | `solve` or benchmark `run`/`resume`: at least one regular unresolved outcome, including no-query and query-budget returns |
| 2 | Invalid input, unsupported document, argument combination or output conflict |
| 1 | Runtime, replay, watchdog, integrity or process-ownership failure |
| 130 | User interruption |

A successful setup, status or analysis command does not assert that its series
contains only solved problems. Likewise, a regular confidence selection can
independently be incorrect; inspect the recorded quality fields.

Structured references and diagnostics go to stdout; prompts and logs are separate.
The optional case watchdog changes no algorithm parameter and returns no partial
plan as a completed solution. Complete API time includes synchronous callbacks
and worker lifetime. Case bootstrap and controller costs are separately scoped;
after a crash, unknown complete API time remains null.
