"""The SDK and argument help must remain usable before numerical bootstrap."""
import ast
import subprocess
import sys
from pathlib import Path


def test_importing_public_sdk_does_not_import_numerics_or_mutate_process_environment():
    code = '''
import os, sys, multiprocessing
before = dict(os.environ)
method = multiprocessing.get_start_method(allow_none=True)
import otqa
assert not any(name in sys.modules for name in ('numpy', 'scipy'))
assert before == dict(os.environ)
assert method == multiprocessing.get_start_method(allow_none=True)
assert otqa.api.solve is otqa.solve
'''
    subprocess.run([sys.executable, '-c', code], check=True)


def test_domain_modules_have_no_runtime_or_numerical_imports():
    root = Path(__file__).parents[2] / 'src' / 'otqa' / 'models'
    forbidden = ('numpy', 'scipy', 'otqa.runtime', 'otqa.cli', 'otqa.experiments', 'otqa.analysis', 'otqa.planning')
    for path in root.glob('*.py'):
        for node in ast.walk(ast.parse(path.read_text())):
            imports = ([alias.name for alias in node.names] if isinstance(node, ast.Import)
                       else [node.module or ''] if isinstance(node, ast.ImportFrom) else [])
            assert not any(name == prefix or name.startswith(prefix + '.') for name in imports for prefix in forbidden), path
            if isinstance(node, ast.ImportFrom) and node.level == 2:
                assert (node.module or '').split('.')[0] not in ('runtime', 'cli', 'experiments', 'analysis', 'planning'), path
