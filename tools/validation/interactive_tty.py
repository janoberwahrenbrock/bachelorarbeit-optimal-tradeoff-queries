"""New native public-CLI acceptance with a real controlling PTY.

Run with the wheel-containing interpreter and a host-qualified standalone profile.
All new inputs, attempts, terminal transcripts and receipts stay in the marked
project. The diagnostic uses an explicit fixed1/budget1/single-worker policy,
15-second Case watchdog and actual terminal EOF/VINTR bytes. No provider,
numerical method or private profile resolver is substituted. This is functional
TTY validation, never a timing gate or an assertion about every input.
"""
from __future__ import annotations

import argparse
import errno
import hashlib
import json
import os
from pathlib import Path
import pty
import re
import select
import sys
import termios
import time

from otqa.runtime.codec import read_json
from otqa.runtime.documents import file_ref, load_execution_profile
from otqa.runtime.ownership import verified_process_chain
from otqa.runtime.processes import group_status
from otqa.runtime.project import identifier, load_project_context
from otqa.runtime.profiles import production_resolver
from otqa.runtime.source import loaded_source
from otqa.runtime.storage import create_directory, publish_json
from otqa.runtime.validation import verify_result


def write_once(path, value):
    with path.open('x', encoding='utf-8') as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def byte(value):
    return bytes([value]) if isinstance(value, int) else value


def collect_terminal(master, transcript, *, until, timeout=20):
    """Drain available bytes and preserve each chunk before acting on them."""
    data = bytearray()
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        ready, _, _ = select.select([master], [], [], .05)
        if not ready:
            if until(bytes(data)):
                return bytes(data), False
            continue
        try:
            chunk = os.read(master, 65536)
        except OSError as error:
            if error.errno == errno.EIO:
                return bytes(data), True
            raise
        if not chunk:
            return bytes(data), True
        transcript.write(chunk)
        transcript.flush()
        os.fsync(transcript.fileno())
        data.extend(chunk)
        if until(bytes(data)):
            return bytes(data), False
    raise TimeoutError('PTY observation exceeded its explicit diagnostic deadline')


