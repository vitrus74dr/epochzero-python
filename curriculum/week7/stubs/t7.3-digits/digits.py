"""W7.3: handwritten digit recognizer.

    uv run python digits.py      # train, then print the rich report and confusion matrix

Needs: uv add scikit-learn rich
"""


def build_model():
    """Return an UNFITTED scikit-learn estimator, usually a Pipeline such as
    make_pipeline(StandardScaler(), SomeClassifier(...)).

    test_digits.py fits it on raw pixel values (0-16), so any scaling must be
    a step inside the model. Which classifier and settings: your /grill-me plan.
    """
    pass  # stub


def main() -> None:
    """Load the digits, split (stratified, fixed random_state), fit build_model(),
    and print a classification report and a confusion matrix as rich tables."""
    pass  # stub


if __name__ == "__main__":
    main()
