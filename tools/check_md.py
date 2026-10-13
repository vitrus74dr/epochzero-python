"""Run the Python snippets in lesson markdown files.

    tools/learner_env.sh                       # once: the learner's libraries
    uv run --project .learner-env python tools/check_md.py curriculum/week*/lesson_*.md
    ARCADE_HEADLESS=1 ... (as above)           # also run whole Arcade programs offscreen

- ```python blocks run in one namespace per lesson (later blocks may use
  earlier names), with cwd set to a temp dir.
- Blocks that need a human or a window (input(), inquirer, mainloop,
  plt.show(), uvicorn.run, network calls) or contain `...` placeholders are
  only compiled. Fences marked ```python fragment are skipped entirely.
- With ARCADE_HEADLESS=1, a block calling arcade.run() is run headless for
  30 frames (a key held from frame 5) and screenshotted to tools/.out/.
- `>>>` REPL blocks: each statement's output is compared with the expected
  lines; an expected "SomeError: message" line must match the raised
  exception (module-qualified names like json.decoder.JSONDecodeError are fine).
Exit status 1 if anything fails.
"""

import contextlib
import io
import os
import re
import sys
import tempfile
import traceback

INTERACTIVE = re.compile(r"input\(|inquirer\.|\.mainloop\(|plt\.show\(|uvicorn\.run\(|"
                         r"requests\.(get|post)\(|time\.sleep\(|^\s*\.\.\.\s*$|# compile-only", re.M)
BLOCK = re.compile(r"```(\w*)([^\n]*)\n(.*?)```", re.S)


def run_repl(code: str, ns: dict) -> list[str]:
    problems = []
    lines = code.splitlines()
    i = 0
    while i < len(lines):
        if not lines[i].startswith(">>> "):
            i += 1
            continue
        stmt = [lines[i][4:]]
        i += 1
        while i < len(lines) and lines[i].startswith("... "):
            stmt.append(lines[i][4:])
            i += 1
        expected = []
        while i < len(lines) and not lines[i].startswith(">>> "):
            expected.append(lines[i])
            i += 1
        src = "\n".join(stmt)
        expected = [e for e in expected if e.strip()]
        buf = io.StringIO()
        got: list[str]
        try:
            with contextlib.redirect_stdout(buf):
                try:
                    val = eval(compile(src, "<repl>", "eval"), ns)
                    if val is not None:
                        print(repr(val))
                except SyntaxError:
                    exec(compile(src, "<repl>", "exec"), ns)
            got = buf.getvalue().splitlines()
        except Exception as e:
            got = buf.getvalue().splitlines() + [f"{type(e).__name__}: {e}"]
        exp = [re.sub(r"^(?:[a-z_]\w*\.)+(\w+(?:Error|Exception|Warning)): ", r"\1: ", e)
               for e in expected if not e.startswith("Traceback")]
        if [g.rstrip() for g in got] != [e.rstrip() for e in exp]:
            problems.append(f"  >>> {src}\n      expected {exp}\n      got      {got}")
    return problems


SHOTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".out")


def run_arcade(code: str, shot: str, frames: int = 30) -> None:
    """Run a whole Arcade program headless: arcade.run() steps the window
    `frames` times (update, fixed update, draw) with an arrow key held, then
    saves a screenshot and closes the window."""
    import arcade
    os.makedirs(SHOTS, exist_ok=True)

    def fake_run(*a, **k):
        w = arcade.get_window()
        for i in range(frames):
            if i == 5:
                w.on_key_press(arcade.key.RIGHT, 0)
            w.on_update(1 / 60)
            if hasattr(w, "on_fixed_update"):
                w.on_fixed_update(1 / 60)
            w.on_draw()
        w.on_key_release(arcade.key.RIGHT, 0)
        arcade.get_image().save(shot)
        arcade.close_window()

    real = arcade.run
    arcade.run = fake_run
    try:
        exec(compile(code, "arcade-block", "exec"), {"__name__": "__main__"})
    finally:
        arcade.run = real


def check(path: str) -> int:
    text = open(path, encoding="utf-8").read()
    ns: dict = {"__name__": "lesson"}
    failures = 0
    with tempfile.TemporaryDirectory() as tmp:
        old = os.getcwd()
        os.chdir(tmp)
        try:
            for n, (lang, info, code) in enumerate(BLOCK.findall(text), 1):
                if "fragment" in info:
                    continue
                if lang not in ("python", "py", ""):
                    continue
                if lang == "" and ">>>" not in code:
                    continue
                if code.lstrip().startswith(">>>"):
                    probs = run_repl(code, ns)
                    if probs:
                        failures += 1
                        print(f"{path} block {n} (repl):\n" + "\n".join(probs))
                    continue
                try:
                    compiled = compile(code, f"block{n}", "exec")
                except SyntaxError as e:
                    failures += 1
                    print(f"{path} block {n}: SyntaxError {e}")
                    continue
                if "arcade.run()" in code and os.environ.get("ARCADE_HEADLESS"):
                    shot = os.path.join(SHOTS, f"{os.path.basename(path)[:-3]}_b{n}.png")
                    try:
                        run_arcade(code, shot)
                    except Exception:
                        failures += 1
                        print(f"{path} block {n}: arcade program raised\n{traceback.format_exc(limit=3)}")
                    continue
                if INTERACTIVE.search(code) or "arcade.run()" in code:
                    continue
                try:
                    with contextlib.redirect_stdout(io.StringIO()):
                        exec(compiled, ns)
                except Exception:
                    failures += 1
                    print(f"{path} block {n}: raised\n{traceback.format_exc(limit=2)}")
        finally:
            os.chdir(old)
    print(f"{path}: {'OK' if not failures else f'{failures} problem(s)'}")
    return failures


if __name__ == "__main__":
    sys.exit(1 if sum(check(p) for p in sys.argv[1:]) else 0)
