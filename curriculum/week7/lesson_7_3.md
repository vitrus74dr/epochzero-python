# Handwritten Digit Recognizer

A program that reads handwritten digits: the problem that launched modern machine
learning. You'll train a model on 1,797 tiny scanned digits, prove it's genuinely good
(not just better than nothing), and present the results like a professional.

## 1. The data

```python
from sklearn.datasets import load_digits

digits = load_digits()
```

```python
>>> digits.images.shape, digits.data.shape
((1797, 8, 8), (1797, 64))
>>> digits.data.min(), digits.data.max()
(np.float64(0.0), np.float64(16.0))
```

Each digit is an 8×8 grayscale image with pixel values 0–16. `images` keeps the 8×8
shape for display; `data` flattens each image into 64 features for the model.

**Try it:** show the first digits with matplotlib:

```python
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.datasets import load_digits

digits = load_digits()
fig, axes = plt.subplots(1, 8, figsize=(8, 1.5))
for ax, image, label in zip(axes, digits.images, digits.target):
    ax.imshow(image, cmap="gray_r")
    ax.set_title(label)
    ax.axis("off")
fig.savefig("digits.png")
plt.close(fig)
```

## 2. A baseline first

How good is "good"? Always compare with a **baseline**, a model that doesn't look at the
features at all. `DummyClassifier` predicts the most common class every time:

```python
from sklearn.datasets import load_digits
from sklearn.dummy import DummyClassifier
from sklearn.model_selection import train_test_split

X, y = load_digits(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=0, stratify=y)
DummyClassifier().fit(X_train, y_train).score(X_test, y_test)    # ≈ 0.10
```

With ten roughly equal classes, guessing gets about 10%. Your model must beat it **by a
clear margin**, and W7.3.d checks exactly that.

## 3. Pipelines: preprocessing that can't leak

Some models (KNN, support vector machines) care about feature scale. Put the scaler and
the model in one **Pipeline**, which behaves like a single model:

```python
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

model = make_pipeline(StandardScaler(), KNeighborsClassifier())
model.fit(X_train, y_train)        # the scaler learns from the TRAINING data only
model.score(X_test, y_test)        # ≈ 0.97; the test data is scaled with training statistics
```

This is why W7.3.b says scaling lives *inside* a Pipeline: `fit` can't accidentally see the
test set (Lesson 7.2, section 3), and cross-validation re-fits the scaler on each fold.

## 4. Beyond accuracy

Accuracy is one number. Which digits get confused with which?

```python
from sklearn.metrics import classification_report, confusion_matrix

predicted = model.predict(X_test)
print(classification_report(y_test, predicted))
matrix = confusion_matrix(y_test, predicted)    # rows: true digit, columns: predicted
```

- **precision** for digit 8: of everything predicted "8", how much really was an 8?
- **recall** for digit 8: of all the real 8s, how many were found?
- In the **confusion matrix**, the diagonal holds the correct predictions. Anything off
  it is a mistake, and `matrix[3][8]` counts the 3s mistaken for 8s.

W7.3.c wants both printed as `rich` tables (Lesson 2.3). Colour the diagonal green and
the biggest off-diagonal count red, so the worst confusion jumps out.

## 5. The test contract

`epochzero-tutor scaffold W7.3` gives you `test_digits.py`. It needs one function from
`digits.py`:

```python fragment
def build_model():
    """An *unfitted* scikit-learn estimator (usually a Pipeline)."""
```

The test splits the data itself (stratified, fixed seed), fits your model, and requires
its test accuracy to beat `DummyClassifier` by at least **0.5**. It feeds your model the
raw pixel values, so any scaling has to happen inside the model, which means inside a Pipeline. Which model, which settings, and how you tune them
(cross-validation, Lesson 7.2) are yours to decide at `/grill-me`.

## 6. How it's checked

- **W7.3.a**: `/grill-me W7.3` (which models you'll compare, how you'll choose, and why).
- **W7.3.b–c**: tutor review: the Pipeline, and the `rich` report and confusion matrix.
- **W7.3.d**: `/verify W7.3`.
- **W7.3.e**: `walkthrough.md`, including which digits your model confuses most, and a guess at why.

## Pitfalls

- Scaling outside the Pipeline: leakage, and the test's raw pixels won't be scaled.
- No baseline. "97%" means nothing until you know guessing gets 10%.
- Reading the confusion matrix backwards: rows are the truth.
- Plotting with `plt.show()` in a script that should just save images.
