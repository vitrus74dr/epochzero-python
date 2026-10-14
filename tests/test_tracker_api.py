import json
import threading
from pathlib import Path

import pytest

from server import tracker as tr
from server.progress import ProgressError, load_state, write_checked
from server.paths import Paths
from server.tracker_api import CheckRefused, check_item
from server.verifications import Record, VerificationLog

REAL = Path(__file__).resolve().parent.parent / "CURRICULUM_TRACKER.md"


def verify(paths, item, passed=True):
    VerificationLog(paths.verifications).append(
        Record(item=item, kind="tutor", passed=passed, summary="test", by="claude-code"))


def test_get_tracker(client):
    data = client.get("/api/tracker").json()
    assert len(data["weeks"]) == 12
    assert data["weeks"][0]["unlocked"] and not data["weeks"][1]["unlocked"]
    assert data["weeks"][0]["total"] == 9 and data["weeks"][0]["done"] == 0
    assert data["current"]["item"]["id"] == "W1.1.a"
    assert data["current"]["task_title"] == "Environment & Hello World"
    assert data["completion"]["items"][0]["id"] == "W8.Z.a"
    assert data["recent"] == []


def test_check_refused_without_verification(client, paths):
    before = paths.tracker.read_bytes()
    r = client.post("/api/tracker/check", json={"item": "W1.1.a"})
    assert r.status_code == 409
    assert "no passing record" in r.json()["detail"]
    assert paths.tracker.read_bytes() == before


def test_failed_verification_does_not_count(client, paths):
    verify(paths, "W1.1.a", passed=False)
    assert client.post("/api/tracker/check", json={"item": "W1.1.a"}).status_code == 409


def test_check_with_verification_ticks_one_byte(client, paths):
    before = paths.tracker.read_text(encoding="utf-8")
    verify(paths, "W1.1.a")
    r = client.post("/api/tracker/check", json={"item": "W1.1.a"})
    assert r.status_code == 200
    data = r.json()
    assert data["weeks"][0]["done"] == 1
    assert data["current"]["item"]["id"] == "W1.1.b"
    assert data["recent"][0]["item"] == "W1.1.a"
    assert paths.tracker.read_text(encoding="utf-8") == before      # the curriculum file is never written
    assert json.loads(paths.checked.read_text(encoding="utf-8")) == {"checked": ["W1.1.a"]}


def test_locked_week_refused_even_with_verification(client, paths):
    verify(paths, "W2.1.a")
    r = client.post("/api/tracker/check", json={"item": "W2.1.a"})
    assert r.status_code == 409
    assert "week 2 is locked" in r.json()["detail"]


def test_untick_needs_no_verification(client, paths):
    verify(paths, "W1.1.a")
    client.post("/api/tracker/check", json={"item": "W1.1.a"})
    r = client.post("/api/tracker/check", json={"item": "W1.1.a", "checked": False})
    assert r.status_code == 200
    assert paths.tracker.read_bytes() == REAL.read_bytes()


def test_unknown_item_404(client):
    assert client.post("/api/tracker/check", json={"item": "W9.9.z"}).status_code == 404


def test_parse_error_is_422_with_line(client, paths):
    text = paths.tracker.read_text(encoding="utf-8").replace("[W1.1.b] ", "", 1)
    paths.tracker.write_text(text, encoding="utf-8")
    r = client.get("/api/tracker")
    assert r.status_code == 422
    assert r.json()["line"] > 0


def test_concurrent_ticks_all_persist(paths):
    week1 = [i.id for i in load_state(paths).weeks[0].items]
    for i in week1:
        verify(paths, i)
    errors = []

    def tick(item_id):
        try:
            check_item(paths, item_id)
        except Exception as e:  # pragma: no cover - surfaced below
            errors.append(e)

    threads = [threading.Thread(target=tick, args=(i,)) for i in week1]
    for th in threads:
        th.start()
    for th in threads:
        th.join()
    assert errors == []
    assert all(i.checked for i in load_state(paths).weeks[0].items)


def test_check_item_refuses_directly(paths):
    with pytest.raises(CheckRefused):
        check_item(paths, "W1.1.a")


def test_corrupt_log_lines_are_skipped(paths):
    paths.progress.mkdir()
    paths.verifications.write_text('{"item": "W1.1.a"\nnot json\n', encoding="utf-8")
    verify(paths, "W1.1.b")
    log = VerificationLog(paths.verifications)
    assert log.passing_items() == {"W1.1.b"}


def test_untick_removes_from_progress(client, paths):
    verify(paths, "W1.1.a")
    client.post("/api/tracker/check", json={"item": "W1.1.a"})
    r = client.post("/api/tracker/check", json={"item": "W1.1.a", "checked": False})
    assert r.status_code == 200 and r.json()["weeks"][0]["done"] == 0
    assert json.loads(paths.checked.read_text(encoding="utf-8")) == {"checked": []}


def test_legacy_ticks_in_the_tracker_are_imported_once(paths):
    text = paths.tracker.read_text(encoding="utf-8").replace("- [ ] [W1.1.a]", "- [x] [W1.1.a]")
    paths.tracker.write_text(text, encoding="utf-8")
    assert load_state(paths).item("W1.1.a").checked          # no progress file yet: imported
    write_checked(paths, set())                                # from now on the progress file rules
    assert not load_state(paths).item("W1.1.a").checked


def test_unknown_ids_in_progress_are_ignored(paths):
    write_checked(paths, {"W1.1.a", "W99.9.z"})
    t = load_state(paths)
    assert t.item("W1.1.a").checked and sum(i.checked for i in t.items()) == 1


def test_corrupt_progress_is_an_error_not_a_reset(client, paths):
    paths.checked.parent.mkdir(exist_ok=True)
    paths.checked.write_text("{oops")
    with pytest.raises(ProgressError):
        load_state(paths)
    r = client.get("/api/tracker")
    assert r.status_code == 422 and "checked.json" in r.json()["detail"]
    verify(paths, "W1.1.a")
    assert client.post("/api/tracker/check", json={"item": "W1.1.a"}).status_code == 422
    assert paths.checked.read_text(encoding="utf-8") == "{oops"                # not overwritten


def test_shipped_tracker_has_no_ticks():
    """The curriculum file in the repo stays pristine: ticks belong in progress/."""
    assert "- [x]" not in REAL.read_text(encoding="utf-8") and "- [X]" not in REAL.read_text(encoding="utf-8")
