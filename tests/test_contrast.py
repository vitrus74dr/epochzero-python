"""Every text colour must meet WCAG AA (4.5:1) on every surface it can sit on."""

import re
from pathlib import Path

import pytest

TOKENS = Path(__file__).resolve().parent.parent / "web/src/theme/tokens.css"

FOREGROUNDS = ["text", "text-muted", "accent", "accent-2", "success", "danger", "info", "magenta"]
SURFACES = ["bg", "surface", "surface-2"]
AA = 4.5


def parse_themes() -> dict[str, dict[str, str]]:
    css = TOKENS.read_text(encoding="utf-8")
    themes = {}
    for selector, body in re.findall(r"([^{}]+)\{([^}]*)\}", css):
        m = re.search(r'data-theme="(\w+)"', selector)
        if m:
            themes[m.group(1)] = dict(re.findall(r"--([\w-]+):\s*(#[0-9A-Fa-f]{6})", body))
    return themes


def luminance(hex_colour: str) -> float:
    def channel(c: float) -> float:
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = (channel(int(hex_colour[i:i + 2], 16) / 255) for i in (1, 3, 5))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a: str, b: str) -> float:
    hi, lo = sorted((luminance(a), luminance(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


THEMES = parse_themes()
PAIRS = [(t, fg, bg) for t in ("dark", "light") for fg in FOREGROUNDS for bg in SURFACES]
PAIRS += [(t, "text", "selection") for t in ("dark", "light")]


def test_both_themes_define_every_token():
    expected = set(FOREGROUNDS + SURFACES + ["border", "grid", "selection"])
    for name in ("dark", "light"):
        assert expected <= THEMES[name].keys(), f"{name} theme missing tokens"


@pytest.mark.parametrize("theme,fg,bg", PAIRS, ids=lambda x: str(x))
def test_contrast_meets_aa(theme, fg, bg):
    t = THEMES[theme]
    ratio = contrast(t[fg], t[bg])
    assert ratio >= AA, f"{theme}: --{fg} on --{bg} is {ratio:.2f}:1"