def _run_case(args, context, problem, config, native_validation, mode, owned):
    observation = native_validation / mode
    create_directory(context, observation)
    output = context.project_root / 'runs' / f'{args.output_id}-{mode}'
    command = [sys.executable, '-m', 'otqa', '--project-root', str(context.project_root),
               'solve', '--source-root', str(context.project_root), '--problem', str(problem),
               '--config', str(config), '--execution-profile', str(args.execution_profile),
               '--answers', 'interactive', '--output', str(output)]
    write_once(observation / 'command.json', {'argv': command, 'expected_output': str(output),
               'mode': mode, 'native_case_watchdog_seconds': 15})
    # forkpty supplies an actual controlling terminal and session. Exec a shell
    # with positional argv, preserving that shell's PID/foreground group for CLI.
    pid, master = pty.fork()
    if pid == 0:
        try:
            os.chdir(context.project_root)
            settings = termios.tcgetattr(0)
            proof = {'pid': os.getpid(), 'pgid': os.getpgrp(), 'sid': os.getsid(0),
                     'foreground_pgid': os.tcgetpgrp(0), 'terminal': os.ttyname(0),
                     'stdin_isatty': os.isatty(0), 'stdout_isatty': os.isatty(1),
                     'stderr_isatty': os.isatty(2),
                     'canonical_input': bool(settings[3] & termios.ICANON),
                     'terminal_signals': bool(settings[3] & termios.ISIG),
                     'eof_hex': byte(settings[6][termios.VEOF]).hex(),
                     'vintr_hex': byte(settings[6][termios.VINTR]).hex(),
                     'shell': '/bin/sh', 'exec_command': command}
            write_once(observation / 'terminal-session.json', proof)
            os.execv('/bin/sh', ['sh', '-c', 'exec "$@"', 'otqa-interactive-pty', *command])
        except BaseException:
            import traceback
            traceback.print_exc()
            os._exit(125)
    owned.update(pid=pid, master=master, reaped=False, exit_code=None)
    raw = observation / 'terminal.raw'
    before = after_invalid = None
    with raw.open('xb', buffering=0) as transcript:
        first, ended = collect_terminal(master, transcript, until=lambda data: b'(<, =, >): ' in data)
        require(not ended, 'CLI ended before its first real interactive prompt')
        proof = read_json(observation / 'terminal-session.json')
        require(proof['pid'] == proof['pgid'] == proof['sid'] == proof['foreground_pgid'] == pid,
                'Shell is not its actual terminal foreground session/group leader')
        require(all(proof[k] for k in ('stdin_isatty', 'stdout_isatty', 'stderr_isatty', 'canonical_input', 'terminal_signals')),
                'Actual terminal input/foreground signal behavior missing')
        require(os.tcgetpgrp(master) == pid, 'PTY foreground group changed before input')
        before = read_json(output / 'progress.json')
        require(before['query_counts']['dispatched_new'] == 1 and before['query_counts']['answered_new'] == 0,
                'Initial prompt has no exactly-one open dispatch')
        if mode == 'invalid-valid':
            os.write(master, b'not-an-answer\n')
            repeated, ended = collect_terminal(master, transcript,
                until=lambda data: b'Enter exactly <, = or >.' in data and b'(<, =, >): ' in data)
            require(not ended, 'Invalid input ended the process')
            prompts = [re.search(rb'weight\[[^\r\n]+\(<, =, >\): ', data) for data in (first, repeated)]
            require(all(prompts) and prompts[0].group() == prompts[1].group(), 'Invalid answer changed the query prompt')
            after_invalid = read_json(output / 'progress.json')
            require(after_invalid == before, 'Invalid text changed committed cursor/counts')
            os.write(master, b'>\n')
        elif mode == 'eof':
            os.write(master, bytes.fromhex(proof['eof_hex']))
        elif mode == 'sigint':
            # Delivered through the terminal driver to the true foreground group.
            os.write(master, bytes.fromhex(proof['vintr_hex']))
        else:
            raise ValueError(mode)
        _, ended = collect_terminal(master, transcript, until=lambda data: False)
        require(ended, 'PTY has not reached terminal EOF')
    deadline = time.monotonic() + 5
    while not _reap_owned(owned) and time.monotonic() < deadline:
        time.sleep(.01)
    require(owned['reaped'], 'Exact forkpty child did not exit after terminal EOF')
    exit_code = owned['exit_code']
    (observation / 'terminal.txt').write_text(raw.read_bytes().decode('utf-8', errors='replace'))
    request = read_json(output / 'case-request.json')
    intent_path = output / 'launch_intent.json'
    registration_path = output / 'child_registration.json'
    grant_path = output / 'start_grant.json'
    identity, reg, grant = verified_process_chain(output, output,
        identities={key: request[key] for key in ('run_id', 'attempt_id', 'series_id', 'job_id', 'problem_id', 'configuration_id')},
        intent_ref=file_ref(intent_path, output), registration_ref=file_ref(registration_path, output),
        grant_ref=file_ref(grant_path, output), recorded_process=read_json(registration_path)['process'])
    require(identity is not None and reg and grant, 'Interactive run lacks valid immutable launch chain')
    case_group = group_status(identity)
    require(case_group == 'dead', 'Native Case group remains alive or unknown; next solver blocked')
    try:
        os.killpg(pid, 0)
    except ProcessLookupError:
        outer_group = 'dead'
    else:
        raise AssertionError('PTY shell/CLI foreground group remains live or unknown')
    result = verify_result(output / 'result.json', output, request)
    counts = result['query_counts']
    require(counts['dispatched_new'] == 1, 'Interactive input created a second dispatch')
    if mode == 'invalid-valid':
        require(exit_code in (0, 3) and result['execution_status'] == 'completed' and counts['answered_new'] == 1,
                'Valid terminal response was not accepted exactly once')
    else:
        require(exit_code == 130 and result['execution_status'] == 'interrupted'
                and result['interruption']['reason'] == 'user_cancel' and counts['answered_new'] == 0
                and result['timings']['api_call_wall_seconds'] is None,
                'Terminal EOF/SIGINT was not retained as interrupted open dispatch')
    events = [json.loads(line) for line in (output / 'events.jsonl').read_text().splitlines()]
    answers = [event for event in events if event['event_type'] == 'answer_received']
    require(len(answers) == (1 if mode == 'invalid-valid' else 0), 'Journal accepted an invalid/unreceived response')
    row = {'mode': mode, 'passed': True, 'native_run': str(output), 'exit_code': exit_code,
           'terminal_session': proof, 'foreground_control_source': 'actual PTY canonical VEOF/VINTR, no signal-to-PID substitute',
           'terminal_transcript': file_ref(raw, context.project_root), 'terminal_text': file_ref(observation / 'terminal.txt', context.project_root),
           'before_input_cursor': before, 'after_invalid_input_cursor': after_invalid,
           'query_counts': counts, 'execution_status': result['execution_status'], 'interruption': result['interruption'],
           'result': file_ref(output / 'result.json', context.project_root), 'journal': result['journal'],
           'child_process_identity': identity, 'native_case_group_status_after': case_group,
           'outer_foreground_group_status_after': outer_group,
           'launch_chain_result_journal_validation': 'passed'}
    write_once(observation / 'readback.json', row)
    return row



