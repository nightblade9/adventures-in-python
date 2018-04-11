Title: Creating a Roguelike in Python + TDL, Part 1: Entity-Component System
Date: 2018-04-01
Slug: creating-a-roguelike-in-python-tdl-part-1

In this series, we're going to build a roguelike in Python and TDL. Python is a high-level, interpreted, object-oriented and functional language with expressive syntax, native lambdas, and more goodness. TDL is one of two console-like libraries for the UI (the other being `libtcod`, which is more "C++ic" than Pythonic).

This series aims to build on top of [this excellent series on RogueBasin](http://www.roguebasin.com/index.php?title=Roguelike_Tutorial,_using_python3%2Btdl), which walks you from basics to having a complete, shippable, small roguelike; the main additional benefit we want to confer from this tutorial is *code quality*.

The RogueBasin roguelike code, while excellent in terms of functionality, includes some poor design choices -- probably because the goal was a) make something fast that works, and b) put everything in one file so it's easy to copy-paste. As a result, it doesn't provide a solid foundation for extension -- you quickly get bogged down with complexity.

Specifically, we plan to:

- Use an entity-component system instead of a (mostly) monolithic `GameObject` base class
- Avoid the use of global variables completely
- Isolate TDL code as much as possible, so that our code is more testable

Without further ado, let's dive into the first part: writing our entity-component system.

# The Simplest Entity-Component System

If you haven't heard about them before, you can read [this classic post about Entity-Component Systems](http://cowboyprogramming.com/2007/01/05/evolve-your-heirachy/). In a nutshell, the goal is to avoid complex classes with interweaved logic (input handling + UI/drawing + game logic + ...), and instead, compose classes made of small, independent components.

While there are many, *many* ways to write an ECS, ours will follow the design of [CraftyJS](http://craftyjs.com), quite possibly one of the best ECS libraries ever:

- Components are small, reusable classes that encapsulate code and data (eg. `HealthComponent` with `get_hurt(damage)`, `die()`, `current_health`, etc.)
- Entities are classes that implement custom logic that spans components

With this in mind, let's create our base class: the entity.

# The Entity Class

The Entity class has a few simple requrements:

- A user can `set(component)` a component, and the entity will keep that. (The entity has, at most, one component of each type/class.)
- A user can `get(clazz)` a component, specifying the class/type, and will get the actual component
- A user can check if an entity has a component of a specific type/class via `has(clazz)`

Internally, we can store components in a dictionary that maps components by type to instance.  Here's what that looks like:

```Python
class Entity:
    def __init__(self, *components):
        self.components = {}
        Entity.all_entities.append(self)

        for component in components:
            self.set(component)
    
    def set(self, component):
        key = type(component)
        self.components[key] = component
    
    def get(self, clazz):
        return self.components[clazz]
    
    def has(self, clazz):
        return self.get(clazz) is not None

```

That's it! We don't even need a `Component` class, because entities can technically use any class/instance/object as a component.

We also only need a simple test: that we can `get` a component which was `set`, and that `has` returns `True` if the component exists (and `False` otherwise). We should also test that `set` overwrites the previous component. 

Tests (`pytest` tests):

```Python
from ecs.entity import Entity

class TestEntity:
    def test_getter_gets_set_values(self):
        e = Entity()
        expected = IntComponent(13)
        e.set(expected)

        actual = e.get(IntComponent)
        assert actual == expected

    def test_set_overwrites_previous_value(self):
        e = Entity()
        expected = IntComponent(13)

        e.set(IntComponent(1888))
        e.set(expected)

        actual = e.get(IntComponent)
        assert actual == expected
    
    def test_has_retruns_true_if_component_exists(self):
        # Note: doesn't work for subclasses of the component
        e = Entity(IntComponent(77))
        assert e.has(IntComponent) is True
        assert e.has(StringComponent) is False


class IntComponent:
    def __init__(self, value):
        self.value = value


class StringComponent:
    def __init__(self, value):
        self.value = str(value)
```

With this, we can be sure our Entity class works as expected. In part two, we'll create a "Hello World" TDL application where we get the main UI window up, and start detecting/processing input so we can quit/terminate our game.