"""W7.3.d: the model must clearly beat a guessing baseline on unseen digits."""

import pytest
from sklearn.base import clone
from sklearn.datasets import load_digits
from sklearn.dummy import DummyClassifier
from sklearn.exceptions import NotFittedError
from sklearn.model_selection import train_test_split
from sklearn.utils.validation import check_is_fitted

from digits import build_model

MARGIN = 0.5


@pytest.fixture(scope="module")
def split():
    X, y = load_digits(return_X_y=True)
    return train_test_split(X, y, test_size=0.25, random_state=0, stratify=y)


def test_build_model_is_unfitted():
    model = build_model()
    assert hasattr(model, "fit") and hasattr(model, "predict"), "return a scikit-learn estimator"
    with pytest.raises(NotFittedError):
        check_is_fitted(model)


def test_beats_the_baseline(split):
    X_train, X_test, y_train, y_test = split
    baseline = DummyClassifier().fit(X_train, y_train).score(X_test, y_test)
    accuracy = clone(build_model()).fit(X_train, y_train).score(X_test, y_test)
    assert accuracy >= baseline + MARGIN, f"accuracy {accuracy:.3f} vs baseline {baseline:.3f}"


def test_predicts_every_test_digit(split):
    X_train, X_test, y_train, _ = split
    predictions = build_model().fit(X_train, y_train).predict(X_test)
    assert predictions.shape == (len(X_test),)
    assert set(predictions) <= set(range(10))
