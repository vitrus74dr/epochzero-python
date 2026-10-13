"""Sandboxed file API over workspace/ (HANDOFF.md §3, §7).

Every path is resolved (symlinks included) and must stay inside workspace/.
Reads and writes carry a version (mtime_ns + size) so a save from the browser
can't silently clobber an edit Claude Code made in the terminal meanwhile.
"""

from __future__ import annotations

import os
from pathlib import Path, PurePosixPath

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from server.paths import Paths
from server.tracker import write_atomic

MAX_FILE_BYTES = 1_000_000
MAX_TREE_ENTRIES = 2_000
HIDDEN_DIRS = {"__pycache__", ".venv", "venv", ".pytest_cache", ".mypy_cache",
               ".ruff_cache", "node_modules", ".git"}


class SandboxError(Exception):
    pass


def resolve_in(base: Path, rel: str) -> Path:
    """Resolve a client-supplied relative path inside base, or raise SandboxError."""
    if not rel or "\x00" in rel:
        raise SandboxError("empty or invalid path")
    pure = PurePosixPath(rel.replace("\\", "/"))
    if pure.is_absolute() or ".." in pure.parts:
        raise SandboxError("path must be relative and stay inside workspace/")
    base = base.resolve()
    target = (base / pure).resolve()
    if target != base and base not in target.parents:
        raise SandboxError("path escapes workspace/")  # e.g. via a symlink
    return target


def version_of(path: Path) -> str:
    st = path.stat()
    return f"{st.st_mtime_ns}-{st.st_size}"


def build_tree(base: Path) -> list[dict]:
    """Nested listing; dirs first, hidden/cache entries skipped, symlinks not followed."""
    base = base.resolve()
    count = 0

    def walk(d: Path) -> list[dict]:
        nonlocal count
        try:
            entries = sorted(os.scandir(d), key=lambda e: (not e.is_dir(follow_symlinks=False),
                                                           e.name.lower()))
        except OSError:
            return []
        out = []
        for e in entries:
            if e.name.startswith(".") or e.name in HIDDEN_DIRS:
                continue
            count += 1
            if count > MAX_TREE_ENTRIES:
                break
            rel = Path(e.path).relative_to(base).as_posix()
            if e.is_dir(follow_symlinks=False):
                out.append({"name": e.name, "path": rel, "type": "dir",
                            "children": walk(Path(e.path))})
            elif e.is_file(follow_symlinks=False):
                out.append({"name": e.name, "path": rel, "type": "file"})
        return out

    return walk(base)


class WriteRequest(BaseModel):
    content: str
    # Version the client last read; None means "create, must not exist".
    base_version: str | None = None
    force: bool = False


def router(paths: Paths) -> APIRouter:
    r = APIRouter(prefix="/api/files")

    def target(path: str) -> Path:
        try:
            return resolve_in(paths.workspace, path)
        except SandboxError as e:
            raise HTTPException(403, str(e)) from None

    @r.get("/tree")
    def tree():
        paths.workspace.mkdir(exist_ok=True)
        return {"root": "workspace", "children": build_tree(paths.workspace)}

    @r.get("")
    def read(path: str = Query(...)):
        p = target(path)
        if not p.is_file():
            raise HTTPException(404, f"{path} not found")
        if p.stat().st_size > MAX_FILE_BYTES:
            raise HTTPException(413, f"{path} is larger than {MAX_FILE_BYTES} bytes")
        try:
            content = p.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            raise HTTPException(415, f"{path} is not UTF-8 text") from None
        return {"path": path, "content": content, "version": version_of(p)}

    @r.put("")
    def write(body: WriteRequest, path: str = Query(...)):
        p = target(path)
        if len(body.content.encode("utf-8")) > MAX_FILE_BYTES:
            raise HTTPException(413, "file too large")
        if p.is_dir():
            raise HTTPException(409, f"{path} is a directory")
        if not body.force:
            if p.exists() and body.base_version is None:
                raise HTTPException(409, f"{path} already exists")
            if p.exists() and body.base_version != version_of(p):
                raise HTTPException(409, f"{path} changed on disk since you opened it")
            if not p.exists() and body.base_version is not None:
                raise HTTPException(409, f"{path} was deleted on disk")
        p.parent.mkdir(parents=True, exist_ok=True)
        # Re-check after mkdir: parents may be fresh dirs, but must still be inside.
        target(path)
        write_atomic(p, body.content)
        return {"path": path, "version": version_of(p)}

    return r
