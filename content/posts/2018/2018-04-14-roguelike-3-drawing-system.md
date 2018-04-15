Title: Creating a Roguelike in Python + TDL, Part 3: The Drawing System
Date: 2018-04-14
Slug: creating-a-roguelike-in-python-tdl-part-3
Category: Posts

This is the third part of our series for creating a Python roguelike with TDL and an ECS. In [part two]({filename}2018-04-12-roguelike-2-basic-movement.md), we finally enabled our player to run around with the arrow keys, learning about about TDL's drawing APIs along the way.

In this part, we aim to take our spaghetti-like mess of code and refactor the drawing part out into a testable drawing system.

# A Word About Testing

Testing is a complicated topic. To keep it simple, we'll write unit-tests (fast, isolated, class-/method-level tests) that test our code. We'll keep TDL out of the picture with a combination of mocks/stubs and dependency injection.

We do this because writing complex "integration" tests that include TDL. This can be problematic because:

- They run in the order of seconds instead of milliseconds per test
- They require spinning up a TDL application and removing it
- They can be fragile/fickle depending on how TDL's inner workings are (something we want to avoid learninag about)
- They can't run in a *headless* CI environment like Travis that doesn't have a display

There's a lot more we can say about testing, but this is enough for now.

# Adding Systems to our Entity Component Systems

Like most ECSes out there, in ours, a `System` is a class with a single purpose, that will operate on entities  that have one or more matching components. For example, we'll make a `DisplayComponent` that encapsulates display data (`x, y` coordinates, character, and colour), and the `DisplaySystem` will simply draw all entities' display components on-screen.

Since we'll probably use different sets of systems in different scenes (eg. the menu and core game might require a `KeyboardInputSystem` but only the core game would require a `DisplaySystem` for drawing entities). we'll introduce a new concept called a `Container`.

A `Container` is basically just a collection of entities and systems used together. Calling `update` on the container will call `update` on each system, passing in the list of entities. Our core game loop, instead of managing input, drawing, etc. will simply call `container.update`, which will call `update` on each system to handle drawing, input, etc.

