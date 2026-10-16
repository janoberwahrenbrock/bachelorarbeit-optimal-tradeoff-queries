# Portable series archives

A seal is an explicitly requested, byte-identical copy of a finished native
series. Ordinary audits and exports do not require it. Sealing does not run a
solver or grant qualification, and it does not change any calculation.

```python
from pathlib import Path
from uuid import uuid4
from otqa.runtime.project import load_project_context
from otqa.analysis.seal import seal_inventory, verify_seal

context = load_project_context(Path("/absolute/project"))
series = context.project_root / "runs" / "my-series"
output = series / "seals" / str(uuid4()) / "archive_inventory.json"
reference = seal_inventory(context, series, output)
inventory = verify_seal(output.parent, inventory_ref=reference)
```

`seal_series` is an alias for `seal_inventory`. The returned FileRef belongs to
the **new bundle root**, so its path is `archive_inventory.json`. Output must be a
new bundle below the explicit project's `runs/` directory; existing targets are
never overwritten. An external directory can receive a later copy of the
finished bundle, and `verify_seal` can verify that offline copy without a project
marker or access to the original series.

The first implementation accepts only `completed` or
`completed_with_failures` series with all jobs and attempts terminal, bound
results, no active job, and an ended or absent controller. The shared native
result reader checks each result against its manifest, input hashes and committed
journal proof before any archive output is created. Sealing does not rerun the
algorithm or independently recalculate oracle quality. It holds the series'
existing exclusive controller lock throughout the snapshot. Process identities
are admitted through the shared durable Intent → Registration → Grant/Manifest
chain, then checked against actual process-group state. A live or unknown group,
a contradictory recorded identity, or an unregistered spawn gap blocks sealing.
This deliberately includes some terminal bootstrap failures whose group absence
cannot be independently proved. It never stops processes to obtain a seal.

Every regular payload file present in the source is copied exactly once at its
relative path, including raw logs, original provenance, immutable inputs, states,
results and existing reports. There is no deduplication by content hash and no
rewriting of documents. Empty source directories are not payload. The source
root's own `archive_inventory.json` is not copied recursively. The source root's
reserved `seals/` namespace is excluded in its entirety: successive seals are
independent archives and never recursively copy previous archives. An in-series
destination must be below this namespace. Native SeriesRoot artifact references
cannot point into that excluded namespace. The check follows declared schema
reference positions, including journal proofs, without promoting free metadata
to reference edges. Original source-root provenance remains opaque original
bytes. Symlinks and special files in the included payload are rejected,
including internal symlinks.

The operation reserves the destination directory exclusively. It reads and
writes through no-follow directory/file descriptors, opens reads nonblocking
before checking the bound file type, completes short writes,
synchronizes payload bytes and directories, checks for changed source objects,
and verifies the complete copied payload before publishing the inventory last.
The inventory is the commit marker. A failed copy or barrier leaves an
uncommitted directory for inspection; without the inventory it is not a valid
seal, and a retry must choose a fresh destination. The checks establish the
implemented POSIX durability barriers; they are not a separate claim of tested
power-loss recovery on every filesystem.

The inventory lists sorted, unique relative file paths, byte counts and SHA-256
hashes. It excludes itself. `inventory_sha256` hashes the UTF-8 JSON encoding of
the sorted `files` list with sorted object keys, compact separators, no NaN and
no trailing newline. `verify_seal` rejects changed/missing/extra payload files,
extra directories, duplicate or unsorted inventory paths, an invalid inventory
digest, size/hash differences, symlinks and an absent commit marker. It checks
the archive's entire inventory rather than just a report's reference closure.
The optional `inventory_ref` checks the externally retained inventory hash.
Without an external reference, verification establishes internal consistency;
it cannot authenticate an archive whose payload and inventory were both replaced.

An offline seal is an **archive, not a relocated executable project**. Original
`ProjectBinding` values and source/build metadata remain byte-identical. A new
host/root cannot resume this series merely because the archive verifies. The
archive contains whatever code/environment artifacts were actually stored in
the source series; it does not claim to contain a complete installed wheel or
all external dependencies. An outer ZIP/tar file and its external archive hash
are separate operations.

## Multiple document versions

Reference validation dispatches by document kind and schema version. V2 execution
documents and their continuations are not skipped merely because an old reader
recognized only version one. Unchanged v1 input/source/profile records may share
the same closure. Raw copied continuation origin documents remain byte-identical
proof artifacts and are independently checked through their declared mapping.
Sealing preserves historical modulo/countdown semantics and original v1 digests;
it does not convert an old execution into the current algorithm contract.
