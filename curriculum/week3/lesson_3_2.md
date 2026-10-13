# Inheritance & Polymorphism

Often several classes are *mostly* the same. A circle and a square are both shapes;
a player and an enemy are both characters with a position and health.
**Inheritance** lets one class build on another, and **polymorphism** lets your code
treat them all the same way.

## 1. A subclass

```python
class Animal:
    def __init__(self, name):
        self.name = name

    def speak(self):
        return "..."

    def introduce(self):
        return f"I'm {self.name} and I say {self.speak()}"


class Dog(Animal):          # Dog inherits from Animal
    def speak(self):        # override one method
        return "Woof"


class Cat(Animal):
    def speak(self):
        return "Meow"


Dog("Rex").introduce()      # "I'm Rex and I say Woof"
```

`Dog` gets everything `Animal` has (`__init__`, `introduce`) and replaces `speak`.
Notice that `introduce`, written once in `Animal`, calls whichever `speak` the actual
object has.

## 2. Polymorphism

Code that works with an `Animal` works with *any* kind of animal:

```python
for pet in [Dog("Rex"), Cat("Tom"), Animal("Generic")]:
    print(pet.introduce())
```

No `if isinstance(pet, Dog)` chains needed: each object knows how to `speak`. When you
catch yourself writing `if kind == "dog": ... elif kind == "cat": ...`, a class per
kind is often cleaner.

## 3. `super()`: extend, don't replace

Sometimes a subclass needs *more* setup than its parent. Call the parent's version with
`super()`, then add your part:

```python
class Shape:
    def __init__(self, name):
        self.name = name

    def area(self):
        raise NotImplementedError


class Rectangle(Shape):
    def __init__(self, width, height):
        super().__init__("rectangle")    # let Shape set self.name
        self.width = width
        self.height = height

    def area(self):
        return self.width * self.height


class Square(Rectangle):
    def __init__(self, side):
        super().__init__(side, side)     # a square is a rectangle with equal sides
        self.name = "square"
```

```python
>>> s = Square(3)
>>> s.area()
9
>>> isinstance(s, Rectangle), isinstance(s, Shape)
(True, True)
```

If you override `__init__` and forget `super().__init__(...)`, the parent's setup never
runs. You'll get an `AttributeError` later, when something reads `self.name`.

`raise NotImplementedError` in `Shape.area` says "every real shape must provide this".

## 4. When *not* to inherit

Inheritance says "**is a**": a square *is a* rectangle. If the relation is "**has a**"
(a car *has an* engine), store the other object as an attribute instead. That's called
*composition*. Deep inheritance trees (more than two or three levels) are hard to follow.

## 5. Your turn

**W3.2.a (tutor check):** in `week3/t3.2-shapes/shapes.py`, write `Shape`, `Rectangle`,
`Square` and `Circle` (with `import math`, area = `math.pi * r ** 2`). Then:

```python fragment
shapes = [Rectangle(2, 3), Square(4), Circle(1)]
for s in sorted(shapes, key=lambda s: s.area()):
    print(f"{s.name}: {s.area():.2f}")
```

Explain to the tutor where polymorphism happens in that loop.

**W3.2.b (quiz):** five questions on OOP; you need 4/5. [Take the quiz](#/quiz/W3.2.quiz),
or run `pygrid-quiz W3.2.quiz`.

## Pitfalls

- Overriding `__init__` without calling `super().__init__(...)`.
- Using inheritance for "has a" relationships.
- `isinstance` chains where a method on each class would do.
