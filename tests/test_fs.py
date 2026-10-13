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
    (ws / "link").symlink_to(tmp_path)
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
    assert (paths.workspace / "week1" / "hello.py").read_text() == "print('hi')\n"

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
    assert f.read_text() == "changed by claude code\n"
    r = client.put("/api/files", params={"path": "a.py"},
                   json={"content": "two\n", "base_version": v, "force": True})
    assert r.status_code == 200 and f.read_text() == "two\n"


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
