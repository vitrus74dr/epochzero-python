#!/bin/sh
# Proves the starter tests can be passed: for each curriculum/weekN/stubs/<task>
# that has a reference solution in $EPOCHZERO_SOLUTIONS/weekN/<task>/ (a private
# folder outside this repo; solutions must never ship to students), copy the
# stub folder, overlay the solution's files, and require every test to pass.
# Tasks without a solution are listed as "-- ".
cd "$(dirname "$0")/.." || exit 2
ENV="$PWD/.learner-env"
SOL="${EPOCHZERO_SOLUTIONS:-$PWD/../pygrid-solutions}"
[ -d "$ENV" ] || { echo "run tools/learner_env.sh first"; exit 2; }
[ -d "$SOL" ] || { echo "no solutions folder at $SOL (set EPOCHZERO_SOLUTIONS); skipped"; exit 0; }
bad=0
for d in curriculum/week*/stubs/t*; do
  week=$(basename "$(dirname "$(dirname "$d")")"); task=$(basename "$d")
  s="$SOL/$week/$task"
  if [ ! -d "$s" ]; then echo "--  $d: no reference solution"; continue; fi
  tmp=$(mktemp -d); cp -r "$d"/. "$tmp"/; cp -r "$s"/. "$tmp"/
  out=$(cd "$tmp" && MPLBACKEND=Agg timeout 300 uv run -q --project "$ENV" python -m pytest -q -p no:cacheprovider 2>&1)
  last=$(printf '%s\n' "$out" | tail -1)
  case "$last" in
    *failed*|*error*|*"no tests"*|"") verdict="BAD"; bad=1; printf '%s\n' "$out" | grep -E "^(FAILED|ERROR|E )" | head -20 ;;
    *passed*) verdict="ok " ;;
    *) verdict="BAD"; bad=1 ;;
  esac
  echo "$verdict $d: $last"; rm -rf "$tmp"
done
exit $bad
