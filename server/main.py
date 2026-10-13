"""PYGRID app factory and launcher.

Security model (see HANDOFF.md §7): the server binds 127.0.0.1 only, rejects
requests whose Host/Origin aren't this app (DNS rebinding, cross-site
WebSockets), and requires a per-launch session cookie on every /api route.
The cookie is obtained by POSTing the token from the launch URL to
/api/session, so the token never has to live in page JS after startup.
"""

from __future__ import annotations

import argparse
import hmac
import secrets
import shutil
import socket
import subprocess
import sys
import threading
import webbrowser
from http.cookies import SimpleCookie
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from starlette.types import ASGIApp, Receive, Scope, Send

ROOT = Path(__file__).resolve().parent.parent
WEB = ROOT / "web"
DIST = WEB / "dist"
DEFAULT_PORT = 8765
VITE_PORT = 5173

# Routes reachable without a session cookie. /api/session is how you get one.
PUBLIC_API = {"/api/session"}


def cookie_name(port: int) -> str:
    # Cookies aren't port-scoped, so include the port to keep two
    # instances on different ports from clobbering each other.
    return f"pygrid_session_{port}"


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
               dist: Path = DIST) -> FastAPI:
    app = FastAPI(title="PYGRID", docs_url=None, redoc_url=None, openapi_url=None)

    @app.post("/api/session", status_code=204)
    def open_session(body: SessionRequest, response: Response) -> None:
        if not hmac.compare_digest(body.token, token):
            raise HTTPException(403, "bad token")
        response.set_cookie(cookie_name(port), token, httponly=True,
                            samesite="strict", path="/")

    @app.get("/api/status")
    def status() -> dict:
        return {"app": "pygrid", "version": "0.1.0", "root": str(ROOT)}

    if dist.is_dir():
        app.mount("/", StaticFiles(directory=dist, html=True), name="web")
    else:
        @app.get("/", response_class=HTMLResponse)
        def no_build() -> str:
            return ("<pre>PYGRID: web/dist not found. Run `pnpm -C web build`, "
                    "or start the Vite dev server with `pnpm -C web dev`.</pre>")

    app.add_middleware(GuardMiddleware, token=token, port=port, dev=dev)
    return app


def build_web() -> None:
    pnpm = shutil.which("pnpm")
    if pnpm is None:
        sys.exit("PYGRID: web/dist is missing and pnpm is not installed.")
    print("PYGRID: building web UI (first run)...", flush=True)
    if not (WEB / "node_modules").is_dir():
        subprocess.run([pnpm, "install", "--frozen-lockfile"], cwd=WEB, check=True)
    subprocess.run([pnpm, "build"], cwd=WEB, check=True)


def port_free(port: int) -> bool:
    with socket.socket() as s:
        try:
            s.bind(("127.0.0.1", port))
        except OSError:
            return False
    return True


def run() -> None:
    parser = argparse.ArgumentParser(prog="pygrid")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--dev", action="store_true",
                        help="API only; open the Vite dev server (pnpm -C web dev) instead")
    parser.add_argument("--rebuild", action="store_true", help="rebuild web/dist first")
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args()

    if not args.dev and (args.rebuild or not DIST.is_dir()):
        build_web()

    # Check before printing/opening the URL, or the browser lands on whatever
    # already holds the port with a token it doesn't know.
    if not port_free(args.port):
        sys.exit(f"PYGRID: 127.0.0.1:{args.port} is in use. Is PYGRID already running? "
                 "Try --port.")

    token = secrets.token_urlsafe(32)
    ui_port = VITE_PORT if args.dev else args.port
    url = f"http://127.0.0.1:{ui_port}/?token={token}"
    app = create_app(token=token, port=args.port, dev=args.dev)

    print(f"PYGRID ▸ {url}", flush=True)
    print("PYGRID ▸ bound to 127.0.0.1 only. Learner code runs as you; it is not sandboxed.",
          flush=True)
    if not args.no_browser:
        threading.Timer(1.0, webbrowser.open, [url]).start()

    # Never 0.0.0.0: this app executes arbitrary code.
    uvicorn.run(app, host="127.0.0.1", port=args.port, log_level="warning")


if __name__ == "__main__":
    run()
