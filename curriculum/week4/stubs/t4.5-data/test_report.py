"""W4.5.c: cleaning and aggregation on small frames built right here, so every
expected number can be checked by hand. One test also reads the real sales.csv."""

from pathlib import Path

import pandas as pd
import pytest

from report import by_region, clean, load, main, monthly_totals, save_charts

HERE = Path(__file__).parent


@pytest.fixture
def raw() -> pd.DataFrame:
    return pd.DataFrame({
        "order_id": [1, 2, 2, 3, 4, 5, 6],
        "date": ["2026-01-05", "2026-01-20", "2026-01-20", "2026-02-02", "2026-02-10", "2026-02-11", "2026-03-01"],
        "region": ["North", "  south ", "  south ", None, "NORTH", "East", ""],
        "product": ["Pen", " Lamp", " Lamp", "Pen", "Pen", "Lamp", "Pen"],
        "qty": [1, 2, 2, 3, 1, 1, 2],
        "amount": ["$1.20", "$1,050.00", "$1,050.00", "$3.60", "n/a", None, "$2.40"],
    })


def test_clean(raw):
    before = raw.copy()
    df = clean(raw)
    pd.testing.assert_frame_equal(raw, before)             # input untouched
    assert list(df["order_id"]) == [1, 2, 3, 6]            # duplicate and bad amounts gone
    assert list(df.index) == [0, 1, 2, 3]
    assert list(df["amount"]) == [1.2, 1050.0, 3.6, 2.4]
    assert list(df["region"]) == ["North", "South", "Unknown", "Unknown"]
    assert list(df["product"]) == ["Pen", "Lamp", "Pen", "Pen"]
    assert pd.api.types.is_datetime64_any_dtype(df["date"])
    assert pd.api.types.is_float_dtype(df["amount"])


def test_monthly_totals(raw):
    m = monthly_totals(clean(raw))
    assert list(m.columns) == ["month", "total"]
    assert list(m["month"]) == ["2026-01", "2026-02", "2026-03"]
    assert list(m["total"]) == [1051.2, 3.6, 2.4]


def test_by_region(raw):
    r = by_region(clean(raw))
    assert list(r.columns) == ["region", "orders", "total", "average"]
    assert list(r["region"]) == ["South", "Unknown", "North"]
    assert list(r["orders"]) == [1, 2, 1]
    assert list(r["total"]) == [1050.0, 6.0, 1.2]
    assert list(r["average"]) == [1050.0, 3.0, 1.2]


def test_save_charts(raw, tmp_path):
    paths = save_charts(clean(raw), tmp_path / "charts")
    assert sorted(p.name for p in paths) == ["by_region.png", "monthly.png"]
    for p in paths:
        assert p.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"   # a real PNG file


def test_real_csv():
    df = clean(load(HERE / "sales.csv"))
    assert len(df) == 158                       # 162 rows - 2 duplicates - 2 bad amounts
    assert set(df["region"]) == {"North", "South", "East", "West", "Unknown"}
    assert df["amount"].max() == 1234.5


def test_main(tmp_path, capsys):
    assert main([str(HERE / "sales.csv"), "--out", str(tmp_path)]) == 0
    out = capsys.readouterr().out
    assert "North" in out and "2026-01" in out
    assert (tmp_path / "monthly.png").exists()
