"""Analytical process-bootstrap contracts, independent of solver timings."""
from pathlib import Path
import os
import subprocess
import sys


SOURCE = Path(__file__).resolve().parents[2] / 'src'


def isolated(code):
    result = subprocess.run([sys.executable, '-c', code], capture_output=True, text=True,
        env={**os.environ, 'PYTHONPATH': str(SOURCE), 'OPENBLAS_NUM_THREADS': '1', 'OMP_NUM_THREADS': '1'}, timeout=15)
    assert result.returncode == 0, result.stdout + result.stderr


HEADER = '''
from otqa import AlgorithmPolicy, Problem, SingleCandidateStop, SolverExecution
import otqa.planning.session as module
problem=Problem([[1.,0.],[0.,1.]])
policy=AlgorithmPolicy('fixed',1,'both',5,'candidate_count',SingleCandidateStop())
'''


def test_owned_registration_imports_modules_without_session_backend_or_handles():
    isolated(HEADER + '''
import sys
calls=[]
def forbidden():
    calls.append('backend')
    raise AssertionError('idle registration called a backend factory')
module._initialize_worker(problem,policy,SolverExecution(8),None,forbidden,'owner')
assert 'otqa.geometry' in sys.modules and 'otqa.state' in sys.modules
assert 'numpy' in sys.modules and 'scipy' in sys.modules
assert module._WORKER is None and module._WORKER_FAILURE is None and not calls
assert module._WORKER_CONTEXT[-1]=='owner'
''')


def test_import_failure_is_deferred_identity_preserved_and_duplicate_ownership_fails():
    isolated(HEADER + '''
import builtins
from otqa.errors import ExecutionContextError
original=builtins.__import__
sentinel=ImportError('isolated numerical import failure')
def failing(name,*args,**kwargs):
    if name=='otqa.geometry':raise sentinel
    return original(name,*args,**kwargs)
builtins.__import__=failing
module._initialize_worker(problem,policy,SolverExecution(8),None,None,'owner')
builtins.__import__=original
assert module._WORKER is None
failure=module._WORKER_FAILURE
assert isinstance(failure,ExecutionContextError) and failure.__cause__ is sentinel
for _ in range(2):
    try:module._run_worker(None)
    except ExecutionContextError as error:assert error is failure and error.__cause__ is sentinel
    else:raise AssertionError('first actual task did not receive deferred import error')
try:module._initialize_worker(problem,policy,SolverExecution(8),None,None,'different-owner')
except ExecutionContextError as error:assert 'already registered' in str(error)
else:raise AssertionError('ownership violation was deferred')
''')


def test_base_exception_is_not_swallowed():
    isolated(HEADER + '''
import builtins
class Sentinel(BaseException):pass
sentinel=Sentinel()
original=builtins.__import__
def failing(name,*args,**kwargs):
    if name=='otqa.geometry':raise sentinel
    return original(name,*args,**kwargs)
builtins.__import__=failing
try:module._initialize_worker(problem,policy,SolverExecution(8),None,None,'owner')
except Sentinel as error:assert error is sentinel
else:raise AssertionError('BaseException swallowed')
assert module._WORKER_FAILURE is None
''')


def test_sessions_remain_first_task_lazy_and_reused():
    isolated(HEADER + '''
calls=[]
module._initialize_worker(problem,policy,SolverExecution(8),None,None,'owner')
class Fake:
    def __init__(self,*args,**kwargs):calls.append('session')
    def close(self):calls.append('close')
    def _execute_task(self,task):calls.append(task);return 'original-result',()
module.PlannerSession=Fake
assert not calls
assert module._run_worker('first-task')=='original-result'
assert module._run_worker('second-task')=='original-result'
assert calls==['session','first-task','second-task']
''')
