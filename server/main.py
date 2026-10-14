"""EpochZero Python: app factory and launcher.

Security model (see HANDOFF.md §7): the server binds 127.0.0.1 only, rejects
requests whose Host/Origin aren't this app (DNS rebinding, cross-site
WebSockets), and requires a per-launch session cookie on every /api route.
The cookie is obtained by POSTing the token from the launch URL to
/api/session, so the token never has to live in page JS after startup.
"""

from __future__ import annotations

import argparse
import asyncio
import hmac
import secrets
import shutil
import socket
import subprocess
import sys
import threading
import webbrowser
from contextlib import asynccontextmanager
from http.cookies import SimpleCookie
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from starlette.types import ASGIApp, Receive, Scope, Send

from server.compat import WINDOWS, utf8_stdio
from server import fs, lessons, pty_ws, quizzes, tests_runner, tracker_api
from server.paths import ROOT, Paths
from server.watch import EventHub, watch_root

WEB = ROOT / "web"
DIST = WEB / "dist"
DEFAULT_PORT = 8765
VITE_PORT = 5173

# Routes reachable without a session cookie. /api/session is how you get one.
PUBLIC_API = {"/api/session"}


def cookie_name(port: int) -> str:
    # Cookies aren't port-scoped, so include the port to keep two
    # instances on different ports from clobbering each other.
    return f"epochzero_session_{port}"


class GuardMiddleware:
    """Host/Origin allow-list plus session-cookie check, for HTTP and WebSocket."""

    def __init__(self, app: ASGIApp, *, token: str, port: int, dev: bool) -> None:
        self.app = app
        self.token = token
        self.cookie = cookie_name(port)
        ports = [port] + ([VITE_PORT] if dev else [])
        self.hosts = {f"{h}:{p}" for h in ("127.0.0.1", "localhost") for p in ports}
        self.origins = {f"http://{h}" for h in self.hosts}

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] not in ("http", "websocket"):
            await self.app(scope, receive, send)
            return

        headers = {k.decode("latin-1"): v.decode("latin-1") for k, v in scope["headers"]}
        host = headers.get("host", "")
        origin = headers.get("origin")
        path: str = scope["path"]

        if host not in self.hosts:
            await self._deny(scope, send, 403, "bad host")
            return
        if origin is not None and origin not in self.origins:
            await self._deny(scope, send, 403, "bad origin")
            return
        if path.startswith("/api") and path not in PUBLIC_API:
            if not self._has_session(headers.get("cookie", "")):
                await self._deny(scope, send, 401, "no session")
                return

        await self.app(scope, receive, send)

    def _has_session(self, cookie_header: str) -> bool:
        jar = SimpleCookie()
        try:
            jar.load(cookie_header)
        except Exception:
            return False
        morsel = jar.get(self.cookie)
        return morsel is not None and hmac.compare_digest(morsel.value, self.token)

    @staticmethod
    async def _deny(scope: Scope, send: Send, status: int, reason: str) -> None:
        if scope["type"] == "websocket":
            # Closing before accept makes the server answer the handshake with 403.
            await send({"type": "websocket.close", "code": 1008, "reason": reason})
            return
        body = f'{{"detail":"{reason}"}}'.encode()
        await send({
            "type": "http.response.start",
            "status": status,
            "headers": [(b"content-type", b"application/json"),
                        (b"content-length", str(len(body)).encode())],
        })
        await send({"type": "http.response.body", "body": body})


class SessionRequest(BaseModel):
    token: str


