---
description: Architecture interview before a [PROJECT]; writes implementation_plan.md from the learner's answers
argument-hint: <task, e.g. W1.3>
allowed-tools: Bash(pygrid-tutor:*), Read, Write
---
Run the design interview for project task `$ARGUMENTS` before any code is written.

1. Run `pygrid-tutor status`. The task's items are the acceptance criteria.
2. Ask **4–6 questions, one at a time**, and wait for each answer. Cover:
   - the data model (what values/objects exist, and their types)
   - function or class boundaries (what is pure logic, what does I/O)
   - the error strategy (which exceptions, where they're caught, what the user sees)
   - how it will be tested (which functions, which edge cases)
   - for Arcade/scikit-learn tasks, the API approach (check the installed version's docs first)
3. Don't give answers. If an answer is weak, ask a follow-up or name the trade-off, and let the
   learner decide. Only after they've committed may you say what you'd have chosen and why.
4. Create the task folder `weekN/tN.M-<slug>/` (short kebab-case slug, e.g. `week1/t1.3-calculator`) if it
   doesn't exist, and write `implementation_plan.md` there **from the learner's answers only**:
   ```markdown
   # Implementation plan: <project>
   ## Goal
   ## Data model
   ## Structure        (files, functions/classes, which are pure)
   ## Error handling
   ## Tests            (test names and the edge cases each covers)
   ## Open questions
   ```
5. Ask the learner to read it (cockpit dashboard: the task's `[ plan ]` link) and approve it. When
   they approve: `pygrid-tutor record WN.M.a --kind artifact --summary "plan approved by learner"`,
   then `/checkoff WN.M.a`.
6. Next (per CLAUDE.md): `pygrid-tutor scaffold WN.M`, read the starter tests, and add tests for the
   functions in the plan, before the learner writes any logic.
