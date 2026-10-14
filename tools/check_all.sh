#!/bin/sh
# Everything: app tests, UI build, lesson snippets (Arcade headless), stubs, reference
# solutions (when $EPOCHZERO_SOLUTIONS or ../pygrid-solutions exists), levels.
# Exit status 1 if any step fails.
cd "$(dirname "$0")/.." || exit 2
[ -d .learner-env ] || tools/learner_env.sh || exit 2
fail=0
step() { echo; echo "== $1"; }

step "app tests"
out=$(uv run pytest -q 2>&1 | tail -1); echo "$out"
case "$out" in *failed*|*error*) fail=1 ;; *passed*) ;; *) fail=1 ;; esac

step "UI typecheck + build (and the committed build is current)"
if pnpm -C web -s build >/dev/null 2>&1; then
  # web/dist is committed so students don't need Node; it must match the source.
  if [ -z "$(git status --porcelain -- web/dist)" ]; then echo ok
  else echo "web/dist differs from a fresh build: commit it"; git status --short -- web/dist | head -5; fail=1; fi
else echo FAILED; fail=1; fi

step "lesson snippets"
out=$(ARCADE_HEADLESS=1 uv run -q --project .learner-env python tools/check_md.py curriculum/week*/lesson_*.md 2>&1)
if [ $? -eq 0 ]; then echo "all $(echo "$out" | grep -c ': OK$') lessons ok"; else echo "$out" | grep -v ": OK$"; fail=1; fi

step "starter tests fail cleanly on the stubs"
out=$(tools/check_stubs.sh)
if [ $? -eq 0 ]; then echo "all $(echo "$out" | grep -c '^ok') stub folders ok"; else echo "$out" | grep -v "^ok "; fail=1; fi

step "starter tests pass with the reference solutions (private, outside the repo)"
out=$(tools/check_solutions.sh)
if [ $? -eq 0 ]; then
  n=$(echo "$out" | grep -c '^ok'); missing=$(echo "$out" | grep -c '^-- ')
  case "$out" in "no solutions folder"*) echo "$out" ;; *) echo "$n stub folders ok, $missing without a solution" ;; esac
else echo "$out" | grep -v "^ok "; fail=1; fi

step "platformer levels reachable"
python3 tools/check_levels.py curriculum/week6/stubs/t6.3-platformer/levels/*.txt || fail=1

echo; [ $fail -eq 0 ] && echo "ALL CHECKS PASSED" || echo "SOME CHECKS FAILED"
exit $fail
