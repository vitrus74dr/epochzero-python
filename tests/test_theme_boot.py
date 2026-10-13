"""The no-flash script in index.html must agree with theme.ts."""

import re
from pathlib import Path

WEB = Path(__file__).resolve().parent.parent / "web"


def test_no_flash_script_runs_before_app():
    html = (WEB / "index.html").read_text(encoding="utf-8")
    head = html.split("</head>")[0]
    assert "setAttribute('data-theme'" in head
    assert "prefers-color-scheme" in head
    assert html.index("data-theme") < html.index('src="/src/main.tsx"')


def test_storage_key_matches():
    html = (WEB / "index.html").read_text(encoding="utf-8")
    ts = (WEB / "src/theme/theme.ts").read_text(encoding="utf-8")
    key = re.search(r"STORAGE_KEY = '([^']+)'", ts).group(1)
    assert f"localStorage.getItem('{key}')" in html
