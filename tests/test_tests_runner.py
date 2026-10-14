import json
import sys

import pytest

from conftest import HOST
from server import tests_runner
from server.tests_runner import parse_junit, summarize
from server.verifications import VerificationLog

PASSING = "def test_a():\n    assert 1 + 1 == 2\n\ndef test_b():\n    assert 'x'\n"
FAILING = "def test_ok():\n    pass\n\ndef test_bad():\n    assert 2 + 2 == 5, 'math'\n"


@pytest.fixture(autouse=True)
def app_python(monkeypatch):
    # The learner's env may not have pytest; the app's dev env does.
    monkeypatch.setattr(tests_runner, "learner_python", lambda ws, start: [sys.executable])


def run(client, **body) -> tuple[int, list[dict]]:
    r = client.post("/api/tests/run", json=body)
    if r.status_code != 200:
        return r.status_code, [r.json()]
    return 200, [json.loads(line) for line in r.text.splitlines() if line]


def task(paths, files: dict[str, str], folder="week1/calc") -> str:
    d = paths.workspace / folder
    d.mkdir(parents=True)
    for name, body in files.items():
        (d / name).write_text(body)
    return folder


def test_pass_records_and_unlocks_tick(client, paths):
    folder = task(paths, {"test_calc.py": PASSING})
    status, events = run(client, path=folder, item="W1.1.c")
    assert status == 200
    assert events[0]["type"] == "start" and events[0]["cwd"] == folder
    assert any(e["type"] == "output" for e in events)
    result = events[-1]
    assert result["type"] == "result"
    assert result["passed"] and result["summary"] == "2 passed"
    assert [t["outcome"] for t in result["tests"]] == ["passed", "passed"]
    [record] = result["records"]
    assert record["item"] == "W1.1.c" and record["kind"] == "pytest"
    [rec] = VerificationLog(paths.verifications).read()
    assert rec.passed and rec.by == "app"
    assert client.post("/api/tracker/check", json={"item": "W1.1.c"}).status_code == 200


def test_failure_shows_fail_and_blocks_tick(client, paths):
    folder = task(paths, {"test_calc.py": FAILING})
    _, events = run(client, path=folder, item="W1.1.c")
    result = events[-1]
    assert not result["passed"] and result["summary"] == "1 passed, 1 failed"
    bad = next(t for t in result["tests"] if t["outcome"] == "failed")
    assert bad["name"] == "test_bad" and "math" in bad["message"]
    assert "assert" in bad["detail"]
    assert "test_bad" in "".join(e["data"] for e in events if e["type"] == "output")
    [rec] = VerificationLog(paths.verifications).read()
    assert not rec.passed
    assert client.post("/api/tracker/check", json={"item": "W1.1.c"}).status_code == 409


def test_without_item_records_nothing(client, paths):
    folder = task(paths, {"test_calc.py": PASSING})
    _, events = run(client, path=folder)
    assert events[-1]["passed"] and events[-1]["records"] == []
    assert VerificationLog(paths.verifications).read() == []


def test_single_file(client, paths):
    folder = task(paths, {"test_one.py": PASSING, "test_two.py": FAILING})
    _, events = run(client, path=f"{folder}/test_one.py")
    assert events[-1]["passed"] and len(events[-1]["tests"]) == 2


def test_no_tests_is_not_a_pass(client, paths):
    folder = task(paths, {"calc.py": "print('hi')\n"})
    _, events = run(client, path=folder, item="W1.1.c")
    assert not events[-1]["passed"] and events[-1]["summary"] == "no tests collected"


def test_collection_error_fails(client, paths):
    folder = task(paths, {"test_calc.py": "import nope_not_a_module\n"})
    _, events = run(client, path=folder)
    assert not events[-1]["passed"] and "error" in events[-1]["summary"]


@pytest.mark.parametrize("item,detail", [
    ("W1.2.b", "verified by quiz"),
    ("W1.1.a", "verified by tutor"),
    ("W2.1.b", "locked week"),
    ("W9.9.z", "no item"),
])
def test_item_must_be_unlocked_pytest_item(client, paths, item, detail):
    folder = task(paths, {"test_calc.py": PASSING})
    status, [body] = run(client, path=folder, item=item)
    assert status == 409 and detail in body["detail"]


@pytest.mark.parametrize("path,code", [("../x", 403), ("nope", 404), ("notes.md", 422)])
def test_bad_paths(client, paths, path, code):
    (paths.workspace / "notes.md").write_text("hi")
    assert run(client, path=path)[0] == code


def test_missing_pytest_is_explained(client, paths, monkeypatch, tmp_path):
    fake = tmp_path / "no_pytest.py"     # a "python" whose -m pytest fails like the real thing
    fake.write_text("import sys\nprint('No module named pytest', file=sys.stderr)\nsys.exit(1)\n")
    monkeypatch.setattr(tests_runner, "learner_python", lambda ws, start: [sys.executable, str(fake)])
    folder = task(paths, {"test_calc.py": PASSING})
    _, events = run(client, path=folder)
    assert "uv add --dev pytest" in events[-1]["error"]


def test_requires_session(paths):
    from fastapi.testclient import TestClient
    from server.main import create_app
    c = TestClient(create_app(token="t", root=paths.root, dist=paths.root / "nd", watch=False),
                   base_url=f"http://{HOST}")
    assert c.post("/api/tests/run", json={"path": "x"}).status_code == 401


def test_summarize_and_parse():
    xml = """<testsuites><testsuite>
      <testcase classname="test_c" name="test_a" time="0.01"/>
      <testcase classname="test_c" name="test_b"><failure message="boom">trace</failure></testcase>
      <testcase classname="test_c" name="test_c"><skipped message="later"/></testcase>
    </testsuite></testsuites>"""
    tests = parse_junit(xml)
    assert [t["outcome"] for t in tests] == ["passed", "failed", "skipped"]
    assert tests[1]["id"] == "test_c::test_b" and tests[1]["detail"] == "trace"
    assert summarize(tests, 1)[:2] == (False, "1 passed, 1 failed, 1 skipped")
    assert summarize(tests[:1], 0)[0] is True
    assert summarize([dict(tests[0], outcome="skipped")], 0)[0] is False


def test_learner_tests_ignore_the_app_pytest_config(tmp_path):
    """workspace/pytest.ini stops pytest walking up to the app's pyproject.toml, whose
    options (timeout, pythonpath=tests) aren't the learner's: on a fresh clone every run
    warned "Unknown config option: timeout"."""
    import shutil
    import subprocess

    from server.paths import ROOT
    shutil.copy(ROOT / "pyproject.toml", tmp_path / "pyproject.toml")
    ws = tmp_path / "workspace"
    (ws / "week1" / "t").mkdir(parents=True)
    shutil.copy(ROOT / "workspace" / "pytest.ini", ws / "pytest.ini")
    (ws / "week1" / "t" / "test_x.py").write_text(PASSING)
    out = subprocess.run([sys.executable, "-m", "pytest", "-p", "no:cacheprovider", "."],
                         cwd=ws / "week1" / "t", capture_output=True, text=True).stdout
    assert f"rootdir: {ws}" in out and "configfile: pytest.ini" in out
    assert "Unknown config option" not in out and "2 passed" in out
    ignored = subprocess.run(["git", "check-ignore", "-q", "workspace/pytest.ini"], cwd=ROOT)
    assert ignored.returncode == 1, "workspace/pytest.ini must not be gitignored: students need it"
