"""Distribution hooks: generate and verify immutable source build metadata."""
from __future__ import annotations

import importlib.util
import shutil
import subprocess
import tempfile
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


def _normalized_build_path(path: Path) -> Path:
    path = path.absolute()
    # macOS declares /var/folders/.../T as its system temp root even though
    # /var aliases /private/var. Trust only that declared prefix, keeping every
    # suffix component intact for the normal symlink and overlap checks.
    temporary = Path(tempfile.gettempdir()).absolute()
    resolved_temporary = temporary.resolve()
    if temporary != resolved_temporary and path.is_relative_to(temporary):
        return resolved_temporary / path.relative_to(temporary)
    return path


def _checked_package_paths(build_lib: str) -> tuple[Path, Path]:
    source = _normalized_build_path(ROOT / 'src' / 'otqa')
    target = _normalized_build_path(Path(build_lib) / 'otqa')
    for path in (source, target):
        # Inspect the lexical ancestors before resolving aliases. In particular,
        # a symlinked build parent must never redirect cleanup into another tree.
        for ancestor in (path, *path.parents):
            if ancestor.is_symlink():
                raise ValueError(f'Symlink in package build path: {ancestor}')
    source, target = source.resolve(), target.resolve()
    if source == target or source.is_relative_to(target) or target.is_relative_to(source):
        raise ValueError('Package build output must not overlap package source')
    if not source.is_dir():
        raise ValueError('Package source must be a real directory')
    if target.exists() and not target.is_dir():
        raise ValueError('Package build output must be a real directory')
    for root in (source, target):
        if root.is_dir():
            for path in root.rglob('*'):
                if path.is_symlink():
                    raise ValueError(f'Symlink in package build tree: {path}')
    return source, target


class BuildPy(build_py):
    def mkpath(self, name, mode=0o777):
        # Distutils caches created paths across command instances. An owned
        # output tree removed below must still be recreated on a repeat build.
        if self.dry_run or getattr(self.distribution, 'dry_run', False):
            return
        owned = getattr(self, '_owned_package_output', None)
        directory = _normalized_build_path(Path(name))
        if owned is not None:
            for ancestor in (directory, *directory.parents):
                if ancestor.is_symlink():
                    raise ValueError(f'Symlink in package build path: {ancestor}')
            if directory.resolve().is_relative_to(owned):
                directory.mkdir(mode=mode, parents=True, exist_ok=True)
        return super().mkpath(name, mode)

    def run(self) -> None:
        source, target = _checked_package_paths(self.build_lib)
        self._owned_package_output = target
        if self.dry_run or getattr(self.distribution, 'dry_run', False):
            # The pinned Setuptools copy/mkpath wrappers do not themselves pass
            # dry_run through, so delegating would still write package files.
            self.announce(f'Would rebuild and verify {target}', level=2)
            return
        tools = source_tools()
        expected = tools.build_inventory(source)
        # Setuptools copies current files but does not remove deleted modules or
        # data. Rebuild only our package directory, leaving sibling outputs alone.
        if target.exists():
            shutil.rmtree(target)
        super().run()
        if tools.build_inventory(source) != expected:
            raise ValueError('Package source changed during build')
        if tools.build_inventory(target) != expected:
            raise ValueError('Built package inventory differs from package source')
        # A stamp copied from an input sdist is verified and preserved; a
        # checkout build receives metadata only after the exact copy check.
        stamp(target)


class SourceDist(sdist):
    def make_release_tree(self, base_dir, files) -> None:
        super().make_release_tree(base_dir, files)
        stamp(Path(base_dir) / 'src' / 'otqa')
