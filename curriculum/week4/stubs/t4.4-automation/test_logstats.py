"""W4.4.c: log parsing and the summary."""

from logstats import main, parse_line, summarize

LOG = """\
2026-10-13 09:15:02 INFO [web] server started
2026-10-13 14:02:11 ERROR [db] connection refused
2026-10-13 14:05:40 WARNING [web] slow response: 2.3s
2026-10-13 14:30:00 ERROR [db] connection refused
this line is garbage
2026-10-13 15:01:09 CRITICAL [disk] disk full
2026-10-13 15:20:33 ERROR [web] template missing

2026-10-13 16:45:00 INFO [web] server stopped
"""


def test_parse_line():
    assert parse_line("2026-10-13 14:02:11 ERROR [db] connection refused") == {
        "date": "2026-10-13", "hour": 14, "level": "ERROR", "source": "db",
        "message": "connection refused"}


def test_parse_line_keeps_message_spaces_and_colons():
    rec = parse_line("  2026-10-13 14:05:40 WARNING [web] slow response: 2.3s \n")
    assert rec["message"] == "slow response: 2.3s" and rec["hour"] == 14


def test_parse_line_rejects_junk():
    assert parse_line("2026-10-13 14:02:11 DEBUG [db] fine") is not None
    for line in ["", "garbage", "2026-10-13 14:02:11 LOUD [db] what", "2026-10-13 ERROR [db] no time"]:
        assert parse_line(line) is None


def test_summarize():
    s = summarize(LOG.splitlines())
    assert s["levels"] == {"INFO": 2, "ERROR": 3, "WARNING": 1, "CRITICAL": 1}
    assert s["top_errors"] == [("connection refused", 2), ("disk full", 1), ("template missing", 1)]
    assert s["busiest_hour"] == 14
    assert s["parsed"] == 7 and s["skipped"] == 1   # blank lines don't count


def test_summarize_empty():
    s = summarize([])
    assert s["levels"] == {} and s["top_errors"] == [] and s["busiest_hour"] is None
    assert s["parsed"] == 0 and s["skipped"] == 0


def test_busiest_hour_tie_goes_to_earliest():
    lines = ["2026-10-13 15:00:00 INFO [a] x", "2026-10-13 09:00:00 INFO [a] y"]
    assert summarize(lines)["busiest_hour"] == 9


def test_main(tmp_path, capsys):
    log = tmp_path / "app.log"
    log.write_text(LOG, encoding="utf-8")
    assert main([str(log)]) == 0
    out = capsys.readouterr().out
    assert "connection refused" in out and "14" in out