def create_app(*, token: str, port: int = DEFAULT_PORT, dev: bool = False,
               dist: Path = DIST, root: Path = ROOT, watch: bool = True) -> FastAPI:
    paths = Paths(root)
    hub = EventHub()

    @asynccontextmanager
    async def lifespan(_app: FastAPI):
        stop = asyncio.Event()
        task = asyncio.create_task(watch_root(root, hub, stop)) if watch else None
        yield
        stop.set()
        if task:
            await task

    app = FastAPI(title="EpochZero Python", docs_url=None, redoc_url=None, openapi_url=None,
                  lifespan=lifespan)
    app.state.hub = hub

    @app.post("/api/session", status_code=204)
    def open_session(body: SessionRequest, response: Response) -> None:
        if not hmac.compare_digest(body.token, token):
            raise HTTPException(403, "bad token")
        response.set_cookie(cookie_name(port), token, httponly=True,
                            samesite="strict", path="/")

    @app.get("/api/status")
    def status() -> dict:
        return {"app": "epochzero-python", "version": "0.1.0", "root": str(root)}

    @app.get("/api/events")
    def events() -> StreamingResponse:
        return StreamingResponse(hub.stream(), media_type="text/event-stream",
                                 headers={"Cache-Control": "no-store"})

    app.include_router(tracker_api.router(paths))
    app.include_router(fs.router(paths))
    app.include_router(pty_ws.router(paths))
    app.include_router(tests_runner.router(paths))
    app.include_router(quizzes.router(paths))
    app.include_router(lessons.router(paths))

    if dist.is_dir():
        app.mount("/", StaticFiles(directory=dist, html=True), name="web")
    else:
        @app.get("/", response_class=HTMLResponse)
        def no_build() -> str:
            return ("<pre>EpochZero Python: web/dist not found. Run `pnpm -C web build`, "
                    "or start the Vite dev server with `pnpm -C web dev`.</pre>")

    app.add_middleware(GuardMiddleware, token=token, port=port, dev=dev)
    return app


def build_web() -> None:
    pnpm = shutil.which("pnpm")
    if pnpm is None:
        sys.exit("EpochZero Python: web/dist is missing and pnpm is not installed.")
    print("EpochZero Python: building web UI (first run)...", flush=True)
    if not (WEB / "node_modules").is_dir():
        subprocess.run([pnpm, "install", "--frozen-lockfile"], cwd=WEB, check=True)
    subprocess.run([pnpm, "build"], cwd=WEB, check=True)


def port_free(port: int) -> bool:
    """True unless something is listening on the port. SO_REUSEADDR, as uvicorn
    uses, so connections lingering in TIME_WAIT after a restart don't count. (On
    Windows SO_REUSEADDR would let us bind over a live listener; the default
    there already ignores TIME_WAIT, and SO_EXCLUSIVEADDRUSE refuses a listener.)"""
    with socket.socket() as s:
        if WINDOWS:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
        else:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            s.bind(("127.0.0.1", port))
        except OSError:
            return False
    return True


def run() -> None:
    utf8_stdio()
    parser = argparse.ArgumentParser(prog="epochzero")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--dev", action="store_true",
                        help="API only; open the Vite dev server (pnpm -C web dev) instead")
    parser.add_argument("--rebuild", action="store_true", help="rebuild web/dist first")
    parser.add_argument("--no-browser", action="store_true")
    parser.add_argument("--root", type=Path, default=ROOT,
                        help="directory holding CURRICULUM_TRACKER.md, progress/, workspace/")
    args = parser.parse_args()

    if not args.dev and (args.rebuild or not DIST.is_dir()):
        build_web()

    # Check before printing/opening the URL, or the browser lands on whatever
    # already holds the port with a token it doesn't know.
    if not port_free(args.port):
        sys.exit(f"EpochZero Python: 127.0.0.1:{args.port} is in use. Is it already running? "
                 "Try --port.")

    token = secrets.token_urlsafe(32)
    ui_port = VITE_PORT if args.dev else args.port
    url = f"http://127.0.0.1:{ui_port}/?token={token}"
    app = create_app(token=token, port=args.port, dev=args.dev, root=args.root.resolve())

    print(f"EpochZero Python ▸ {url}", flush=True)
    print("EpochZero Python ▸ bound to 127.0.0.1 only. Learner code runs as you; it is not sandboxed.",
          flush=True)
    if not args.no_browser:
        threading.Timer(1.0, webbrowser.open, [url]).start()

    # Never 0.0.0.0: this app executes arbitrary code.
    # The graceful-shutdown timeout stops open SSE streams from blocking Ctrl+C.
    uvicorn.run(app, host="127.0.0.1", port=args.port, log_level="warning",
                timeout_graceful_shutdown=1)


if __name__ == "__main__":
    run()
