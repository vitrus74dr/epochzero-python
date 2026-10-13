import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocket, WebSocketDisconnect

from server.main import cookie_name, create_app

TOKEN = "test-token"
PORT = 8765
HOST = f"127.0.0.1:{PORT}"
ORIGIN = f"http://{HOST}"


@pytest.fixture
def app(tmp_path):
    app = create_app(token=TOKEN, port=PORT, dist=tmp_path / "missing")

    @app.websocket("/api/echo")
    async def echo(ws: WebSocket):
        await ws.accept()
        await ws.send_text(await ws.receive_text())
        await ws.close()

    return app


@pytest.fixture
def client(app):
    return TestClient(app, base_url=f"http://{HOST}")


def login(client):
    r = client.post("/api/session", json={"token": TOKEN}, headers={"Origin": ORIGIN})
    assert r.status_code == 204


def test_api_requires_session(client):
    assert client.get("/api/status").status_code == 401


def test_session_with_wrong_token_is_refused(client):
    r = client.post("/api/session", json={"token": "nope"}, headers={"Origin": ORIGIN})
    assert r.status_code == 403
    assert client.get("/api/status").status_code == 401


def test_session_cookie_is_strict_and_httponly(client):
    r = client.post("/api/session", json={"token": TOKEN})
    cookie = r.headers["set-cookie"].lower()
    assert cookie.startswith(cookie_name(PORT))
    assert "httponly" in cookie and "samesite=strict" in cookie


def test_status_after_login(client):
    login(client)
    r = client.get("/api/status")
    assert r.status_code == 200
    assert r.json()["app"] == "pygrid"


@pytest.mark.parametrize("host", ["evil.example:8765", "127.0.0.1:9999", "0.0.0.0:8765"])
def test_foreign_host_rejected(client, host):
    login(client)
    assert client.get("/api/status", headers={"Host": host}).status_code == 403


def test_foreign_origin_rejected_even_with_session(client):
    login(client)
    r = client.get("/api/status", headers={"Origin": "http://evil.example"})
    assert r.status_code == 403


def test_vite_origin_only_allowed_in_dev(tmp_path):
    vite = {"Host": "127.0.0.1:5173", "Origin": "http://127.0.0.1:5173"}
    prod = TestClient(create_app(token=TOKEN, port=PORT, dist=tmp_path))
    dev = TestClient(create_app(token=TOKEN, port=PORT, dev=True, dist=tmp_path))
    assert prod.post("/api/session", json={"token": TOKEN}, headers=vite).status_code == 403
    assert dev.post("/api/session", json={"token": TOKEN}, headers=vite).status_code == 204


def test_websocket_requires_session(client):
    with pytest.raises(WebSocketDisconnect):
        with client.websocket_connect(f"ws://{HOST}/api/echo", headers={"Origin": ORIGIN}):
            pass


def test_websocket_cross_origin_rejected(client):
    login(client)
    with pytest.raises(WebSocketDisconnect):
        with client.websocket_connect(f"ws://{HOST}/api/echo", headers={"Origin": "http://evil.example"}):
            pass


def test_websocket_works_with_session(client):
    login(client)
    with client.websocket_connect(f"ws://{HOST}/api/echo", headers={"Origin": ORIGIN}) as ws:
        ws.send_text("ping")
        assert ws.receive_text() == "ping"


def test_static_root_is_public(client):
    # The page shell needs no session; it's how the browser gets the token flow.
    assert client.get("/").status_code == 200
