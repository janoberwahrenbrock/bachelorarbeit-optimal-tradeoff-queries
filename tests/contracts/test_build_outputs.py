"""Actual distribution-command checks on independently constructed packages."""
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import tarfile

import pytest
from setuptools.dist import Distribution


@pytest.fixture
def build_fixture(tmp_path, monkeypatch):
    repository = Path(__file__).resolve().parents[2]
    spec = importlib.util.spec_from_file_location('isolated_build_support', repository / 'build_support.py')
    hook = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(hook)
    # The name also permits an output that would be an ancestor of src/otqa.
    root = (tmp_path / 'otqa').resolve()
    source = root / 'src' / 'otqa'
    (source / 'schemas').mkdir(parents=True)
    (root / 'pyproject.toml').write_text('[project]\nname="build-control"\nversion="0.1.0"\n')
    (source / '__init__.py').write_text('"""Analytical build fixture."""\n')
    (source / 'keep.py').write_text('VALUE = 1\n')
    (source / 'schemas' / 'keep.json').write_text('{"type":"object"}\n')
    shutil.copyfile(repository / 'src' / 'otqa' / '_build_metadata.py', source / '_build_metadata.py')
    monkeypatch.setattr(hook, 'ROOT', root)
    monkeypatch.chdir(root)

    def run(build_lib=None, *, dry_run=False, command_dry_run=False):
        dist = Distribution({
            'name': 'build-control', 'version': '0.1.0', 'packages': ['otqa'],
            'package_dir': {'': 'src'}, 'include_package_data': False,
            'package_data': {'otqa': ['schemas/*.json', '_source_inventory.json', '_build_provenance.json']},
        })
        if dry_run:
            dist.dry_run = True
        dist.script_name = 'setup.py'
        command = hook.BuildPy(dist)
        command.dry_run = command_dry_run
        command.build_lib = str(build_lib if build_lib is not None else root / 'build' / 'lib')
        command.ensure_finalized()
        command.run()
        return Path(command.build_lib) / 'otqa'

    return hook, root, source, run


def source_bytes(source):
    return {path.relative_to(source).as_posix(): path.read_bytes()
            for path in source.rglob('*') if path.is_file() and '__pycache__' not in path.parts}


def test_repeat_build_removes_deleted_modules_and_schemas_only_from_owned_package(build_fixture):
    hook, root, source, run = build_fixture
    (source / 'removed.py').write_text('REMOVED = True\n')
    (source / 'schemas' / 'removed.json').write_text('{"removed":true}\n')
    output = run()
    first = json.loads((output / '_source_inventory.json').read_text())
    sibling = output.parent / 'unrelated' / 'keep.txt'
    sibling.parent.mkdir()
    sibling.write_text('Another package owns this file')
    (source / 'removed.py').unlink()
    (source / 'schemas' / 'removed.json').unlink()
    (source / 'added.py').write_text('ADDED = True\n')
    before = source_bytes(source)
    run()
    tools = hook.source_tools()
    recorded = json.loads((output / '_source_inventory.json').read_text())
    assert recorded == tools.build_inventory(source) == tools.build_inventory(output)
    assert recorded != first
    assert not (output / 'removed.py').exists()
    assert not (output / 'schemas' / 'removed.json').exists()
    assert (output / 'added.py').read_bytes() == (source / 'added.py').read_bytes()
    assert sibling.read_text() == 'Another package owns this file'
    assert source_bytes(source) == before


def test_input_sdist_provenance_is_preserved_after_clean_repeat_build(build_fixture):
    hook, _, source, run = build_fixture
    tools = hook.source_tools()
    original = tools.write_build_metadata(source, 'original-sdist', 'a' * 40, False)
    stamps = {name: (source / name).read_bytes()
              for name in ('_source_inventory.json', '_build_provenance.json')}
    output = run()
    (output / 'stale.py').write_text('OLD = True\n')
    run()
    assert not (output / 'stale.py').exists()
    assert {name: (output / name).read_bytes() for name in stamps} == stamps
    assert json.loads((output / '_build_provenance.json').read_text()) == original
    assert {name: (source / name).read_bytes() for name in stamps} == stamps


@pytest.mark.parametrize('flag', ['distribution', 'command'])
def test_dry_run_neither_removes_outputs_nor_publishes_metadata(build_fixture, flag):
    _, root, source, run = build_fixture
    output = root / 'build' / 'lib' / 'otqa'
    output.mkdir(parents=True)
    (output / 'stale.py').write_text('OWNED_PREEXISTING = True\n')
    source_before, output_before = source_bytes(source), source_bytes(output)
    run(dry_run=flag == 'distribution', command_dry_run=flag == 'command')
    assert source_bytes(source) == source_before
    assert source_bytes(output) == output_before


