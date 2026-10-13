# The Preprocessing Problem

Real tables mix kinds of data: numbers on wildly different scales, and categories stored
as text or codes. Most models need every feature as a number on a comparable scale. This
lesson covers the two workhorse transformers, and the rule that keeps them honest.

## 1. Why scale?

Two features: income in dollars (20,000–200,000) and age in years (18–90). To a
distance-based model like KNN, a difference of 1,000 dollars outweighs a difference of
50 years: the bigger numbers dominate, whatever they mean. **Standardising** puts every
numeric feature on the same footing: mean 0, standard deviation 1.

```python
import numpy as np
from sklearn.preprocessing import StandardScaler

X_train = np.array([[50_000, 30], [80_000, 45], [20_000, 25], [110_000, 60]], dtype=float)
scaler = StandardScaler()
Z = scaler.fit_transform(X_train)
Z.mean(axis=0).round(6), Z.std(axis=0).round(6)     # (array([0., 0.]), array([1., 1.]))
scaler.mean_            # the column means, 65000 and 40, learned from the TRAINING data
```

Every transformer follows the same pattern as models:

- `fit(X)` **learns** something from the data (here, each column's mean and spread)
- `transform(X)` **applies** it
- `fit_transform(X)` does both, on training data

## 2. The golden rule: fit on train, transform both

```python
X_test = np.array([[65_000, 40]], dtype=float)
scaler.transform(X_test)         # uses the TRAINING mean and spread: array([[0., 0.]])
```

Never call `fit` or `fit_transform` on the test set. The test data must be transformed
*exactly* the way new data will be in real use, with statistics learned from training data
only. Fitting on test data is leakage (Lesson 7.2).

## 3. Categories: one-hot encoding

A `colour` column holding `"red"`, `"green"`, `"blue"` can't go into maths as text. And
coding them 0, 1, 2 invents an order (is blue "twice" green?). **One-hot encoding** makes
one 0/1 column per category:

```python
import pandas as pd
from sklearn.preprocessing import OneHotEncoder

train = pd.DataFrame({"colour": ["red", "green", "blue", "green"]})
enc = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
enc.fit_transform(train)
# array([[0., 0., 1.],      categories are sorted: blue, green, red
#        [0., 1., 0.],
#        [1., 0., 0.],
#        [0., 1., 0.]])
enc.get_feature_names_out()        # array(['colour_blue', 'colour_green', 'colour_red'], dtype=object)
```

- `handle_unknown="ignore"`: a category the encoder never saw in training (say,
  `"purple"`) becomes all zeros instead of crashing your app in production.
- `sparse_output=False` returns a normal array. (By default you get a memory-saving
  *sparse* matrix, which is harder to look at.)

```python
enc.transform(pd.DataFrame({"colour": ["purple"]}))    # array([[0., 0., 0.]])
```

Numbers can be categories too: a code such as `sex` stored as 1 or 2 is a label, not an
amount. You'll meet exactly that in Lesson 8.3.

## 4. Your turn (W8.1.a)

`week8/t8.1-preprocess/preprocess.py`, with this small mixed table:

```python fragment
df = pd.DataFrame({
    "age":    [25, 32, 47, 51, 62, 23],
    "income": [32_000, 48_000, 90_000, 61_000, 120_000, 28_000],
    "city":   ["Leeds", "York", "Leeds", "Hull", "York", "Hull"],
})
```

1. Split it (4 train, 2 test rows).
2. Scale `age` and `income` with a `StandardScaler` fitted on the train rows; one-hot
   `city` with `handle_unknown="ignore"`.
3. Transform the test rows, *and* a new row from `"Bath"`. Show the tutor what happens to Bath.

Next lesson does all of this in one object.

## Pitfalls

- `fit_transform` on test data.
- Integer codes for categories that have no order.
- Forgetting `handle_unknown="ignore"`: the first unseen category in production raises an error.
