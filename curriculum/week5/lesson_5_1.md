# Arcade: Your First Window

Weeks 5–12 are about graphics and games, built with **Arcade**, a modern Python game
library. This first lesson is about the shape of every game program: a window, and a
loop that draws and updates many times a second.

```sh
uv add arcade
uv run python -c "import arcade; print(arcade.__version__)"
```

> This course uses **Arcade 3**. Arcade 2.6 tutorials (2022 and earlier) are still all
> over the web, and much of their code no longer runs: `start_render()`,
> `draw_rectangle_filled()` and `arcade.set_background_color()` belong to the old API.
> When code from the web fails, check which version it was written for, and ask the
> tutor to check the current docs.

## 1. The smallest game

```python
import arcade

WIDTH, HEIGHT = 800, 600


class Game(arcade.Window):
    def __init__(self):
        super().__init__(WIDTH, HEIGHT, "My first window")
        self.background_color = arcade.color.DARK_SLATE_BLUE

    def on_draw(self):
        self.clear()
        arcade.draw_circle_filled(400, 300, 50, arcade.color.ORANGE)


def main():
    Game()
    arcade.run()


if __name__ == "__main__":
    main()
```

Run it with **Ctrl/Cmd+Enter**: a window opens on your desktop. Close it to end the program.

- `class Game(arcade.Window)` is inheritance from Week 3: your game *is a* window.
  `super().__init__(...)` sets up the window itself.
- `arcade.run()` starts the **game loop**. From then on, Arcade calls your methods:
  `on_draw` about 60 times a second, plus methods like `on_key_press` when things happen.
  It's the same event-driven style as Tkinter (Lesson 3.4).
- `on_draw` must start with `self.clear()`, which paints the background. Without it,
  every frame is drawn on top of the last one.

## 2. Coordinates: the origin is bottom-left

In Arcade, `(0, 0)` is the **bottom-left** corner, and *y grows upward*, like a
maths graph. Many other libraries (and screens) put `(0, 0)` at the top left; this is
the week's first pitfall.

```text
(0, 600) ┌──────────────┐ (800, 600)
         │              │
         │   (400, 300) │
         │       ●      │
(0, 0)   └──────────────┘ (800, 0)
```

So the circle above sits at the centre, and `y = 550` would be near the **top**.

## 3. Drawing primitives

Everything is drawn inside `on_draw`, after `self.clear()`, in order: later shapes
cover earlier ones.

```python fragment
def on_draw(self):
    self.clear()
    # sky, from left/right/bottom/top edges
    arcade.draw_lrbt_rectangle_filled(0, WIDTH, 200, HEIGHT, arcade.color.SKY_BLUE)
    # ground, as centre x, centre y, width, height
    arcade.draw_rect_filled(arcade.XYWH(400, 100, 800, 200), arcade.color.DARK_GREEN)
    arcade.draw_circle_filled(650, 500, 40, arcade.color.YELLOW)            # sun
    arcade.draw_triangle_filled(300, 200, 400, 320, 500, 200, arcade.color.GRAY)
    arcade.draw_line(0, 200, 800, 200, arcade.color.BLACK, 2)
```

Colours are `arcade.color.SOMETHING` or plain `(r, g, b)` tuples (each 0–255), with an
optional fourth value for transparency: `(255, 0, 0, 128)` is half-transparent red.

Rectangles come in two flavours: by edges (`draw_lrbt_rectangle_filled`) or from a
**rect** object: `arcade.XYWH(center_x, center_y, width, height)`, or
`arcade.LBWH(left, bottom, width, height)`.

## 4. Your turn (W5.1.a)

In `week5/t5.1-window/scene.py`, draw a landscape: sky, ground, a sun, a house with a
door and two windows, and a tree. Use at least four kinds of primitive.

Then answer the tutor's coordinate question: where would `(20, 580)` appear, and why?

## Pitfalls

- Forgetting `self.clear()` at the start of `on_draw`.
- Thinking `y = 0` is the top.
- Code from Arcade 2 tutorials (`start_render`, `draw_rectangle_filled`).
- Doing work (movement, counting) in `on_draw`. That belongs in `on_update`, next lesson.
