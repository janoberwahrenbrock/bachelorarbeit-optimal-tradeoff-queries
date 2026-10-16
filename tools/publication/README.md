# Study publication bundles

`study_bundle.py` is a Python standard-library tool, independent of the solver.
It packages an explicitly reviewed file manifest into a reproducible ZIP and
verifies downloaded bundles. It never starts experiments or restores processes.
The supported interpreters are Python 3.13 and 3.14 on Linux and macOS.

The manifest has `schema_version: 1`, a nonempty `study_id`, and a `files` list
sorted by the unique `path` field. Every file record contains:

- `path`: portable project-relative location inside the download;
- `source_path`: original project-relative source location;
- `bytes`: exact original byte count;
- `sha256`: lowercase SHA-256 of the original bytes.

Additional metadata is allowed. Sources may be mapped to a new destination path;
the manifest preserves that mapping. The original source files are never edited.
Symlink sources and unsafe paths are refused. The `_publication/` directory is
reserved for the exact supplied manifest bytes embedded in the archive.

```sh
python tools/publication/study_bundle.py build \
  --project-root /absolute/path/to/project \
  --manifest /absolute/path/to/publication-manifest.json \
  --output /absolute/path/to/study-data.zip

python tools/publication/study_bundle.py verify \
  --manifest /absolute/path/to/publication-manifest.json \
  --archive /absolute/path/to/study-data.zip \
  --destination /absolute/path/to/fresh-extracted-project
```

Build exclusively creates a new output file and removes an incomplete output on
failure. Fixed timestamps, permissions, entry order and compression settings make
repeated builds byte-identical on the same Python/zlib implementation. Different
zlib implementations can produce different compressed bytes; the original file
hashes remain the authoritative cross-environment identity. The final archive must
be smaller than 2 GiB. No automatic splitting is performed.

Verification checks exact membership, the embedded manifest bytes, every file size
and SHA-256, and refuses duplicate members, traversal and symlinks. Extraction is
optional and requires a destination that does not exist. It occurs only after all
content has passed validation. Extracted paths preserve the manifest layout and
add only `_publication/publication-manifest.json`. A failed extraction is removed.

Both operations print one compact JSON receipt including file/byte totals and
archive/manifest hashes. Verification uses the supplied manifest as its trust
anchor: publish its checksum separately, and compare the receipt with that source.

The original sealed study directories and backup copies remain untouched. A
publication archive is a scientific data download, not a process-resumption image.

`compare_analysis.py --reference RESULTS.json` recomputes condition means from
saved individual observations. Add `--reproduced FRESH_RESULTS.json` to compare
an independently regenerated analysis with the published one. Only the generated
timestamp is excluded; all scientific values and provenance must match.
