import os

import pytest

from server.fs import SandboxError, resolve_in


@pytest.mark.parametrize("bad", [
    "../CURRICULUM_TRACKER.md", "week1/../../x.py", "/etc/passwd", "", "a\x00b",
    "..\\CURRICULUM_TRACKER.md",
])
def test_resolve_rejects_escapes(tmp_path, bad):
    with pytest.raises(SandboxError):
        resolve_in(tmp_path, bad)


def test_resolve_rejects_symlink_escape(tmp_path):
    ws = tmp_path / "ws"
    ws.mkdir()
    try:
        (ws / "link").symlink_to(tmp_path, target_is_directory=True)
    except OSError:
        pytest.skip("can't create symlinks here (Windows without Developer Mode)")
    with pytest.raises(SandboxError):
        resolve_in(ws, "link/secret.txt")


def test_api_rejects_traversal(client):
    for p in ["../CURRICULUM_TRACKER.md", "/etc/passwd", "a/../../x"]:
        assert client.get("/api/files", params={"path": p}).status_code == 403
        r = client.put("/api/files", params={"path": p}, json={"content": "x"})
        assert r.status_code == 403


def test_tree_hides_caches_and_lists_dirs_first(client, paths):
    ws = paths.workspace
    (ws / "week1" / "__pycache__").mkdir(parents=True)
    (ws / "week1" / "__pycache__" / "x.pyc").write_bytes(b"")
    (ws / "week1" / "calc.py").write_text("", encoding="utf-8")
    (ws / ".venv").mkdir()
    (ws / "CLAUDE.md").write_text("", encoding="utf-8")
    tree = client.get("/api/files/tree").json()["children"]
    assert [n["name"] for n in tree] == ["week1", "CLAUDE.md"]
    assert [n["path"] for n in tree[0]["children"]] == ["week1/calc.py"]


def test_create_read_update_cycle(client, paths):
    r = client.put("/api/files", params={"path": "week1/hello.py"},
                   json={"content": "print('hi')\n"})
    assert r.status_code == 200
    v1 = r.json()["version"]
    assert (paths.workspace / "week1" / "hello.py").read_text(encoding="utf-8") == "print('hi')\n"

    got = client.get("/api/files", params={"path": "week1/hello.py"}).json()
    assert got["content"] == "print('hi')\n" and got["version"] == v1

    r = client.put("/api/files", params={"path": "week1/hello.py"},
                   json={"content": "print('hey')\n", "base_version": v1})
    assert r.status_code == 200 and r.json()["version"] != v1


def test_create_refuses_to_overwrite_existing(client, paths):
    (paths.workspace / "a.py").write_text("x", encoding="utf-8")
    r = client.put("/api/files", params={"path": "a.py"}, json={"content": "y"})
    assert r.status_code == 409


def test_stale_save_conflicts_then_force_wins(client, paths):
    f = paths.workspace / "a.py"
    f.write_text("one\n", encoding="utf-8")
    v = client.get("/api/files", params={"path": "a.py"}).json()["version"]
    f.write_text("changed by claude code\n", encoding="utf-8")  # edit behind the editor's back
    r = client.put("/api/files", params={"path": "a.py"}, json={"content": "two\n", "base_version": v})
    assert r.status_code == 409 and "changed on disk" in r.json()["detail"]
    assert f.read_text(encoding="utf-8") == "changed by claude code\n"
    r = client.put("/api/files", params={"path": "a.py"},
                   json={"content": "two\n", "base_version": v, "force": True})
    assert r.status_code == 200 and f.read_text(encoding="utf-8") == "two\n"


@pytest.mark.skipif(os.name == "nt", reason="Windows has no POSIX file modes")
def test_save_keeps_file_mode(client, paths):
    f = paths.workspace / "run.sh"
    f.write_text("echo hi\n", encoding="utf-8")
    f.chmod(0o755)
    v = client.get("/api/files", params={"path": "run.sh"}).json()["version"]
    client.put("/api/files", params={"path": "run.sh"}, json={"content": "echo yo\n", "base_version": v})
    assert os.stat(f).st_mode & 0o777 == 0o755


def test_binary_and_missing_files(client, paths):
    (paths.workspace / "img.png").write_bytes(b"\x89PNG\xff\xfe")
    assert client.get("/api/files", params={"path": "img.png"}).status_code == 415
    assert client.get("/api/files", params={"path": "nope.py"}).status_code == 404


def test_image_preview(client, paths):
    png = b"\x89PNG\r\n\x1a\n" + b"\x00" * 16
    (paths.workspace / "charts").mkdir()
    (paths.workspace / "charts" / "monthly.png").write_bytes(png)
    r = client.get("/api/files/image", params={"path": "charts/monthly.png"})
    assert r.status_code == 200 and r.content == png
    assert r.headers["content-type"] == "image/png"
    assert r.headers["x-content-type-options"] == "nosniff"


@pytest.mark.parametrize("path,code", [
    ("evil.svg", 415),            # SVG can carry script: never served from our origin
    ("notes.txt", 415),
    ("missing.png", 404),
    ("../outside.png", 403),
])
def test_image_preview_refuses(client, paths, path, code):
    (paths.workspace / "evil.svg").write_text("<svg onload='alert(1)'/>", encoding="utf-8")
    (paths.workspace / "notes.txt").write_text("hi", encoding="utf-8")
    assert client.get("/api/files/image", params={"path": path}).status_code == code


def test_image_preview_needs_a_session(paths):
    from fastapi.testclient import TestClient

    from conftest import HOST
    from server.main import create_app
    (paths.workspace / "a.png").write_bytes(b"\x89PNG\r\n\x1a\n")
    c = TestClient(create_app(token="t", root=paths.root, dist=paths.root / "x", watch=False),
                   base_url=f"http://{HOST}")
    assert c.get("/api/files/image", params={"path": "a.png"}).status_code == 401
