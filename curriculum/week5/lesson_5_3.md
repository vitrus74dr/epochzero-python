# Animated Generative Art

Art made by maths: curves that draw themselves, colours that cycle, shapes that breathe.
This project practises the maths you'll need for every game from here on (angles,
sine and cosine, interpolation), and keeps it **pure and testable**, separate from Arcade.

## 1. Angles and the unit circle

A point at angle `θ` (theta) on a circle of radius `r`, centred at `(cx, cy)`:

```python
import math

def on_circle(cx, cy, r, theta):
    return cx + r * math.cos(theta), cy + r * math.sin(theta)

on_circle(0, 0, 1, 0)              # (1.0, 0.0): angle 0 points right
on_circle(0, 0, 1, math.pi / 2)    # (≈0.0, 1.0): a quarter turn, straight up
```

Python's `math.sin` and `math.cos` use **radians**: a full turn is `2 * math.pi`, not 360.
Convert with `math.radians(90)` and `math.degrees(math.pi)`. Mixing the two up is
a pitfall all through Weeks 5–12.

**Try it:** generate 12 points around a circle (`theta = 2 * math.pi * i / 12`) and draw a
small dot at each one.

## 2. Parametric curves

A **parametric** curve gives `x` and `y` as functions of one parameter `t`. Sweep `t`
and join the dots.

Lissajous figures (an oscilloscope classic):

```python
import math

def lissajous(t, a=3, b=2, delta=math.pi / 2, size=200):
    return size * math.sin(a * t + delta), size * math.sin(b * t)
```

A rose curve, in **polar** form: the radius depends on the angle, `r = cos(k·θ)`:

```python
import math

def rose(theta, k=5, size=250):
    r = size * math.cos(k * theta)
    return r * math.cos(theta), r * math.sin(theta)      # polar → cartesian
```

To draw one, make a list of points and hand it to `arcade.draw_line_strip(points, color, width)`:

```python fragment
points = [rose(2 * math.pi * i / 600) for i in range(601)]
points = [(400 + x, 300 + y) for x, y in points]          # shift to the screen centre
arcade.draw_line_strip(points, arcade.color.PINK, 2)
```

Integer `k` gives `k` petals when it's odd and `2k` when it's even. Try `k = 4`, then
`k = 2.5`.

## 3. Animation: time as a parameter

Make the curve change over time: keep a clock in `on_update`, and use it in the maths.

```python fragment
def on_update(self, delta_time):
    self.t += delta_time                       # seconds since start
    self.k = 3 + 2 * math.sin(self.t * 0.5)    # k drifts between 1 and 5
```

Because the clock adds `delta_time`, the animation runs at the same speed on every
computer (W5.3.b).

## 4. Easing

Straight-line (linear) motion looks mechanical. **Easing** functions bend the
progress `p`, from 0 to 1, so that motion starts and stops gently:

```python
import math

def lerp(a, b, p):
    """Linear interpolation: a when p=0, b when p=1."""
    return a + (b - a) * p

def ease_in_out_sine(p):
    return -(math.cos(math.pi * p) - 1) / 2

lerp(100, 300, 0.5)                        # 200.0
lerp(100, 300, ease_in_out_sine(0.25))     # ≈129.3: still slow near the start
```

## 5. Colour from numbers

HSV (hue, saturation, value) is easier to animate than RGB: sweep the hue for a rainbow.

```python
import colorsys

def hue_to_rgb(h):
    """h in [0, 1) → an (r, g, b) tuple of ints 0-255."""
    r, g, b = colorsys.hsv_to_rgb(h % 1.0, 0.8, 1.0)
    return round(r * 255), round(g * 255), round(b * 255)

hue_to_rgb(0.0)      # (255, 51, 51): red
hue_to_rgb(1 / 3)    # (51, 255, 51): green
```

## 6. Structure: maths apart from Arcade

```text
week5/t5.3-art/
    art_math.py        pure: curve points, easing, colour mapping. No `import arcade`.
    art.py             the Arcade window: state, keys, drawing
    test_art_math.py   tests without a window
```

The tests for W5.3.c check things you can know for sure: a point on a circle is
exactly `r` from the centre; `lerp` hits both ends; the easing function goes from 0 to 1;
a rose curve's points never lie further than `size` from the centre; colours stay in
0–255. Floats are rarely exactly equal, so use `pytest.approx`:
`assert x == pytest.approx(1.0)`.

At `/grill-me` you'll explain *your* maths: which curves, which parameters animate, and
what the keyboard controls (W5.3.b needs at least one live control, e.g. ↑/↓ changes `k`).

## Pitfalls

- Degrees given to `math.sin`/`math.cos`, which expect radians.
- Rebuilding thousands of points in `on_draw`. Compute them in `on_update`, only when a
  parameter changes.
- Comparing floats with `==` in tests.
- `int()` on a computed float. `colorsys` returns `0.19999999999999996`, not `0.2`, so
  `int(value * 255)` gives 50 instead of 51: `int` chops, it doesn't round. Use `round()`.
- Animation by frame count instead of the `delta_time` clock.
