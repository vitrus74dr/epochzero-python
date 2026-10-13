# Data App: CSV Report with pandas

Spreadsheets full of real data are messy: dollar signs in number columns, blank cells,
`"north"` vs `"North"`, the same row pasted twice. You'll build a report generator that
cleans a sales CSV, summarizes it, and draws charts, using the two libraries every
Python data job starts with: **pandas** for tables, **matplotlib** for charts. Week 8's
machine learning uses pandas too, so this is the foundation.

```sh
uv add pandas matplotlib
```

Run `pygrid-tutor scaffold W4.5` for `report.py` (stubs), `test_report.py` and `sales.csv`.
Open `sales.csv` in the workbench first and look for the mess yourself.

> This course uses **pandas 3**. Many tutorials online were written for pandas 1 or 2
> and behave differently on three points (section 5). When an example from the web
> doesn't work, check its date.

## 1. DataFrames

A `DataFrame` is a table: named columns, each holding one type.

```python
import pandas as pd

df = pd.DataFrame({
    "product": ["Pen", "Lamp", "Pen"],
    "region": ["North", "South", "North"],
    "amount": [1.2, 24.99, 3.6],
})
df.shape                 # (3, 3): rows, columns
df["amount"].sum()       # a column is a Series
df[df["region"] == "North"]          # filter rows with a boolean mask
df.sort_values("amount", ascending=False).head(2)
```

From a file: `pd.read_csv("sales.csv")`. Then always look before you touch:
`df.head()`, `df.dtypes`, `df.isna().sum()` (missing values per column) and
`df.duplicated().sum()`.

**Try it:** in `uv run python`, load `sales.csv` and run those four. Which columns are
the wrong type, and why?

## 2. Cleaning, one column at a time

`amount` was read as text because of `"$4.80"` and `"n/a"`. Strip the symbols, then
convert. `errors="coerce"` turns anything unparseable into `NaN` ("not a number") instead of crashing:

```python
s = pd.Series(["$4.80", "$1,234.50", "n/a", None])
cleaned = s.str.replace(r"[$,]", "", regex=True)
pd.to_numeric(cleaned, errors="coerce").tolist()     # [4.8, 1234.5, nan, nan]
```

The `.str` accessor applies a string method to every value: `.str.strip()`,
`.str.title()`, `.str.lower()`. Missing values stay missing, so fill them before or
after, as the case needs: `fillna("Unknown")`.

Rows you can't use: `df.dropna(subset=["amount"])`. Exact duplicates:
`df.drop_duplicates()`. Dates: `pd.to_datetime(df["date"])`, after which `df["date"].dt.month`
and friends work.

`clean()` must **return a new frame** and leave its input alone (the test checks).
Start it with `df = df.drop_duplicates().copy()` and build from there.

## 3. Group and aggregate

"Total per region" is *split → apply → combine*:

```python
summary = (
    df.groupby("region")["amount"]
      .agg(orders="count", total="sum", average="mean")
      .round(2)
      .sort_values("total", ascending=False)
      .reset_index()
)
```

Each `name="function"` inside `.agg()` becomes a column. `.reset_index()` turns the
group keys back into a normal column. For months, group by a *period*:
`df.groupby(df["date"].dt.to_period("M"))`; the periods become `"2026-01"` with `astype(str)`.

## 4. Charts with matplotlib

```python
import matplotlib
matplotlib.use("Agg")              # draw to files, never open a window
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(6, 4))
ax.bar(["North", "South"], [120.5, 98.0])
ax.set_title("Sales by region")
ax.set_ylabel("Total ($)")
fig.tight_layout()
fig.savefig("by_region.png", dpi=120)
plt.close(fig)                      # free the memory; important in loops and tests
```

`ax.plot(x, y, marker="o")` draws a line chart. The `Agg` line must come **before**
`import matplotlib.pyplot`; it's why the report works in tests and on servers with no
screen. (`plt.show()` would open a window and pause your program; a report never does that.)

## 5. pandas 3: what changed

```python
import pandas as pd

df = pd.DataFrame({"name": ["Ada", "Grace"], "score": [90, 85]})
str(df.dtypes["name"])   # 'str': a real string type, no longer `object`
```

**Chained assignment doesn't work any more.** This *looks* like it sets a value:

```python fragment
df["score"][0] = 100     # ⚠ changes nothing; warns ChainedAssignmentError
```

`df["score"]` gives you a new object, and you change *that*. Use a single `.loc[row, column]`:

```python
df.loc[0, "score"] = 100   # works
```

**Copy-on-write:** a filtered frame behaves as an independent copy. Changing it never
changes the original, and the old `SettingWithCopyWarning` is gone.

## 6. How it's checked

- **W4.5.a–b** (tutor checks): run `uv run python report.py sales.csv --out charts`, then
  open the two PNGs (the workbench file tree shows them) and explain each chart.
- **W4.5.c**: `/verify W4.5`. The tests use tiny frames where you can check every
  number by hand. Read `test_clean` first: it is the cleaning spec.

## Pitfalls

- `df["col"][i] = value` (section 5). Use `.loc`.
- `plt.show()` in a report, or forgetting `matplotlib.use("Agg")` before importing pyplot.
- Cleaning in place and surprising the caller: return a new frame.
- Comparing floats with `==` after maths. The tests round to 2 decimals for this reason.
