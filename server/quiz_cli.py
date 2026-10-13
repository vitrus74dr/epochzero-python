"""Terminal quiz runner: `epochzero-quiz W1.2.quiz` (or `python -m server.quiz_cli`).

The same spec, grading and result file as the browser quiz (server/quizzes.py),
rendered with rich and answered with inquirer arrow-key prompts. Needs a real
TTY, so the cockpit launches it in its pty terminal; Claude Code's Bash can't
drive it. Like the browser, it never reveals the answer to a missed question:
the tutor walks through those from the result file.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import inquirer
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.text import Text
from rich.theme import Theme

from server import quizzes
from server.paths import ROOT, Paths

# Plain ANSI colours, so the terminal's token-built palette decides the actual
# shades; no hard-coded backgrounds that would clash with the light theme.
OK, BAD, DIM, ACCENT = "green", "red", "bright_black", "cyan"
THEME = Theme({"markdown.code": ACCENT, "markdown.code_block": ACCENT})


def ask(console: Console, quiz: quizzes.Quiz) -> dict[str, int] | None:
    answers: dict[str, int] = {}
    total = len(quiz.questions)
    for n, q in enumerate(quiz.questions, 1):
        console.print()
        console.print(Text(f"── {n}/{total} ", style=DIM), end="")
        console.print(Markdown(q.prompt))
        choice = inquirer.list_input(
            "answer", choices=[(c, i) for i, c in enumerate(q.choices)])
        if choice is None:  # Ctrl+C inside inquirer
            return None
        answers[q.id] = choice
    return answers


def report(console: Console, quiz: quizzes.Quiz, attempt: dict) -> None:
    by_id = {q.id: q for q in quiz.questions}
    console.print()
    for a in attempt["answers"]:
        q = by_id[a["q"]]
        tag = ("[ PASS ] ", OK) if a["correct"] else ("[ FAIL ] ", BAD)
        console.print(Text.assemble(tag, (q.id, "bold")))
        if not a["correct"]:
            console.print(Text(f"  you chose: {q.choices[a['choice']]}", style=DIM))
        elif q.explain:
            console.print(Text("  ") + Text(q.explain))
    verdict = ("[ PASS ]", OK) if attempt["passed"] else ("[ FAIL ]", BAD)
    console.print()
    console.print(Panel(
        Text.assemble((verdict[0], verdict[1]),
                      f"  {attempt['score']}/{attempt['total']}  (pass mark {attempt['pass_mark']})"
                      f"  ·  recorded for {attempt['item']}" if attempt["item"]
                      else "  ·  practice (not recorded)"),
        border_style=DIM, expand=False))
    if attempt["answers"] and not all(a["correct"] for a in attempt["answers"]):
        console.print(Text("Ask the tutor to walk through the missed questions.", style=DIM))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="epochzero-quiz")
    parser.add_argument("quiz_id", help="e.g. W1.2.quiz")
    parser.add_argument("--root", type=Path, default=Path(os.environ.get("EPOCHZERO_ROOT") or ROOT))
    args = parser.parse_args(argv)
    paths = Paths(args.root.resolve())
    console = Console(theme=THEME)

    try:
        quiz = quizzes.get(paths, args.quiz_id)
    except KeyError as e:
        console.print(Text(f"epochzero-quiz: {e.args[0]}", style=BAD))
        return 2
    if not sys.stdin.isatty():
        console.print(Text("epochzero-quiz needs an interactive terminal. "
                           "Run it from the cockpit's terminal.", style=BAD))
        return 2

    console.print(Panel(Text.assemble((f"{quiz.id}  ", ACCENT), quiz.title,
                                      (f"\n{len(quiz.questions)} questions · pass mark "
                                       f"{quiz.pass_mark} · ↑/↓ then Enter", DIM)),
                        title="QUIZ", title_align="left", border_style=DIM, expand=False))
    try:
        answers = ask(console, quiz)
    except KeyboardInterrupt:
        answers = None
    if answers is None:
        console.print(Text("\nQuiz abandoned. Nothing was recorded.", style=DIM))
        return 130

    try:
        attempt = quizzes.record_attempt(paths, quiz, answers, by="cli")
    except quizzes.QuizError as e:
        console.print(Text(f"Not recorded: {e}", style=BAD))
        return 1
    report(console, quiz, attempt)
    return 0 if attempt["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
