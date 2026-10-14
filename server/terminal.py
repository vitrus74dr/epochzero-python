"""A child process on a pseudo-terminal, behind one interface for pty_ws.

POSIX uses ptyprocess and reads the pty's fd from the event loop. Windows uses
pywinpty (ConPTY) and reads on a thread, since its event loop can't watch fds.
Either way, output arrives as bytes on an asyncio.Queue, with b"" at the end.
"""

from __future__ import annotations

import asyncio
import contextlib
import os
import threading
from pathlib import Path

from server.compat import WINDOWS, kill_tree

READ_CHUNK = 65536


class PosixTerminal:
    def __init__(self, argv: list[str], cwd: Path, env: dict[str, str], rows: int, cols: int):
        from ptyprocess import PtyProcess
        self.proc = PtyProcess.spawn(argv, cwd=str(cwd), env=env, dimensions=(rows, cols))
        self.pid = self.proc.pid
        self._loop: asyncio.AbstractEventLoop | None = None

    def start_reading(self, output: asyncio.Queue[bytes]) -> None:
        self._loop = loop = asyncio.get_running_loop()

        def on_readable() -> None:
            try:
                data = os.read(self.proc.fd, READ_CHUNK)
            except OSError:  # EIO once the child side closes
                data = b""
            if not data:
                loop.remove_reader(self.proc.fd)
            output.put_nowait(data)

        loop.add_reader(self.proc.fd, on_readable)

    def stop_reading(self) -> None:
        if self._loop is not None:
            self._loop.remove_reader(self.proc.fd)

    def write(self, data: bytes) -> None:
        os.write(self.proc.fd, data)

    def resize(self, rows: int, cols: int) -> None:
        self.proc.setwinsize(rows, cols)

    def stop(self) -> None:
        """Hang up the whole session (shell and its jobs), then make sure it's dead."""
        kill_tree(self.pid, hangup=True)
        with contextlib.suppress(Exception):
            self.proc.terminate(force=True)

    def exit_code(self) -> int | None:
        """Blocks until the process has exited."""
        with contextlib.suppress(Exception):
            self.proc.wait()
        if self.proc.signalstatus is not None:
            return -self.proc.signalstatus
        return self.proc.exitstatus

    def close(self) -> None:
        with contextlib.suppress(Exception):
            self.proc.close(force=True)


class WindowsTerminal:
    def __init__(self, argv: list[str], cwd: Path, env: dict[str, str], rows: int, cols: int):
        from winpty import PtyProcess
        self.proc = PtyProcess.spawn(argv, cwd=str(cwd), env=env, dimensions=(rows, cols))
        self.pid = self.proc.pid
        self._stopped = threading.Event()

    def start_reading(self, output: asyncio.Queue[bytes]) -> None:
        loop = asyncio.get_running_loop()

        def reader() -> None:
            while not self._stopped.is_set():
                try:
                    text = self.proc.read(READ_CHUNK)
                except (EOFError, OSError):
                    break
                if text:
                    loop.call_soon_threadsafe(output.put_nowait, text.encode("utf-8"))
            loop.call_soon_threadsafe(output.put_nowait, b"")

        threading.Thread(target=reader, name=f"pty-{self.pid}", daemon=True).start()

    def stop_reading(self) -> None:
        self._stopped.set()

    def write(self, data: bytes) -> None:
        self.proc.write(data.decode("utf-8", errors="replace"))

    def resize(self, rows: int, cols: int) -> None:
        self.proc.setwinsize(rows, cols)

    def stop(self) -> None:
        self._stopped.set()
        kill_tree(self.pid)
        with contextlib.suppress(Exception):
            self.proc.terminate(force=True)

    def exit_code(self) -> int | None:
        """Blocks until the process has exited."""
        with contextlib.suppress(Exception):
            self.proc.wait()
        return self.proc.exitstatus

    def close(self) -> None:
        with contextlib.suppress(Exception):
            self.proc.close(force=True)


Terminal = WindowsTerminal if WINDOWS else PosixTerminal
