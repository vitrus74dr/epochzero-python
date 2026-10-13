# Desktop App: Habit Tracker (Tkinter)

Your first app with windows and buttons. You'll track daily habits ("read 20 pages",
"walk") and see each habit's **streak**: how many days in a row you've done it.
Tkinter ships with Python, so there's nothing to install.

The big idea is the one from Week 2, made bigger. The **model** (habits, dates,
streaks, saving) knows nothing about windows. The **view** (Tkinter) only displays
the model and passes clicks on to it. That's how you test the important part without
clicking anything.

## 1. A window in ten lines

```python
import tkinter as tk
from tkinter import ttk

root = tk.Tk()
root.title("Hello Tk")

label = ttk.Label(root, text="Clicked 0 times")
label.pack(padx=20, pady=10)

clicks = 0
def on_click():
    global clicks          # fine for a 10-line demo; the real app uses a class
    clicks += 1
    label.config(text=f"Clicked {clicks} times")

ttk.Button(root, text="Click me", command=on_click).pack(pady=(0, 20))
root.mainloop()
```

- `tk.Tk()` is the main window. `ttk` widgets use the native look.
- `pack()` places a widget; `padx`/`pady` add space around it.
- `command=on_click` passes the *function itself*, with no `()`. Tk calls it later, on each click.
- `mainloop()` hands control to Tk: from here on, your code runs only in callbacks.
  This style is **event-driven** programming, and games work the same way.

Run it with **Ctrl/Cmd+Enter**; the window opens on your desktop.

## 2. The widgets you need

```python fragment
entry = ttk.Entry(root)            # one line of text input
entry.get()                        # read it
entry.delete(0, tk.END)            # clear it

listbox = tk.Listbox(root, height=8)
listbox.insert(tk.END, "Read")     # add a row
listbox.curselection()             # tuple of selected row indexes, e.g. (0,)
listbox.delete(0, tk.END)          # clear all rows

from tkinter import messagebox
messagebox.showerror("Oops", "Type a habit name first")
```

To lay out rows and columns, use `grid(row=..., column=...)` instead of `pack()`. Don't mix
the two in the same parent widget.

## 3. The app as a class

Globals don't scale. Put the window in a class that holds a reference to the model:

```python fragment
class HabitApp:
    def __init__(self, root: tk.Tk, tracker: HabitTracker, today: date):
        self.tracker = tracker
        self.today = today
        self.entry = ttk.Entry(root)
        self.entry.grid(row=0, column=0, sticky="ew")
        ttk.Button(root, text="Add", command=self.add).grid(row=0, column=1)
        self.listbox = tk.Listbox(root, width=40)
        self.listbox.grid(row=1, column=0, columnspan=2)
        ...
        self.refresh()

    def add(self):
        name = self.entry.get().strip()
        if not name:
            messagebox.showerror("Oops", "Type a habit name first")
            return
        self.tracker.add(name)          # the model does the work
        self.refresh()                  # the view redraws from the model

    def refresh(self):
        self.listbox.delete(0, tk.END)
        for habit in self.tracker.habits:
            mark = "✓" if habit.done_on(self.today) else " "
            self.listbox.insert(tk.END, f"[{mark}] {habit.name}  🔥 {habit.streak(self.today)}")
```

Every callback follows the same three steps: read the widgets, call the model, `refresh()`.

## 4. The model: streaks

A `Habit` stores the set of dates it was done. Its streak needs a careful definition,
and this is a good `/grill-me` question:

- Done today, yesterday and the day before: streak **3**.
- Done yesterday and the day before, not *yet* today: still **2**. The day isn't over,
  so the streak isn't broken.
- Last done three days ago: streak **0**.

```python fragment
def streak(self, today: date) -> int:
    ...
```

`today` is a parameter, as in the Leitner project (Lesson 3.3), so a test can check any
day. The tests to write (W3.4.d):

- a new habit has streak 0
- consecutive days count up; a gap resets
- "not yet today" keeps yesterday's streak
- marking the same day twice doesn't double-count (a **set** of dates helps)
- save → load gives identical habits (JSON with ISO date strings)

## 5. Saving

Same pattern as Lesson 3.3: `to_dict()`/`from_dict()`, dates as `isoformat()` strings,
`with open(path, "w", encoding="utf-8")`. Save after every change, so closing the
window never loses data.

## 6. How it's checked

- **W3.4.a**: `/grill-me W3.4` (model vs view split, the streak rules, file format).
- **W3.4.b–c**: a demo of the running app; the tutor reads your model code.
- **W3.4.d**: `/verify W3.4` runs the model tests. They never create a `tk.Tk()`.
- **W3.4.e**: `walkthrough.md`.

## Pitfalls

- `command=self.add()` with parentheses: it calls `add` once while *building* the
  window, and passes its return value (`None`) as the command.
- Model code that imports `tkinter`. Then you can't test it without a display.
- Mixing `pack()` and `grid()` in the same parent widget: Tk hangs trying to satisfy both.
- Calling `date.today()` inside `streak()`.
