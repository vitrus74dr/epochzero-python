# Health Predictor (Diabetes)

A complete, honest machine-learning workflow on real medical data: predict how far a
patient's diabetes will progress in a year, from ten measurements. It's **regression**
(predicting a number), with mixed feature types, a tuned pipeline, and a baseline
comparison that decides whether the model is worth anything. Next task, you'll serve it as a web app.

## 1. The data

```python
from sklearn.datasets import load_diabetes

data = load_diabetes(scaled=False, as_frame=True)
X, y = data.data, data.target
```

```python
>>> X.shape
(442, 10)
>>> list(X.columns)
['age', 'sex', 'bmi', 'bp', 's1', 's2', 's3', 's4', 's5', 's6']
>>> sorted(X["sex"].unique())
[np.float64(1.0), np.float64(2.0)]
```

`y` is a disease-progression score (25–346). `s1`–`s6` are blood measurements.

Two details that older tutorials get wrong:

- **`scaled=False`**. By default, `load_diabetes()` returns features that are *already*
  centred and scaled, so adding a `StandardScaler` does nothing, and `sex` becomes two
  odd decimals. With `scaled=False` you get the raw values and do the preprocessing
  yourself, properly, inside a pipeline.
- **`sex` is a category**, coded 1 or 2. It gets one-hot encoded; every other feature is
  numeric and gets scaled.

## 2. The pipeline

```python
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

numeric = [c for c in X.columns if c != "sex"]
pre = ColumnTransformer([
    ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), ["sex"]),
    ("num", StandardScaler(), numeric),
])
pipeline = make_pipeline(pre, Ridge())
list(pipeline.named_steps)     # ['columntransformer', 'ridge']
```

**Ridge** is linear regression with a penalty that keeps the coefficients small. That
helps when features are correlated, as these blood measurements are. Its penalty
strength, `alpha`, is what you'll tune.

## 3. Tuning with `GridSearchCV`, on training data only

```python
from sklearn.model_selection import GridSearchCV, train_test_split

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

search = GridSearchCV(pipeline, {"ridge__alpha": [0.1, 1, 10, 100]}, cv=5, scoring="r2")
search.fit(X_train, y_train)
search.best_params_            # {'ridge__alpha': 10}
```

`GridSearchCV` tries each `alpha` with 5-fold cross-validation **inside the training
set**, re-fitting the whole pipeline (scaler included) on every fold, and then re-fits
the winner on all of `X_train`. The test set is untouched until the end (W8.3.c).

## 4. R², and the baseline

For regression, **R²** ("R squared") measures the share of the variation in `y` the
model explains: 1.0 is perfect, and **0.0 is no better than always predicting the
mean**. It can go negative: a model can be worse than that.

```python
from sklearn.dummy import DummyRegressor

search.score(X_test, y_test)                                    # ≈ 0.46
DummyRegressor().fit(X_train, y_train).score(X_test, y_test)    # ≈ -0.01: predicts the mean
```

A positive R² is a low bar. The real question is "better than the dummy?", and here it
is, clearly. For medical data like this, explaining about half the variation from ten
routine measurements is a genuinely useful result.

## 5. The test contract

`pygrid-tutor scaffold W8.3` gives `test_health.py`, which needs one function from `health.py`:

```python fragment
def build_search():
    """An UNFITTED GridSearchCV over a Pipeline whose ColumnTransformer
    one-hot encodes `sex` and scales the other columns."""
```

The test does its own split, fits your search on the training part only, and checks:
the test R² is positive and beats `DummyRegressor` by a clear margin; `sex` is one-hot
encoded (two `sex` columns appear in the feature names); and the grid tunes something
inside the pipeline.

## 6. Saving the model for Task 8.4

```python fragment
import joblib
joblib.dump(search.best_estimator_, "model.joblib")
model = joblib.load("model.joblib")        # later, in the web app
```

Only load model files you created yourself: unpickling a file can run arbitrary code.

## 7. How it's checked

- **W8.3.a**: `/grill-me W8.3` (features, which model, which grid, how you'll judge it).
- **W8.3.b–c**: tutor review: `scaled=False`, the ColumnTransformer, and a grid search fitted on training data.
- **W8.3.d**: `/verify W8.3`, and the script itself runs end to end.
- **W8.3.e**: `walkthrough.md`, including what R² means in plain words.

## Pitfalls

- `load_diabetes()` without `scaled=False`.
- Treating `sex` as a number to be scaled.
- Running `GridSearchCV` on all the data, or choosing `alpha` by test score.
- Reporting R² without the baseline next to it.
