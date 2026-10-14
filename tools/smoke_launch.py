"""Start `uv run epochzero` the way a student does, load the page with the printed
link, open a session with its token and check the API answers, then stop it.
Used by CI on every OS.

    uv run python tools/smoke_launch.py
"""

import json
import re
import subprocess
import sys
import threading
import time
import urllib.request
from http.cookiejar import CookieJar
from pathlib import Path

PORT = 8799
ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    proc = subprocess.Popen(["uv", "run", "epochzero", "--no-browser", "--port", str(PORT)],
                            cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    lines: list[str] = []
    found = threading.Event()

    def read() -> None:
        assert proc.stdout is not None
        for line in proc.stdout:
            lines.append(line)
            print(line, end="")
            if "?token=" in line:
                found.set()

    threading.Thread(target=read, daemon=True).start()
    try:
        for _ in range(360):  # up to 180 s: the first run may download Python
            if found.wait(0.5):
                break
            if proc.poll() is not None:
                print(f"epochzero exited with {proc.returncode} before printing a link")
                return 1
        else:
            print("no link printed within 180 s")
            return 1
        url = re.search(r"http://\S+", "".join(lines)).group(0)
        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(CookieJar()))
        for _ in range(60):  # the link is printed just before the port starts listening
            try:
                page = opener.open(url, timeout=10).read().decode()
                break
            except OSError:
                time.sleep(0.5)
        else:
            print("the server never answered")
            return 1
        assert "EpochZero Python" in page, "the page didn't load"
        origin = f"http://127.0.0.1:{PORT}"
        token = url.split("token=", 1)[1]
        session = urllib.request.Request(f"{origin}/api/session", method="POST",
                                         data=json.dumps({"token": token}).encode(),
                                         headers={"Content-Type": "application/json", "Origin": origin})
        assert opener.open(session, timeout=10).status == 204
        api = opener.open(urllib.request.Request(f"{origin}/api/tracker", headers={"Origin": origin}),
                          timeout=10)
        assert api.status == 200 and "weeks" in json.loads(api.read()), "the API didn't answer"
        print("smoke test passed")
        return 0
    finally:
        proc.terminate()
        try:
            proc.wait(10)
        except subprocess.TimeoutExpired:
            proc.kill()


if __name__ == "__main__":
    sys.exit(main())
