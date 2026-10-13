# Sprites and SpriteLists

Drawing every shape by hand stops scaling at about ten objects. A real game has
hundreds: coins, walls, bullets, enemies. Arcade's answer is the **sprite**, an object
with an image, a position and a velocity, and the **SpriteList**, which draws thousands
of them in one fast batch and answers "what is touching what?".

## 1. A sprite

```python fragment
player = arcade.Sprite(
    ":resources:images/animated_characters/female_adventurer/femaleAdventurer_idle.png",
    scale=0.5,
    center_x=200,
    center_y=150,
)
```

A sprite knows its position (`center_x`, `center_y`), its edges (`left`, `right`,
`top`, `bottom`), its `angle` in degrees, and a velocity (`change_x`, `change_y`).
Setting an edge moves the sprite: `player.left = 0` puts it against the left side of the screen.

For prototypes without art, `arcade.SpriteSolidColor(width, height, color=...)` and
`arcade.SpriteCircle(radius, color)` make plain shapes. Every classic game in Weeks 9–12
can start that way.

## 2. SpriteLists

```python
import random

import arcade


class Game(arcade.Window):
    def __init__(self):
        super().__init__(800, 600, "Coins")
        self.background_color = arcade.color.DARK_MIDNIGHT_BLUE
        self.player_list = arcade.SpriteList()
        self.coins = arcade.SpriteList()
        self.player = arcade.Sprite(
            ":resources:images/animated_characters/female_adventurer/femaleAdventurer_idle.png",
            scale=0.5, center_x=400, center_y=300)
        self.player_list.append(self.player)
        rng = random.Random(1)
        for _ in range(20):
            coin = arcade.Sprite(":resources:images/items/coinGold.png", scale=0.4)
            coin.position = rng.randrange(40, 760), rng.randrange(40, 560)
            self.coins.append(coin)
        self.score = 0
        self.score_text = arcade.Text("Score: 0", 10, 570, arcade.color.WHITE, 16)

    def on_key_press(self, key, modifiers):
        speed = 250
        if key == arcade.key.LEFT:
            self.player.change_x = -speed
        elif key == arcade.key.RIGHT:
            self.player.change_x = speed
        elif key == arcade.key.UP:
            self.player.change_y = speed
        elif key == arcade.key.DOWN:
            self.player.change_y = -speed

    def on_key_release(self, key, modifiers):
        if key in (arcade.key.LEFT, arcade.key.RIGHT):
            self.player.change_x = 0
        elif key in (arcade.key.UP, arcade.key.DOWN):
            self.player.change_y = 0

    def on_update(self, delta_time):
        self.player.center_x += self.player.change_x * delta_time
        self.player.center_y += self.player.change_y * delta_time
        for coin in arcade.check_for_collision_with_list(self.player, self.coins):
            coin.remove_from_sprite_lists()
            self.score += 1
        self.score_text.text = f"Score: {self.score}"

    def on_draw(self):
        self.clear()
        self.coins.draw()
        self.player_list.draw()
        self.score_text.draw()


if __name__ == "__main__":
    Game()
    arcade.run()
```

What's new:

- **`list.draw()`** draws every sprite in the list in one go, on the graphics card. A
  `SpriteList` is fast in a way that a Python list of sprites drawn one by one is not.
- **`check_for_collision_with_list(sprite, sprite_list)`** returns every sprite in the
  list that overlaps `sprite`, using their hit boxes.
- **`remove_from_sprite_lists()`** takes a sprite out of every list it belongs to.

Here `change_x` is in pixels per second, and the game applies `* delta_time` itself.
(Next lesson, the physics engine applies `change_x` *per step* instead. Keep the
two apart.)

## 3. Removing while iterating

The coin loop above is safe because `check_for_collision_with_list` returns a **new**
list: you iterate over that, and remove from the sprite list. What's *not* safe:

```python fragment
for coin in self.coins:              # ⚠ iterating the list you're removing from
    if coin.center_y < 0:
        coin.remove_from_sprite_lists()
```

Same bug as Lesson 2.1, section 4: items get skipped. Iterate over a copy,
`for coin in list(self.coins):`, or collect the doomed sprites first and remove them afterwards.

## 4. Your turn (W6.1.a)

`week6/t6.1-sprites/collect.py`, building on the example:

- coins that **fall** from the top at random speeds and respawn above the screen when they leave the bottom
- a few "bomb" sprites (`:resources:images/tiles/bomb.png`): touching one costs 5 points
- the player can't leave the screen

Show the tutor where you remove sprites and why it's safe.

## Pitfalls

- Drawing sprites one at a time instead of with `SpriteList.draw()`.
- Creating sprites (and so loading their images) inside `on_draw` or `on_update`. Make them once.
- Removing from a `SpriteList` while iterating over it.
- Forgetting `* delta_time` when you move sprites yourself.
