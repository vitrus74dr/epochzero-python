# Building the Pipeline

Last lesson's preprocessing took a dozen careful lines, with plenty of chances to fit
something on the wrong data. scikit-learn can bundle it all into one object, which you
`fit` once on training data and which then can't leak.

## 1. `ColumnTransformer`: different columns, different treatment

```python
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler

df = pd.DataFrame({
    "age":    [25, 32, 47, 51, 62, 23],
    "income": [32_000, 48_000, 90_000, 61_000, 120_000, 28_000],
    "city":   ["Leeds", "York", "Leeds", "Hull", "York", "Hull"],
    "id":     [101, 102, 103, 104, 105, 106],
})

pre = ColumnTransformer([
    ("num", StandardScaler(), ["age", "income"]),
    ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), ["city"]),
], remainder="drop")

out = pre.fit_transform(df)
out.shape                       # (6, 5): 2 scaled + 3 one-hot columns
pre.get_feature_names_out()
# array(['num__age', 'num__income', 'cat__city_Hull', 'cat__city_Leeds', 'cat__city_York'], dtype=object)
```

Each entry is `(name, transformer, columns)`. The names prefix the output feature names.

## 2. `remainder`: what about the other columns?

Columns not listed (here `id`) are handled by `remainder`:

| `remainder=` | Effect |
|---|---|
| `"drop"` (the default) | unlisted columns are **removed** |
| `"passthrough"` | unlisted columns are **kept unchanged** |

```python
keep = ColumnTransformer([
    ("cat", OneHotEncoder(sparse_output=False), ["city"]),
], remainder="passthrough")
keep.fit_transform(df).shape    # (6, 6): 3 one-hot + age, income and id untouched
```

`"passthrough"` is handy, and dangerous: an ID column slipping into a model lets it
"learn" row numbers. Be deliberate: list what you use and drop the rest.

## 3. `Pipeline`: preprocessing plus model, as one estimator

```python
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline, make_pipeline

model = Pipeline([
    ("pre", pre),
    ("clf", LogisticRegression()),
])
# or, with names generated from the class names:
model = make_pipeline(pre, LogisticRegression())
list(model.named_steps)         # ['columntransformer', 'logisticregression']
```

A Pipeline *is* an estimator: `model.fit(X_train, y_train)` fits each step on the
training data in turn, and `model.predict(X_test)` transforms with what was learned, then
predicts. Cross-validation and grid search re-fit the **whole** pipeline on each fold, so
the preprocessing never sees held-out data.

## 4. Reaching inside: `step__param`

To change a setting deep inside a pipeline, join the step names with double underscores:

```python
model.set_params(logisticregression__C=0.5)
model.get_params()["columntransformer__num__with_mean"]      # True
```

This naming is how `GridSearchCV` (next lesson) tunes settings inside a pipeline:
`{"ridge__alpha": [0.1, 1, 10]}` means "the `alpha` of the step called `ridge`".

## 5. Your turn

**W8.2.a (tutor check):** redo Lesson 8.1's exercise with one `ColumnTransformer`. Then
switch `remainder` between `"drop"` and `"passthrough"` with the `id` column present, print
the output shape and feature names each time, and explain the difference to the tutor.

**W8.2.b (tutor check):** wrap it with a classifier in a pipeline. Invent a target, say
`bought = [0, 0, 1, 1, 1, 0]`, then fit, predict a new row (including an unseen city), and
read back one parameter with `get_params()` using the `step__param` syntax.

## Pitfalls

- `remainder="passthrough"` letting an ID or a target-like column into the model.
- A single underscore in `step__param` names: it's **two**.
- Preprocessing outside the pipeline, which puts the leakage back.
