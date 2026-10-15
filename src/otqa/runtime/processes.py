"""Real process identities and conservative process-group ownership checks."""
from __future__ import annotations

import os
import platform
import signal
import sys
from pathlib import Path

from .codec import DocumentError


def _proc_fields(pid: int):
    text = Path(f"/proc/{pid}/stat").read_text()
    # comm is parenthesized and may contain spaces or parentheses.
    tail = text[text.rfind(")") + 2:].split()
    return {"state": tail[0], "pgid": int(tail[2]), "sid": int(tail[3]), "start_ticks": int(tail[19])}


def process_identity(owner_token: str, pid: int | None = None) -> dict:
    pid = os.getpid() if pid is None else pid
    linux = sys.platform.startswith("linux")
    fields = _proc_fields(pid) if linux else None
    return {"pid": pid, "hostname": platform.node(), "identity_method": "linux_proc" if linux else "owned_child",
        "boot_id": Path("/proc/sys/kernel/random/boot_id").read_text().strip() if linux else None,
        "start_ticks": fields["start_ticks"] if fields else None, "pgid": os.getpgid(pid), "sid": os.getsid(pid), "owner_token": owner_token}


def identity_status(identity: dict, *, owned_child=None) -> str:
    """alive/dead/unknown. PID existence alone is never positive identity proof."""
    if identity["hostname"] != platform.node():
        return "unknown"
    if identity["identity_method"] == "linux_proc":
        if not sys.platform.startswith("linux"):
            return "unknown"
        if Path("/proc/sys/kernel/random/boot_id").read_text().strip() != identity["boot_id"]:
            return "dead"
        try:
            fields = _proc_fields(identity["pid"])
        except FileNotFoundError:
            return "dead"
        except (OSError, ValueError, IndexError):
            return "unknown"
        if fields["start_ticks"] != identity["start_ticks"]:
            return "dead"
        if fields["pgid"] != identity["pgid"] or fields["sid"] != identity["sid"]:
            return "unknown"
        return "dead" if fields["state"] == "Z" else "alive"
    if owned_child is not None and owned_child.pid == identity["pid"]:
        return "alive" if owned_child.poll() is None else "dead"
    try:
        os.kill(identity["pid"], 0)
    except ProcessLookupError:
        return "dead"
    except PermissionError:
        return "unknown"
    return "unknown"


def group_status(identity: dict, *, owned_child=None) -> str:
    """No member/owned members/unknown; complete recovery is Linux-qualified."""
    pgid, sid = identity["pgid"], identity["sid"]
    if pgid is None or sid is None or pgid != identity["pid"] or sid != identity["pid"]:
        return "unknown"
    if identity["hostname"] != platform.node():
        return "unknown"
    if identity["identity_method"] == "linux_proc" and sys.platform.startswith("linux"):
        if Path("/proc/sys/kernel/random/boot_id").read_text().strip() != identity["boot_id"]:
            return "dead"
        found = False
        try:
            for entry in Path("/proc").iterdir():
                if not entry.name.isdigit():
                    continue
                try:
                    fields = _proc_fields(int(entry.name))
                except (FileNotFoundError, ProcessLookupError):
                    continue
                if fields["pgid"] != pgid or fields["state"] == "Z":
                    continue
                if fields["sid"] != sid or fields["start_ticks"] < identity["start_ticks"]:
                    return "unknown"
                found = True
        except (OSError, ValueError, IndexError):
            return "unknown"
        return "alive" if found else "dead"
    try:
        os.killpg(pgid, 0)
    except ProcessLookupError:
        return "dead"
    except PermissionError:
        return "unknown"
    if owned_child is not None and identity_status(identity, owned_child=owned_child) == "alive":
        return "alive"
    return "unknown"


def terminate_owned_group(identity: dict, *, owned_child=None, force=False) -> None:
    if group_status(identity, owned_child=owned_child) != "alive":
        raise DocumentError("Cannot signal a group whose ownership is unproven")
    os.killpg(identity["pgid"], signal.SIGKILL if force else signal.SIGTERM)
