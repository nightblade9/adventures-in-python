Title: Creating a Roguelike in Python + TDL, Part 4: The Keyboard Input System
Date: 2018-04-14
Slug: creating-a-roguelike-in-python-tdl-part-4
Category: Posts

This is the fourth part of our series for creating a Python roguelike with TDL and an ECS. In [part three]({filename}2018-04-14-roguelike-3-drawing-system), we refactored out a display system that handles drawing our player on-screen. We still have a lot of untestable keyboard input code in our `main.py` file, so we're going to extract that into a `KeyboardInputSystem` (with corresponding `KeyboardInputComponent`).

# Input is Complicated

Unlike the display system, we can't simply copy-paste the keyboard handling code into a new system and call it a day. Our game is real-time (so we can do things like animation and mouse-look), so we need to keep track of a couple of things:

- If the player presses `ESC` or `q`, we want to terminate the game
- If the player moves, we want to update all the systems in the game
- if the player doesn't move, we want to just redraw and check for input.

We also need to convert the player into an `Entity` subclass with a `DisplayComponent`; that will allow us to refactor our arrow-key-handling into the `Player` class. Let's handle this first, since it's the easiest part.

```Python
class Player(Entity):
    def __init__(self):
        self.set(DisplayComponent(40, 25, '@', (255, 255, 255)))
    
    def process_input(self, key_pressed):
        dc = self.get(DisplayComponent)
        if key_pressed == "UP":
            dc.y -= 1
        elif key_pressed == "DOWN":
            dc.y += 1
        elif key_pressed == "LEFT":
            dc.x -= 1
        elif key_pressed == "RIGHT":
            dc.x += 1
```

Pretty straight-forward; our main loop today would call `player.process_input`. But we'll leave that for now and move into the keyboard system.

# The Keyboard Input System

The keyboard input system is pretty simple: keep track of keys pressed, and in `update`, call a keypress callback on every entity's `KeyboardInputComponent`.  That gives us something like this:

```Python
class KeyboardInputSystem:
    """Handles keyboard input. Given an entity with a KeyboardInputComponent,
    this system calls the on_keydown callback when a key is pressed."""

    def __init__(self):
        self.keys_pressed = []

    def update(self, entities):
        current_keys_pressed = []

        # Check if there's input
        for event in tdl.event.get():
            if event.type == 'KEYDOWN':
                current_keys_pressed.append(event.keychar)
        
        # TODO: key_onpress, key_onrelease is now possible
        self.keys_pressed = current_keys_pressed
                
        if self.keys_pressed:
            for e in entities:
                if e.has(KeyboardInputComponent):
                    ki = e.get(KeyboardInputComponent)
                    ki.on_keydown_callback(self.keys_pressed)
    
    def get_all_keys_pressed(self):
       return self.keys_pressed
```

There's a subtlety here: in TDL, when you call `tdl.event.get()`, it actually *consumes* the events from the queue. That is, the events are processed and removed. calling `tdl.event.get` again will return nothing.

