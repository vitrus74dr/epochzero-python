# Drawing & Movement

A picture becomes a game when things move and respond to the keyboard. This lesson
adds the other half of the game loop, `on_update`, and the idea that makes movement
smooth on every computer: **`delta_time`**.

## 1. `on_update` and `delta_time`

```python
import arcade


class Game(arcade.Window):
    def __init__(self):
        super().__init__(800, 600, "Moving")
        self.x = 100
        self.speed = 200            # pixels per SECOND, not per frame

    def on_update(self, delta_time):
        self.x += self.speed * delta_time
        if self.x > 800:
            self.x = 0

    def on_draw(self):
        self.clear()
        arcade.draw_circle_filled(self.x, 300, 20, arcade.color.ORANGE)


if __name__ == "__main__":
    Game()
    arcade.run()
```

Arcade calls `on_update(delta_time)` every frame. `delta_time` is how many seconds
passed since the last frame: about `0.0167` at 60 frames per second.

Why multiply by it? Write `self.x += 3` and the ball moves 3 pixels *per frame*: 180
pixels a second on a 60 Hz screen, but 432 on a 144 Hz gaming monitor. The same game
runs at different speeds on different computers. `speed * delta_time` makes the speed
"200 pixels per **second**" everywhere. This is **frame-rate independence**, and it's
the rule in every game you'll build.

Keep the jobs separate: `on_update` changes the state (positions, scores, timers);
`on_draw` only shows it.

## 2. Keyboard control

`on_key_press` fires once when a key goes down, `on_key_release` once when it comes up.
To move *while a key is held*, record which keys are down, and move in `on_update`:

```python
import arcade

SPEED = 300


class Game(arcade.Window):
    def __init__(self):
        super().__init__(800, 600, "Keys")
        self.x, self.y = 400, 300
        self.held = set()

    def on_key_press(self, key, modifiers):
        self.held.add(key)
        if key == arcade.key.ESCAPE:
            self.close()

    def on_key_release(self, key, modifiers):
        self.held.discard(key)

    def on_update(self, delta_time):
        dx = (arcade.key.RIGHT in self.held) - (arcade.key.LEFT in self.held)
        dy = (arcade.key.UP in self.held) - (arcade.key.DOWN in self.held)
        self.x += dx * SPEED * delta_time
        self.y += dy * SPEED * delta_time
        self.x = max(20, min(self.x, 780))      # keep it on screen
        self.y = max(20, min(self.y, 580))

    def on_draw(self):
        self.clear()
        arcade.draw_circle_filled(self.x, self.y, 20, arcade.color.YELLOW)


if __name__ == "__main__":
    Game()
    arcade.run()
```

`(RIGHT held) - (LEFT held)` uses the fact that `True` is 1 and `False` is 0: the result
is 1, -1, or 0 when both or neither are held. A neat trick, and it handles both keys at once.

## 3. Images: textures

Arcade ships with free game art, under paths starting `:resources:`:

```python fragment
class Game(arcade.Window):
    def __init__(self):
        super().__init__(800, 600, "Ship")
        self.ship = arcade.load_texture(":resources:images/space_shooter/playerShip1_orange.png")

    def on_draw(self):
        self.clear()
        arcade.draw_texture_rect(self.ship, arcade.XYWH(400, 300, 99, 75))
```

Load textures **once**, in `__init__`, never in `on_draw`: loading reads a file from
disk, and doing that 60 times a second wastes a lot of time. For your own images,
`arcade.load_texture(Path(__file__).parent / "ship.png")` (Lesson 4.1, section 3). From
Week 6 on, sprites will manage textures for you.

## 4. Text

```python fragment
self.score_text = arcade.Text("Score: 0", 10, 570, arcade.color.WHITE, 16)   # in __init__
self.score_text.text = f"Score: {self.score}"                                # when it changes
self.score_text.draw()                                                       # in on_draw
```

`arcade.draw_text(...)` also exists, but it rebuilds the text every frame. An
`arcade.Text` object is built once, which is much faster.

## 5. Your turn

**W5.2.a (tutor check):** add to your scene from 5.1: a texture from `:resources:`, and an
`arcade.Text` label.

**W5.2.b (tutor check):** `week5/t5.2-move/move.py`: a ship (texture) you fly with the
arrow keys or WASD, frame-rate independent, kept on screen, with `Esc` to quit. Then
double the speed constant and explain to the tutor why the ship goes exactly twice as fast
on *any* computer.

## Pitfalls

- Moving by a fixed amount per frame instead of `speed * delta_time`.
- Changing state in `on_draw`, or drawing in `on_update`.
- Loading textures inside `on_draw`.
- Moving in `on_key_press`: you get one step per keypress, not smooth motion.