@pytest.mark.parametrize('location', ['equal', 'child', 'deep_child', 'ancestor', 'relative_alias'])
def test_source_overlap_is_rejected_before_cleanup(build_fixture, location):
    _, root, source, run = build_fixture
    build_lib = {
        'equal': root / 'src',
        'child': source,
        'deep_child': source / 'child',
        'ancestor': root.parent,
        'relative_alias': Path('build') / '..' / 'src',
    }[location]
    before = source_bytes(source)
    with pytest.raises(ValueError, match='overlap'):
        run(build_lib)
    assert source_bytes(source) == before


@pytest.mark.parametrize('location', ['target', 'output_parent', 'source', 'source_parent', 'source_hook', 'output_child'])
def test_symlinks_are_rejected_before_copy_cleanup_or_source_hook_execution(build_fixture, location):
    _, root, source, run = build_fixture
    build_lib = root / 'build' / 'lib'
    output = build_lib / 'otqa'
    foreign = root.parent / 'foreign'
    foreign.mkdir()
    sentinel = foreign / 'keep.txt'
    sentinel.write_text('Foreign data must survive')
    output.mkdir(parents=True)
    owned = output / 'owned.py'
    owned.write_text('PRESERVED_ON_ERROR = True\n')
    if location == 'target':
        shutil.rmtree(output)
        output.symlink_to(foreign, target_is_directory=True)
    elif location == 'output_parent':
        shutil.rmtree(build_lib)
        build_lib.symlink_to(foreign, target_is_directory=True)
    elif location == 'source':
        shutil.move(source, foreign / 'package')
        source.symlink_to(foreign / 'package', target_is_directory=True)
    elif location == 'source_parent':
        shutil.move(root / 'src', foreign / 'src')
        (root / 'src').symlink_to(foreign / 'src', target_is_directory=True)
    elif location == 'source_hook':
        (source / '_build_metadata.py').unlink()
        unexpected = foreign / 'unexpected.py'
        unexpected.write_text('raise AssertionError("source hook must not execute")\n')
        (source / '_build_metadata.py').symlink_to(unexpected)
    else:
        (output / 'alias.py').symlink_to(sentinel)
    before = source_bytes(source)
    with pytest.raises(ValueError, match='Symlink'):
        run(build_lib)
    assert sentinel.read_text() == 'Foreign data must survive'
    assert source_bytes(source) == before
    if location not in {'target', 'output_parent'}:
        assert owned.read_text() == 'PRESERVED_ON_ERROR = True\n'


@pytest.mark.parametrize('mutation', ['extra', 'missing', 'changed'])
def test_copy_mismatch_cannot_receive_a_new_build_stamp(build_fixture, monkeypatch, mutation):
    hook, root, _, run = build_fixture
    original = hook.build_py.run

    def changed_copy(command):
        original(command)
        output = Path(command.build_lib) / 'otqa'
        if mutation == 'extra':
            (output / 'unexpected.py').write_text('EXTRA = True\n')
        elif mutation == 'missing':
            (output / 'keep.py').unlink()
        else:
            (output / 'keep.py').write_text('VALUE = 999\n')

    monkeypatch.setattr(hook.build_py, 'run', changed_copy)
    with pytest.raises(ValueError, match='inventory differs'):
        run()
    assert not (root / 'build' / 'lib' / 'otqa' / '_source_inventory.json').exists()
    assert not (root / 'build' / 'lib' / 'otqa' / '_build_provenance.json').exists()


def test_source_change_during_copy_is_rejected(build_fixture, monkeypatch):
    hook, _, source, run = build_fixture
    original = hook.build_py.run

    def changed_source(command):
        original(command)
        (source / 'keep.py').write_text('VALUE = 2\n')

    monkeypatch.setattr(hook.build_py, 'run', changed_source)
    with pytest.raises(ValueError, match='source changed'):
        run()


def test_declared_system_temporary_root_alias_supports_real_builds(build_fixture, monkeypatch):
    hook, root, source, run = build_fixture
    real = root.parent / 'real-system-temp'
    real.mkdir()
    declared = root.parent / 'declared-system-temp'
    declared.symlink_to(real, target_is_directory=True)
    monkeypatch.setattr(hook.tempfile, 'gettempdir', lambda: str(declared))
    output = run(declared / 'pip-build' / 'lib')
    assert output.resolve() == real / 'pip-build' / 'lib' / 'otqa'
    assert hook.source_tools().build_inventory(source) == hook.source_tools().build_inventory(output)