For this reason, we have to keep the list of keys pressed in an internal array, so that callers can consume them however they want. (This also lets us expose events like `key_justpressed` and `key_released`, but don't need those yet.)

The keyboard input component is straight-forward:

```Python
class KeyboardInputComponent:
    """Add this component to entities that need to track keyboard input."""
    def __init__(self, on_keydown_callback):
        """on_keypress_callback should accept an argument for the keys pressed."""
        self.on_keydown_callback = on_keydown_callback
```

With that in place, we can rewrite the main loop. We delete all references to keyboard processing, and add the keyboard system to the container. We want to write something like this:

```Python
class Main:
    def __init__(self):
        # ...
        self.container.add_system(KeyboardInputSystem())
        self.container.add_system(DisplaySystem(tdl.init(80, 50)))
        # ...
    
    def core_game_loop(self):
        self.container.update()
        while not self.game_over:
            # Game over?
            # Did time pass?
```

We can't easily check if the game is over and terminate, nor can we check if time passed (and process the loop differently in this case). To handle these two cases, we need to keep references to the display and keyboard input systems. Not quite elegant, but it'll do.  

When we add in in the `Player` instance, and keep track of game state with a `game_over` variable, our main loop then looks like this:

```Python
import os
import sys
# import ../*
sys.path.insert(1, os.path.join(sys.path[0], '..'))

from fantastic_couscous.ecs.container import Container
from fantastic_couscous.ecs.systems.display_system import DisplaySystem
from fantastic_couscous.ecs.systems.keyboard_input_system import KeyboardInputSystem

from player import Player
import tdl

class Main:
    def __init__(self):
        self.player = Player()
        self.game_over = False
        
        # We need a reference so we can draw even if there's no input (realtime)
        self.display_system = DisplaySystem(tdl.init(80, 50))
        # Needed so we can detect game-over and tell if time passed
        self.keyboard_input_system = KeyboardInputSystem()

        self.container = Container()

        # Order matters. Draw last.
        self.container.add_system(self.keyboard_input_system)
        self.container.add_system(self.display_system)
        
        self.container.add_entity(self.player)

    def core_game_loop(self):
        self.container.update()

        while not self.game_over:
            self.check_for_game_over()
            time_passed = self.check_if_time_passed()

            if time_passed:
                self.container.update()
            else:
                self.keyboard_input_system.update(self.container.entities)
                self.display_system.update(self.container.entities)
    
    def check_for_game_over(self):
        keys_pressed = [e for e in self.keyboard_input_system.get_all_keys_pressed() if e == 'ESCAPE' or e == 'q']
        if keys_pressed: # len > 0
            self.game_over = True
    
    def check_if_time_passed(self):
        all_keys_pressed = self.keyboard_input_system.get_all_keys_pressed()

        keys_pressed = [e for e in all_keys_pressed
            if e == 'UP' or e == 'DOWN' or e == 'LEFT' or e == 'RIGHT']

        return keys_pressed # len > 0
        
if __name__ == "__main__":
    Main().core_game_loop()

```

No surprises here:

- The initializer keeps track of our display/input systems
- The core game loop calls `update` on our container, or selectively updates just the display/input systems
- We have a `game_over` variable and a `check_for_game_over` method that updates the value to `True` if the user ever clicks `ESCAPE`/`q`
- We have a placeholder method to check if time passed by checking if the player moved (user pressed an arrow key)

The best part is that we can test most of the main code (from our keyboard input system).

# Testing

## KeyboardInputComponent
Tests are pretty straight-forward. Let's start with the easiest, our `KeyboardInputComponent`: all we can test is that the callback accepts a list of keys pressed and logs them:

```Python
from fantastic_couscous.ecs.components.keyboard_input_component import KeyboardInputComponent

import pytest

class TestKeyboardInputComponent:

    def test_init_takes_callback_which_accepts_keys_pressed(self):
        pressed = []
        k = KeyboardInputComponent(lambda keys: pressed.extend(keys))
        k.on_keydown_callback(["a", "b"])

        assert len(pressed) == 2
        assert "a" in pressed
        assert "b" in pressed
```

## KeyboardInputSystem

For the keyboard input system, we want to test a couple of things:

- `get_all_keys_pressed` returns keys after we call `update`.
- `update` calls `on_keydown` callbacks on all entities

To achieve both, like our `DisplaySystem` test, we need to mock TDL. tdl.event.get()` should return a list of keys pressed (even if hard-coded). We can achieve it with something like this:

```Python
class GetEvent:
    def get(self):
        return ["LEFT"]

event = GetEvent()
```

With this, calling `tdl.event` returns an instance of `GetEvent`, which returns `["LEFT"]`. But if we try to use this in a test, we run into an error; `KeyboardInputSystem` has this code in `update`:

```Python
for event in tdl.event.get():
    if event.type == 'KEYDOWN':
        # key pressed
```

We need to return a struct with a `type` and a `keychar`, like so:

```Python
class GetEvent:
    def get(self):
        return [KeyEvent("LEFT")]

class KeyEvent:
    def __init__(self, key, event_type="KEYDOWN"):
        self.keychar = key
        self.type = event_type
        
event = GetEvent()
```

With this, we can write our two tests:

```Python
class TestKeyboardInputSystem:
    def test_get_all_keys_pressed_returns_keys_from_update(self):
        kis = KeyboardInputSystem()
        assert kis.get_all_keys_pressed() == []

        # tdl.event.get() returns ["LEFT"]
        kis.update([])

        assert kis.get_all_keys_pressed() == ["LEFT"]

    def test_update_calls_keydown_callback_on_all_entities(self):
        pressed = []
        k = KeyboardInputComponent(lambda keys: pressed.extend(keys))
        e = Entity(k)

        kis = KeyboardInputSystem()
        kis.update([e])

        # tdl.event.get() returns ["LEFT"]        
        assert "LEFT" in pressed
```

## Player

The final piece is to test the `Player` class. We have one major method to test: the key-processing one:

```Python

class Player(Entity):
    def __init__(self):
        super().__init__(
            DisplayComponent('@', 0xFFFFFF, 40, 25),
            KeyboardInputComponent(self._process_input))
        
    def _process_input(self, keys_pressed):
        for key_pressed in keys_pressed:
            if key_pressed == "UP":
                self.get(DisplayComponent).y -= 1
            elif key_pressed == "DOWN":
                self.get(DisplayComponent).y += 1
            elif key_pressed == "LEFT":
                self.get(DisplayComponent).x -= 1
            elif key_pressed == "RIGHT":
                self.get(DisplayComponent).x += 1
            else:
                print("You pressed {}".format(key_pressed))
```

We can also test that the constructor sets a `DisplayComponent` and `KeyboardInputComponent`. That's simple enough, so we leave that as an exercise to the reader.

While Python discourages calling "private" methods (with leading underscores), that's really the only easy way to test our code, so we're going to call it. We want to test processing for all four arrow keys:

```Python
def test_process_input_moves_display_component_for_arrow_keys(self):
    p = Player()
    display = p.get(DisplayComponent)
    old_x, old_y = display.x, display.y

    p._process_input(["UP"])
    assert display.x == old_x
    assert display.y == old_y - 1
    old_x, old_y = display.x, display.y
    
    p._process_input(["DOWN"])
    assert display.x == old_x
    assert display.y == old_y + 1
    old_x, old_y = display.x, display.y

    p._process_input(["LEFT"])
    assert display.x == old_x - 1
    assert display.y == old_y
    old_x, old_y = display.x, display.y

    p._process_input(["RIGHT"])
    assert display.x == old_x + 1
    assert display.y == old_y
```

Pretty simple. With this, we have a mostly complete refactored loop.

In part five, we'll forage onward and add some new functionality to our roguelike (solid walls that we can't walk through).

Meanwhile, I'll also clean up the `main.py` file and extract out some of the dependencies on the various systems so we can test `check_for_game_over` and `check_if_time_passed`. While having 100% testable code is an ideal to strive for, the practical reality is that it's not always worth it to write complex/flaky tests to get there.

In this case, we have two methods that are relatively easy to make testable by extracting dependencies, so it's worth it.