"""The few things that differ between POSIX (Linux, macOS) and Windows."""

from __future__ import annotations

import contextlib
import os
import shutil
import signal
import subprocess
import time
from typing import IO, Any

WINDOWS = os.name == "nt"

# A virtualenv's executables: .venv/bin on POSIX, .venv\Scripts on Windows.
VENV_BIN = "Scripts" if WINDOWS else "bin"


def lock_exclusive(fh: IO[Any]) -> None:
    """Block until we hold an exclusive lock on the open file `fh`."""
    if WINDOWS:
        import msvcrt
        while True:  # LK_LOCK gives up after ~10 s; keep waiting like flock does
            try:
                msvcrt.locking(fh.fileno(), msvcrt.LK_LOCK, 1)
                return
            except OSError:
                time.sleep(0.05)
    else:
        import fcntl
        fcntl.flock(fh, fcntl.LOCK_EX)


def unlock(fh: IO[Any]) -> None:
    if WINDOWS:
        import msvcrt
        with contextlib.suppress(OSError):
            fh.seek(0)
            msvcrt.locking(fh.fileno(), msvcrt.LK_UNLCK, 1)
    else:
        import fcntl
        fcntl.flock(fh, fcntl.LOCK_UN)


def new_group_kwargs() -> dict[str, Any]:
    """subprocess kwargs that start the child in its own process group, so
    kill_tree() can take its children down with it."""
    if WINDOWS:
        return {"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP}
    return {"start_new_session": True}


def kill_tree(pid: int, hangup: bool = False) -> None:
    """Kill a process and everything it started (its group/session on POSIX).
    On POSIX, hangup=True sends SIGHUP (as closing a terminal does) instead of SIGKILL."""
    if WINDOWS:
        subprocess.run(["taskkill", "/T", "/F", "/PID", str(pid)],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
        return
    with contextlib.suppress(ProcessLookupError, PermissionError):
        os.killpg(pid, signal.SIGHUP if hangup else signal.SIGKILL)


def default_shell() -> list[str]:
    """The learner's interactive shell for the cockpit terminal."""
    if WINDOWS:
        for exe in ("pwsh.exe", "powershell.exe"):
            if path := shutil.which(exe):
                return [path, "-NoLogo"]
        return [os.environ.get("COMSPEC") or "cmd.exe"]
    return [os.environ.get("SHELL") or "/bin/bash"]
