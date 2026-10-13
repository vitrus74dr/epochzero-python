#!/bin/sh
# Create (or update) .learner-env/: a uv project with the libraries a learner
# installs during the course, at today's versions. The content checks run in it.
set -e
cd "$(dirname "$0")/.."
mkdir -p .learner-env
cd .learner-env
# --no-workspace: otherwise uv makes this a member of the app project and
# installs the learner libraries into the app's own environment.
[ -f pyproject.toml ] || uv init -q --bare --no-workspace --python 3.12 --name learner-env
uv add -q arcade scikit-learn pandas matplotlib "fastapi[standard]" joblib requests rich inquirer
uv add -q --dev pytest
uv pip list 2>/dev/null | grep -iE "^(arcade|pandas|scikit-learn|fastapi|matplotlib) "
