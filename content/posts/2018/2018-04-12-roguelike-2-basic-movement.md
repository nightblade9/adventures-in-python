Title: Creating a Roguelike in Python + TDL, Part 2: Basic Movement
Date: 2018-04-01
Slug: creating-a-roguelike-in-python-tdl-part-2

This is the second part of our series for creating a Python roguelike with TDL and an ECS. In [part one]({filename}2018-04-11-roguelike-1-ecs.md), we created our basic `Entity` class with the few methods it needs (`get`, `set`, `has`) and some unit tests. In this part, we're going to initialize out UI, draw our player on-screen, and have him move around when we use the arrow keys.

# Final Code

```Python
import os
import sys
# import ../*
sys.path.insert(1, os.path.join(sys.path[0], '..'))

from ecs.entity import Entity
from ecs.components.display_component import DisplayComponent

import tdl

class Player(Entity):
    def __init__(self, x, y):
        super().__init__(DisplayComponent('@', 0xFFFFFF, x, y))

class Main:
    def __init__(self):
        self.root_console = tdl.init(80, 50)
        self.player = Player(40, 25)
        self.game_over = False

    def core_game_loop(self):
        self.draw()

        while not tdl.event.is_window_closed() and not self.game_over:
            user_input = tdl.event.key_wait()
            key_pressed = user_input.keychar
            self.process_input(key_pressed)
            # time passes
            self.draw()
    
    # TODO: refactor into system and component
    def process_input(self, key_pressed):
        if key_pressed == "ESCAPE" or key_pressed == 'q':
            self.game_over = True
        elif key_pressed == "UP":
            self.player.get(DisplayComponent).y -= 1
        elif key_pressed == "DOWN":
            self.player.get(DisplayComponent).y += 1
        elif key_pressed == "LEFT":
            self.player.get(DisplayComponent).x -= 1
        elif key_pressed == "RIGHT":
            self.player.get(DisplayComponent).x += 1
        else:
            print("You pressed {}".format(key_pressed))

    def draw(self):
        # TODO: refactor into system
        dc = self.player.get(DisplayComponent)
        self.root_console.clear()
        self.root_console.draw_char(dc.x, dc.y, dc.character, dc.colour)
        tdl.flush()

if __name__ == "__main__":
    Main().core_game_loop()
```