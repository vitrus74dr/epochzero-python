#!/bin/sh
# Everything: app tests, UI build, lesson snippets (Arcade headless), stubs, levels.
# Exit status 1 if any step fails.
cd "$(dirname "$0")/.." || exit 2
[ -d .learner-env ] || tools/learner_env.sh || exit 2
fail=0
step() { echo; echo "== $1"; }

step "app tests"
out=$(uv run pytest -q 2>&1 | tail -1); echo "$out"
case "$out" in *failed*|*error*) fail=1 ;; *passed*) ;; *) fail=1 ;; esac

step "UI typecheck + build"
pnpm -C web -s build >/dev/null 2>&1 && echo ok || { echo FAILED; fail=1; }

step "lesson snippets"
out=$(ARCADE_HEADLESS=1 uv run -q --project .learner-env python tools/check_md.py curriculum/week*/lesson_*.md 2>&1)
if [ $? -eq 0 ]; then echo "all $(echo "$out" | grep -c ': OK$') lessons ok"; else echo "$out" | grep -v ": OK$"; fail=1; fi

step "starter tests fail cleanly on the stubs"
out=$(tools/check_stubs.sh)
if [ $? -eq 0 ]; then echo "all $(echo "$out" | grep -c '^ok') stub folders ok"; else echo "$out" | grep -v "^ok "; fail=1; fi

step "platformer levels reachable"
python3 tools/check_levels.py curriculum/week6/stubs/t6.3-platformer/levels/*.txt || fail=1

echo; [ $fail -eq 0 ] && echo "ALL CHECKS PASSED" || echo "SOME CHECKS FAILED"
exit $fail
