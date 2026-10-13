---
description: Run pytest for a task or item and record the result as a verification
argument-hint: <task or item, e.g. W1.3 or W1.3.c> [--path <folder>]
allowed-tools: Bash(epochzero-tutor:*), Read
---
Verify `$ARGUMENTS` with the tutor CLI. Don't run pytest yourself and don't try to write progress
files: the CLI runs pytest in the learner's environment and appends the record.

1. Run `epochzero-tutor verify $ARGUMENTS`
   - With a task (`W1.3`) it verifies every pytest item in that task; with an item (`W1.3.c`), just that one.
   - It runs in the task folder `weekN/tN.M-<slug>/`. If it says there's no folder, find where the
     learner's tests are and pass `--path weekN/<folder>`.
   - "refused" means a gate said no (wrong kind of item, locked week). Explain it; don't work around it.
2. Report the RESULT line and what was recorded.
3. On **FAIL**: don't fix the code. Read the failing test and the learner's code, then give the
   Socratic treatment from CLAUDE.md: what the failure means, plus one question that points at the cause.
4. On **PASS**: say the item is ready and suggest `/checkoff <item>`. For W2.3.d, first confirm the
   learner has also done the manual run in the cockpit terminal.

The cockpit updates live: the record appears under "Recent" and the item's box becomes tickable.
