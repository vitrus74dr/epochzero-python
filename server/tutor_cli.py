"""`epochzero-tutor`: the tutor's (Claude Code's) way to read progress and record checks.

The slash commands in workspace/.claude/commands/ call this through Bash, so
the tutor never edits CURRICULUM_TRACKER.md or progress/ by hand. It uses the
same code as the app: run_pytest() for /verify, check_item() for /checkoff,
VerificationLog for tutor/artifact records. The app sees every change live
through its file watcher.

    epochzero-tutor status
    epochzero-tutor scaffold W1.3                      # copy the task's starter files/tests
    epochzero-tutor verify W1.3 [--path week1/t1.3-calculator]   # or one item: W1.3.c
    epochzero-tutor record W1.1.a --kind tutor --summary "uv venv on 3.12 confirmed"
    epochzero-tutor record W1.3.a --kind artifact
    epochzero-tutor checkoff W1.3.c [--undo]
    epochzero-tutor quiz-check .epochzero/quiz_1_2.json
    epochzero-tutor quiz-add .epochzero/quiz_1_2.json      # validate, install into curriculum/
    epochzero-tutor lesson-add 2.1 .epochzero/lesson_2_1.md  # install a new or replacement lesson
    epochzero-tutor quiz-results W1.2.quiz

Claude Code only lets the tutor session touch files inside workspace/, so
anything outside it (tracker, progress/, curriculum/) goes through here.

Exit codes: 0 done, 1 refused or failed, 2 bad usage.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import re
import sys
from pathlib import Path

from pydantic import ValidationError

from server import lessons, quizzes
from server import tracker as tr
from server.fs import SandboxError, resolve_in
from server.paths import ROOT, Paths
from server.tasks import DOCS, FolderError, task_folder
from server.tests_runner import RunRefused, check_item_for_pytest, run_pytest
from server.tracker_api import CheckRefused, check_item
from server.verifications import Record, VerificationLog, verify_kind

BY = "claude-code"
ITEM_RE = re.compile(r"^W\d+\.(\d+|Z)\.[a-z]+$")
MIN_DOC_CHARS = 200  # an artifact must be more than a stub


class Usage(Exception):
    """Bad input: exit 2."""


class Refused(Exception):
    """A gate said no: exit 1."""


def find_task(t: tr.Tracker, task_id: str) -> tuple[tr.Week, tr.Task]:
    for w in t.weeks:
        for task in w.tasks:
            if task.id == task_id:
                return w, task
    raise Usage(f"no task {task_id} in the tracker")


def task_of(item_id: str) -> str:
    return ".".join(item_id[1:].split(".")[:2])


def workspace_path(paths: Paths, given: str) -> Path:
    """--path relative to the cwd (if that lands inside workspace/) or to workspace/."""
    ws = paths.workspace.resolve()
    here = Path(given).expanduser()
    candidate = here if here.is_absolute() else Path.cwd() / here
    try:
        rel = candidate.resolve().relative_to(ws).as_posix() if candidate.exists() else given
        return resolve_in(ws, rel or ".")
    except (ValueError, SandboxError) as e:
        raise Usage(f"--path must be inside workspace/: {e}") from None


# ── commands ──────────────────────────────────────────────────────────────

def cmd_status(paths: Paths, args: argparse.Namespace) -> int:
    t = tr.load(paths.tracker)
    log = VerificationLog(paths.verifications)
    passing = log.passing_items()
    cur = t.current()
    if cur is None:
        print("All items ticked.")
    else:
        week, task, item = cur
        print(f"current: [{item.id}] {item.text}")
        if task:
            print(f"task:    {task.id} {task.title}" + (f" [{task.kind}]" if task.kind else ""))
            try:
                folder = task_folder(paths, task.id)
            except FolderError as e:
                folder, note = None, str(e)
            else:
                note = f"(none yet: create workspace/week{week.n}/t{task.id}-<slug>/)" if week else ""
            print(f"folder:  {folder.relative_to(paths.root).as_posix() if folder else note}")
        print(f"verify:  {verify_kind(item.text)}"
              + ("  (passing record exists: ready for /checkoff)" if item.id in passing else ""))
        if week:
            print(f"\nweek {week.n}: {week.title}, {sum(i.checked for i in week.items)}/"
                  f"{len(week.items)} ticked")
            if week.focus:
                print(f"focus:    {week.focus}")
            if week.pitfalls:
                print(f"pitfalls: {week.pitfalls}")
        if task:
            print(f"\ntask {task.id} items (box, id, how it's verified):")
            for i in task.items:
                mark = "x" if i.checked else ("v" if i.id in passing else " ")
                print(f"  [{mark}] {i.id:7} {verify_kind(i.text):8} {i.text}")
            print("  ([v] = passing record, not ticked yet)")
    records = log.read()[-args.recent:]
    if records:
        print("\nrecent verifications (newest last):")
        for r in records:
            print(f"  {'PASS' if r.passed else 'FAIL'}  {r.item:8} {r.kind:8} {r.at}  {r.summary}")
    return 0


def cmd_verify(paths: Paths, args: argparse.Namespace) -> int:
    t = tr.load(paths.tracker)
    target = args.target.removeprefix("T")
    if ITEM_RE.match(target):
        items, task_id = [target], task_of(target)
    else:
        task_id = target.removeprefix("W")
        _, task = find_task(t, task_id)
        items = [i.id for i in task.items if verify_kind(i.text) == "pytest"]
        if not items:
            raise Refused(f"task {task_id} has no pytest-verified items; "
                          "use `record --kind tutor|artifact` or a quiz instead")
    for item in items:
        try:
            check_item_for_pytest(paths, item)
        except RunRefused as e:
            raise Refused(str(e)) from None

    if args.path:
        folder = workspace_path(paths, args.path)
    else:
        try:
            folder = task_folder(paths, task_id)
        except FolderError as e:
            raise Usage(f"{e}; pass --path") from None
        if folder is None:
            raise Usage(f"no folder for task {task_id}: expected "
                        f"workspace/week{task_id.split('.')[0]}/t{task_id}-<slug>/, or pass --path")
    rel = folder.relative_to(paths.workspace.resolve()).as_posix() or "."

    async def run() -> dict:
        result: dict = {}
        async for e in run_pytest(paths, rel, items, by=BY):
            if e["type"] == "output":
                sys.stdout.write(e["data"])
                sys.stdout.flush()
            elif e["type"] == "start":
                print(f"$ pytest in workspace/{e['cwd']}  (records for {', '.join(items)})", flush=True)
            elif e["type"] == "result":
                result = e
        return result

    result = asyncio.run(run())
    verdict = "PASS" if result["passed"] else "FAIL"
    print(f"\nRESULT: {verdict}  {result['summary']}")
    for r in result["records"]:
        print(f"recorded: {r['item']} pytest {'pass' if r['passed'] else 'fail'}")
    if result["passed"]:
        print(f"next: /checkoff {' '.join(items)}")
    return 0 if result["passed"] else 1


def artifact_check(paths: Paths, item: tr.Item) -> str:
    """Summary for an artifact record, or Refused if the file isn't there."""
    name = next((n for n in DOCS.values() if f"`{n}`" in item.text), None)
    if name is None:
        raise Refused(f"{item.id} names no implementation_plan.md or walkthrough.md")
    task_id = task_of(item.id)
    try:
        folder = task_folder(paths, task_id)
    except FolderError as e:
        raise Refused(str(e)) from None
    if folder is None:
        raise Refused(f"no folder for task {task_id} (workspace/week{task_id.split('.')[0]}/t{task_id}-<slug>/)")
    doc = folder / name
    if not doc.is_file():
        raise Refused(f"{doc.relative_to(paths.root).as_posix()} does not exist")
    text = doc.read_text(encoding="utf-8")
    if len("".join(text.split())) < MIN_DOC_CHARS:
        raise Refused(f"{doc.relative_to(paths.root).as_posix()} is a stub "
                      f"(under {MIN_DOC_CHARS} non-space characters)")
    return f"{doc.relative_to(paths.workspace).as_posix()} ({len(text.splitlines())} lines)"


