---
description: Author a 5-question quiz for a task, install it, and send the learner to the cockpit
argument-hint: <task, e.g. W1.2>
allowed-tools: Bash(pygrid-tutor:*), Read, Write
---
Write a quiz for task `$ARGUMENTS`.

1. Run `pygrid-tutor status` to see the task's items and the week's pitfalls. Read the learner's code
   for the task. If they took earlier quizzes, `pygrid-tutor quiz-results <id>` shows what they missed.
   Aim the questions at those weak spots.
2. Write a draft to `.pygrid/quiz_N_M.json` (inside workspace/; for task N.M) in this exact shape:
   ```json
   { "id": "WN.M.quiz", "title": "...", "pass_mark": 4,
     "questions": [
       { "id": "q1", "prompt": "What does `not (True and False)` evaluate to?",
         "choices": ["True", "False", "None", "SyntaxError"], "answer": 0,
         "explain": "True and False is False; not flips it to True." } ] }
   ```
   - 5 questions; `pass_mark` from the tracker item (≥ 4/5 means 4). `answer` is a 0-based index.
   - 3–4 choices each, with plausible distractors: the mistakes beginners really make (`=` vs `==`,
     `is` vs `==`, off-by-one, truthiness of `"0"` and `[]`). No joke answers.
   - Prefer "what does this print / evaluate to" with a short snippet in backticks.
   - `explain` says *why* in one or two sentences. The learner only sees it for questions they got right.
   - A task with a `Quiz:` item gets a graded quiz that records a verification. For any other task it's
     practice: same shape, use an id like `WN.M.check`, and nothing is recorded.
3. Install it with `pygrid-tutor quiz-add .pygrid/quiz_N_M.json`, and fix the draft until it says `installed`.
4. Tell the learner to take it in the cockpit: the **quiz** view (`g q`), or `pygrid-quiz WN.M.quiz` in
   the cockpit terminal. You can't drive the quiz from Bash. Don't reveal answers.
5. When they're done, run `pygrid-tutor quiz-results WN.M.quiz` and walk through each missed question
   Socratically: ask why they picked their answer before explaining. Don't paste the answer key; it's for you.
