"""W4.5: turn a messy sales CSV into a clean summary and two charts.

    uv run python report.py sales.csv --out charts

Needs: uv add pandas matplotlib
"""

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # draw to files only: no window, works in tests and on servers
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402


def load(path: Path) -> pd.DataFrame:
    """Read the CSV as-is (no cleaning here)."""
    pass  # stub


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """A cleaned copy; the input DataFrame is left unchanged.

    - drop exact duplicate rows
    - `date` -> datetime
    - `amount` like "$1,234.50" -> float 1234.5; rows whose amount is missing
      or not a number are dropped
    - `region`: surrounding spaces stripped, Title Case ("  north " -> "North");
      missing or empty -> "Unknown"
    - `product`: surrounding spaces stripped
    - the index is reset to 0..n-1
    """
    pass  # stub


def monthly_totals(df: pd.DataFrame) -> pd.DataFrame:
    """Columns `month` ("2026-01" strings) and `total` (sum of amount, rounded
    to 2 decimals), one row per month, oldest first. Takes a cleaned frame."""
    pass  # stub


def by_region(df: pd.DataFrame) -> pd.DataFrame:
    """Columns `region`, `orders` (row count), `total` and `average` (amount,
    both rounded to 2 decimals), biggest total first. Takes a cleaned frame."""
    pass  # stub


def save_charts(df: pd.DataFrame, outdir: Path) -> list[Path]:
    """Save a bar chart of total by region (`by_region.png`) and a line chart
    of monthly totals (`monthly.png`) into outdir (created if needed).
    Return the two paths. Close each figure after saving."""
    pass  # stub


def main(argv: list[str] | None = None) -> int:
    """Load, clean, print both tables and the chart paths."""
    pass  # stub


if __name__ == "__main__":
    raise SystemExit(main())