def cmd_record(paths: Paths, args: argparse.Namespace) -> int:
    t = tr.load(paths.tracker)
    try:
        item = t.item(args.item)
    except KeyError:
        raise Usage(f"no item {args.item} in the tracker") from None
    expected = verify_kind(item.text)
    if args.kind != expected:
        how = {"pytest": "/verify (a pytest run)", "quiz": "the learner taking the quiz"}
        raise Refused(f"{item.id} is verified by {how.get(expected, expected)}, "
                      f"not a {args.kind} record")
    if not t.item_unlocked(item.id):
        raise Refused(f"{item.id} is in a locked week")
    if args.kind == "artifact":
        summary = artifact_check(paths, item) if not args.fail else ""
        summary = "; ".join(s for s in (summary, args.summary) if s)
    else:
        if not args.summary:
            raise Usage("a tutor record needs --summary saying what you checked")
        summary = args.summary
    rec = VerificationLog(paths.verifications).append(Record(
        item=item.id, kind=args.kind, passed=not args.fail, summary=summary, by=BY))
    print(f"recorded: {rec.item} {rec.kind} {'pass' if rec.passed else 'fail'}  {rec.summary}")
    return 0


def cmd_checkoff(paths: Paths, args: argparse.Namespace) -> int:
    failures = 0
    for item_id in args.items:
        try:
            check_item(paths, item_id, checked=not args.undo)
        except KeyError as e:
            print(f"refused: {e.args[0]}")
            failures += 1
        except CheckRefused as e:
            print(f"refused: {e}")
            failures += 1
        else:
            print(f"{'unticked' if args.undo else 'ticked'}: {item_id}")
    return 1 if failures else 0


