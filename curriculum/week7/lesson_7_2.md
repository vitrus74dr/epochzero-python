# Training a Classifier, Honestly

Fitting a model takes three lines. The hard part, and the part that matters, is
**measuring it honestly**. A model that scores 100% on the data it learned from might be
useless on anything new. This lesson is about train/test discipline, and the bug that
sinks real ML projects: **data leakage**.

## 1. Fit and predict

Every scikit-learn model has the same two core methods:

```python
from sklearn.datasets import load_iris
from sklearn.neighbors import KNeighborsClassifier

X, y = load_iris(return_X_y=True)
model = KNeighborsClassifier(n_neighbors=5)
model.fit(X, y)                    # learn from examples
model.predict([[5.0, 3.4, 1.5, 0.2]])   # array([0]): setosa
```

**k-nearest neighbours (KNN)** predicts by finding the `k` training samples closest to
the new one, and letting them vote. A **decision tree** learns a flowchart of yes/no
questions ("petal length < 2.45 cm?"). Same interface, different models: swapping one
for the other is a one-line change.

## 2. Never grade on the training data

```python
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier

X, y = load_iris(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=42, stratify=y)

tree = DecisionTreeClassifier(random_state=42).fit(X_train, y_train)
tree.score(X_train, y_train)    # 1.0
tree.score(X_test, y_test)      # ≈ 0.89
```

On data it has seen, the tree is perfect: it memorised it. On the **held-out test
set**, the 38 flowers it never saw, it scores about 0.89. That gap is **overfitting**,
and the test score is the only honest one.

`train_test_split`'s arguments, all of which matter:

| Argument | Why |
|---|---|
| `test_size=0.25` | keep a quarter of the data hidden for the final grade |
| `random_state=42` | the shuffle is random. Fixing the seed makes your results repeatable, for you, the tutor and the tests |
| `stratify=y` | keep the class proportions the same in both parts. Without it, an unlucky split could put few virginicas in the test set |

## 3. Data leakage

**Leakage** is when information from the test set sneaks into training. The model then
looks better than it really is, and the truth only shows up in production. The common ways:

- **Preprocessing before splitting.** Scaling the whole dataset (Week 8), then splitting:
  the scaler has seen the test set's mean and spread. Always split **first**, then fit
  preprocessing on the training part only. Week 8's Pipelines make this automatic.
- **Choosing settings by test score.** Try 20 values of `k`, keep the best *test* score,
  and you've tuned to the test set: it's no longer a fair final exam. Choose settings
  with **cross-validation** on the training data, and touch the test set once, at the end.
- **Duplicates across the split.** The same sample in both parts tests memory, not learning.
- **Features that encode the answer.** A "was readmitted" column in a model predicting readmission.

## 4. Cross-validation

```python
from sklearn.model_selection import cross_val_score
from sklearn.neighbors import KNeighborsClassifier

for k in (1, 3, 5, 9, 15):
    scores = cross_val_score(KNeighborsClassifier(n_neighbors=k), X_train, y_train, cv=5)
    print(k, scores.mean().round(3))
```

`cv=5` splits the *training* data into five parts, trains on four and scores on the
fifth, five times round, then averages. You pick `k` from these numbers; the test set
stays untouched.

## 5. Your turn

**W7.2.a (tutor check):** `week7/t7.2-classify/classify.py`:

1. Split iris with `random_state` and `stratify` set.
2. Use cross-validation to choose `k` for KNN *and* `max_depth` for a decision tree.
3. Fit both winners on the full training set, then score each **once** on the test set.
4. Print a table: model, chosen setting, cross-validation mean, test score.

Explain to the tutor why you didn't just pick the settings with the best test score.

**W7.2.b (quiz):** five questions on leakage and train/test discipline; you need 4/5.
[Take the quiz](#/quiz/W7.2.quiz), or run `epochzero-quiz W7.2.quiz`.

## Pitfalls

- Reporting the training score as "accuracy".
- Scaling or otherwise preprocessing before `train_test_split`.
- Tuning against the test set.
- No `random_state`: results change every run, and nobody can reproduce them.
