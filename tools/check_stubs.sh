#!/bin/sh
# Every curriculum/week*/stubs/* folder, run in the learner env: its tests must
# fail cleanly on the untouched stubs (some failures, no passes, no errors).
# A pass means a test checks nothing; an error means the stub or test is broken.
cd "$(dirname "$0")/.." || exit 2
ENV="$PWD/.learner-env"
[ -d "$ENV" ] || { echo "run tools/learner_env.sh first"; exit 2; }
bad=0
for d in curriculum/week*/stubs/t*; do
  tmp=$(mktemp -d); cp -r "$d"/. "$tmp"/
  out=$(cd "$tmp" && MPLBACKEND=Agg timeout 120 uv run -q --project "$ENV" python -m pytest -q -p no:cacheprovider 2>&1 | tail -1)
  case "$out" in
    *passed*|*error*|*"no tests"*|"") verdict="BAD"; bad=1 ;;
    *failed*) verdict="ok " ;;
    *) verdict="BAD"; bad=1 ;;
  esac
  echo "$verdict $d: $out"; rm -rf "$tmp"
done
exit $bad
