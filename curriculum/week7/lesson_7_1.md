# Datasets: Machine Learning's Raw Material

Machine learning means writing programs that learn rules from **examples** instead of
having the rules typed in. Weeks 7–8 use **scikit-learn**, the standard Python library
for it. Every project starts the same way: understand the data before you fit anything.

```sh
uv add scikit-learn
```

## 1. The vocabulary

| Term | Means | Shape |
|---|---|---|
| **sample** | one example: a flower, an image, a patient | a row |
| **feature** | a measured property: petal length, a pixel, blood pressure | a column |
| **`X`** | the feature table, every sample × every feature | `(n_samples, n_features)` |
| **`y`** | the **target**: what we want to predict, one per sample | `(n_samples,)` |
| **classification** | `y` is a category (species, digit 0–9) | |
| **regression** | `y` is a number (a disease progression score) | |

By convention, `X` is a capital letter (a 2-D table) and `y` is lower case (a 1-D list).

## 2. The iris dataset

Botanist Ronald Fisher measured 150 iris flowers in 1936. It's the "hello world" of ML:

```python
from sklearn.datasets import load_iris

iris = load_iris()
X, y = iris.data, iris.target
```

```python
>>> X.shape, y.shape
((150, 4), (150,))
>>> iris.feature_names
['sepal length (cm)', 'sepal width (cm)', 'petal length (cm)', 'petal width (cm)']
>>> list(iris.target_names)
[np.str_('setosa'), np.str_('versicolor'), np.str_('virginica')]
>>> X[0], y[0]
(array([5.1, 3.5, 1.4, 0.2]), np.int64(0))
```

`X` is a **NumPy array**: like a list of lists, but every number has the same type, and
maths works on whole columns at once. `y` holds 0, 1 or 2: indexes into `target_names`.
(`np.str_` and `np.int64` are NumPy's own types; they behave like `str` and `int`.)

## 3. NumPy in five minutes

```python
import numpy as np

a = np.array([[1, 2, 3],
              [4, 5, 6]])
a.shape            # (2, 3)
a[0]               # the first row: array([1, 2, 3])
a[:, 1]            # the second column, from every row: array([2, 5])
a.mean(axis=0)     # mean of each column: array([2.5, 3.5, 4.5])
a * 10             # every element times 10, no loop needed
a[a > 2]           # a boolean mask: array([3, 4, 5, 6])
np.bincount([0, 1, 1, 2, 2, 2])   # how many of each value: array([1, 2, 3])
```

`[:, 1]` reads "every row, column 1". `axis=0` means "down the rows", giving one result per column.

## 4. Look before you learn

Get the data as a pandas DataFrame (Lesson 4.5) for easy exploring:

```python
from sklearn.datasets import load_iris

frame = load_iris(as_frame=True).frame
frame.head()
frame.describe()                            # count, mean, std, min, max per column
frame.groupby("target").mean().round(2)     # average measurements per species
```

Questions to always ask:

- **How many samples of each class?** `np.bincount(y)`: iris has 50 / 50 / 50. A
  *balanced* dataset like this makes accuracy easy to interpret; an unbalanced one
  doesn't (Lesson 7.3).
- **What range is each feature?** If one feature runs 0–1 and another 0–1000, some
  models will be dominated by the big one (Week 8: scaling).
- **Anything missing or odd?** `frame.isna().sum()`.

## 5. Your turn (W7.1.a)

In `week7/t7.1-iris/explore.py`:

1. Load iris; print `X.shape`, `y.shape`, the feature and target names, and the class counts.
2. Print the mean of each feature per species (pandas `groupby`).
3. Save a scatter plot of petal length vs petal width, coloured by species, to
   `petals.png` (matplotlib, Lesson 4.5).

Then look at the plot and tell the tutor: which species could you separate with a single
straight line, and which two overlap? You've just done what a classifier does.

## Pitfalls

- Mixing up `X` (2-D, all features) and `y` (1-D, the answers).
- Assuming classes are balanced without checking.
- Using Python loops where NumPy does it per column (`a.mean(axis=0)`).