def _reap_owned(owned):
    """Reap only the still-owned forkpty child; never infer identity from a PID."""
    if owned.get('reaped'):
        return True
    pid = owned.get('pid')
    if pid is None:
        return False
    waited, status = os.waitpid(pid, os.WNOHANG)
    if waited:
        require(waited == pid, 'Unexpected forkpty child from waitpid')
        owned.update(reaped=True, exit_code=os.waitstatus_to_exitcode(status))
    return owned.get('reaped', False)


def _close_master(owned):
    descriptor = owned.pop('master', None)
    if descriptor is not None:
        os.close(descriptor)


def cleanup_failed_case(owned, output, observation, *, seconds=5):
    """Bound observation of our exact terminal; uncertainty blocks the tool.

    A terminal VINTR is sent only while waitpid proves our unreaped child is
    still live and PID=PGID=SID=the actual foreground group. The native parent
    remains responsible for its registered Case. This helper never signals a
    Case PID/group, never treats an unregistered launch gap as dead and never
    authorizes another solver after a failed observation.
    """
    record = {'next_solver_allowed': False, 'direct_process_signals': [],
              'terminal_vintr_sent': False, 'outer_child_reaped': False,
              'case_group_status': 'unknown', 'status': 'blocked_unknown'}
    deadline = time.monotonic() + seconds
    try:
        if owned.get('pid') is not None and not _reap_owned(owned):
            pid, master = owned['pid'], owned.get('master')
            if (master is not None and os.getpgid(pid) == os.getsid(pid)
                    == os.tcgetpgrp(master) == pid):
                settings = termios.tcgetattr(master)
                if settings[3] & termios.ISIG:
                    os.write(master, byte(settings[6][termios.VINTR]))
                    record['terminal_vintr_sent'] = True
            raw = observation / 'terminal.raw'
            with raw.open('ab', buffering=0) as transcript:
                while time.monotonic() < deadline:
                    if _reap_owned(owned):
                        break
                    ready, _, _ = select.select([master], [], [], .02) if master is not None else ([], [], [])
                    if ready:
                        try:
                            chunk = os.read(master, 65536)
                        except OSError as error:
                            if error.errno != errno.EIO:
                                raise
                        else:
                            if chunk:
                                transcript.write(chunk)
                                os.fsync(transcript.fileno())
        record['outer_child_reaped'] = owned.get('reaped', False)
        record['outer_exit_code'] = owned.get('exit_code')
        if owned.get('pid') is None:
            record['outer_child_status'] = 'not_created'
        elif owned.get('reaped'):
            try:
                os.killpg(owned['pid'], 0)
            except ProcessLookupError:
                record['outer_child_status'] = 'dead'
            else:
                record['outer_child_status'] = 'unknown'
        else:
            record['outer_child_status'] = 'unknown'
        intent = output / 'launch_intent.json'
        if not intent.exists():
            # The native protocol publishes Intent before any Case Popen.
            record['case_group_status'] = 'not_created_no_launch_intent'
        else:
            request = read_json(output / 'case-request.json')
            registration = output / 'child_registration.json'
            grant = output / 'start_grant.json'
            identity, _, _ = verified_process_chain(output, output,
                identities={key: request[key] for key in ('run_id', 'attempt_id', 'series_id', 'job_id', 'problem_id', 'configuration_id')},
                intent_ref=file_ref(intent, output),
                registration_ref=file_ref(registration, output) if registration.exists() else None,
                grant_ref=file_ref(grant, output) if grant.exists() else None,
                recorded_process=read_json(registration)['process'] if registration.exists() else None)
            record['case_group_status'] = group_status(identity) if identity is not None else 'unknown_unregistered_spawn_gap'
            record['registered_identity'] = identity
        if (record['outer_child_status'] in ('dead', 'not_created')
                and record['case_group_status'] in ('dead', 'not_created_no_launch_intent')):
            record['status'] = 'cleaned_failed_observation'
    except BaseException as error:
        record['cleanup_error'] = {'type': type(error).__name__, 'message': str(error)}
    finally:
        try:
            _close_master(owned)
            record['pty_master_closed'] = True
        except OSError as error:
            record['pty_master_closed'] = False
            record['descriptor_close_error'] = str(error)
            record['status'] = 'blocked_unknown'
    return record


