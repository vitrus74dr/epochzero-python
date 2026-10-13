"""W8.3: health predictor on the diabetes dataset.

    uv run python health.py    # tune, report test R² vs a DummyRegressor, save model.joblib

Needs: uv add scikit-learn pandas joblib
"""


def build_search():
    """Return an UNFITTED GridSearchCV whose estimator is a Pipeline:
    a ColumnTransformer (one-hot `sex`, scale the other nine columns) followed
    by a regressor, and whose param grid tunes a setting inside the pipeline
    (e.g. {"ridge__alpha": [...]}). Use scoring="r2"."""
    pass  # stub


def main() -> None:
    """load_diabetes(scaled=False, as_frame=True); split (fixed random_state);
    fit build_search() on the training part; print the best params, test R²
    and DummyRegressor R²; save best_estimator_ to model.joblib."""
    pass  # stub


if __name__ == "__main__":
    main()
