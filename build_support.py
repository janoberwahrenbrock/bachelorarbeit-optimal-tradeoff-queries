"""Distribution hooks: generate and verify immutable source build metadata."""
from __future__ import annotations

import importlib.util
import subprocess
import tomllib
from pathlib import Path

from setuptools.command.build_py import build_py
from setuptools.command.sdist import sdist

ROOT = Path(__file__).resolve().parent


def source_tools():
    path = ROOT / 'src' / 'otqa' / '_build_metadata.py'
    spec = importlib.util.spec_from_file_location('otqa_build_metadata', path)
    if spec is None or spec.loader is None:
        raise RuntimeError('cannot load dependency-free source identity helpers')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def build_provenance() -> tuple[str, str | None, bool]:
    version = tomllib.loads((ROOT / 'pyproject.toml').read_text())['project']['version']
    try:
        commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT,
                                         stderr=subprocess.DEVNULL, text=True).strip()
        dirty = bool(subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT, text=True))
    except (OSError, subprocess.CalledProcessError):
        commit, dirty = None, True
    return version, commit, dirty


def stamp(package_root: Path) -> None:
    source_tools().write_build_metadata(package_root, *build_provenance(), preserve_existing=True)


class BuildPy(build_py):
    def run(self) -> None:
        # build/lib may retain stamps from a previous build of this checkout.
        # Only stamps present in an input sdist carry preserved provenance.
        for name in ('_source_inventory.json', '_build_provenance.json'):
            stale = Path(self.build_lib) / 'otqa' / name
            if stale.exists():
                stale.unlink()
        super().run()
        stamp(Path(self.build_lib) / 'otqa')


class SourceDist(sdist):
    def make_release_tree(self, base_dir, files) -> None:
        super().make_release_tree(base_dir, files)
        stamp(Path(base_dir) / 'src' / 'otqa')