@pytest.mark.parametrize('location', ['descendant', 'undeclared', 'source_overlap'])
def test_system_temporary_alias_does_not_allow_other_aliases_or_source_overlap(
        build_fixture, monkeypatch, location):
    hook, root, source, run = build_fixture
    real = root.parent / 'real-system-temp'
    real.mkdir()
    declared = root.parent / 'declared-system-temp'
    declared.symlink_to(real, target_is_directory=True)
    monkeypatch.setattr(hook.tempfile, 'gettempdir', lambda: str(declared))
    foreign = root.parent / 'foreign-build'
    foreign.mkdir()
    sentinel = foreign / 'keep.txt'
    sentinel.write_text('Must not be removed')
    if location == 'descendant':
        (real / 'nested-alias').symlink_to(foreign, target_is_directory=True)
        build_lib = declared / 'nested-alias' / 'lib'
    elif location == 'undeclared':
        other = root.parent / 'other-alias'
        other.symlink_to(real, target_is_directory=True)
        build_lib = other / 'lib'
    else:
        build_lib = declared / '..' / root.name / 'src'
    before = source_bytes(source)
    with pytest.raises(ValueError, match='overlap' if location == 'source_overlap' else 'Symlink'):
        run(build_lib)
    assert source_bytes(source) == before
    assert sentinel.read_text() == 'Must not be removed'


def source_distribution(hook, root):
    dist = Distribution({
        'name': 'build-control', 'version': '0.1.0', 'packages': ['otqa'],
        'package_dir': {'': 'src'}, 'include_package_data': False,
        'package_data': {'otqa': ['schemas/*.json']},
    })
    dist.script_name = 'setup.py'
    command = hook.SourceDist(dist)
    command.dist_dir = str(root / 'dist')
    command.formats = ['gztar']
    command.ensure_finalized()
    command.run()
    return next((root / 'dist').glob('*.tar.gz'))


def initialize_git(root):
    (root / '.gitignore').write_text('dist/\nbuild/\n*.egg-info/\n__pycache__/\n')
    subprocess.run(['git', 'init', '-q', str(root)], check=True)
    subprocess.run(['git', 'add', '.'], cwd=root, check=True)
    subprocess.run(['git', '-c', 'user.name=Build Control', '-c', 'user.email=build@example.invalid',
                    'commit', '-qm', 'Initial analytical fixture'], cwd=root, check=True)


@pytest.mark.parametrize('user_change', ['clean', 'tracked', 'untracked'])
def test_sdist_records_checkout_before_own_release_tree_without_hiding_user_changes(
        build_fixture, monkeypatch, user_change):
    hook, root, source, _ = build_fixture
    initialize_git(root)
    if user_change == 'tracked':
        (source / 'keep.py').write_text('VALUE = 2\n')
    elif user_change == 'untracked':
        (root / 'user-notes.txt').write_text('Real user change\n')
    expected = hook.build_provenance()
    before = source_bytes(source)
    original = hook.sdist.make_release_tree
    observed = []

    def observe_staging(command, base_dir, files):
        original(command, base_dir, files)
        observed.append((Path(base_dir).is_dir(), hook.build_provenance()[2]))

    monkeypatch.setattr(hook.sdist, 'make_release_tree', observe_staging)
    archive = source_distribution(hook, root)
    assert observed == [(True, True)]  # Even a clean checkout has its own untracked staging tree.
    with tarfile.open(archive) as stream:
        path = next(member for member in stream.getmembers()
                    if member.name.endswith('/src/otqa/_build_provenance.json'))
        metadata = json.load(stream.extractfile(path))
    assert metadata['source']['dirty'] is (user_change != 'clean')
    assert metadata['source']['git_commit'] == expected[1]
    assert hook.build_provenance() == expected
    assert source_bytes(source) == before


def test_sdist_rejects_package_changes_after_provenance_snapshot(build_fixture, monkeypatch):
    hook, root, source, _ = build_fixture
    initialize_git(root)
    original = hook.sdist.make_release_tree

    def mutate_during_release(command, base_dir, files):
        original(command, base_dir, files)
        (source / 'keep.py').write_text('VALUE = 3\n')

    monkeypatch.setattr(hook.sdist, 'make_release_tree', mutate_during_release)
    with pytest.raises(ValueError, match='source changed'):
        source_distribution(hook, root)
    assert not list((root / 'dist').glob('*.tar.gz'))
