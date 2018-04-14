Title: Creating a Roguelike in Python + TDL, Part 2: Basic Movement
Date: 2018-04-01
Slug: creating-a-roguelike-in-python-tdl-part-2

This is the second part of our series for creating a Python roguelike with TDL and an ECS. In [part one]({filename}2018-04-11-roguelike-1-ecs.md), we created our basic `Entity` class with the few methods it needs (`get`, `set`, `has`) and some unit tests. In this part, we're going to initialize out UI, draw our player on-screen, and have him move around when we use the arrow keys.

# Setting Up TDL

TDL is complicated. Accordingly, we're going to start with the simplest possible "hello world" TDL: drawing the screen, processing input, and terminating when the player presses `ESC` or `q`.

Here's the code for creating a basic TDL app:

```Python
import tdl

class Main:
    def run(self):
        tdl.init(80, 50)
        
        while not tdl.event.is_window_closed():
            user_input = tdl.event.key_wait()
            key_pressed = user_input.keychar
            if key_pressed == "ESCAPE" or key_pressed == 'q':
                break
            else:
                print("You pressed {}".format(key_pressed))

if __name__ == "__main__":
    Main().run()
```

If you run this code, you'll see something like this (console in the background):

![screenshot](https://i.imgur.com/sVbghcT.png)

Now that we can trap keyboard input (and arrow keys), we can start to work on our `Player` class.

# Player Entity

In an ECS like ours (inspired by CraftyJS!), a player would be an `Entity`, which is made up of a bunch of `components`. For now, we'll just use a tuple of coordinates to handle this; in the future, we'll turn it into an *actual* `Player` entity, complete with display and keyboard-processing components.

High-level steps:

- Create a tuple to store `(player_x, player_y)`.
- If the player presses an arrow key, update one of the two values appropriately.
- Draw the player onto the screen.

Storing the values is trivial; for the input, we can process input, like so:

```Python
if key_pressed == "UP":
    player_y -= 1
elif key_pressed == "DOWN":
    player_y += 1
elif key_pressed == "LEFT":
    player_x -= 1
elif key_pressed == "RIGHT":
    player_x += 1
```

To draw the player, we need a little more work, and we need to learn a bit more about TDL.

TDL has a `console` concept, which represents, well, an ASCII-like console. There's also the `root_console`, which is the one which draws onto the screen.

To start, we need to keep a reference to the root console; that's the one we draw to. We can also draw to it by calling `root_console.draw_char(player_x, player_y, '@', (255, 255, 255))`. This draws a white '@' at `(player_x, player_y)`.

Our total code looks like this:

```Python
import tdl

import tdl

class Main:
    def run(self):
        root_console = tdl.init(80, 50) # keep a reference to self.console
        player_x, player_y = (40, 25)
        
        while not tdl.event.is_window_closed():
            user_input = tdl.event.key_wait()
            key_pressed = user_input.keychar
            
            if key_pressed == "UP":
                player_y -= 1
            elif key_pressed == "DOWN":
                player_y += 1
            elif key_pressed == "LEFT":
                player_x -= 1
            elif key_pressed == "RIGHT":
                player_x += 1
                
            root_console.draw_char(player_x, player_y, '@', (255, 255, 255))

if __name__ == '__main__':
    Main().run()
```

Run it, and there's a problem! The player never draws! Astute observers might notice that the screen only draws *once you switch tabs and switch back.* What's going on?

It turns out TDL buffers draw calls for performance (which makes sense). What we need to do, is force TDL to flush the output, by calling `tdl.flush()`.

Now, our player moves! Hurrah! But there's another problem: he leaves behind *a trail of `@` characters.* 

![screenshot](https://i.imgur.com/1jRw1e4.png)

It turns out TDL (literally) only draws the changed character, and doesn't redraw anything previously drawn, or clear the previous player drawn onto the console.

To fix this, we can call `root_console.clear` before drawing the player. And everything works as expected!

Whew, that's a lot! Unfortunately, our code is starting to look positively spaghetti-like (almost to the point of global variables) -- we can't easily extract our user input input into a method, nor test it.

In part 3, we'll step back and refactor this into a proper ECS architecture before foraging onward.

# Final Code

```Python
import tdl

class Main:
    def run(self):
        root_console = tdl.init(80, 50) # keep a reference to self.console
        player_x, player_y = (40, 25)
        
        while not tdl.event.is_window_closed():
            user_input = tdl.event.key_wait()
            key_pressed = user_input.keychar
            
            if key_pressed == "UP":
                player_y -= 1
            elif key_pressed == "DOWN":
                player_y += 1
            elif key_pressed == "LEFT":
                player_x -= 1
            elif key_pressed == "RIGHT":
                player_x += 1
                
            root_console.clear()
            root_console.draw_char(player_x, player_y, '@', (255, 255, 255))
            tdl.flush()
    
            
if __name__ == '__main__':
    Main().run()
```