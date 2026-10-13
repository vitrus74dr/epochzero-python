"""W8.3.d: an honest regression model that clearly beats predicting the mean."""

import functools

from sklearn.compose import ColumnTransformer
from sklearn.datasets import load_diabetes
from sklearn.dummy import DummyRegressor
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.pipeline import Pipeline

from health import build_search

MARGIN = 0.25


@functools.cache
def fit_once():
    """Split, then fit build_search() on the training part. Cached: fitted once."""
    data = load_diabetes(scaled=False, as_frame=True)
    X_train, X_test, y_train, y_test = train_test_split(
        data.data, data.target, test_size=0.2, random_state=42)
    search = build_search()
    assert isinstance(search, GridSearchCV), "build_search() should return a GridSearchCV"
    assert not hasattr(search, "best_estimator_"), "return it unfitted; the test fits it"
    search.fit(X_train, y_train)
    return search, X_train, X_test, y_train, y_test


def test_grid_tunes_inside_the_pipeline():
    search = fit_once()[0]
    assert isinstance(search.estimator, Pipeline)
    grid = search.param_grid if isinstance(search.param_grid, list) else [search.param_grid]
    assert all("__" in key for g in grid for key in g), "use step__param names"


def test_sex_is_one_hot_encoded():
    best = fit_once()[0].best_estimator_
    pre = next(step for step in best.named_steps.values() if isinstance(step, ColumnTransformer))
    names = [n for n in pre.get_feature_names_out() if "sex" in n]
    assert len(names) == 2, f"expected two one-hot sex columns, got {names}"


def test_beats_the_baseline():
    search, X_train, X_test, y_train, y_test = fit_once()
    r2 = search.score(X_test, y_test)
    baseline = DummyRegressor().fit(X_train, y_train).score(X_test, y_test)
    assert r2 > 0, f"test R² {r2:.3f} is no better than predicting the mean"
    assert r2 >= baseline + MARGIN, f"R² {r2:.3f} vs baseline {baseline:.3f}"