This way, systems are more lightweight, and easier to test (pass in any set of entities and you're good).

With that out of the way, let's start by adding our first (display) system and component.

# Refactoring Out the Display System and Component

From part two, the end of our core game loop looked like this:

```Python
root_console.clear()
root_console.draw_char(player_x, player_y, '@', (255, 255, 255))
tdl.flush()
```

We can copy-paste this code into a new `DisplaySystem` class:

```Python
class DisplaySystem:
    def update(self, entities):
        for e in entities:
            dc = e.get(DisplayComponent)
            root_console.draw_char(dc.x, dc.y, dc.character, dc.colour)
```

Wait, we need to have access to the root console! Since the display system handles all things display-related, it makes sense to move the TDL initializer code inside, along with the root console:

```Python
from fantastic_couscous.ecs.components.display_component import DisplayComponent
import tdl

class DisplaySystem:
    
    def __init__(self):
        self._root_console = tdl.init(80, 50)

    def update(self, entities):
        # TODO: instead of this, track old positions and redraw only what changed
        self._root_console.clear()
        
        for e in entities:
            dc = e.get(DisplayComponent)
            self._root_console.draw_char(dc.x, dc.y, dc.character, dc.colour)
        
        tdl.flush()
```

This looks fine, except there's one problem: we can't easily test it, because we have a hard dependency on `tdl` and `console`. We can address these problems later; let's get the main loop working first.

## Creating the `Container` Class

Next, we need to wire up our `Container` class. It's pretty simple, and looks something like this:

```Python
# A generic container of systems. This is how we define a bunch of systems.
# Singleton-ish, so it's both easily accessible and unit-testable.
class Container:

    instance = None

    def __init__(self):
        Container.instance = self        
        self._systems = []
        self._entities = []
    
    def add_system(self, system):
        self._systems.append(system)
    
    def add_entity(self, entity):
        self._entities.append(entity)
    
    def update(self):
        for s in self._systems:
            s.update(self._entities)
```

It's pretty simple: you can add entities and systems, and calling update just calls update on each system, passing in the entities. We can also write tests for it:

```Python
from fantastic_couscous.ecs.container import Container
from fantastic_couscous.ecs.entity import Entity

import pytest

class TestContainer:
    def test_add_system_adds_systems(self):
        s1 = DummySystem()
        s2 = DummySystem()
        c = Container()
        c.add_system(s1)
        
        assert s1 in c._systems
        assert s2 not in c._systems
    
    def test_add_entity_adds_it_to_entities(self):
        e = Entity()
        c = Container()
        c.add_entity(e)

        assert e in c._entities

    def test_update_calls_update_on_all_systems(self):
        c = Container()
        s1 = DummySystem()
        c.add_system(s1)
        c.update()

        s2 = DummySystem()
        c.add_system(s2)
        c.update()

        assert s1.update_calls == 2
        assert s2.update_calls == 1

class DummySystem:
    def __init__(self):
        self.update_calls = 0
    
    def update(self, entities):
        self.update_calls += 1
```

With that done, we can finally modify our main loop to:

- Create a new container
- Initialize and add the `DisplaySystem`, initializing the root console from TDL
- Converting the player into an entity class with a `DisplayComponent`.

Let's get to it.

## Modifying the Main Loop

Here's what our (abbreviated) loop should look like now:

```Python
# player.py
class Player(Entity):
    def __init__(self):
        super().__init__(DisplayComponent('@', 0xFFFFFF, 40, 25))

# main.py
class Main:
    def __init__(self):
        self.player = Player()
        
        self.container = Container()
        # Order matters. Draw last.
        self.container.add_system(DisplaySystem(tdl.init(80, 50)))
        
        self.container.add_entity(self.player)

    def core_game_loop(self):
        self.container.update()

        while not tdl.event.is_window_closed():
            user_input = tdl.event.key_wait()
            key_pressed = user_input.keychar
            # Process input as before

            self.container.update()            
```

Input processing can remain as-is. Our game output should be identical to before.  With this in place, our refactoring is done; we can move on to testing our code.

# Testing the Display System

Our display system is inherently untestable because it depends on `tdl` and `console`. How can we resolve this?

Dependency Injection to the rescue!  Instead of creating the `console` internally, we can pass it in:

```Python
def __init__(self, console):
    self.root_console = console
```

When we create the display system in our main loop, we call `DisplaySystem(tdl.init(80, 50))`. In our tests, we can pass in something else, depending on what we want to test. A complete mock (with respect to calls we use now) looks like this:

```Python
class FakeConsole:
    def __init__(self):
        pass

    def clear(self):
        pass

    def draw_char(self, x, y, character, colour):
        pass
```

This allows us to run our tests by calling `DisplaySystem(FakeConsole())`, but it doesn't let us easily test what methods are mocked. To do that, we can log methods with their parameters, like so:

```Python
class FakeConsole:
    def __init__(self):
        self.draw_calls = []

    def clear(self):
        self.draw_calls.append("clear")

    def draw_char(self, x, y, character, colour):
        self.draw_calls.append("draw_char({}, {}, {}, {})".format(x, y, character, colour))
```

This allows us to write things like `assert "draw_char(3, 5, '@', 'white')" in console.draw_calls`.

The second problem is the `tdl` references. How can we mock those out? As it's a module, we can't simply inject it.

The answer comes from Python's import order; if we create a local module called `tdl`, that module gets imported first! We can do something like this:

```Python
# tdl.py

def draw_char(x, y, character, colour):
    pass
```

A more useful mock would be one where we can check what methods are called, like our `FakeConsole`:

```Python
tdl_calls = []
def flush():
    tdl_calls.append("flush")
```

This allows us to add asserts like `assert "flush" in tdl.tdl_calls`.

With this in place, we're ready to test our display system. There aren't many interesting tests, so I'll just add the list below.

```Python
#test_display_system.py
import tdl
import pytest

class TestDisplaySystem:
    def test_init_injects_root_console(self):
        console = 37
        d = DisplaySystem(console)
        assert d._root_console == console
    
    def test_update_calls_draw_char_on_console_with_display_component_from_entity(self):
        player = Entity()
        player.set(DisplayComponent('@', "white", 28, 10))

        monster = Entity()
        monster.set(DisplayComponent('m', "green", 30, 8))

        c = Container()
        c.add_entity(player)
        c.add_entity(monster)
        console = FakeConsole()

        ds = DisplaySystem(console)
        c.add_system(ds)

        # Act
        c.update()

        # Assert
        pd = player.get(DisplayComponent)
        md = monster.get(DisplayComponent)
        calls = console.draw_calls
        assert calls[0] == "clear"
        assert calls[1] == "draw_char({}, {}, {}, {})".format(pd.x, pd.y, pd.character, pd.colour)
        assert calls[2] == "draw_char({}, {}, {}, {})".format(md.x, md.y, md.character, md.colour)
        assert tdl.tdl_calls[0] == "flush"

class FakeConsole:
    def __init__(self):
        self.draw_calls = []

    def clear(self):
        self.draw_calls.append("clear")

    def draw_char(self, x, y, character, colour):
        self.draw_calls.append("draw_char({}, {}, {}, {})".format(x, y, character, colour))
```

The only new, noteworthy piece here is that we're checking that specific calls were made, thanks to our logging them in `draw_calls` in `FakeConsole`. 

Also, consider how much more testable the code is compared to before. While we still have a bunch of untestable code in `main.py`, it's significantly reduced.

It's also worth mentioning here that this responsibility (mocking classes, recording/asserting which calls are made) can usually be done by so-called mocking or dynamic-mocking frameworks like `unittest.mock`.

Since Python relies on duck-typing, and our classes are easy to mock/create, here, we just rely on hand-crafted mocks.

That's a lot, but that wraps up part three. In part four, we'll make a similar change to move the input processing into a keyboard-input-handling system. 