def run_case(args, context, problem, config, native_validation, mode):
    owned = {}
    observation = native_validation / mode
    output = context.project_root / 'runs' / f'{args.output_id}-{mode}'
    try:
        return _run_case(args, context, problem, config, native_validation, mode, owned)
    except BaseException as error:
        cleanup = cleanup_failed_case(owned, output, observation)
        cleanup['original_error'] = {'type': type(error).__name__, 'message': str(error)}
        try:
            write_once(observation / 'failure-cleanup.json', cleanup)
        except BaseException as publication_error:
            error.add_note(f'Failure cleanup receipt publication failed: {publication_error!r}; cleanup={cleanup!r}')
        raise
    finally:
        _close_master(owned)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--project-root', type=Path, required=True)
    parser.add_argument('--execution-profile', type=Path, required=True)
    parser.add_argument('--output-id', required=True, help='Fresh identifier for inputs and the three separate native runs')
    args = parser.parse_args()
    if not (sys.platform.startswith('linux') or sys.platform == 'darwin'):
        parser.error('The controlling-PTY acceptance is supported on Linux and macOS')
    args.project_root = args.project_root.resolve(strict=True)
    args.execution_profile = args.execution_profile.resolve(strict=True)
    args.output_id = identifier(args.output_id)
    context = load_project_context(args.project_root)
    source_before = loaded_source()
    validation = context.project_root / 'runs' / f'{args.output_id}-validation'
    inputs = context.project_root / 'inputs' / args.output_id
    reserved = [validation, inputs, *(context.project_root / 'runs' / f'{args.output_id}-{mode}'
                                    for mode in ('invalid-valid', 'eof', 'sigint'))]
    if any(path.exists() for path in reserved):
        parser.error('The output ID already has inputs, validation or native runs; choose a fresh ID')
    profile = load_execution_profile(args.execution_profile, reference_root=context.project_root)
    production_resolver(context.project_root, profile, 'standalone')
    create_directory(context, validation)
    create_directory(context, inputs, namespace='inputs')
    problem = {'schema_version': 1, 'problem_id': 'interactive-pty-two-alternatives',
               'objective_ids': ['goal0', 'goal1'], 'alternative_ids': ['alternative0', 'alternative1'],
               'alternatives': [[1., 0.], [0., 1.]]}
    config = {'schema_version': 2, 'configuration_id': 'interactive-pty-fixed1-budget1',
              'algorithm': {'query_strategy': 'fixed', 'depth': 1, 'higher_depth_query_source': 'both',
                  'grid_size': 5, 'planning_evaluation': 'candidate_count', 'stopping': {'rule': 'single_candidate'},
                  'horizon_execution': 'receding', 'min_expected_progress': 0.001},
              'budget': {'max_queries': 1}, 'execution': {'workers': 1, 'start_method': 'forkserver',
                  'native_threads': 1, 'case_timeout_seconds': 15, 'cache_policy_id': 'bounded_v1'},
              'recording': {'durability': 'per_answer', 'trace_level': 'standard', 'profile': False, 'telemetry_failure_policy': 'continue'}}
    publish_json(context, inputs / 'problem.json', problem, kind='problem', namespace='inputs')
    publish_json(context, inputs / 'config.json', config, kind='config', namespace='inputs')
    rows = []
    try:
        for mode in ('invalid-valid', 'eof', 'sigint'):
            row = run_case(args, context, inputs / 'problem.json', inputs / 'config.json', validation, mode)
            rows.append(row)
            write_once(validation / f'{mode}.json', row)
            print(mode, 'passed', row['exit_code'], flush=True)
        require(loaded_source() == source_before, 'Installed source changed during PTY acceptance')
    except BaseException as error:
        import traceback
        write_once(validation / 'failure.json', {'type': type(error).__name__, 'message': str(error),
            'traceback': traceback.format_exc(), 'completed_rows': rows, 'native_validation': str(validation)})
        raise
    report = {'schema_version': 1, 'kind': 'actual_public_cli_controlling_pty_acceptance', 'passed': True,
              'source_before': source_before[0], 'source_after': loaded_source()[0],
              'actual_python': sys.executable, 'profile': {'path': str(args.execution_profile), 'sha256': sha(args.execution_profile)},
              'harness_sha256': sha(Path(__file__)), 'native_validation': str(validation), 'rows': rows,
              'scope': 'Three fresh analytic2D fixed1 single-worker public interactive CLI runs; real controlling terminal foreground session, invalid/valid, VEOF and VINTR. No external mathematical reference or private resolver. Not a performance gate.',
              'all_case_and_foreground_groups_dead': True}
    write_once(validation / 'receipt.json', report)
    print(json.dumps({'passed': True, 'receipt': str(validation / 'receipt.json'), 'receipt_sha256': sha(validation / 'receipt.json')}), flush=True)


if __name__ == '__main__':
    main()