def cmd_quiz_check(paths: Paths, args: argparse.Namespace) -> int:
    path = Path(args.file)
    try:
        quiz = quizzes.Quiz.model_validate_json(path.read_text(encoding="utf-8"))
    except OSError as e:
        raise Usage(str(e)) from None
    except ValidationError as e:
        for err in e.errors():
            print(f"invalid: {'.'.join(map(str, err['loc'])) or 'spec'}: {err['msg']}")
        return 1
    try:
        item = quizzes.item_for(quiz, tr.load(paths.tracker))
    except quizzes.QuizError as e:
        print(f"invalid: {e}")
        return 1
    print(f"ok: {quiz.id} '{quiz.title}', {len(quiz.questions)} questions, "
          f"pass mark {quiz.pass_mark}, "
          + (f"verifies {item.id}" if item else "practice (records no verification)"))
    return 0


def cmd_scaffold(paths: Paths, args: argparse.Namespace) -> int:
    task_id = args.task.removeprefix("W")
    t = tr.load(paths.tracker)
    week, _ = find_task(t, task_id)
    if not t.week_unlocked(week.n):
        raise Refused(f"week {week.n} is locked")
    try:
        dest, copied, skipped = lessons.scaffold(paths, task_id)
    except FileNotFoundError as e:
        raise Refused(f"{e}: write the starter tests yourself (tests first)") from None
    except FolderError as e:
        raise Refused(str(e)) from None
    rel = dest.relative_to(paths.workspace).as_posix()
    print(f"folder: {rel}/")
    for f in copied:
        print(f"  copied  {f}")
    for f in skipped:
        print(f"  kept    {f} (already exists; not overwritten)")
    print("Read the copied files before teaching from them: the tests are the spec.")
    return 0


def cmd_lesson_add(paths: Paths, args: argparse.Namespace) -> int:
    task_id = args.task.removeprefix("W")
    t = tr.load(paths.tracker)
    week, task = find_task(t, task_id)
    if not t.week_unlocked(week.n):
        raise Refused(f"week {week.n} is locked; write its lessons when it opens")
    try:
        text = Path(args.file).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        raise Usage(str(e)) from None
    if not text.lstrip().startswith("# "):
        print("invalid: a lesson starts with a `# Title` heading")
        return 1
    dest = lessons.lesson_path(paths, task_id)
    existed = dest.exists()
    dest.parent.mkdir(parents=True, exist_ok=True)
    tr.write_atomic(dest, text if text.endswith("\n") else text + "\n")
    print(f"{'replaced' if existed else 'installed'}: {dest.relative_to(paths.root).as_posix()} "
          f"(task {task.id}: {task.title})")
    return 0


def cmd_quiz_add(paths: Paths, args: argparse.Namespace) -> int:
    """Validate a draft written inside workspace/ and install it as
    curriculum/weekN/quiz_N_M.json, replacing any earlier version."""
    src = Path(args.file)
    try:
        quiz = quizzes.Quiz.model_validate_json(src.read_text(encoding="utf-8"))
    except OSError as e:
        raise Usage(str(e)) from None
    except ValidationError as e:
        for err in e.errors():
            print(f"invalid: {'.'.join(map(str, err['loc'])) or 'spec'}: {err['msg']}")
        return 1
    week, n = quiz.task_id.split(".")
    dest = paths.curriculum / f"week{week}" / f"quiz_{week}_{n}.json"
    for other in paths.curriculum.glob("week*/quiz_*.json"):
        try:
            other_id = json.loads(other.read_text(encoding="utf-8")).get("id")
        except (OSError, ValueError, AttributeError):
            continue
        if other != dest and other_id == quiz.id:
            print(f"invalid: {quiz.id} is already defined in {other.relative_to(paths.root)}")
            return 1
    try:
        item = quizzes.item_for(quiz, tr.load(paths.tracker))
    except quizzes.QuizError as e:
        print(f"invalid: {e}")
        return 1
    dest.parent.mkdir(parents=True, exist_ok=True)
    tr.write_atomic(dest, json.dumps(quiz.model_dump(exclude_none=True), indent=2,
                                     ensure_ascii=False) + "\n")
    print(f"installed: {dest.relative_to(paths.root).as_posix()} ({quiz.id}, "
          + (f"verifies {item.id})" if item else "practice)"))
    print(f"learner: quiz view in the cockpit (g q), or `epochzero-quiz {quiz.id}` in its terminal")
    return 0


