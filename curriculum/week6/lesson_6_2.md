# The Platformer Physics Engine

Gravity, jumping, landing on platforms, bumping into walls: doing that by hand is
fiddly. Arcade includes a physics engine that does it for you. This lesson also fixes a
subtle problem: physics that behaves differently at different frame rates.

## 1. Which engine?

| Engine | Use it for |
|---|---|
| `arcade.PhysicsEngineSimple` | **top-down** games (Zelda, Pac-Man): walls block you, there's no gravity |
| `arcade.PhysicsEnginePlatformer` | **side-on** games (Mario): gravity, jumping, platforms, ladders |

Older tutorials sometimes use `PhysicsEngineSimple` for platformers and then wonder why
nothing falls. It has no gravity at all.

## 2. Setting it up

```python
import arcade

GRAVITY = 1.0          # pixels per step, per step
JUMP_SPEED = 20
MOVE_SPEED = 6
TILE = 64


class Game(arcade.Window):
    def __init__(self):
        super().__init__(1024, 640, "Platformer physics")
        self.background_color = arcade.color.CORNFLOWER_BLUE
        self.players = arcade.SpriteList()
        self.player = arcade.Sprite(
            ":resources:images/animated_characters/female_adventurer/femaleAdventurer_idle.png",
            scale=0.5, center_x=128, center_y=256)
        self.players.append(self.player)

        self.walls = arcade.SpriteList(use_spatial_hash=True)
        for x in range(0, 1024 + TILE, TILE):                    # the floor
            self.walls.append(arcade.Sprite(":resources:images/tiles/grassMid.png",
                                            scale=0.5, center_x=x, center_y=32))
        for x in range(384, 640, TILE):                          # a floating platform
            self.walls.append(arcade.Sprite(":resources:images/tiles/grassMid.png",
                                            scale=0.5, center_x=x, center_y=224))

        self.physics = arcade.PhysicsEnginePlatformer(
            self.player, walls=self.walls, gravity_constant=GRAVITY)

    def on_key_press(self, key, modifiers):
        if key in (arcade.key.UP, arcade.key.SPACE) and self.physics.can_jump():
            self.player.change_y = JUMP_SPEED
        elif key == arcade.key.LEFT:
            self.player.change_x = -MOVE_SPEED
        elif key == arcade.key.RIGHT:
            self.player.change_x = MOVE_SPEED

    def on_key_release(self, key, modifiers):
        if key in (arcade.key.LEFT, arcade.key.RIGHT):
            self.player.change_x = 0

    def on_fixed_update(self, delta_time):
        self.physics.update()

    def on_draw(self):
        self.clear()
        self.walls.draw()
        self.players.draw()


if __name__ == "__main__":
    Game()
    arcade.run()
```

- `walls=` holds everything solid. `use_spatial_hash=True` makes collision checks fast
  for sprites that never move, like walls.
- `can_jump()` is true only when the player stands on something, so there's no jumping in mid-air.
- To jump, set `change_y` upward; gravity pulls it back down every step.

## 3. Why `on_fixed_update`?

`physics.update()` takes no `delta_time`: each call moves the player by `change_x` and
applies `gravity_constant` **once**. Called from `on_update` (once per frame), the game
would run 2.4× faster on a 144 Hz monitor than on a 60 Hz one. Jumps would reach the same
height, but in less time.

Arcade 3's answer is **`on_fixed_update`**. Arcade calls it exactly 60 times per
second (by default), whatever the frame rate: on a fast monitor some frames run it zero
times, on a slow computer some frames run it twice. Physics steps belong there. So
`MOVE_SPEED = 6` means 6 pixels per *step*, 360 pixels per second, everywhere.

The rule from now on:

| Method | What goes in it |
|---|---|
| `on_fixed_update(delta_time)` | physics engines, and anything counted in steps |
| `on_update(delta_time)` | movement you scale yourself with `* delta_time`, animations, timers |
| `on_draw()` | drawing only |

## 4. A camera that follows

When a level is wider than the window, move a **camera** instead of the world:

```python fragment
# in __init__
self.camera = arcade.Camera2D()

# in on_fixed_update, after physics.update()
self.camera.position = (max(self.player.center_x, self.width / 2), self.height / 2)

# in on_draw
self.clear()
with self.camera.activate():
    self.walls.draw()
    self.players.draw()
# draw the score here, outside the camera, so it stays fixed on screen
```

## 5. Your turn (W6.2.a)

`week6/t6.2-physics/physics.py`: a level about three screens wide with platforms at
different heights, a gap you must jump, a following camera, and a fixed score label.
Then tune `GRAVITY` and `JUMP_SPEED` until jumping *feels* right, and tell the tutor what
each change did.

## Pitfalls

- `PhysicsEngineSimple` for a platformer (no gravity).
- `physics.update()` in `on_update`, making the game speed depend on the frame rate.
- Forgetting `can_jump()`, which allows infinite mid-air jumps.
- Drawing the score inside the camera block, so it scrolls away.
