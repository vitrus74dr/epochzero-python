import shutil
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from server.main import create_app
from server.paths import Paths

REAL_TRACKER = Path(__file__).resolve().parent.parent / "CURRICULUM_TRACKER.md"
TOKEN = "t"
HOST = "127.0.0.1:8765"
ORIGIN = f"http://{HOST}"


@pytest.fixture
def paths(tmp_path) -> Paths:
    shutil.copy(REAL_TRACKER, tmp_path / "CURRICULUM_TRACKER.md")
    (tmp_path / "workspace").mkdir()
    return Paths(tmp_path)


@pytest.fixture
def client(paths) -> TestClient:
    app = create_app(token=TOKEN, root=paths.root, dist=paths.root / "nodist", watch=False)
    c = TestClient(app, base_url=f"http://{HOST}")
    assert c.post("/api/session", json={"token": TOKEN}).status_code == 204
    return c