def cmd_quiz_results(paths: Paths, args: argparse.Namespace) -> int:
    try:
        quiz = quizzes.get(paths, args.quiz_id)
    except KeyError as e:
        raise Usage(e.args[0]) from None
    try:
        doc = json.loads((paths.quiz_results / f"{quiz.id}.json").read_text(encoding="utf-8"))
        attempts = doc["attempts"]
    except (OSError, ValueError, KeyError):
        attempts = []
    if not attempts:
        print(f"{quiz.id}: no attempts yet")
        return 0
    last = attempts[-1]
    print(f"{quiz.id}: {len(attempts)} attempt(s); latest {last['score']}/{last['total']} "
          f"({'PASS' if last['passed'] else 'FAIL'}, pass mark {last['pass_mark']}) "
          f"via {last['by']} at {last['at']}")
    by_id = {q.id: q for q in quiz.questions}
    missed = [a for a in last["answers"] if not a["correct"] and a["q"] in by_id]
    for a in missed:
        q = by_id[a["q"]]
        chose = q.choices[a["choice"]] if 0 <= a["choice"] < len(q.choices) else a["choice"]
        print(f"\nmissed {q.id}: {q.prompt}\n  learner chose: {chose}\n"
              f"  correct:       {q.choices[q.answer]}\n  explain:       {q.explain}")
    if not missed:
        print("no missed questions")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="epochzero-tutor", description=__doc__.split("\n\n")[0])
    parser.add_argument("--root", type=Path,
                        default=Path(os.environ.get("EPOCHZERO_ROOT") or ROOT),
                        help="dir holding CURRICULUM_TRACKER.md (default: $EPOCHZERO_ROOT or the app's)")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("status", help="current item, task folder, recent verifications")
    p.add_argument("--recent", type=int, default=5)
    p.set_defaults(fn=cmd_status)

    p = sub.add_parser("scaffold", help="copy a task's starter files and tests into its folder")
    p.add_argument("task")
    p.set_defaults(fn=cmd_scaffold)

    p = sub.add_parser("verify", help="run pytest for a task (W1.3) or item (W1.3.c) and record it")
    p.add_argument("target")
    p.add_argument("--path", help="test folder or file in workspace/ (default: the task folder)")
    p.set_defaults(fn=cmd_verify)

    p = sub.add_parser("record", help="record a tutor or artifact check")
    p.add_argument("item")
    p.add_argument("--kind", choices=["tutor", "artifact"], required=True)
    p.add_argument("--summary", default="")
    p.add_argument("--fail", action="store_true", help="record a failed check")
    p.set_defaults(fn=cmd_record)

    p = sub.add_parser("checkoff", help="tick items (refused without a passing record)")
    p.add_argument("items", nargs="+")
    p.add_argument("--undo", action="store_true", help="untick instead")
    p.set_defaults(fn=cmd_checkoff)

    p = sub.add_parser("quiz-check", help="validate a quiz spec file")
    p.add_argument("file")
    p.set_defaults(fn=cmd_quiz_check)

    p = sub.add_parser("quiz-add", help="validate a draft spec and install it into curriculum/")
    p.add_argument("file")
    p.set_defaults(fn=cmd_quiz_add)

    p = sub.add_parser("lesson-add", help="install a lesson for a task into curriculum/")
    p.add_argument("task")
    p.add_argument("file")
    p.set_defaults(fn=cmd_lesson_add)

    p = sub.add_parser("quiz-results", help="latest attempt, with answers to missed questions")
    p.add_argument("quiz_id")
    p.set_defaults(fn=cmd_quiz_results)

    args = parser.parse_args(argv)
    paths = Paths(args.root.resolve())
    try:
        return args.fn(paths, args)
    except Usage as e:
        print(f"epochzero-tutor: {e}", file=sys.stderr)
        return 2
    except Refused as e:
        print(f"refused: {e}")
        return 1
    except (tr.TrackerError, FileNotFoundError) as e:
        print(f"epochzero-tutor: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
